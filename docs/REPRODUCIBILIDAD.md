# Ejecución y reproducibilidad

## Comprobación rápida sin descargar los datasets grandes

Python 3.12, desde la raíz del repositorio:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r versions/v3.1/requirements.txt
python scripts/verificar_portfolio.py
python scripts/probar_protocolo.py
```

El primer script comprueba los hashes del contenido publicado. El segundo ejecuta los fixtures originales del evaluador en una copia temporal, preservando las evidencias históricas. No entrena modelos y no necesita los Parquet masivos. Sí necesita la pequeña tabla de productos que acompaña a la configuración.

## Datos y experimentos completos

Consulta [DESCARGAS.md](DESCARGAS.md). Para v3.1, `scripts/generar_v31.py` permite generar una copia nueva a partir de las fuentes publicadas. Cada versión mantiene su entorno y sus comandos originales. No ejecutar versiones diferentes contra la misma carpeta de datos.

La regeneración completa original de v3.1 compara 77 archivos; la igualdad histórica se documenta en [reproducibilidad.json](../versions/v3.1/resultados/reproducibilidad.json). No se ha repetido esa regeneración completa al publicar el portafolio.

## Spyder

Seleccionar el intérprete del entorno donde se instalaron las dependencias. Usar `src/00_empezar.py` desde una copia que incluya los datos generados. Si Spyder solicita `spyder-kernels`, instalar la versión compatible con el IDE. La entrega histórica se ejecutó en Linux; no se afirma haber verificado Windows en esta publicación.

## PostgreSQL

La evidencia histórica v3.1 corresponde a PostgreSQL 16.2 local. Los scripts de carga y prueba requieren una **base nueva de pruebas**. El DSN se proporciona por `ACB_DATABASE_URL`, nunca mediante credenciales guardadas en el repositorio. Revisar el [README original](../versions/v3.1/README.md) antes de ejecutar cargas o crear roles.

Neon y una aplicación desplegada siguen pendientes. La presencia de DDL no equivale a un despliegue en producción.
