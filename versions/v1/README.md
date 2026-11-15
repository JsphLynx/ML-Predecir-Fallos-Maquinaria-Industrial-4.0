# Demostrador CSP de mantenimiento predictivo — versión 1.0

**TODOS LOS REGISTROS SON SINTÉTICOS. No son datos de ACB ni de ArcelorMittal.**
Referencia conceptual: proceso compacto de colada y laminación en caliente de Sestao. No existe colaboración empresarial ni validación de ingeniería implícita. Fecha de preparación: 29/10/2026.

## Qué se entrega

- 90 días ficticios: 01/01/2025–31/03/2025, marcas temporales UTC.
- 19 equipos equivalentes que representan subsistemas: dos accionamientos de colada, dos de horno túnel, tijera, descascarillado, siete cajas, hidráulica, lubricación, enfriamiento, mesa de salida y dos bobinadoras.
- Series cada cinco minutos; los datos de vibración son RMS agregados, **no ondas de acelerómetros**.
- Bobinas con geometría, trazabilidad y siete pasadas; perfiles ilustrativos de velocidad cada cinco segundos.
- Averías, intervenciones, defectos de sensor y objetivos de fallo futuro a 1, 4 y 24 horas.
- Generador Python, validación independiente, modelo base temporal, diccionario y documentación de supuestos.

Los recuentos efectivos están en `resultados/resumen_generacion.json`. No debe confundirse número de muestras con número de fallos independientes.

## Empezar en Spyder

1. Descomprime toda la carpeta, manteniendo `src`, `datos`, `documentacion` y `resultados`.
2. Selecciona un entorno con Python, NumPy, pandas y scikit-learn; `requirements.txt` recoge versiones probadas.
3. Los datos ya están generados. Abre `src/02_validar.py` y ejecútalo con F5.
4. Abre `src/03_modelo_base.py` y ejecútalo con F5 para reproducir la prueba de ML.
5. Para regenerar, ejecuta `src/01_generar.py`. Usa `--seed 123` desde terminal para otro escenario. No se necesita Internet una vez instaladas las dependencias.

Los scripts resuelven rutas a partir de su propio archivo, no del directorio de trabajo de Spyder. El generador sobrescribe los CSV y la configuración; vuelve a ejecutar después validación y modelo. `configuracion.json` registra el escenario; editar ese JSON no cambia el generador. Para cambiar el modelo de proceso, edita las hipótesis comentadas de `01_generar.py`.

```python
from pathlib import Path
import pandas as pd

carpeta = Path(r"C:\tu_ruta\ACB_CSP_Sintetico_v1")
sensores = pd.read_csv(carpeta / "datos/telemetria.csv.gz", parse_dates=["timestamp"])
objetivos = pd.read_csv(carpeta / "datos/objetivos_ml.csv.gz")
```

CSV: UTF-8, separador coma, decimal punto. pandas abre `.csv.gz` directamente. Los vacíos representan ausentes, no ceros. Los archivos grandes son adecuados para Python, no para abrir indiscriminadamente en Excel. La carpeta descomprimida ocupa más que el ZIP.

## Orden de lectura

Lee `documentacion/01_proceso_y_alcance.md`, `02_diseno_y_limites.md` y `diccionario.csv`. Las fuentes originales y su alcance están en `fuentes.csv`. `resultados/validacion.json` y `modelo_base.json` describen lo que realmente se comprobó.

## Modelo propuesto

Decisión: revisar un equipo que presenta riesgo de avería en las próximas cuatro horas. La salida es una puntuación de demostración, **no una orden automática de parada ni una probabilidad calibrada para una fábrica**.

La línea temporal se divide en entrenamiento, validación y test; se purgan 24 horas antes de las dos fronteras. No se utiliza partición aleatoria de ventanas. Los equipos son los mismos en periodos posteriores: el test no acredita transferencia a otra máquina o factoría.

Se admiten únicamente sensores y contexto disponibles en el instante de decisión. `verdad_simulador`, eventos futuros, reparaciones futuras, propiedades finales de bobina y objetivos quedan fuera de las variables predictoras.

El modelo base usa imputación ajustada solo con entrenamiento, estadísticas históricas desplazadas, selección del umbral en validación y una única evaluación final. Las métricas indican si funciona el ejercicio de simulación; no prueban validez industrial.

## Para ampliarlo

Prioridades: revisión por especialista de laminación; inventario real; modos de avería documentados por componente; simulación independiente de cada línea y sus buffers; instrumentación real de alta frecuencia; calibración de distribuciones y tasas con registros autorizados. Para un modelo industrial, solicitar históricos SCADA/historian y GMAO, no solo sensores sin averías fechadas.

No atribuir los resultados a ACB. Fórmula de presentación sugerida: «Demostrador de mantenimiento predictivo para una línea CSP, inspirado en la estructura pública de Sestao y construido íntegramente con datos sintéticos».
