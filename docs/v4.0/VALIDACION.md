# Evidencia de validación v4.0

## Resultados del cierre original

La tabla reproduce los resultados de *Informe_Mejora_Dataset_v4_0.pdf*, página 5. **No se han vuelto a ejecutar estas baterías en esta incorporación a GitHub.**

| Batería | Correctos | Fallidos |
|---|---:|---:|
| Datos y causalidad | 734 | 0 |
| Catálogo y segmentos | 108 | 0 |
| Evaluador con fixtures | 44 | 0 |
| Cierre y preparación | 756 | 0 |
| Replay de disponibilidad | 64 | 0 |
| Física y sensibilidad | 318 | 0 |
| Contratos y SQL | 76 | 0 |
| **Total** | **2.100** | **0** |

La reproducción original obtuvo **94/94 archivos idénticos por SHA-256**: Parquet y contrato de columnas. El paquete incluye 18 tablas y 399 definiciones de columna. El parser SQL aceptó DDL y funciones; eso no equivale a ejecutar una base de datos.

## Auditoría posterior del 21/11/2026

*Auditoria_Aportes_Dataset_v4_0.pdf*, página 1, documenta una comprobación posterior de los **182 archivos del manifiesto**, sin diferencias. Los 183 archivos del paquete incluyen el propio manifiesto; son un recuento distinto de los 94 archivos de reproducción.

La auditoría posterior revisó documentación y muestras e hizo dos comprobaciones numéricas. No repitió las 2.100 pruebas originales ni entrenó modelos.

## Particiones documentadas

Fuente: informe de mejora, página 6.

| Partición | Decisiones | Utilizables | Positivas utilizables |
|---|---:|---:|---:|
| train | 227.142 | 174.158 | 23.300 |
| validation | 52.329 | 39.978 | 5.620 |
| test | 71.948 | 54.535 | 7.346 |
| stress | 140.096 | 99.629 | 15.516 |
| excluida | 69.125 | 0 | 0 |
| Total | 560.640 | 368.300 | 51.782 |

Utilizable requiere etiqueta y calidad válidas, además de partición permitida. No usar el número de filas correlacionadas como número de fallos independientes.

## Verificación de esta publicación

Los originales ya se han importado: 182/182 hashes coinciden. [Evidencia de importación](../verification/importacion_v4_0.json). Las nuevas comprobaciones se registran separadas de las 2.100 originales en [VERIFICACION.md](../VERIFICACION.md).

## Límites

No hay entrenamiento de XGBoost/Isolation Forest sobre v4.0, métricas predictivas industriales, ahorro acreditado, integración PostgreSQL/Neon ejecutada ni prueba Windows/Spyder. Revisar estructuras/etiquetas de test y estrés para auditoría no autoriza ajustar modelos con esas particiones.
