"""Primera exploración en Spyder. No regenera ni modifica los datos."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
EQUIPO='F3'
telemetria=pd.read_parquet(ROOT/f'data/telemetria/{EQUIPO}.parquet')
features=pd.read_parquet(ROOT/f'ml/features/{EQUIPO}.parquet')
targets=pd.read_parquet(ROOT/f'ml/targets/{EQUIPO}.parquet')
dataset=features.merge(targets,on=['equipo_id','timestamp'],validate='one_to_one')
train=dataset[(dataset.particion=='train')&dataset.fallo_8h.notna()].copy()
fallos=pd.read_parquet(ROOT/'data/fallos.parquet')
print('DATOS 100% SINTÉTICOS. Equipo:',EQUIPO)
print('Telemetría:',telemetria.shape,'ML:',dataset.shape)
print(dataset.groupby('particion').fallo_8h.agg(['count','mean']))
print('No utilizar columnas de targets ni verdad latente como predictores.')
