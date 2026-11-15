from pathlib import Path
import json
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
r=Path(__file__).resolve().parents[1]
desc={
'equipo_id':('Identificador de conjunto funcional sintético','ID','observable'),
'timestamp':('Instante de lectura/decisión en UTC','UTC','clave'),
'disponible_desde':('Instante de disponibilidad, igual a t en este escenario sin latencia de ingestión','UTC','metadato'),
'tipo_equipo':('Familia del conjunto funcional','categoría','observable'),
'posicion':('Orden conceptual de etapa; no longitud física','orden','metadato'),
'potencia_nominal_kw':('Potencia nominal supuesta del accionamiento equivalente','kW','supuesto'),
'modos_admisibles':('Modos de fallo implementados para el equipo, separados por |','categoría','supuesto'),
'origen':('Marcador sintético','texto','metadato'),
'inventario_real':('Siempre falso; no representa inventario contrastado','booleano','metadato'),
'grado_acero':('Grado de la receta; cuatro familias, no catálogo completo','categoría','observable'),
'espesor_min_demo_mm':('Mínimo elegido en la demostración, no límite comercial vigente','mm','supuesto'),
'factor_carga_demo':('Factor de esfuerzo del grado asumido por el generador','adimensional','supuesto'),
'estado_equipo':('0 marcha; 1 preventivo; 2 parada por causa ajena; 3 averiado; 4 reserva','código','observable'),
'estado_linea':('0 marcha; 1 preventivo; 2 parada no programada; PM tiene prioridad en solapes','código','observable'),
'en_marcha':('Equipo trabajando en la ventana presente','booleano','elegibilidad'),
'bobina_id':('Identificador de bobina/pieza; nulo fuera de producción','ID','clave'),
'espesor_objetivo_mm':('Espesor de producto fijado al inicio de bobina','mm','observable'),
'ancho_mm':('Anchura fijada al inicio de bobina','mm','observable'),
'carga_relativa':('Proxy observable de carga, no daño oculto','fracción nominal','observable'),
'horas_desde_mantenimiento':('Tiempo desde finalización del último mantenimiento conocido; inicio de observación si no hay anterior','h','observable'),
'fraccion_marcha_4h':('Proporción de registros en marcha durante últimas cuatro horas','fracción','feature causal'),
'fraccion_ausentes_1h':('Media del porcentaje de nulos de diez sensores; incluye nulos estructurales','fracción','feature causal'),
'vibracion_rms_mm_s':('Velocidad vibratoria RMS sintética; no señal espectral','mm/s','observable'),
'temperatura_rodamiento_c':('Temperatura de rodamiento equivalente','°C','observable'),
 'temperatura_motor_c':('Temperatura de motor equivalente','°C','observable'),
 'temperatura_aceite_c':('Temperatura de aceite','°C','observable'),
 'presion_aceite_bar':('Presión de lubricación','bar','observable'),
 'presion_hidraulica_bar':('Presión hidráulica; estructuralmente nula cuando no aplica','bar','observable'),
 'caudal_refrigeracion_l_min':('Caudal del circuito de refrigeración equivalente','L/min','observable'),
 'corriente_motor_pct_nominal':('Corriente como porcentaje del nominal supuesto','%','observable'),
 'velocidad_motor_rpm':('Velocidad de accionamiento; cajas deducida de velocidad de banda','rpm','observable'),
 'potencia_kw':('Potencia del accionamiento según carga y nominal, sin balance energético completo','kW','observable'),
 'fuerza_laminacion_mn':('Aproximación de fuerza solo para cajas','MN','observable proceso'),
 'espesor_entrada_caja_mm':('Espesor geométrico a entrada de la caja, solo durante marcha','mm','observable proceso'),
 'espesor_salida_caja_mm':('Espesor geométrico de salida de la caja','mm','observable proceso'),
 'velocidad_entrada_caja_m_s':('Velocidad de entrada consistente con flujo volumétrico','m/s','observable proceso'),
 'velocidad_salida_caja_m_s':('Velocidad de salida consistente con flujo volumétrico','m/s','observable proceso'),
 'temperatura_material_c':('Temperatura simplificada de banda/planchón','°C','observable proceso'),
 'temperatura_ambiente_c':('Estacionalidad y ciclo diario inventados','°C','observable'),
 'velocidad_salida_m_s':('Velocidad final según masa y duración discretizada de bobina','m/s','observable proceso'),
 'flujo_masa_kg_s':('Flujo de masa; cero en parada','kg/s','observable proceso'),
 'inicio':('Inicio del episodio, intervención o fabricación','UTC','evento'),
 'fin':('Fin exclusivo del episodio, intervención o fabricación','UTC','resultado futuro'),
 'evento_id':('Identificador de avería; nulo para preventivos','ID','resultado futuro'),
 'modo_fallo':('Componente/mecanismo diagnosticado tras avería','categoría','resultado futuro'),
 'tipo_inicio':('Progresivo o súbito; clasificación del generador','categoría','resultado futuro'),
 'diagnostico_disponible_desde':('Momento de disponibilidad del diagnóstico, fin de reparación','UTC','resultado futuro'),
 'duracion_h':('Duración de reparación observada','h','resultado futuro'),
 'coste_reparacion_eur_simulado':('Coste inventado; mismo coste que correctivo asociado, evitar doble conteo','EUR ficticios','resultado futuro'),
 'mantenimiento_id':('Identificador de intervención','ID','evento'),
 'tipo':('Clase de mantenimiento, parada o incidencia según tabla','categoría','evento'),
 'conocido_desde':('Fecha de conocimiento: preventivo siete días antes; correctivo al fallo','UTC','disponibilidad'),
 'coste_eur_simulado':('Coste hipotético de intervención, no cotización real','EUR ficticios','resultado futuro'),
 'parada_id':('Identificador de intervalo de parada por causa','ID','evento'),
 'equipo_causa':('Equipo causante; nulo en parada programada general','ID','resultado futuro'),
 'masa_objetivo_t':('Masa de bobina objetivo; máximo 28 t','t','receta'),
 'longitud_objetivo_m':('Longitud coherente con masa y sección','m','receta'),
 'pasos_objetivo':('Número de ventanas previsto para fabricar bobina','pasos','receta'),
 'pasos_procesados':('Ventanas realizadas hasta completar o interrumpir','pasos','resultado futuro'),
 'rama_colada':('Rama elegida por bobina A/B, alternancia hipotética','categoría','receta'),
 'bobinadora_id':('Bobinadora asignada','ID','receta'),
 'estado_resultado':('Completa o interrumpida; solo completas son producto final','categoría','resultado futuro'),
 'masa_procesada_t':('Masa efectivamente procesada, proporcional a pasos realizados','t','resultado futuro'),
 'espesor_medido_final_mm':('Medida final con error sintético; no disponible en decisiones anteriores','mm','resultado futuro'),
 'disponible_resultado_desde':('Resultado conocido diez minutos después del fin','UTC','disponibilidad'),
 'proximo_fallo_id':('Próxima avería observada, incluso si media preventivo; nunca feature','ID','target auxiliar prohibido'),
 'horas_hasta_proximo_fallo_observado':('Distancia al siguiente fallo registrado; no RUL sin intervención','h','target auxiliar prohibido'),
 'particion':('train, validation, test o purga con barrera de 24 h','categoría','partición'),
 'dano_latente':('Daño oculto acumulado; umbral de fallo 1','adimensional','verdad prohibida'),
 'modo_latente':('Modo oculto del componente en ciclo, sin incluir choque eléctrico','categoría','verdad prohibida'),
 'precursor_latente':('Transformación oculta del daño que induce sensores','adimensional','verdad prohibida'),
 'incidencia_id':('Identificador de perturbación instrumental inyectada','ID','verdad prohibida'),
 'sensor':('Nombre de variable afectada','texto','verdad prohibida')}
for h in [4,8,24]:
 desc[f'fallo_{h}h']=(f'Fallo propio en (t,t+{h}h], nulo si censurado','0/1/nulo','target prohibido')
 desc[f'censura_{h}h']=('ninguna, fin_observacion o mantenimiento_preventivo','categoría','target prohibido')

tables={p.stem:p for p in (r/'data').glob('*.parquet')}
tables.update(telemetria=r/'data/telemetria/F1.parquet',features=r/'ml/features/F1.parquet',targets=r/'ml/targets/F1.parquet',verdad_latente=r/'privado_no_usar_como_features/F1.parquet',incidencias_sensores=r/'privado_no_usar_como_features/incidencias_sensores.parquet')
rows=[];unknown=[];sql=['-- Escenario 100% sintético. DDL PostgreSQL; NO ejecutado contra servidor.','BEGIN;','CREATE SCHEMA IF NOT EXISTS acb_demo;']
for name,p in tables.items():
 schema=pq.read_schema(p);cols=[]
 for f in schema:
  if f.name not in desc:
   found=False
   for suff,explain in [('_media_1h','Media retrospectiva 1 hora'),('_std_1h','Desviación típica retrospectiva 1 hora, ddof=1'),('_media_4h','Media retrospectiva 4 horas')]:
    if f.name.endswith(suff):
     base=f.name[:-len(suff)];desc[f.name]=(explain+' de '+base,desc[base][1],'feature causal');found=True;break
   if not found:unknown.append(f.name)
  d,u,role=desc.get(f.name,('NO DOCUMENTADA','?','?'))
  rows.append(dict(tabla=name,columna=f.name,tipo=str(f.type),unidad=u,rol=role,descripcion=d,nulos='Permitidos según aplicación, incidencias o censura; clave nunca nula'))
  typ='TIMESTAMPTZ' if pa.types.is_timestamp(f.type) else 'BOOLEAN' if pa.types.is_boolean(f.type) else 'BIGINT' if pa.types.is_integer(f.type) else 'DOUBLE PRECISION' if pa.types.is_floating(f.type) else 'TEXT'
  cols.append(f'    "{f.name}" {typ}')
 if name in ['verdad_latente','incidencias_sensores']:continue
 pk={'equipos':['equipo_id'],'productos':['grado_acero'],'bobinas':['bobina_id'],'fallos':['evento_id'],'mantenimiento':['mantenimiento_id'],'paradas_linea':['parada_id'],'estado_linea':['timestamp'],'telemetria':['equipo_id','timestamp'],'features':['equipo_id','timestamp'],'targets':['equipo_id','timestamp']}[name]
 cols.append('    PRIMARY KEY ('+', '.join('"'+x+'"' for x in pk)+')')
 sql.append('CREATE TABLE IF NOT EXISTS acb_demo.'+name+' (\n'+',\n'.join(cols)+'\n);')
# Foreign keys added after all entities, idempotent in separate DO statements.
fks=[('fallos','equipo_id','equipos','equipo_id'),('mantenimiento','equipo_id','equipos','equipo_id'),('mantenimiento','evento_id','fallos','evento_id'),('bobinas','grado_acero','productos','grado_acero'),('bobinas','bobinadora_id','equipos','equipo_id'),('paradas_linea','evento_id','fallos','evento_id'),('paradas_linea','equipo_causa','equipos','equipo_id'),('estado_linea','bobina_id','bobinas','bobina_id'),('telemetria','equipo_id','equipos','equipo_id'),('telemetria','bobina_id','bobinas','bobina_id'),('features','equipo_id','equipos','equipo_id'),('targets','equipo_id','equipos','equipo_id')]
for table,col,target,tcol in fks:
 sql.append(f'DO $$ BEGIN ALTER TABLE acb_demo.{table} ADD CONSTRAINT fk_{table}_{col} FOREIGN KEY ({col}) REFERENCES acb_demo.{target} ({tcol}); EXCEPTION WHEN duplicate_object THEN NULL; END $$;')
sql+=['CREATE INDEX IF NOT EXISTS idx_fallos_t ON acb_demo.fallos (equipo_id, inicio);','CREATE INDEX IF NOT EXISTS idx_features_t ON acb_demo.features (timestamp);','COMMIT;']
(r/'sql/01_esquema.sql').write_text('\n\n'.join(sql))
pd.DataFrame(rows).to_csv(r/'docs/diccionario_datos.csv',index=False)
assert not unknown,unknown
(r/'docs/diccionario_datos.md').write_text('# Diccionario completo\n\nGenerado a partir de esquemas Parquet del entregable. Una definición por columna y tabla.\n\n'+'\n'.join(['| '+ ' | '.join(str(row.get(c,c)).replace('|',' / ') for c in ['tabla','columna','tipo','unidad','rol','descripcion'])+' |' for row in [dict(zip(['tabla','columna','tipo','unidad','rol','descripcion'],['tabla','columna','tipo','unidad','rol','descripcion'])),dict.fromkeys(['tabla','columna','tipo','unidad','rol','descripcion'],'---')]+rows])+'\n\nLas unidades son del simulador, sin rangos certificados ni garantías de seguridad industrial. Las columnas con rol prohibido no deben incorporarse a predictores. Nulos estructurales: fuerza, velocidades y espesores por caja solo aplican a cajas; temperatura de material solo a etapas modeladas; presión hidráulica solo a cajas, bobinadoras, cizalla y central hidráulica. El resto de nulos se debe a inactividad o incidencia instrumental; no sustituir siempre por cero.\n')
print('Diccionario',len(rows),'definiciones; SQL',len(tables)-2,'tablas')
