"""Exporta un equipo sin cargar toda la telemetría. Editar EQUIPO en Spyder."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
EQUIPO='F3'
out=ROOT/'exportaciones_csv';out.mkdir(exist_ok=True)
for folder,name in [('data/telemetria','telemetria'),('ml/features','features'),('ml/targets','targets')]:
    df=pd.read_parquet(ROOT/f'{folder}/{EQUIPO}.parquet')
    df.to_csv(out/f'{name}_{EQUIPO}.csv.gz',index=False,compression='gzip')
for file in (ROOT/'data').glob('*.parquet'):
    pd.read_parquet(file).to_csv(out/f'{file.stem}.csv.gz',index=False,compression='gzip')
print('CSV UTF-8, separador coma, punto decimal, nulos vacíos, fechas UTC:',out)
