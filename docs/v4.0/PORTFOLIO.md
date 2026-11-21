# v4.0 · Lectura para reclutadores

**Joseph · [JsphLynx](https://github.com/JsphLynx)**

Proyecto personal de ingeniería y ciencia de datos para diseñar un experimento de mantenimiento predictivo de un motor y dos apoyos en un contexto de laminación en caliente. Desarrollado con asistencia de IA; sin afiliación ni validación empresarial implícita.

> El dataset v4.0 está generado y documentado. Sus fuentes y ejemplos están incorporados desde los ZIP verificados. El estado de distribución y los suplementos se detallan en PUBLICACION.md. XGBoost e Isolation Forest todavía no se han entrenado sobre v4.0.

## Problema y decisión

La pregunta es si las señales disponibles permiten anticipar un fallo simulado con tiempo suficiente para **priorizar una inspección**, manteniendo una carga de falsas alertas asumible. No se propone parar automáticamente un tren real ni se calcula ahorro sin datos industriales.

## Qué aporta el trabajo

| Competencia | Decisión concreta | Evidencia que incorpora la versión |
|---|---|---|
| Análisis de negocio | Objetivo de fallo24h y presupuesto de falsas alertas | Protocolo de evaluación versionado |
| Ingeniería de datos | Conocimiento temporal, claves y ventanas causales | Generador, Parquet, features y targets separados |
| Modelado de dominio | Geometría, fuerza, par, transmisión y potencia | Modelo físico mínimo con supuestos explícitos |
| Arquitectura relacional | Configuraciones con validez e historial de mantenimiento | DDL PostgreSQL y consultas asof |
| Calidad y auditoría | Distinguir sensor defectuoso de fallo funcional | Controles físicos, temporales y de integridad |
| Pensamiento crítico | No atribuir OEM ni calibración sin evidencia | Investigación Sestao–SMS y auditoría posterior |
| Comunicación | Mostrar evolución y límites comprobables | Informes, diccionarios, catálogo y README |

## Tres decisiones técnicas relevantes

1. **Acotar el activo.** Una caja lógica, un motor y dos apoyos. El cojinete de un cilindro, el AGC y el buclero necesitan entidades y eventos propios.
2. **Respetar cuándo se sabe cada dato.** Un cierre futuro de mantenimiento o la verdad interna del simulador no son entradas disponibles para una predicción anterior.
3. **Separar consistencia y eficacia.** 2.100 controles y 94/94 archivos reproducidos son resultados documentados de verificación sintética, no métricas predictivas ni validación industrial.

## Estado y siguiente fase

Completado en la entrega original: generación, contratos, etiquetas/censura, particiones, diccionario, SQL, documentación y controles sintéticos.

Pendiente: entrenamiento y evaluación; integración PostgreSQL/Neon; prueba Windows/Spyder; demostrador de producto y validación con datos reales autorizados.

**Recorrido:** [contrato y arquitectura](ARQUITECTURA.md) → [evidencia documentada](VALIDACION.md) → [decisiones de auditoría](AUDITORIA_POSTERIOR.md) → [distribución y suplementos](PUBLICACION.md).
