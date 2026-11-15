"""Pruebas de regresión con fixtures conocidos. No entrena XGBoost ni IF."""
import json
import numpy as np
import pandas as pd
from comun import ROOT,dump
from protocolo_evaluacion import *
from preparacion_ml import referencia_observable

def main():
    tests=[]
    def ck(name,cond):
        tests.append(dict(test=name,passed=bool(cond)))
        if not cond:raise AssertionError(name)
    def rejects(name,fn):
        try:fn()
        except (ValueError,TypeError):ck(name,True)
        else:ck(name,False)
    zero=pd.Timestamp('2024-01-01',tz='UTC')
    def frame(scores):
        return pd.DataFrame(dict(run_id='R',assembly_id='M',timestamp=pd.date_range(zero,periods=len(scores),freq='15min'),score=scores,evaluable=True,rolling_state='laminacion'))
    d=frame([.9,.9,.9,.1,.1,.1,.1]);a=generar_alertas(d,.8,.3)
    ck('Abre en tercer voto',len(a)==1 and a.opened_at.iloc[0]==zero+pd.Timedelta(minutes=30))
    ck('Cierra tras cuatro recuperaciones',a.closed_at.iloc[0]==zero+pd.Timedelta(minutes=90))
    ck('Dos votos no abren',generar_alertas(frame([.9,.9,.1]),.8,.3).empty)
    d=frame([.9,.9,.9,.1,np.nan,.1,.1,.1]);d.loc[4,'evaluable']=False
    ck('Abstención no recupera',pd.isna(generar_alertas(d,.8,.3).closed_at.iloc[0]))
    d=frame([.9]*9).iloc[[0,1,8]]
    ck('Huecos no comprimen cinco slots',generar_alertas(d,.8,.3).empty)
    d=frame([.9]*5);d.loc[3,'rolling_state']='mantenimiento'
    ck('Intervención cierra',generar_alertas(d,.8,.3).close_reason.iloc[0]=='intervencion_o_fallo')
    ck('Sin datos no abre',generar_alertas(frame([np.nan]*9),.8,.3).empty)
    a=generar_alertas(frame([.9]*102),.8,.3)
    ck('Caduca a las 24 horas',a.close_reason.iloc[0]=='duracion_maxima' and a.closed_at.iloc[0]-a.opened_at.iloc[0]==pd.Timedelta(hours=24))
    rejects('Rechaza duplicados',lambda:generar_alertas(pd.concat([frame([.9]),frame([.9])]),.8,.3))
    d=frame([.9]);d.timestamp+=pd.Timedelta(minutes=1)
    rejects('Rechaza rejilla errónea',lambda:generar_alertas(d,.8,.3))
    rejects('Histeresis ordenada',lambda:generar_alertas(frame([.9]),.2,.8))
    def ts(h):return zero+pd.Timedelta(hours=h)
    events=pd.DataFrame(dict(run_id=['R','R'],event_id=['E1','E2'],start=[ts(12),ts(60)],mode=['progresivo','subito']))
    alerts=pd.DataFrame(dict(run_id=['R']*5,alert_id=list('abcde'),opened_at=[ts(1),ts(2),ts(11.5),ts(30),ts(90)]))
    pm=pd.DataFrame(columns=['run_id','start'])
    z,metrics,modes=evaluar_eventos(alerts,events,pm,{'R':ts(100)},{'R':100})
    ck('Correspondencia única y censura',z.status.tolist()==['util','duplicada','tardia','falsa','censurada'])
    ck('Denominador todos los eventos',metrics.events.iloc[0]==2 and metrics.detected_events.iloc[0]==1)
    ck('Falsas por exposición',metrics.false_per_1000h.iloc[0]==10)
    ck('Modo sin detección no desaparece',modes.set_index('mode').loc['subito','recall']==0)
    pm=pd.DataFrame(dict(run_id=['R'],start=[ts(5)]))
    ck('Preventivo censura',evaluar_eventos(alerts.iloc[:1],events,pm,{'R':ts(100)},{'R':100})[0].status.iloc[0]=='censurada')
    for lead in [1,24]:
        one=alerts.iloc[:1].copy();one.opened_at=ts(12-lead)
        ck(f'Límite inclusivo {lead}h',evaluar_eventos(one,events,pm.iloc[:0],{'R':ts(100)},{'R':100})[0].status.iloc[0]=='util')
    ck('Sin avisos sensibilidad cero',evaluar_eventos(alerts.iloc[:0],events,pm,{'R':ts(100)},{'R':100})[1].recall.iloc[0]==0)
    ck('Brier conocido',np.isclose(metricas_probabilidad([0,1],[.1,.9])['brier'],.01))
    rejects('Score IF no es probabilidad',lambda:metricas_probabilidad([0,1],[-2,5]))
    options=pd.DataFrame(dict(partition=['validation']*2,policy_id=['a','b'],false_per_1000h=[.5,2],recall=[.5,.9]))
    ck('Selección respeta presupuesto',seleccionar_politica(options)['policy_id']=='a')
    rejects('No selecciona con test',lambda:seleccionar_politica(options.assign(partition='test')))
    ck('Sin política admisible',seleccionar_politica(options.assign(false_per_1000h=5)) is None)
    ck('No IC con un mundo',bootstrap_por_mundo(metrics) is None)
    f=pd.DataFrame(dict(evaluation_status=['evaluable']*3,known_service_type=['correctivo']*3,run_hours_since_service=[5,30,5],coverage_min_30m=[1]*3,quality_code=['ok']*3))
    part=pd.Series(['train','train','test']);ck('Referencia observable selectiva',referencia_observable(f,part).tolist()==[True,False,False])
    changed=f.assign(health_state='fallo',y24=1)
    ck('Referencia inmune a verdad y futuro',referencia_observable(f,part).equals(referencia_observable(changed,part)))
    # Los tres casos exactos de la auditoría original, con versión aplazada sin hora futura.
    for run,due,actual in [('R04','2024-08-12 00:00','2024-08-12 05:15'),('R06','2024-04-22 00:00','2024-04-22 00:55'),('R07','2024-11-04 00:00','2024-11-04 01:55')]:
        due=pd.Timestamp(due,tz='UTC');actual=pd.Timestamp(actual,tz='UTC')
        p=pd.DataFrame(dict(run_id=[run]*3,plan_id=['P']*3,revision=[1,2,3],known_at=[due-pd.Timedelta(days=7),due,actual],scheduled_start=[due,pd.NaT,actual],status=['previsto','aplazado_correctivo','iniciado']))
        ck(run+' regresión no anticipa retraso',planes_asof(p,due-pd.Timedelta(minutes=5)).scheduled_start.iloc[0]==due and pd.isna(planes_asof(p,due).scheduled_start.iloc[0]))
        ck(run+' inicio solo conocido al ocurrir',planes_asof(p,actual).scheduled_start.iloc[0]==actual)
    cov=pd.DataFrame(dict(eligible_slots=[10],evaluable_slots=[8]))
    total=resumen_evaluacion(z,metrics,cov)
    ck('Cobertura no oculta abstenciones',total['coverage_eligible']==.8 and np.isclose(total['abstention_eligible'],.2))
    base=pd.DataFrame(dict(run_id=['A','B','C'],events=[10,10,10],detected_events=[2,2,2],operating_hours=[1000.,1000.,1000.],false_alerts=[0,0,0]))
    better=base.assign(detected_events=4)
    ck('Mejora pareada sintética',comparar_pareado(better,base,reps=100)['synthetic_success'])
    ck('Igualdad no acredita mejora',not comparar_pareado(base,base,reps=100)['synthetic_success'])
    rejects('Rechaza exposiciones no pareadas',lambda:comparar_pareado(better,base.assign(operating_hours=999.)))
    ck('Presupuesto también limita éxito',not comparar_pareado(better.assign(false_alerts=2),base,reps=100)['synthetic_success'])
    sample=pd.DataFrame(dict(evaluation_status=['evaluable','evaluable','dato_antiguo'],partition=['test','excluida','test']))
    ck('Servicio no usa partición retrospectiva',mascara_decision(sample,'test','observable').tolist()==[True,True,False])
    ck('Benchmark conserva exclusiones',mascara_decision(sample,'test','benchmark').tolist()==[True,False,False])
    ck('Servicio inmune a cambio de particiones',mascara_decision(sample,'test').equals(mascara_decision(sample.assign(partition='train'),'test')))
    # Fixture del generador real: provocar colisiones sin modificar la entrega.
    import copy,importlib.util
    from comun import config
    sp=importlib.util.spec_from_file_location('generator_fixture',ROOT/'src/01_generar_dataset.py')
    gen=importlib.util.module_from_spec(sp);sp.loader.exec_module(gen)
    c=copy.deepcopy(config());c.update(days=10,failure_rate_per_hour=.5,sudden_rate_per_hour=.1)
    c['run_specs'][0].update(life_factor=.05,pm_interval_days=1,seed=101)
    c['schedule']['pm_jitter_days']=0
    data=gen.simulate(c,1,pd.read_parquet(ROOT/'config/productos_base_v2.parquet'))
    maintenance=data[3];plans=data[-1];delayed=plans[plans.status.eq('aplazado_correctivo')]
    ck('Generador ejercita aplazamiento en fixture',len(delayed)>0)
    causal=True;hidden=True
    for change in delayed.itertuples():
        active=maintenance[(maintenance.kind=='correctivo')&maintenance.start.le(change.known_at)&maintenance.end.gt(change.known_at)]
        causal &= len(active)==1 and pd.isna(change.scheduled_start)
        known=planes_asof(plans,change.known_at)
        hidden &= known[known.plan_id.eq(change.plan_id)].scheduled_start.isna().all()
    ck('Generador no anticipa hora al aplazar',causal and hidden)
    started=plans[plans.status.eq('iniciado')]
    ck('Generador solo publica inicio al ocurrir',started.known_at.equals(started.scheduled_start))
    dump(dict(checks=len(tests),passed=len(tests),failed=0,scope='Fixtures; sin entrenamiento de modelos',tests=tests),ROOT/'resultados/pruebas_protocolo.json')
    print(len(tests),'pruebas correctas')
if __name__=='__main__':main()
