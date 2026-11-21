# Descargas

## Dataset v4.0

Descargar **ambos ZIP** y `SHA256SUMS.txt` desde la [Release v4.0](https://github.com/JsphLynx/ML-Predecir-Fallos-Maquinaria-Industrial-4.0/releases/tag/portfolio-v4.0). Desde la raíz del clon:

```bash
python scripts/verificar_paquete.py RUTA/ACB_Motor_Rodamientos_Sintetico_v4_0_Parte_1.zip
python scripts/verificar_paquete.py RUTA/ACB_Motor_Rodamientos_Sintetico_v4_0_Parte_2.zip
```

Extraer las dos partes en la misma carpeta nueva fuera del clon. No concatenar sus bytes. Dentro de la carpeta reconstruida:

```bash
python -m pip install -r requirements_auditoria.txt
python src/09_verificar_integridad.py
python src/00_empezar.py
```

El verificador debe informar 182 archivos y cero diferencias. No es necesario regenerar ni entrenar para abrir el dataset.

[Catálogo](catalogo_archivos_versiones.csv) · [Registro de activos](../data/releases.json) · [Hashes](v4.0/SHA256SUMS.txt).

## Versiones anteriores

Los paquetes v1–v3.1 permanecen en la [Release histórica](https://github.com/JsphLynx/ML-Predecir-Fallos-Maquinaria-Industrial-4.0/releases/tag/portfolio-v3.1). Extraer cada versión en una carpeta independiente.

Los archivos automáticos “Source code (zip)” y “Source code (tar.gz)” de GitHub contienen el repositorio, no los ZIP completos del dataset.
