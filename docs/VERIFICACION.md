# Verificación de la publicación

Fecha: **15/11/2026**. Esta revisión organiza y comprueba el material existente; no entrena modelos nuevos.

## Ejecutado ahora

| Comprobación | Resultado |
|---|---|
| Integridad de v1 | 30/30 archivos del manifiesto original coinciden |
| Integridad de v2 | 113/113 coinciden |
| Integridad de v3 | 99/99 coinciden |
| Integridad de v3.1 | 168/168 coinciden |
| Fixtures del protocolo v3.1 | 44 correctos, 0 fallidos, ejecutados en copia temporal |
| Sintaxis Python | 79 archivos analizados sin error sintáctico |

Evidencia: [integridad_originales.json](verification/integridad_originales.json) y [publicacion.json](verification/publicacion.json). El total de 410 archivos corresponde a las entradas de los cuatro manifiestos; los propios manifiestos no se incluyen en ese total.

`PORTFOLIO_SHA256.json` protege la selección publicada en Git; es distinto de los manifiestos originales, que cubren también los datos grandes. Ejecutar `python scripts/verificar_portfolio.py` desde la raíz para comprobarlo.

## Evidencia histórica conservada

La entrega v3.1 registra 1.693 comprobaciones, PostgreSQL local y una segunda generación con 77/77 archivos idénticos. Estos resultados se preservan sin presentarlos como ejecuciones nuevas de la publicación. [Aceptación original](../versions/v3.1/resultados/aceptacion_v31.json).

Los experimentos de modelos base de v1 y v2 son históricos. No se han vuelto a entrenar ni reinterpretado como resultados del subsistema v3.1.

## No ejecutado en esta publicación

Regeneración completa de las cuatro versiones; entrenamiento; verificación Windows/Spyder; carga PostgreSQL; despliegue Neon; validación industrial. No se acredita ninguna de estas operaciones mediante la comprobación de hashes.

La automatización del protocolo sí utiliza un escenario corto del generador para comprobar las colisiones de mantenimiento, además de fixtures del evaluador. Esta prueba no sustituye a regenerar el dataset completo.
