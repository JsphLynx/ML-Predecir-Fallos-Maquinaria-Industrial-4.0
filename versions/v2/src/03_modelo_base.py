"""Prueba temporal congelada: ML, regla y ausencia de avisos.
Umbral elegido exclusivamente en validación. Test se utiliza una vez para informar.
No acredita rendimiento industrial ni calibración de probabilidades.
"""
from pathlib import Path
import json
import warnings
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score, precision_score, recall_score, brier_score_loss
ROOT=Path(__file__).resolve().parents[1]

def episodes(df,score,threshold,cooldown):
    candidates=df.loc[np.asarray(score)>=threshold,['equipo_id','timestamp']].sort_values(['equipo_id','timestamp'])
    rows=[]
    for aid,g in candidates.groupby('equipo_id'):
        last=None
        for t in g.timestamp:
            if last is None or t-last>=pd.Timedelta(hours=cooldown):
                rows.append((aid,t));last=t
    return pd.DataFrame(rows,columns=['equipo_id','timestamp'])

def event_metrics(df,scores,threshold,events,cfg):
    h=cfg['primary_horizon_hours'];lead=cfg['minimum_warning_minutes']
    alerts=episodes(df,scores,threshold,cfg['alert_cooldown_hours'])
    evaluable=set();detected=set();leads=[];false=0
    for e in events.itertuples():
        eligible=df[(df.equipo_id==e.equipo_id)&(df.timestamp>=e.inicio-pd.Timedelta(hours=h))&(df.timestamp<=e.inicio-pd.Timedelta(minutes=lead))]
        if len(eligible):evaluable.add(e.evento_id)
    for alert in alerts.itertuples():
        matching=events[(events.equipo_id==alert.equipo_id)&(events.inicio>=alert.timestamp+pd.Timedelta(minutes=lead))&(events.inicio<=alert.timestamp+pd.Timedelta(hours=h))]
        if not len(matching):false+=1
        for e in matching.itertuples():
            if e.evento_id not in detected:leads.append((e.inicio-alert.timestamp).total_seconds()/3600)
            detected.add(e.evento_id)
    exposure=len(df)*cfg['decision_minutes']/60
    return dict(eventos_evaluables=len(evaluable),eventos_detectados=len(detected&evaluable),
        recall_eventos=len(detected&evaluable)/len(evaluable) if evaluable else None,
        episodios_alerta=len(alerts),falsas_alertas=false,
        falsas_alertas_por_1000_h_equipo=false/exposure*1000 if exposure else None,
        alertas_por_1000_h_equipo=len(alerts)/exposure*1000 if exposure else None,
        anticipacion_mediana_h=float(np.median(leads)) if leads else None,
        horas_equipo_evaluadas=exposure),alerts

def main():
    cfg=json.loads((ROOT/'config/escenario.json').read_text())
    spec=json.loads((ROOT/'ml/columnas_modelo.json').read_text())
    frames=[]
    for fp in sorted((ROOT/'ml/features').glob('*.parquet')):
        x=pd.read_parquet(fp);y=pd.read_parquet(ROOT/'ml/targets'/fp.name)
        frames.append(x.merge(y,on=['equipo_id','timestamp'],validate='one_to_one'))
    df=pd.concat(frames,ignore_index=True)
    df=df[df[spec['target']].notna() & df.particion.ne('purga')].reset_index(drop=True)
    df[spec['target']]=df[spec['target']].astype(int)
    train=df[df.particion=='train'].copy();val=df[df.particion=='validation'].copy();test=df[df.particion=='test'].copy()
    columns=spec['numeric']+spec['categorical'];target=spec['target']
    pre=ColumnTransformer([
        ('num',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True),spec['numeric']),
        ('cat',OneHotEncoder(handle_unknown='ignore',sparse_output=False),spec['categorical'])])
    model=make_pipeline(pre,HistGradientBoostingClassifier(max_iter=90,max_leaf_nodes=15,learning_rate=.08,
        min_samples_leaf=80,l2_regularization=2,early_stopping=False,random_state=cfg['seed']))
    model.fit(train[columns],train[target])
    events=pd.read_parquet(ROOT/'data/fallos.parquet')
    # Simple rule standardized only by normal training observations, per equipment type.
    rulecols=['vibracion_rms_mm_s_media_1h','temperatura_rodamiento_c_media_1h','temperatura_motor_c_media_1h']
    normal=train[train[target]==0]
    centers=normal.groupby('tipo_equipo')[rulecols].median()
    scales=normal.groupby('tipo_equipo')[rulecols].std().clip(lower=.1)
    def rule(x):
        z=(x[rulecols].to_numpy()-centers.loc[x.tipo_equipo].to_numpy())/scales.loc[x.tipo_equipo].to_numpy()
        return np.nan_to_num(np.nanmax(z,axis=1),nan=0)
    results={};predictions=[];allalerts=[]
    for name,pv,pt in [('hist_gradient_boosting',model.predict_proba(val[columns])[:,1],model.predict_proba(test[columns])[:,1]),('regla_estadistica',rule(val),rule(test))]:
        # Fixed search, including no-alert policy. No test-driven optimization.
        choices=np.r_[np.unique(np.quantile(pv,[.90,.95,.97,.98,.99,.995,.999])),np.inf]
        candidates=[]
        for threshold in choices:
            stats,_=event_metrics(val,pv,threshold,events,cfg)
            if stats['alertas_por_1000_h_equipo']<=cfg['alert_budget_per_1000_equipment_hours']:
                candidates.append((stats['recall_eventos'] or 0,-stats['falsas_alertas'],float(threshold),stats))
        best=max(candidates,key=lambda x:(x[0],x[1]));threshold=best[2]
        stats,alerts=event_metrics(test,pt,threshold,events,cfg)
        stats.update(average_precision=float(average_precision_score(test[target],pt)),roc_auc=float(roc_auc_score(test[target],pt)),
            precision_muestras=float(precision_score(test[target],pt>=threshold,zero_division=0)),
            recall_muestras=float(recall_score(test[target],pt>=threshold,zero_division=0)),
            prevalencia=float(test[target].mean()))
        if name=='hist_gradient_boosting':stats['brier_score']=float(brier_score_loss(test[target],pt))
        results[name]=dict(umbral=None if np.isinf(threshold) else threshold,politica_sin_alertas=bool(np.isinf(threshold)),validation=best[3],test=stats)
        for part,x,pred in [('validation',val,pv),('test',test,pt)]:
            pr=x[['equipo_id','timestamp',target]].copy();pr['score']=pred;pr['modelo']=name;pr['particion']=part;predictions.append(pr)
        alerts['modelo']=name;allalerts.append(alerts)
    stats,_=event_metrics(test,np.zeros(len(test)),np.inf,events,cfg)
    results['sin_avisos']={'test':stats}
    output=dict(origen='SIMULACION: no extrapolar métricas a ACB',target=target,
        seleccion='umbral en validación sujeto a presupuesto de episodios; test sin ajuste',
        train_filas=len(train),validation_filas=len(val),test_filas=len(test),modelos=results)
    (ROOT/'resultados/modelo_base.json').write_text(json.dumps(output,indent=2,ensure_ascii=False))
    pd.concat(predictions).to_parquet(ROOT/'resultados/predicciones.parquet',index=False,compression='zstd')
    pd.concat(allalerts).to_csv(ROOT/'resultados/episodios_alerta_test.csv',index=False)
    print(json.dumps(output,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
