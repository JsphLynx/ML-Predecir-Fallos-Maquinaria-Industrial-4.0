# Fuentes, hechos y decisiones — v2.0.0

Fecha de preparación: 01/11/2026. Proyecto: Prjct_ML_Predecir_Fallos_Maquinaria_Industrial.

## Evidencia examinada

| ID | Fuente y acceso | Información comprobada | Uso y límites |
|---|---|---|---|
| F01 | `arcelormittal-sestao-de-un-vistazo.pdf`, adjunto, página 1; texto íntegro extraído | Ficha V5, copyright 2013; bobina de 1–15 mm; anchura 845–1550 mm con restricciones; máximo 28 t; grados comerciales | Referencia histórica de dimensiones. Se simulan anchos 1000–1550 mm y cuatro grados, con mínimos conservadores. No representa la cartera comercial vigente ni garantiza todas las combinaciones. |
| F02 | `ArcelorMittalSestao-DeclaracionAmbiental2024.pdf`, adjunto, 35 páginas; OCR completo, contraste visual de páginas 11 y 28 | Página 11: colada continua, horno túnel, siete cajas, bobinado e instalaciones auxiliares. Página 28: horno túnel B inactivo | Base de topología. La alternancia A/B del simulador es un escenario hipotético, incompatible con interpretar las fechas ficticias como la operación observada de 2024. OCR inglés usado para extracción; no se usan cantidades ambiguas sin inspección. |
| F03 | `Estudio_Eficiencia_Aceria_Arcelor_Mittal.pdf`, adjunto, 97 páginas; texto extraído, revisión focalizada del proceso y aire comprimido | PFC de Javier Pindado Cebrián, Universidad Carlos III. Páginas PDF 39–42: descripción de laminación convencional con slabs de 220–250 mm y bobinado. El estudio se centra en eficiencia del aire comprimido | Contexto de componentes y auxiliares. No se transfieren espesores de entrada ni parámetros de compresores al CSP. No contiene un histórico etiquetado de fallos del tren. No se han validado todos sus cálculos. |
| F04 | [ArcelorMittal Europe: Sestao](https://flateurope.arcelormittal.com/ourmills/spain/sestao), página oficial consultada 01/11/2026 | Inventario publicado: dos coladas CSP, dos hornos túnel y un tren con dos bobinadoras | Confirma instalaciones, no su utilización simultánea ni inventario de sensores. |
| F05 | [ArcelorMittal España: Sestao](https://spain.arcelormittal.com/que-hacemos/productos-planos/sestao/), consulta 01/11/2026 | Producción de bobina caliente/decapada; proyectos de automatización y rodillos de horno | Contexto, sin usar cifras agregadas como calibración de telemetría o averías. |
| F06 | [Comunicado oficial, 18/05/2026](https://spain.arcelormittal.com/comunicados/sestao-impulsa-actividad-industrial-euskadi/), texto leído | Describe inversiones y automatización del laminador | Las configuraciones y capacidades cambian con el tiempo. Las capacidades de distintas publicaciones no se mezclan ni se fuerzan como producción real del dataset. |
| F07 | [SMS group: Condition monitoring for hot strip, CSP and plate mills](https://www.sms-group.com/en-pe/competences/condition-monitoring-for-flat-rolling-mills), consulta 01/11/2026 | Texto indexado del fabricante describe vibración, temperatura, par, rodamientos y servoválvulas para monitorización | Sustento conceptual de familias de señales. Texto indexado accesible; apertura directa devolvió 403. No prueba instalación de ese sistema en ACB, ni calibra nuestros rangos. |
| C01 | Expediente `Business_Data_Project_Mantenimiento_Predictivo.md`, versión leída 0.2, 30/10/2026 | Restricción confirmada: sin acceso a datos reales. Demostrador, no piloto; auditoría de claves y fuga; evaluación por eventos | Se conserva la decisión. El ZIP v1 no se sobrescribe; esta versión se genera de nuevo y no reutiliza su test conocido. |
| C02 | Contexto de conversaciones del proyecto recuperado | Propuestas anteriores de 4 h y 8/24 h; 18 meses y cadencia por minuto eran propuestas, no parámetros industriales | Se entregan los tres horizontes; 8 h es el principal. Cadencia entregada 5 minutos para trabajo local; configurable a 1 minuto. |

Los tres PDF adjuntos han podido procesarse. Solo se atribuyen hechos a las secciones especificadas. No se incorporan PDF nuevos inaccesibles como evidencia. Los originales no se redistribuyen dentro del ZIP.

## Hipótesis explícitas de simulación

| ID | Decisión reproducible | Justificación y limitación |
|---|---|---|
| S01 | 18 conjuntos de equipos, incluidas 7 cajas F1–F7 | IDs, motores, potencias, sensores y componentes equivalentes son inventados; no es inventario de activos reales. |
| S02 | Rama A/B y bobinadoras se alternan por bobina | Escenario didáctico de utilización, no cronología de planta. No se modelan buffers, transporte ni funcionamiento paralelo real. |
| S03 | Cualquier avería considerada detiene toda la isla | Regla conservadora del simulador. No explota redundancia ni transferencia a la otra rama. No permite inferir disponibilidad industrial. |
| S04 | Entrada al tren 60 mm y 7 reducciones geométricas; ancho constante | Parámetro asumido de planchón delgado. Conserva flujo volumétrico entre cajas; no es un modelo metalúrgico calibrado. |
| S05 | Calendario ficticio UTC 01/01/2024–30/06/2025; paso 5 min | Ninguna fecha corresponde a un suceso real. El paso no permite análisis espectral ni transitorios rápidos de mordida. |
| S06 | Mantenimiento cada 28 días, 8 horas; daño residual 45% | Hipótesis: preventivo imperfecto. Censura objetivos si interviene antes del horizonte, salvo fallo previo. |
| S07 | Vida latente lognormal, mediana 450 horas de esfuerzo equivalente, dispersión log 0,40; reparación mediana 3 h | Escenario de estrés deliberadamente enriquecido para disponer de averías de varios modos. No es MTBF de ACB. La exposición y los preventivos modifican la frecuencia resultante. |
| S08 | Fallos súbitos con tasa 1/18000 horas-equipo en marcha | Sin precursor añadido de forma artificial. No se promete anticiparlos. |
| S09 | Carga depende de espesor, ancho y grado; daño crece con esfuerzo; sensores con ruido correlacionado | Generación causal en el tiempo. La firma del deterioro es una regla inventada, y un modelo puede aprenderla. |
| S10 | 0,4% de ausentes aleatorios por señal; bloques perdidos, congelaciones y picos; deriva y cambio de mezcla | Diferenciar error instrumental de fallo mecánico. Presión hidráulica es estructuralmente ausente en equipos donde no se modela. |
| S11 | Decisión cada 15 min, ventana 8 h, aviso mínimo 30 min, silencio 8 h; presupuesto 2 episodios/1000 h-equipo | Política técnica hipotética para comparar modelos. No equivale a capacidad de una brigada real ni a orden de parada. |
| S12 | Costes uniformes inventados por intervención | Solo escenarios de análisis. No sumar reparación de fallos y mantenimiento correctivo: son el mismo coste, duplicado por trazabilidad. No calcular ROI real. |

## Hechos frente a incógnitas

**Hechos del entregable:** las filas, recuentos, pruebas y métricas proceden de ejecutar el código incluido. **Desconocidos:** límites reales de sensores, MTBF/MTTR, señales disponibles, configuración de componentes, política de mantenimiento, tiempos de intervención, costes y eficacia industrial. No se inventan como hechos.

Las fuentes no establecen que la planta tenga un problema de mantenimiento sin resolver. El problema empresarial del ejercicio consiste en evaluar una priorización simulada de inspecciones antes de fallos, comparando ML con reglas y ausencia de avisos.
