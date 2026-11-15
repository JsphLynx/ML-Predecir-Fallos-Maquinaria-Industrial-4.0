# ACB Motor y Rodamientos - Sintético v3.1.0

Entrega revisada a partir de la auditoría de v3.0.0. **Datos 100 % sintéticos; sin modelos entrenados.** Conserva la v3 original como referencia externa. No representa el inventario ni la fiabilidad real de ArcelorMittal Sestao.

## Qué contiene

- 16 mundos alternativos de un conjunto lógico motor/apoyos DE y NDE durante 365 días. No equivalen a 16 motores reales.
- Telemetría cada 5 minutos y decisiones cada 15 minutos. Objetivo: fallo funcional en las siguientes 24 horas.
- R01-R06: degradación enriquecida; R07-R12: vida más larga. R13-R16: escenarios de estrés reservados para evaluación final.
- Generador, datos Parquet, variables, objetivos, diccionario, SQL, validaciones, evaluador de alertas y protocolo congelado.
- Lecturas PostgreSQL por instante de conocimiento, sin exponer resultados de mantenimiento futuros ni verdad interna al rol lector.

## Empezar en Windows / Spyder

1. Extraer **todo** el ZIP a una carpeta local (no ejecutar dentro del ZIP).
2. Crear un entorno Python 3.12 e instalar `pip install -r requirements.txt`. Usar el intérprete de ese entorno en Spyder.
3. Abrir y ejecutar `src/09_verificar_integridad.py` antes de cambiar archivos.
4. Ejecutar `src/00_empezar.py`: lectura y exploración de R01, sin entrenamiento.
5. Consultar `docs/PROTOCOLO_PREENTRENAMIENTO.md`, `docs/CIERRE_AUDITORIA.md` y `docs/diccionario_datos.csv`.

Se ha ejecutado en Linux/Python 3.12 y PostgreSQL local. La instalación Windows/Spyder y Neon requiere verificación en ese destino; no se presenta como ya probada.

## Contratos que no deben romperse

- `ml/features` contiene entradas y metadatos causales; usar **solo** la lista de `ml/columnas_modelo.json`.
- `ml/targets` y `sim_truth` son retrospectivos. Salud, daño, evento futuro, etiquetas y selectores nunca son predictores.
- `y24 = nulo` significa objetivo no observable/censurado/no elegible. No convertirlo en cero.
- `partition = excluida` tiene cero filas utilizables; `quality_label_rows` es otro conteo, no autorización de entrenamiento.
- Isolation Forest principal usa `if_reference_observable` de train. La referencia `healthy_reference_if` es ideal y privilegiada, solo análisis de sensibilidad. Ninguna garantiza ausencia de fallo futuro.
- `data/mantenimiento` conserva resultados reales del simulador; no usar sus filas completas en una aplicación retrospectiva. Consultar las funciones `*_asof`.
- Las funciones de preparación devuelven objetos sin ajustar. Imputación, escalado y codificación se ajustan exclusivamente dentro de cada train/fold.

## Repetir las comprobaciones

Desde la carpeta del paquete:

```bash
python src/04_validar_dataset.py
python src/11_validar_catalogo.py
python src/12_probar_protocolo.py
python src/13_validar_correcciones.py
python src/14_replay_llegada.py
```

Regeneración completa en una carpeta nueva (requiere tiempo y espacio):

```bash
python src/10_reproducibilidad.py --out ../reproduccion_v31_nueva
```

No ejecutar `01_generar_dataset.py` encima de la entrega. El generador rechaza un destino con telemetría existente. La segunda generación compara todos los Parquet y el contrato de predictores por SHA-256. El manifiesto de la entrega inicial deja de coincidir si se modifican datos o informes: conservar el original.

## PostgreSQL opcional

Instalar `requirements_sql_opcional.txt`. Usar una **base de pruebas nueva** y definir `ACB_DATABASE_URL` localmente, sin guardar contraseñas en scripts. Ejecutar `src/06_cargar_postgresql.py --include-truth` para reproducir todas las pruebas; sin esa opción las tablas privadas quedan vacías. La carga y la API se crean en una transacción; rechaza esquemas existentes. No toca los esquemas v2/v3.

`src/15_verificar_postgresql.py` comprueba carga completa y restricciones; crea el rol NOLOGIN `acb_v31_demo_reader`, que debe no existir previamente. El rol solo consulta las funciones de `acb_motor_v3_1_api`. Ejecutar con una cuenta de pruebas que pueda crear roles. No usar el propietario ni un superusuario como cuenta del dashboard.

## Próxima fase

Entrenar los comparadores y XGBoost; ensayar Isolation Forest observable e ideal por separado; elegir hiperparámetros en folds internos de train y umbrales en validation; congelar decisiones; evaluar test/estrés una vez. No hay métricas de rendimiento predictivo en esta entrega.

La ampliación reduce simplificaciones, pero no calibra la máquina real. No permite afirmar ahorro, capacidad predictiva industrial ni fiabilidad de ACB. Los descriptores de 5 minutos no son ondas de vibración de alta frecuencia.
