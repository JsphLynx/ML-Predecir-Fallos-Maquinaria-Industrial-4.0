# Auditoría posterior · Conservar la base v4.0

Fuente leída completa: *Auditoria_Aportes_Dataset_v4_0.pdf*, 21/11/2026, cinco páginas. Es una auditoría documental/técnica posterior a la generación, no una nueva versión del dataset.

## Dictamen

Mantener v4.0 como referencia para el entrenamiento sintético. El documento adicional examinado por la auditoría no contiene historial real de sensores, cambios de cilindro o averías fechadas del accionamiento que permitan recalibrar Sestao.

## Decisiones que se incorporan a la documentación

- La declaración ambiental 2024 identifica siete cajas. v4.0 representa una caja lógica; no seis cajas reales ni una réplica de F4.
- El vínculo CSP con SMS no identifica por sí solo el fabricante/modelo del motor.
- Separar referencias históricas de producto por fecha y fuente. No combinar extremos de catálogos distintos para inventar un rango.
- Los apoyos DE/NDE del motor no son cojinetes de cilindros; AGC, buclero, husillo y cilindros requieren activos y objetivos propios.
- La temperatura tras el horno, la temperatura de banda, el agua de cilindros y la refrigeración del motor corresponden a ubicaciones/circuitos distintos.
- Los datos estudiados de Nucor proceden de Decatur; no se deben atribuir automáticamente a Crawfordsville ni a una instalación CSP idéntica.

## Por qué no sustituir el generador por el script del documento adicional

Según la revisión del código impreso, su alarma contemporánea reproduce umbrales; no constituye una etiqueta de avería futura. Además, la fórmula de corriente contradice sus rangos, las etiquetas de modo/RUL pueden revelar el estado interno y ni la bobina ni la campaña quedan identificadas correctamente.

La auditoría ilustra el problema eléctrico con un caso sano que produce 56.138 A en la fórmula propuesta, frente a su rango declarado de 1.800–4.500 A. Es una comprobación aritmética del documento, no una medida real ni una estimación de falsas alarmas de v4.0.

## Ampliaciones posibles, aún no implementadas

1. Estimar longitud laminada por segmento a partir de velocidad y tiempo, con cobertura y disponibilidad temporal.
2. Crear campañas solo con identidad del cilindro y eventos de montaje/retirada. Una parada o un servicio al motor no implican cambio de cilindro.
3. Modelar AGC/perturbaciones en un módulo separado con etiquetas por activo.
4. Versionar cualquier cambio de dinámica, cadencia o predictores y repetir su verificación antes de evaluar modelos.

La muestra auditada ilustra aproximadamente 0,822 km en un intervalo de 300 s usando extremos de 2,7404 m/s. No demuestra longitud de bobina ni fecha de montaje. Una lectura que todavía no había llegado no puede sumarse retrospectivamente a una variable ML anterior.

## Estado de las fuentes originales

El PDF de esta auditoría sigue pendiente de revisión manual e incorporación. Las observaciones anteriores se atribuyen a la auditoría que sí se leyó. El documento externo analizado por ella no forma parte de los archivos requeridos para esta publicación; su script no se trata como código ejecutable validado.
