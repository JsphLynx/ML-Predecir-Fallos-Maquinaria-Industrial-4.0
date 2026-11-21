"""Diccionario y DDL derivados del contrato y de TODOS los esquemas Parquet.
SQL nuevo en acb_motor_v4_0 / acb_motor_v4_0_truth; nunca modifica acb_demo (v2).
"""
import argparse
from pathlib import Path
import json
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from comun import ROOT, KEY, SIGNALS, config, write, dump, sha

DESC={
 'plan_id':('ID','Identificador del plan preventivo versionado'),
 'revision':('entero','Versión de conocimiento del plan'),
 'scheduled_start':('UTC','Fecha prevista en esa revisión; nula al aplazar sin nueva hora conocida'),
 'status':('categoría','previsto, aplazado_correctivo o iniciado'),
 'planned_duration_hours':('h','Duración planeada, no cierre real futuro'),
 'if_reference_observable':('booleano','Referencia candidata observable de train; no garantiza salud ni ausencia de fallo futuro'),
 'run_id':('ID','Ejecución sintética; mundos alternativos, no motores reales distintos'),
 'assembly_id':('ID','Conjunto lógico de predicción motor y apoyos'),
 'asset_id':('ID','Activo o componente lógico'),
 'parent_asset_id':('ID','Activo padre; nulo solo para la planta'),
 'asset_type':('categoría','planta, linea, caja, conjunto, motor o apoyo'),
 'description':('texto','Descripción del activo'),
 'is_synthetic':('booleano','Siempre verdadero; no es inventario real'),
 'timestamp':('UTC','Instante de observación o decisión, según tabla'),
 'available_at':('UTC','Llegada del paquete de sensores; contexto operativo conocido en timestamp'),
 'source_available_at_max':('UTC','Máxima llegada de paquetes utilizados en las últimas 4 h; nunca posterior a decisión'),
 'sensor_id':('ID','Sensor lógico que produce un descriptor'),
 'variable':('texto','Nombre exacto de la señal en telemetría'),
 'unit':('texto','Unidad física del descriptor'),
 'min_demo':('unidad señal','Mínimo admisible configurado; no límite industrial certificado'),
 'max_demo':('unidad señal','Máximo admisible configurado; no límite industrial certificado'),
 'method':('texto','Descriptor sintético; no deriva de una onda adquirida'),
 'seed':('entero','Semilla maestra del generador'),
 'subseed_index':('entero','Índice usado con semilla maestra para crear cinco flujos RNG'),
 'version':('texto','Versión del generador y contrato'),
 'start':('UTC','Inicio inclusivo de ejecución, segmento, fallo, mantenimiento o incidencia'),
 'end':('UTC','Fin exclusivo del intervalo'),
 'scenario':('categoría','base_degradacion, base_vida_larga, stress_carga o stress_mecanismo_ruido; prohibido como predictor'),
 'step_minutes':('min','Cadencia de telemetría: 5'),
 'decision_minutes':('min','Cadencia de snapshots: 15'),
 'config_sha256':('SHA-256','Huella de configuración usada'),
 'rolling_state':('categoría','parado, arranque, sin_carga, laminacion, desaceleracion, mantenimiento o fallo'),
 'production_segment_id':('ID','Producto/segmento lógico simulado; no prueba fabricación de una bobina completa'),
 'steel_family':('categoría','Familia de producto fijada antes de la operación'),
 'target_thickness_mm':('mm','Espesor objetivo de la receta; nulo fuera de laminación'),
 'width_mm':('mm','Anchura objetivo; nula fuera de laminación'),
 'run_hours_since_service':('h','Horas operativas desde último servicio completado y conocido; al inicio desde seguimiento'),
 'known_service_type':('categoría','Último tipo de mantenimiento cuyo resultado ya estaba disponible'),
 'starts_last_24h':('recuento','Transiciones a operación en las 24 h anteriores incluyendo instante presente'),
 'grado_acero':('categoría','Cuatro grados heredados del catálogo sintético v2; no oferta actual verificada'),
 'espesor_min_demo_mm':('mm','Espesor mínimo del escenario heredado'),
 'factor_carga_demo':('adimensional','Factor supuesto de carga por grado, usado solo en el generador'),
 'event_id':('ID','Evento de fallo; en targets identifica el fallo futuro positivo y nunca es predictor'),
 'mode':('categoría','rodamiento_de, rodamiento_nde, termico_motor o electrico_subito'),
 'onset':('categoría','progresivo o subito; clasificación retrospectiva del simulador'),
 'detected_at':('UTC','Disponibilidad de detección del fallo; aquí igual a su inicio'),
 'diagnosis_available_at':('UTC','Disponibilidad del diagnóstico: 15 min tras fin'),
 'maintenance_id':('ID','Intervención vinculada al conjunto/componente'),
 'kind':('categoría','Tipo de mantenimiento o defecto instrumental, según tabla'),
 'known_at':('UTC','Instante de conocimiento de revisión; intervención real conocida al inicio; resultado solo tras cierre'),
 'result_available_at':('UTC','Cuándo se conoce cierre y resultado del mantenimiento'),
 'action':('categoría','sustitucion, reparacion_parcial, mejora_parcial o pendiente'),
 'completed_operating_hours':('h','Contador operativo al cierre; conocido únicamente en result_available_at'),
 'segment_id':('ID','Intervalo contiguo con mismo estado y receta'),
 'coverage_min_30m':('fracción','Mínima cobertura entre ocho señales esenciales sobre seis slots de 5 min; ausentes/tardíos/inválidos cuentan como falta'),
 'missing_fraction_30m':('fracción','Fracción de slots sin dato válido disponible de todas las señales, últimos 30 min'),
 'out_of_range_fraction_30m':('fracción','Fracción de slots disponibles fuera de límites del contrato, últimos 30 min'),
 'sensor_stale':('booleano','Señal esencial idéntica en seis slots válidos del mismo régimen activo; detector causal, no verdad de incidencias'),
 'max_data_age_minutes':('min','Mayor antigüedad del último dato válido de las señales esenciales; nulo si alguna no tiene dato en 4 h'),
 'eligible_operation':('booleano','Estado operativo apto para etiqueta: sin_carga o laminacion'),
 'evaluation_status':('categoría','evaluable o causa de abstención; no significa salud o avería'),
 'quality_code':('categoría','Resultado de controles observables: ok, cobertura_insuficiente, dato_antiguo, sensor_congelado, fuera_rango'),
 'y24':('0/1/nulo','Fallo funcional del conjunto en (t,t+24 h] antes de preventivo; desconocido si censurado o régimen excluido'),
 'censor_reason':('categoría','ninguna, fin_observacion, mantenimiento_preventivo o regimen_no_elegible'),
 'partition':('categoría','train, validation, test, stress o excluida; nunca predictor'),
 'exclusion_reason':('categoría','ninguno, purga_28h, episodio_cruza_frontera o calentamiento'),
 'healthy_reference_if':('booleano','Selector retrospectivo simulado para entrenamiento IF: normal latente, sin incidencias en ventana, train y evaluable; no disponible en servicio'),
 'damage_de':('adimensional','Degradación oculta DE; no observable ni RUL'),
 'damage_nde':('adimensional','Degradación oculta NDE; no observable ni RUL'),
 'damage_motor':('adimensional','Degradación oculta del motor; no observable ni RUL'),
 'health_state':('categoría','normal/degradacion/fallo según verdad simulada; degradación si máximo daño >=0.55, no etiqueta de fallo futuro'),
 'episode_id':('ID','Episodio latente de componente con daño >=0.55; uso exclusivo para auditoría de particiones'),
 'incident_id':('ID','Perturbación de sensor inyectada; no flag disponible automáticamente en servicio'),
 'damage_before':('adimensional','Daño del componente antes de reparación, verdad oculta'),
 'damage_after':('adimensional','Daño del componente después de reparación, verdad oculta'),
 'relative_path':('ruta','Ruta relativa al paquete, nunca credenciales ni URL privada'),
 'table_name':('texto','Tabla lógica del archivo Parquet'),
 'row_count':('filas','Número exacto de registros del archivo'),
 'sha256':('SHA-256','Huella de bytes del archivo Parquet'),
}

from contrato_v4 import EXTRA_DESC
DESC.update(EXTRA_DESC)

def table_files(root):
    public={p.stem:[p] for p in sorted((root/'data').glob('*.parquet'))}
    public['telemetria']=sorted((root/'data/telemetria').glob('*.parquet'))
    public['features']=sorted((root/'ml/features').glob('*.parquet'))
    private={p.stem:[p] for p in sorted((root/'sim_truth').glob('*.parquet'))}
    private['fisica']=sorted((root/'sim_truth/fisica').glob('*.parquet'))
    private['estado_latente']=sorted((root/'sim_truth/estado_latente').glob('*.parquet'))
    private['targets']=sorted((root/'ml/targets').glob('*.parquet'))
    return public,private

def describe(col):
    if col in SIGNALS:
        v=SIGNALS[col];return v[0],v[4]
    if col in DESC:return DESC[col]
    for minutes in [30,240]:
        for suffix,description in [('mean','Media'),('std','Desviación típica muestral ddof=1'),('slope_per_h','Pendiente OLS por hora')]:
            ending=f'_{suffix}_{minutes}m'
            if col.endswith(ending):
                base=col[:-len(ending)];unit,text=describe(base)
                return unit+('/h' if suffix=='slope_per_h' else ''),f'{description} de {text}; ventana (t-{minutes} min,t], solo medidas disponibles en t; nulo si muestras insuficientes'
    raise ValueError('Columna sin documentación: '+col)

def main(root=ROOT):
    root=Path(root);c=config(root/'config/escenario.json');(root/'sql').mkdir(exist_ok=True);(root/'docs').mkdir(exist_ok=True)
    # Contiguous segment register, exactly covering each execution.
    parts=[]
    for p in sorted((root/'data/telemetria').glob('*.parquet')):
        f=pd.read_parquet(p)
        context=['stand_id','configuration_id','rolling_state','production_segment_id','steel_family','target_thickness_mm','width_mm']
        changed=f[context].fillna('__null__').astype(str).ne(f[context].fillna('__null__').astype(str).shift()).any(axis=1)
        starts=np.flatnonzero(changed);ends=np.r_[starts[1:],len(f)]
        s=f.iloc[starts][['run_id','assembly_id']+context].reset_index(drop=True)
        s['segment_id']=s['production_segment_id']
        s['start']=f.timestamp.iloc[starts].to_numpy();s['end']=[f.timestamp.iloc[int(e)] if e<len(f) else f.timestamp.iloc[-1]+pd.Timedelta(minutes=5) for e in ends]
        s['known_at']=s.start;parts.append(s)
    write(pd.concat(parts,ignore_index=True),root/'data/segmentos_produccion.parquet')
    public,private=table_files(root)
    catalogue=[]
    for name,paths in {**public,**private}.items():
        if name=='catalogo_archivos':continue
        for p in paths:
            catalogue.append(dict(relative_path=p.relative_to(root).as_posix(),table_name=name,
                row_count=pq.ParquetFile(p).metadata.num_rows,sha256=sha(p)))
    write(pd.DataFrame(catalogue),root/'data/catalogo_archivos.parquet')
    public,private=table_files(root)
    model=json.loads((root/'ml/columnas_modelo.json').read_text(encoding='utf-8'))
    predictors=set(model['numeric']+model['categorical']);rows=[];sql=[]
    sql += ['-- Datos 100% sintéticos. Crear únicamente en una base de pruebas. No sobrescribe esquemas existentes.',
        '-- Ejecutar todo dentro de una transacción; el cargador lo hace automáticamente.',
        'CREATE SCHEMA acb_motor_v4_0;', 'CREATE SCHEMA acb_motor_v4_0_truth;',
        'REVOKE ALL ON SCHEMA acb_motor_v4_0_truth FROM PUBLIC;']
    pks={'configuraciones':['configuration_id'],'fisica':KEY,'plan_mantenimiento':['run_id','plan_id','revision'],'activos':['asset_id'],'sensores':['sensor_id'],'productos':['grado_acero'],'ejecuciones':['run_id'],
        'fallos':['run_id','event_id'],'mantenimiento':['run_id','maintenance_id'],
        'segmentos_produccion':['run_id','segment_id'],'telemetria':KEY,'features':KEY,'targets':KEY,
        'estado_latente':KEY,'episodios':['run_id','episode_id'],'incidencias_sensores':['run_id','incident_id'],
        'reparaciones':['run_id','maintenance_id','asset_id'],'catalogo_archivos':['relative_path']}
    sqlchecks={
        'configuraciones':['valid_to > valid_from','known_at <= valid_from','gear_ratio > 0','roll_radius_m > 0','motor_efficiency BETWEEN 0 AND 1','transmission_efficiency BETWEEN 0 AND 1','power_factor > 0 AND power_factor <= 1','voltage_ll_v > 0','is_synthetic'],
        'plan_mantenimiento':['revision >= 1',"status IN ('previsto','aplazado_correctivo','iniciado')","(status = 'aplazado_correctivo') = (scheduled_start IS NULL)",'planned_duration_hours > 0'],
        'ejecuciones':["end > start",'step_minutes = 5','decision_minutes = 15'],
        'fallos':["end > start",'diagnosis_available_at >= start'],
        'mantenimiento':["end > start",'result_available_at >= end'],
        'segmentos_produccion':["end > start",'known_at <= start'],
        'telemetria':['available_at >= timestamp'],
        'features':['coverage_min_30m BETWEEN 0 AND 1','missing_fraction_30m BETWEEN 0 AND 1','source_available_at_max <= timestamp'],
        'targets':['y24 IN (0,1)',"partition IN ('train','validation','test','stress','excluida')",
            "(y24 IS NULL) = (censor_reason <> 'ninguna')"],
        'episodios':["end > start"], 'incidencias_sensores':["end > start"],
        'reparaciones':['damage_after <= damage_before'],
        'activos':['is_synthetic'], 'sensores':['is_synthetic','max_demo > min_demo'],
        'catalogo_archivos':['row_count >= 0'],
    }
    for schema,tables in [('acb_motor_v4_0',public),('acb_motor_v4_0_truth',private)]:
        for name,paths in tables.items():
            schema_arrow=pq.read_schema(paths[0]);cols=[]
            for p in paths[1:]:
                if not schema_arrow.equals(pq.read_schema(p),check_metadata=False):raise ValueError('Esquema incoherente: '+str(p))
            for field in schema_arrow:
                unit,desc=describe(field.name)
                role='predictor' if name=='features' and field.name in predictors else 'verdad_restringida' if schema.endswith('_truth') else 'contexto_o_metadato'
                if name=='targets' and field.name=='y24':role='objetivo_restringido'
                rows.append(dict(table=f'{schema}.{name}',column=field.name,arrow_type=str(field.type),unit=unit,role=role,
                    allowed_predictor=role=='predictor',description=desc,
                    null_policy='Nunca nula' if field.name in pks[name] else 'Ver contrato: señal ausente, producto fuera de laminación, falta de historia o censura según campo'))
                typ='TIMESTAMPTZ' if pa.types.is_timestamp(field.type) else 'BOOLEAN' if pa.types.is_boolean(field.type) else 'BIGINT' if pa.types.is_integer(field.type) else 'DOUBLE PRECISION' if pa.types.is_floating(field.type) else 'TEXT'
                cols.append(f'    "{field.name}" {typ}'+(' NOT NULL' if field.name in pks[name] else ''))
            cols.append('    PRIMARY KEY ('+', '.join('"'+x+'"' for x in pks[name])+')')
            # Quote reserved interval identifiers, including PostgreSQL END.
            for clause in sqlchecks.get(name,[]):
                import re
                clause=re.sub(r'\b(end|start|timestamp)\b',r'"\1"',clause)
                cols.append('    CHECK ('+clause+')')
            sql.append(f'CREATE TABLE {schema}.{name} (\n'+',\n'.join(cols)+'\n);')
    def fk(schema,table,cols,target_schema,target,targetcols):
        q=lambda a:', '.join('"'+x+'"' for x in a)
        sql.append(f'ALTER TABLE {schema}.{table} ADD FOREIGN KEY ({q(cols)}) REFERENCES {target_schema}.{target} ({q(targetcols)});')
    op='acb_motor_v4_0';truth='acb_motor_v4_0_truth'
    fk(op,'configuraciones',['stand_id'],op,'activos',['asset_id'])
    for table in ['telemetria','features','segmentos_produccion']:
        fk(op,table,['configuration_id'],op,'configuraciones',['configuration_id'])
        fk(op,table,['stand_id'],op,'activos',['asset_id'])
    fk(op,'telemetria',['run_id','production_segment_id'],op,'segmentos_produccion',['run_id','segment_id'])
    fk(truth,'fisica',KEY,op,'telemetria',KEY)
    fk(op,'activos',['parent_asset_id'],op,'activos',['asset_id'])
    fk(op,'sensores',['asset_id'],op,'activos',['asset_id'])
    for schema,tables in [(op,public),(truth,private)]:
        for name,paths in tables.items():
            names=pq.read_schema(paths[0]).names
            if 'run_id' in names and name!='ejecuciones':fk(schema,name,['run_id'],op,'ejecuciones',['run_id'])
            if 'assembly_id' in names:fk(schema,name,['assembly_id'],op,'activos',['asset_id'])
            if 'asset_id' in names and name not in ['activos','sensores']:fk(schema,name,['asset_id'],op,'activos',['asset_id'])
    fk(op,'mantenimiento',['run_id','event_id'],op,'fallos',['run_id','event_id'])
    fk(op,'features',KEY,op,'telemetria',KEY)
    fk(truth,'targets',KEY,op,'features',KEY)
    fk(truth,'targets',['run_id','event_id'],op,'fallos',['run_id','event_id'])
    fk(truth,'estado_latente',KEY,op,'telemetria',KEY)
    fk(truth,'incidencias_sensores',['sensor_id'],op,'sensores',['sensor_id'])
    fk(truth,'reparaciones',['run_id','maintenance_id'],op,'mantenimiento',['run_id','maintenance_id'])
    for table in ['telemetria','features','segmentos_produccion']:
        fk(op,table,['steel_family'],op,'productos',['grado_acero'])
    sql += [f'CREATE INDEX ON {op}.fallos (assembly_id, "start");',
        f'CREATE INDEX ON {op}.features ("timestamp");',f'CREATE INDEX ON {truth}.targets (partition);',
        f'REVOKE ALL ON ALL TABLES IN SCHEMA {truth} FROM PUBLIC;',
        f'ALTER DEFAULT PRIVILEGES IN SCHEMA {truth} REVOKE ALL ON TABLES FROM PUBLIC;']
    sqltext='\n\n'.join(sql)+'\n';(root/'sql/01_esquema.sql').write_text(sqltext,encoding='utf-8')
    dictionary=pd.DataFrame(rows);dictionary.to_csv(root/'docs/diccionario_datos.csv',index=False,encoding='utf-8')
    text=['# Diccionario de datos v4.0','', 'Generado desde los esquemas Parquet. Fechas UTC; dimensiones y límites son supuestos de demostración.',
        '','| Tabla | Columna | Tipo | Unidad | Uso | Definición |','|---|---|---|---|---|---|']
    for r in rows:text.append('| '+' | '.join(str(r[k]).replace('|','/') for k in ['table','column','arrow_type','unit','role','description'])+' |')
    (root/'docs/diccionario_datos.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    dump({'public':{k:[p.relative_to(root).as_posix() for p in v] for k,v in public.items()},
          'private':{k:[p.relative_to(root).as_posix() for p in v] for k,v in private.items()}},root/'sql/tablas_carga.json')
    result={'dictionary_definitions':len(rows),'tables':len(public)+len(private),'unknown_columns':0,
        'live_postgresql_executed':False,'syntax_parsed':False}
    try:
        from pglast import parse_sql
        result['sql_statements']=len(parse_sql(sqltext));result['syntax_parsed']=True
    except ImportError:result['syntax_note']='pglast opcional no instalado; validación sintáctica pendiente'
    dump(result,root/'resultados/esquema.json');print(result,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));a=p.parse_args();main(a.root)
