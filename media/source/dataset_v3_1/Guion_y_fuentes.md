# Guion temporal y trazabilidad

| Inicio | Duración | Escena | Mensaje |
|---|---:|---|---|
| 00:00 | 10 s | Del dato al mantenimiento anticipado. | Un proyecto sintético para aprender a aplicar machine learning en maquinaria industrial. |
| 00:10 | 12 s | Una parada no planificada interrumpe el flujo. | Objetivo del proyecto: anticipar fallos y priorizar el mantenimiento. El ahorro real aún no está demostrado. |
| 00:22 | 12 s | Acotar. Adaptar. Auditar. | La v2 permanece como referencia; la v3 centra el trabajo en motor y apoyos; la v3.1 incorpora la revisión. |
| 00:34 | 10 s | Mucho más que una tabla. | Datos, código, contratos y evidencias permiten seguir el recorrido de cada decisión del proyecto. |
| 00:44 | 14 s | Simular una historia, no sortear una etiqueta. | Configuración y semillas fijadas; degradación, fallos y reparaciones con incertidumbre. Parámetros no calibrados a ACB. |
| 00:58 | 14 s | Motor y apoyos se observan por separado. | Series extraídas de R01. Son descriptores sintéticos de 5 minutos, no ondas de vibración de alta frecuencia. |
| 01:12 | 14 s | Medir no significa poder evaluar. | Se controlan ausencias, retrasos, valores fuera de rango y sensores congelados. Mala calidad puede producir abstención. |
| 01:26 | 12 s | Corregir antes de entrenar. | Se recalculan los datos afectados sin cambiar semillas para buscar mejores resultados predictivos. |
| 01:38 | 14 s | Cada columna tiene un significado y un uso. | Las estadísticas usan solo observaciones disponibles en la decisión. Salud interna y fallo futuro quedan fuera de las entradas. |
| 01:52 | 12 s | Relacionar los datos. Separar los permisos. | Claves, transacciones y consultas por instante de conocimiento. El lector no recibe objetivos ni verdad privada. |
| 02:04 | 12 s | Desconocido no significa «sin fallo». | El siguiente preventivo y el fin del seguimiento pueden dejar el horizonte incompleto. Esas etiquetas se conservan nulas. |
| 02:16 | 12 s | Aprender del pasado. Evaluar después. | Cortes por fechas comunes, purga de 28 h, calentamiento de 4 h y exclusión de episodios que cruzan fronteras. |
| 02:28 | 12 s | El ensayo necesita situaciones diferentes. | Vida larga, carga y ruido variables. La proporción de salud es verdad simulada para auditoría, nunca un predictor. |
| 02:40 | 14 s | Evidencias incluidas en la entrega. | Pruebas técnicas de coherencia y causalidad. No son ensayos estadísticos independientes ni validación industrial. |
| 02:54 | 12 s | Muchos registros no son muchas máquinas. | Los 16 mundos son simulaciones alternativas. La incertidumbre debe acompañar los resultados y no puede eliminarse contando más filas. |
| 03:06 | 14 s | Aprender a estimar el riesgo de fallo. | XGBoost utilizará variables observables y etiquetas conocidas de entrenamiento. El modelo todavía no está entrenado. |
| 03:20 | 14 s | Detectar lo que se sale del patrón. | Una puntuación de anomalía no equivale a una probabilidad de fallo en 24 horas. El modelo todavía no está entrenado. |
| 03:34 | 13 s | Un modelo complejo debe justificar su uso. | Ajustes con entrenamiento; umbrales con validación. Test y estrés evalúan después de congelar las decisiones. |
| 03:47 | 12 s | Evaluar eventos, no solo acertar filas. | Sensibilidad por fallo, falsas alertas, anticipación, cobertura y abstención. Los huecos permanecen en el reloj. |
| 03:59 | 10 s | Del aviso a una decisión de mantenimiento. | Flujo conceptual de una futura aplicación. La inspección y la intervención deben quedar a cargo de profesionales. |
| 04:09 | 10 s | Demostración sintética, no promesa industrial. | Sin datos reales no se acredita capacidad predictiva, ahorro ni fiabilidad sobre la maquinaria de ACB. |
| 04:19 | 12 s | Iniciar con una versión congelada. | Antes de entrenar: repetir verificaciones y registrar entorno, semillas, variables y decisiones. Guardar modelo, preparación y política antes del test. |
| 04:31 | 9 s | Preparado para aprender. Preparado para comprobar. | Próxima fase: entrenar, comparar y evaluar XGBoost e Isolation Forest bajo el protocolo definido. |

## Fuentes del ZIP

| Hecho o gráfico | Fuente |
|---|---|
| Cambios H01–H08 | CHANGELOG.md; docs/CIERRE_AUDITORIA.md |
| Simulador | src/01_generar_dataset.py; config/escenario.json |
| Señales R01 | data/telemetria/R01.parquet, primer día UTC |
| Variables, calidad | src/02_construir_variables.py; ml/columnas_modelo.json |
| Diccionario | docs/diccionario_datos.csv |
| Etiquetas y cortes | src/03_etiquetas_particiones.py; resultados/particiones.csv |
| SQL | sql/; resultados/postgresql_ejecutado.json |
| Salud por mundo | resultados/escenarios_salud.csv |
| 404 fallos | data/fallos.parquet |
| Siete estratos pequeños | resultados/cohortes_eventos.csv |
| Referencia IF | resultados/referencias_if.csv: observable |
| Pruebas técnicas | resultados/validacion.json: 705; validacion_catalogo_segmentos.json: 91; pruebas_protocolo.json: 44; cierre_correcciones.json: 762; replay_llegada.json: 64; postgresql_ejecutado.json: 27 |
| Reproducción | resultados/reproducibilidad.json: 77/77 |
| Aceptación | resultados/aceptacion_v31.json |
| Protocolo | docs/PROTOCOLO_PREENTRENAMIENTO.md; config/protocolo_preentrenamiento.json; src/preparacion_ml.py |

Esquemas conceptuales: tren de laminación, árboles, particiones de Isolation Forest, ejemplos de etiquetas y votos de alerta. No son resultados predictivos ni mediciones reales de ACB.