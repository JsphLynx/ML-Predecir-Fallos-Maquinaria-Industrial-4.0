# Proceso y alcance documental

## Qué conocemos y qué no

ArcelorMittal describe Sestao como una planta de horno eléctrico y colada de planchón delgado para laminación directa. Su ficha enumera dos coladas CSP, dos hornos túnel, un tren y dos bobinadoras [S1]. La declaración ambiental de 2023 describe siete cajas [S2]. Son referencias públicas, no una comprobación de la instalación a 29/10/2026.

No se dispone de planos actualizados, lista de señales, manual de arranque, lógicas de enclavamiento, ajustes de regulación, frecuencias reales de fallo o límites operativos. No se reproduce un procedimiento de operación de ACB.

El acero líquido entra en la colada continua. **En las cajas del tren entra material ya solidificado: un planchón caliente**, no acero líquido. Esta distinción organiza la simulación.

## Recorrido del material

| Fase | Función | Datos de interés para el demostrador |
|---|---|---|
| Preparación y disponibilidad | Comprobar que equipos, servicios y automatización están disponibles; preparar programa de fabricación. Secuencia conceptual, no procedimiento de ACB. | Estado, disponibilidad, lubricación, hidráulica y temperaturas. |
| Colada continua | Paso de cuchara a artesa y molde; solidificación y extracción. | Grado, nivel del molde, temperatura de artesa, velocidad y accionamientos. |
| Corte | Separar planchones para la ruta por lotes considerada. | Actuador de tijera, presión e identificación del material. |
| Horno túnel | Mantener y homogeneizar temperatura antes del tren. | Temperaturas por zonas y accionamientos de rodillos. |
| Descascarillado | Retirar óxido superficial antes de laminar mediante agua a presión. | Presión, bomba y estado mecánico. |
| Enhebrado y siete cajas | Introducir la cabeza; reducir progresivamente espesor y coordinar velocidades. | Fuerza, par, corriente, separación, vibración y temperatura. |
| Régimen y salida de cola | Mantener geometría y estabilidad mientras pasa la banda; gestionar transitorios de final de pieza. | Cambios de velocidad, fuerza, tensión y estado operativo. |
| Mesa de salida y enfriamiento | Transportar y enfriar la banda hacia la temperatura de bobinado. | Caudal, temperatura y accionamientos. |
| Bobinado | Guiar, sujetar y enrollar la banda en la bobinadora seleccionada. | Accionamiento, tensión, temperatura y presión. |
| Extracción, identificación e inspección | Retirar y registrar bobina, tomar muestras y realizar operaciones posteriores. | Fin de bobinado y características finales. |

La cadena de transformación de ACB se sustenta en [S1, S2]. El papel general de descascarillado, refrigeración y bobinadoras se apoya en [S3, S4]. La preparación, descomposición de estados y variables elegidas son una propuesta de modelado.

El decapado es una operación posterior y queda fuera del conjunto. Fusión y afino se representan únicamente mediante lotes de colada y composición ilustrativa; no se simulan los hornos eléctricos ni hornos de cuchara.

## Similitud entre factorías

La combinación de colada de planchón delgado, horno túnel, tren, enfriamiento y bobinado es común en CSP [S3]. Un tren convencional puede añadir recalentar planchones gruesos y desbaste [S4]. No corresponde copiar sin ajustes sus velocidades, equipos, recetas o degradación a una línea compacta.

## Fuentes

- [S1] ArcelorMittal Europe, ficha de Sestao: https://flateurope.arcelormittal.com/ourmills/spain/sestao
- [S2] ArcelorMittal Sestao, Declaración Ambiental 2023: https://spain.arcelormittal.com/wp-content/uploads/declaracion-ambiental-2023.pdf
- [S3] SMS group, CSP Nexus (estructura CSP de referencia): https://www.sms-group.com/pt-br/insights/all-insights/csp-nexus
- [S4] SMS group, Hot strip mills for steel: https://www.sms-group.com/plants/all-plants/hot-strip-mills-steel/

Consulta: 29/10/2026. Las fichas públicas no son una aprobación de este simulador. El PDF S2 se contrastó mediante su texto indexado; no se inspeccionó visualmente el documento completo.
