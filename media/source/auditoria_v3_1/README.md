# Auditoría ACB v3.1 - Animación gráfica

Vídeo explicativo horizontal de 2 minutos y 30 segundos. Full HD (1920 × 1080), 30 fps, H.264/AAC. Textos en español y banda sonora electrónica original, sin locución. La música se puede silenciar sin perder la explicación.

## Fuente y fidelidad

Basado en el Informe de cierre de auditoría de 05/11/2026. El PDF se conserva en `source`; su huella está en `source/trazabilidad.json`. Los gráficos de salud y frecuencia son recortes de la imagen original del informe. No se han estimado ni inventado sus valores. La animación revela los gráficos y destaca grupos sin modificar los datos.

Los recuentos animados se estabilizan en los valores documentados: 1.681.920 medidas, 560.640 decisiones, 404 fallos, 16 mundos, 1.693 comprobaciones y 77/77 archivos idénticos. El movimiento inicial de un contador es una transición gráfica, no una serie temporal.

Los esquemas de rodamientos, líneas de sensores y persistencia son ilustraciones conceptuales identificadas en pantalla. No son fotografías de ACB, mediciones del dataset ni resultados de modelos.

## Contenido

1. Por qué auditar antes de predecir.
2. Cadencia 5/15 minutos y horizonte 24 h.
3. Dimensión del laboratorio sintético.
4. Cronología del mantenimiento y corrección de sustituciones.
5. Escenarios de vida larga y variación instrumental.
6. Gráfico documental de salud del simulador.
7. Gráfico documental de tasas simuladas de fallo.
8. Entradas permitidas y referencias de Isolation Forest.
9. Persistencia de alertas y presupuesto de falsas alarmas.
10. Comparadores y criterio de mejora.
11. Evidencias ejecutadas y PostgreSQL local.
12. Incertidumbre por sucesos escasos.
13. Límites y verificaciones pendientes.
14. Conocimiento, desarrollo e impacto por demostrar.

## Reproducir o editar

Instalar Python 3.12, Pillow y NumPy. Instalar FFmpeg y añadirlo al PATH. Las fuentes DejaVu se incluyen con su licencia.

```bash
python -m pip install pillow numpy
python render_video.py --preview
python render_video.py
```

Editar `storyboard.json` para títulos, pies y tiempos. Las composiciones se editan en `render_video.py`. El render genera el MP4, una banda WAV original y subtítulos externos SRT. Se entrega también el SRT generado para facilitar reutilización.

Los subtítulos externos resumen las escenas; la información gráfica principal ya está visible en pantalla. No son una transcripción de voz: el vídeo no lleva locución.

## Alcance

Datos sintéticos, sin XGBoost o Isolation Forest entrenados. Las pruebas técnicas no certifican capacidad predictiva industrial, fiabilidad de ACB ni ahorro económico. Windows/Spyder, Neon y dashboard final no se presentan como verificados. El siguiente paso es entrenar y evaluar bajo el protocolo congelado.
