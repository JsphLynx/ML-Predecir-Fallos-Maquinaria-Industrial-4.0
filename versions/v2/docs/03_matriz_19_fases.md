# Seguimiento de las 19 fases — alcance de esta entrega

Nueva instantánea v2; no sustituye ni sobrescribe el expediente Business_Data_Project del 30/10/2026. No se declara cerrado el proyecto completo.

| Fase | Evidencia en esta entrega | Estado / pendiente |
|---|---|---|
| 1 Problema | Priorizar inspecciones ante fallos simulados | Definido para demo; necesidad industrial no validada |
| 2 Objetivos | Etiquetas 4/8/24 h; benchmark a 8 h | Definidos técnicamente; utilidad operativa pendiente |
| 3 Stakeholders | Usuario del proyecto y roles hipotéticos operación/mantenimiento | Sin participación empresarial confirmada |
| 4 Requisitos | Claves, fechas, censura, trazabilidad y separación de verdad | Verificados en pruebas incluidas |
| 5 Fuentes | Tres PDF, páginas oficiales, contexto/expediente | Documentados; sin históricos industriales |
| 6 Calidad | Validador ejecutado y JSON por prueba | Consistencia sintética verificada |
| 7 Modelo de datos | Parquet, diccionario y SQL con claves | Archivos verificados; SQL no ejecutado en servidor |
| 8 EDA | Recuentos por equipo, particiones y figuras | Exploración inicial; análisis profundo por realizar |
| 9 KPIs | Prevalencia, detección, falsas alertas, anticipación y exposición | Calculados para benchmark sintético |
| 10 Estadística | Desbalance y muestras dependientes reconocidos | Incertidumbre por evento y análisis de sensibilidad pendientes |
| 11 ML | Benchmark temporal ML/regla/sin avisos | Prueba ejecutada; no validación industrial |
| 12 Arquitectura | Scripts Python separados, Parquet; PostgreSQL opcional | Solución local lista; sin integración OT |
| 13 MVP | Generación → datos → etiquetas → modelo → episodios | Recorrido técnico; sin app ni revisión humana implementada |
| 14 Testing | Claves, intervalos, física simplificada, causalidad, censura, purga y reproducción | Evidencias en resultados; no equivale a certificación |
| 15 Seguridad | Sin credenciales ni datos personales; verdad del simulador separada | No hay conexión industrial ni control de maquinaria |
| 16 Despliegue | ZIP reproducible, entorno y guía | Ejecutado en Linux; Windows/Spyder y PostgreSQL pendientes de verificación local |
| 17 Monitorización | Registro de ejecución, hashes, métricas | No hay monitorización continua configurada |
| 18 ROI | Costes identificados como hipotéticos | No se calcula ROI ni ahorro industrial |
| 19 Documentación | Fuentes, supuestos, diccionario, guía, changelog y resultados | Incluidos; revisión experta del dominio pendiente |

La entrega cumple el nuevo objetivo de disponer de un dataset sintético usable para ML. No convierte las 19 fases en un producto industrial terminado.
