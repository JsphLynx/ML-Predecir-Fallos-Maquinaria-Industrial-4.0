# Verificación v4.0 · 21/11/2026

[Importación ejecutada en GitHub Actions](verification/importacion_v4_0.json): ambos ZIP coinciden en tamaño y SHA-256; 182/182 archivos del manifiesto original correctos; 90 originales en Git, 93 de datos solo en los ZIP; sintaxis de 24 archivos Python comprobada. No se ha entrenado ni regenerado el dataset completo.

Las comprobaciones de cierre quedan registradas en [cierre_v4_0.json](verification/cierre_v4_0.json). Los 2.100 controles y 94/94 archivos reproducidos son evidencia histórica del paquete original.

Los dos informes PDF requeridos están publicados; no quedan PDF pendientes de incorporación. [Alcance documental cerrado](v4.0/PUBLICACION.md). Windows/Spyder, PostgreSQL/Neon y validación industrial no han sido ejecutados para v4.0.

---

# Verificación de la publicación

Publicación inicial: **15/11/2026**. Cierre de distribución: **19/11/2026**. Estas revisiones organizan y comprueban el material existente; no entrenan modelos nuevos.

## Cierre de publicación · 19/11/2026

- Los cuatro ZIP originales coinciden con sus tamaños y SHA-256 registrados.
- Los 410 archivos incluidos en sus manifiestos se han vuelto a verificar: 30 de v1, 113 de v2, 99 de v3 y 168 de v3.1; ningún error.
- Las 44 pruebas del protocolo se han vuelto a ejecutar en una copia temporal: 44 correctas y 0 fallidas.
- Antes de actualizar la documentación, los 378 archivos del portafolio coincidían con su manifiesto; se comprobaron 101 enlaces internos y la sintaxis de 79 archivos Python.
- Los cuatro paquetes y el archivo de checksums están publicados. Se contrastaron los tamaños y SHA-256 de los activos recibidos por GitHub con los originales.
- Se actualizó el manifiesto del portafolio para recoger la documentación de cierre y se volvió a comprobar su integridad.

Evidencia de esta revisión: [cierre_publicacion_2026_11_19.json](verification/cierre_publicacion_2026_11_19.json). No se ha realizado entrenamiento, evaluación de modelos, regeneración completa, carga PostgreSQL ni prueba Windows/Spyder. Las comprobaciones de fixtures prueban el protocolo, no el rendimiento predictivo.

## Comprobaciones del 15/11/2026

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
