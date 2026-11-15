# Fuentes, supuestos y límites

## Evidencia del proyecto

Los paquetes originales v1, v2, v3 y v3.1 contienen los generadores, diccionarios y resultados. La [verificación de publicación](VERIFICACION.md) distingue las pruebas repetidas ahora de los resultados históricos conservados.

## Contexto industrial

| Fuente aportada al proyecto | Uso y alcance |
|---|---|
| ArcelorMittal Sestao, Declaración Ambiental 2024 | Contexto de proceso; consultar alcance de lectura y páginas en la documentación original |
| ArcelorMittal Sestao de un vistazo, ficha histórica | Referencia dimensional e industrial histórica; no especificación actual ni inventario de sensores |
| Javier Pindado Cebrián, Estudio de eficiencia de una acería en Sestao | Contexto académico del proceso; no caracterización actual del motor |
| [Página oficial de Sestao](https://spain.arcelormittal.com/que-hacemos/productos-planos/sestao/) | Enlace de referencia documental conservado |

El detalle de fuentes, páginas y supuestos está en [fuentes v2](../versions/v2/docs/01_fuentes_y_decisiones.md), [fuentes v3](../versions/v3/docs/05_fuentes_supuestos.md) y [arquitectura original](history/arquitectura_subsistema_original.md). Esta publicación no amplía la lectura histórica ni verifica de nuevo la configuración real de la planta.

El [informe de búsqueda de datasets públicos](research/datasets_publicos_informe_historico.md) se conserva como investigación histórica. Sus enlaces y condiciones de acceso requieren nueva comprobación antes de adoptar datos externos.

## Límites que se mantienen en todas las versiones

- Datos artificiales, sin acceso a telemetría ni averías reales de ACB.
- Parámetros de sensores, tasas de fallo y mantenimiento no calibrados con la planta.
- Los descriptores a 5 minutos no sustituyen a señales de vibración de alta frecuencia.
- Salud, daño y verdad interna del simulador son material de auditoría, no entradas permitidas al modelo.
- Los resultados sintéticos no acreditan ahorro, retorno económico, fiabilidad real ni transferencia a otra máquina.
- Las imágenes conceptuales no son planos ni fotografías de ingeniería verificadas.
- Los horizontes y políticas cambian entre versiones: no sumar datos ni comparar métricas sin controlar esas diferencias.

## Autoría y reutilización

Proyecto personal de Joseph, desarrollado con asistencia de IA. Los nombres de empresas se utilizan como referencia contextual, sin patrocinio ni afiliación implícitos. No se añade una licencia general no elegida por el autor. Las fuentes de terceros y las tipografías conservan sus avisos; las licencias incluidas en las carpetas de fuentes se aplican a esos componentes.
