# ACB Motor y Rodamientos · Dataset sintético v4.0.0

**100 % sintético. Sin modelos entrenados. Sin calibración ni validación industrial de Sestao.**

Nueva versión basada en `Informe_Investigacion_Sestao_SMS_Contraste_v3_1.pdf` (incluido en docs). Conserva v3.1 como experimento independiente. Cambia el contrato y el generador: no es una corrección de nombres sobre los mismos datos.

## Contenido

- 16 realizaciones independientes de una caja lógica con motor y apoyos DE/NDE; 365 días por realización.
- 1.681.920 observaciones de telemetría (5 min), 560.640 decisiones (15 min), 26 señales. No equivalen a 16 motores reales.
- Contexto geométrico, térmico y mecánico con relaciones explícitas; dos dominios virtuales de configuración.
- Telemetría observada, verdad privada del simulador, eventos, mantenimiento, segmentos, diccionario y SQL PostgreSQL.
- Generador reproducible, comprobaciones de calidad/causalidad/física y protocolo de evaluación futura. No contiene pesos de XGBoost/Isolation Forest.

## Abrir en Windows 11 / Spyder

1. Extraer todo el ZIP en una carpeta local con espacio para los datos; no ejecutar dentro del comprimido.
2. Crear un entorno Python 3.12 y ejecutar `python -m pip install -r requirements_auditoria.txt` desde esa carpeta.
3. Seleccionar ese intérprete en Spyder. Abrir `src/09_verificar_integridad.py` y ejecutarlo antes de modificar archivos.
4. Abrir `src/00_empezar.py`: lee R01 y muestra un resumen; no entrena.
5. Leer `docs/Informe_Mejora_Dataset_v4_0.pdf`, `docs/MODELO_FISICO.md`, `docs/MIGRACION_v3_1_v4_0.md` y el diccionario CSV.

El entorno ejecutado fue Linux/Python 3.12. La instalación Windows/Spyder no se ha ejecutado aquí. Las versiones de paquetes probadas están fijadas en requirements y en resultados/entorno_ejecutado.json.

## Estructura y grano

| Carpeta | Contenido | Uso |
|---|---|---|
| data/telemetria | Una fila por mundo/conjunto/5 min | Señales brutas con defectos y latencia |
| data/*.parquet | Activos, productos, sensores, configuraciones, ejecuciones, fallos, mantenimiento, planes, segmentos y catálogo | Metadatos; respetar conocimiento temporal |
| ml/features | Una fila por mundo/conjunto/15 min | Entradas y metadatos causales |
| ml/targets | y24, censura, partición y selectores | Solo evaluación/objetivo; nunca entradas |
| sim_truth | Daño, episodios, defectos, reparaciones y física limpia | Privado: auditoría, no entrenamiento como entrada |
| ejemplos_csv | Extractos de R01 y catálogos | Lectura rápida; no sustituyen el dataset |
| config | Parámetros, protocolo y congelación | Reproducibilidad |
| resultados | Informes de controles ejecutados | Sin rendimiento predictivo |

`production_segment_id` sustituye a `coil_id`: identifica un bloque contiguo, no una bobina física. `motor_speed_rpm`, `roll_speed_rpm` y `strip_speed_m_s` son magnitudes distintas. `stand_id=DEMO-C01` no identifica una caja real de ACB. La posición didáctica no establece correspondencia con F4.

## Reglas para la fase posterior

- Utilizar exclusivamente `ml/columnas_modelo.json` como lista de predictores.
- Unir features/targets por (`run_id`, `assembly_id`, `timestamp`), nunca por posición de fila.
- `y24` nulo significa desconocido/censurado/no elegible; nunca convertirlo en cero.
- Respetar `evaluation_status`, partición y purga. `excluida` no tiene filas autorizadas para entrenamiento.
- No usar verdad física limpia, daño, futuro, identificadores de eventos, fin de segmentos ni final de configuraciones como entradas.
- Isolation Forest principal: referencia observable de train; referencia ideal solo como sensibilidad declarada.
- Separar versiones del dataset. No elegir parámetros del simulador por métricas de test/estrés.
- Los rangos admisibles son reglas demo de calidad, no límites de protección del equipo.

## Repetir comprobaciones

Desde la carpeta raíz del paquete:

```bash
python src/04_validar_dataset.py
python src/11_validar_catalogo.py
python src/12_probar_protocolo.py
python src/13_validar_correcciones.py
python src/14_replay_llegada.py
python src/16_validar_fisica.py
python src/17_validar_contratos.py
```

Los informes de auditoría se vuelven a escribir. El manifiesto SHA256 corresponde a la entrega original: conservar una copia sin modificar.

Regeneración completa en un destino inexistente (requiere espacio para otra copia):

```bash
python src/10_reproducibilidad.py --out ../reproduccion_v40
```

Este comando genera datos, variables, etiquetas y catálogo y compara todos los Parquet y el contrato ML por SHA-256. Usa el código/configuración del paquete original; el destino es una salida de reproducción de datos, no una copia completa de documentación. No ejecutar el generador sobre el dataset entregado: rechaza el destino existente.

## PostgreSQL opcional

El DDL y las funciones se generan para esquemas nuevos `acb_motor_v4_0`, `acb_motor_v4_0_truth` y `acb_motor_v4_0_api`. Se comprobó la sintaxis con pglast y las relaciones en Parquet. **No se ejecutó carga ni control de permisos en un servidor PostgreSQL/Neon en esta entrega.**

Para verificar en una base de pruebas nueva: instalar `requirements_sql_opcional.txt`, definir `ACB_DATABASE_URL` sin guardar credenciales en archivos y ejecutar `src/06_cargar_postgresql.py --include-truth`; después `src/15_verificar_postgresql.py`. Sin include-truth la zona privada queda vacía. El cargador usa transacción y rechaza esquemas existentes. No ejecutarlo sobre producción. El rol de demostración creado por 15 es NOLOGIN y debe no existir previamente.

Las APIs asof exponen observaciones históricas, revisiones conocidas del plan, cierres de mantenimiento ya disponibles y configuración conocida; no conceden acceso a las tablas completas de futuro/verdad. Los archivos Parquet no implementan permisos: restringir su acceso al desplegar.

## Qué sigue pendiente

Entrenamiento y evaluación con XGBoost e Isolation Forest; pruebas externas independientes; calibración con sensores reales; ciclos de bobina físicos y dinámica de mayor frecuencia. El cambio de generador modifica también las tasas simuladas de fallo: no representa un cambio de fiabilidad de Sestao. No demuestra anticipación real, ahorro ni retorno económico.
