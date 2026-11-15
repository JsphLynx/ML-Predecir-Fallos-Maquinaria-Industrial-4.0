# Diseño y uso correcto del dataset

## Unidad de observación y relaciones

- `equipos`: conjunto funcional equivalente; el componente causante aparece en `modo_fallo`.
- `telemetria/<equipo>.parquet`: una fila por equipo y timestamp UTC, también durante paradas/reserva. Lectura instantánea o indicador agregado disponible en t; vibración es RMS, no onda cruda.
- `bobinas`: una bobina o pieza interrumpida, con receta fijada al inicio y resultado disponible tras el cierre. Una bobina interrumpida NO cuenta como producto acabado.
- `estado_linea`: calendario de marcha y paradas a 5 min; bobina actual, velocidad y flujo de masa.
- `fallos`: un fallo causal de un equipo. El resto puede detenerse, pero no recibe etiqueta de avería propia.
- `mantenimiento`: preventivo o correctivo, con fecha de conocimiento; finalización es la referencia para edad desde mantenimiento.
- `paradas_linea`: intervalos por causa. Pueden solaparse un preventivo y un correctivo; calcular unión de intervalos, no sumar duraciones directamente.
- `ml/features`: decisiones en marcha cada 15 min, observaciones actuales y medias/desviaciones históricas de 1/4 h.
- `ml/targets`: etiquetas y partición, separadas físicamente de las características.
- `privado_no_usar_como_features`: daño, modo y precursor latentes e incidencias de sensores. Solo auditoría del generador.

Clave de telemetría/ML: `(equipo_id, timestamp)`. Unión 1:1 validada; no unir por posición de fila. Fechas UTC; convertir con `dt.tz_convert('Europe/Madrid')` para visualización sin alterar la clave.

## Mecánica del escenario

Cada campaña de ocho horas propone acero, ancho y espesor. Una bobina conserva su receta hasta completarse o interrumpirse. Masa, densidad asumida (7850 kg/m³), ancho y espesor determinan longitud; duración se redondea a múltiplos de cinco minutos y se obtiene la velocidad compatible. El ritmo resultante no se calibra con cifras comerciales de capacidad.

Las siete cajas comparten el mismo flujo másico y una reducción geométrica desde 60 mm hasta el objetivo. El cálculo de fuerza es una aproximación geométrica con tensión de fluencia supuesta; potencia y corriente son proxies separados del accionamiento. No hay balance energético completo, modelo térmico PDE, tensiones entre cajas ni simulación de solidificación. El transporte entre etapas se colapsa a una misma ventana; los timestamps no describen tránsito físico exacto por toda la planta.

El daño se acumula por exposición en marcha y carga, con ciclo de vida variable. El deterioro genera firmas distintas por modo, con ruido; reparación renueva el componente equivalente, y preventivo reduce daño sin renovarlo completamente. El choque eléctrico no recibe precursor específico. Los fallos de sensor se inyectan después e independientemente de la degradación.

La temperatura de material, fuerza y espesores de caja son valores sintéticos del proceso. Los sensores de condición tienen ruido, ausentes e incidencias. No usar estos rangos como límites de seguridad.

## Etiquetas y censura

`fallo_hh = 1` si empieza una avería del mismo equipo en `(t, t+h]`, antes del siguiente preventivo. Es `0` si se observa toda la ventana sin fallo ni preventivo. Es nula si la observación termina o interviene un preventivo antes de completar la ventana, salvo que ya se haya observado el fallo dentro de ella.

El horizonte mide horas de calendario, no horas de funcionamiento. Solo se decide con el equipo en marcha. Paradas de otros equipos afectan a la evolución simulada, pero no se etiquetan como fallo propio. Una bobina defectuosa tampoco es automáticamente una avería.

`horas_hasta_proximo_fallo_observado` y `proximo_fallo_id` son información retrospectiva del objetivo, **nunca features**. No constituyen RUL contrafactual: puede haber mantenimiento antes de ese fallo. Para supervivencia deben construirse episodios, exposición e intervenciones expresamente; el paquete no contiene un modelo RUL industrial.

## Particiones congeladas

| Partición | Inicio inclusivo | Límite exclusivo | Regla |
|---|---|---|---|
| train | 01/01/2024 | 01/01/2025 | Tras calentamiento histórico inicial de 4 h; purga de últimas 24 h |
| validation | 01/01/2025 | 01/04/2025 | Umbral y política seleccionados aquí; purga últimas 24 h |
| test | 01/04/2025 | 01/07/2025 | Una evaluación final; purga últimas 24 h |

No hacer `train_test_split` aleatorio. Estadísticas de imputación, codificación y normalización se ajustan con train. Las ventanas retrospectivas al inicio de validation/test pueden utilizar el pasado anterior: estaba disponible al decidir. La purga garantiza que etiquetas de entrenamiento no alcanzan el periodo siguiente.

El esquema mide futuro de equipos conocidos. No mide generalización a equipos, plantas o mecanismos desconocidos. Cambiar la semilla explora el mismo simulador, no valida transferencia real. Para selección futura repetida, reservar otra simulación independiente antes de iterar.

## Modelo de referencia y avisos

Se incluye HistGradientBoosting, regla estadística de vibración/temperatura y política sin avisos. La regla usa centros y escalas ajustados en observaciones normales de train. ML no incluye ID de equipo ni reloj absoluto.

El script fija hiperparámetros y explora una lista predefinida de umbrales en validation. Selecciona mayor detección por evento dentro de un presupuesto de 2 episodios por 1000 horas-equipo evaluadas; desempata por menos falsas alertas. Si ningún umbral finito cumple, permite no emitir avisos. No ajusta el modelo con test.

Un episodio es el primer cruce admitido tras un silencio de 8 horas por equipo. Se cuenta detección cuando hay alerta con 30 min–8 h de antelación. Cada fallo se cuenta una sola vez; una alerta demasiado tardía no es útil según esta política. Un evento es evaluable si hay al menos una decisión elegible en esa ventana: se informa el denominador, no se confunde con todos los fallos.

Las métricas incluyen average precision, prevalencia, precision/recall por muestra, detección por evento, falsas alertas, episodios por exposición y anticipación condicionada a detección. Brier del modelo se informa como error probabilístico, sin afirmar calibración. Millones de muestras no equivalen a millones de fallos independientes; resultados por modo escaso tienen alta incertidumbre. No se calculan intervalos de confianza ni se demuestra superioridad estadística.

## Ejecutar en Windows / Spyder

1. Descomprimir todo el ZIP en una carpeta local, conservando estructura.
2. Crear entorno con Miniforge: `conda env create -f environment.yml`; después `conda activate acb_ml_demo`.
3. En Spyder seleccionar el intérprete de ese entorno. Si Spyder requiere `spyder-kernels`, instalar la versión compatible que indique el propio IDE.
4. Los datos ya están generados. Ejecutar `src/00_empezar.py` para abrir una caja, unir objetivos por claves y explorar los datos sin cargarlos todos.
5. `src/02_validar_dataset.py` ejecuta la auditoría. `src/03_modelo_base.py` reproduce la evaluación y sobrescribe sus resultados locales.
6. Para regenerar desde cero ejecutar `src/01_generar_dataset.py`. Mantener la semilla y versiones para reproducir el mismo escenario.
7. `src/04_exportar_csv.py` crea CSV de un equipo seleccionado: compatible con pandas, R o herramientas BI. El paquete usa Parquet para tamaño y tipos; CSV no conserva por sí solo todos los tipos.

Comandos equivalentes en consola:

```bash
python src/00_empezar.py
python src/02_validar_dataset.py
python src/03_modelo_base.py
```

Dependencias registradas y ejecución verificada en Python 3.12 Linux. No se ha ejecutado directamente en Windows/Spyder ni en un servidor PostgreSQL. El SQL incluido es DDL y guion de carga propuesto; revisar y ejecutar en una base de pruebas propia.

Memoria: cargar un equipo cada vez para explorar. El modelo de referencia concatena los equipos y requiere más memoria; 8 GB libres es una reserva prudente, no una medición del pico. El generador permite cambiar `step_minutes` a 1 y mantener decisión a 15 min; esto cambia el escenario y aumenta sustancialmente volumen y coste. Volver a validar después de cambiar parámetros. Configuraciones muy cortas sin averías pueden no servir para ejecutar el benchmark.

La exposición del benchmark se aproxima como número de decisiones elegibles multiplicado por 15 minutos; no equivale a un registro continuo de horas de riesgo. El modelo térmico no incluye inercia durante paradas. Estas simplificaciones deben revisarse antes de cualquier interpretación física.
