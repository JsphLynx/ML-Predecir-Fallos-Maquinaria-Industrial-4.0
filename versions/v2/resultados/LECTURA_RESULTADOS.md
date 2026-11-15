# Lectura crítica del benchmark

La generación final contiene 210 eventos. En test hay 34 eventos evaluables según la disponibilidad de decisiones previas; no hay 120.294 averías independientes, aunque el test contenga ese número de filas.

Con el umbral congelado en validación, ML detecta 17/34 y emite 58 episodios, de los que 41 son falsas alertas según la ventana útil de 30 minutos a 8 horas. La regla detecta 2/34 y emite 22 episodios, de los que 20 son falsos. La política sin avisos detecta 0 y no genera avisos.

Hay un techo común de carga en validación, pero no igualdad exacta de alertas entre métodos. No se afirma superioridad a igual tasa ni significación estadística. Las métricas empeoran respecto a validación: no se ha reajustado test para disimularlo.

Average precision de ML: 0,425; prevalencia en test: 0,00802. El ROC-AUC de 0,963 no significa detectar el 96,3% de los fallos. Recall por muestra: 35,75%; detección por evento: 50%. Son denominadores diferentes. Mediana de anticipación de 3,58 horas solo entre eventos detectados, no entre todos los fallos.

Las señales se construyen a partir de mecanismos inventados. Algunos equipos/modos tienen muy pocos eventos o ningún positivo en una partición (por ejemplo F3 en validación). La evaluación principal agrupa los equipos; no da soporte a un clasificador fiable para cada equipo/modo individual.

Las estadísticas no tienen intervalos de confianza por evento. La validación técnica de 494 pruebas y la reproducción exacta de 83 archivos del generador demuestran consistencia y determinismo de esta ejecución, no realismo metalúrgico ni eficacia empresarial.

Antes de modificar modelos: conservar esta versión como referencia, fijar nuevas hipótesis y reservar una simulación independiente de evaluación. Para transferencia industrial harían falta datos autorizados y revisión del dominio; actualmente fuera del alcance del proyecto.
