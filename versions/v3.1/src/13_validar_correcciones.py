"""Cierre de hallazgos con datos regenerados; no interpreta salud como predictor."""
import json,hashlib,importlib.util
import numpy as np
import pandas as pd
from comun import ROOT,KEY,SIGNALS,dump
from preparacion_ml import referencia_observable,cargar_particion,folds_temporales,preprocesador,comparadores_sin_ajustar
from protocolo_evaluacion import planes_asof,construir_cohorte

def main():
    r=ROOT;c=json.loads((r/'config/escenario.json').read_text());tests=[]
    def ck(n,v,detail=''):
        tests.append(dict(test=n,passed=bool(v),detail=detail))
        if not v:print('FALLO',n,detail,flush=True)
    frozen=json.loads((r/'config/diseno_prerregistrado.json').read_text())
    ck('Configuración congelada antes de generar',hashlib.sha256((r/'config/escenario.json').read_bytes()).hexdigest()==frozen['config_sha256'])
    plans=pd.read_parquet(r/'data/plan_mantenimiento.parquet');maint=pd.read_parquet(r/'data/mantenimiento.parquet')
    ck('PK revisiones',not plans.duplicated(['run_id','plan_id','revision']).any())
    ck('Intervención real conocida al inicio',maint.known_at.equals(maint.start))
    ck('Hora desconocida al aplazar',plans.loc[plans.status.eq('aplazado_correctivo'),'scheduled_start'].isna().all())
    delays=plans[plans.status.eq('aplazado_correctivo')]
    causality=[]
    for p in delays.itertuples():
        causal=maint[maint.run_id.eq(p.run_id)&maint.kind.eq('correctivo')&maint.start.le(p.known_at)&maint.end.gt(p.known_at)]
        causality.append(len(causal)==1)
    ck('Aplazamientos causados por correctivo ya ocurrido',all(causality),str(len(delays))+' aplazamientos')
    for (run,pid),g in plans.groupby(['run_id','plan_id']):
        g=g.sort_values('revision')
        ck(pid+' cronología',g.revision.tolist()==list(range(1,len(g)+1)) and g.known_at.is_monotonic_increasing and g.iloc[0].status=='previsto')
        if (g.status=='iniciado').any():
            last=g.iloc[-1];ck(pid+' inicio real',last.known_at==last.scheduled_start and ((maint.run_id==run)&(maint.kind=='preventivo')&(maint.start==last.scheduled_start)).sum()==1)
    for cut in [pd.Timestamp(c['start'])+pd.Timedelta(days=d) for d in [20,100,200,364]]:
        before=planes_asof(plans,cut);changed=plans.copy();changed.loc[changed.known_at>cut,'scheduled_start']=cut+pd.Timedelta(days=900)
        ck('Plan inmune a futuro '+str(cut.date()),before.equals(planes_asof(changed,cut)))
    parts=pd.read_csv(r/'resultados/particiones.csv')
    ck('Excluidas utilizables cero',parts.loc[parts.partition.eq('excluida'),'usable_rows'].eq(0).all())
    ck('Conteo calidad separado',parts.quality_label_rows.ge(parts.usable_rows).all())
    rows=[];refs=[];fullkeys=[]
    for p in sorted((r/'ml/features').glob('*.parquet')):
        f=pd.read_parquet(p);y=pd.read_parquet(r/'ml/targets'/p.name);tr=pd.read_parquet(r/'sim_truth/estado_latente'/p.name)
        tele=pd.read_parquet(r/'data/telemetria'/p.name)
        ck(p.stem+' referencia observable exacta',np.array_equal(referencia_observable(f,y.partition),y.if_reference_observable))
        ck(p.stem+' referencia nunca fuera train',not (y.if_reference_observable&~y.partition.eq('train')).any())
        for name,col in [('observable','if_reference_observable'),('ideal','healthy_reference_if')]:
            sel=y[col];refs.append(dict(run_id=p.stem,reference=name,rows=int(sel.sum()),known_positive_24h=int(y.loc[sel,'y24'].eq(1).sum()),unknown_label=int(y.loc[sel,'y24'].isna().sum())))
        active=tele.rolling_state.isin(['arranque','sin_carga','laminacion','desaceleracion'])
        ev=pd.read_parquet(r/'data/fallos.parquet');n=ev.run_id.eq(p.stem).sum()
        rows.append(dict(run_id=p.stem,scenario=c['run_specs'][int(p.stem[1:])-1]['scenario'],normal_fraction=tr.health_state.eq('normal').mean(),degraded_fraction=tr.health_state.eq('degradacion').mean(),failures=int(n),operating_hours=active.sum()/12,failures_per_1000h=n*1000/(active.sum()/12)))
        # Reconstrucción directa del último servicio conocido para 20 momentos.
        m=maint[maint.run_id.eq(p.stem)]
        for i in np.linspace(1,len(tele)-1,20,dtype=int):
            row=tele.iloc[i];known=m[(m.result_available_at<=row.timestamp)&m.completed_operating_hours.notna()].sort_values('result_available_at')
            hours=active.iloc[:i].sum()/12
            expected=hours-(known.iloc[-1].completed_operating_hours if len(known) else 0)
            ck(p.stem+' historial '+str(i),np.isclose(row.run_hours_since_service,expected,atol=.01))
        fullkeys.append(f.loc[y.partition.eq('train')&f.evaluation_status.eq('evaluable')&y.y24.notna(),KEY])
    health=pd.DataFrame(rows);health.to_csv(r/'resultados/escenarios_salud.csv',index=False)
    pd.DataFrame(refs).to_csv(r/'resultados/referencias_if.csv',index=False)
    ck('Escenarios largos menos fallos, sin retocar semilla',health.loc[health.scenario.eq('base_vida_larga'),'failures'].mean()<health.loc[health.scenario.eq('base_degradacion'),'failures'].mean())
    ck('Escenarios largos mayor proporción normal',health.loc[health.scenario.eq('base_vida_larga'),'normal_fraction'].mean()>health.loc[health.scenario.eq('base_degradacion'),'normal_fraction'].mean())
    incidents=pd.read_parquet(r/'sim_truth/incidencias_sensores.parquet')
    ck('Pérdidas correlacionadas presentes',incidents.kind.eq('sin_datos_correlacionada').any())
    counts=incidents.groupby(['run_id','sensor_id','kind']).size()
    ck('Incidencias no exactamente una por clase',counts.nunique()>1)
    ck('Calendario no periódico de 28 días',plans[plans.revision.eq(1)].sort_values(['run_id','scheduled_start']).groupby('run_id').scheduled_start.diff().dropna().nunique()>1)
    keys=pd.concat(fullkeys).sort_values(['timestamp','run_id']).reset_index(drop=True)
    eps=pd.read_parquet(r/'sim_truth/episodios.parquet');foldrows=[]
    for i,(a,b) in enumerate(folds_temporales(keys,eps),1):
        ck('Fold '+str(i)+' no vacío',len(a)>0 and len(b)>0)
        ck('Fold '+str(i)+' fechas comunes y purga',keys.iloc[a].timestamp.max()+pd.Timedelta(hours=28)<keys.iloc[b].timestamp.min())
        foldrows.append(dict(fold=i,train_rows=len(a),validation_rows=len(b),train_end=str(keys.iloc[a].timestamp.max()),validation_start=str(keys.iloc[b].timestamp.min())))
    dump(foldrows,r/'resultados/folds_temporales.json')
    x,y,k=cargar_particion('train');contract=json.loads((r/'ml/columnas_modelo.json').read_text())
    ck('Cargador lista permitida',list(x)==contract['numeric']+contract['categorical'] and not set(x)&set(contract['forbidden']))
    ck('Cargador cuenta exacta',len(x)==parts.loc[parts.partition.eq('train'),'usable_rows'].sum())
    # Ajuste SOLO de preprocesador sobre fixture de dos filas, nunca sobre dataset.
    fixture=pd.DataFrame({col:[1.,np.nan] for col in contract['numeric']})
    for col in contract['categorical']:fixture[col]=['a',np.nan]
    pre=preprocesador();pre.fit(fixture)
    ck('Ausentes y categorías nuevas admitidos en fixture',np.isfinite(pre.transform(fixture.assign(steel_family='nueva'))).all())
    ck('Comparadores preparados sin ajustar',set(comparadores_sin_ajustar())=={'constante','condicion','historial_carga'})
    cohort=[]
    for part in ['train','validation','test','stress']:
        d,e,m,ends,h,coverage=construir_cohorte(r,part)
        coverage.to_csv(r/f'resultados/cobertura_{part}.csv',index=False)
        ck(part+' score aún no calculado',d.score.isna().all())
        for mode,g in e.groupby('mode'):
            cohort.append(dict(partition=part,mode=mode,events=len(g),worlds=g.run_id.nunique(),descriptive_only=len(g)<20))
    pd.DataFrame(cohort).to_csv(r/'resultados/cohortes_eventos.csv',index=False)
    result=dict(checks=len(tests),passed=sum(t['passed'] for t in tests),failed=sum(not t['passed'] for t in tests),tests=tests,models_trained=False)
    dump(result,r/'resultados/cierre_correcciones.json');print({k:v for k,v in result.items() if k!='tests'})
    if result['failed']:raise SystemExit(1)
if __name__=='__main__':main()
