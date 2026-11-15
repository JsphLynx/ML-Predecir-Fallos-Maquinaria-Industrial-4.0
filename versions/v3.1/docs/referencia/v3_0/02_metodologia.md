# Metodología efectiva del dataset v3

## Grano y tiempos

Una fila de telemetría por ejecución, conjunto y cinco minutos. Cada fila contiene quince descriptores, contexto e historia disponible. Una decisión cada quince minutos, incluso si el equipo está parado o no hay calidad suficiente: esas decisiones conservan su causa de abstención. No son 280.320 observaciones independientes.

Todos los instantes son UTC. `timestamp` es observación/decisión; `available_at` es llegada del paquete de sensores. El estado operativo y la receta se suponen conocidos en `timestamp` por un canal de contexto local sin retraso. Las señales tienen retrasos de 0/5/10/20 minutos. Esta asimetría es un supuesto explícito del demostrador.

Los ocho mundos simulan el mismo diseño, no máquinas reales distintas. R01–R06 comparten mecanismos base. R07 aumenta carga y modifica mezcla de productos; R08 cambia exponente de desgaste, relación daño-señal, función de riesgo y nivel de ruido. Ambos aumentan ausencias/latencias. No son una validación de generalización a una planta real.

## Motor, apoyos y generación

`DEMO-C01-DRV01` contiene `DEMO-C01-M01`, con apoyos `DEMO-C01-BRG-DE` y `DEMO-C01-BRG-NDE`. La jerarquía y los apoyos son hipótesis del ejercicio. Los rodamientos de cilindros, reductores y demás activos quedan fuera.

Cuatro flujos aleatorios por ejecución: contexto/producto, daño/fallos, ruido de señales y adquisición. La semilla maestra y el índice de ejecución se combinan mediante `SeedSequence`; las versiones ejecutadas están en `resultados/entorno_ejecutado.json`.

Secuencia: calendario y receta → régimen/carga → evolución de daño de tres componentes → riesgo y fallo → intervención → observaciones, defectos y latencias → snapshots → etiquetas. Las funciones y coeficientes completos están en `src/01_generar_dataset.py`; no están calibrados contra datos reales.

El daño crece durante funcionamiento con carga, lubricación, refrigeración, vida latente variable y perturbaciones. La probabilidad de fallo en un intervalo usa `1-exp(-tasa*dt)`; la tasa depende del daño y carga. La tasa base por componente es `0.02 * max(daño-0.35,0)^3 * sqrt(carga)` por hora en escenarios base; R08 modifica su forma. Hay un riesgo súbito independiente de 1/1800 horas operativas. Un daño concreto no garantiza fallo en ese instante. Los sensores siguen dependiendo de reglas artificiales: un modelo puede aprenderlas.

Las temperaturas conservan inercia, también al parar. La velocidad motriz y la corriente se simulan como parámetros del motor lógico. La corriente nominal de 1600 A y los límites de los sensores son ficticios; no se deducen potencias ni tensiones de placa.

Mantenimiento preventivo cada 28 días (si coincide con reparación se pospone), duración supuesta de 6 h, con mejora parcial. Los correctivos pueden sustituir o reparar parcialmente el componente. Sus resultados solo se conocen 15 minutos después del cierre. Los otros componentes conservan su daño. Se guardan mejoras latentes exclusivamente en `sim_truth/reparaciones.parquet`.

## Señales, calidad y variables

Las quince señales son temperatura DE/NDE/devanado, vibración RMS DE/NDE, aceleración RMS DE/NDE, curtosis DE/NDE, corriente, carga, velocidad, ambiente, caudal de refrigeración y presión de lubricación. Son descriptores sintetizados: no hay ondas originales ni frecuencias de defecto verificables.

El generador inyecta ausencias aleatorias y bloques de pérdida, congelación, picos y deriva. `sim_truth/incidencias_sensores.parquet` registra las inyecciones para auditoría. Ese registro no se consulta al construir variables. La detección observable es parcial: una deriva dentro de rango puede pasar controles de calidad.

Ventanas retrospectivas de 30 min (seis slots) y 4 h (48 slots): media, desviación muestral y pendiente OLS por hora. Una ventana de cinco minutos aporta como máximo una observación: se representa por el último valor disponible, sin inventar desviación o pendiente. El último valor se acepta solo si tiene como máximo 10 minutos de antigüedad. No se rellena usando datos futuros ni se ajusta imputador alguno en esta entrega.

Cada estadístico usa observaciones en `(t-ventana,t]` y disponibles en `t`. Datos tardíos, ausentes o fuera de los límites del contrato no contribuyen. Los ocho esenciales son temperaturas DE/NDE/devanado, vibraciones DE/NDE, corriente, carga y velocidad. Se exige al menos 80 % de cobertura **en cada señal esencial** durante 30 min (en la rejilla de seis slots equivale a cinco válidos), ausencia de congelación detectada y antigüedad máxima de 10 min. Se detecta congelación si seis valores válidos consecutivos son idénticos en un régimen activo estable. Un solo pico puede excluirse y aun así dejar cobertura suficiente; no implica automáticamente abstención ni fallo de máquina.

`evaluation_status` distingue evaluable, régimen excluido, calentamiento, cobertura insuficiente, dato antiguo y sensor congelado. `quality_code` informa controles de calidad. Ninguno significa «saludable». Calentamiento inicial: cuatro horas. Regímenes elegibles: marcha sin carga y laminación; el resto se conserva pero no se modela inicialmente.

## Etiqueta y censura

`y24=1` si un fallo funcional propio comienza en `(t,t+24h]`, antes del siguiente preventivo y del fin de seguimiento. `y24=0` si se observa el horizonte completo sin fallo ni intervención preventiva. `y24` es nulo si el preventivo o el fin de observación impiden completar la ventana, salvo fallo ya observado antes de la intervención; también es nulo en regímenes no elegibles. El horizonte usa tiempo de calendario, no horas operativas.

La censura puede depender de mantenimiento y estado: este objetivo mide fallo observado bajo esa política. No estima RUL ni lo que habría ocurrido sin intervenir. `event_id` en objetivos es futuro retrospectivo y está prohibido como predictor. Una etiqueta puede ser conocida aunque el snapshot no sea evaluable; se conservan ambos conceptos separados.

## Particiones y referencia para Isolation Forest

R01–R06: primeros 60 % de días para train, siguientes 20 % para validation y últimos 20 % para test. Cortes comunes: **07/08/2024 00:00 UTC** y **19/10/2024 00:00 UTC**. Se excluyen las 28 h anteriores a cada frontera (24 h de horizonte + 4 h de ventana). R07–R08 quedan íntegros como estrés, salvo calentamiento inicial.

También se excluyen episodios latentes de degradación de un componente que crucen una frontera, junto con las 24 h anteriores al inicio de esos episodios. Degradación para esta auditoría significa daño >=0.55; su umbral es una convención del simulador, no el disparador de fallo. Las exclusiones conservadoras pueden abarcar días o semanas. Las proporciones finales utilizables no son 60/20/20. Se conservan las filas y motivos, sin redistribuirlas.

`healthy_reference_if` es un selector retrospectivo **solo de entrenamiento**: estado latente normal, ninguna incidencia de sensor inyectada que afecte a la ventana de cuatro horas, calidad suficiente y partición train. Hay 8.785 snapshots seleccionados. Este privilegio de conocer salud simulada sirve al demostrador; no existe automáticamente con datos reales. Nunca usar el selector, salud, daño, escenario, IDs o tiempo absoluto como entradas.

La única lista de predictores autorizados es `ml/columnas_modelo.json`. No hay normalización, imputación, calibración ni modelo ajustado. Esos procesos se ajustarán con entrenamiento; selección en validación y prueba final sin ajuste. El conjunto de estrés también debe permanecer reservado durante el futuro ajuste.

## Aceptación y límites

375 comprobaciones de datos, objetivos y causalidad; 50 comprobaciones de catálogo e intervalos; reproducción completa de 44 archivos mediante SHA-256. Incluye reconstrucción independiente de etiquetas, prefijos temporales y mutación de lecturas todavía no disponibles. Comprobar un simulador no demuestra realismo físico.

No se simula el flujo físico completo de bobinas, la dinámica de transmisión, vibración espectral, adquisición de alta frecuencia ni física electromagnética. `coil_id` es contexto de producto, no contabilización certificada de producción. El escenario está enriquecido con averías para demostración; no estima tasas, costes ni ahorro de la planta.
