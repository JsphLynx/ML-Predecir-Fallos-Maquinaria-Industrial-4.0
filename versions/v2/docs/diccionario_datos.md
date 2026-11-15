# Diccionario completo

Generado a partir de esquemas Parquet del entregable. Una definición por columna y tabla.

| tabla | columna | tipo | unidad | rol | descripcion |
| --- | --- | --- | --- | --- | --- |
| paradas_linea | parada_id | string | ID | evento | Identificador de intervalo de parada por causa |
| paradas_linea | inicio | timestamp[ns, tz=UTC] | UTC | evento | Inicio del episodio, intervención o fabricación |
| paradas_linea | fin | timestamp[ns, tz=UTC] | UTC | resultado futuro | Fin exclusivo del episodio, intervención o fabricación |
| paradas_linea | tipo | string | categoría | evento | Clase de mantenimiento, parada o incidencia según tabla |
| paradas_linea | evento_id | string | ID | resultado futuro | Identificador de avería; nulo para preventivos |
| paradas_linea | equipo_causa | string | ID | resultado futuro | Equipo causante; nulo en parada programada general |
| equipos | equipo_id | string | ID | observable | Identificador de conjunto funcional sintético |
| equipos | tipo_equipo | string | categoría | observable | Familia del conjunto funcional |
| equipos | posicion | int64 | orden | metadato | Orden conceptual de etapa; no longitud física |
| equipos | potencia_nominal_kw | int64 | kW | supuesto | Potencia nominal supuesta del accionamiento equivalente |
| equipos | modos_admisibles | string | categoría | supuesto | Modos de fallo implementados para el equipo, separados por  /  |
| equipos | origen | string | texto | metadato | Marcador sintético |
| equipos | inventario_real | bool | booleano | metadato | Siempre falso; no representa inventario contrastado |
| bobinas | bobina_id | int64 | ID | clave | Identificador de bobina/pieza; nulo fuera de producción |
| bobinas | inicio | timestamp[ns, tz=UTC] | UTC | evento | Inicio del episodio, intervención o fabricación |
| bobinas | grado_acero | string | categoría | observable | Grado de la receta; cuatro familias, no catálogo completo |
| bobinas | espesor_objetivo_mm | float | mm | observable | Espesor de producto fijado al inicio de bobina |
| bobinas | ancho_mm | float | mm | observable | Anchura fijada al inicio de bobina |
| bobinas | masa_objetivo_t | float | t | receta | Masa de bobina objetivo; máximo 28 t |
| bobinas | longitud_objetivo_m | float | m | receta | Longitud coherente con masa y sección |
| bobinas | pasos_objetivo | int64 | pasos | receta | Número de ventanas previsto para fabricar bobina |
| bobinas | pasos_procesados | int64 | pasos | resultado futuro | Ventanas realizadas hasta completar o interrumpir |
| bobinas | rama_colada | string | categoría | receta | Rama elegida por bobina A/B, alternancia hipotética |
| bobinas | bobinadora_id | string | ID | receta | Bobinadora asignada |
| bobinas | fin | timestamp[ns, tz=UTC] | UTC | resultado futuro | Fin exclusivo del episodio, intervención o fabricación |
| bobinas | estado_resultado | string | categoría | resultado futuro | Completa o interrumpida; solo completas son producto final |
| bobinas | masa_procesada_t | float | t | resultado futuro | Masa efectivamente procesada, proporcional a pasos realizados |
| bobinas | espesor_medido_final_mm | float | mm | resultado futuro | Medida final con error sintético; no disponible en decisiones anteriores |
| bobinas | disponible_resultado_desde | timestamp[ns, tz=UTC] | UTC | disponibilidad | Resultado conocido diez minutos después del fin |
| fallos | evento_id | string | ID | resultado futuro | Identificador de avería; nulo para preventivos |
| fallos | equipo_id | string | ID | observable | Identificador de conjunto funcional sintético |
| fallos | inicio | timestamp[ns, tz=UTC] | UTC | evento | Inicio del episodio, intervención o fabricación |
| fallos | fin | timestamp[ns, tz=UTC] | UTC | resultado futuro | Fin exclusivo del episodio, intervención o fabricación |
| fallos | modo_fallo | string | categoría | resultado futuro | Componente/mecanismo diagnosticado tras avería |
| fallos | tipo_inicio | string | categoría | resultado futuro | Progresivo o súbito; clasificación del generador |
| fallos | diagnostico_disponible_desde | timestamp[ns, tz=UTC] | UTC | resultado futuro | Momento de disponibilidad del diagnóstico, fin de reparación |
| fallos | duracion_h | float | h | resultado futuro | Duración de reparación observada |
| fallos | coste_reparacion_eur_simulado | float | EUR ficticios | resultado futuro | Coste inventado; mismo coste que correctivo asociado, evitar doble conteo |
| productos | grado_acero | string | categoría | observable | Grado de la receta; cuatro familias, no catálogo completo |
| productos | espesor_min_demo_mm | float | mm | supuesto | Mínimo elegido en la demostración, no límite comercial vigente |
| productos | factor_carga_demo | float | adimensional | supuesto | Factor de esfuerzo del grado asumido por el generador |
| mantenimiento | mantenimiento_id | string | ID | evento | Identificador de intervención |
| mantenimiento | equipo_id | string | ID | observable | Identificador de conjunto funcional sintético |
| mantenimiento | inicio | timestamp[ns, tz=UTC] | UTC | evento | Inicio del episodio, intervención o fabricación |
| mantenimiento | fin | timestamp[ns, tz=UTC] | UTC | resultado futuro | Fin exclusivo del episodio, intervención o fabricación |
| mantenimiento | tipo | string | categoría | evento | Clase de mantenimiento, parada o incidencia según tabla |
| mantenimiento | evento_id | string | ID | resultado futuro | Identificador de avería; nulo para preventivos |
| mantenimiento | conocido_desde | timestamp[ns, tz=UTC] | UTC | disponibilidad | Fecha de conocimiento: preventivo siete días antes; correctivo al fallo |
| mantenimiento | coste_eur_simulado | float | EUR ficticios | resultado futuro | Coste hipotético de intervención, no cotización real |
| estado_linea | timestamp | timestamp[ns, tz=UTC] | UTC | clave | Instante de lectura/decisión en UTC |
| estado_linea | estado_linea | int8 | código | observable | 0 marcha; 1 preventivo; 2 parada no programada; PM tiene prioridad en solapes |
| estado_linea | bobina_id | int64 | ID | clave | Identificador de bobina/pieza; nulo fuera de producción |
| estado_linea | espesor_objetivo_mm | float | mm | observable | Espesor de producto fijado al inicio de bobina |
| estado_linea | ancho_mm | float | mm | observable | Anchura fijada al inicio de bobina |
| estado_linea | velocidad_salida_m_s | float | m/s | observable proceso | Velocidad final según masa y duración discretizada de bobina |
| estado_linea | flujo_masa_kg_s | float | kg/s | observable proceso | Flujo de masa; cero en parada |
| telemetria | equipo_id | string | ID | observable | Identificador de conjunto funcional sintético |
| telemetria | timestamp | timestamp[ns, tz=UTC] | UTC | clave | Instante de lectura/decisión en UTC |
| telemetria | disponible_desde | timestamp[ns, tz=UTC] | UTC | metadato | Instante de disponibilidad, igual a t en este escenario sin latencia de ingestión |
| telemetria | tipo_equipo | string | categoría | observable | Familia del conjunto funcional |
| telemetria | estado_equipo | int8 | código | observable | 0 marcha; 1 preventivo; 2 parada por causa ajena; 3 averiado; 4 reserva |
| telemetria | en_marcha | bool | booleano | elegibilidad | Equipo trabajando en la ventana presente |
| telemetria | bobina_id | int64 | ID | clave | Identificador de bobina/pieza; nulo fuera de producción |
| telemetria | grado_acero | string | categoría | observable | Grado de la receta; cuatro familias, no catálogo completo |
| telemetria | espesor_objetivo_mm | float | mm | observable | Espesor de producto fijado al inicio de bobina |
| telemetria | ancho_mm | float | mm | observable | Anchura fijada al inicio de bobina |
| telemetria | carga_relativa | float | fracción nominal | observable | Proxy observable de carga, no daño oculto |
| telemetria | horas_desde_mantenimiento | float | h | observable | Tiempo desde finalización del último mantenimiento conocido; inicio de observación si no hay anterior |
| telemetria | temperatura_ambiente_c | float | °C | observable | Estacionalidad y ciclo diario inventados |
| telemetria | vibracion_rms_mm_s | float | mm/s | observable | Velocidad vibratoria RMS sintética; no señal espectral |
| telemetria | temperatura_rodamiento_c | float | °C | observable | Temperatura de rodamiento equivalente |
| telemetria | temperatura_motor_c | float | °C | observable | Temperatura de motor equivalente |
| telemetria | temperatura_aceite_c | float | °C | observable | Temperatura de aceite |
| telemetria | presion_aceite_bar | float | bar | observable | Presión de lubricación |
| telemetria | presion_hidraulica_bar | float | bar | observable | Presión hidráulica; estructuralmente nula cuando no aplica |
| telemetria | caudal_refrigeracion_l_min | float | L/min | observable | Caudal del circuito de refrigeración equivalente |
| telemetria | corriente_motor_pct_nominal | float | % | observable | Corriente como porcentaje del nominal supuesto |
| telemetria | velocidad_motor_rpm | float | rpm | observable | Velocidad de accionamiento; cajas deducida de velocidad de banda |
| telemetria | potencia_kw | float | kW | observable | Potencia del accionamiento según carga y nominal, sin balance energético completo |
| telemetria | fuerza_laminacion_mn | float | MN | observable proceso | Aproximación de fuerza solo para cajas |
| telemetria | espesor_entrada_caja_mm | float | mm | observable proceso | Espesor geométrico a entrada de la caja, solo durante marcha |
| telemetria | espesor_salida_caja_mm | float | mm | observable proceso | Espesor geométrico de salida de la caja |
| telemetria | velocidad_entrada_caja_m_s | float | m/s | observable proceso | Velocidad de entrada consistente con flujo volumétrico |
| telemetria | velocidad_salida_caja_m_s | float | m/s | observable proceso | Velocidad de salida consistente con flujo volumétrico |
| telemetria | temperatura_material_c | float | °C | observable proceso | Temperatura simplificada de banda/planchón |
| features | equipo_id | string | ID | observable | Identificador de conjunto funcional sintético |
| features | timestamp | timestamp[ns, tz=UTC] | UTC | clave | Instante de lectura/decisión en UTC |
| features | disponible_desde | timestamp[ns, tz=UTC] | UTC | metadato | Instante de disponibilidad, igual a t en este escenario sin latencia de ingestión |
| features | tipo_equipo | string | categoría | observable | Familia del conjunto funcional |
| features | en_marcha | bool | booleano | elegibilidad | Equipo trabajando en la ventana presente |
| features | grado_acero | string | categoría | observable | Grado de la receta; cuatro familias, no catálogo completo |
| features | espesor_objetivo_mm | float | mm | observable | Espesor de producto fijado al inicio de bobina |
| features | ancho_mm | float | mm | observable | Anchura fijada al inicio de bobina |
| features | carga_relativa | float | fracción nominal | observable | Proxy observable de carga, no daño oculto |
| features | horas_desde_mantenimiento | float | h | observable | Tiempo desde finalización del último mantenimiento conocido; inicio de observación si no hay anterior |
| features | temperatura_ambiente_c | float | °C | observable | Estacionalidad y ciclo diario inventados |
| features | vibracion_rms_mm_s | float | mm/s | observable | Velocidad vibratoria RMS sintética; no señal espectral |
| features | temperatura_rodamiento_c | float | °C | observable | Temperatura de rodamiento equivalente |
| features | temperatura_motor_c | float | °C | observable | Temperatura de motor equivalente |
| features | temperatura_aceite_c | float | °C | observable | Temperatura de aceite |
| features | presion_aceite_bar | float | bar | observable | Presión de lubricación |
| features | presion_hidraulica_bar | float | bar | observable | Presión hidráulica; estructuralmente nula cuando no aplica |
| features | caudal_refrigeracion_l_min | float | L/min | observable | Caudal del circuito de refrigeración equivalente |
| features | corriente_motor_pct_nominal | float | % | observable | Corriente como porcentaje del nominal supuesto |
| features | velocidad_motor_rpm | float | rpm | observable | Velocidad de accionamiento; cajas deducida de velocidad de banda |
| features | potencia_kw | float | kW | observable | Potencia del accionamiento según carga y nominal, sin balance energético completo |
| features | vibracion_rms_mm_s_media_1h | float | mm/s | feature causal | Media retrospectiva 1 hora de vibracion_rms_mm_s |
| features | vibracion_rms_mm_s_std_1h | float | mm/s | feature causal | Desviación típica retrospectiva 1 hora, ddof=1 de vibracion_rms_mm_s |
| features | vibracion_rms_mm_s_media_4h | float | mm/s | feature causal | Media retrospectiva 4 horas de vibracion_rms_mm_s |
| features | temperatura_rodamiento_c_media_1h | float | °C | feature causal | Media retrospectiva 1 hora de temperatura_rodamiento_c |
| features | temperatura_rodamiento_c_std_1h | float | °C | feature causal | Desviación típica retrospectiva 1 hora, ddof=1 de temperatura_rodamiento_c |
| features | temperatura_rodamiento_c_media_4h | float | °C | feature causal | Media retrospectiva 4 horas de temperatura_rodamiento_c |
| features | temperatura_motor_c_media_1h | float | °C | feature causal | Media retrospectiva 1 hora de temperatura_motor_c |
| features | temperatura_motor_c_std_1h | float | °C | feature causal | Desviación típica retrospectiva 1 hora, ddof=1 de temperatura_motor_c |
| features | temperatura_motor_c_media_4h | float | °C | feature causal | Media retrospectiva 4 horas de temperatura_motor_c |
| features | temperatura_aceite_c_media_1h | float | °C | feature causal | Media retrospectiva 1 hora de temperatura_aceite_c |
| features | temperatura_aceite_c_std_1h | float | °C | feature causal | Desviación típica retrospectiva 1 hora, ddof=1 de temperatura_aceite_c |
| features | temperatura_aceite_c_media_4h | float | °C | feature causal | Media retrospectiva 4 horas de temperatura_aceite_c |
| features | presion_aceite_bar_media_1h | float | bar | feature causal | Media retrospectiva 1 hora de presion_aceite_bar |
| features | presion_aceite_bar_std_1h | float | bar | feature causal | Desviación típica retrospectiva 1 hora, ddof=1 de presion_aceite_bar |
| features | presion_aceite_bar_media_4h | float | bar | feature causal | Media retrospectiva 4 horas de presion_aceite_bar |
| features | presion_hidraulica_bar_media_1h | float | bar | feature causal | Media retrospectiva 1 hora de presion_hidraulica_bar |
| features | presion_hidraulica_bar_std_1h | float | bar | feature causal | Desviación típica retrospectiva 1 hora, ddof=1 de presion_hidraulica_bar |
| features | presion_hidraulica_bar_media_4h | float | bar | feature causal | Media retrospectiva 4 horas de presion_hidraulica_bar |
| features | caudal_refrigeracion_l_min_media_1h | float | L/min | feature causal | Media retrospectiva 1 hora de caudal_refrigeracion_l_min |
| features | caudal_refrigeracion_l_min_std_1h | float | L/min | feature causal | Desviación típica retrospectiva 1 hora, ddof=1 de caudal_refrigeracion_l_min |
| features | caudal_refrigeracion_l_min_media_4h | float | L/min | feature causal | Media retrospectiva 4 horas de caudal_refrigeracion_l_min |
| features | corriente_motor_pct_nominal_media_1h | float | % | feature causal | Media retrospectiva 1 hora de corriente_motor_pct_nominal |
| features | corriente_motor_pct_nominal_std_1h | float | % | feature causal | Desviación típica retrospectiva 1 hora, ddof=1 de corriente_motor_pct_nominal |
| features | corriente_motor_pct_nominal_media_4h | float | % | feature causal | Media retrospectiva 4 horas de corriente_motor_pct_nominal |
| features | velocidad_motor_rpm_media_1h | float | rpm | feature causal | Media retrospectiva 1 hora de velocidad_motor_rpm |
| features | velocidad_motor_rpm_std_1h | float | rpm | feature causal | Desviación típica retrospectiva 1 hora, ddof=1 de velocidad_motor_rpm |
| features | velocidad_motor_rpm_media_4h | float | rpm | feature causal | Media retrospectiva 4 horas de velocidad_motor_rpm |
| features | fraccion_marcha_4h | float | fracción | feature causal | Proporción de registros en marcha durante últimas cuatro horas |
| features | fraccion_ausentes_1h | float | fracción | feature causal | Media del porcentaje de nulos de diez sensores; incluye nulos estructurales |
| targets | equipo_id | string | ID | observable | Identificador de conjunto funcional sintético |
| targets | timestamp | timestamp[ns, tz=UTC] | UTC | clave | Instante de lectura/decisión en UTC |
| targets | proximo_fallo_id | string | ID | target auxiliar prohibido | Próxima avería observada, incluso si media preventivo; nunca feature |
| targets | horas_hasta_proximo_fallo_observado | float | h | target auxiliar prohibido | Distancia al siguiente fallo registrado; no RUL sin intervención |
| targets | fallo_4h | int8 | 0/1/nulo | target prohibido | Fallo propio en (t,t+4h], nulo si censurado |
| targets | censura_4h | string | categoría | target prohibido | ninguna, fin_observacion o mantenimiento_preventivo |
| targets | fallo_8h | int8 | 0/1/nulo | target prohibido | Fallo propio en (t,t+8h], nulo si censurado |
| targets | censura_8h | string | categoría | target prohibido | ninguna, fin_observacion o mantenimiento_preventivo |
| targets | fallo_24h | int8 | 0/1/nulo | target prohibido | Fallo propio en (t,t+24h], nulo si censurado |
| targets | censura_24h | string | categoría | target prohibido | ninguna, fin_observacion o mantenimiento_preventivo |
| targets | particion | string | categoría | partición | train, validation, test o purga con barrera de 24 h |
| verdad_latente | equipo_id | string | ID | observable | Identificador de conjunto funcional sintético |
| verdad_latente | timestamp | timestamp[ns, tz=UTC] | UTC | clave | Instante de lectura/decisión en UTC |
| verdad_latente | dano_latente | float | adimensional | verdad prohibida | Daño oculto acumulado; umbral de fallo 1 |
| verdad_latente | modo_latente | string | categoría | verdad prohibida | Modo oculto del componente en ciclo, sin incluir choque eléctrico |
| verdad_latente | precursor_latente | float | adimensional | verdad prohibida | Transformación oculta del daño que induce sensores |
| incidencias_sensores | incidencia_id | string | ID | verdad prohibida | Identificador de perturbación instrumental inyectada |
| incidencias_sensores | equipo_id | string | ID | observable | Identificador de conjunto funcional sintético |
| incidencias_sensores | sensor | string | texto | verdad prohibida | Nombre de variable afectada |
| incidencias_sensores | inicio | timestamp[ns, tz=UTC] | UTC | evento | Inicio del episodio, intervención o fabricación |
| incidencias_sensores | fin | timestamp[ns, tz=UTC] | UTC | resultado futuro | Fin exclusivo del episodio, intervención o fabricación |
| incidencias_sensores | tipo | string | categoría | evento | Clase de mantenimiento, parada o incidencia según tabla |

Las unidades son del simulador, sin rangos certificados ni garantías de seguridad industrial. Las columnas con rol prohibido no deben incorporarse a predictores. Nulos estructurales: fuerza, velocidades y espesores por caja solo aplican a cajas; temperatura de material solo a etapas modeladas; presión hidráulica solo a cajas, bobinadoras, cizalla y central hidráulica. El resto de nulos se debe a inactividad o incidencia instrumental; no sustituir siempre por cero.
