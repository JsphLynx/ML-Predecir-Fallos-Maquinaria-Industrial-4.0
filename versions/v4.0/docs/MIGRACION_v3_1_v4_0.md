# Migración v3.1 → v4.0

Cambio mayor por ruptura de contrato y mecanismo generador. Conservar ambos ZIP; no sustituir filas de v3.1 ni concatenar versiones para evaluar resultados.

| Hallazgo del informe | Implementación v4 | Estado |
|---|---|---|
| P0 bobina confundida con bloque | `coil_id` desaparece; `production_segment_id` contiguo, cubre todos los estados | Aplicado |
| P0 procedencia de parámetros | CSV parámetro, valor, unidad, fuente, fecha y estado; OEM/modelo real nulos | Aplicado |
| P1 contexto por caja | `stand_id`, entrada/salida, temperatura y velocidad de banda; una caja lógica | Aplicado con alcance limitado |
| P1 carga/par/potencia/corriente | Modelo mínimo cuasiestático y verdad física separada | Aplicado, sin calibración |
| P1 configuración versionada | Dos dominios de accionamiento/control/sensores; política e intervenciones diferenciadas | Aplicado |
| P1 contrato vibratorio | Descriptor/eje/montaje/ventana/frecuencia/banda explícitos; desconocidos no inventados | Aplicado |
| P2 campañas/transitorios | Bloques de receta heredados y trazabilidad; sin nueva resolución subyacente | Parcial: dinámica rápida pendiente |
| P2 ensayos externos | Protocolos de uso separados; sin reetiquetar datos externos | Documentado; ensayos pendientes |

`speed_rpm` pasa a `motor_speed_rpm`; se añade `roll_speed_rpm`. 15 señales anteriores pasan a 26 señales. No comparar la corriente previa basada en nominal 1.600 A con la nueva como si fueran calibraciones sucesivas del mismo motor. Ahora la corriente se deriva de potencia, eficiencia, tensión y factor de potencia supuestos.

Las 16 realizaciones se regeneran con semillas nuevas, manteniendo 365 días, 5 min de telemetría, 15 min de decisión, 24 h de objetivo, ventanas 30/240 min y purga 28 h. Etiquetas y particiones se recalculan: no copiar las de v3.1. El protocolo se versiona antes de entrenar. Las pruebas comprueban causalidad, disponibilidad, censura, catálogo, física y reproducción, no capacidad predictiva ni rentabilidad.
