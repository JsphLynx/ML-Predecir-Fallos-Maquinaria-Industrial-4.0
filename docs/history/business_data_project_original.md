# Business_Data_Project — Mantenimiento predictivo industrial

Proyecto: Prjct_Ml_Predecir_Fallos_Maquinaria_Industrial  
Expediente y matriz de seguimiento: versión 0.2 · 30/10/2026 · metodología Business_Data_Project 1.0  
Referencia conceptual: ACB / ArcelorMittal Sestao. Madurez acreditada: demostrador con datos sintéticos y resultados almacenados. No acredita piloto ni implantación industrial.

## 1. Dictamen inicial

Existe trabajo reutilizable: generador, 14 tablas sintéticas, diccionario, reglas, validaciones y una prueba de ML. El siguiente paso útil es concretar la decisión de mantenimiento que se pretende mejorar. No procede empezar por elegir otro algoritmo ni por ampliar indiscriminadamente el dataset.

**Problema del demostrador:** evaluar, en escenarios sintéticos explícitos, si las señales disponibles permiten priorizar inspecciones de equipos antes de fallos simulados, comparando reglas simples y ML mediante detección por evento, falsas alertas y anticipación. La necesidad empresarial real permanece como hipótesis no validada.

No está demostrado que ACB carezca de mantenimiento predictivo, que su proceso actual sea deficiente ni que registre un nivel determinado de paradas. Esas afirmaciones requieren evidencia empresarial.

Alcance de trabajo vigente: demostrador reproducible con datos sintéticos para portafolio. Joseph confirma el 30/10/2026 que no tiene posibilidad de acceder a datos reales. No se condiciona su finalización a conseguir datos de ACB. La validación industrial está bloqueada por esa falta de acceso y queda fuera de esta entrega; solo se reconsiderará mediante un cambio de alcance con acceso autorizado. No se presupone colaboración con la empresa.

## 2. Fase 1 ejecutada: ficha del problema empresarial

| Campo | Definición inicial y grado de certeza |
|---|---|
| PROB-01 | Evaluar si una priorización anticipada de inspecciones mejora la detección de fallos simulados frente a reglas simples, a igual carga de alertas. No se compara con la política real de ACB, que se desconoce. |
| Proceso delimitado | Contexto desde colada hasta bobinado; foco predictivo inicial propuesto en accionamientos de las cajas del tren. El alcance general solicitado por Joseph permanece; el foco inicial reduce el experimento. |
| Situación actual verificable | Hay un simulador local y una prueba almacenada. No se dispone en el expediente revisado de históricos reales de planta ni de evidencia de uso industrial. |
| Proceso actual de mantenimiento | Desconocidos: monitorización existente, gestión de avisos, mantenimiento preventivo/predictivo, planificación, tiempos de respuesta y registro de averías. No asumir mantenimiento exclusivamente reactivo. |
| Usuarios afectados potenciales | Mantenimiento, operación del tren y planificación de producción. Roles propuestos, sin personas ni participación confirmadas. |
| Decisión DEC-01 | Qué equipo revisar primero, con qué prioridad y dentro de qué ventana; la intervención la decide un responsable humano. No es una orden automática de parada. |
| Quién decide | Joseph define y evalúa el escenario del demostrador. El responsable de mantenimiento es un rol simulado, sin autoridad ni actuación en planta. |
| Datos de apoyo | Señales observadas, estado operativo, producto/carga, intervenciones conocidas hasta el instante de decisión y registro de fallos posteriores para evaluación. Solo disponibles como simulación en el material revisado. |
| Síntomas a medir | Paradas no planificadas, reparación urgente, daño secundario, material afectado y carga de avisos. Son impactos posibles, no hechos observados en ACB. |
| Causas hipotéticas | Degradación detectable, cambios de régimen confundidos con avería, fallos de sensor o falta de integración entre señales e intervenciones. Requieren contraste; también puede haber fallos súbitos no anticipables. |
| Línea base empresarial | Desconocida: número y duración de averías, exposición en marcha, criticidad, costes, avisos existentes y porcentaje de intervenciones útiles. |
| Unidad de decisión | Equipo–instante de evaluación; distinguir equipo, componente y modo de fallo. En v1, equipos equivalentes, no inventario real de componentes. |
| Horizonte inicial | Cuatro horas, heredado del demostrador. Hipótesis técnica; su utilidad depende del tiempo necesario para revisar y actuar. |
| Acción demostrable | Una alerta agrupada por episodio permite abrir una revisión simulada con equipo, señales, instante y prioridad; registrar posteriormente su resultado. Flujo propuesto, aún sin implementar. |
| Alternativa de continuidad | Mantener la política actual de la empresa, cuando se conozca. En el experimento: comparar con ausencia de avisos y reglas de umbral/tendencia, sin atribuirlas a la política real. |
| Exclusiones iniciales propuestas | Control automático de maquinaria, consignas, diagnóstico físico certificado, predicción universal de cualquier fallo, RUL industrial y afirmaciones de ahorro real. |
| Cierre de la fase | Para el demostrador: identificar decisión simulada, responsable del proyecto, activos/modos de fallo, respuesta y ventana asumidas, comparadores y límites. Una validación empresarial requeriría evidencia real y queda fuera del alcance actual. |

**Estado: en curso.** Alcance sintético definido; falta concretar activos/modos de fallo y reglas de acción simulada. La ausencia de validación empresarial no impide cerrar posteriormente la fase dentro del demostrador, con sus límites explícitos.

## 3. Evidencias revisadas

E-01. Instrucción actual de Joseph: aplicar las 19 fases, mantener una matriz y distinguir hechos, supuestos y decisiones pendientes. Contexto del proyecto: mantenimiento predictivo de maquinaria, especialmente tren de laminación, con propósito de demostración y portafolio.

E-02. [ACB_CSP_Sintetico_v1.zip](https://chatgpt.com/library?file_id=libfile_a09fe1ec19108191be8b5408acafd00a&account_id=personal), versión interna 1.0, preparado el 29/10/2026. Se han leído README, configuración, documentación de alcance y límites, resultados JSON y código del modelo base. Archivo revisado sin modificar. SHA-256 del ZIP: `8ff3bb676fea2daeeebd99437f16b1cbfe5ca02d2504e3c16f3aa1827ef91eb1`.

E-03. Verificación ejecutada el 30/10/2026: los 30 archivos incluidos en SHA256.json coinciden con sus huellas; recuento directo de cinco tablas: 19 equipos, 492.480 filas de telemetría, 72 fallos, 81 intervenciones y 10.262 bobinas. La coincidencia de huellas acredita integridad respecto al manifiesto, no validez industrial.

E-04. `resultados/validacion.json` registra 23 comprobaciones satisfactorias. Este informe se ha leído; no se ha vuelto a ejecutar el validador. No confundir estos resultados previos con nuevas pruebas realizadas hoy.

E-05. `resultados/modelo_base.json` registra precisión por muestra 17,96 %, recall por muestra 28,63 %, average precision 0,1399 y 9 de 16 eventos de test con aviso previo. Son resultados almacenados, íntegramente sintéticos; no se ha reentrenado el modelo en esta revisión. El 9/16 corresponde a eventos, no al recall por muestra. No hay incertidumbre estimada ni calibración industrial.

E-06. El código revisado usa estadísticas históricas desplazadas, imputación ajustada con entrenamiento, particiones temporales, umbral seleccionado en validación y evaluación sobre los mismos equipos en tiempo posterior. Asigna etiquetas a telemetría por posición de fila: conviene sustituirlo por unión comprobada por `equipo_id + timestamp` antes de aceptar nuevos archivos. Esta revisión no sustituye una auditoría completa de fuga de información.

E-07. Las dos páginas oficiales aportadas en el contexto no han podido recuperarse en esta consulta. No se usan para dar por confirmada la configuración actual de planta:

- https://spain.arcelormittal.com/que-hacemos/productos-planos/sestao/
- https://spain.arcelormittal.com/comunicados/sestao-impulsa-actividad-industrial-euskadi/

El paquete cita la [Declaración Ambiental 2023](https://spain.arcelormittal.com/wp-content/uploads/declaracion-ambiental-2023.pdf). **Contenido del PDF no leído ni procesado en esta revisión.** Su posible utilidad, inferida del título y de la referencia del paquete, es contrastar el contexto industrial y ambiental; no aporta por sí solo etiquetas de avería. El documento interno dice haber utilizado texto indexado, lo que no equivale aquí a verificar el PDF original. Si Joseph considera que aporta contexto, puede descargarlo y adjuntarlo para su análisis.

## 4. Registro de hechos, supuestos y decisiones pendientes

### Hechos comprobados

| ID | Hecho | Evidencia y límite |
|---|---|---|
| H-01 | Existe un paquete reproducible en estructura con código, datos y documentación. | E-02/E-03; no se ha reproducido hoy todo el pipeline. |
| H-02 | Los datos están declarados íntegramente sintéticos y no calibrados a ACB. | README y configuración. Ninguna fila se considera dato real de planta. |
| H-03 | El escenario cubre 90 días ficticios y telemetría cada cinco minutos. | Configuración; no es cobertura histórica real. |
| H-04 | Hay 72 eventos de fallo y 492.480 muestras de telemetría. | Recuento directo E-03; las muestras no equivalen a fallos independientes. |
| H-05 | Hay una prueba de ML a cuatro horas con resultados almacenados y limitaciones explícitas. | E-05/E-06; no demuestra mejora económica. |
| H-06 | El simulador trata la línea como una única isla de disponibilidad y no modela buffers ni redundancias reales. | `02_diseno_y_limites.md`; limita la interpretación de paradas. |
| H-07 | No se ha aportado en el material revisado una línea base económica ni aceptación de responsables industriales. | Ausencia documental limitada a este expediente; no implica que la empresa carezca de ellas. |

E-08 / H-08. Confirmación directa de Joseph, 30/10/2026: «No tengo la posibilidad de acceder a datos reales». Restricción confirmada; no es un supuesto ni una tarea pendiente de obtención de datos.

### Supuestos reversibles

| ID | Supuesto de trabajo | Cómo contrastarlo y efecto si falla |
|---|---|---|
| S-01 | Resuelto para esta entrega: demostrador sintético, dado el propósito de portafolio y la restricción H-08. | Conservado como historial; sustituido por DEC-02. Reabrir únicamente si cambia el acceso y el alcance. |
| S-02 | Cuatro horas permiten alguna acción útil. | Obtener tiempos de revisión, preparación e intervención; cambiar horizonte si no sirve. |
| S-03 | Conviene iniciar la evaluación en accionamientos de cajas y degradación progresiva. | Priorizar por criticidad, datos y eventos; cambiar activos si el valor o los precursores son insuficientes. |
| S-04 | Una persona revisará y decidirá sobre los avisos. | Definir responsable y capacidad de atención; sin acción viable, el modelo no resuelve el problema. |
| S-05 | Python y archivos locales bastan para el próximo incremento. | Revisar si aparecen varios usuarios, persistencia compartida o integración; PostgreSQL y web no están aprobados como requisitos. |

### Decisiones pendientes

| ID | Decisión o información necesaria | Responsable propuesto | Impacto / prioridad |
|---|---|---|---|
| DP-01 | Resuelta para esta entrega: continuar como demostrador sintético; DEC-02. | Joseph, fuente de la restricción | No hay piloto industrial en el alcance vigente. |
| DP-02 | Elegir activos/componentes y modos de fallo del primer experimento. | Joseph; especialista industrial por designar | Alta; delimita población y sensores. |
| DP-03 | Definir acción tras aviso, anticipación mínima y capacidad diaria de inspección. | Responsable de mantenimiento por designar; Joseph para simulación | Alta; determina horizonte y umbral. |
| DP-04 | Resuelta: no hay posibilidad de acceso a datos reales, H-08. | Joseph | Validación industrial bloqueada; no bloquea el demostrador. |
| DP-05 | Definir exposición y costes hipotéticos para escenarios; valores reales no disponibles. | Joseph para simulación | ROI real no estimable; no se presenta como ahorro validado. |
| DP-06 | Fijar metas y límites: detección por evento, alertas por turno y anticipación útil. | Dueño del proceso por designar; Joseph para demo | Alta; sin ello no hay aceptación empresarial. |
| DP-07 | Acordar calendario, horas disponibles y presupuesto. | Joseph; patrocinador industrial si procede | Media; no se inventan fecha final ni costes. |

## 5. Matriz de seguimiento de las 19 fases

Estados permitidos: pendiente, en curso, bloqueada, completada, no aplica. El estado refleja el cierre de cada fase dentro del demostrador; las dependencias de un eventual piloto se indican expresamente. Ninguna fase se declara completa por disponer de un plan. La falta de acceso no se clasifica como no aplica.

Responsables: J = Joseph, coordinador propuesto del demostrador; M = mantenimiento/dueño del proceso por designar; D = responsable de datos por designar; T = TI/OT por designar; C = control de gestión por designar. Estas asignaciones funcionales son propuestas, no aceptación de terceros. Tras DEC-02, J asume la coordinación de todas las fases del demostrador; M, D, T y C designan perspectivas funcionales simuladas o futuras, no personas que deban incorporarse para terminar esta entrega.

| Nº | Fase | Estado | Entregable / evidencia existente | Información que falta | Criterio de cierre | Responsable | Siguiente acción |
|---:|---|---|---|---|---|---|---|
| 1 | Problema empresarial | en curso | PROB-01 y restricción H-08 | Activos/modos y acción del escenario | Decisión y comparación sintéticas delimitadas; límites visibles | J | Concretar DP-02 y DP-03 sin exigir acceso real |
| 2 | Objetivos | en curso | OBJ-01 a OBJ-03 propuestos abajo | Metas, plazo, recursos y aceptación | Indicador, base, meta, plazo y dueño por objetivo | J / M | Traducir la ventana de acción a criterios medibles |
| 3 | Stakeholders | en curso | Joseph como responsable; roles industriales simulados | Perfil de quien revisará la demo y criterios de evaluación | Responsabilidades del demostrador identificadas sin inventar participantes | J | Documentar usuario simulado y destinatario del portafolio |
| 4 | Requisitos | en curso | REQ-01 a REQ-05 y trazabilidad inicial | Política de avisos, presupuesto, calendario, integración | Requisitos prioritarios comprobables y vinculados a pruebas | J / M | Especificar episodio de alerta y recorrido de revisión |
| 5 | Fuentes de datos | en curso | ZIP sintético accesible; H-08 confirma falta de datos reales | Catálogo completo, supuestos del generador y restricciones de fuentes adicionales | Procedencia y acceso comprobados para las fuentes del demostrador | J | Catalogar las 14 tablas; datos públicos externos serían opcionales y separados |
| 6 | Calidad | en curso | Informe previo de 23 controles; huellas y cinco recuentos revisados hoy | Auditoría de etiquetas, censura, señales aplicables y coherencia temporal | Controles críticos reproducidos y límites documentados | J / D | Ejecutar auditoría centrada en uso predictivo, sin alterar el original |
| 7 | Modelo de datos | en curso | Claves, granularidad y diccionario existentes | Tiempos de disponibilidad, componentes, episodios y reglas de enlace | Uniones y disponibilidad temporal verificadas, sin doble conteo | J / D | Diseñar unión por claves y entidad de alerta; SQL solo si se justifica |
| 8 | EDA | pendiente | Resúmenes de generación y calidad, sin EDA suficiente | Distribuciones por activo, régimen, fallo y partición | Preguntas prioritarias exploradas con cobertura y sesgos | J | Analizar eventos y exposición por equipo antes de modelar |
| 9 | KPIs | en curso | Métricas sintéticas del modelo y candidatos de negocio | Definiciones de episodio/exposición, base y metas | Fórmulas, denominadores y ejemplos conciliados | J / M | Separar muestras, episodios de aviso y eventos de fallo |
| 10 | Estadística | pendiente | Descriptivos parciales | Incertidumbre, dependencia y sensibilidad al simulador | Métodos adecuados al diseño y límites de generalización explícitos | J | Evaluar incertidumbre por eventos/bloques y varias semillas |
| 11 | Machine Learning | en curso | Clasificador y resultados almacenados; revisión parcial de código | Comparación con reglas, robustez, costes y prueba nueva | Mejora útil frente a baseline en evaluación independiente del alcance | J / M | Congelar test ya visto; diseñar comparación sin reutilizarlo para elegir modelos |
| 12 | Arquitectura | en curso | Python, archivos comprimidos y dependencias declaradas | Reproducción del entorno, consumo y necesidad de persistencia | Diseño mínimo reproducible y proporcional | J / T | Mantener solución local y especificar salida de alertas |
| 13 | MVP | en curso | Recorrido técnico de generación a predicciones documentado | Flujo completo de alerta, revisión y resultado | Demostración reproducible con límites y acción visibles | J / M | Añadir revisión simulada y trazabilidad de episodios |
| 14 | Testing | en curso | Validador y resultados previos; verificación de integridad actual | Pruebas de uniones, fuga, censura, alertas y aceptación | Pruebas relevantes ejecutadas con esperado/observado y sin fallos críticos | J / M | Completar matriz requisito–prueba; aceptación industrial pendiente |
| 15 | Seguridad | pendiente | Datos declarados sintéticos; sin controles industriales verificados | Inventario de secretos/accesos, datos sensibles y riesgos si hay integración | Controles acordes al uso comprobados | J / T | Revisar contenido y configuración antes de difusión; diseñar aislamiento si hay piloto |
| 16 | Despliegue | pendiente | ZIP y guía de ejecución local | Prueba en entorno destino y mecanismo de actualización | Entrega reproducida en entorno definido; producción exige validación adicional | J / T | Verificar ejecución en Spyder/entorno acordado; no desplegar a planta |
| 17 | Monitorización | pendiente | No consta monitorización activa | Señales, frecuencia, umbrales, responsable y acción | Seguimiento probado y proporcional al alcance | J / M / T | Definir revisión manual por entrega; operación industrial pendiente |
| 18 | ROI | pendiente | H-08; costes sintéticos sin valor industrial acreditado | Esfuerzo propio y supuestos de escenarios económicos | Costes observados separados de escenarios; ROI industrial no estimable | J | Registrar esfuerzo y diseñar sensibilidad hipotética, sin pedir línea base inaccesible |
| 19 | Documentación | en curso | README, diccionario, fuentes, código y este expediente | Registro de cambios, aceptación y limitaciones del nuevo flujo | Otra persona comprende y reproduce el alcance entregado | J | Versionar esta matriz con evidencia y decisiones en cada continuación |

Balance: 13 fases en curso y 6 pendientes; 0 completadas y 0 no aplica. La validación industrial está bloqueada por la falta de acceso confirmada y fuera de la entrega vigente. Las 19 fases se mantienen aplicadas al demostrador: despliegue significa entrega reproducible; monitorización, seguimiento de ejecuciones; ROI, esfuerzo y escenarios hipotéticos con límites explícitos.

## 6. Objetivos, requisitos y pruebas iniciales

| ID | Objetivo | Indicador y línea base | Meta / plazo / responsable |
|---|---|---|---|
| OBJ-01 | Evaluar la priorización de inspecciones en un escenario sintético | Fallos simulados con aviso, anticipación y episodios de alerta frente a reglas simples | Fijar supuestos de acción y metas antes del nuevo test; plazo pendiente; J |
| OBJ-02 | Comprobar si ML aporta mejora frente a reglas simples | Detección por evento a igual carga de alertas; resultados previos no comparables aún por episodio | Superioridad útil a definir antes del nuevo test; plazo pendiente; J |
| OBJ-03 | Entregar un demostrador reproducible y honesto | Reproducción de datos→predicción→alerta→revisión simulada; flujo de revisión aún ausente | Recorrido completo verificable y origen sintético visible, propuesta; plazo pendiente; J |

| Requisito propuesto | Prioridad | Trazabilidad a datos y transformación | KPI / prueba prevista |
|---|---|---|---|
| REQ-01: utilizar solo información disponible en t | Imprescindible; OBJ-02 | Telemetría y contexto con instante de disponibilidad; agregados históricos; excluir verdad del simulador y resultados futuros | TEST-01: comprobar tiempos y excluir variables prohibidas |
| REQ-02: separar pasado y futuro con purga por horizonte | Imprescindible; OBJ-02 | Objetivos y particiones temporales; ajustar preprocesamiento solo con entrenamiento | TEST-02: comprobar fronteras y ventanas; no optimizar con test |
| REQ-03: convertir muestras en episodios atendibles | Imprescindible; OBJ-01 | Agrupar avisos por equipo y política de cierre/silencio pendiente; enlazar fallos sin doble conteo | KPI-02; TEST-03: múltiples avisos del mismo episodio no multiplican tickets |
| REQ-04: mantener origen sintético y límites en resultados | Imprescindible; OBJ-03 | Metadatos de ejecución, versión, semilla y etiquetas visibles | TEST-04: cada salida identifica simulación y no atribuye eficacia a ACB |
| REQ-05: enlazar tablas por claves verificadas | Imprescindible; OBJ-02/03 | `equipo_id + timestamp`; exigir unicidad y conciliación de filas | TEST-05: barajar orden de objetivos no cambia las asociaciones; rechazar duplicados |

Pruebas de esta tabla: **previstas, no ejecutadas**. Las verificaciones ejecutadas hoy figuran exclusivamente en E-03.

KPIs candidatos, aún sin catálogo aprobado:

- KPI-01: eventos de fallo evaluables con al menos un aviso dentro de la ventana útil / eventos de fallo evaluables. Definir anticipación mínima, cobertura suficiente y atribución al mismo equipo.
- KPI-02: episodios de falsa alerta / 100 horas-equipo observadas y elegibles. Episodios con seguimiento incompleto no se clasifican automáticamente como falsos; censura e intervención requieren tratamiento explícito.
- KPI-03: distribución de anticipación del primer aviso útil, solo en eventos detectados, acompañada de cobertura de detección. No confundir esta distribución condicionada con anticipación para todos los fallos.
- KPI-04: horas de parada no planificada / horas de producción programada, con calendario y causas definidos. Calcular aparte la versión sintética y la real si llega a existir; no atribuir reducción al modelo sin diseño de evaluación.

## 7. Dictamen de ML y evaluación propuesta

**Viable con condiciones para demostración; evidencia insuficiente para utilidad industrial.** El gran número de muestras no compensa el pequeño número de eventos ni su origen sintético. El modelo puede aprender las reglas del generador sin representar mecanismos reales.

Ficha inicial: población = equipos sintéticos en marcha; unidad = equipo–instante; objetivo = inicio de fallo del mismo equipo en (t, t+4h]; cadencia existente de decisión = 15 minutos sobre señales agregadas a cinco minutos; horizonte sujeto a validación operativa. No se pretende anticipar todos los fallos súbitos ni hacer diagnóstico vibratorio espectral con RMS agregado.

Comparadores propuestos: sin avisos, reglas de tendencia/umbral y clasificador existente. Los umbrales sintéticos no se presentarán como límites físicos de seguridad. Comparar por evento y a igual presupuesto de episodios de alerta; incluir incertidumbre y sensibilidad a semillas, ruido y régimen de producción.

El test existente ya tiene resultados conocidos. Se conserva como evidencia histórica y no se utilizará repetidamente para seleccionar cambios. Para nuevas decisiones de modelado, definir desarrollo/validación y una prueba sintética independiente reservada de antemano; cambiar la semilla prueba sensibilidad al mismo simulador, no transferencia industrial.

Condiciones para avanzar hacia piloto: confirmar señales disponibles en t, fallos fechados y clasificados, intervenciones preventivas, inventario, estados de marcha y disponibilidad de acción. La cantidad necesaria de eventos se decidirá según modos de fallo, heterogeneidad e incertidumbre; no se fija un mínimo arbitrario de filas.

## 8. Valor, riesgos y criterios de parada

Valor esperado, no demostrado: detectar oportunidades de inspección con anticipación útil y reducir consecuencias de averías. Costes a registrar desde ahora: dedicación propia, preparación de datos, revisión de dominio, integración, infraestructura, formación y operación; incluir atención de falsas alertas.

ROI = (beneficios incrementales acumulados − costes acumulados) / costes acumulados × 100, para el mismo periodo y con coste positivo. Sin base ni atribución causal no se calcula ROI industrial. Evitar sumar dos veces pérdida de producción y margen perdido por la misma parada; separar coste de reparación, coste de inspección y efectos sobre producción.

Riesgos prioritarios: simulador no representativo; pocas averías independientes; transitorios confundidos con degradación; fuga temporal; exceso de avisos; falta de acción dentro de la ventana; confusión entre fallo de sensor y de equipo; atribución indebida a ACB. Controles propuestos: límites visibles, separación temporal, uniones por claves, evaluación por episodio, comparación con reglas y revisión industrial cuando exista colaboración.

Criterios de parada o reformulación: ausencia de acción útil; datos sin etiquetas o sin precursores adecuados; ML sin mejora frente a reglas; carga de alertas incompatible con recursos; beneficio no justificable. El resultado puede ser usar reglas, acotar el problema o mantener solo la demostración.

## 9. Hitos, próximos pasos y mantenimiento de la matriz

| Hito | Estado de revisión | Condición pendiente |
|---|---|---|
| A — fases 1–4 | En curso, no superado | Problema/objetivos/alcance y decisión de mantenimiento acordados |
| B — fases 5–10 | En curso parcial, no superado | Calidad predictiva, EDA, KPIs e incertidumbre; para piloto, datos reales |
| C — fases 11–13 | En curso parcial, no superado | Comparador simple, alertas por episodio y recorrido de revisión |
| D — fases 14–16 | No superado | Pruebas críticas y ejecución en entorno destino; aceptación real si hay piloto |
| E — fases 17–19 | No superado | Seguimiento, evaluación de valor y transferencia del alcance |

Siguiente secuencia: (1) concretar DP-02/DP-03 con supuestos reversibles de activos, fallos y respuesta simulada; (2) definir criterios de aceptación del demostrador; (3) auditar etiquetas, uniones y eventos; (4) definir episodios y comparadores antes de mejorar ML. DP-01 y DP-04 quedan resueltas para esta entrega. No se vuelve a pedir acceso real como condición de avance.

Este archivo es el expediente de continuidad. En próximas revisiones se actualizará conservando identidad, fecha, evidencias y decisiones anteriores. No constituye un seguimiento automático ni un servicio de monitorización configurado.

Registro de cambios: 30/10/2026 · v0.1 · Aplicación inicial de las 19 fases; ficha PROB-01; lectura del paquete v1; comprobación de integridad y recuentos; separación de hechos, supuestos y decisiones; sin modificación de datos ni entrenamiento nuevo.


## 10. Decisión de alcance DEC-02 — actualización v0.2

Fuente: H-08 y objetivo previo de demostración/portafolio. Se continúa con un demostrador íntegramente sintético. No se afirma que sea un gemelo digital validado de ACB. Los históricos reales y la eficacia industrial no son criterios de cierre de esta versión.

Criterios de éxito propuestos: pipeline reproducible; pruebas críticas de integridad y disponibilidad temporal superadas; comparación de reglas y ML sobre prueba reservada; alertas agrupadas por episodio; explicación de errores y limitaciones; trazabilidad del origen sintético. Un resultado negativo para ML también constituye un resultado válido si la evaluación es rigurosa.

Supuestos todavía pendientes: activos iniciales, modos de fallo, horizonte útil, capacidad de inspección, metas numéricas y calendario. La restricción de datos no los convierte en hechos. Las cuatro horas se mantienen provisionalmente como parámetro del ejercicio.

Los datos públicos de otros equipos podrían aportar un experimento externo separado si se verifican su licencia, señales y objetivo. No se presupone que existan datos compatibles ni que su rendimiento sea transferible al tren de ACB. No se han buscado ni añadido nuevos datasets en esta actualización.

Impacto del cambio: desaparece la obtención de datos reales de la ruta crítica del demostrador; permanecen las tareas técnicas. No cambia el estado de cierre de las fases ni se han ejecutado entrenamientos o nuevas pruebas de datos.

Registro de cambios: 30/10/2026 · v0.2 · Restricción de acceso confirmada por Joseph; DP-01 y DP-04 resueltas para la entrega sintética; problema, objetivos, fuentes, responsabilidades y criterios de cierre ajustados; historial v0.1 conservado.
