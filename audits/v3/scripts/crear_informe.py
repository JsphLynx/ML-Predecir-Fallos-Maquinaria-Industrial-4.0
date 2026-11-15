"""Construye el informe PDF a partir de las evidencias verificadas."""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

R=Path(__file__).resolve().parents[1];E=R/'evidence';T=R/'render';T.mkdir(exist_ok=True)
fn='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
pdfmetrics.registerFont(TTFont('D',fn));pdfmetrics.registerFont(TTFont('DB',fn.replace('.ttf','-Bold.ttf')))
pdfmetrics.registerFontFamily('D',normal='D',bold='DB',italic='D',boldItalic='DB')
ink='#193746';blue='#176e92';gray='#596b76'
styles={
 'body':ParagraphStyle('body',fontName='D',fontSize=10,leading=14.5,textColor=ink,spaceAfter=9),
 'title':ParagraphStyle('title',fontName='DB',fontSize=24,leading=30,textColor=ink,spaceAfter=15),
 'h':ParagraphStyle('h',fontName='DB',fontSize=17,leading=23,textColor=ink,spaceAfter=12),
 'small':ParagraphStyle('small',fontName='D',fontSize=8.3,leading=12,textColor=gray,spaceAfter=8),
 'cell':ParagraphStyle('cell',fontName='D',fontSize=9,leading=13,textColor=ink),
 'tag':ParagraphStyle('tag',fontName='DB',fontSize=9,leading=13,textColor=blue,spaceAfter=11)}
s=[]
def p(t,style='body'):s.append(Paragraph(t,styles[style]))
def h(n,t):p(f'AUDITORÍA V3  /  {n:02d}','tag');p(t,'h')
def new():s.append(PageBreak())
def tab(rows,widths):
 t=Table([[Paragraph(str(c),styles['cell']) for c in row] for row in rows],colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8f0f4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),.35,colors.HexColor('#cedae1'))]));s.append(t);s.append(Spacer(1,11))
def img(path,w=499):
 from PIL import Image as PI
 with PI.open(path) as a:x,y=a.size
 s.append(Image(str(path),width=w,height=w*y/x));s.append(Spacer(1,10))

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#c9d3d9','text.color':ink,'axes.labelcolor':ink,'xtick.color':gray,'ytick.color':gray})
a=pd.read_csv(E/'escenarios.csv');fig,ax=plt.subplots(figsize=(8,3))
x=a.normal_fraction*100;y=a.degraded_fraction*100;z=100-x-y
ax.barh(a.run_id,x,label='Normal',color='#43866c');ax.barh(a.run_id,y,left=x,label='Degradación',color='#d5a350');ax.barh(a.run_id,z,left=x+y,label='Fallo',color='#ac5557')
ax.invert_yaxis();ax.set_xlim(0,100);ax.set_xlabel('Registros de telemetría (%)');ax.legend(loc='upper center',bbox_to_anchor=(.5,1.22),ncol=3,frameon=False)
fig.subplots_adjust(left=.08,right=.96,top=.81,bottom=.19);fig.savefig(T/'estados.png',dpi=190);plt.close(fig)

p('PROYECTO DE JOSEPH  /  5 DE NOVIEMBRE DE 2026','tag')
p('Auditoría antes<br/>del entrenamiento','title')
p('ACB_Motor_Rodamientos_Sintetico_v3 · entrega 3.0.0')
p('<b>Dictamen: apto condicionado para ensayar el método y la aplicación.</b> El núcleo de datos, etiquetas y variables supera las pruebas ejecutadas. No procede aprobarlo como simulación industrial validada ni como demostración de utilidad del machine learning antes de comparar modelos y reglas simples.')
tab([['Resultado','Qué significa'],['486 comprobaciones correctas; 3 fallidas','Las tres fallidas corresponden al mismo defecto semántico en tres mantenimientos reprogramados. No se ha detectado fuga de información en los predictores permitidos mediante las pruebas realizadas.'],['Datos preservados; sin modelos entrenados','Se ha trabajado con una copia para ejecutar las validaciones originales. No se han modificado la v3 ni sus etiquetas y no se han entrenado XGBoost o Isolation Forest.'],['Realismo condicionado','Hay degradación progresiva, fallos súbitos, reparaciones y defectos de adquisición. Sus magnitudes y frecuencias siguen siendo supuestos del demostrador.']],[148,351])
p('<b>Decisión recomendada.</b> Cerrar el protocolo de evaluación, las reglas de selección de filas y las dos variantes de referencia para Isolation Forest antes de entrenar. Corregir la cronología de programación antes de usarla en la aplicación. Ampliar escenarios antes de afirmar robustez.')
p('<b>Qué no puede certificar esta auditoría.</b> No hay medidas reales, características OEM verificadas ni tasas de avería de ACB con las que calibrar el simulador. No se puede garantizar que el conjunto se comporte como una máquina real ni que un modelo entrenado con él mejore el mantenimiento industrial.')
p('Objeto auditado: ZIP v3.0.0, 840.960 registros de telemetría, 280.320 decisiones y 398 fallos sintéticos. Telemetría cada 5 minutos; decisiones cada 15 minutos.','small')

new();h(1,'Qué se ha comprobado realmente')
tab([['Bloque','Evidencia ejecutada','Resultado'],['Integridad','SHA-256 de los 99 archivos incluidos en el manifiesto','99 coinciden'],['Validaciones del paquete','Claves, rejillas, etiquetas, calidad, causalidad, catálogo y segmentos','375 + 50 correctas'],['Auditoría independiente','Oráculo vectorizado de etiquetas, estadísticas directas, historia de mantenimiento, separación y contratos','61 correctas; 3 fallidas'],['Regeneración','Ocho mundos, variables y etiquetas, comparados con la misma configuración','44/44 archivos idénticos por SHA-256'],['SQL','Análisis sintáctico con pglast','57 sentencias aceptadas; no ejecutadas en servidor']],[100,290,109])
p('<b>Temporalidad.</b> Se comprueba que las señales se usan cuando ya han llegado, no solo cuando fueron observadas. Se han contrastado directamente 8.640 estadísticas de 15 señales, dos ventanas y 12 instantes por ejecución, sin reutilizar el constructor de variables.')
p('<b>Etiquetas.</b> Se reconstruye el fallo en las siguientes 24 horas, respetando el siguiente preventivo, el fin de seguimiento y los regímenes elegibles. Las etiquetas nulas se conservan: no se convierten en “no fallo”.')
p('<b>Entradas.</b> La lista de 110 predictores numéricos y 3 categóricos excluye daño, salud simulada, evento futuro, identificadores y partición. No hay normalización ni imputación ajustadas en la entrega. Treinta y dos predictores numéricos presentan algún ausente en entrenamiento; esto debe resolverse dentro del futuro pipeline.')
p('<b>Separación.</b> La purga de 28 horas y la exclusión de episodios que cruzan fronteras están implementadas. No se comparten eventos positivos entre particiones. R07-R08 quedan fuera del entrenamiento. El uso de verdad latente para excluir episodios es una ventaja de la simulación, no algo automáticamente disponible en una planta.')
p('Alcance: pruebas funcionales y estructurales. No son 489 ensayos estadísticos independientes. Test y estrés se han inspeccionado para auditoría de estructura y disponibilidad; no se han utilizado para optimizar modelos o umbrales. La inspección previa impide describirlos como conjuntos nunca vistos por el analista.','small')

new();h(2,'Defecto de cronología en mantenimiento')
p('<b>H01 · Prioridad alta para la aplicación.</b> En tres preventivos, el inicio real se retrasa hasta terminar un correctivo. El generador asigna <b>known_at = inicio real - 7 días</b>. Así atribuye conocimiento anticipado a una reprogramación causada por una avería todavía futura.')
tab([['Preventivo','Inicio real UTC','Retraso'],['R04-M0040','12/08/2024 05:15','5 h 15 min'],['R06-M0020','22/04/2024 00:55','55 min'],['R07-M0066','04/11/2024 01:55','1 h 55 min']],[150,225,124])
p('<b>Ejemplo comprobado: R04-M0040.</b> El plan periódico llevaba al 12 de agosto a las 00:00. Una avería comienza el 11 de agosto a las 22:45 y el correctivo termina el día 12 a las 05:15. El preventivo empieza entonces, pero su registro sitúa el conocimiento de esa hora el 5 de agosto a las 05:15.')
p('<b>Impacto delimitado.</b> El campo no forma parte de las 113 entradas permitidas. Las variables de historial de servicio solo incorporan resultados ya disponibles y han pasado su reconstrucción. Este hallazgo no invalida por sí mismo las etiquetas retrospectivas ni demuestra una fuga en X; sí invalida interpretar esa fila completa como un calendario conocido en tiempo real.')
p('<b>Cierre verificable.</b> Separar fecha prevista, fecha real y momento de conocimiento de cada cambio. Mantener versiones del plan: el retraso no puede estar disponible antes de la causa que lo genera. Añadir el test de regresión de estos tres casos y volver a construir la documentación y el SQL afectados. No basta con cambiar una cifra en el informe.')
p('<b>H02 · Prioridad media de integración.</b> El resumen original asigna 28.852 <i>usable_rows</i> a la partición excluida porque cuenta calidad y etiqueta, sin descontar la exclusión. El ejemplo de carga filtra bien, pero el nombre puede inducir un error. La auditoría asigna <b>cero filas utilizables</b> a “excluida”; debe mantenerse ese filtro en toda exportación y entrenamiento.')
p('Evidencia: src/01_generar_dataset.py, función simulate; src/03_etiquetas_particiones.py, resumen de particiones; evidence/preventivos_pospuestos.csv y auditoria_independiente.json. Se conservan los originales sin aplicar una corrección silenciosa.','small')

new();h(3,'Realismo: variedad sí, calibración no')
img(T/'estados.png')
p('<b>H03 · Predomina la degradación.</b> Entre el 85,26 % y el 92,15 % de los registros de cada mundo están etiquetados como degradación del conjunto. Basta que un componente supere el umbral latente de 0,55. Este porcentaje depende de una convención del simulador; no equivale a una medición real de daño ni a la probabilidad de fallo en 24 horas.')
p('Se generan 42-63 fallos por mundo y 5,49-8,31 fallos por 1.000 horas operativas. El escenario está enriquecido para practicar. <b>No se sabe</b> si esas tasas representan el motor real: no hay histórico industrial para compararlas.')
p('<b>H04 · Simplificaciones observadas.</b> El ciclo operativo se repite cada 8 horas; el preventivo nominal, cada 28 días. Cada señal recibe un bloque de ausencia, congelación, pico y deriva por mundo. Los picos se construyen a 1,25 veces el máximo de rango, por lo que son fáciles de filtrar. No se simulan ondas ni frecuencias de defecto de rodamientos.')
p('<b>Ampliación recomendada antes del benchmark final.</b> Incorporar periodos sanos largos, ritmos de operación irregulares, fallos menos frecuentes, distintos niveles de ruido y deriva dentro de rango, pérdidas correlacionadas y calibraciones distintas por sensor. Reservar semillas nuevas. Cambiar estos supuestos para probar sensibilidad, nunca para aumentar artificialmente la precisión.')
p('No convertir la falta de datos reales en una promesa de parecido industrial. La meta alcanzable es un experimento sintético trazable con decisiones, fallos y limitaciones coherentes. La carga, corriente, vida útil, transmisión e inventario del motor siguen sin calibración OEM.','small')

new();h(4,'Suficiencia para aprender y evaluar')
tab([['Partición','Filas utilizables','Fallos con etiqueta útil','Con oportunidad 3/5 y ≥60 min'],['Entrenamiento','93.614','164','162'],['Validación','20.907','33','33'],['Prueba temporal','20.983','34','33'],['Estrés','51.273','113','111']],[115,112,130,142])
p('La última columna solo pregunta si existen suficientes decisiones positivas utilizables para abrir un aviso con antelación. <b>No son fallos detectados ni un techo predictivo.</b> Cinco instantes separados 15 minutos abarcan 60 minutos entre el primero y el último; no se saltan huecos para fabricar cinco decisiones válidas.')
p('<b>H05 · Incertidumbre por eventos.</b> Validación y prueba contienen 30 fallos progresivos cada una, y solo 3 y 4 súbitos respectivamente con etiqueta útil. Un solo fallo cambia una sensibilidad calculada sobre 33-34 sucesos en unos 3 puntos porcentuales. Las muchas filas correlacionadas no sustituyen a nuevos eventos independientes.')
p('<b>¿Es una predicción trivial?</b> La mejor separación univariante entre las entradas numéricas, examinada solo en entrenamiento, alcanza AUROC 0,693 con vibración DE. La prevalencia positiva es 12,99 %. No se observa una variable numérica que separe perfectamente las clases en esa prueba. Esto no descarta atajos multivariantes ni es una métrica de generalización.')
p('<b>H06 · Referencia privilegiada de Isolation Forest.</b> Los 8.785 registros “sanos” usan salud e incidencias internas del simulador. Incluyen 27 decisiones con fallo posterior en 24 horas y 121 sin etiqueta conocida: estar sano ahora no garantiza ausencia de fallo futuro.')
p('<b>Dos ensayos necesarios.</b> Comparar una referencia limpia asistida por el simulador, claramente identificada como ideal, con otra construida solo con información observable de entrenamiento. Isolation Forest produce una puntuación de anomalía; no equivale por sí mismo a una probabilidad de fallo en 24 horas [W2].')
p('Evidencia: particiones_independientes.csv, oportunidades_eventos.csv, discriminacion_univariante_solo_train.csv. No se han evaluado predicciones en test/estrés.','small')

new();h(5,'Contrato de evaluación que debe cerrarse')
p('<b>H07 · Antes de entrenar.</b> El dataset define la etiqueta y propone persistencia, pero todavía no existe una evaluación ejecutable de alertas. Estos son los criterios de aceptación propuestos; no son resultados obtenidos ni normas industriales.')
tab([['Regla propuesta','Comprobación de aceptación'],['Comparadores obligatorios','Comparar XGBoost con una probabilidad constante, una regla sencilla de condición y un modelo sencillo basado en historial/carga. Misma exposición, mismas particiones y mismo presupuesto de avisos.'],['Selección sin contaminar prueba','Imputación, codificación y cualquier ajuste: solo entrenamiento. Hiperparámetros y umbrales: validación. Test y estrés: evaluación final tras congelar decisiones [W1].'],['Tiempo y episodios','Usar cortes por fechas comunes en las seis ejecuciones, con purga y exclusión de episodios. No dividir al azar las filas ni aplicar TimeSeriesSplit a mundos concatenados sin respetar sus fechas [W3].'],['Persistencia y abstención','Probar 3 de las últimas 5 posiciones de 15 min. Una posición no evaluable no cuenta como alarma ni como recuperación. Definir pausa y cierre; probar huecos y cambios de régimen.'],['Aviso útil','Asociar avisos agrupados con el siguiente fallo, entre 1 y 24 horas antes. Definir correspondencia única, repetición, cierres y avisos censurados por mantenimiento o fin de seguimiento.'],['Métricas principales','Sensibilidad por fallo y modo, falsas alertas por 1.000 horas operativas, anticipación, cobertura y porcentaje sin evaluación. Añadir PR-AUC y calibración para la probabilidad de XGBoost.']],[129,370])
p('<b>Regla de éxito.</b> El modelo deberá mejorar a los comparadores con el mismo límite de falsas alertas y un margen útil de aviso. El presupuesto aceptable debe fijarse antes de optimizar. Informar intervalos de incertidumbre por episodios/mundos y resultados de fallos súbitos por separado, sin ocultarlos.')
p('<b>Utilidad empresarial.</b> Puede ensayarse la priorización de inspecciones. Un análisis de costes debe declarar costes y eficacia de intervención como hipótesis y hacer sensibilidad. No se pueden sumar las paradas históricas asociadas a alertas y llamarlas “horas evitadas”: la v3 no simula todavía el efecto causal de actuar sobre esos avisos.')

new();h(6,'Plan de cierre y alcance de la aprobación')
tab([['Prioridad','Acción concreta','Criterio de cierre'],['Alta · aplicación','H01: versionar programación y reprogramación de preventivos','Los tres casos no anticipan información; nuevo test pasa y catálogo/SQL/documentación coinciden.'],['Alta · método','H07: implementar el evaluador de alertas y fijar comparadores, presupuesto y reglas','Pruebas con sucesos conocidos, avisos repetidos, censura, huecos y ausencia de avisos.'],['Alta · método','H06: separar las dos referencias de Isolation Forest','Resultados reportados por variante; ninguna utiliza verdad interna en inferencia.'],['Media · integración','H02: filtrar excluidas y aclarar el resumen; tratar ausentes dentro del pipeline','Cero filas excluidas en X; unión por claves; transformaciones ajustadas solo con train.'],['Media · robustez','H03-H05: añadir escenarios sanos, variabilidad y semillas reservadas','Configuración y semillas congeladas antes del entrenamiento final; resultados por escenario y evento.'],['Antes de desplegar','H08: ejecutar carga PostgreSQL y simulación de llegada de datos','Conteos, claves, transacciones, permisos de verdad privada y reproducibilidad del snapshot verificados.']],[95,210,194])
p('<b>Qué puede hacerse ya.</b> EDA, desarrollo del pipeline sobre una copia y diseño del dashboard con señales, calidad y abstenciones. El dataset actual sirve para probar las piezas técnicas, manteniendo explícitas las restricciones detectadas.')
p('<b>Qué no queda aprobado todavía.</b> La evaluación final de utilidad del ML, el comportamiento de una aplicación con calendario de mantenimiento y cualquier afirmación sobre maquinaria real. La ejecución de SQL en PostgreSQL/Neon, Windows/Spyder y el dashboard no se han verificado en esta auditoría.')
p('<b>Recomendación de versión.</b> Conservar v3.0.0 como referencia. Separar una corrección de metadatos y contratos de la ampliación de escenarios; cada cambio debe llevar nueva versión, manifiesto y pruebas. No cambiar etiquetas o tasas de fallo para conseguir un resultado favorable.')
p('Los cierres son trabajo pendiente identificado por la auditoría; no se presentan como correcciones ya aplicadas.','small')

new();h(7,'Fuentes, límites y reproducción')
p('<b>Datos y código verificados.</b> Paquete ACB_Motor_Rodamientos_Sintetico_v3.zip, entrega 3.0.0. Se inspeccionaron generador, constructor de variables, etiquetas, validadores, cargador, DDL, diccionario y metodología. La evidencia numérica procede de los Parquet y de las ejecuciones guardadas en el anexo reproducible.')
p('SHA-256 del ZIP auditado:<br/><font size="7">8f04104e555701ba7336b5c23428346b5deb8c6a3f7b432755745b0597d74137</font>','small')
tab([['Documento aportado','Contenido comprobado y límite'],['Sestao de un vistazo','Página 1, ficha histórica con copyright 2013: productos y dimensiones. Es contexto de diseño; no es verificación de condiciones actuales ni fuente de parámetros de motor.'],['Estudio de Eficiencia de una Acería en Sestao','Texto extraíble de 97 páginas; revisión específica de páginas PDF 38-40 (numeradas 36-38): tren, transmisión y motor. Las medidas de compresores del estudio no calibran este motor lógico.'],['Declaración Ambiental 2024','PDF de 35 páginas sin texto útil extraíble. OCR parcial de páginas 1-10; página 10 identifica producción de bobina laminada en caliente. No se ha realizado lectura integral de las 35 páginas ni obtenido una serie de sensores del motor.']],[155,344])
p('<b>Referencias metodológicas oficiales consultadas el 05/11/2026.</b> Se usan para fundamentar el diseño de la evaluación, no para calibrar la física del simulador.','small')
p('[W1] scikit-learn, Common pitfalls and recommended practices. Ajustar transformaciones solo en entrenamiento y evitar fugas mediante pipelines.<br/><link href="https://scikit-learn.org/stable/common_pitfalls.html">https://scikit-learn.org/stable/common_pitfalls.html</link>','small')
p('[W2] scikit-learn, Novelty and Outlier Detection. Distingue detección de anomalías y novedad; el score no es una probabilidad de fallo futura.<br/><link href="https://scikit-learn.org/stable/modules/outlier_detection.html">https://scikit-learn.org/stable/modules/outlier_detection.html</link>','small')
p('[W3] scikit-learn, TimeSeriesSplit. Particiones ordenadas en el tiempo y separación mediante gap. La adaptación a múltiples mundos y episodios es un criterio de esta auditoría.<br/><link href="https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html">Documentación oficial de TimeSeriesSplit</link>','small')
p('<b>Reproducibilidad.</b> El anexo incluye scripts, entorno, logs, tablas de hallazgos y resultados. No redistribuye los PDF originales ni el dataset completo. Las comprobaciones se ejecutan sobre una copia; el ZIP original y la v2 permanecen intactos. El README detalla cómo repetirlas.')
p('<b>Conclusión.</b> Es posible construir una demostración rigurosa sin datos reales si se declara qué es observado, qué es supuesto y qué sigue sin comprobarse. La auditoría acredita coherencia técnica bajo esas condiciones; el valor añadido del machine learning sigue siendo una hipótesis que la evaluación debe poner a prueba.')

def footer(can,doc):
 can.saveState();can.setStrokeColor(colors.HexColor('#d1dce2'));can.line(48,43,547,43);can.setFont('D',8);can.setFillColor(colors.HexColor(gray));can.drawString(48,29,'ACB v3 · Auditoría del demostrador sintético · 05/11/2026');can.drawRightString(547,29,f'{doc.page} / 8');can.restoreState()
dest=R/'Auditoria_ACB_Motor_Rodamientos_Sintetico_v3.pdf'
doc=SimpleDocTemplate(str(dest),pagesize=(595.276,841.89),leftMargin=48,rightMargin=48,topMargin=44,bottomMargin=58,title='Auditoría ACB Motor Rodamientos Sintético v3',author='Proyecto de Joseph')
doc.build(s,onFirstPage=footer,onLaterPages=footer);print(dest)
