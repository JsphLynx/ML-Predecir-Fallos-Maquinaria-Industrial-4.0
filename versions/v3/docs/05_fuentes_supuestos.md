# Fuentes, decisiones y elementos no comprobados

## Evidencia usada en esta actualización

| Fuente | Qué se ha comprobado en esta tarea | Uso |
|---|---|---|
| `ACB_CSP_Sintetico_v2.zip` | Código, configuración, diccionario, DDL, esquemas de 81 Parquet y validaciones originales ejecutadas | Identificar incompatibilidades y elementos reutilizables |
| `LEEME_ACB_CSP_v2.md` | Contenido completo | Contrastar alcance y resultados declarados con los archivos |
| `Arquitectura_Subsistema_Laminacion_ACB_v1.md` | Contenido completo | Contrato de motor/DE/NDE, objetivo, calidad, evaluación y límites |
| Instrucción de Joseph en esta tarea | Telemetría de 5 min y decisiones de 15 min; conservar v2 y crear paquete específico | Sustituye la propuesta de observación/evaluación por minuto |
| Código y ejecución v3 | Recuentos, distribución, calidad, etiquetas, particiones y hashes | Fuente de todas las cifras de la entrega nueva |

Los documentos previos conservados en `docs/referencia/` citan la ficha histórica de Sestao, la declaración ambiental 2024, el estudio de eficiencia y fuentes oficiales de contexto. **En esta actualización no se ha hecho una nueva auditoría integral de esos PDF ni una nueva búsqueda web.** Sus referencias se mantienen como procedencia de diseño, no como verificación actual del inventario, condiciones de operación o capacidades de la planta.

## Supuestos explícitos

- Una caja lógica, un motor y dos apoyos DE/NDE. No es inventario OEM verificado.
- Quince descriptores simulados. No se han adquirido señales reales ni ondas de vibración.
- Motor con corriente nominal ficticia de 1600 A; velocidad y cargas sin calibración de placa ni transmisión.
- Duración de 365 días por ejecución, ocho ejecuciones, calendario de turnos y recetas inventados.
- Vidas latentes, riesgos de fallo, ruido, degradación, reparaciones y preventivos son distribuciones de demostración.
- Límites de señal en `sensores.parquet` son controles de rango del simulador, no límites ISO/OEM ni instrucciones de seguridad.
- Horizonte de 24 h, cobertura 80 %, antigüedad 10 min, ventana máxima 4 h y margen 28 h son decisiones de proyecto.
- Los estados normal/degradación/fallo y los defectos instrumentales inyectados son verdad privada para auditoría. El umbral de daño 0.55 define una visualización/episodio, no el inicio forzado de avería.
- La referencia sana para Isolation Forest usa verdad simulada retrospectiva. En un sistema real se necesitaría otra forma de validar esos periodos.

## No comprobado o fuera de alcance

Tipo y potencia de motor, tipo de rodamiento, transmisión, ubicación real de sensores, frecuencias originales de adquisición, límites operativos, tasas reales de avería, costes, tiempo útil de aviso, disponibilidad de mantenimiento e integración OT/IT. No se infieren de este dataset. Tampoco se han ejecutado PostgreSQL/Neon, Windows/Spyder, API o dashboard en esta entrega.

No se prometen precisión, ahorro ni reducción de fallos. La validación demuestra consistencia del código/datos bajo supuestos, no eficacia en ArcelorMittal Sestao.
