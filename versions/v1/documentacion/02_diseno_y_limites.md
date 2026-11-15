# Diseño de datos, hipótesis y limitaciones

## Modelo generativo

La simulación no consiste en sortear columnas independientes. Un calendario y programa de producto determinan la demanda compartida. La carga afecta al desgaste, potencia, corriente, temperatura y vibración. La temperatura posee inercia y la vibración ruido autocorrelacionado. Un desgaste latente cruza un umbral, genera avería y desencadena una intervención con recuperación. También se introducen sucesos súbitos sin precursor deliberado.

La causalidad es la del simulador: carga → desgaste → señales y avería. Un modelo puede aprender esas reglas y aun así fallar en una instalación real. Las tasas de avería, vidas entre 250 y 550 horas equivalentes, costes, duraciones y magnitudes son hipótesis didácticas **deliberadamente enriquecidas con eventos**, no estimaciones de ACB.

La programación de producto introduce cambios de espesor, ancho y familia. Los arranques generan transitorios que pueden parecer averías. Se añaden pérdidas de comunicación, deriva de temperatura y ausentes independientes. No hay diagnóstico espectral de defectos ni clasificación físicamente validada de rodamientos frente a engranajes.

## Integridad física aproximada

- Geometría por bobina: masa = densidad × anchura × espesor × longitud; densidad de referencia 7.850 kg/m³ constante.
- Balance de masa: planchón = bobina + pérdidas sintéticas de 0,7–1,8 %. No se modela la distribución espacial de las pérdidas.
- Siete reducciones geométricas; espesor de entrada de cada caja igual a salida de la anterior.
- Conservación de caudal volumétrico entre cajas para una bobina, despreciando ensanchamiento y cambios de densidad.
- Fuerza basada en tensión de fluencia ilustrativa y longitud de contacto; par y potencia derivados. **No es un modelo metalúrgico validado ni un cálculo de dimensionamiento.**
- La integral del perfil de velocidad coincide con longitud de banda. Son perfiles ilustrativos separados de las series agregadas a cinco minutos.

## Simplificaciones que deben conocerse

1. La disponibilidad se trata como una sola isla: la indisponibilidad de un equipo detiene el conjunto. No se modelan buffers, continuidad de colada, desvíos, redundancias ni transiciones térmicas de una parada industrial real. Una avería de bobinadora no demuestra que una planta real deba detener todo el proceso.
2. Los 19 equipos son subsistemas equivalentes, no un inventario de todos los motores, válvulas, cilindros, guías o lazos. Las dos bobinadoras y líneas tienen señales de disponibilidad/carga agregadas; no se modela su ciclo individual de toma y extracción en telemetría. La trazabilidad sí selecciona una ruta por bobina.
3. Se registran bobinas completas solo en ventanas con disponibilidad a lo largo del recorrido. Las ventanas sin bobina completa no llevan un modelo explícito de material retenido, abortado o desechado.
4. `coladas` agrupa el material asignado en el alcance simulado. Su masa NO representa una carga de horno o una cuchara real. Las familias DEMO no son grados normalizados ni especificaciones comerciales.
5. Los hitos de trazabilidad son paso de cabeza, no intervalos completos de ocupación. No usar su resta como tiempo de residencia industrial exacto.
6. Los datos por caja y las señales agregadas de accionamientos trabajan a escalas distintas. No deben igualarse par o potencia entre ambas tablas: no se simulan cajas de engranajes, reparto entre motores ni relación cinemática calibrada.
7. Las señales térmicas y de proceso de `proceso_linea` son aproximaciones de contexto. No resuelven un balance térmico, la regulación de nivel ni la microestructura. Su instante no equivale al recorrido material de una bobina concreta; no deben unirse por proximidad como si fueran medidas de esa bobina.
8. Cinco minutos no permiten estudiar eventos rápidos como un enganchón, una rotura de banda o la evolución vibratoria de un rodamiento en frecuencia. Los perfiles de cinco segundos tampoco contienen vibración de alta frecuencia.
9. No se genera una etiqueta RUL industrial: las sustituciones preventivas y el final de observación censuran trayectorias. No confundir tiempo hasta intervención con vida útil restante hasta fallo.

## Tablas y claves

| Archivo en datos (.csv.gz) | Unidad y clave | Uso |
|---|---|---|
| equipos | equipo_id | Catálogo de subsistemas equivalentes. |
| estado_linea | timestamp | Programa y estado compartido. |
| proceso_linea | timestamp | Señales de proceso ilustrativas. |
| telemetria | timestamp + equipo_id | Variables observables por equipo. |
| objetivos_ml | timestamp + equipo_id | Etiquetas futuras y partición; no predictores. |
| eventos_fallo | evento_id | Inicio, fin y causa; información posterior al suceso. |
| mantenimiento | mantenimiento_id | Intervención, avería relacionada y coste final. |
| coladas | colada_id | Lote asignado y composición sintética. |
| bobinas | bobina_id; FK colada_id | Geometría y resultado final. |
| trazabilidad | bobina_id + orden | Ruta e hitos de cabeza; FK equipo_id. |
| pasadas_laminacion | bobina_id + caja | Valores calculados por pasada. |
| perfiles_bobina | bobina_id + timestamp | Perfil ilustrativo de velocidad. |
| verdad_simulador | timestamp + equipo_id | Desgaste oculto. EXCLUIR de ML. |
| incidencias_sensor | equipo_id + inicio + variable | Registro de inyección. EXCLUIR de ML. |

## Etiquetas y censura

Para un equipo en marcha en t: `fallo_proximas_4h=1` cuando comienza una avería de ese mismo equipo en **(t, t+4 h]**. Un fallo ya comenzado no es un futuro fallo. Se usa el mismo criterio para 1 y 24 horas.

La etiqueta queda vacía si el equipo no está en marcha, si el horizonte llega al final de observación o si hay intervención preventiva antes de terminar el horizonte. Este último criterio es conservador. El conjunto no representa efectos contrafactuales de una política preventiva distinta.

Partición temporal: días 1–54 entrenamiento, 55–72 validación, 73–90 test; se excluyen las últimas 24 h de las dos primeras particiones. Se mantienen juntos los equipos del mismo instante. Los huecos terminales permanecen censurados.

No usar en X: desgaste oculto, causa de fallo futuro, costes o duración de reparación futura, IDs como sustitutos de calendario, ni resultados finales de bobina antes de su disponibilidad. Los metadatos de partición tampoco son una señal de producción.

## Interpretar la prueba de ML

El clasificador base estima la etiqueta a cuatro horas. Se calculan medias históricas, se imputan ausentes y se ajusta un HistGradientBoostingClassifier. El umbral maximiza F2 en validación. No se calibran probabilidades ni se optimiza un coste empresarial.

Se reportan average precision, prevalencia, precisión, recall, matriz de confusión y eventos con aviso en las cuatro horas anteriores. El recuento de falsos avisos es por muestra de 15 minutos, sin agrupar episodios ni aplicar tiempo de silencio; no equivale a tickets de mantenimiento. La anticipación se calcula solo en los eventos detectados.

Quedan pendientes validación de ingeniería, pruebas con varias semillas, sensibilidad a intensidad del ruido, evaluación en equipos nuevos, comparación con umbrales físicos, intervalos de incertidumbre por evento y estudio de costes. El generador es la principal hipótesis del proyecto; el rendimiento de ML no lo valida.
