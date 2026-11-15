# ACB / Sestao — Dataset sintético de mantenimiento predictivo v2.0

**Demostración de ciencia de datos. El 100% de los registros es artificial. No son datos reales ni un gemelo digital validado de ArcelorMittal Sestao.**

## Qué contiene

| Elemento | Contenido entregado |
|---|---|
| Periodo ficticio | 01/01/2024–30/06/2025, UTC: 18 meses |
| Equipos funcionales | 18, incluidas siete cajas de laminación F1–F7 |
| Telemetría | 2.835.648 filas, cada 5 minutos, 29 columnas por fila |
| Casos para ML | 733.545 decisiones en marcha, cada 15 minutos, antes de excluir censura/purga |
| Producción | 74.624 bobinas/piezas: 74.514 completas y 110 interrumpidas |
| Productos | 12 espesores objetivo de 1 a 15 mm; anchos de 1000 a 1550 mm; cuatro grados de acero |
| Averías | 210: rodamientos, reductores, lubricación, hidráulica, refrigeración y fallos eléctricos súbitos |
| Mantenimiento | 552 intervenciones: 342 preventivas y 210 correctivas |
| Objetivos | Inicio de avería del mismo equipo en las próximas 4, 8 y 24 horas |
| Formato | Parquet comprimido, scripts Python, diccionario CSV/Markdown, SQL y documentación |

En `data/` están las tablas de negocio y telemetría; en `ml/` las características y objetivos separados. `privado_no_usar_como_features/` contiene la verdad interna del simulador, excluida del modelo. Los IDs y parámetros de maquinaria son supuestos.

## Comenzar en Spyder

1. Descomprime el ZIP completo.
2. Crea el entorno con `conda env create -f environment.yml` y actívalo con `conda activate acb_ml_demo`.
3. Selecciona ese intérprete en Spyder y abre `src/00_empezar.py`. Carga la caja F3 y une características/objetivos por `(equipo_id, timestamp)`.
4. Consulta `docs/02_metodologia_y_uso.md` para regenerar, entrenar, exportar CSV o usar el esquema PostgreSQL opcional.

Los datos ya están generados: **no necesitas volver a generarlos para empezar**. Lee un equipo cada vez para reducir el consumo de memoria. La configuración permite generar a un minuto, pero esta entrega es de cinco minutos y modificarla exige nueva validación.

## Comprobaciones y prueba de ML ejecutadas

- 494 comprobaciones superadas: claves, relaciones, fechas, masa y flujo simplificados, objetivos, censura, purga y agregados causales.
- Segunda generación completa con semilla idéntica: archivos finales comparados mediante SHA-256; véase `resultados/reproducibilidad.json`.
- División temporal: 2024 entrenamiento; enero–marzo 2025 validación; abril–junio 2025 test. Purga de 24 horas en fronteras.
- Entrenamiento/evaluación principal a 8 h: 481.523 filas de train, 119.271 de validation y 120.294 de test, tras exclusiones.

| Resultado en test sintético | ML | Regla estadística |
|---|---:|---:|
| Fallos evaluables detectados | 17/34 | 2/34 |
| Episodios de alerta | 58 | 22 |
| Falsas alertas | 41 | 20 |
| Anticipación mediana en detectados | 3,58 h | 2,46 h |

Los umbrales se seleccionaron solo en validación bajo un mismo techo de avisos. **Las cargas observadas son distintas; esta tabla no demuestra superioridad a idéntica tasa de alertas ni eficacia industrial.** El modelo deja sin detectar la mitad de los eventos evaluables y genera falsas alertas. No se presentan las métricas como una garantía de funcionamiento.

## Archivos clave

- `docs/01_fuentes_y_decisiones.md`: evidencia de los tres PDF adjuntos, páginas oficiales, contexto previo y supuestos.
- `docs/diccionario_datos.csv`: 157 definiciones de columnas por tabla, tipos, unidades y uso permitido.
- `docs/02_metodologia_y_uso.md`: simulación, etiquetas, censura, evaluación y pasos de ejecución.
- `docs/03_matriz_19_fases.md`: avance y pendientes del proyecto.
- `resultados/resumen_visual.png`: vista rápida del escenario.
- `resultados/validacion.json`, `modelo_base.json`, `reproducibilidad.json`: evidencias ejecutadas.
- `src/01_generar_dataset.py`: generador; semilla y calendario en `config/escenario.json`.
- `sql/01_esquema.sql`: esquema relacional opcional; no ejecutado en PostgreSQL durante la entrega.
- `SHA256.json`: integridad de los archivos entregados.

## Límites esenciales

El simulador conserva relaciones básicas de producción, pero no reproduce física térmica, dinámica del tren, buffers ni redundancias reales. La alternancia de ambas ramas es hipotética: la declaración ambiental de 2024 indicaba inactivo el horno túnel B. Los sensores, degradación, tasas de fallo, costes y mantenimiento no están calibrados con datos de ACB. El catálogo dimensional se inspira en una ficha histórica de 2013, no en una oferta comercial actual.

La simulación de estrés facilita experimentar con eventos escasos. Aprender sus reglas no demuestra capacidad de anticipar fallos reales. Las 733.545 decisiones no son observaciones independientes. Validado técnicamente en Python 3.12/Linux; pendiente de ejecución directa en Windows/Spyder y PostgreSQL.
