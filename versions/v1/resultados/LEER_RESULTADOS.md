# Resultado de la verificación — datos íntegramente sintéticos

23 comprobaciones superadas. No equivalen a validación de ingeniería.

| Tabla | Registros | Columnas |
|---|---:|---:|
| equipos | 19 | 7 |
| estado_linea | 25,920 | 6 |
| proceso_linea | 25,920 | 20 |
| telemetria | 492,480 | 12 |
| objetivos_ml | 492,480 | 6 |
| eventos_fallo | 72 | 6 |
| mantenimiento | 81 | 7 |
| bobinas | 10,262 | 22 |
| coladas | 2,671 | 6 |
| trazabilidad | 123,144 | 4 |
| pasadas_laminacion | 71,834 | 13 |
| perfiles_bobina | 379,694 | 5 |
| verdad_simulador | 492,480 | 3 |
| incidencias_sensor | 38 | 5 |

## Prueba de funcionamiento de ML, horizonte de cuatro horas

Average precision: 0.140; prevalencia de referencia: 0.852%.
Precisión por muestra: 18.0%; recall por muestra: 28.6%.
Aviso previo en 9 de 16 eventos evaluables del test.

El modelo base tiene limitaciones claras y genera falsos avisos. No se ha optimizado para obtener cifras vistosas. Los eventos son pocos; no se ha estimado incertidumbre. Los resultados solo prueban una ejecución de extremo a extremo sobre las hipótesis de este simulador.

La evaluación usa tiempo posterior sobre los mismos equipos. Las filas próximas no son eventos independientes. No presentar estas métricas como resultados de una planta real.
