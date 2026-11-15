# ACB · Motor y rodamientos · Dataset sintético v3

**Entrega 3.0.0 · 4 de noviembre de 2026 · Proyecto de Joseph**

El 100 % de los registros es artificial. No son medidas de ArcelorMittal Sestao ni un gemelo digital validado. Esta entrega prepara el subsistema antes de entrenar: **no contiene modelos entrenados, probabilidades de fallo ni métricas predictivas**.

## Qué cambia y qué se conserva

- Se conserva `ACB_CSP_Sintetico_v2` como referencia independiente para el EDA general.
- Nuevo conjunto lógico: un motor y dos apoyos DE/NDE identificados por separado. DE = lado de accionamiento; NDE = lado opuesto.
- **Telemetría cada 5 minutos y decisiones cada 15 minutos.** No se interpola a un minuto.
- Quince señales, calidad y latencias; fallos probabilísticos, degradación progresiva, reparaciones parciales y defectos de sensores.
- Etiqueta principal: fallo funcional del conjunto en las próximas **24 horas**, con censura y particiones temporales recalculadas.

## Contenido generado y comprobado

| Elemento | Resultado |
|---|---:|
| Ejecuciones independientes del mismo diseño | 8 |
| Duración por ejecución | 365 días |
| Telemetría | 840.960 filas, 27 columnas |
| Decisiones, incluidas abstenciones | 280.320 filas, 124 columnas de snapshot |
| Predictores permitidos | 110 numéricos + 3 categóricos |
| Fallos | 398: 359 progresivos y 39 súbitos |
| Mantenimiento | 502: 398 correctivos y 104 preventivos |
| Señales / activos de la jerarquía | 15 / 7 |
| Definiciones en diccionario / tablas SQL | 248 / 15 |
| Validaciones de datos y causalidad | 375 correctas, 0 fallidas |
| Validaciones de catálogo y segmentos | 50 correctas, 0 fallidas |
| Segunda generación completa | 44 archivos idénticos mediante SHA-256 |

Las ocho ejecuciones son mundos alternativos del mismo conjunto, no ocho motores reales. Calendario ficticio UTC: 01/01/2024 hasta 31/12/2024 **exclusivo**, exactamente 365 días. Se amplió la propuesta inicial de 180 días porque dejaba solo seis fallos utilizables en validación tras excluir episodios que cruzaban los cortes. No se ajustaron modelos ni se modificaron los mecanismos para mejorar métricas.

## Particiones disponibles

| Partición | Filas utilizables* | Fallos con alguna decisión positiva utilizable |
|---|---:|---:|
| Entrenamiento | 93.614 | 164 |
| Validación | 20.907 | 33 |
| Prueba temporal | 20.983 | 34 |
| Estrés reservado R07–R08 | 51.273 | 113 |

*Calidad suficiente, régimen elegible, etiqueta conocida y sin exclusión de frontera. Los recuentos de fallos describen disponibilidad para modelar; **no son fallos detectados** ni una evaluación con el plazo mínimo de aviso. El resto de filas se conserva para EDA, auditoría y abstenciones. La validación y la prueba seguirán teniendo incertidumbre por el número de eventos.

## Empezar en Spyder

1. Descomprimir el paquete completo.
2. En Miniforge, desde la carpeta del paquete: `conda env create -f environment.yml` y `conda activate acb_motor_v3`.
3. Seleccionar ese intérprete en Spyder. Instalar `spyder-kernels` compatible si el IDE lo solicita.
4. Ejecutar `src/00_empezar.py`. Los datos ya están generados; no hace falta regenerarlos.
5. Explorar `telemetria`, `dataset`, `X_train` e `y_train`. Cambiar `EJECUCION` para otra simulación.

`X_train` usa exclusivamente la lista de entradas permitidas. Nunca pasar todas las columnas de `dataset`, `targets` o `sim_truth` a un modelo.

## Archivos principales

- `docs/01_auditoria_migracion.md`: inspección real de v2, elementos reutilizados y cambios.
- `docs/migracion_29_columnas_v2_v3.csv`: correspondencia exacta de las 29 columnas originales.
- `docs/02_metodologia.md`: simulación, calidad, etiquetas y particiones.
- `docs/03_guia_spyder.md`: ejecución, regeneración, exportación y SQL.
- `docs/04_arquitectura_v3.md`: contrato vigente, sustituyendo la propuesta de un minuto.
- `docs/05_fuentes_supuestos.md`: evidencia, supuestos y límites.
- `docs/06_matriz_19_fases.md`: estado del proyecto y siguientes pasos.
- `docs/diccionario_datos.csv` y `.md`: unidades, tipos y uso de cada columna.
- `sql/01_esquema.sql`: DDL PostgreSQL nuevo; tablas operativas y verdad separadas.
- `resultados/`: validaciones, reproducibilidad, calidad, particiones y dos gráficos de control.
- `SHA256.json`: integridad de todos los archivos entregados, excepto el propio manifiesto.

## Límites de la entrega

Ejecución verificada en Python 3.12/Linux. Windows/Spyder no se ha ejecutado directamente. La sintaxis PostgreSQL está comprobada con parser; **no se ha desplegado ni cargado en PostgreSQL o Neon**. El API, el dashboard, XGBoost, Isolation Forest y su evaluación quedan para las siguientes fases.

La frecuencia de cinco minutos sirve para tendencias de estos descriptores; no reproduce señales espectrales ni transitorios rápidos. Parámetros, tasas de fallo, corriente nominal y límites de señales son supuestos sin calibración industrial. Las figuras que muestran salud o incidencias utilizan verdad del simulador, claramente separada de una futura predicción.
