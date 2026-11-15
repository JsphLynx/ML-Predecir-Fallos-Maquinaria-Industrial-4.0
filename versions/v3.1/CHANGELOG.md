# Cambios 3.1.0 respecto a 3.0.0

1. Corrección de contrato: historial versionado de planes; conocimiento separado de ejecución y resultados; funciones asof.
2. Corrección de selección: cero usable_rows en excluida, quality_label_rows separado, cargador con lista permitida y unión por clave.
3. Ampliación del simulador: 16 mundos, vidas más largas, restauración variable, calendarios irregulares, calibraciones, defectos de cantidad/duración variable, picos dentro/fuera de rango y pérdidas correlacionadas. Nuevas semillas y configuración fijadas antes de generar; no se modifican para mejorar métricas.
4. Referencias IF observable e ideal separadas; selectores fuera de predictores.
5. Protocolo ejecutable: avisos 3/5, huecos, cierres, correspondencia única con eventos, censura, exposición, métricas y comparación pareada; comparadores sin ajustar.
6. Nuevas pruebas de correcciones, replay y PostgreSQL. Nuevos diccionario, SQL, evidencias y manifiesto.

Se conservan la cadencia 5/15 minutos, la etiqueta 24 horas y el alcance motor/apoyos. Cambian los valores, eventos y particiones: no combinar filas de v3.0 y v3.1. Las métricas de versiones distintas no son directamente comparables sin controlar los escenarios.

Defecto adicional detectado durante validación: una sustitución en escenarios con poco daño podía reiniciar el daño a un valor superior al anterior. Se limita el reinicio al mínimo entre daño previo y nuevo valor aleatorio. Se conserva la extracción aleatoria y la configuración; se recalculan los mundos afectados y se compara después con una regeneración completa. No se ajustan tasas ni semillas según métricas de modelos.
