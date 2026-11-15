# Dataset ACB v3.1 — Del simulador al machine learning

Vídeo de animación gráfica en español basado en `ACB_Motor_Rodamientos_Sintetico_v3_1.zip`. Duración: 4 min 40 s, 23 escenas, 1920 × 1080, 30 fps, H.264/AAC. Textos explicativos y música electrónica original generada por código. Sin locución.

## Qué contiene

Problema industrial; evolución v2 → v3 → v3.1; generador; señales y calidad; correcciones; diccionario; PostgreSQL; etiquetas y censura; particiones; escenarios; evidencias; incertidumbre; preparación de XGBoost e Isolation Forest; comparadores; alertas; futura aplicación; limitaciones y protocolo antes de entrenar.

El paquete editable permite reconstruir el vídeo sin el dataset completo: basta con las fuentes tipográficas y `assets/chart_data.json`. El ZIP completo original no se duplica aquí.

## Reproducción

Instalar Python, Pillow, NumPy y FFmpeg (disponible en PATH). Ejecutar:

```bash
python render_video.py --preview
python render_video.py
python verify_video.py
```

`storyboard.json` contiene textos, duración y capítulos. `render_video.py` contiene composiciones y animaciones; `motion_engine.py`, utilidades gráficas y música original. `output/*.srt` contiene títulos y mensajes principales por escena; no transcribe todo el texto de pantalla. `Guion_y_fuentes.md` aporta el índice temporal y la trazabilidad. Las fuentes DejaVu incluyen su licencia.

Para recalcular los datos resumidos se necesita pandas, pyarrow, el ZIP original y los Parquet seleccionados extraídos en `source/inspeccion/`. `prepare_chart_data.py` realiza esa extracción numérica y la verificación de hashes. Estos Parquet grandes no se incluyen en el paquete editable.

## Qué está verificado

Se inspeccionaron documentos, configuración, código, SQL, diccionario y resultados de la entrega v3.1. Se comprobaron los hashes de los 168 archivos declarados: cero diferencias. La comprobación figura en `source/inspeccion_zip.json`. Se contrastaron las cifras del vídeo con las tablas del ZIP.

Las 1.693 pruebas correctas, cero fallidas y 77/77 archivos reproducidos idénticos son **evidencias incluidas en la entrega**, no pruebas ejecutadas de nuevo al producir el vídeo. No se volvió a generar todo el dataset ni se entrenó ningún modelo. `qa/validacion_video.json` registra por separado los controles audiovisuales.

Las series proceden del primer día UTC de R01 (288 registros de 5 min), sin interpolar los huecos. El gráfico de salud usa `resultados/escenarios_salud.csv`. Es salud interna conocida por el simulador, utilizada para auditar, nunca como predictor.

## Matices de interpretación

- Los 16 mundos son simulaciones alternativas de un mismo conjunto lógico, no 16 motores reales.
- La v2 y la v3 son antecedentes del proyecto; el paquete inspeccionado para esta producción es la v3.1.
- Las tres cajas del dibujo del tren son conceptuales; no representan el inventario de ACB.
- Las 256 definiciones corresponden a 16 tablas. El contrato ML contiene 113 entradas antes de codificar las categorías: 110 numéricas y 3 categóricas.
- El reparto 60/20/20 es del tiempo nominal, no del número final de filas utilizables.
- La cifra de siete estratos pequeños procede de `cohortes_eventos.csv`, que considera eventos de los intervalos nominales. No debe sustituirse por la población distinta de `eventos_por_particion.csv`.
- Isolation Forest usa 12.494 filas candidatas observables. No se garantiza que sean sanas. Su selección ideal privilegiada es una sensibilidad separada.
- Las exclusiones de episodios latentes se aplican al benchmark retrospectivo. En servicio, la elegibilidad solo puede depender de calidad y operación observables. Son evaluaciones separadas.
- Test y estrés ya fueron inspeccionados por estructura y calidad; no son «nunca vistos por el analista». No se han usado para elegir ajustes predictivos.
- La mejora de al menos cinco puntos de sensibilidad, intervalo pareado positivo y presupuesto de falsas alertas es un criterio fijado previamente, no un resultado conseguido.
- El score de Isolation Forest no es una probabilidad de fallo a 24 h. La probabilidad de XGBoost debe evaluarse, incluyendo calibración.
- El objetivo funcional es fallo en las próximas 24 h. Las etiquetas incompletas por preventivo o fin se mantienen nulas, no se convierten en ausencia de fallo.
- Windows/Spyder, Neon, dashboard, entrenamiento y validación industrial siguen pendientes.

El vídeo acredita un recorrido metodológico reproducible y explica la aceptación técnica sintética documentada. No demuestra capacidad predictiva, fiabilidad, ahorro, eficacia de intervención ni reducción real de paradas en ACB. No sugiere colaboración o aprobación oficial de ACB o ArcelorMittal.

## Fuentes

Fuente principal: ZIP versión 3.1.0, cierre del 05/11/2026. SHA-256: `b87cd6c257fa2844c629e6250ebd9af9e0aab290a40200a451f0fd38e16359dd`.

Definiciones generales de algoritmos contrastadas con documentación oficial:

- https://xgboost.readthedocs.io/en/latest/tutorials/model.html
- https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html

Estas referencias explican los algoritmos; no validan el simulador industrial ni sus parámetros. La música se sintetiza con NumPy, sin grabaciones externas.
