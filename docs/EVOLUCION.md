# Evolución hasta v4.0

La nueva entrega relaciona geometría, fuerza, par, velocidades, potencia y corriente. Añade configuraciones temporales y contratos de sensores; sustituye bobina por segmento de producción. Es un nuevo experimento, no una mejora predictiva demostrada.

[Migración v3.1 → v4.0](../versions/v4.0/docs/MIGRACION_v3_1_v4_0.md) · [Investigación que motiva los cambios](reports/Informe_Investigacion_Sestao_SMS_Contraste_v3_1.pdf).

---

# Evolución documentada: v1 → v2 → v3 → v3.1

Las fechas corresponden a las entregas originales. La incorporación a GitHub es posterior, el 15/11/2026; no se reconstruyen commits históricos ficticios.

| Entrega | Fecha | Alcance | Telemetría | Fallos simulados | Aportación |
|---|---|---|---:|---:|---|
| [v1](../versions/v1/) | 29/10/2026 | 19 equipos equivalentes, 90 días | 492.480 filas | 72 | CSV comprimido, trazabilidad, generador y primer modelo base |
| [v2](../versions/v2/) | 01/11/2026 | 18 equipos funcionales, 18 meses | 2.835.648 filas | 210 | Parquet, SQL, diccionario, 19 fases y evaluación por episodios |
| [v3](../versions/v3/) | 04/11/2026 | Motor y apoyos; 8 mundos × 365 días | 840.960 filas | 398 | Jerarquía de activos, calidad/latencia y objetivo a 24 h |
| [v3.1](../versions/v3.1/) | 05/11/2026 | Mismo subsistema; 16 mundos × 365 días | 1.681.920 filas | 404 | Correcciones de auditoría, más escenarios y protocolo ejecutable |

**Fuente de los recuentos:** [v1/resumen_generacion.json](../versions/v1/resultados/resumen_generacion.json), [README v2](../versions/v2/README.md), [README v3](../versions/v3/README.md), [informe de cierre v3.1](reports/cierre_auditoria_v3_1.pdf). Son cantidades simuladas, no inventario ni averías de ACB. Los mundos son ejecuciones alternativas del mismo diseño.

## v1: demostrar el recorrido completo

Se representa el contexto de colada y laminación, las bobinas, los equipos y los eventos. El experimento principal del modelo base usa un horizonte de 4 horas, con partición temporal y selección del umbral en validación.

El resultado histórico recoge 9 eventos con aviso de 16 evaluables en test, pero los avisos se cuentan por fila, sin agrupar episodios ni estimar incertidumbre. No puede compararse directamente con las alertas de v2 o v3.1. [Resultado y limitaciones](../versions/v1/resultados/modelo_base.json).

## v2: ampliar el sistema y mejorar la evaluación

Se separan tablas de negocio, telemetría, variables, objetivos y verdad interna. El experimento principal a 8 horas compara HistGradientBoosting con una regla estadística y una política sin avisos.

| Test sintético v2, horizonte 8 h | HistGradientBoosting | Regla estadística |
|---|---:|---:|
| Eventos detectados / evaluables | 17/34 | 2/34 |
| Episodios de alerta | 58 | 22 |
| Falsas alertas | 41 | 20 |
| Anticipación mediana, solo detectados | 3,58 h | 2,46 h |

Fuente: [modelo_base.json](../versions/v2/resultados/modelo_base.json). **Las tasas de alertas observadas son diferentes.** Esto no demuestra superioridad a igual carga de avisos ni eficacia industrial. El experimento deja sin detectar la mitad de los eventos evaluables.

## v3: acotar a motor y rodamientos

El rediseño distingue motor, apoyo del lado de accionamiento (DE) y apoyo opuesto (NDE). Conserva telemetría a 5 minutos y decisiones a 15 minutos. El horizonte principal pasa a 24 horas. Se documenta [la correspondencia de las 29 columnas de v2](../versions/v3/docs/migracion_29_columnas_v2_v3.csv).

La auditoría obtuvo 486 comprobaciones correctas y 3 fallidas, relativas al mismo defecto de cronología en tres mantenimientos aplazados. También encontró simplificaciones de escenarios y criterios de evaluación pendientes. [Informe](reports/auditoria_v3.pdf) · [Evidencias y scripts](../audits/v3/).

## v3.1: cerrar hallazgos antes de entrenar

| Hallazgo | Respuesta documentada |
|---|---|
| H01: cronología de mantenimiento | Plan previsto, aplazado e iniciado; conocimiento separado de ejecución; consultas `asof` |
| H02: filas utilizables | Cero utilizables en partición excluida; calidad y elegibilidad contadas por separado |
| H03–H04: escenarios poco variados | Mundos de vida larga, calendarios irregulares y más defectos de adquisición |
| H05: pocos eventos en algunos estratos | Denominadores visibles, incertidumbre por mundos y resultados descriptivos cuando proceda |
| H06: referencia privilegiada para IF | Referencia observable principal y referencia ideal separada |
| H07: evaluación pendiente | Evaluador por episodios, comparadores y regla de éxito definidos antes de entrenar |
| H08: integración | Evidencias de PostgreSQL local y replay de llegada; Windows/Neon pendientes |

Fuente: [matriz de cierre](../versions/v3.1/docs/matriz_cierre.csv). Se documentan 1.693 comprobaciones correctas, ninguna fallida y 77/77 archivos idénticos en una segunda generación. Estas son evidencias de la entrega original: las nuevas comprobaciones de publicación se detallan por separado en [VERIFICACION.md](VERIFICACION.md).

**No hay entrenamiento de XGBoost ni Isolation Forest en v3.1.** La aceptación es para iniciar un experimento sintético; no acredita utilidad predictiva real ni ahorro económico.
