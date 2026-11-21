# Publicación v4.0 · Distribución y trazabilidad

<!-- release-status -->
**Dataset v4.0 publicado:** [descargar las dos partes y hashes](https://github.com/JsphLynx/ML-Predecir-Fallos-Maquinaria-Industrial-4.0/releases/tag/portfolio-v4.0). Código, ejemplos y los informes internos del paquete están incorporados.
<!-- /release-status -->

Los dos ZIP reconstruyen **183 archivos dentro del paquete**, más un LEEME externo que aparece idéntico en ambas partes. Los **182 hashes** del manifiesto original coinciden.

| Destino | Contenido |
|---|---|
| [versions/v4.0](../../versions/v4.0/) | 90 originales: código, configuraciones, SQL, diccionario, contratos, ejemplos y resultados |
| [Release v4.0](https://github.com/JsphLynx/ML-Predecir-Fallos-Maquinaria-Industrial-4.0/releases/tag/portfolio-v4.0) | Los dos ZIP íntegros, incluyendo los 93 archivos de datos no incorporados a Git |
| [Informe de mejora](../reports/Informe_Mejora_Dataset_v4_0.pdf) | Copia original incluida en el paquete |
| [Investigación Sestao–SMS](../reports/Informe_Investigacion_Sestao_SMS_Contraste_v3_1.pdf) | Copia original incluida en el paquete |

El [catálogo](../catalogo_archivos_versiones.csv) registra ruta, tamaño, hash y ubicación. El manifiesto original se conserva intacto y debe comprobarse sobre el paquete completo extraído. Para el clon, usar `scripts/verificar_portfolio.py`.

[Integridad de importación](../verification/importacion_v4_0.json) · [Hashes de ZIP](SHA256SUMS.txt) · [Verificación de publicación](../VERIFICACION.md).

## Suplementos externos al paquete

Los siguientes PDF no forman parte de los 183 archivos y todavía no se han incorporado como binarios a GitHub:

- `Informe_Sestao_SMS_Dataset_Sintetico.pdf` (adjunto con nombre abreviado INFORM~1.PDF).
- `Auditoria_Aportes_Dataset_v4_0.pdf`: su contenido está resumido en [AUDITORIA_POSTERIOR.md](AUDITORIA_POSTERIOR.md).
- `Info_Predecir_Fallos_Anticipar_Mantenimiento_Maquinaria.pdf`: fuente externa comentada por la auditoría; el archivo no pudo recuperarse.

Esta lista evita presentar la publicación del dataset completo como si incluyera todos los documentos complementarios del chat. La copia adjunta del informe de mejora y el archivo INFORM~2.PDF pueden contener metadatos de distribución distintos; se publican las copias internas protegidas por el manifiesto.

Los vídeos existentes conservan su versión v3.1. No hay un vídeo nuevo de v4.0. Las versiones anteriores no se modifican.
