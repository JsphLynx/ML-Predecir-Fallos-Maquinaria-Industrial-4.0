# Protocolo v4.0.0 · congelado antes del entrenamiento

Fuente ejecutable: `config/protocolo_preentrenamiento.json`. Hereda la política de v3.1 pero se aplica a un generador y semillas nuevos; no autoriza comparaciones predictivas mezclando versiones.

- Fallo funcional de motor/apoyos en (t,t+24 h], antes del próximo preventivo y del fin observado. El fin es exclusivo. Censura nula, no cero.
- Telemetría cada 5 min, decisiones cada 15 min, ventanas causales de 30 y 240 min. Solo señales disponibles en cada decisión. Contexto de receta/estado/configuración conocido en timestamp por supuesto del simulador.
- R01–R12: 60 % temporal train, 20 % validation, 20 % test; purga previa de 28 h. R13–R16 estrés. Calentamiento y episodios latentes que cruzan cortes se excluyen conforme al código.
- La máscara de exclusión latente pertenece al benchmark offline, no es información accesible en servicio. Evaluar sensibilidad con máscara observable y conservar todos los eventos/exposición en denominadores.
- Tres folds temporales internos de train para selección futura; transformaciones ajustadas solo con train de cada fold. Umbrales seleccionados solo en validation. Sin ajuste por test/estrés.
- Aviso persistente: 3 de 5 decisiones; cierre tras 4 decisiones válidas bajas; abstenciones no son recuperación. Vigencia máxima de 24 h. Aviso útil de 1 a 24 h antes del fallo.
- Presupuesto de 1 falsa alerta por 1.000 horas operativas. Si no hay política útil que lo cumpla, informar ese resultado; no relajar presupuesto tras observar test.
- IF principal: `if_reference_observable`; ideal privilegiado: `healthy_reference_if`, solo sensibilidad. Score IF no es probabilidad de fallo24h.
- Métricas futuras: sensibilidad por evento, falsas alertas/exposición, anticipación, cobertura/abstención, duplicadas/tardías/censuradas, PR-AUC y calibración para probabilidades apropiadas.
- Resultados por mundo, régimen y configuración; la única caja de esta versión impide una comparación entre cajas reales. Intervalos por remuestreo de mundos; estratos con menos de 20 eventos, descriptivos.

El analista revisó estructura, etiquetas, fallos y calidad en todas las particiones para auditar generación. Test/estrés son reservados para selección/evaluación predictiva, pero no se describen como nunca vistos. No hay scores ni métricas predictivas calculadas. Las pruebas del evaluador usan fixtures fabricados; la prueba de imputador usa dos filas ficticias y no ajusta un modelo sobre el dataset.
