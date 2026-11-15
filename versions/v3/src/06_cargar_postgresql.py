"""OPCIONAL. Carga atómica en esquemas NUEVOS de una base de pruebas.
No se ejecuta automáticamente. No contiene ni registra credenciales.
Instalar psycopg[binary] y definir ACB_DATABASE_URL localmente.
Por defecto no carga sim_truth ni targets. --include-truth carga tablas restringidas.
"""
import argparse
from pathlib import Path
import json
import os
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def main(root=ROOT,include_truth=False):
    import psycopg
    from psycopg import sql
    root=Path(root);url=os.environ.get('ACB_DATABASE_URL')
    if not url:raise SystemExit('Falta ACB_DATABASE_URL. Usa una base de pruebas y configura la variable localmente.')
    mapping=json.loads((root/'sql/tablas_carga.json').read_text(encoding='utf-8'))
    public_order=['activos','productos','sensores','ejecuciones','fallos','mantenimiento','segmentos_produccion','telemetria','features','catalogo_archivos']
    private_order=['estado_latente','episodios','incidencias_sensores','reparaciones','targets']
    # All DDL and COPY statements share one transaction; collision rolls everything back.
    with psycopg.connect(url) as conn:
        existing=conn.execute("SELECT nspname FROM pg_namespace WHERE nspname IN ('acb_motor_v3','acb_motor_v3_truth')").fetchall()
        if existing:raise RuntimeError('Ya existe un esquema v3. No se modifica ni borra; utiliza otra base de pruebas.')
        conn.execute((root/'sql/01_esquema.sql').read_text(encoding='utf-8'))
        for schema,names,files in [('acb_motor_v3',public_order,mapping['public']),
            ('acb_motor_v3_truth',private_order if include_truth else [],mapping['private'])]:
            for name in names:
                for rel in files[name]:
                    df=pd.read_parquet(root/rel)
                    if name=='activos':
                        # Parent rows precede children even if source order changes.
                        pending=df.copy();order=[];seen=set()
                        while len(pending):
                            ready=pending.parent_asset_id.isna()|pending.parent_asset_id.isin(seen)
                            if not ready.any():raise ValueError('Ciclo en jerarquía de activos')
                            order.append(pending[ready]);seen.update(pending.loc[ready,'asset_id']);pending=pending[~ready]
                        df=pd.concat(order)
                    statement=sql.SQL('COPY {}.{} ({}) FROM STDIN').format(sql.Identifier(schema),sql.Identifier(name),
                        sql.SQL(',').join(map(sql.Identifier,df.columns)))
                    with conn.cursor().copy(statement) as copy:
                        for row in df.itertuples(index=False,name=None):
                            copy.write_row(tuple(None if pd.isna(v) else v.item() if hasattr(v,'item') else v for v in row))
                print('Cargada',schema+'.'+name,flush=True)
    print('Transacción completada. Revisar permisos antes de habilitar lectores.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--include-truth',action='store_true')
    a=p.parse_args();main(a.root,a.include_truth)
