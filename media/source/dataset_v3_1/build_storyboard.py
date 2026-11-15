from pathlib import Path
import json
R=Path(__file__).resolve().parent
rows=[
(10,'INDUSTRIA 4.0','Del dato al mantenimiento\nanticipado.','Un proyecto sintético para aprender a aplicar machine learning en maquinaria industrial.','README y alcance','opening'),
(12,'EL PROBLEMA INDUSTRIAL','Una parada no planificada interrumpe el flujo.','Objetivo del proyecto: anticipar fallos y priorizar el mantenimiento. El ahorro real aún no está demostrado.','Contexto del proyecto · esquema conceptual','mill'),
(12,'EVOLUCIÓN DEL PROYECTO','Acotar. Adaptar. Auditar.','La v2 permanece como referencia; la v3 centra el trabajo en motor y apoyos; la v3.1 incorpora la revisión.','CHANGELOG y referencias','versions'),
(10,'EL PAQUETE COMPLETO','Mucho más que una tabla.','Datos, código, contratos y evidencias permiten seguir el recorrido de cada decisión del proyecto.','Estructura del ZIP','package'),
(14,'GENERADOR REPRODUCIBLE','Simular una historia, no sortear una etiqueta.','Configuración y semillas fijadas; degradación, fallos y reparaciones con incertidumbre. Parámetros no calibrados a ACB.','Generador y configuración','generator'),
(14,'SEÑALES Y COMPONENTES','Motor y apoyos se observan por separado.','Series extraídas de R01. Son descriptores sintéticos de 5 minutos, no ondas de vibración de alta frecuencia.','Telemetría R01','signals'),
(14,'CALIDAD Y DISPONIBILIDAD','Medir no significa poder evaluar.','Se controlan ausencias, retrasos, valores fuera de rango y sensores congelados. Mala calidad puede producir abstención.','Constructor de variables','quality'),
(12,'CORRECCIONES DE LA AUDITORÍA','Corregir antes de entrenar.','Se recalculan los datos afectados sin cambiar semillas para buscar mejores resultados predictivos.','Cambios y pruebas de regresión','fixes'),
(14,'VARIABLES Y DICCIONARIO','Cada columna tiene un significado y un uso.','Las estadísticas usan solo observaciones disponibles en la decisión. Salud interna y fallo futuro quedan fuera de las entradas.','Diccionario y contrato ML','dictionary'),
(12,'POSTGRESQL Y TRAZABILIDAD','Relacionar los datos. Separar los permisos.','Claves, transacciones y consultas por instante de conocimiento. El lector no recibe objetivos ni verdad privada.','SQL y prueba local PostgreSQL','sql'),
(12,'OBJETIVO A 24 HORAS','Desconocido no significa «sin fallo».','El siguiente preventivo y el fin del seguimiento pueden dejar el horizonte incompleto. Esas etiquetas se conservan nulas.','Etiquetas y censura','labels'),
(12,'PARTICIONES TEMPORALES','Aprender del pasado. Evaluar después.','Cortes por fechas comunes, purga de 28 h, calentamiento de 4 h y exclusión de episodios que cruzan fronteras.','Particiones y preparación ML','splits'),
(12,'VARIEDAD DE ESCENARIOS','El ensayo necesita situaciones diferentes.','Vida larga, carga y ruido variables. La proporción de salud es verdad simulada para auditoría, nunca un predictor.','Escenarios y salud','scenarios'),
(14,'VALIDACIÓN Y REPRODUCIBILIDAD','Evidencias incluidas en la entrega.','Pruebas técnicas de coherencia y causalidad. No son ensayos estadísticos independientes ni validación industrial.','Resultados de validación','proof'),
(12,'INCERTIDUMBRE DEL ENSAYO','Muchos registros no son muchas máquinas.','Los 16 mundos son simulaciones alternativas. La incertidumbre debe acompañar los resultados y no puede eliminarse contando más filas.','Eventos y protocolo','uncertainty'),
(14,'XGBOOST · SIGUIENTE FASE','Aprender a estimar el riesgo de fallo.','XGBoost utilizará variables observables y etiquetas conocidas de entrenamiento. El modelo todavía no está entrenado.','Protocolo preentrenamiento','xgboost'),
(14,'ISOLATION FOREST · SIGUIENTE FASE','Detectar lo que se sale del patrón.','Una puntuación de anomalía no equivale a una probabilidad de fallo en 24 horas. El modelo todavía no está entrenado.','Referencias IF y protocolo','isolation'),
(13,'EXPERIMENTO SIN ATAJOS','Un modelo complejo debe justificar su uso.','Ajustes con entrenamiento; umbrales con validación. Test y estrés evalúan después de congelar las decisiones.','Comparadores y protocolo','benchmark'),
(12,'DE LA PUNTUACIÓN AL AVISO','Evaluar eventos, no solo acertar filas.','Sensibilidad por fallo, falsas alertas, anticipación, cobertura y abstención. Los huecos permanecen en el reloj.','Evaluador de alertas','policy'),
(10,'APLICACIÓN FUTURA','Del aviso a una decisión de mantenimiento.','Flujo conceptual de una futura aplicación. La inspección y la intervención deben quedar a cargo de profesionales.','Objetivo del proyecto · propuesta','action'),
(10,'LÍMITES QUE SIGUEN VIGENTES','Demostración sintética, no promesa industrial.','Sin datos reales no se acredita capacidad predictiva, ahorro ni fiabilidad sobre la maquinaria de ACB.','Aviso de uso y cierre','boundaries'),
(12,'PUERTA DE ENTRADA AL ENTRENAMIENTO','Iniciar con una versión congelada.','Antes de entrenar: repetir verificaciones y registrar entorno, semillas, variables y decisiones. Guardar modelo, preparación y política antes del test.','Protocolo, sección 7','preflight'),
(9,'CONOCIMIENTO · DESARROLLO · IMPACTO','Preparado para aprender.\nPreparado para comprobar.','Próxima fase: entrenar, comparar y evaluar XGBoost e Isolation Forest bajo el protocolo definido.','Proyecto de Joseph · dataset v3.1','closing')]
s=[dict(duration=d,chapter=f'{i+1:02d} / {ch}',title=t,caption=cap,source=src,kind=k) for i,(d,ch,t,cap,src,k) in enumerate(rows)]
(R/'storyboard.json').write_text(json.dumps(s,ensure_ascii=False,indent=2))
print(sum(a['duration'] for a in s),'seconds',len(s),'scenes')
