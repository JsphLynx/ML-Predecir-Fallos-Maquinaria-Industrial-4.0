"""Pruebas de datos, etiquetas y disponibilidad temporal. No entrena modelos.
Reconstruye objetivos por intervalos y compara snapshots con prefijos causales.
"""
import argparse
import importlib.util
from pathlib import Path
import json
import numpy as np
import pandas as pd
from comun import ROOT, KEY, SIGNALS, ESSENTIAL, ASSEMBLY, DE, NDE, MOTOR, config, dump, sha

spec=importlib.util.spec_from_file_location('features_builder',Path(__file__).with_name('02_construir_variables.py'))
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

def main(root=ROOT):
    root=Path(root);c=config(root/'config/escenario.json');checks=[]
    def check(name, condition, detail=''):
        checks.append(dict(test=name,passed=bool(condition),detail=str(detail)))
        if not condition:print('FALLO:',name,detail,flush=True)
    assets=pd.read_parquet(root/'data/activos.parquet');runs=pd.read_parquet(root/'data/ejecuciones.parquet')
    sensors=pd.read_parquet(root/'data/sensores.parquet');events=pd.read_parquet(root/'data/fallos.parquet')
    maint=pd.read_parquet(root/'data/mantenimiento.parquet')
    incidents=pd.read_parquet(root/'sim_truth/incidencias_sensores.parquet')
    episodes=pd.read_parquet(root/'sim_truth/episodios.parquet');repairs=pd.read_parquet(root/'sim_truth/reparaciones.parquet')
    allowed=json.loads((root/'ml/columnas_modelo.json').read_text(encoding='utf-8'))
    preds=allowed['numeric']+allowed['categorical']
    check('Activos PK y jerarquía',assets.asset_id.is_unique and assets.parent_asset_id.dropna().isin(assets.asset_id).all())
    check('Motor y apoyos distintos',{DE,NDE,MOTOR,ASSEMBLY}<=set(assets.asset_id))
    check('Todo inventario es sintético',assets.is_synthetic.all())
    check('Sensores vinculados',sensors.sensor_id.is_unique and sensors.asset_id.isin(assets.asset_id).all())
    check('Ejecuciones distintas',runs.run_id.is_unique and len(runs)==c['runs'])
    check('Semillas independientes por índice',runs.subseed_index.is_unique)
    for name,df,idcol in [('fallos',events,'event_id'),('mantenimiento',maint,'maintenance_id'),('incidencias',incidents,'incident_id'),('episodios',episodes,'episode_id')]:
        check(name+' claves',not df.duplicated(['run_id',idcol]).any() and df[idcol].notna().all())
        check(name+' ejecuciones',df.run_id.isin(runs.run_id).all())
        check(name+' intervalos',df.end.gt(df.start).all())
    check('Eventos en motor/apoyos',events.asset_id.isin([DE,NDE,MOTOR]).all())
    check('Un correctivo por evento',maint.loc[maint.kind=='correctivo','event_id'].is_unique and set(maint.event_id.dropna())==set(events.event_id))
    check('Diagnóstico no anterior al fallo',events.diagnosis_available_at.ge(events.start).all())
    check('Resultado mantenimiento no disponible antes del cierre',maint.result_available_at.ge(maint.end).all())
    check('Reparación reduce daño',repairs.damage_after.le(repairs.damage_before).all())
    check('Sustituciones y mejoras parciales presentes',{'sustitucion','reparacion_parcial','mejora_parcial'}<=set(repairs.action))
    check('Existen fallos súbitos y progresivos',set(events.onset)=={'subito','progresivo'})
    check('Todas las incidencias instrumentales',{'sin_datos','pico','congelado','deriva'}<=set(incidents.kind))
    check('Predictores con lista explícita',not(set(preds)&set(allowed['forbidden'])) and len(preds)==len(set(preds)))
    all_targets=[];quality_counts={};independent_events=[]
    end=pd.Timestamp(c['start'])+pd.Timedelta(days=c['days'])
    b1=pd.Timestamp(c['start'])+pd.Timedelta(days=c['days']*c['train_fraction']);b2=b1+pd.Timedelta(days=c['days']*c['validation_fraction'])
    for run in runs.itertuples():
        r=run.run_id;tele=pd.read_parquet(root/f'data/telemetria/{r}.parquet')
        f=pd.read_parquet(root/f'ml/features/{r}.parquet');y=pd.read_parquet(root/f'ml/targets/{r}.parquet')
        tr=pd.read_parquet(root/f'sim_truth/estado_latente/{r}.parquet')
        ev=events[events.run_id==r];pm=maint[(maint.run_id==r)&(maint.kind=='preventivo')]
        check(r+' cardinalidad telemetría',len(tele)==c['days']*288)
        check(r+' cardinalidad decisiones',len(f)==c['days']*96)
        for name,df in [('tele',tele),('features',f),('targets',y),('truth',tr)]:
            check(r+' '+name+' PK',not df.duplicated(KEY).any() and df[KEY].notna().all().all())
            check(r+' '+name+' run/assembly',df.run_id.eq(r).all() and df.assembly_id.eq(ASSEMBLY).all())
        check(r+' telemetría 5 minutos',tele.timestamp.diff().dropna().eq(pd.Timedelta(minutes=5)).all())
        check(r+' decisiones 15 minutos',f.timestamp.diff().dropna().eq(pd.Timedelta(minutes=15)).all())
        check(r+' UTC',str(tele.timestamp.dt.tz)=='UTC')
        check(r+' latencia no negativa',tele.available_at.ge(tele.timestamp).all())
        check(r+' latencia realmente inyectada',tele.available_at.gt(tele.timestamp).any())
        check(r+' solo disponibilidad pasada',f.source_available_at_max.dropna().le(f.timestamp[f.source_available_at_max.notna()]).all())
        check(r+' sin infinitos',not np.isinf(f.select_dtypes('number').to_numpy(dtype=float,na_value=np.nan)).any())
        check(r+' sensores separados',not tele.bearing_temperature_de_c.equals(tele.bearing_temperature_nde_c))
        check(r+' predictores presentes',set(preds)<=set(f.columns))
        check(r+' verdad no presente en features',not any(x in f for x in ['damage_de','damage_nde','health_state','y24','partition','event_id']))
        merged=f.merge(y.sample(frac=1,random_state=17),on=KEY,validate='one_to_one',indicator=True)
        check(r+' unión por clave robusta a orden',len(merged)==len(f) and merged['_merge'].eq('both').all())
        check(r+' cobertura en rango',f.coverage_min_30m.between(0,1).all())
        evaluable=f.evaluation_status.eq('evaluable')
        check(r+' calidad bloquea evaluación',f.loc[evaluable,'coverage_min_30m'].ge(c['coverage_min']).all() and
            not f.loc[evaluable,'sensor_stale'].any() and f.loc[evaluable,'max_data_age_minutes'].le(c['max_data_age_minutes']).all())
        check(r+' fallo y mantenimiento no evaluados',not f.loc[f.rolling_state.isin(['fallo','mantenimiento']),'evaluation_status'].eq('evaluable').any())
        check(r+' seis regímenes operativos',{'parado','arranque','sin_carga','laminacion','desaceleracion','mantenimiento'}<=set(tele.rolling_state))
        check(r+' receta solo al laminar',tele.loc[tele.rolling_state!='laminacion','coil_id'].isna().all())
        check(r+' familia FK',tele.steel_family.dropna().isin(pd.read_parquet(root/'data/productos.parquet').grado_acero).all())
        check(r+' historia servicio no negativa',tele.run_hours_since_service.ge(0).all())
        # Independent label oracle: compare every row with all event intervals.
        t=f.timestamp;deadline=t+pd.Timedelta(hours=24)
        expected=np.zeros(len(f),dtype=float)
        earliest_pm=pd.Series(end,index=f.index)
        for item in pm.itertuples():
            mask=(item.start>t)&(item.start<earliest_pm);earliest_pm.loc[mask]=item.start
        positives=np.zeros(len(f),bool);ids=np.full(len(f),None,dtype=object)
        for item in ev.sort_values('start',ascending=False).itertuples():
            match=((item.start>t)&(item.start<=deadline)&(item.start<earliest_pm)).to_numpy()
            positives|=match;ids[match]=item.event_id
        censored=((deadline>=end)|((earliest_pm<end)&(earliest_pm<=deadline))).to_numpy()
        expected[censored]=np.nan;expected[positives]=1;expected[~f.eligible_operation.to_numpy()]=np.nan
        check(r+' etiquetas 24h reconstruidas independientemente',np.allclose(expected,y.y24.to_numpy(dtype=float,na_value=np.nan),equal_nan=True))
        check(r+' censura coherente',y.y24.isna().equals(y.censor_reason.ne('ninguna')))
        pos=y.y24.eq(1).fillna(False).to_numpy(dtype=bool)
        check(r+' evento objetivo corresponde',np.array_equal(y.loc[pos,'event_id'].to_numpy(),ids[pos]))
        check(r+' cero futuro conocido en entradas',not set(allowed['forbidden'])&set(preds))
        for part,bound in [('train',b1),('validation',b2)]:
            selected=y.partition.eq(part)
            check(r+' purga '+part,(y.loc[selected,'timestamp']+pd.Timedelta(hours=28)<bound).all())
        if run.scenario.startswith('stress'):
            check(r+' estrés nunca entrena',set(y.partition)<=set(['stress','excluida']))
        else:
            for boundary in [b1,b2]:
                for ep in episodes[(episodes.run_id==r)&(episodes.start<boundary)&(episodes.end>boundary)].itertuples():
                    inside=(y.timestamp>=ep.start-pd.Timedelta(hours=24))&(y.timestamp<ep.end)
                    check(ep.episode_id+' excluido al cruzar corte',y.loc[inside,'partition'].eq('excluida').all())
        # Every failure starts after an operating interval; matching fault row exists.
        event_ok=True
        for e in ev.itertuples():
            now=tele.loc[tele.timestamp==e.start,'rolling_state'];prev=tele.loc[tele.timestamp==e.start-pd.Timedelta(minutes=5),'rolling_state']
            event_ok &= len(now)==1 and now.iloc[0]=='fallo' and len(prev)==1 and prev.iloc[0] in ['arranque','sin_carga','laminacion','desaceleracion']
            selected=merged[merged.event_id==e.event_id]
            for part,g in selected.groupby('partition'):
                if part not in ['excluida']:
                    independent_events.append(dict(run_id=r,event_id=e.event_id,partition=part,
                        evaluable=bool(g.evaluation_status.eq('evaluable').any()),onset=e.onset,mode=e.mode))
        check(r+' fallos precedidos de operación',event_ok)
        check(r+' referencia IF solo train evaluable',not(y.healthy_reference_if&(~y.partition.eq('train')|~evaluable)).any())
        # Prefix recomputation tests actual implementation dependence on the future.
        for offset in [99,1001,4001]:
            i=min(offset,len(f)-1);cut=f.timestamp.iloc[i]
            prefix=builder.build_features(tele[tele.timestamp<=cut].copy(),c).iloc[-1]
            stored=f.iloc[i]
            comparable=allowed['numeric']+['coverage_min_30m','max_data_age_minutes']
            check(r+f' prefijo causal {i}',np.allclose(prefix[comparable].to_numpy(float),stored[comparable].to_numpy(float),rtol=2e-5,atol=1e-4,equal_nan=True))
        # Direct mean from observed/available samples, without using rolling builder.
        ok=True
        for row in f.iloc[::max(1,len(f)//30)].itertuples():
            h=tele[(tele.timestamp>row.timestamp-pd.Timedelta(minutes=30))&(tele.timestamp<=row.timestamp)&(tele.available_at<=row.timestamp)]
            s=h.vibration_de_mm_s.where(h.vibration_de_mm_s.between(0,40))
            ok &= np.isclose(s.mean(),row.vibration_de_mm_s_mean_30m,rtol=1e-5,equal_nan=True)
        check(r+' media causal independiente',ok)
        all_targets.append(merged.drop(columns='_merge'))
        for k,v in f.evaluation_status.value_counts().items():quality_counts[k]=quality_counts.get(k,0)+int(v)
    full=pd.concat(all_targets,ignore_index=True)
    for part in ['train','validation','test','stress']:
        sample=full[(full.partition==part)&full.evaluation_status.eq('evaluable')&full.y24.notna()]
        check(part+' tiene positivos y negativos',sample.y24.nunique()==2)
        check(part+' eventos distintos suficientes para calcular métricas básicas',sample.event_id.nunique()>=2,str(sample.event_id.nunique())+' eventos; no acredita potencia estadística')
    # Mutation test: inaccessible readings must not change this decision.
    tele=pd.read_parquet(root/'data/telemetria/R01.parquet').iloc[:300].copy()
    tele.loc[tele.index[-3:],'available_at']=tele.timestamp.iloc[-1]+pd.Timedelta(hours=5)
    before=builder.build_features(tele,c)
    changed=tele.copy();changed.loc[changed.index[-3:],list(SIGNALS)]=1e9
    after=builder.build_features(changed,c)
    check('Lecturas no disponibles no alteran features',before.equals(after))
    # Snapshot control: quality must fail on a missing essential channel.
    missing=tele.copy();missing.loc[missing.index[-60:],'vibration_de_mm_s']=np.nan
    mf=builder.build_features(missing,c)
    check('Ausencia esencial produce abstención',mf.iloc[-1].evaluation_status!='evaluable')
    event_report=pd.DataFrame(independent_events).drop_duplicates(['run_id','event_id','partition'])
    event_report.to_csv(root/'resultados/eventos_por_particion.csv',index=False)
    result=dict(checks=len(checks),passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),
        quality_status=quality_counts,scope='Consistencia y causalidad temporal sintéticas. No validación física/industrial ni entrenamiento.',tests=checks)
    dump(result,root/'resultados/validacion.json')
    print(json.dumps({k:v for k,v in result.items() if k!='tests'},ensure_ascii=False),flush=True)
    if result['failed']:raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));a=p.parse_args();main(a.root)
