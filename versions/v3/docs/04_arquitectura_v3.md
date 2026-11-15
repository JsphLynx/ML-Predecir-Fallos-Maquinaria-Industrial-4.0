# Arquitectura vigente del subsistema · v3

Versión 3.0.0, 04/11/2026. Este contrato aplica al paquete `ACB_Motor_Rodamientos_Sintetico_v3`. La arquitectura v1 original se conserva en `docs/referencia/Arquitectura_v1_original.md` como antecedente; sus propuestas de un minuto y 180 días quedan sustituidas por lo indicado aquí.

## Decisión empresarial y alcance

Preparar una demostración de priorización de inspecciones ante riesgo de fallo funcional de un conjunto motor-apoyos en las próximas 24 h. El resultado futuro será una alerta explicada y revisable. No se conecta a maquinaria ni se ordenan paradas. Sin datos reales no se demuestra reducción de averías, ahorro o eficacia industrial.

El conjunto lógico `DEMO-C01-DRV01` es la unidad de predicción. Se observan motor, apoyo DE y apoyo NDE por separado. No se entrenan tres modelos independientes por componente; un modo o localización del evento es diagnóstico retrospectivo del simulador. La inferencia futura deberá tratar cualquier localización como indicio hasta disponer de evidencia y evaluación propias.

## Contrato temporal y de datos

| Elemento | Contrato efectivo |
|---|---|
| Telemetría | 5 min por ejecución/conjunto; 27 columnas, 15 señales |
| Decisión | 15 min; se conservan abstenciones |
| Horizonte | 24 h de calendario |
| Ventanas | Último valor con edad <=10 min; estadísticas de 30 min y 4 h |
| Calidad esencial | >=80 % en cada señal esencial sobre seis slots, sin congelación detectada |
| Observación / disponibilidad | UTC; llegada independiente de paquetes de sensores; contexto conocido en t |
| Exposición | 365 días por mundo; ocho mundos, seis base y dos de estrés |
| Unicidad | run_id + assembly_id + timestamp |
| División | Cortes 60/20/20 por fechas comunes, con purga 28 h y exclusión de episodios completos |

No se crean muestras intermedias a un minuto. La referencia anterior a 3 de 5 resultados dentro de 5 min ya no es aplicable. Para el futuro dashboard se propone **3 de las últimas 5 decisiones de 15 min** dentro de una ventana retrospectiva de 75 min; la primera y última de esas cinco decisiones están separadas 60 min. Cierre propuesto tras 60 min válidos bajo el umbral de salida. Son parámetros futuros en configuración, pendientes de evaluar; no se han generado alertas en esta entrega. Datos faltantes no se interpretan como recuperación.

## Componentes implementados

| Componente | Estado y evidencia |
|---|---|
| Simulador | Implementado; flujos RNG separados, estados físicos simplificados, defectos y latencias |
| Parquet | Generado por ejecución para telemetría, snapshots, objetivos y verdad |
| Variables causales | Implementadas; mismo constructor utilizable posteriormente para reproducción temporal |
| Etiquetas y particiones | Implementadas; conservan motivos de censura/exclusión |
| EDA de control | Tablas de calidad y regímenes; figuras de auditoría con verdad claramente identificada |
| Contrato SQL | DDL de 15 tablas y cargador opcional; sintaxis comprobada, no desplegado |
| Entrenamiento | Pendiente: baseline, XGBoost e Isolation Forest |
| API / dashboard | Pendientes: FastAPI y Streamlit según propuesta anterior, sin instalación en esta entrega |
| Alertas y revisión | Pendientes: persistencia, agrupación, explicación, revisión y cierre |

## Capas y acceso

`data/` contiene inventario, sensores, contexto, fallos/mantenimiento históricos y telemetría. Los diagnósticos y resultados conservan su momento de disponibilidad: no usar toda una fila histórica como si se hubiera conocido antes del cierre. `ml/features/` contiene solo observables causales más metadatos de evaluación. `ml/targets/` y `sim_truth/` se reservan para entrenamiento y auditoría.

En SQL, `acb_motor_v3` contiene 10 tablas operativas y `acb_motor_v3_truth` cinco tablas restringidas. El servicio futuro solo debe leer observaciones/snapshots y resultados de modelos. No debe tener acceso a objetivos, daños, episodios ni incidencias inyectadas. La separación local de carpetas es organizativa; los permisos efectivos se tendrán que aplicar al desplegar.

El catálogo registra rutas relativas y hashes de 42 archivos Parquet; no se incluye a sí mismo para evitar autorreferencia. `SHA256.json` cubre el paquete completo. Los esquemas SQL reflejan los archivos actuales, incluyendo la posibilidad opcional de cargar telemetría/features. Para la aplicación, los históricos masivos pueden permanecer en Parquet y PostgreSQL servir de catálogo y trazabilidad.

## Siguiente etapa

Revisar EDA por régimen y componente, congelar esta entrega y entrenar referencias/modelos con listas permitidas. Los dos scores futuros se mostrarán separados: riesgo supervisado y anomalía multivariante. Un score de anomalía no se convertirá en probabilidad sin un procedimiento validado. No hay RUL calculada en este paquete.

La evaluación deberá contabilizar fallos/episodios, falsas alertas por exposición, anticipación, cobertura y calibración, incluyendo los fallos súbitos sin precursores. Se seleccionarán políticas con validación y se reservará test/estrés para evaluación final. Las cifras del README son disponibilidad de datos, no resultados de detección.
