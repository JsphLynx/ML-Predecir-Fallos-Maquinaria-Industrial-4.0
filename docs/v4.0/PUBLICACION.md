# Publicación íntegra v4.0 · Estado y cierre pendiente

**Estado: borrador documental.** El dataset original está terminado, pero aún no están incorporados a GitHub sus fuentes, PDF, evidencias y descargas completas. No presentar esta rama como publicación cerrada.

## Paquetes originales

| Archivo | Tamaño documentado |
|---|---:|
| ACB_Motor_Rodamientos_Sintetico_v4_0_Parte_1.zip | 441.246.147 bytes |
| ACB_Motor_Rodamientos_Sintetico_v4_0_Parte_2.zip | 437.652.006 bytes |

Son dos ZIP independientes que se extraen en la misma carpeta. La primera parte contiene documentación, fuentes, tablas comunes y R01–R08; la segunda añade R09–R16. No se concatenan sus bytes. Los dos reconstruyen una carpeta de 183 archivos, de los que 182 están protegidos por SHA256.json.

Los tamaños se verificaron mediante metadatos de los archivos conservados. Los hashes ZIP y su nueva comprobación quedan pendientes; no se inventan ni se reutiliza el hash del ZIP único.

## Material a incorporar

| Material | Destino previsto | Estado |
|---|---|---|
| Generador, módulos y comprobaciones | versions/v4.0/src/ | Pendiente de importar originales |
| Configuración, semillas y protocolo | versions/v4.0/config/ | Pendiente |
| Diccionario, procedencia y migración | versions/v4.0/docs/ | Pendiente |
| SQL y contratos de carga | versions/v4.0/sql/ | Pendiente |
| Informes JSON/CSV de controles | versions/v4.0/resultados/ | Pendiente |
| Ejemplos CSV y figuras | versions/v4.0/ejemplos_csv/ y resultados/ | Pendiente |
| Informe_Mejora_Dataset_v4_0.pdf | docs/reports/ | Pendiente de incorporar PDF original |
| Informe_Investigacion_Sestao_SMS_Contraste_v3_1.pdf | docs/reports/ | Pendiente |
| Informe_Sestao_SMS_Dataset_Sintetico.pdf | docs/reports/ | Pendiente; conservar como antecedente |
| Auditoria_Aportes_Dataset_v4_0.pdf | audits/v4.0/ | Pendiente; síntesis disponible |
| Info_Predecir_Fallos_Anticipar_Mantenimiento_Maquinaria.pdf | docs/references/ | Pendiente de recuperar; propuesta criticada por auditoría |
| Datos grandes de ambos ZIP | GitHub Releases, etiqueta por confirmar | Pendiente de subir y verificar |

No hay vídeos nuevos de v4.0 identificados en esta entrega. Los vídeos existentes v3.1 conservan su versión y no deben rebautizarse.

## Procedimiento de cierre

1. Recuperar ambos ZIP originales y PDFs. Mantener v1–v3.1 intactos.
2. Verificar los 182 hashes internos; comprobar que los dos ZIP no duplican rutas incompatibles.
3. Importar código, documentación, ejemplos y evidencias byte a byte. Conservar el manifiesto original completo y documentar la separación entre Git y los datos de Release.
4. No regenerar datos ni entrenar modelos para esta publicación.
5. Adjuntar ambos ZIP y SHA256SUMS.txt a una Release de v4.0. No añadir 879 MB de datos al historial normal de Git.
6. Verificar archivos recibidos, tamaños y hashes. Solo entonces registrar URLs públicas en data/releases.json.
7. Actualizar portada, evolución, roadmap, catálogo por archivo, documentación inglesa y manifiesto del portafolio.
8. Ejecutar comprobaciones de publicación. Distinguir resultados históricos del dataset de pruebas nuevas de la importación.
9. Cerrar el borrador y presentar v4.0 como versión vigente.

Los enlaces privados del autor no sustituyen a una descarga pública para reclutadores. No se han insertado URLs temporales o enlaces de descarga que todavía no existen.

## Bloqueo observado el 21/11/2026

El entorno de ejecución de archivos no estaba disponible. La conexión GitHub permitió leer y preparar documentación, pero no extraer los ZIP ni ejecutar verificaciones locales. Los instrumentos GitHub disponibles tampoco proporcionaban una operación para adjuntar archivos de Release. La preparación editorial puede revisarse sin confundirla con la importación binaria pendiente.
