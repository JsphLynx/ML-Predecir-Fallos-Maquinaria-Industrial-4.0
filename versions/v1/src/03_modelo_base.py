"""Prueba funcional de ML. Resultados SOLO sintéticos, sin validez industrial."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import average_precision_score, precision_score, recall_score, confusion_matrix

ROOT=Path(__file__).resolve().parents[1]


def run():
    t=pd.read_csv(ROOT/"datos/telemetria.csv.gz",parse_dates=["timestamp"])
    y=pd.read_csv(ROOT/"datos/objetivos_ml.csv.gz")
    line=pd.read_csv(ROOT/"datos/estado_linea.csv.gz",parse_dates=["timestamp"])
    # y and t are aligned by validated primary keys; identifiers are not predictors.
    t["y"]=y.fallo_proximas_4h
    t["particion"]=y.particion
    t=t.sort_values(["equipo_id","timestamp"])
    signal_cols=["rpm","par_nm","potencia_kw","corriente_a","temperatura_equipo_c",
                 "vibracion_rms_mm_s","presion_circuito_bar","horas_desde_intervencion"]
    extra=[]
    for col in ["temperatura_equipo_c","vibracion_rms_mm_s","corriente_a"]:
        for window in (12,72):
            name=f"{col}_media_{window*5}min"
            # Shift before rolling: historical-only, with no backfill.
            t[name]=t.groupby("equipo_id",sort=False)[col].transform(lambda s:s.shift(1).rolling(window,min_periods=3).mean())
            extra.append(name)
    t=t.merge(line[["timestamp","espesor_objetivo_mm","ancho_objetivo_mm","ambiente_c"]],on="timestamp",validate="many_to_one")
    features=signal_cols+extra+["espesor_objetivo_mm","ancho_objetivo_mm","ambiente_c"]
    # One decision each 15 min. Do not randomise the chronological partitions.
    t=t[t.timestamp.dt.minute.mod(15).eq(0)&t.y.notna()&t.particion.ne("purga")]
    train=t[t.particion.eq("train")]; val=t[t.particion.eq("validacion")]; test=t[t.particion.eq("test")]
    model=make_pipeline(SimpleImputer(strategy="median",add_indicator=True),
         HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=15,l2_regularization=10,learning_rate=.08,random_state=73,early_stopping=False))
    model.fit(train[features],train.y)
    pv=model.predict_proba(val[features])[:,1]
    candidates=np.unique(np.r_[np.linspace(.01,.9,100),np.quantile(pv,np.linspace(.8,.999,60))])
    scores=[]
    for threshold in candidates:
        pred=pv>=threshold
        pr=precision_score(val.y,pred,zero_division=0); re=recall_score(val.y,pred,zero_division=0)
        scores.append(5*pr*re/(4*pr+re+1e-12))
    threshold=float(candidates[np.argmax(scores)])
    prob=model.predict_proba(test[features])[:,1]; pred=prob>=threshold
    cm=confusion_matrix(test.y,pred,labels=[0,1])
    predictions=test[["timestamp","equipo_id","y"]].copy()
    predictions["probabilidad"]=prob; predictions["alerta"]=pred.astype(int)
    predictions.to_csv(ROOT/"resultados/predicciones_test.csv.gz",index=False)
    events=pd.read_csv(ROOT/"datos/eventos_fallo.csv.gz",parse_dates=["inicio"])
    eligible=events[(events.inicio>=test.timestamp.min()+pd.Timedelta(hours=4))&(events.inicio<=test.timestamp.max())]
    detected=0; leads=[]
    for row in eligible.itertuples():
        warnings=predictions[(predictions.equipo_id==row.equipo_id)&predictions.alerta.eq(1)&(predictions.timestamp<row.inicio)&(predictions.timestamp>=row.inicio-pd.Timedelta(hours=4))]
        if len(warnings):
            detected+=1; leads.append((row.inicio-warnings.timestamp.min()).total_seconds()/60)
    report={"advertencia":"Rendimiento sobre reglas del simulador; NO evidencia de eficacia en ACB.",
        "objetivo":"Avería del mismo equipo en (t,t+4h]", "variables_permitidas":features,
        "filas_train":len(train),"filas_validacion":len(val),"filas_test":len(test),
        "umbral_elegido_en_validacion":threshold,"criterio_umbral":"F2 por fila; sin calibración de probabilidades",
        "test_average_precision":float(average_precision_score(test.y,prob)),
        "test_prevalencia_base":float(test.y.mean()),
        "test_precision":float(precision_score(test.y,pred,zero_division=0)),
        "test_recall":float(recall_score(test.y,pred,zero_division=0)),
        "matriz_confusion_TN_FP_FN_TP":cm.ravel().tolist(),
        "falsos_avisos_por_100_h_equipo_evaluables":float(cm[0,1]/(len(test)*.25)*100),
        "eventos_evaluables_test":len(eligible),"eventos_con_aviso_4h":detected,
        "mediana_anticipacion_min_solo_detectados":float(np.median(leads)) if leads else None,
        "limites":"Avisos por fila sin agrupación ni supresión; exposición solo tiempo evaluable. No incertidumbre por bootstrap. Mismos equipos en periodos posteriores; no mide generalización a equipos nuevos."}
    (ROOT/"resultados/modelo_base.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=="__main__":
    run()
