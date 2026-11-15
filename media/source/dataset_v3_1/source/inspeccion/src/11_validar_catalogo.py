"""Comprueba huellas, recuentos y continuidad de segmentos de producción."""
import argparse
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq
from comun import ROOT,sha,dump

def main(root=ROOT):
    root=Path(root);checks=[]
    for row in pd.read_parquet(root/'data/catalogo_archivos.parquet').itertuples():
        p=root/row.relative_path
        checks.append(dict(check='catalogue '+row.relative_path,passed=p.is_file() and sha(p)==row.sha256 and pq.ParquetFile(p).metadata.num_rows==row.row_count))
    seg=pd.read_parquet(root/'data/segmentos_produccion.parquet')
    for run,g in seg.groupby('run_id'):
        g=g.sort_values('start');t=pd.read_parquet(root/f'data/telemetria/{run}.parquet',columns=['timestamp'])
        valid=g.end.iloc[:-1].reset_index(drop=True).equals(g.start.iloc[1:].reset_index(drop=True))
        valid=valid and g.start.iloc[0]==t.timestamp.iloc[0] and g.end.iloc[-1]==t.timestamp.iloc[-1]+pd.Timedelta(minutes=5)
        checks.append(dict(check='segments '+run,passed=bool(valid)))
    result=dict(checks=len(checks),passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),tests=checks)
    dump(result,root/'resultados/validacion_catalogo_segmentos.json')
    print({k:v for k,v in result.items() if k!='tests'})
    if result['failed']:raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));a=p.parse_args();main(a.root)
