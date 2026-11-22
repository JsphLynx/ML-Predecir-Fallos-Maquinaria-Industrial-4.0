# Dataset v4.0 de motores y rodamientos

## Auditoría cerrada · Revisión A

El dictamen autoriza iniciar el entrenamiento sintético de motores y rodamientos. La auditoría documenta cinco hallazgos cerrados, 55 controles adicionales superados y 94/94 archivos reproducidos. La preparación y la evaluación incorporan las correcciones de la revisión A.

| Descarga | Contenido |
|---|---|
| [Parte 1 auditada](https://github.com/JsphLynx/ML-Predecir-Fallos-Maquinaria-Industrial-4.0/releases/download/portfolio-v4.0-revision-a/ACB_v4_0_Auditada_Parte_1.zip) | Primera mitad del dataset con las correcciones aplicadas |
| [Parte 2 compatible](https://github.com/JsphLynx/ML-Predecir-Fallos-Maquinaria-Industrial-4.0/releases/download/portfolio-v4.0/ACB_Motor_Rodamientos_Sintetico_v4_0_Parte_2.zip) | Segunda mitad del dataset, idéntica a la original |
| [Informe PDF](https://github.com/JsphLynx/ML-Predecir-Fallos-Maquinaria-Industrial-4.0/releases/download/portfolio-v4.0-revision-a/Auditoria_ACB_v4_0.pdf) | Dictamen, hallazgos y criterios de aceptación |
| [Protocolo, código corregido y evidencias](https://github.com/JsphLynx/ML-Predecir-Fallos-Maquinaria-Industrial-4.0/releases/download/portfolio-v4.0-revision-a/Correcciones_y_protocolo_ACB_v4_0.zip) | Adenda, instalador alternativo y resultados reproducibles |
| [SHA256SUMS.txt](https://github.com/JsphLynx/ML-Predecir-Fallos-Maquinaria-Industrial-4.0/releases/download/portfolio-v4.0-revision-a/SHA256SUMS.txt) | Huellas de las cuatro descargas |

Extraer las dos partes en la misma carpeta nueva. Dentro de `ACB_Motor_Rodamientos_Sintetico_v4_0`, ejecutar:

```bash
python src/09_verificar_integridad.py
```

El resultado esperado es **184 archivos verificados y cero diferencias**. El propio manifiesto `SHA256.json` es el archivo 185 de la carpeta del dataset. Seguir las instrucciones de `docs/PROTOCOLO_AUDITADO.md` para la siguiente fase.

La auditoría se ejecutó en Linux con Python 3.12.14. Windows/Spyder y PostgreSQL/Neon siguen pendientes de verificación. El entrenamiento y la evaluación de XGBoost e Isolation Forest corresponden a la fase siguiente.

El PDF distribuido por separado y el incluido en el ZIP tienen el mismo texto extraído y distintas huellas binarias. La huella del informe en `SHA256SUMS.txt` corresponde a la descarga independiente.

[Leer el protocolo](PROTOCOLO_AUDITADO.md) · [Consultar los cinco hallazgos](matriz_hallazgos.csv).
