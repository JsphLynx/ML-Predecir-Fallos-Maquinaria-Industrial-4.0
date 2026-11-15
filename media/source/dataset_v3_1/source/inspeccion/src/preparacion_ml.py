"""Preparación sin entrenamiento; lista permitida y cortes por fechas comunes."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from comun import ROOT, KEY

def referencia_observable(f, partition):
    return (partition.eq('train') & f.evaluation_status.eq('evaluable') &
        f.known_service_type.isin(['preventivo','correctivo']) &
        f.run_hours_since_service.between(4,24) & f.coverage_min_30m.eq(1) & f.quality_code.eq('ok'))

def cargar_particion(partition='train',root=ROOT,reference=None,final_evaluation=False):
    root=Path(root)
    if partition not in ['train','validation','test','stress']:raise ValueError('Partición no permitida')
    if partition in ['test','stress'] and not final_evaluation:raise ValueError('Congelar protocolo antes de abrir evaluación final')
    if reference and (partition!='train' or reference not in ['observable','ideal']):raise ValueError('Referencia solo train: observable o ideal')
    contract=json.loads((root/'ml/columnas_modelo.json').read_text())
    frames=[]
    for p in sorted((root/'ml/features').glob('*.parquet')):
        f=pd.read_parquet(p);t=pd.read_parquet(root/'ml/targets'/p.name)
        a=f.merge(t,on=KEY,validate='one_to_one')
        mask=a.partition.eq(partition)&a.evaluation_status.eq('evaluable')
        if reference:mask &= a['if_reference_observable' if reference=='observable' else 'healthy_reference_if']
        else:mask &= a.y24.notna()
        frames.append(a[mask])
    a=pd.concat(frames).sort_values(['timestamp','run_id']).reset_index(drop=True)
    x=a[contract['numeric']+contract['categorical']].copy()
    for col in contract['categorical']:x[col]=x[col].astype(object).where(x[col].notna(),np.nan)
    return x,a.y24.copy(),a[KEY].copy()

def preprocesador(root=ROOT,columns=None):
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import OneHotEncoder,StandardScaler
    from sklearn.pipeline import Pipeline
    c=json.loads((Path(root)/'ml/columnas_modelo.json').read_text())
    num=[v for v in c['numeric'] if columns is None or v in columns]
    cat=[v for v in c['categorical'] if columns is None or v in columns]
    return ColumnTransformer([
        ('numeric',Pipeline([('imputer',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)),('scale',StandardScaler())]),num),
        ('category',Pipeline([('imputer',SimpleImputer(strategy='constant',fill_value='sin_receta')),('encode',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cat)])

def folds_temporales(keys,episodes,folds=3,purge_hours=28):
    """Entrada exclusivamente train. Validación expansiva, purga y episodios completos."""
    t=keys.timestamp;lo=t.min();hi=t.max();span=hi-lo
    for i in range(folds):
        start=lo+span*(.4+i*.6/folds);end=lo+span*(.4+(i+1)*.6/folds)
        train=t+pd.Timedelta(hours=purge_hours)<start
        val=(t>=start)&(t+pd.Timedelta(hours=purge_hours)<end)
        for boundary in [start,end]:
            for ep in episodes[(episodes.start<boundary)&(episodes.end>boundary)].itertuples():
                mask=keys.run_id.eq(ep.run_id)&t.ge(ep.start-pd.Timedelta(hours=24))&t.lt(ep.end)
                train &= ~mask;val &= ~mask
        yield np.flatnonzero(train),np.flatnonzero(val)

HISTORIAL_CARGA=['run_hours_since_service','starts_last_24h','load_ratio','speed_rpm','rolling_state','known_service_type']
CONDICION=['bearing_temperature_de_c','bearing_temperature_nde_c','winding_temperature_c','vibration_de_mm_s','vibration_nde_mm_s']

class ReglaCondicion:
    """Score máximo de condición relativo a percentiles de train; no probabilidad."""
    def fit(self,x,y=None):
        self.median_=x[CONDICION].median();self.scale_=(x[CONDICION].quantile(.95)-self.median_).clip(lower=1e-6);return self
    def score(self,x):return ((x[CONDICION]-self.median_)/self.scale_).max(axis=1)

def comparadores_sin_ajustar(root=ROOT):
    from sklearn.dummy import DummyClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    return {'constante':DummyClassifier(strategy='prior'), 'condicion':ReglaCondicion(),
        'historial_carga':Pipeline([('preprocesador',preprocesador(root,HISTORIAL_CARGA)),('modelo',LogisticRegression(max_iter=1000,random_state=20261105))])}
