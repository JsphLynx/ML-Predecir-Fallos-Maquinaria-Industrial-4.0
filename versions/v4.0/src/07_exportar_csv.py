"""CSV opcional para R/Power BI. Una ejecución cada vez; UTC explícito."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
EJECUCION='R01'

if __name__=='__main__':
    out=ROOT/'exportaciones_csv';out.mkdir(exist_ok=True)
    for folder,name in [('data/telemetria','telemetria'),('ml/features','features'),('ml/targets','targets_RESTRINGIDO')]:
        df=pd.read_parquet(ROOT/f'{folder}/{EJECUCION}.parquet')
        df.to_csv(out/f'{name}_{EJECUCION}.csv.gz',index=False,compression='gzip',encoding='utf-8')
    print('CSV UTF-8, coma, decimal punto, nulos vacíos. Targets solo para evaluación:',out)
