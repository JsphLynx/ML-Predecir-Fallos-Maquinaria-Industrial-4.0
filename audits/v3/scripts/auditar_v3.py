"""Auditoría independiente. No cambia el dataset ni ajusta modelos.
Uso: python auditar_v3.py --root RUTA_DATASET --out RUTA_EVIDENCIAS
"""
import argparse, hashlib, json, sys, platform
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

def audit(root,out):
    out.mkdir(parents=True,exist_ok=True)
    checks=[]
    def check(name,ok,detail=''):
        checks.append({'test':name,'passed':bool(ok),'detail':str(detail)})
    c=json.loads((root/'config/escenario.json').read_text())
    allowed=json.loads((root/'ml/columnas_modelo.json').read_text())
    pred=allowed['numeric']+allowed['categorical'];keys=['run_id','assembly_id','timestamp']
    sensors=pd.read_parquet(root/'data/sensores.parquet')
    signals=list(sensors.variable);ranges=sensors.set_index('variable')[['min_demo','max_demo']]
    events=pd.read_parquet(root/'data/fallos.parquet');maint=pd.read_parquet(root/'data/mantenimiento.parquet')
    inc=pd.read_parquet(root/'sim_truth/incidencias_sensores.parquet')
    ep=pd.read_parquet(root/'sim_truth/episodios.parquet')
    end=pd.Timestamp(c['start'])+pd.Timedelta(days=c['days'])
    hashes=json.loads((root/'SHA256.json').read_text());bad=[]
    for name,h in hashes.items():
        p=root/name
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:bad.append(name)
    check('SHA256: todos los archivos declarados',not bad,f'{len(hashes)} archivos; diferencias={bad}')
    check('Allowlist disjunta de prohibidas',not set(pred)&set(allowed['forbidden']))
    # Causal meaning of maintenance scheduling: delayed actual start cannot have
    # been announced before the unplanned corrective event that caused it.
    delayed=[]
    for run,group in maint[maint.kind.eq('preventivo')].groupby('run_id'):
        for i,pm in enumerate(group.sort_values('start').itertuples(),1):
            due=pd.Timestamp(c['start'])+pd.Timedelta(days=i*c['pm_interval_days'])
            causes=maint[maint.run_id.eq(run)&maint.kind.eq('correctivo')&maint.start.le(due)&maint.end.gt(due)]
            if pm.start>due and len(causes):
                cause=causes.iloc[0]
                delayed.append(dict(run_id=run,maintenance_id=pm.maintenance_id,planned_due=str(due),actual_start=str(pm.start),known_at=str(pm.known_at),cause_start=str(cause.start),delay_hours=(pm.start-due).total_seconds()/3600))
                check(pm.maintenance_id+' conocimiento de reprogramación causal',pm.known_at>=cause.start,
                    'known_at antecede al fallo imprevisto causante; campo fuera de la allowlist actual')
    pd.DataFrame(delayed).to_csv(out/'preventivos_pospuestos.csv',index=False)
    frames=[];rstats=[];ops=[];qstats=[];physical=[];incident_stats=[];independence=[]
    for n in range(1,9):
        run=f'R{n:02}';print('Auditando',run,flush=True)
        t=pd.read_parquet(root/f'data/telemetria/{run}.parquet')
        f=pd.read_parquet(root/f'ml/features/{run}.parquet')
        y=pd.read_parquet(root/f'ml/targets/{run}.parquet')
        tr=pd.read_parquet(root/f'sim_truth/estado_latente/{run}.parquet')
        e=events[events.run_id.eq(run)].sort_values('start');m=maint[maint.run_id.eq(run)]
        check(run+' claves y orden',all(not v.duplicated(keys).any() and v.timestamp.is_monotonic_increasing for v in [t,f,y,tr]))
        check(run+' rejillas completas',len(t)==365*288 and len(f)==365*96 and t.timestamp.diff().dropna().eq(pd.Timedelta(minutes=5)).all() and f.timestamp.diff().dropna().eq(pd.Timedelta(minutes=15)).all())
        z=f.merge(y,on=keys,validate='one_to_one');z=z.merge(tr[keys+['health_state']],on=keys,validate='one_to_one')
        z['usable']=z.partition.ne('excluida')&z.evaluation_status.eq('evaluable')&z.y24.notna()
        # Independent vectorized future-event/maintenance oracle, not imported from generator.
        ts=f.timestamp.astype('int64').to_numpy();ei=e.start.astype('int64').to_numpy()
        pi=m.loc[m.kind.eq('preventivo'),'start'].sort_values().astype('int64').to_numpy()
        ne=np.r_[ei,np.iinfo('int64').max][np.searchsorted(ei,ts,side='right')]
        np_=np.r_[pi,np.iinfo('int64').max][np.searchsorted(pi,ts,side='right')]
        lim=ts+pd.Timedelta(hours=24).value
        ex=np.zeros(len(f));pos=(ne<=lim)&(ne<np_)&(ne<end.value)
        ex[((lim>=end.value)|(np_<=lim))&~pos]=np.nan;ex[pos]=1
        ex[~f.rolling_state.isin(c['eligible_regimes']).to_numpy()]=np.nan
        check(run+' y24 oráculo independiente',np.allclose(ex,y.y24.to_numpy(float,na_value=np.nan),equal_nan=True))
        check(run+' disponibles antes de decisión',f.source_available_at_max.dropna().le(f.loc[f.source_available_at_max.notna(),'timestamp']).all())
        # Direct statistics, all sensors, 12 cutoffs/run, both windows; no builder reused.
        errors=[]
        for ix in np.linspace(20,len(f)-1,12,dtype=int):
            row=f.iloc[ix];cut=row.timestamp
            for w in [30,240]:
                hist=t[(t.timestamp>cut-pd.Timedelta(minutes=w))&(t.timestamp<=cut)&(t.available_at<=cut)]
                for col in signals:
                    a=hist.loc[hist[col].between(*ranges.loc[col]),['timestamp',col]].dropna()
                    vals=a[col].to_numpy(float);x=(a.timestamp-cut).dt.total_seconds().to_numpy()/3600
                    expect=[vals.mean() if len(vals) else np.nan,vals.std(ddof=1) if len(vals)>1 else np.nan,np.polyfit(x,vals,1)[0] if len(vals)>1 else np.nan]
                    got=[row[f'{col}_{s}_{w}m'] for s in ['mean','std','slope_per_h']]
                    if not np.allclose(expect,got,rtol=5e-4,atol=2e-3,equal_nan=True):errors.append((ix,w,col,expect,got))
        check(run+' estadísticos causales directos',not errors,f'{12*2*15*3} valores; diferencias={len(errors)}')
        # Service context reconstructed solely from completed results and observed operation.
        active=t.rolling_state.isin(['arranque','sin_carga','laminacion','desaceleracion'])
        cum=active.astype(int).cumsum().shift(1,fill_value=0).to_numpy()*5/60
        completed=m[m.completed_operating_hours.notna()].sort_values('result_available_at')
        ci=np.searchsorted(completed.result_available_at.astype('int64'),t.timestamp.astype('int64'),side='right')-1
        prev=np.r_[0,completed.completed_operating_hours.to_numpy()][ci+1]
        check(run+' historia de mantenimiento causal',np.allclose(t.run_hours_since_service,cum-prev,rtol=1e-4,atol=1e-3))
        # Per-event opportunity = data availability, NOT achieved detection.
        for ev in e.itertuples():
            for part in ['train','validation','test','stress']:
                g=z[z.partition.eq(part)&z.usable&z.event_id.eq(ev.event_id).fillna(False)]
                if len(g)==0:continue
                eligible=g[g.timestamp<=ev.start-pd.Timedelta(minutes=60)]
                times=eligible.timestamp.astype('int64').to_numpy()
                possible=any(((times>=tt-pd.Timedelta(minutes=60).value)&(times<=tt)).sum()>=3 for tt in times)
                ops.append(dict(run_id=run,event_id=ev.event_id,partition=part,onset=ev.onset,mode=ev.mode,positive_rows=len(g),rows_lead_60m=len(eligible),persistence_3_of_5_possible=bool(possible),max_lead_hours=float((ev.start-g.timestamp.min()).total_seconds()/3600)))
        # How many states have reliable data, and healthy reference coverage.
        for part,g in z.groupby('partition'):
            u=g[g.usable];ref=g[g.healthy_reference_if]
            rstats.append(dict(run_id=run,partition=part,rows=len(g),usable=len(u),positive_rows=int(u.y24.sum()),positive_events=int(u.event_id.nunique()),positive_pct=float(u.y24.mean()*100) if len(u) else None,healthy_if=len(ref),reference_start=str(ref.timestamp.min()),reference_end=str(ref.timestamp.max())))
        for state,g in z.groupby('health_state'):
            qstats.append(dict(run_id=run,health_state=state,rows=len(g),evaluable=int(g.evaluation_status.eq('evaluable').sum())))
        for k,g in inc[inc.run_id.eq(run)].groupby('kind'):
            mask=pd.Series(False,index=z.index)
            for it in g.itertuples():mask|=z.timestamp.ge(it.start)&z.timestamp.lt(it.end)
            a=z[mask]
            incident_stats.append(dict(run_id=run,kind=k,decisions_in_incident=len(a),evaluable_in_incident=int(a.evaluation_status.eq('evaluable').sum())))
        # Physically impossible raw readings must be attributable to injected acquisition faults.
        faultmask=t.rolling_state.isin(['parado','fallo','mantenimiento'])
        corrupt=np.zeros(len(t),bool)
        for it in inc[inc.run_id.eq(run)&inc.sensor_id.eq('S-speed_rpm')].itertuples():
            corrupt|=(t.timestamp.ge(it.start)&t.timestamp.lt(it.end)).to_numpy()
        check(run+' rpm parado sin incidencia = 0',t.loc[faultmask&~corrupt,'speed_rpm'].dropna().eq(0).all())
        physical.append(dict(run_id=run,failures=len(e),sudden=int(e.onset.eq('subito').sum()),operating_hours=float(active.sum()/12),failures_per_1000_operating_h=float(len(e)/(active.sum()/12)*1000),degraded_fraction=float(tr.health_state.eq('degradacion').mean()),normal_fraction=float(tr.health_state.eq('normal').mean()),median_repair_hours=float((e.end-e.start).dt.total_seconds().median()/3600)))
        frames.append(z)
    allz=pd.concat(frames,ignore_index=True)
    eo=pd.DataFrame(ops)
    check('Un evento positivo no se comparte entre particiones',not eo.groupby(['run_id','event_id']).partition.nunique().gt(1).any())
    check('Estrés no usado como entrenamiento',not allz.loc[allz.run_id.isin(['R07','R08']),'partition'].isin(['train','validation','test']).any())
    train=allz[allz.partition.eq('train')&allz.usable]
    # Descriptive discrimination only on train; no threshold fitted and no held-out scoring.
    discrimination=[]
    for col in allowed['numeric']:
        a=train[[col,'y24']].dropna()
        if a[col].nunique()>1:
            auc=roc_auc_score(a.y24.astype(int),a[col]);ap=average_precision_score(a.y24.astype(int),a[col])
            discrimination.append(dict(feature=col,n=len(a),auc_increasing=float(auc),absolute_separation_auc=float(max(auc,1-auc)),average_precision_increasing=float(ap)))
    ds=pd.DataFrame(discrimination).sort_values('absolute_separation_auc',ascending=False)
    check('No predictor numérico constante en train',all(train[x].nunique(dropna=True)>1 for x in allowed['numeric']))
    cross=train[allowed['numeric']].isna().mean().sort_values(ascending=False)
    cross.rename('missing_fraction').to_csv(out/'ausencias_predictores_train.csv')
    counts=allz.groupby(['partition','evaluation_status'],observed=True).size().reset_index(name='n')
    for name,df in [('particiones_independientes',pd.DataFrame(rstats)),('oportunidades_eventos',eo),('calidad_por_salud',pd.DataFrame(qstats)),('escenarios',pd.DataFrame(physical)),('incidencias_y_evaluacion',pd.DataFrame(incident_stats)),('discriminacion_univariante_solo_train',ds),('estados_por_particion',counts)]:df.to_csv(out/(name+'.csv'),index=False)
    summary=dict(checks=len(checks),passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),tests=checks,hash_files=len(hashes),hash_mismatches=bad,
        telemetry_rows=840960,decision_rows=len(allz),failures=len(events),train_positive_pct=float(train.y24.mean()*100),healthy_reference=int(allz.healthy_reference_if.sum()),
        total_evaluable=int(allz.evaluation_status.eq('evaluable').sum()),evaluable_excluded=int((allz.partition.eq('excluida')&allz.evaluation_status.eq('evaluable')&allz.y24.notna()).sum()),
        train_predictors_with_missing=int((cross>0).sum()),python=sys.version,platform=platform.platform(),numpy=np.__version__,pandas=pd.__version__,models_trained=False,
        heldout_use='Structural audit only. No held-out model/threshold performance computed.')
    (out/'auditoria_independiente.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str))
    print(json.dumps({k:v for k,v in summary.items() if k!='tests'},ensure_ascii=False,default=str))
    if summary['failed']:print('PRUEBAS FALLIDAS:',[x for x in checks if not x['passed']])
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();audit(a.root,a.out)
