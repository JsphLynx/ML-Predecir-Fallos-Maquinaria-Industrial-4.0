"""Entrada de lectura para Spyder. No genera datos ni entrena modelos.
Editar EJECUCION para explorar otra simulación. Variables quedan en el explorador.
"""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
EJECUCION='R01'
telemetria=pd.read_parquet(ROOT/f'data/telemetria/{EJECUCION}.parquet')
variables=pd.read_parquet(ROOT/f'ml/features/{EJECUCION}.parquet')
objetivos=pd.read_parquet(ROOT/f'ml/targets/{EJECUCION}.parquet')
dataset=variables.merge(objetivos,on=['run_id','assembly_id','timestamp'],validate='one_to_one')
contrato=json.loads((ROOT/'ml/columnas_modelo.json').read_text(encoding='utf-8'))
columnas=contrato['numeric']+contrato['categorical']
train=dataset[(dataset.partition=='train')&dataset.evaluation_status.eq('evaluable')&dataset.y24.notna()].copy()
X_train=train[columnas].copy()
y_train=train.y24.astype(int).copy()
fallos=pd.read_parquet(ROOT/'data/fallos.parquet')
fallos=fallos[fallos.run_id==EJECUCION].copy()
print('DATOS SINTÉTICOS. No hay modelos entrenados. Ejecución:',EJECUCION)
print('Telemetría:',telemetria.shape,'Decisiones:',variables.shape,'X_train:',X_train.shape)
print(dataset.groupby('partition').y24.agg(['count','mean']))
print('No usar todas las columnas de dataset como entradas. X_train usa la lista permitida.')
