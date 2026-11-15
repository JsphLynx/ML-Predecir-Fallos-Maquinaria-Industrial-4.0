"""Replay de llegada de paquetes en cortes UTC; conserva la rejilla de observación.
Simula lo que conoce la aplicación. No elimina slots tardíos ni usa valores futuros.
"""
import importlib.util
import pandas as pd
import numpy as np
from comun import ROOT,SIGNALS,config,dump
spec=importlib.util.spec_from_file_location('builder',ROOT/'src/02_construir_variables.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

def snapshot_asof(tele,cutoff,c):
    if cutoff.minute%15 or cutoff.second:raise ValueError('Decisión fuera de rejilla')
    prefix=tele[tele.timestamp<=cutoff].copy()
    # Se conoce el contexto operativo en timestamp; los sensores solo a la llegada.
    prefix.loc[prefix.available_at>cutoff,list(SIGNALS)]=np.nan
    return builder.build_features(prefix,c).iloc[-1]

def main():
    c=config();tests=[]
    for p in sorted((ROOT/'data/telemetria').glob('*.parquet')):
        tele=pd.read_parquet(p);f=pd.read_parquet(ROOT/'ml/features'/p.name)
        for index in [300,2000,10000,20000]:
            cut=f.timestamp.iloc[index];a=snapshot_asof(tele,cut,c);b=f.iloc[index]
            num=f.select_dtypes('number').columns
            same=np.allclose(a[num].to_numpy(float),b[num].to_numpy(float),atol=1e-4,rtol=2e-5,equal_nan=True)
            same &= a.evaluation_status==b.evaluation_status and a.quality_code==b.quality_code and a.known_service_type==b.known_service_type
            tests.append(dict(test=f'{p.stem} replay {index}',passed=bool(same)))
    result=dict(checks=len(tests),passed=sum(t['passed'] for t in tests),failed=sum(not t['passed'] for t in tests),tests=tests)
    dump(result,ROOT/'resultados/replay_llegada.json');print({k:v for k,v in result.items() if k!='tests'})
    if result['failed']:raise SystemExit(1)
if __name__=='__main__':main()
