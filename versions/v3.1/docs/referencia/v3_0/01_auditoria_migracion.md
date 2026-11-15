# Auditoría y migración de v2 a v3

Fecha: 04/11/2026. Alcance solicitado: identificar componentes, revisar señales/calidad, adaptar simulador y recalcular variables/etiquetas/particiones. Cadencias fijadas por Joseph: 5/15 minutos.

## Revisión realizada

Se han leído el LEEME de la v2 y la arquitectura del subsistema v1; los nueve scripts de Python del ZIP, la configuración, el diccionario, el DDL y la metodología. Se han inspeccionado los esquemas y recuentos de sus **81 Parquet**. Se ejecutaron el comprobador de integridad y el validador original: **113 archivos sin diferencias y 494 comprobaciones correctas**. La validación original lee las tablas principales, la telemetría y las variables/objetivos de los 18 equipos. Las predicciones antiguas solo se inventariaron: no se reutilizan ni se reevalúan como resultado v3.

Evidencias reproducibles de la revisión: `resultados/auditoria_v2.json` (incluye hash del ZIP y de cada script) e `inventario_v2.json` (cada Parquet, filas, columnas y tipos). El ZIP original no se ha reemplazado.

## Hallazgos confirmados

| Elemento | Hallazgo en código y tablas v2 | Decisión v3 |
|---|---|---|
| Identidad | F1–F7 son equipos agregados. No hay motor/DE/NDE identificados por separado. | Jerarquía explícita de siete activos, un conjunto de predicción. |
| Rodamientos | Una temperatura y una vibración agregadas. | Señales DE/NDE nuevas; no copiar la misma serie en ambos apoyos. |
| Corriente | `corriente_motor_pct_nominal`, en porcentaje. | `current_a` en A con nominal ficticio de 1600 A, declarado en configuración. No se presenta como conversión de una corriente real. |
| Velocidad | En cajas, `rpm=vout/.35*60/(2*pi)`: se deriva de banda y radio supuesto. | Velocidad del eje motor lógico independiente. No atribuir a v2 una velocidad real de motor. |
| Fallo progresivo | Se dispara cuando el daño interno alcanza 1. Hay ruido y firmas por modo, pero disparo determinista. | Riesgos probabilísticos competidores según daño y carga; choque súbito separado. |
| Sensor | Ausencias, bloqueos, picos y deriva global de vibración; disponibilidad siempre igual al instante observado. | Registrar deriva como incidencia por señal y añadir latencias de 0/5/10/20 min; construcción as-of y abstención por calidad. |
| Temperatura | Se calcula instantáneamente desde ambiente/carga/precursor; sin enfriamiento inercial en parada. | Estado térmico con relajación gradual durante operación y paradas. |
| Mantenimiento | Preventivo parcial; correctivo reinicia el componente equivalente. | Sustitución o reparación parcial del componente afectado; otros daños permanecen. |
| Objetivos | 4/8/24 h; benchmark a 8 h, HistGradientBoosting. | Un objetivo y24 para el conjunto. Modelos aún no entrenados. |
| Evaluación | Cortes cronológicos y purga de 24 h. | Cortes por fecha compartidos entre ejecuciones base, margen de 28 h y exclusión de episodios completos que cruzan fronteras; dos mundos de estrés reservados. |

En F3 había **15 fallos**: 6 de refrigeración, 3 hidráulicos, 3 de reductor, 2 de lubricación y **1 de rodamiento**. Filtrar F3 no proporciona eventos ni señales separados suficientes para el nuevo contrato.

## Reutilización real

**Reutilización directa de datos:** únicamente el catálogo sintético de cuatro productos, copiado sin cambios a `config/productos_base_v2.parquet` y `data/productos.parquet`. Se incluyen copias de los documentos de referencia en `docs/referencia/`.

**Reutilización conceptual/adaptación:** semilla reproducible, Parquet por unidad, fechas UTC, unión por claves, separación de objetivos/verdad, censura por preventivos, ventanas retrospectivas, validación temporal, auditoría de integridad, exportación CSV y patrón de carga PostgreSQL.

**Implementación nueva:** simulación de motor y dos apoyos; contratos de señales; disponibilidad temporal; snapshots, etiquetas y particiones; diccionario y SQL; comprobaciones específicas. No se ha reutilizado ni interpolado la telemetría v2. No se afirma un porcentaje de código reutilizado: no sería una medida útil de compatibilidad entre dos alcances distintos.

## Compatibilidad y migración

`docs/migracion_29_columnas_v2_v3.csv` resuelve las 29 columnas de telemetría v2 una a una. La v3 no es una actualización binaria compatible con scripts que esperan `equipo_id`, `fallo_8h` o las tablas de toda la acería. La clave nueva es `(run_id, assembly_id, timestamp)`.

Se omiten del subsistema fuerzas del tren, balances de masa, espesores por caja, hidráulica, potencia de placa y costes. Se mantiene contexto de receta, régimen, carga, lubricación y refrigeración, con alcance explícito. No se interpreta `DEMO-C01` como equivalencia física verificada con F3.

La v2 permanece como referencia de proceso y EDA general. No unir eventos v2 y v3 como si fueran el mismo historial ni comparar sus métricas de modelo: cambian unidad, simulador, horizonte principal y particiones.
