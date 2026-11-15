# Protocolo congelado antes del entrenamiento

Fecha: 05/11/2026. Versión: 3.1.0. Configuración exacta: `config/protocolo_preentrenamiento.json`. Los parámetros son decisiones de demostración, no límites validados por ACB.

## 1. Definición de la tarea

Una decisión cada 15 minutos. Objetivo supervisado: primer fallo funcional del conjunto en (t, t+24 h], antes del siguiente preventivo. Si no se observa un fallo y el horizonte queda incompleto por preventivo o fin de seguimiento, la etiqueta es nula. Los fallos ya iniciados y estados no elegibles no reciben una etiqueta de normalidad. La clasificación es del conjunto; el modo del fallo es información retrospectiva para evaluar, no una etiqueta de diagnóstico disponible en servicio.

## 2. Datos y aislamiento temporal

Unir siempre por run_id, assembly_id y timestamp. Lista positiva de 110 columnas numéricas y 3 categóricas. El cargador evita las filas excluidas y exige una opción explícita para abrir test/estrés. Esa opción es una protección de procedimiento, no un control de seguridad frente a quien posee el ZIP.

Cortes temporales comunes 60/20/20 en los 12 mundos base; 28 horas de purga; exclusión de episodios latentes que cruzan fronteras y sus 24 horas previas; 4 horas de calentamiento. El uso de episodios internos es una ventaja de la simulación y debe declararse. Cuatro mundos de estrés completos usan semilla reservada.

Los 3 folds internos son expansivos y por fechas compartidas. Imputación, categorías, escalado y selección de variables se ajustan dentro de cada fold, nunca antes del corte. Folds con una sola clase se declaran no evaluables; no se sustituyen por divisiones aleatorias. Tras escoger hiperparámetros en train, reajustar solo con train; validation decide umbrales. Test y estrés no eligen parámetros. Han sido inspeccionados por calidad/estructura, no por resultados predictivos; no son datos nunca vistos por el analista.

## 3. Modelos y comparadores

Comparadores obligatorios: probabilidad constante ajustada a prevalencia de train; regla de condición basada en percentiles de temperatura/vibración de train; regresión logística con carga, velocidad, historial de servicio y arranques. Implementación preparada en `preparacion_ml.py`. La regla produce un score de condición, no una probabilidad.

XGBoost usa y24 con etiqueta conocida. Isolation Forest principal utiliza un conjunto candidato observable: train evaluable, servicio conocido, entre 4 y 24 horas operativas desde el servicio, cobertura completa de 30 minutos y calidad ok. No usa y24 ni salud para seleccionarlo; puede contener degradación y fallos futuros. La selección ideal usa la verdad del simulador y se informa aparte. Nunca incluir el selector en X. El score IF se orientará como anomalía creciente (`-score_samples`); no se evaluará como probabilidad mediante Brier salvo calibración futura explícita y validada sin contaminar test.

Las rejillas de candidatos están en JSON. Las clases y factorías se entregan sin ajustar. No se ha entrenado ningún comparador sobre el dataset.

## 4. Política de avisos

Abrir cuando el instante actual supera el umbral alto y hay 3 superaciones en las últimas 5 posiciones de 15 minutos. Cinco posiciones abarcan 60 minutos entre extremos; la ventana de observación equivale a (t-75 min,t]. No compactar huecos. Un instante no evaluable no vota y no cuenta como recuperación.

Cerrar tras cuatro posiciones consecutivas válidas con score menor que el umbral bajo, al entrar en fallo/mantenimiento o a las 24 horas de apertura. El umbral bajo no puede superar al alto. En otras abstenciones la alerta permanece abierta hasta un cierre explícito; el dashboard deberá mostrar el último dato válido y la abstención, sin representarla como normalidad. El cierre duro borra votos pendientes. No crear una nueva apertura solo por datos ausentes.

Una política sin avisos es un comparador válido con sensibilidad cero. Se implementa con una tabla de alertas vacía del mismo esquema, no asignando a NaN significado de salud.

## 5. Correspondencia con eventos

Asociar apertura con el siguiente fallo en el mismo mundo, antes del siguiente preventivo y del fin del periodo. Es útil entre 60 minutos y 24 horas antes, ambos límites incluidos. El primer aviso útil detecta el suceso; posteriores se clasifican duplicados. Un aviso a menos de 60 minutos es tardío. Si el horizonte termina por preventivo o fin antes de observar un fallo, queda censurado; en otro caso, si no ocurre fallo, es falso.

El evaluador del benchmark usa **todos los fallos del intervalo nominal**, incluidos los que no tenían calidad suficiente, datos o filas válidas del benchmark. Las exclusiones metodológicas se registran como abstención y no eliminan sucesos del denominador. Informar también el benchmark de clasificación con etiquetas conocidas, identificando que es otra población. Las alertas de cada partición comienzan sin estado heredado del periodo anterior.

**Dos evaluaciones separadas:** `construir_cohorte(..., modo="benchmark")` respeta exclusiones retrospectivas de episodios; es la comparación metodológica principal, no una política de aplicación. `modo="observable"` simula servicio con todos los instantes de calidad elegible, sin consultar la partición para decidir si emite un score. Se informa como análisis de sensibilidad separado, sin usarlo para reajustar umbrales. En la aplicación, la elegibilidad depende solo de calidad/operación observables; nunca de salud interna o episodios futuros.

Exposición: horas operativas de telemetría de 5 minutos (arranque, sin_carga, laminacion, desaceleracion), incluyendo periodos sin evaluación. No usar filas ML multiplicadas por 15 minutos. Exponer horas, cobertura y abstenciones junto a falsas alertas, para no ocultar mala cobertura tras una tasa baja.

## 6. Selección, métricas y regla de éxito

Presupuesto predefinido: máximo 1 falsa alerta por 1.000 horas operativas, con al menos 60 minutos de anticipación útil. Elegir en validation la sensibilidad mayor que cumple presupuesto; desempatar por menos falsas alertas y policy_id estable. Si ninguna política útil cumple, declararlo; no relajar el presupuesto después de ver test. La calibración de umbrales usa exclusivamente validation.

Informar sensibilidad por evento y por modo, falsas alertas/1.000 horas, anticipación p10/mediana/p90, cobertura, abstención y avisos tardíos, duplicados y censurados. En probabilidades XGBoost: PR-AUC, Brier y tabla de calibración. Mostrar siempre número de fallos y de mundos, no solo filas. Estratos de menos de 20 sucesos se consideran descriptivos, no confirmatorios; 20 tampoco garantiza potencia.

IC 95 % con 2.000 remuestreos de mundos completos. Comparar modelos y comparadores con las mismas muestras de mundos y los mismos eventos/exposición. Éxito sintético predefinido: mejora absoluta de sensibilidad >=5 puntos frente a cada comparador, límite inferior del IC pareado >0 y ambos dentro del presupuesto. Si no se cumple, el proyecto sigue siendo un ensayo metodológico válido, pero no ha demostrado valor añadido del modelo. No cambiar semillas para favorecerlo.

## 7. Puerta de entrada a la siguiente fase

Verificar manifiesto, todas las pruebas y tamaños de referencias. Congelar versión de software de XGBoost/IF y guardar semillas, lista de entradas, pliegues y configuración exacta. Guardar cada decisión de ajuste. Entrenar únicamente en la fase siguiente. Antes de evaluación final, guardar un manifiesto del modelo/preprocesador y política seleccionada. No usar explicabilidad o resultados de test para volver a ajustar sin declarar un nuevo experimento y nuevas reservas.

## 8. Límites de negocio

La evaluación cuantifica el comportamiento en escenarios sintéticos. No predice la máquina real de Sestao. Costes de inspección, eficacia de intervenir y horas evitadas no están observados: cualquier análisis de negocio será de sensibilidad con hipótesis explícitas. La suma de paradas históricas vinculadas a alertas no equivale a ahorro causal.

Fuentes metodológicas oficiales consultadas 05/11/2026: scikit-learn, Common pitfalls, https://scikit-learn.org/stable/common_pitfalls ; documentación de PostgreSQL, https://www.postgresql.org/docs/current/app-postgres.html . Las reglas de alertas y presupuestos son decisiones del demostrador, no derivaciones de estas fuentes.
