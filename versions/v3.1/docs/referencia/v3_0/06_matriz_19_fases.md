# Matriz de seguimiento · mantenimiento predictivo v3

Las fases marcadas como preparadas se limitan al demostrador sintético. No se presupone aceptación por la planta.

| Fase | Estado al entregar v3 | Evidencia o pendiente |
|---|---|---|
| 1. Problema empresarial | Definido para demo | Priorizar inspección del conjunto motor/apoyos por fallo futuro a 24 h |
| 2. Objetivos | Definidos | Preparar datos causales y evaluación por evento; sin prometer eficacia |
| 3. Stakeholders | Parcial | Joseph como promotor del demostrador; responsables industriales no confirmados |
| 4. Requisitos | Contrato de datos implementado | 5/15 min, componentes, señales y calidad; revisión de requisitos reales pendiente |
| 5. Fuentes | Documentadas | Referencias v2/arquitectura y catálogo; sin telemetría real |
| 6. Calidad | Comprobada sintéticamente | 375 pruebas principales + 50 de catálogo/segmentos |
| 7. Modelo de datos | Implementado en archivos | 15 tablas SQL, PK/FK y diccionario; carga PostgreSQL pendiente |
| 8. EDA | Control inicial realizado | Perfiles por régimen/salud, ausencias, exposición y figuras; investigación detallada posterior |
| 9. KPIs | Definidos parcialmente | Exposición, cobertura, fallos y censura; KPI de alertas requiere modelos |
| 10. Estadística | Descriptiva inicial | Distribuciones y recuentos; incertidumbre por eventos/ejecuciones pendiente |
| 11. Machine Learning | Datos preparados, no entrenado | Baseline, XGBoost, Isolation Forest, explicación y evaluación pendientes |
| 12. Arquitectura | Contrato v3 actualizado | Motor/DE/NDE; 5/15 min; capas operativas y verdad separadas |
| 13. MVP | Pendiente | API, interfaz, reproducción temporal y revisiones humanas |
| 14. Testing | Dataset y scripts comprobados | Dos generaciones idénticas; integración de aplicación pendiente |
| 15. Seguridad | Diseño parcial | Lista permitida, esquemas separados y revocación pública; roles reales pendientes |
| 16. Despliegue | No realizado | No se conectó Neon ni servidor industrial |
| 17. Monitorización | Pendiente | Drift, latencia, calidad y rendimiento cuando exista servicio |
| 18. ROI | No estimable industrialmente | No hay costes ni efecto causal de mantenimiento real |
| 19. Documentación | Actualizada | Auditoría, metodología, guía, arquitectura, diccionario, SQL y evidencias |

Próximo trabajo: EDA detallado del conjunto y definición de baseline/política antes de entrenar. Mantener test y escenarios de estrés fuera de cualquier ajuste futuro.
