"""Animación documental reproducible. No entrena modelos. Python + Pillow + NumPy + FFmpeg."""
from motion_engine import *
DATA=json.loads((R/'assets/chart_data.json').read_text())
NAME='Dataset_ACB_v3_1_Del_Simulador_al_Machine_Learning_1080p'

def card(im,x,y,w,h,label,title,body,col='cyan',size=38):
 panel(im,(x,y,x+w,y+h),col);txt(im,label,x+28,y+24,24,True,col,maxw=w-56)
 yy=y+79
 for line in wrap(title,size,w-56):txt(im,line,x+28,yy,size,True,maxw=w-56);yy+=size+11
 if body:
  yy=max(yy+20,y+h-40-len(wrap(body,27,w-56))*35)
  for line in wrap(body,27,w-56):txt(im,line,x+28,yy,27,color='muted',maxw=w-56);yy+=35

def badge(im,text,x,y,col='cyan',w=500):
 d=ImageDraw.Draw(im);d.rounded_rectangle((x,y,x+w,y+54),radius=14,fill='#183441',outline=C[col],width=1);txt(im,text,x+w/2,y+12,24,True,col,maxw=w-28,center=True)

def flow(im,labels,y=490):
 d=ImageDraw.Draw(im);n=len(labels);gap=48;w=(1760-gap*(n-1))/n
 for j,(a,b) in enumerate(labels):
  x=80+j*(w+gap);card(im,x,y,w,220,f'{j+1:02d}',a,b,['cyan','purple','amber','cyan'][j%4],34)
  if j<n-1:arrow(d,(x+w+8,y+110),(x+w+gap-8,y+110),'muted')

def cards3(im,items,y=345,h=445,size=47):
 for j,(a,b,c,col) in enumerate(items):card(im,80+j*600,y,560,h,a,b,c,col,size)

def cards4(im,items,y=330,h=250,size=39):
 for j,(a,b,c,col) in enumerate(items):card(im,80+(j%2)*900,y+(j//2)*280,860,h,a,b,c,col,size)

def mill(im,t,stopped=False,y=580):
 d=ImageDraw.Draw(im);d.rounded_rectangle((110,y-15,1710,y+15),radius=8,fill='#ed713e');d.rectangle((110,y-4,1710,y+4),fill='#ffd48a')
 for j,x in enumerate([380,730,1080]):
  d.rounded_rectangle((x-94,y-190,x+94,y+190),radius=16,outline='#376071',width=14)
  for yy in [y-69,y+69]:
   d.ellipse((x-61,yy-61,x+61,yy+61),fill='#153442',outline=C['cyan'],width=5);a=(0 if stopped else t*1.4)*(1 if yy<y else -1)
   for k in range(3):
    an=a+k*math.tau/3;d.line((x,yy,x+48*math.cos(an),yy+48*math.sin(an)),fill='#6b9ba8',width=4)
  txt(im,f'CAJA {j+1}',x,y+225,24,True,'muted',center=True)
 for k in range(16):
  x=120+((k*100+(0 if stopped else t*100))%1560);d.line((x,y-6,x+32,y-6),fill='#ffe6ac',width=3)
 for radius in range(40,130,13):d.ellipse((1690-radius,y-radius,1690+radius,y+radius),outline=C['amber'],width=5)
 txt(im,'BANDA CALIENTE',160,y-245,28,True,'amber');txt(im,'BOBINA',1690,y+225,27,True,'amber',center=True)

def series(im,keys,box,u,unit):
 x0,y0,x1,y1=box;d=ImageDraw.Draw(im);rows=DATA['telemetry'];vals=[r[k] for r in rows for k in keys if r[k] is not None];lo=math.floor(min(vals)/5)*5;hi=math.ceil(max(vals)/5)*5
 if hi==lo:hi=lo+1
 for frac in [0,.5,1]:
  y=y1-(y1-y0)*frac;d.line((x0,y,x1,y),fill=C['line'],width=1);txt(im,f'{lo+(hi-lo)*frac:g}',x0-70,y-12,22,color='muted',maxw=60)
 txt(im,unit,x0-70,y0-38,22,True,'muted');count=max(2,min(len(rows),int(len(rows)*ease((u-.5)/5))))
 for k,col in zip(keys,['cyan','purple']):
  seg=[]
  for j,r in enumerate(rows[:count]):
   if r[k] is None:
    if len(seg)>1:d.line(seg,fill=C[col],width=3)
    seg=[]
   else:seg.append((x0+(x1-x0)*j/len(rows),y1-(r[k]-lo)/(hi-lo)*(y1-y0)))
  if len(seg)>1:d.line(seg,fill=C[col],width=3)
 for h in [0,6,12,18,24]:txt(im,f'{h:02d} h',x0+(x1-x0)*h/24,y1+15,22,color='muted',center=True)

def frame(t):
 idx=min(len(SCENES)-1,int(np.searchsorted(STARTS,t,side='right')-1));s=SCENES[idx];u=t-STARTS[idx];q=ease((u-.4)/2.8);im=base(idx,t);d=ImageDraw.Draw(im);kind=s['kind']
 if kind not in ['opening','closing']:heading(im,s,u)
 if kind=='opening':
  motor(im,1470,520,t,1.24);txt(im,'DEL SIMULADOR AL MACHINE LEARNING',80,230,28,True,'amber',maxw=1180)
  for j,tx in enumerate(['Del dato al','mantenimiento','anticipado.']):txt(im,tx,80,300+j*103,90,True,maxw=1250,alpha=ease((u-j*.2)/.9))
  badge(im,'DATASET v3.1 · MOTOR + RODAMIENTOS',80,665,w=1020);txt(im,'Tren de laminación en caliente · bobinas de metal',85,769,30,color='muted',maxw=1160);txt(im,'Representación conceptual',1470,830,22,color='muted',center=True)
 elif kind=='mill':
  mill(im,u,stopped=u>7);badge(im,'PARADA → FLUJO INTERRUMPIDO' if u>7 else 'MOVIMIENTO · CARGA · TEMPERATURA',500,300,'red' if u>7 else 'cyan',920)
  txt(im,'Foco del proyecto: el conjunto motor + rodamientos de un accionamiento',960,861,29,True,center=True,maxw=1750)
 elif kind=='versions':
  vals=[('v2','BASE GENERAL','ACB_CSP_Sintetico_v2','Referencia para contexto y exploración.','muted'),('v3','ALCANCE ESPECÍFICO','Motor + rodamientos','Componentes, señales, simulador y etiquetas.','purple'),('v3.1','CORRECCIÓN AUDITADA','Paquete reproducible','Coherencia temporal y protocolo congelado.','cyan')]
  for j,(v,l,a,b,c) in enumerate(vals):
   x=80+j*600;card(im,x,350,560,450,l,a,b,c,38);txt(im,v,x+30,530,112,True,c,alpha=ease((u-.5-j*.4)/1.4),maxw=480)
   if j<2:arrow(d,(x+565,575),(x+594,575),'muted')
  txt(im,'El detalle de la v3.1 se verifica en el ZIP; v2 y v3 son antecedentes del proyecto.',960,853,25,color='muted',center=True,maxw=1740)
 elif kind=='package':
  vals=[('01','GENERADOR','Configuración, semillas y simulación.','cyan'),('02','DATOS','Telemetría, eventos y tablas para ML.','purple'),('03','DICCIONARIO','Definiciones, unidades y roles.','amber'),('04','SQL','Relaciones y lectura por disponibilidad.','cyan'),('05','VALIDACIONES','Pruebas, reproducción y manifiesto.','purple'),('06','PROTOCOLO','Comparación y reglas antes de entrenar.','amber')]
  for j,(n,a,b,c) in enumerate(vals):card(im,80+(j%3)*600,330+(j//3)*280,560,250,n,a,b,c,35)
 elif kind=='generator':
  flow(im,[('Operación','Carga, régimen y ambiente'),('Degradación','Evolución progresiva y variabilidad'),('Fallo y reparación','Eventos y restauración parcial'),('Medición','Ruido, pérdidas y retrasos')],345)
  for j,(n,lab) in enumerate([('16','mundos alternativos'),('365','días por mundo'),('1.681.920','filas de telemetría')]):
   x=80+j*600;txt(im,n,x+270,642,83,True,['cyan','purple','amber'][j],center=True,maxw=550);txt(im,lab,x+270,746,28,color='muted',center=True,maxw=550)
  txt(im,'Un conjunto lógico en 16 simulaciones: no son 16 motores reales de ACB.',960,854,29,True,center=True,maxw=1750)
 elif kind=='signals':
  panel(im,(80,320,640,882),'cyan');motor(im,360,490,t,.57);txt(im,'MOTOR + 2 APOYOS',360,658,34,True,'cyan',center=True,maxw=500)
  lines(im,['DE: lado de accionamiento','NDE: lado opuesto','Temperatura · vibración','Corriente · carga · velocidad'],120,720,26,gap=12,maxw=480)
  txt(im,'R01 · 01/01/2024 · UTC · observaciones cada 5 min',735,303,23,color='muted',maxw=1080)
  series(im,['bearing_temperature_de_c','bearing_temperature_nde_c'],(800,390,1800,550),u,'°C');series(im,['vibration_de_mm_s','vibration_nde_mm_s'],(800,680,1800,815),u,'mm/s')
  txt(im,'DE',1300,864,23,True,'cyan');txt(im,'NDE',1420,864,23,True,'purple');txt(im,'Valores sintéticos observados',800,864,23,color='muted',maxw=470)
 elif kind=='quality':
  cards3(im,[('MEDIR','5 min','Cadencia de telemetría.','cyan'),('EVALUAR','15 min','Una decisión cada tres posiciones.','purple'),('ANTICIPAR','24 h','Horizonte objetivo del fallo.','amber')],325,250,70)
  d.line((150,673,1760,673),fill=C['line'],width=4)
  for j in range(13):
   x=150+j*134;bad=j in [4,5];rr=13 if j%3==0 else 8;d.ellipse((x-rr,673-rr,x+rr,673+rr),outline=C['red'] if bad else C['cyan'],fill=None if bad else C['cyan'],width=3)
  txt(im,'HUECOS',752,714,24,True,'red',center=True);badge(im,'Solo datos ya disponibles',80,793,'cyan',530);badge(im,'Cobertura esencial ≥ 80 %',690,793,'purple',550);badge(im,'Sin calidad → abstención',1320,793,'amber',520)
 elif kind=='fixes':
  cards4(im,[('CORRECCIÓN 1','PLANES VERSIONADOS','Un aplazamiento no revela una fecha futura.','cyan'),('CORRECCIÓN 2','REEMPLAZOS COHERENTES','Cambiar un componente no aumenta su daño.','purple'),('CORRECCIÓN 3','EXCLUSIONES EFECTIVAS','Las filas excluidas no entran en entrenamiento.','amber'),('CORRECCIÓN 4','ESCENARIOS MÁS VARIADOS','Vida larga, calendario, ruido y pérdidas.','cyan')],335,245,34)
 elif kind=='dictionary':
  cards3(im,[('DICCIONARIO','256 definiciones','En 16 tablas. No son 256 predictores.','cyan'),('CONTRATO DE ENTRADA','113 predictores','110 numéricos + 3 categóricos, antes de codificar.','purple'),('PROTECCIÓN TEMPORAL','Sin información futura','Lista explícita de variables admitidas.','amber')],330,480,48)
  txt(im,'Nombre · tipo · unidad',110,530,31,True,maxw=500);txt(im,'Rol · nulos · uso permitido',110,585,29,color='muted',maxw=500)
  txt(im,'Ventanas: 30 y 240 min',710,530,31,True,maxw=500);txt(im,'Imputación dentro de train',710,585,29,color='muted',maxw=500)
  lines(im,['Fuera: salud interna','Fuera: fallo futuro','Fuera: selector IF'],1310,540,29,color='white',gap=18,maxw=480)
  txt(im,'Una variable útil debe existir y estar disponible en el instante de decidir.',960,853,30,True,center=True,maxw=1760)
 elif kind=='sql':
  cards3(im,[('DATOS','acb_motor_v3_1','Activos, señales, planes y servicios.','cyan'),('VERDAD RESTRINGIDA','acb_motor_v3_1_truth','Salud interna y objetivos retrospectivos.','amber'),('LECTURA POR INSTANTE','acb_motor_v3_1_api','Funciones as-of: lo conocido hasta t.','purple')],350,350,33)
  badge(im,'run_id + assembly_id + timestamp',80,765,'cyan',920);badge(im,'PostgreSQL 16.2 · prueba local',1060,765,'purple',780);txt(im,'Servicio: su resultado se revela cuando está disponible, no antes.',960,853,29,True,center=True,maxw=1750)
 elif kind=='labels':
  x0,x1=530,1540
  for j,(lab,state,col,event) in enumerate([('Fallo observado','y24 = 1','red',.68),('24 h completas sin fallo','y24 = 0','cyan',None),('Preventivo o fin antes de 24 h','y24 = nulo','amber',.57)]):
   y=405+j*170;txt(im,lab,80,y-18,31,True,maxw=420);d.line((x0,y,x1,y),fill=C['line'],width=6);d.ellipse((x0-8,y-8,x0+8,y+8),fill=C['white']);txt(im,'t',x0,y+28,23,center=True,color='muted');txt(im,'+24 h',x1,y+28,23,center=True,color='muted')
   end=x1 if event is None else x0+(x1-x0)*event;d.line((x0,y,x0+(end-x0)*q,y),fill=C[col],width=6)
   if event:d.rectangle((end-7,y-25,end+7,y+25),fill=C[col])
   txt(im,state,1600,y-25,40,True,col,maxw=250)
  txt(im,'Ejemplos conceptuales de etiquetado · solo estados elegibles',960,859,26,color='muted',center=True)
 elif kind=='splits':
  txt(im,'12 MUNDOS BASE · REPARTO NOMINAL DEL TIEMPO',80,320,28,True,'muted');x=80
  for frac,col,label in [(.6,'cyan','60 % · TRAIN'),(.2,'purple','20 % · VALIDACIÓN'),(.2,'amber','20 % · TEST')]:
   w=1760*frac;d.rounded_rectangle((x,378,x+w-12,490),radius=14,fill=C[col]);txt(im,label,x+(w-12)/2,417,30,True,'bg',center=True,maxw=w-30);x+=w
  for j,(a,b,c) in enumerate([('179.998','train','cyan'),('44.590','validación','purple'),('56.164','test','amber'),('101.477','estrés','cyan')]):
   x=80+j*450;txt(im,a,x+210,565,61,True,c,center=True,maxw=420);txt(im,b,x+210,644,30,color='muted',center=True)
  txt(im,'FILAS UTILIZABLES DESPUÉS DE LOS FILTROS',960,714,26,True,'muted',center=True);badge(im,'4 mundos de estrés reservados',80,795,'cyan',790);badge(im,'3 folds internos expansivos en train',930,795,'purple',910)
 elif kind=='scenarios':
  txt(im,'Fracción de tiempo en estado normal interno · dato de auditoría',80,310,28,True,'muted',maxw=1770);x0,x1=330,1730;ys=361;bh=24;gap=29
  for pct in [0,25,50,75,100]:
   x=x0+(x1-x0)*pct/100;d.line((x,ys-8,x,ys+15*gap+bh),fill=C['line'],width=1);txt(im,f'{pct} %',x,832,22,color='muted',center=True)
  for j,r in enumerate(DATA['scenarios']):
   y=ys+j*gap;col='purple' if j<6 else 'cyan' if j<12 else 'amber';txt(im,r['run_id'],160,y-3,23,True,col,maxw=140);width=(x1-x0)*r['normal_fraction']*ease((u-.2-j*.06)/2.2)
   if width>0:d.rounded_rectangle((x0,y,x0+width,y+bh-5),radius=4,fill=C[col])
   txt(im,f"{100*r['normal_fraction']:.1f} %".replace('.',','),x0+width+15,y-3,21,color='white',maxw=130)
  txt(im,'R01–06: degradación',80,877,24,True,'purple');txt(im,'R07–12: vida larga',670,877,24,True,'cyan');txt(im,'R13–16: estrés',1260,877,24,True,'amber')
 elif kind=='proof':
  vals=[705,91,44,762,64,27];labs=['Datos, etiquetas y causalidad','Catálogo y segmentos','Pruebas del protocolo','Correcciones y referencias','Llegada de datos','PostgreSQL local']
  for j,(n,lab) in enumerate(zip(vals,labs)):
   y=336+j*80;txt(im,lab,80,y+6,29,maxw=580);d.rounded_rectangle((675,y,1275,y+38),radius=8,fill=C['panel']);p=ease((u-.4-j*.15)/2.5)
   if p>0:d.rounded_rectangle((675,y,675+600*n/762*p,y+38),radius=8,fill=C['cyan'] if j%2==0 else C['purple'])
   txt(im,str(round(n*p)),1320,y,36,True,maxw=140)
  card(im,1480,325,360,270,'COMPROBACIONES','1.693','0 fallidas','cyan',78);card(im,1480,625,360,215,'REPRODUCCIÓN','77 / 77','Archivos idénticos','purple',54)
  txt(im,'Además: 168 archivos del manifiesto comprobados al preparar este vídeo; 0 diferencias.',80,865,25,color='muted',maxw=1750)
 elif kind=='uncertainty':
  cards3(im,[('EVENTOS SINTÉTICOS','404 fallos','Ocurridos en 16 mundos alternativos del mismo conjunto lógico.','cyan'),('MUESTRAS PEQUEÑAS','7 estratos','Combinaciones de partición y modo con menos de 20 sucesos: solo descriptivas.','amber'),('PROTOCOLO ESTADÍSTICO','IC del 95 %','2.000 remuestreos de mundos completos, pareados entre modelos.','purple')],335,470,62)
  txt(im,'Repetir filas correlacionadas no crea evidencia industrial independiente.',960,851,32,True,center=True,maxw=1750)
 elif kind=='xgboost':
  txt(im,'ESQUEMA DEL FUTURO ENTRENAMIENTO · SIN RESULTADOS PREDICTIVOS',80,310,26,True,'muted',maxw=1750);card(im,80,395,410,360,'ENTRENAMIENTO','Variables + y24','Solo train y etiqueta conocida.','cyan',43)
  for j,cx in enumerate([750,1120]):
   root=(cx,430);children=[(cx-90,550),(cx+90,550)];arrow(d,root,children[0],'purple');arrow(d,root,children[1],'purple')
   for child in children:
    for delta in [-44,44]:arrow(d,child,(child[0]+delta,670),'purple',3)
   for xx,yy in [root]+children:d.rounded_rectangle((xx-40,yy-25,xx+40,yy+25),radius=12,fill=C['panel'],outline=C['purple'],width=3)
   for xx in [cx-134,cx-46,cx+46,cx+134]:d.ellipse((xx-12,658,xx+12,682),fill=C['purple'])
   txt(im,f'Árbol {j+1}',cx,720,29,True,'purple',center=True)
  txt(im,'+',934,540,55,True,'muted',center=True);arrow(d,(500,565),(600,565));arrow(d,(1280,565),(1375,565));card(im,1390,395,450,360,'SALIDA PREVISTA','P(fallo ≤ 24 h)','Estimar, comprobar y evaluar calibración.','amber',47)
  txt(im,'Árboles sucesivos corrigen errores del conjunto. La probabilidad deberá validarse.',960,845,30,True,center=True,maxw=1750)
 elif kind=='isolation':
  panel(im,(80,330,930,850),'purple');rng=np.random.default_rng(12);pts=rng.normal([470,590],[115,75],(100,2))
  for x,y in pts:d.ellipse((x-4,y-4,x+4,y+4),fill=C['cyan'])
  d.ellipse((790,390,810,410),fill=C['amber']);txt(im,'Punto aislado',750,348,27,True,'amber',center=True)
  for a,b,delay in [((720,370),(720,800),1),((130,470),(720,470),2),((450,470),(450,800),3),((130,670),(450,670),4)]:
   p=ease((u-delay)/1.4)
   if p>0:d.line([a,(a[0]+(b[0]-a[0])*p,a[1]+(b[1]-a[1])*p)],fill=C['purple'],width=3)
  txt(im,'Particiones conceptuales · no es un modelo ajustado',505,812,24,color='muted',center=True,maxw=800)
  card(im,990,330,850,320,'REFERENCIA PRINCIPAL','12.494 filas candidatas','Selección observable de train: servicio conocido, 4–24 h operativas, cobertura completa y calidad ok.','cyan',49)
  lines(im,['Pocos cortes para aislar → mayor anomalía','La referencia puede contener degradación.','La selección ideal queda como sensibilidad.'],1020,700,29,color='white',gap=22,maxw=790)
 elif kind=='benchmark':
  flow(im,[('Train','Elegir ajustes en folds temporales'),('Validación','Elegir umbrales de aviso'),('Congelar','Modelo + preparación + política'),('Test y estrés','Evaluar las decisiones fijadas')],330)
  card(im,80,615,860,250,'COMPARADORES OBLIGATORIOS','Constante · regla · regresión logística','El modelo debe aportar valor frente a alternativas simples.','cyan',34);card(im,980,615,860,250,'CRITERIO PREDEFINIDO · NO RESULTADO','≥ 5 puntos de sensibilidad','Frente a cada comparador, IC pareado positivo y mismo límite de falsas alertas.','amber',39)
 elif kind=='policy':
  txt(im,'ABRIR: INSTANTE ACTUAL ALTO + 3 DE LAS ÚLTIMAS 5 POSICIONES',80,316,27,True,'muted',maxw=1760)
  for j,(a,b,col) in enumerate([('−60 min','alto','amber'),('−45 min','bajo','cyan'),('−30 min','sin dato','muted'),('−15 min','alto','amber'),('ahora','alto','amber')]):
   x=80+j*355;panel(im,(x,380,x+320,570),col);txt(im,a,x+160,410,28,True,center=True);txt(im,b,x+160,480,39,True,col,center=True,maxw=285)
  for j,(a,b,c) in enumerate([('1–24 h','Anticipación útil','cyan'),('≤ 1 / 1.000 h','Falsas alertas operativas','amber'),('1 fallo','Se cuenta una vez','purple')]):
   x=80+j*600;txt(im,a,x+270,642,61,True,c,center=True,maxw=540);txt(im,b,x+270,726,28,color='muted',center=True,maxw=550)
  txt(im,'Cinco posiciones abarcan 60 min. Los huecos no votan ni se convierten en normalidad.',960,842,29,True,center=True,maxw=1740)
 elif kind=='action':
  flow(im,[('Observar','Señales y calidad disponibles'),('Priorizar','Score, aviso y contexto'),('Revisar','Inspección de profesionales'),('Actuar y registrar','Intervención y resultado')],360)
  d.line((350,685,1570,685),fill=C['line'],width=3);arrow(d,(1570,685),(1570,605),'muted');arrow(d,(350,685),(350,605),'muted');txt(im,'Retroalimentar el proceso con hechos observados',960,727,43,True,'cyan',center=True,maxw=1750);txt(im,'Objetivo de negocio: anticipar mantenimiento y reducir paradas no planificadas.',960,827,30,color='white',center=True,maxw=1750)
 elif kind=='boundaries':
  cards3(im,[('SÍ PERMITE','Ensayar el método','Datos, código, comparación y aplicación demostradora.','cyan'),('NO ACREDITA','Rendimiento real','Predicción, fiabilidad, ahorro y horas de parada evitadas.','amber'),('SIGUIENTE VALIDACIÓN','Máquina real','Datos, revisión técnica y un piloto medido serían necesarios.','purple')])
  txt(im,'Pendientes también: Windows / Spyder, Neon y dashboard. No se ha entrenado ningún modelo.',960,847,27,True,'muted',center=True,maxw=1760)
 elif kind=='preflight':
  cards4(im,[('VERIFICAR','Manifiesto y pruebas','Repetir controles y tamaños de referencias.','cyan'),('CONGELAR','Software y configuración','Versiones, semillas, entradas y folds.','purple'),('REGISTRAR','Cada decisión de ajuste','Train ajusta; validación fija umbrales.','amber'),('CONSERVAR','Modelo y política','Guardar artefactos antes de evaluar test.','cyan')])
  txt(im,'Test y estrés ya se inspeccionaron por calidad; no han elegido ajustes predictivos.',960,874,25,color='muted',center=True,maxw=1750)
 elif kind=='closing':
  motor(im,1510,520,t,1.13);txt(im,'CONOCIMIENTO · DESARROLLO · IMPACTO',80,235,28,True,'amber',maxw=1200)
  for j,line in enumerate(['Preparado para','aprender.','Preparado para','comprobar.']):txt(im,line,80,300+j*93,78,True,'cyan' if j%2 else 'white',maxw=1180,alpha=ease((u-.2-j*.16)/.8))
  badge(im,'SIGUIENTE FASE: XGBOOST + ISOLATION FOREST',80,733,'cyan',1150);txt(im,'ACB_Motor_Rodamientos_Sintetico_v3_1',80,839,29,color='muted',maxw=1720)
 caption(im,s,u);fade=min(ease(u/.5),ease((s['duration']-u)/.45))
 if fade<1:im=Image.blend(Image.new('RGB',(W,H),C['bg']),im,fade)
 return im

def subtitles():
 def stamp(t):return f'{int(t)//3600:02d}:{(int(t)//60)%60:02d}:{int(t)%60:02d},000'
 rows=[f'{i+1}\n{stamp(STARTS[i])} --> {stamp(STARTS[i+1])}\n'+s['title'].replace('\n',' ')+'\n'+s['caption']+'\n' for i,s in enumerate(SCENES)]
 (R/f'output/{NAME}.srt').write_text('\n'.join(rows),encoding='utf-8')

def render():
 (R/'output').mkdir(exist_ok=True);audio_path=audio();subtitles();output=R/f'output/{NAME}.mp4'
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(audio_path),'-c:v','libx264','-preset','fast','-threads','4','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-t',str(DURATION),'-metadata','title=Dataset ACB v3.1: del simulador al machine learning','-metadata','comment=Animación documental basada en el ZIP completo v3.1. Datos sintéticos. Sin entrenamiento ni validación industrial.',str(output)]
 with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
  for i in range(DURATION*FPS):
   proc.stdin.write(frame(i/FPS).tobytes())
   if i%(FPS*10)==0:print(f'{i/FPS:.0f}/{DURATION} segundos',flush=True)
  proc.stdin.close();code=proc.wait()
  if code:raise RuntimeError(f'FFmpeg {code}')
 print(output,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');a=p.parse_args()
 if a.preview:
  (R/'qa').mkdir(exist_ok=True);sheet=Image.new('RGB',(1920,math.ceil(len(SCENES)/3)*360),C['bg'])
  for i,s in enumerate(SCENES):
   im=frame(float(STARTS[i])+s['duration']*.65);im.save(R/f'qa/escena_{i+1:02d}.png');sheet.paste(im.resize((640,360)),((i%3)*640,(i//3)*360))
  sheet.save(R/'qa/contact_sheet.jpg');print('Previews',len(SCENES),'duración',DURATION)
 else:render()
