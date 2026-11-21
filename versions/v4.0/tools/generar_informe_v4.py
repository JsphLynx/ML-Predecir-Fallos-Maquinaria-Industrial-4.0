"""Informe de entrega a partir de los controles ejecutados; no entrena modelos."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
NAVY=HexColor('#153247');TEAL=HexColor('#087f83');LIGHT=HexColor('#eaf3f4');GRAY=HexColor('#455764')

def main():
    fonts=Path('/usr/share/fonts/truetype/dejavu')
    # On Windows, Arial is a supported fallback; fonts are local, no download needed.
    if fonts.exists():normal=fonts/'DejaVuSans.ttf';bold=fonts/'DejaVuSans-Bold.ttf'
    else:
        import os
        fonts=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts';normal=fonts/'arial.ttf';bold=fonts/'arialbd.ttf'
    pdfmetrics.registerFont(TTFont('Body',str(normal)));pdfmetrics.registerFont(TTFont('BodyBold',str(bold)))
    styles={
        'title':ParagraphStyle('title',fontName='BodyBold',fontSize=25,leading=31,textColor=NAVY,spaceAfter=15),
        'h':ParagraphStyle('h',fontName='BodyBold',fontSize=19,leading=25,textColor=NAVY,spaceAfter=14),
        'sub':ParagraphStyle('sub',fontName='BodyBold',fontSize=11,leading=16,textColor=TEAL,spaceBefore=12,spaceAfter=6),
        'p':ParagraphStyle('p',fontName='Body',fontSize=9.3,leading=14,textColor=GRAY,spaceAfter=9),
        'small':ParagraphStyle('small',fontName='Body',fontSize=7.6,leading=11,textColor=GRAY,spaceAfter=7),
        'cell':ParagraphStyle('cell',fontName='Body',fontSize=8,leading=11,textColor=NAVY),
        'head':ParagraphStyle('head',fontName='BodyBold',fontSize=8,leading=11,textColor=white),
        'label':ParagraphStyle('label',fontName='BodyBold',fontSize=8,leading=11,textColor=TEAL,spaceAfter=14),
    }
    story=[]
    def p(text,kind='p'):story.append(Paragraph(text,styles[kind]))
    def table(headers,rows,widths):
        data=[[Paragraph(escape(str(x)),styles['head']) for x in headers]]
        data += [[Paragraph(escape(str(x)),styles['cell']) for x in row] for row in rows]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[LIGHT,white]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
        story.append(t);story.append(Spacer(1,10))
    def page(title,kicker):
        if story:story.append(PageBreak())
        p('INDUSTRIA 4.0 / DATASET SINTÉTICO / '+kicker,'label');p(title,'h')
    def read(name):return json.loads((ROOT/'resultados'/name).read_text())
    gen=read('generacion.json');feat=read('variables.json');rep=read('reproducibilidad.json')
    suites=[('Datos y causalidad','validacion.json'),('Catálogo y segmentos','validacion_catalogo_segmentos.json'),('Evaluador con fixtures','pruebas_protocolo.json'),('Cierre y preparación','cierre_correcciones.json'),('Replay de disponibilidad','replay_llegada.json'),('Física y sensibilidad','validacion_fisica.json'),('Contratos y SQL','contratos_relacionales.json')]
    audit=[(name,read(file)) for name,file in suites];total=sum(x['checks'] for _,x in audit)
    p('PROYECTO DE JOSEPH / 20 DE NOVIEMBRE DE 2026','label')
    p('Dataset sintético<br/>Motor y rodamientos<br/>Versión 4.0','title')
    p('Mejora del simulador a partir del contraste Sestao - SMS group','sub')
    p('Nueva generación completa con contexto mecánico explícito, contratos de sensores y trazabilidad de parámetros. Se conserva la v3.1 como experimento independiente.')
    table(['Entrega','Resultado'],[
        ['Telemetría',f"{gen['telemetry_rows']:,}".replace(',','.')+' filas; 16 mundos, 365 días, paso de 5 min'],
        ['Decisiones',f"{feat['decision_rows']:,}".replace(',','.')+' filas; intervalo de 15 min; objetivo de 24 h'],
        ['Señales y predictores','26 señales; 187 variables numéricas y 4 categóricas permitidas'],
        ['Eventos',str(gen['failure_count'])+' fallos funcionales SIMULADOS; no historial industrial'],
        ['Control de entrega',f'{total:,}'.replace(',','.')+' controles superados; reproducción '+str(rep['identical_files'])+'/'+str(rep['compared_files'])+' archivos idénticos'],
        ['Entrenamiento','Pendiente. No se han entrenado XGBoost ni Isolation Forest.'],
    ],[118,381])
    p('Qué acredita esta versión','sub')
    p('Coherencia interna, disponibilidad temporal, reproducibilidad y relaciones físicas mínimas. No acredita calibración de Sestao, equivalencia con una caja real, anticipación de averías reales ni ahorro económico.')
    p('Fuente de la mejora: Informe_Investigacion_Sestao_SMS_Contraste_v3_1.pdf, especialmente páginas 10-14. El informe original se incluye sin cambios en docs.','small')

    page('Del hallazgo al cambio implementado','01')
    table(['Hallazgo / prioridad','Aplicación en v4.0','Alcance'],[
        ['Bloque confundido con bobina / P0','production_segment_id, contiguo por receta, estado y configuración','Aplicado; sin bobinas físicas'],
        ['Parámetros sin trazabilidad / P0','CSV con valor, unidad, fuente, fecha, equipo y estado de evidencia','Aplicado; valores físicos supuestos'],
        ['Contexto de laminación / P1','Caja lógica, espesor de entrada/salida, temperatura y velocidades de banda','Aplicado a una caja equivalente'],
        ['Carga y accionamiento / P1','Fuerza, par, potencia, eficiencia, tensión y corriente relacionadas','Aplicado; modelo cuasiestático'],
        ['Cambios de equipo / P1','Dominios con validez temporal; accionamiento, control y sensores versionados','Aplicado; cambio virtual, no obra real'],
        ['Contrato vibratorio / P1','RMS/curtosis; eje, montaje, frecuencia, banda y ventana explícitos','Aplicado; desconocidos no inventados'],
        ['Campañas y transitorios / P2','Trazabilidad de bloques de receta y estados operativos','Parcial; sin nueva resolución rápida'],
        ['Ensayos externos / P2','Protocolos separados para proceso, anomalías y laboratorio','Pendientes; sin transferir etiquetas'],
    ],[126,237,136])
    p('Por qué cambia la versión mayor','sub')
    p('Cambian el significado de la carga, la generación de corriente y velocidad, el número de señales y el conjunto de predictores. Las semillas son nuevas y se recalculan eventos, etiquetas y particiones. La v4.0 no debe concatenarse con v3.1 ni presentarse como una calibración sucesiva del mismo motor real.')
    p('Sestao y SMS aportan contexto tecnológico; el fabricante/modelo del motor concreto sigue sin acreditarse. Los campos de OEM y modelo reales se conservan nulos en configuración.','small')

    page('Modelo mecánico mínimo y sus límites','02')
    table(['Relación','Interpretación'],[
        ['h_entrada = h_salida / (1 - reducción)','Reducción entre 0,18 y 0,32. Ancho constante; sin ensanchamiento.'],
        ['Contacto = sqrt(R × reducción de espesor)','R en metros; convertir espesores de mm a m.'],
        ['Fuerza = tensión de fluencia × ancho × contacto × factor','Ley simplificada dependiente del grado y de temperatura de banda. No ajustada a datos reales.'],
        ['Par equivalente = 2 × fuerza × contacto × brazo relativo','Equivale al accionamiento de dos cilindros; no es par individual de cada cilindro.'],
        ['rpm_motor = transmisión × rpm_cilindro','Velocidades distintas. Banda = velocidad periférica × (1 + deslizamiento).'],
        ['Potencia mecánica = par_motor × omega_motor','Incluye transmisión y pérdidas auxiliares equivalentes. omega = 2π × rpm / 60.'],
        ['Potencia eléctrica = mecánica / eficiencia','I = potencia eléctrica / (sqrt(3) × tensión línea-línea × factor de potencia).'],
        ['Carga relativa = potencia mecánica / nominal demo','La nominal de 2.000 kW es un supuesto; no placa de Sestao.'],
    ],[219,280])
    p('Supuestos explícitos','sub')
    p('Radio de cilindro 0,35 m; tensión 3.300 V; factor de potencia 0,90; transmisión 6,0 o 5,7 según dominio; eficiencia de transmisión 0,97. Ningún valor se presenta como especificación OEM. La tabla completa está en docs/procedencia_parametros.csv.')
    p('Se conserva masa volumétrica bajo ancho y densidad constantes. No se calculan masa/longitud de bobina, dinámica de mordida, tensiones entre cajas, elasticidad ni resonancias. El paso interno sigue siendo 5 min: no existe una simulación rápida oculta.','small')

    page('Observaciones, verdad y configuración','03')
    table(['Capa','Uso correcto'],[
        ['data/telemetria','Señales observadas con ruido, defectos y llegada retrasada. Magnitudes geométricas y temperatura de banda nulas cuando no hay laminación.'],
        ['ml/features','Ventanas de 30 y 240 min y lectura vigente; únicamente datos disponibles en la decisión. Metadatos de receta/estado conocidos por supuesto.'],
        ['ml/targets','Fallo24h, censura, partición y selectores; separados de las entradas.'],
        ['sim_truth/fisica','Valores coherentes antes de defectos instrumentales y eficiencia efectiva. Auditoría privada, prohibida como predictor.'],
        ['sim_truth/estado_latente','Daño y estado de salud ocultos; no se observan en servicio.'],
        ['data/configuraciones','Intervalos de validez, versiones de accionamiento/control/sensores y política de mantenimiento.'],
    ],[151,348])
    p('Dos dominios experimentales','sub')
    p('El segundo comienza el día 183. Cambian transmisión, eficiencia nominal y ganancia de sensores. El daño no se reinicia. Es un cambio virtual instantáneo, sin atribuir una modernización a una fábrica real. Las ventanas se reinician al cambiar de configuración para evitar mezclar instrumentos.')
    p('Vibración sin adquisición inventada','sub')
    p('Se generan descriptores RMS y curtosis directamente. Frecuencia original, banda y ventana de adquisición son nulas; eje y montaje, no especificados. Los 300 segundos indican cadencia de salida, no frecuencia de una onda. No se pueden reconstruir espectros de alta frecuencia.')
    p('La física limpia satisface las identidades; la telemetría corrupta puede no hacerlo. No usar sus máximos brutos como límites físicos del motor. Los fines de segmentos y configuraciones son retrospectivos y no entran en predictores.','small')

    page('Controles ejecutados y reproducibilidad','04')
    table(['Batería','Superados','Fallidos'],[(name,x['passed'],x['failed']) for name,x in audit]+[('TOTAL',total,sum(x['failed'] for _,x in audit))],[325,87,87])
    p('Dos generaciones completas','sub')
    p(f"La reproducción con iguales semillas, configuración y dependencias produjo {rep['identical_files']} de {rep['compared_files']} archivos idénticos por SHA-256: todos los Parquet y el contrato de columnas ML. La segunda generación superó también sus controles de datos y causalidad.")
    p('Qué incluyen las pruebas','sub')
    p('Claves y cardinalidad; censura reconstruida independientemente; purga y episodios; prefijos causales y replay de llegada; ventanas por configuración; relaciones de velocidad, continuidad, par, potencia e intensidad; sensibilidad a ancho/temperatura/transmisión; independencia de fallos respecto a la inyección instrumental.')
    p('SQL y límites de ejecución','sub')
    p('18 tablas y 399 definiciones de columna. El parser aceptó el DDL y las funciones; se comprobaron relaciones en Parquet. No se ejecutó el servidor PostgreSQL/Neon ni Windows/Spyder. Las pruebas de fixtures no son resultados de rendimiento predictivo del dataset.')

    page('Particiones y fase de entrenamiento futura','05')
    parts=pd.read_csv(ROOT/'resultados/particiones.csv').groupby('partition')[['rows','usable_rows','positive_rows']].sum()
    table(['Partición','Decisiones','Utilizables','Positivas utilizables'],[[k,*[f'{int(v):,}'.replace(',','.') for v in parts.loc[k]]] for k in ['train','validation','test','stress','excluida']],[100,125,125,149])
    p('Reglas conservadas y versionadas','sub')
    p('R01-R12 mantienen separación temporal 60/20/20 y purga de 28 h; R13-R16 reservan escenarios de estrés. Las filas excluidas no son utilizables. y24 nulo significa censura o no elegibilidad y nunca debe convertirse en cero. Las reglas están en config/protocolo_preentrenamiento.json.')
    p('La futura preparación se ajustará exclusivamente dentro de train/fold. Hiperparámetros en folds temporales; umbrales solo en validation. Persistencia 3 de 5 decisiones; presupuesto de 1 falsa alerta por 1.000 horas operativas; aviso útil entre 1 y 24 h. Son decisiones de experimento, no garantías industriales.')
    p('Isolation Forest y evaluación','sub')
    p('Referencia principal observable; referencia ideal latente solo como sensibilidad. Un score de IF no es probabilidad de fallo24h. Conservar denominadores de eventos y horas operativas aunque haya abstenciones. Informar resultados por mundo, régimen y configuración; no hay varias cajas físicas para compararlas.')
    p('Se revisaron estructura y etiquetas de todas las particiones para auditar generación. No se calcularon scores predictivos ni se seleccionaron parámetros por resultados de test o estrés. La nueva cuenta de fallos simulados refleja otro generador/semillas, no una diferencia de fiabilidad real.','small')

    page('Uso de la entrega y decisiones pendientes','06')
    p('Inicio recomendado','sub')
    p('Extraer el ZIP completo. Instalar requirements_auditoria.txt en Python 3.12; configurar ese intérprete en Spyder. Ejecutar src/09_verificar_integridad.py antes de editar y src/00_empezar.py para una primera lectura. Los ejemplos CSV permiten inspección rápida; no sustituyen los Parquet completos.')
    table(['Documento / archivo','Para qué sirve'],[
        ['README.md','Inicio, estructura, comandos, límites y uso PostgreSQL opcional.'],
        ['docs/MODELO_FISICO.md','Ecuaciones, unidades, supuestos y dinámica omitida.'],
        ['docs/diccionario_datos.csv','Todas las columnas, tipos, unidades, rol y política de nulos.'],
        ['docs/procedencia_parametros.csv','Separación de decisiones, supuestos y desconocidos.'],
        ['docs/MIGRACION_v3_1_v4_0.md','Relación entre hallazgos, cambios y alcance.'],
        ['docs/ENSAYOS_EXTERNOS_PENDIENTES.md','Uso independiente de Nucor, TCM y bancos de rodamientos.'],
        ['src/10_reproducibilidad.py','Segunda generación en una carpeta nueva y comparación por huellas.'],
        ['SHA256.json','Integridad de los archivos de la entrega original.'],
    ],[224,275])
    p('Siguiente fase','sub')
    p('Entrenar y evaluar los modelos bajo el protocolo v4.0, manteniendo esta entrega congelada. Los experimentos externos siguen separados: Nucor para proceso, TCM para anomalías en frío, laboratorios para otras modalidades de rodamientos. No se han transferido sus etiquetas ni mezclado sus registros con Sestao.')
    p('La versión queda preparada para experimentación sintética. Para uso industrial harán falta identificación del equipo, adquisición real, historial de eventos/mantenimiento y validación externa. El entrenamiento solicitado permanece pendiente.','small')

    out=ROOT/'docs/Informe_Mejora_Dataset_v4_0.pdf'
    def footer(c,doc):
        c.setStrokeColor(HexColor('#cfdbdf'));c.line(48,42,547,42)
        c.setFont('Body',7);c.setFillColor(GRAY);c.drawString(48,29,'ACB / MOTOR Y RODAMIENTOS / v4.0 / 100 % SINTÉTICO')
        c.drawRightString(547,29,str(doc.page))
    SimpleDocTemplate(str(out),pagesize=(595.28,841.89),rightMargin=48,leftMargin=48,topMargin=45,bottomMargin=60,title='Mejora del dataset sintético - v4.0',author='Proyecto de Joseph').build(story,onFirstPage=footer,onLaterPages=footer)
    print(out)

if __name__=='__main__':main()
