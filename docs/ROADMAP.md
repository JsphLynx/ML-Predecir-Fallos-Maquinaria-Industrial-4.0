# Próximas versiones

## Publicación completada · 19/11/2026

- [x] Publicar código, informes, evidencias y vídeos de la evolución v1–v3.1.
- [x] Publicar los cuatro paquetes completos y sus checksums en GitHub Releases.
- [x] Verificar integridad, pruebas del protocolo y enlaces del portafolio.

## Fases posteriores

El entrenamiento y la evaluación sintética se realizarán en otra fase, por decisión del autor.

Las siguientes tareas son pendientes, no funcionalidades entregadas. La numeración de nuevas versiones se decidirá al cerrar su alcance.

- [ ] Ejecutar comparadores, XGBoost e Isolation Forest observable bajo el protocolo v3.1.
- [ ] Ajustar preprocesamiento dentro de cada fold de entrenamiento; conservar hiperparámetros, semillas y artefactos.
- [ ] Elegir umbrales en validación bajo el presupuesto de falsas alertas y congelar decisiones.
- [ ] Evaluar test y estrés con sensibilidad por evento, anticipación, carga de falsas alertas, cobertura e incertidumbre por mundos.
- [ ] Separar IF observable e ideal; no presentar el score de anomalía como probabilidad de fallo.
- [ ] Analizar atajos del simulador, explicabilidad y sensibilidad a escenarios alternativos.
- [ ] Construir API y dashboard de demostración con abstenciones y trazabilidad.
- [ ] Verificar instalación Windows/Spyder y, si se utiliza, despliegue Neon.
- [ ] Obtener revisión de dominio y datos reales autorizados antes de formular conclusiones industriales.

## Cómo incorporar una versión

1. Crear `versions/vX.Y/` conservando las versiones anteriores y sus evidencias.
2. Documentar problema, cambios, fuentes, supuestos, limitaciones y criterios de aceptación.
3. Registrar entorno, semillas, configuración, manifiesto SHA-256 y resultados ejecutados.
4. Mantener los datos completos como activos de una Release, con tamaño y checksum en `data/releases.json`.
5. Actualizar `README.md`, `CHANGELOG.md`, `docs/EVOLUCION.md` y el catálogo de archivos.
6. Ejecutar comprobaciones y diferenciar evidencias históricas de nuevas verificaciones.
7. Publicar una Release solo cuando sus enlaces y archivos estén verificados.

La documentación es acumulativa. No se sobrescriben resultados antiguos para que parezcan corresponder al último dataset.
