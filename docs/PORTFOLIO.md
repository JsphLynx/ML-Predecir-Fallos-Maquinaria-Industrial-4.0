# Versión vigente: v4.0

[Presentación actual para reclutadores](v4.0/PORTFOLIO.md) · [Código](../versions/v4.0/src/). El texto siguiente conserva la presentación histórica v1–v3.1.

---

# Lectura para reclutadores

**Autor del proyecto: Joseph · [GitHub: JsphLynx](https://github.com/JsphLynx)**

Proyecto personal de ciencia e ingeniería de datos para estudiar mantenimiento predictivo industrial. El caso se inspira en documentación pública de la línea CSP de Sestao. No existe colaboración empresarial implícita; los datos se han generado artificialmente.

## El problema de negocio

Una parada no planificada puede interrumpir la producción. La pregunta del demostrador es si las señales disponibles permitirían anticipar un fallo simulado con tiempo suficiente para revisar el equipo y con una carga de falsas alertas asumible.

La decisión propuesta es **priorizar una inspección**, no ordenar una parada automática. No se calcula ahorro industrial: faltan datos reales de averías, costes, intervenciones y consecuencias.

## Qué demuestra este repositorio

| Competencia | Evidencia concreta |
|---|---|
| Análisis de negocio | [Problema, decisiones y matriz de 19 fases](history/business_data_project_original.md) |
| Ingeniería de datos | [Generador v3.1](../versions/v3.1/src/01_generar_dataset.py), Parquet, contratos y claves temporales |
| Diseño relacional | [DDL PostgreSQL](../versions/v3.1/sql/01_esquema.sql) y [lecturas por instante de conocimiento](../versions/v3.1/sql/02_lecturas_asof.sql) |
| Ciencia de datos | [Modelo base v2](../versions/v2/resultados/modelo_base.json), [EDA](reports/eda_v3.pdf) y selección de variables permitidas |
| Evaluación rigurosa | [Protocolo v3.1](../versions/v3.1/docs/PROTOCOLO_PREENTRENAMIENTO.md): separación temporal, alertas por evento, comparadores e incertidumbre |
| Auditoría y mejora | [Auditoría v3](reports/auditoria_v3.pdf) y [cierre v3.1](reports/cierre_auditoria_v3_1.pdf) |
| Comunicación técnica | [Vídeos, guiones y fuentes editables](../media/README.md) |

Los archivos incluyen material desarrollado con asistencia de IA. La evidencia del proyecto debe juzgarse por el código, las decisiones documentadas y los resultados verificables; la existencia de un informe no sustituye a una ejecución.

## Tres decisiones que explican la evolución

1. **Acotar el problema.** El escenario general de una línea CSP de v1/v2 sirve para aprender el proceso; v3 concentra el diseño en un motor y dos apoyos DE/NDE para concretar señales, fallos y evaluación.
2. **Respetar el tiempo de conocimiento.** Una fecha de mantenimiento observada después del fallo no puede tratarse como conocida antes. v3.1 introduce un historial versionado y consultas `asof`.
3. **Evaluar utilidad, no solo clasificación.** Un gran número de filas correlacionadas no equivale a muchos fallos independientes. Se contabilizan eventos, falsas alertas, anticipación, cobertura y abstenciones.

## Estado y alcance

Se conservan experimentos históricos de modelos base en v1 y v2. Para el subsistema v3.1, XGBoost e Isolation Forest están pendientes de entrenamiento y evaluación bajo el protocolo fijado. API de producto, dashboard final y despliegue no están completados.

La inspección de test/estrés para auditar estructura ya está documentada. No se presentan como conjuntos nunca vistos por el analista. Las métricas de v1, v2 y el futuro experimento v3.1 no deben compararse como una mejora lineal: cambian horizonte, escenario y política de alerta.

**Recorrido de cinco minutos:** [evolución](EVOLUCION.md) → [auditoría](reports/auditoria_v3.pdf) → [correcciones](../versions/v3.1/docs/CIERRE_AUDITORIA.md) → [código del evaluador](../versions/v3.1/src/protocolo_evaluacion.py) → [siguientes fases](ROADMAP.md).
