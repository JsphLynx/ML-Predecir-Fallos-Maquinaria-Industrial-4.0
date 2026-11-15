# Uso y reproducción en Spyder / consola

## Abrir los datos

Crear el entorno desde la carpeta del paquete:

```bash
conda env create -f environment.yml
conda activate acb_motor_v3
```

Seleccionar el intérprete del entorno en Spyder. Instalar la versión compatible de `spyder-kernels` si el IDE la solicita. Abrir `src/00_empezar.py`: permite inspeccionar telemetría, variables, objetivos y la matriz de entrenamiento por una ejecución. Las rutas se resuelven desde el script, sin rutas de Windows fijadas en el código.

Consola equivalente:

```bash
python src/00_empezar.py
python src/09_verificar_integridad.py
python src/04_validar_dataset.py
python src/11_validar_catalogo.py
```

El verificador de integridad se usa antes de regenerar resultados. No ejecutar `01_generar_dataset.py` sobre el paquete entregado: rechaza un destino con telemetría para preservar los datos originales.

## Regenerar en otra carpeta

```bash
python src/01_generar_dataset.py --out ../ACB_v3_nueva_generacion
python src/02_construir_variables.py --root ../ACB_v3_nueva_generacion
python src/03_etiquetas_particiones.py --root ../ACB_v3_nueva_generacion
python src/04_validar_dataset.py --root ../ACB_v3_nueva_generacion
python src/05_documentar_sql.py --root ../ACB_v3_nueva_generacion
python src/11_validar_catalogo.py --root ../ACB_v3_nueva_generacion
python src/08_resumen_eda.py --root ../ACB_v3_nueva_generacion
```

`--config` permite proporcionar otra configuración a la generación. El contrato v3 exige 5/15 minutos. Cambiar parámetros, semillas o duración produce otro escenario: volver a construir variables, etiquetas y validaciones. La carpeta nueva contiene datos y resultados; los scripts y documentos se siguen ejecutando desde este paquete.

Para una segunda generación completa con comparación automática de bytes:

```bash
python src/10_reproducibilidad.py --out ../ACB_v3_reproduccion
```

Usar un destino inexistente. Requiere espacio para otra copia de los datos. La identidad de bytes está comprobada con las versiones registradas; otras versiones de Parquet pueden producir bytes diferentes aun si los valores coinciden.

## EDA y exportaciones

`src/08_resumen_eda.py` produce perfiles por régimen y salud simulada, recuentos de calidad y figuras. Las tablas con sufijo `RESTRINGIDO` y los fondos de salud de las figuras utilizan verdad del simulador, no diagnósticos de ML.

`src/07_exportar_csv.py` exporta una ejecución a CSV comprimido para R o BI. CSV usa coma, punto decimal, UTF-8, nulos vacíos y fechas UTC. Cambiar `EJECUCION` al principio del script. La exportación no conserva todos los tipos de Parquet; los objetivos exportados siguen siendo información restringida a entrenamiento/evaluación.

Para presentar hora local sin cambiar la clave almacenada:

```python
telemetria['hora_madrid'] = telemetria['timestamp'].dt.tz_convert('Europe/Madrid')
```

## PostgreSQL opcional

`sql/01_esquema.sql` define 15 tablas en dos esquemas nuevos: `acb_motor_v3` y `acb_motor_v3_truth`. No afecta a `acb_demo` ni al esquema de la v2. Incluye PK, FK, controles de intervalos, cobertura, disponibilidad y etiquetas. Revoca acceso público al esquema de verdad y sus tablas. La asignación de roles concretos queda pendiente del despliegue.

Instalar `requirements_sql_opcional.txt` solo si se quiere analizar el DDL con pglast o cargar PostgreSQL. `src/06_cargar_postgresql.py` usa `ACB_DATABASE_URL`, definida localmente; no hay credenciales en el paquete. Trabaja en una sola transacción y rechaza esquemas v3 ya existentes. Por defecto carga tablas operativas; `--include-truth` incluye también objetivos y verdad en el esquema restringido.

La sintaxis se ha validado con pglast. **No se ha probado la creación ni la carga en un servidor PostgreSQL.** Hacer la primera prueba en una base vacía de pruebas y revisar sus permisos. Las tablas masivas en SQL son una opción para trabajo local; el diseño de aplicación mantiene Parquet como histórico principal.

## Estado de compatibilidad

Ejecutado con Python 3.12 en Linux; se incluyen las versiones exactas de numpy, pandas, pyarrow y matplotlib. No se ha ejecutado directamente en Windows/Spyder. No se instalan XGBoost ni Isolation Forest porque el entrenamiento es la fase siguiente. Cargar una ejecución cada vez reduce memoria frente a concatenar todas las señales y ventanas.
