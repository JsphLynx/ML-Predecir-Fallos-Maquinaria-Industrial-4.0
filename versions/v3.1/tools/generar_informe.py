"""Informe de cierre desde evidencias ejecutadas. Requiere reportlab y matplotlib."""
from pathlib import Path
import json,hashlib
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]

def main():
 r=ROOT;out=r/'docs/Cierre_Auditoria_ACB_Motor_Rodamientos_Sintetico_v3_1.pdf'
 load=lambda name:json.loads((r/'resultados'/name).read_text())
 gen=load('generacion.json');var=load('variables.json');rep=load('reproducibilidad.json');pg=load('postgresql_ejecutado.json')
 files=['validacion.json','validacion_catalogo_segmentos.json','pruebas_protocolo.json','cierre_correcciones.json','replay_llegada.json','postgresql_ejecutado.json']
 evidence=[load(f) for f in files]
 if any(v['failed'] for v in evidence) or rep['differences']:raise ValueError('No publicar aprobación con pruebas fallidas')
 total=sum(v['checks'] for v in evidence)
 health=pd.read_csv(r/'resultados/escenarios_salud.csv');parts=pd.read_csv(r/'resultados/particiones.csv')
 cohorts=pd.read_csv(r/'resultados/cohortes_eventos.csv');refs=pd.read_csv(r/'resultados/referencias_if.csv')
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
 fig,ax=plt.subplots(2,1,figsize=(9,6.3),layout='constrained')
 x=health.run_id;ax[0].bar(x,health.normal_fraction*100,color='#168879',label='Normal simulado')
 ax[0].bar(x,health.degraded_fraction*100,bottom=health.normal_fraction*100,color='#deb64b',label='Degradación simulada')
 rem=100*(1-health.normal_fraction-health.degraded_fraction)
 ax[0].bar(x,rem,bottom=100*(health.normal_fraction+health.degraded_fraction),color='#bd5555',label='Fallo')
 ax[0].set_ylabel('% de telemetría');ax[0].set_ylim(0,104);ax[0].legend(ncol=3,loc='upper center',bbox_to_anchor=(.5,1.2),frameon=False,fontsize=8)
 ax[1].bar(x,health.failures_per_1000h,color=['#28495d']*6+['#168879']*6+['#8071ad']*4)
 ax[1].set_ylabel('Fallos / 1.000 h operativas');ax[1].set_xlabel('R01-R06: degradación frecuente | R07-R12: vida larga | R13-R16: estrés')
 for a in ax:a.grid(axis='y',alpha=.15);a.set_axisbelow(True)
 chart=r/'resultados/comparacion_escenarios_v31.png';fig.savefig(chart,dpi=170);plt.close(fig)
 # Durable machine-readable closure matrix.
 matrix=[
 ('H01','Corregido','Plan versionado: previsto, aplazado e iniciado. Hora futura desconocida al aplazar. Lecturas asof, tres casos originales y fixture del generador con colisiones forzadas.'),
 ('H02','Corregido','Cero filas utilizables en excluida; conteos de calidad separados; unión por claves y lista permitida de entradas.'),
 ('H03','Ampliado','Seis mundos base de vida larga y dos de estrés de vida larga. Menos predominio de degradación; sin calibración industrial.'),
 ('H04','Ampliado','Turnos y preventivos variables, calibración distinta, picos variables, deriva dentro de rango y pérdidas correlacionadas.'),
 ('H05','Tratado en protocolo','Denominadores por suceso, incertidumbre por mundos y modos escasos descriptivos. La suficiencia estadística no se presume.'),
 ('H06','Separado','Referencia observable principal y referencia ideal privilegiada para sensibilidad. Ninguna es predictor.'),
 ('H07','Implementado','Evaluador de alertas, comparadores sin ajustar, folds, presupuesto y regla de éxito. Rendimiento pendiente del entrenamiento.'),
 ('H08','Verificado localmente','Carga real PostgreSQL, restricciones, rollback, permisos y lectura causal; replay de llegada. Windows/Neon aún no verificados.')]
 pd.DataFrame(matrix,columns=['hallazgo','estado','consecuencia_y_cierre']).to_csv(r/'docs/matriz_cierre.csv',index=False)
 md=['# Cierre de auditoría v3.1.0','',f'{total} comprobaciones correctas; 0 fallidas. {rep["identical_files"]}/{rep["compared_files"]} archivos reproducidos idénticos. No son ensayos estadísticos independientes.','', '| Hallazgo | Estado | Cierre y límite |','|---|---|---|']
 md += ['| '+' | '.join(row)+' |' for row in matrix]
 md += ['', 'Apto para iniciar el experimento sintético bajo el protocolo congelado. No acredita capacidad predictiva, ahorro o fiabilidad reales. El entrenamiento definitivo y los resultados por modelo pertenecen a la siguiente fase.', '', 'Defecto adicional corregido: una sustitución no puede aumentar el daño latente. Se recalcularon los mundos afectados y se verificó la regeneración completa. La configuración y semillas no se ajustaron por resultados de modelos.', '', 'Evidencia: archivos JSON de resultados, src/12-15, config/protocolo_preentrenamiento.json y SHA256.json. La auditoría v3 original se conserva en docs/referencia/Auditoria_v3_0.pdf.']
 (r/'docs/CIERRE_AUDITORIA.md').write_text('\n'.join(md)+'\n')
 font=Path('/usr/share/fonts/truetype/dejavu')
 if font.exists():
  pdfmetrics.registerFont(TTFont('DejaVu',str(font/'DejaVuSans.ttf')));pdfmetrics.registerFont(TTFont('DejaVu-Bold',str(font/'DejaVuSans-Bold.ttf')))
  normal,bold='DejaVu','DejaVu-Bold'
  pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVu-Bold',italic='DejaVu',boldItalic='DejaVu-Bold')
 else:normal,bold='Helvetica','Helvetica-Bold'
 styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyCustom',fontName=normal,fontSize=9.3,leading=14,textColor=colors.HexColor('#263c4c'),spaceAfter=9))
 styles.add(ParagraphStyle(name='TitleCustom',fontName=bold,fontSize=26,leading=31,textColor=colors.HexColor('#123347'),spaceAfter=14))
 styles.add(ParagraphStyle(name='HeadCustom',fontName=bold,fontSize=18,leading=23,textColor=colors.HexColor('#123347'),spaceAfter=13))
 styles.add(ParagraphStyle(name='SmallCustom',fontName=normal,fontSize=7.8,leading=11,textColor=colors.HexColor('#48616e'),spaceAfter=7))
 styles.add(ParagraphStyle(name='CellCustom',fontName=normal,fontSize=8,leading=11,textColor=colors.HexColor('#263c4c')))
 P=lambda x,style='BodyCustom':Paragraph(x,styles[style]);story=[]
 def title(k,h):story.extend([P(k.upper(),'SmallCustom'),P(h,'HeadCustom')])
 def para(t):story.append(P(t))
 def table(rows,widths):
  data=[[P(str(x),'CellCustom') for x in row] for row in rows]
  t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1)
  t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dce9ed')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f2f6f7')]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)]));story.append(t);story.append(Spacer(1,11))
 story.append(P('PROYECTO DE JOSEPH / 05 NOVIEMBRE 2026','SmallCustom'))
 story.append(Spacer(1,18));story.append(P('Dataset revisado<br/>Motor y rodamientos','TitleCustom'))
 para('<b>ACB_Motor_Rodamientos_Sintetico_v3_1 · entrega 3.1.0</b>')
 para('Se han corregido los defectos detectados, ampliado los escenarios y preparado la evaluación. La v3 original se conserva. Esta entrega permite ensayar el método y la aplicación con datos sintéticos trazables.')
 table([['Telemetría','Decisiones','Fallos simulados','Mundos alternativos'],[f'{gen["telemetry_rows"]:,}'.replace(',','.'),f'{var["decision_rows"]:,}'.replace(',','.'),gen['failure_count'],16]],[128,128,128,128])
 para('<b>Dictamen: apto para iniciar el experimento sintético bajo el protocolo definido.</b> No se han entrenado XGBoost ni Isolation Forest. Tampoco se ha demostrado todavía que superen a los comparadores simples.')
 para('La telemetría conserva una medida cada <b>5 minutos</b>; las decisiones, cada <b>15 minutos</b>. La pregunta sigue siendo: ¿ocurrirá un fallo funcional en las próximas <b>24 horas</b>?')
 para(f'<b>Comprobaciones:</b> {total} correctas y ninguna fallida en los bloques de validación final. Segunda generación: {rep["identical_files"]} archivos idénticos de {rep["compared_files"]} comparados.')
 para('Los 16 mundos son simulaciones alternativas de un conjunto lógico, no 16 motores de ACB. Los rangos, vidas y frecuencias son supuestos; no constituyen un gemelo digital validado.')
 story.append(Spacer(1,13));para('<b>Qué queda para después:</b> entrenar, comparar, explicar y evaluar los modelos. Cualquier afirmación de capacidad predictiva sobre maquinaria real o ahorro requeriría evidencia que este dataset no proporciona.')
 story.append(PageBreak());title('01 / Respuesta a la auditoría','Qué se ha corregido y qué significa')
 table([['Hallazgo','Estado','Cierre y límite']]+[list(row) for row in matrix],[60,100,352])
 para('<b>Corrección adicional de la revisión:</b> se impide que una sustitución aumente el daño interno. Se recalcularon los datos afectados sin cambiar semillas ni buscar mejores resultados predictivos.')
 story.append(PageBreak());title('02 / Exploración de los datos','Más variedad para probar el método')
 story.append(Image(str(chart),width=512,height=358));story.append(Spacer(1,8))
 normalrange=health.loc[health.scenario.eq('base_vida_larga'),'normal_fraction']*100
 para(f'En R07-R12, el estado normal ocupa entre {normalrange.min():.1f} % y {normalrange.max():.1f} % de la telemetría. La figura superior usa <b>verdad interna del simulador</b>: sirve para auditar escenarios y está prohibida como entrada del modelo.')
 para('La figura inferior divide fallos por horas de funcionamiento. Permite comprobar que conviven escenarios de fallos frecuentes y otros con menor incidencia. No compara rendimiento de modelos ni estima una tasa real de avería de ACB.')
 small=cohorts[cohorts.descriptive_only]
 para(f'La evaluación por modo mantiene visibles los estratos pequeños: {len(small)} combinaciones de partición y modo tienen menos de 20 sucesos. Se informarán como resultados descriptivos, con sus denominadores; muchas filas no sustituyen a fallos independientes.')
 story.append(PageBreak());title('03 / Reglas antes de entrenar','Cómo se evitarán conclusiones engañosas')
 table([['Regla','Aplicación concreta'],['Entradas disponibles','Solo señales e historial conocidos en ese instante. Salud, daño interno y fallo futuro quedan fuera.'],['Dos referencias IF','La principal usa calidad e historial observable; la ideal usa verdad simulada y se informa aparte.'],['Separación temporal','Cortes por fechas comunes, purga de 28 h y episodios separados. Transformaciones ajustadas solo con train.'],['Aviso persistente','3 de 5 posiciones de 15 min; un hueco no cuenta como normalidad ni se elimina del reloj.'],['Aviso útil','Entre 1 y 24 h antes del siguiente fallo; un evento detectado una sola vez. Preventivos y fin pueden censurar avisos.'],['Presupuesto fijo','Máximo 1 falsa alerta por 1.000 h operativas. Los umbrales se eligen en validación.'],['Comparación exigente','Constante, regla de condición e historial/carga. Mejora >=5 puntos de sensibilidad e IC pareado positivo bajo el mismo presupuesto.']],[126,386])
 para('Se contabilizan todos los fallos del periodo, incluidos los que no tenían datos suficientes. El benchmark conserva exclusiones retrospectivas; la simulación de servicio se informa aparte y solo usa elegibilidad observable. La aplicación nunca debe consultar episodios futuros para decidir si predice.')
 para('La precisión-recall y la calibración se calculan para probabilidades supervisadas. Un score de Isolation Forest es una puntuación de anomalía, no una probabilidad de fallo futuro.')
 para('La configuración exacta y el código están incluidos. Si ningún modelo mejora a los comparadores dentro del presupuesto, el resultado se comunicará así; no se cambiarán las reglas para forzar el éxito.')
 story.append(PageBreak());title('04 / Evidencias y siguiente fase','Qué se ha ejecutado realmente')
 names=['Datos, etiquetas y causalidad','Catálogo y segmentos','Fixtures del protocolo','Correcciones y referencias','Replay de llegada','PostgreSQL real']
 table([['Bloque','Correctas','Alcance']]+[[name,item['passed'],'0 fallidas'] for name,item in zip(names,evidence)]+[['Regeneración completa',f'{rep["identical_files"]}/{rep["compared_files"]}','Igualdad SHA-256']],[300,85,127])
 para('La carga SQL se ejecutó con PostgreSQL 16.2 en un entorno local aislado. Se verificaron conteos, claves, restricciones, rollback y denegación de acceso del lector a verdad, objetivos y filas completas de mantenimiento. El replay reconstruyó decisiones con las medidas disponibles en cada instante.')
 para('<b>No comprobado en esta entrega:</b> instalación Windows/Spyder, despliegue Neon, dashboard final y rendimiento de modelos. Son verificaciones del destino o de la fase siguiente; no se presentan como superadas.')
 para('<b>Próximo paso:</b> verificar el manifiesto y ejecutar los comparadores y modelos bajo el protocolo congelado. Guardar preprocesador, semillas, hiperparámetros y umbrales antes de evaluar test y estrés.')
 para('Fuentes de esta revisión: ZIP v3.0.0 y auditoría del 05/11/2026; generador, Parquet y resultados ejecutados de v3.1.0. Las fuentes industriales aportadas son contexto documental, no medidas para calibrar el motor.')
 story.append(P('Referencia metodológica: scikit-learn, Common pitfalls: https://scikit-learn.org/stable/common_pitfalls . Reglas y presupuestos del ensayo: decisiones explícitas del proyecto, no recomendaciones de operación de ACB.','SmallCustom'))
 def footer(canvas,doc):
  canvas.setStrokeColor(colors.HexColor('#dce9ed'));canvas.line(42,43,554,43)
  canvas.setFont(normal,7);canvas.setFillColor(colors.HexColor('#48616e'))
  canvas.drawString(42,30,'ACB v3.1 · Demostrador sintético · Sin modelos entrenados')
  canvas.drawRightString(554,30,str(doc.page))
 SimpleDocTemplate(str(out),pagesize=(595.28,841.89),leftMargin=42,rightMargin=41.28,topMargin=40,bottomMargin=58,title='Cierre de auditoría ACB Motor Rodamientos v3.1',author='Proyecto de Joseph').build(story,onFirstPage=footer,onLaterPages=footer)
 print(out)
if __name__=='__main__':main()
