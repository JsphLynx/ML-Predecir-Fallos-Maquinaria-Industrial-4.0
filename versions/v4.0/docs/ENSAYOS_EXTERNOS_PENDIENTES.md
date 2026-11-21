# Contraste externo: mantener tres experimentos separados

Base: informe de investigación adjunto, páginas 7–9 y referencias. En v4 se implementa estructura motivada por esas fuentes; no se ha calibrado ni validado el generador contra una planta real.

1. Nucor Decatur: contrastar distribución de espesor/ancho/fuerza/temperatura por caja y grado, conservando procedencia y claves repetidas. La relación exacta de esa instalación con SMS CSP no quedó acreditada. No contiene el objetivo fallo24h de motor/apoyos. No comparar temperatura de banda con devanado.
2. TCM: benchmark sintético de laminación en frío para probar detección de anomalías como tarea independiente. No transferir sus etiquetas al fallo funcional24h de laminación en caliente.
3. Paderborn/IMS: ensayos de rodamientos para otras modalidades y ventanas; resolver condiciones de operación, sensores, licencias y unidades antes de comparar. No transformar cinco minutos de descriptores en una onda original inexistente.

Prerregistrar por fuente: pregunta, unidad de análisis, claves, split por activo/ensayo, frecuencia, normalización solo en train, métricas, licencia y límites. Mantener namespace/versiones distintas. Ninguna coincidencia de rangos prueba equivalencia de activos o capacidad de predicción en Sestao. No se incluyen archivos externos ni se ejecutan estos experimentos en esta fase.
