# Datos completos y distribución

El repositorio ofrece código, configuración, diccionarios, SQL, informes, evidencias, vídeos y sus fuentes editables. Los cuatro paquetes completos originales ocupan aproximadamente 1,28 GB y se mantienen separados del historial de código.

**Estado de esta publicación:** los ZIP completos están preparados y verificados; su carga como activos de GitHub Releases está pendiente. No se presentan enlaces privados o temporales como descargas públicas. El estado y los SHA-256 se registran en [data/releases.json](../data/releases.json).

| Versión | Paquete original | Tamaño aproximado |
|---|---|---:|
| v1 | `ACB_CSP_Sintetico_v1.zip` | 29,45 MB |
| v2 | `ACB_CSP_Sintetico_v2.zip` | 449,73 MB |
| v3 | `ACB_Motor_Rodamientos_Sintetico_v3.zip` | 268,40 MB |
| v3.1 | `ACB_Motor_Rodamientos_Sintetico_v3_1.zip` | 532,00 MB |

Los tamaños usan MB decimales. El [catálogo](catalogo_archivos_versiones.csv) identifica todos los archivos originales, sus tamaños, hashes y ubicación: `git` o `original_package`.

## Trabajar con una copia completa

Si ya dispones de los ZIP originales, comprueba primero su SHA-256 con `python scripts/verificar_paquete.py RUTA_AL_ZIP`. Descomprime cada versión por separado. Después ejecuta su verificador de integridad antes de modificar los archivos.

Los README históricos indican «datos ya generados» porque describen el ZIP completo. La selección de Git no incluye esos grandes Parquet/CSV; cada carpeta contiene `ARCHIVE_NOTE.md` para evitar confusiones.

## Generar v3.1 desde el código publicado

Desde la raíz del repositorio y con las dependencias de `versions/v3.1/requirements.txt` instaladas:

```bash
python scripts/generar_v31.py --out trabajo/v3_1
```

Se exige un destino nuevo. El proceso genera datos, variables, etiquetas y documentación en esa carpeta, conservando intactas las versiones originales. Puede requerir varios minutos y espacio adicional. No ejecuta entrenamiento ni despliega PostgreSQL.

La igualdad binaria con el paquete histórico depende de conservar entorno, dependencias y configuración; consulta las [instrucciones de reproducción](REPRODUCIBILIDAD.md).
