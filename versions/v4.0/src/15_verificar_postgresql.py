"""Integración en PostgreSQL YA cargado por 06. Solo base de pruebas nueva.
ACB_DATABASE_URL debe identificar esa base; incluye verdad para probar aislamiento.
El rol de demostración debe no existir antes de esta comprobación.
"""
import os,json
import pandas as pd
import pyarrow.parquet as pq
import psycopg
from psycopg import sql
from comun import ROOT,dump
from protocolo_evaluacion import planes_asof

def main():
    tests=[]
    def ck(n,v):
        tests.append(dict(test=n,passed=bool(v)))
        if not v:raise AssertionError(n)
    mapping=json.loads((ROOT/'sql/tablas_carga.json').read_text())
    with psycopg.connect(os.environ['ACB_DATABASE_URL']) as conn:
        version=conn.execute('SELECT version()').fetchone()[0]
        for schema,key in [('acb_motor_v4_0','public'),('acb_motor_v4_0_truth','private')]:
            for name,files in mapping[key].items():
                expected=sum(pq.ParquetFile(ROOT/f).metadata.num_rows for f in files)
                count=conn.execute(sql.SQL('SELECT count(*) FROM {}.{}').format(sql.Identifier(schema),sql.Identifier(name))).fetchone()[0]
                ck('Conteo '+schema+'.'+name,count==expected)
        def rejected(name,statement,exception):
            try:
                with conn.transaction():conn.execute(statement)
            except exception:ck(name,True)
            else:ck(name,False)
        rejected('PK rechaza duplicado','INSERT INTO acb_motor_v4_0.activos SELECT * FROM acb_motor_v4_0.activos LIMIT 1',psycopg.errors.UniqueViolation)
        rejected('FK rechaza padre inexistente',"INSERT INTO acb_motor_v4_0.activos VALUES ('BAD','NO_EXISTE','motor','prueba',true)",psycopg.errors.ForeignKeyViolation)
        rejected('CHECK rechaza etiqueta 2',"UPDATE acb_motor_v4_0_truth.targets SET y24=2 WHERE run_id='R01' AND timestamp=(SELECT min(timestamp) FROM acb_motor_v4_0_truth.targets WHERE run_id='R01')",psycopg.errors.CheckViolation)
        conn.execute('SAVEPOINT rollback_test')
        conn.execute("INSERT INTO acb_motor_v4_0.activos VALUES ('TEMP',NULL,'planta','prueba',true)")
        conn.execute('ROLLBACK TO SAVEPOINT rollback_test')
        ck('Rollback deshace escritura',conn.execute("SELECT count(*) FROM acb_motor_v4_0.activos WHERE asset_id='TEMP'").fetchone()[0]==0)
        conn.execute((ROOT/'sql/03_rol_demostracion.sql').read_text())
        conn.execute('SET ROLE acb_v40_demo_reader')
        rejected('Lector no lee verdad','SELECT * FROM acb_motor_v4_0_truth.estado_latente LIMIT 1',psycopg.errors.InsufficientPrivilege)
        rejected('Lector no lee objetivos','SELECT * FROM acb_motor_v4_0_truth.targets LIMIT 1',psycopg.errors.InsufficientPrivilege)
        rejected('Lector no lee resultados futuros','SELECT * FROM acb_motor_v4_0.mantenimiento LIMIT 1',psycopg.errors.InsufficientPrivilege)
        rejected('Lector no escribe datos',"DELETE FROM acb_motor_v4_0.features WHERE false",psycopg.errors.InsufficientPrivilege)
        cutoff=pd.Timestamp('2024-05-01',tz='UTC')
        ck('API features no devuelve futuro',conn.execute('SELECT max(timestamp)<=%s FROM acb_motor_v4_0_api.features_asof(%s)',[cutoff,cutoff]).fetchone()[0])
        rows=conn.execute('SELECT run_id,plan_id,revision FROM acb_motor_v4_0_api.planes_asof(%s)',[cutoff]).fetchall()
        p=planes_asof(pd.read_parquet(ROOT/'data/plan_mantenimiento.parquet'),cutoff)
        ck('API plan coincide con asof Python',sorted(rows)==sorted(p[['run_id','plan_id','revision']].itertuples(index=False,name=None)))
        m=pd.read_parquet(ROOT/'data/mantenimiento.parquet');m=m.iloc[0];cutoff=m.start
        service=conn.execute('SELECT completed_end,action,completed_operating_hours FROM acb_motor_v4_0_api.servicios_asof(%s) WHERE run_id=%s AND maintenance_id=%s',[cutoff,m.run_id,m.maintenance_id]).fetchone()
        ck('API cierre oculto antes de disponibilidad',service==(None,None,None))
        conn.execute('RESET ROLE')
        conn.commit()
    dump(dict(version=version,checks=len(tests),passed=len(tests),failed=0,tests=tests,environment='PostgreSQL local aislado. No acredita Neon ni Windows.'),ROOT/'resultados/postgresql_ejecutado.json')
    schema=json.loads((ROOT/'resultados/esquema.json').read_text());schema.update(live_postgresql_executed=True,postgresql_version=version);dump(schema,ROOT/'resultados/esquema.json')
    print(len(tests),'pruebas PostgreSQL correctas')
if __name__=='__main__':main()
