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

## Alcance documental cerrado

Por decisión del autor, los únicos PDF requeridos para la publicación de v4.0 son:

- [Informe_Investigacion_Sestao_SMS_Contraste_v3_1.pdf](../../docs/reports/Informe_Investigacion_Sestao_SMS_Contraste_v3_1.pdf).
- [Informe_Mejora_Dataset_v4_0.pdf](../../docs/reports/Informe_Mejora_Dataset_v4_0.pdf).

Ambos están publicados en `docs/reports/` y `versions/v4.0/docs/`, y se conservan dentro de los ZIP originales. Las copias de cada informe coinciden byte a byte. No quedan PDF pendientes de incorporación.

`Auditoria_Aportes_Dataset_v4_0.pdf` queda excluido y retirado del registro de pendientes por decisión del autor; no estaba incorporado como archivo PDF al repositorio. La [síntesis histórica de la auditoría](AUDITORIA_POSTERIOR.md) se conserva como antecedente documental, sin exigir la publicación de ese PDF.

Los adjuntos duplicados `INFORM~1.PDF` e `INFORM~2.PDF` y el documento `Info_Predecir_Fallos_Anticipar_Mantenimiento_Maquinaria.pdf` también quedan fuera del alcance. Se conserva el informe original de investigación Sestao–SMS.

Este cierre documental no modifica el dataset, los paquetes originales ni sus hashes. El entrenamiento y la evaluación con XGBoost e Isolation Forest quedan para una fase posterior.

Los vídeos existentes conservan su versión v3.1. No hay un vídeo nuevo de v4.0. Las versiones anteriores no se modifican.
