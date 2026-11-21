"""Validación relacional adicional y sintaxis PostgreSQL sin servidor.
No equivale a ejecutar COPY, privilegios y consultas en PostgreSQL/Neon.
"""
import json
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq
from comun import ROOT,KEY,dump

def main(root=ROOT):
    root=Path(root);checks=[]
    def ck(name,ok):checks.append(dict(test=name,passed=bool(ok)))
    mapping=json.loads((root/'sql/tablas_carga.json').read_text())
    dictionary=pd.read_csv(root/'docs/diccionario_datos.csv')
    ck('Diccionario sin definiciones duplicadas',not dictionary.duplicated(['table','column']).any())
    for section,prefix in [('public','acb_motor_v4_0'),('private','acb_motor_v4_0_truth')]:
        for name,paths in mapping[section].items():
            cols=pq.read_schema(root/paths[0]).names
            selected=dictionary[dictionary.table.eq(prefix+'.'+name)]
            ck(name+' todas las columnas definidas',set(selected.column)==set(cols) and selected.description.notna().all())
            ck(name+' esquemas homogéneos',all(pq.read_schema(root/p).equals(pq.read_schema(root/paths[0]),check_metadata=False) for p in paths))
    segments=pd.read_parquet(root/'data/segmentos_produccion.parquet')
    ck('PK segmentos única',not segments.duplicated(['run_id','segment_id']).any())
    for p in sorted((root/'data/telemetria').glob('*.parquet')):
        tele=pd.read_parquet(p,columns=KEY+['production_segment_id','configuration_id','stand_id'])
        seg=segments[segments.run_id.eq(p.stem)]
        a=tele.merge(seg[['production_segment_id','start','end','configuration_id','stand_id']],on='production_segment_id',suffixes=('','_segment'),how='left',validate='many_to_one')
        ck(p.stem+' FK segmento y pertenencia temporal',a.start.notna().all() and ((a.timestamp>=a.start)&(a.timestamp<a.end)).all())
        ck(p.stem+' segmento conserva configuración/caja',a.configuration_id.eq(a.configuration_id_segment).all() and a.stand_id.eq(a.stand_id_segment).all())
    source=pd.read_csv(root/'docs/procedencia_parametros.csv')
    c=json.loads((root/'config/escenario.json').read_text())
    ck('Todo parámetro físico trazado',{'physics.'+k for k in c['physics']}<=set(source.parameter))
    ck('Ningún parámetro físico afirma calibración',source.loc[source.parameter.str.startswith('physics.'),'industrial_calibration'].astype(str).str.lower().eq('false').all())
    stats=[]
    try:
        from pglast import parse_sql
        for p in sorted((root/'sql').glob('*.sql')):
            parsed=parse_sql(p.read_text());ck('Sintaxis PostgreSQL '+p.name,len(parsed)>0)
            stats.append(dict(file=p.name,statements=len(parsed)))
        syntax=True
    except ImportError:syntax=False
    ck('Parser PostgreSQL disponible para esta auditoría',syntax)
    out=dict(checks=len(checks),passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),
             syntax_files=stats,live_postgresql_executed=False,tests=checks,
             scope='Esquemas, claves, trazabilidad y parser SQL. Sin integración con servidor.')
    dump(out,root/'resultados/contratos_relacionales.json');print({k:v for k,v in out.items() if k!='tests'},flush=True)
    if out['failed']:raise SystemExit(1)

if __name__=='__main__':main()
