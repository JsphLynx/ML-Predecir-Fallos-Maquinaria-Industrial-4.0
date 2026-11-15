"""Evaluación retrospectiva. No importa ni ajusta modelos. Fechas UTC."""
import numpy as np
import pandas as pd

def generar_alertas(decisions,high,low,max_open_hours=24):
    if not np.isfinite([high,low]).all() or low>high:raise ValueError('Umbrales inválidos')
    cols=['run_id','assembly_id','timestamp','score','evaluable','rolling_state']
    d=decisions[cols].copy()
    if d.duplicated(cols[:3]).any():raise ValueError('Decisiones duplicadas')
    if str(d.timestamp.dt.tz)!='UTC':raise ValueError('Se requiere UTC')
    if (d.timestamp.dt.minute%15).any() or d.timestamp.dt.second.any() or d.timestamp.dt.microsecond.any():raise ValueError('Rejilla de 15 minutos')
    records=[]
    for (run,asset),group in d.groupby(['run_id','assembly_id']):
        group=group.set_index('timestamp').sort_index()
        group=group.reindex(pd.date_range(group.index.min(),group.index.max(),freq='15min'))
        votes=[];active=None;recover=0;counter=0
        for t,row in group.iterrows():
            ok=pd.notna(row.evaluable) and bool(row.evaluable) and pd.notna(row.score) and np.isfinite(row.score)
            hard=pd.notna(row.rolling_state) and row.rolling_state in ['fallo','mantenimiento']
            if hard:
                if active is not None:active.update(closed_at=t,close_reason='intervencion_o_fallo');active=None
                votes=[];recover=0;continue
            if active is not None and t-active['opened_at']>=pd.Timedelta(hours=max_open_hours):
                active.update(closed_at=t,close_reason='duracion_maxima');active=None;votes=[];recover=0
            votes=(votes+[bool(ok and row.score>=high)])[-5:]
            if active is None and ok and row.score>=high and sum(votes)>=3:
                counter+=1;active=dict(run_id=run,assembly_id=asset,alert_id=f'{run}-{asset}-A{counter:05d}',opened_at=t,closed_at=pd.NaT,close_reason='abierta')
                records.append(active);recover=0
            elif active is not None:
                recover=recover+1 if ok and row.score<low else 0
                if recover>=4:
                    active.update(closed_at=t,close_reason='recuperacion_4_validas');active=None;votes=[];recover=0
    return pd.DataFrame(records,columns=['run_id','assembly_id','alert_id','opened_at','closed_at','close_reason'])

def evaluar_eventos(alerts,events,preventives,end_by_run,exposure_hours,min_lead_minutes=60,horizon_hours=24):
    """events contiene todos los fallos de la cohorte, incluso sin datos evaluables.
    exposure_hours: horas operativas de telemetría 5m, no 0.25 * filas etiquetadas.
    """
    if events.duplicated(['run_id','event_id']).any():raise ValueError('Eventos duplicados')
    out=[];matched=set()
    for a in alerts.sort_values('opened_at').itertuples():
        t=a.opened_at;deadline=t+pd.Timedelta(hours=horizon_hours)
        ev=events[(events.run_id==a.run_id)&(events.start>t)].sort_values('start')
        pm=preventives[(preventives.run_id==a.run_id)&(preventives.start>t)].start.min()
        end=end_by_run[a.run_id];boundary=min(end,pm) if pd.notna(pm) else end
        candidate=ev.iloc[0] if len(ev) else None;eid=None;lead=np.nan
        if candidate is not None and candidate.start<=deadline and candidate.start<boundary:
            eid=candidate.event_id;lead=(candidate.start-t).total_seconds()/60
            if lead<min_lead_minutes:status='tardia'
            elif (a.run_id,eid) in matched:status='duplicada'
            else:status='util';matched.add((a.run_id,eid))
        elif boundary<=deadline:status='censurada'
        else:status='falsa'
        out.append(dict(run_id=a.run_id,alert_id=a.alert_id,event_id=eid,status=status,lead_minutes=lead))
    result=pd.DataFrame(out,columns=['run_id','alert_id','event_id','status','lead_minutes'])
    rows=[]
    for run,hours in exposure_hours.items():
        e=events[events.run_id==run];a=result[result.run_id==run]
        hits=sum((run,i) in matched for i in e.event_id)
        rows.append(dict(run_id=run,events=len(e),detected_events=hits,recall=hits/len(e) if len(e) else np.nan,
            false_alerts=int(a.status.eq('falsa').sum()),operating_hours=hours,
            false_per_1000h=float(a.status.eq('falsa').sum()*1000/hours) if hours else np.nan,
            censored_alerts=int(a.status.eq('censurada').sum()),late_alerts=int(a.status.eq('tardia').sum()),duplicate_alerts=int(a.status.eq('duplicada').sum())))
    modes=[]
    for mode,g in events.groupby('mode'):
        n=sum((r.run_id,r.event_id) in matched for r in g.itertuples())
        modes.append(dict(mode=mode,events=len(g),detected_events=n,recall=n/len(g),descriptive_only=len(g)<20))
    return result,pd.DataFrame(rows),pd.DataFrame(modes)

def mascara_decision(f,partition,modo='observable'):
    if modo not in ['benchmark','observable']:raise ValueError('Modo inválido')
    mask=f.evaluation_status.eq('evaluable')
    return mask & f.partition.eq(partition) if modo=='benchmark' else mask

def construir_cohorte(root,partition,modo="benchmark"):
    """Intervalo nominal por fecha común; incluye fallos sin oportunidad/calidad.
    La selección por episodios del benchmark ML se conserva en máscara de decisión.
    Purga/episodios = abstención del benchmark, nunca borran el denominador de eventos.
    modo=observable no aplica la máscara retrospectiva; es la simulación de servicio.
    No usar el modo benchmark como política de inferencia en una aplicación.
    """
    import json
    from pathlib import Path
    root=Path(root);c=json.loads((root/'config/escenario.json').read_text())
    if modo not in ['benchmark','observable']:raise ValueError('Modo de evaluación inválido')
    if partition not in ['train','validation','test','stress']:raise ValueError(partition)
    start=pd.Timestamp(c['start']);end=start+pd.Timedelta(days=c['days'])
    b1=start+(end-start)*c['train_fraction'];b2=b1+(end-start)*c['validation_fraction']
    lo,hi={'train':(start+pd.Timedelta(hours=4),b1),'validation':(b1,b2),'test':(b2,end),'stress':(start+pd.Timedelta(hours=4),end)}[partition]
    runs=pd.read_parquet(root/'data/ejecuciones.parquet')
    selected=runs[runs.scenario.str.startswith('stress').eq(partition=='stress')].run_id
    events=pd.read_parquet(root/'data/fallos.parquet');events=events[events.run_id.isin(selected)&events.start.ge(lo)&events.start.lt(hi)]
    maint=pd.read_parquet(root/'data/mantenimiento.parquet');maint=maint[maint.run_id.isin(selected)&maint.kind.eq('preventivo')&maint.start.ge(lo)&maint.start.lt(hi)]
    frames=[];hours={};coverage=[]
    for run in selected:
        f=pd.read_parquet(root/f'ml/features/{run}.parquet');y=pd.read_parquet(root/f'ml/targets/{run}.parquet')
        f=f.merge(y[['run_id','assembly_id','timestamp','partition']],on=['run_id','assembly_id','timestamp'],validate='one_to_one')
        f=f[f.timestamp.ge(lo)&f.timestamp.lt(hi)].copy()
        f['evaluable']=mascara_decision(f,partition,modo)
        f['score']=np.nan;frames.append(f)
        tele=pd.read_parquet(root/f'data/telemetria/{run}.parquet')
        hours[run]=int((tele.timestamp.ge(lo)&tele.timestamp.lt(hi)&tele.rolling_state.isin(['arranque','sin_carga','laminacion','desaceleracion'])).sum())/12
        eligible=f.eligible_operation.sum()
        coverage.append(dict(run_id=run,decision_slots=len(f),evaluable_slots=int(f.evaluable.sum()),eligible_slots=int(eligible),coverage_eligible=float(f.evaluable.sum()/eligible) if eligible else None))
    return pd.concat(frames,ignore_index=True),events,maint,{r:hi for r in selected},hours,pd.DataFrame(coverage)

def metricas_probabilidad(y,p):
    from sklearn.metrics import average_precision_score,brier_score_loss
    y=np.asarray(y,dtype=float);p=np.asarray(p,dtype=float);m=np.isfinite(y)
    if not np.isfinite(p[m]).all() or ((p[m]<0)|(p[m]>1)).any():raise ValueError('Probabilidades entre 0 y 1')
    if not set(y[m])<= {0,1} or not m.any():raise ValueError('Objetivo inválido')
    bins=[]
    for lo in np.arange(0,1,.1):
        q=m&(p>=lo)&((p<lo+.1) if lo<.9 else (p<=1))
        if q.any():bins.append(dict(n=int(q.sum()),predicted=float(p[q].mean()),observed=float(y[q].mean())))
    return dict(pr_auc=float(average_precision_score(y[m],p[m])) if len(set(y[m]))==2 else None,brier=float(brier_score_loss(y[m],p[m])),calibration=bins)

def bootstrap_por_mundo(rows,reps=2000,seed=20261105):
    """IC agrupado de sensibilidad y falsas alarmas; variabilidad sintética, no industrial."""
    if len(rows)<2:return None
    rng=np.random.default_rng(seed);vals=[]
    for _ in range(reps):
        b=rows.iloc[rng.integers(0,len(rows),len(rows))];n=b.events.sum();h=b.operating_hours.sum()
        vals.append([b.detected_events.sum()/n if n else np.nan,b.false_alerts.sum()*1000/h if h else np.nan])
    return dict(recall_95=np.nanquantile(np.array(vals)[:,0],[.025,.975]).tolist(),false_per_1000h_95=np.nanquantile(np.array(vals)[:,1],[.025,.975]).tolist())

def seleccionar_politica(results,budget=1):
    if not results.partition.eq('validation').all():raise ValueError('Selección solo validación')
    ok=results[results.false_per_1000h.le(budget)&results.recall.notna()]
    return None if ok.empty else ok.sort_values(['recall','false_per_1000h','policy_id'],ascending=[False,True,True]).iloc[0].to_dict()

def planes_asof(plans,cutoff):
    p=plans[plans.known_at.le(cutoff)]
    return p.sort_values(['known_at','revision']).drop_duplicates(['run_id','plan_id'],keep='last').reset_index(drop=True)

def resumen_evaluacion(alert_details,world_metrics,coverage):
    n=world_metrics.events.sum();h=world_metrics.operating_hours.sum()
    lead=alert_details.loc[alert_details.status.eq('util'),'lead_minutes']
    eligible=coverage.eligible_slots.sum();ev=coverage.evaluable_slots.sum()
    return dict(events=int(n),detected_events=int(world_metrics.detected_events.sum()),
        recall=float(world_metrics.detected_events.sum()/n) if n else None,
        false_per_1000h=float(world_metrics.false_alerts.sum()*1000/h) if h else None,
        operating_hours=float(h),coverage_eligible=float(ev/eligible) if eligible else None,
        abstention_eligible=float(1-ev/eligible) if eligible else None,
        alert_status_counts=alert_details.status.value_counts().to_dict(),
        useful_lead_minutes_quantiles=lead.quantile([.1,.5,.9]).to_dict() if len(lead) else {},
        uncertainty=bootstrap_por_mundo(world_metrics))

def comparar_pareado(model,baseline,reps=2000,seed=20261105,budget=1,min_gain=.05):
    """Mismos mundos, eventos y exposición; sin fingir independencia entre filas."""
    a=model.sort_values('run_id').reset_index(drop=True);b=baseline.sort_values('run_id').reset_index(drop=True)
    if len(a)<2 or not a[['run_id','events','operating_hours']].equals(b[['run_id','events','operating_hours']]):raise ValueError('Cohortes pareadas incompatibles')
    if not a.events.sum():return dict(conclusive=False,reason='sin_eventos')
    rng=np.random.default_rng(seed);delta=[]
    for _ in range(reps):
        ix=rng.integers(0,len(a),len(a));n=a.iloc[ix].events.sum()
        if n:delta.append((a.iloc[ix].detected_events.sum()-b.iloc[ix].detected_events.sum())/n)
    ci=np.quantile(delta,[.025,.975]).tolist();gain=(a.detected_events.sum()-b.detected_events.sum())/a.events.sum()
    rates=[x.false_alerts.sum()*1000/x.operating_hours.sum() if x.operating_hours.sum() else np.inf for x in [a,b]]
    return dict(recall_gain=float(gain),recall_gain_95=ci,model_false_per_1000h=float(rates[0]),baseline_false_per_1000h=float(rates[1]),
        synthetic_success=bool(gain>=min_gain and ci[0]>0 and max(rates)<=budget),scope='Comparación sintética; no evidencia de ahorro industrial')
