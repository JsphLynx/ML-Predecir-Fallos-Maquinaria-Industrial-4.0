"""OPCIONAL. Carga en una base de pruebas propia. No ejecutado en la entrega.
Instalar: pip install 'psycopg[binary]'. Configurar ACB_DATABASE_URL localmente.
No contiene credenciales. Rechaza cargar si alguna tabla ya tiene filas.
"""
from pathlib import Path
import os
import pandas as pd
import psycopg
from psycopg import sql
ROOT=Path(__file__).resolve().parents[1]
TABLES=['equipos','productos','bobinas','fallos','mantenimiento','paradas_linea','estado_linea','telemetria','features','targets']

def main():
    url=os.environ.get('ACB_DATABASE_URL')
    if not url:raise SystemExit('Configura ACB_DATABASE_URL con tu conexión de pruebas; no pegues credenciales en el código.')
    with psycopg.connect(url,autocommit=True) as conn:
        conn.execute((ROOT/'sql/01_esquema.sql').read_text())
        with conn.transaction():
            for table in TABLES:
                exists=conn.execute(sql.SQL('SELECT EXISTS(SELECT 1 FROM acb_demo.{})').format(sql.Identifier(table))).fetchone()[0]
                if exists:raise RuntimeError('Se requiere un esquema vacío. No se reemplazan datos existentes: '+table)
            for table in TABLES:
                folder={'telemetria':'data/telemetria','features':'ml/features','targets':'ml/targets'}.get(table)
                files=sorted((ROOT/folder).glob('*.parquet')) if folder else [ROOT/f'data/{table}.parquet']
                for p in files:
                    df=pd.read_parquet(p)
                    statement=sql.SQL('COPY acb_demo.{} ({}) FROM STDIN').format(sql.Identifier(table),sql.SQL(',').join(map(sql.Identifier,df.columns)))
                    with conn.cursor().copy(statement) as copy:
                        for row in df.itertuples(index=False,name=None):
                            copy.write_row(tuple(None if pd.isna(v) else v.item() if hasattr(v,'item') else v for v in row))
                print('Cargada',table)
if __name__=='__main__':main()
