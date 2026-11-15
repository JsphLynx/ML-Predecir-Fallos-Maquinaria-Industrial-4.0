# Auditoría ACB Motor y Rodamientos v3

Fecha: 5 de noviembre de 2026. Auditoría del paquete 3.0.0; no modifica el dataset original y no entrena XGBoost ni Isolation Forest.

## Dictamen

**Apto condicionado para ensayar el método y la aplicación. No constituye un benchmark industrial validado.**

Las etiquetas y las entradas actuales superan las pruebas de consistencia y disponibilidad temporal ejecutadas. Una prueba semántica nueva identifica tres mantenimientos preventivos cuya hora reprogramada aparece conocida antes de la avería que causó el retraso. `known_at` no está en la lista actual de predictores: es un defecto del historial para reutilizarlo en la aplicación, no una fuga detectada en X.

Antes de entrenar: cerrar el contrato de evaluación por eventos, asegurar el filtrado de filas excluidas y definir dos variantes de Isolation Forest (referencia con verdad simulada y referencia basada solo en información observable). Antes del ensayo del calendario: corregir el historial de programación. Antes de afirmar robustez: ampliar escenarios sanos, variabilidad y semillas reservadas, sin ajustar el simulador para obtener mejores métricas.

## Contenido

- `Auditoria_ACB_Motor_Rodamientos_Sintetico_v3.pdf`: dictamen, cifras, hallazgos, plan de cierre, fuentes y límites.
- `scripts/auditar_v3.py`: comprobaciones independientes; produce JSON y CSV. Devuelve un informe con fallos; no es un certificado ni un entrenamiento.
- `scripts/ejecutar_auditoria.py`: ejecuta las validaciones originales sobre una copia, la auditoría independiente y, opcionalmente, la regeneración completa.
- `evidence/`: resultados, salidas y tablas de la ejecución. Los TXT de fuentes completas y las imágenes de revisión no se distribuyen.

## Reproducir

Usar el entorno del dataset original (Python 3.12, numpy 2.3.5, pandas 2.2.3, pyarrow 26.0.1). Añadir `scikit-learn` para las métricas descriptivas univariantes. `pglast` es opcional para la comprobación sintáctica SQL. Las versiones efectivas de la auditoría están en `evidence/entorno_auditoria.json`.

```bash
python scripts/ejecutar_auditoria.py --dataset /ruta/ACB_Motor_Rodamientos_Sintetico_v3 --work /ruta/nueva/auditoria
```

Añadir `--reproducir` para regenerar los ocho mundos y comparar los archivos. La carpeta `--work` debe ser nueva. No ejecuta SQL ni necesita credenciales. Para Spyder se puede llamar a `audit(Path(...), Path(...))` del módulo `auditar_v3.py`; los argumentos son la raíz descomprimida y una carpeta de resultados.

## Cómo interpretar los resultados

Las pruebas originales dan 375 + 50 éxitos. La auditoría independiente da 61 éxitos y 3 fallos del mismo problema de cronología. Total: 489 comprobaciones, 486 correctas y 3 fallidas; las comprobaciones no son ensayos estadísticos independientes. El resultado de la regeneración se entrega por separado. Ninguna cifra demuestra realismo físico ni capacidad predictiva industrial.

`oportunidades_eventos.csv` mide disponibilidad de registros con etiqueta positiva y antelación; no mide detección. La regla de disponibilidad 3 de 5 usa cinco instantes de la rejilla de 15 minutos (60 minutos entre extremos). El análisis univariante usa solamente entrenamiento; no ajusta umbrales, no es validación y no demuestra ausencia de atajos multivariantes.

La fila `excluida` del CSV original puede contener `usable_rows` por calidad/etiqueta, pero no debe entrar al entrenamiento. El CSV independiente corrige esta interpretación y le asigna cero filas utilizables. No se altera el original.
