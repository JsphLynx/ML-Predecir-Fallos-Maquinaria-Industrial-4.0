"""Animación reproducible del informe. Gráficos documentales sin redibujar valores.
Python 3.12 + Pillow + NumPy; FFmpeg en PATH. Sin modelos, APIs ni imágenes generadas.
"""
from pathlib import Path
import json, math, subprocess, sys, argparse, functools, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R=Path(__file__).resolve().parent
W,H,FPS=1920,1080,30
SCENES=json.loads((R/'storyboard.json').read_text())
STARTS=np.r_[0,np.cumsum([s['duration'] for s in SCENES])];DURATION=int(STARTS[-1])
C={'bg':'#07121e','panel':'#102435','line':'#244758','white':'#f2f6fa','muted':'#9eb6c4','cyan':'#4ee2cf','amber':'#edbd61','purple':'#ad9bf5','red':'#f07f86'}
FONT_DIR=(R/'assets/fonts') if (R/'assets/fonts').exists() else Path('/usr/share/fonts/truetype/dejavu')
@functools.lru_cache(None)
def font(size,bold=False,mono=False):
 name='DejaVuSansMono.ttf' if mono else 'DejaVuSansCondensed-Bold.ttf' if bold else 'DejaVuSans.ttf'
 return ImageFont.truetype(str(FONT_DIR/name),size)
def rgb(c):return tuple(bytes.fromhex(c.lstrip('#')))
def ease(x):x=max(0,min(1,x));return 1-(1-x)**3
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def mix(a,b,p):return tuple(int(x*(1-p)+y*p) for x,y in zip(rgb(a),rgb(b)))
@functools.lru_cache(maxsize=1800)
def glyph(text,size,bold=False,color='white',maxw=1800,mono=False):
 color=C.get(color,color);f=font(size,bold,mono)
 while f.getlength(text)>maxw and size>16:size-=1;f=font(size,bold,mono)
 box=f.getbbox(text);im=Image.new('RGBA',(math.ceil(f.getlength(text))+6,size+14),(0,0,0,0));ImageDraw.Draw(im).text((0,-box[1]+2),text,font=f,fill=color)
 return im

def txt(im,text,x,y,size=38,bold=False,color='white',maxw=1700,alpha=1,center=False,mono=False):
 g=glyph(str(text),size,bold,color,maxw,mono)
 if alpha<1:g=g.copy();g.putalpha(g.getchannel('A').point(lambda v:int(v*max(0,alpha))))
 if center:x-=g.width/2
 im.paste(g,(int(x),int(y)),g)

def lines(im,arr,x,y,size=34,color='muted',gap=12,maxw=1700,bold=False):
 for j,text in enumerate(arr):txt(im,text,x,y+j*(size+gap),size,bold,color,maxw)
def wrap(text,size,maxw):
 out=[];cur=''
 for word in text.split():
  test=(cur+' '+word).strip()
  if font(size).getlength(test)>maxw and cur:out.append(cur);cur=word
  else:cur=test
 if cur:out.append(cur)
 return out

def panel(im,box,accent=None):
 d=ImageDraw.Draw(im);d.rounded_rectangle(tuple(map(int,box)),radius=24,fill=C['panel'],outline=C['line'],width=2)
 if accent:d.rounded_rectangle((box[0]+2,box[1]+20,box[0]+6,box[3]-20),radius=2,fill=C[accent])
def arrow(d,a,b,color='cyan',width=4):
 col=C.get(color,color);d.line([a,b],fill=col,width=width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);l=13
 d.polygon([b,(b[0]-l*math.cos(ang-.5),b[1]-l*math.sin(ang-.5)),(b[0]-l*math.cos(ang+.5),b[1]-l*math.sin(ang+.5))],fill=col)

def make_bg():
 y,x=np.mgrid[0:H,0:W];g=np.exp(-(((x-1450)/1000)**2+((y-240)/650)**2))
 a=np.zeros((H,W,3),np.uint8)
 for k,(b,v) in enumerate(zip((6,15,26),(7,22,29))):a[:,:,k]=b+g*v
 im=Image.fromarray(a);d=ImageDraw.Draw(im)
 for x0 in range(-200,2200,100):d.line([(W/2,500),(x0,H)],fill='#142c3b',width=1)
 for y0 in [720,800,900,1020]:d.line([(0,y0),(W,y0)],fill='#142c3b',width=1)
 return im
BG=make_bg();RNG=np.random.default_rng(42);PART=RNG.uniform([50,160],[1870,900],(38,2))
ORIGINAL=Image.open(R/'assets/grafico_original_0.png').convert('RGB')
HEALTH=ORIGINAL.crop((0,0,1530,558)).resize((1660,605),Image.Resampling.LANCZOS)
RATES=ORIGINAL.crop((0,558,1530,1071)).resize((1740,583),Image.Resampling.LANCZOS)

def motor(im,cx,cy,t,scale=1):
 d=ImageDraw.Draw(im);s=scale
 # Stylized assembly, not an engineering drawing.
 for rad,col,w in [(232,'#183c4d',2),(204,'#305564',3),(172,C['cyan'],3),(107,'#60858d',2),(53,C['cyan'],4)]:
  rr=rad*s;d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=col,width=w)
 for j in range(12):
  a=j*math.tau/12+t*.22;px=cx+138*s*math.cos(a);py=cy+138*s*math.sin(a);rr=23*s
  d.ellipse((px-rr,py-rr,px+rr,py+rr),fill='#1b3c4b',outline=C['cyan'],width=2)
 for j in range(32):
  a=j*math.tau/32;d.line([(cx+182*s*math.cos(a),cy+182*s*math.sin(a)),(cx+195*s*math.cos(a),cy+195*s*math.sin(a))],fill='#638493',width=2)
 a=t*.8;d.line([(cx,cy),(cx+85*s*math.cos(a),cy+85*s*math.sin(a))],fill=C['amber'],width=5)
 d.arc((cx-225*s,cy-225*s,cx+225*s,cy+225*s),start=(t*30)%360,end=(t*30)%360+110,fill=C['cyan'],width=6)

def base(index,t):
 im=BG.copy();d=ImageDraw.Draw(im)
 for j,(x,y) in enumerate(PART):
  px=(x+t*(4+j%5))%W;py=y+10*math.sin(t*.3+j)
  d.ellipse((px,py,px+2,py+2),fill='#386477')
 txt(im,'INDUSTRIA 4.0',80,46,23,True,'cyan');txt(im,'ACB / MOTOR + RODAMIENTOS',340,46,22,color='muted')
 txt(im,'AUDITORÍA  v3.1',1840,46,23,True,'white',center=False) if False else None
 txt(im,f'{index+1:02d} / 14',1755,46,23,mono=True)
 d.line((80,93,1840,93),fill=C['line'],width=2)
 d.rectangle((80,93,80+1760*(t/DURATION),95),fill=C['cyan'])
 txt(im,SCENES[index]['chapter'],80,122,23,True,'cyan')
 txt(im,'100 % SINTÉTICO  ·  SIN MODELOS ENTRENADOS',80,1016,20,color='muted')
 txt(im,SCENES[index]['source'],1840-glyph(SCENES[index]['source'],18).width,1019,18,color='muted')
 return im

def heading(im,s,u):
 alpha=ease(u/.7);yy=184+24*(1-alpha)
 for j,line in enumerate(s['title'].split('\n')):txt(im,line,80,(175 if s['kind']=='health' else yy)+j*86,54 if s['kind']=='health' else 68,True,maxw=1750,alpha=alpha)

def caption(im,s,u):
 d=ImageDraw.Draw(im);d.rounded_rectangle((80,913,1840,985),radius=16,fill='#0c2030',outline='#1a3c4d',width=1)
 rows=wrap(s['caption'],29,1680);y=932 if len(rows)==1 else 920
 for j,line in enumerate(rows):txt(im,line,110,y+j*33,29,color='white',maxw=1680)

def frame(t):
 idx=min(len(SCENES)-1,int(np.searchsorted(STARTS,t,side='right')-1));s=SCENES[idx];u=t-STARTS[idx];q=ease((u-.5)/2.6);im=base(idx,t);d=ImageDraw.Draw(im)
 kind=s['kind']
 if kind not in ['hero','outro']:heading(im,s,u)
 if kind=='hero':
  motor(im,1450,527,t,1.2)
  txt(im,'ANTES DE ENTRENAR',85,236,27,True,'amber',alpha=ease(u/.8))
  for j,a in enumerate(['Antes de predecir,','hay que poder','confiar.']):txt(im,a,80,306+j*102,82,True,maxw=1170,alpha=ease((u-j*.22)/.8))
  txt(im,'DE LA v3 A LA v3.1',85,668,38,True,'cyan',alpha=ease((u-1)/.7))
  txt(im,'Cambios · gráficos · evidencias · límites',85,738,31,color='muted',maxw=1120)
  txt(im,'Esquema conceptual del conjunto',1450,820,23,color='muted',center=True)
 elif kind=='cadence':
  vals=[('5','min','TELEMETRÍA','Medir'),('15','min','DECISIONES','Evaluar'),('24','h','HORIZONTE','Anticipar')]
  for j,(n,unit,label,verb) in enumerate(vals):
   x=80+j*600;p=ease((u-.4-j*.25)/1.3);panel(im,(x,340,x+560,735),['cyan','purple','amber'][j])
   txt(im,label,x+35,375,27,True,'muted');txt(im,n,x+35,440,137,True,['cyan','purple','amber'][j],alpha=p)
   txt(im,unit,x+230,510,50,color='white');txt(im,verb,x+35,651,40,True)
  for j in range(13):
   x=180+j*128;y=830;col='cyan' if j%3 else 'amber';rr=8 if j%3 else 14;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=C[col] if q>j/13 else C['line'])
  txt(im,'Una decisión cada tres observaciones de 5 min',960,856,27,color='muted',center=True)
 elif kind=='scale':
  vals=[(1681920,'REGISTROS DE TELEMETRÍA','cyan'),(560640,'DECISIONES','purple'),(404,'FALLOS SIMULADOS','amber'),(16,'MUNDOS ALTERNATIVOS','cyan')]
  for j,(n,lab,col) in enumerate(vals):
   x=80+(j%2)*900;y=330+(j//2)*275;panel(im,(x,y,x+860,y+242),col)
   val=f'{round(n*ease((u-.3-j*.15)/2.8)):,}'.replace(',','.')
   txt(im,val,x+36,y+38,100,True,col,maxw=780);txt(im,lab,x+40,y+171,29,True,'muted')
 elif kind=='timeline':
  txt(im,'PLAN DE MANTENIMIENTO VERSIONADO',80,302,26,True,'muted')
  labs=[('PREVISTO','Fecha programada','Conocimiento del plan'),('APLAZADO','Nueva hora: desconocida','No anticipar el futuro'),('INICIADO','Inicio real registrado','Conocido al ocurrir')]
  for j,(a,b,c) in enumerate(labs):
   x=80+j*600;p=ease((u-.8-j*.6)/1.1);panel(im,(x,372,x+560,674),['purple','amber','cyan'][j]);txt(im,a,x+32,409,34,True,['purple','amber','cyan'][j],alpha=p)
   txt(im,b,x+32,489,35,True,maxw=500,alpha=p);txt(im,c,x+32,575,27,color='muted',maxw=495,alpha=p)
   if j<2:arrow(d,(x+565,522),(x+594,522),'muted',3)
  d.line((120,774,1800,774),fill=C['line'],width=3);x=120+1680*((u*.13)%1);d.ellipse((x-9,765,x+9,783),fill=C['cyan'])
  txt(im,'La aplicación solo muestra lo que ya se sabía.',960,805,38,True,'white',center=True)
 elif kind=='variability':
  labs=[('VIDA LARGA','Más periodos normales','cyan'),('CALENDARIOS','Turnos y preventivos variables','purple'),('SENSORES','Calibración, picos y deriva','amber'),('ADQUISICIÓN','Pérdidas correlacionadas','cyan')]
  for j,(a,b,col) in enumerate(labs):
   x=80+(j%2)*900;y=325+(j//2)*275;panel(im,(x,y,x+860,y+245),col);txt(im,a,x+30,y+28,33,True,col);txt(im,b,x+30,y+87,31,maxw=790)
   pts=[]
   for k in range(150):
    xx=x+35+k*5.2;wave=math.sin(k*.12+u*.9)*(10+j*4)+math.sin(k*.6+u)*3
    if j==2 and k%41<2:wave+=29
    yy=y+179+wave;pts.append((xx,yy))
   if j==3:
    for lo,hi in [(0,40),(55,90),(115,150)]:d.line(pts[lo:hi],fill=C[col],width=3)
   else:d.line(pts,fill=C[col],width=3)
  txt(im,'Trazos conceptuales · no representan mediciones del dataset',960,872,22,color='muted',center=True)
 elif kind=='health':
  # Unaltered source chart with an animated frame, not reconstructed numeric values.
  im.paste(HEALTH,(130,295));d=ImageDraw.Draw(im)
  reveal=ease((u-.6)/3)
  if reveal<1:d.rectangle((130+int(1660*reveal),295+87/558*605,1790,295+515/558*605),fill='white')
  # Highlight R07-R12 without concealing bars.
  x0=130+642/1530*1660;x1=130+1138/1530*1660
  if u>3.5:d.rectangle((int(x0),int(295+80/558*605),int(x1),int(295+516/558*605)),outline=C['cyan'],width=4)
  # Source image includes legend and axis; range label uses separate overlay above figure.
  txt(im,'R07–R12: estado normal entre 29,4 % y 80,0 %',960,247,28,True,'cyan',center=True)
 elif kind=='rates':
  im.paste(RATES,(90,310));d=ImageDraw.Draw(im)
  reveal=ease((u-.5)/3)
  if reveal<1:d.rectangle((90+int(1740*reveal),315,1830,310+435/513*583),fill='white')
  txt(im,'TASAS DEL SIMULADOR · NO SON RESULTADOS DE UN MODELO',960,265,26,True,'amber',center=True)
  # moving cursor traverses groups; source values unchanged
  x=90+130+(1530*q);d.line((int(x),320,int(x),850),fill='#ad9bf5',width=2)
 elif kind=='inputs':
  panel(im,(80,330,810,620),'cyan');txt(im,'SÍ EN LA ENTRADA',115,367,32,True,'cyan')
  lines(im,['Señales disponibles','Historial ya conocido','Lista permitida de variables'],115,440,35,gap=18,color='white')
  panel(im,(1110,330,1840,620),'red');txt(im,'FUERA DE LA ENTRADA',1145,367,32,True,'red')
  lines(im,['Salud y daño internos','Fallo futuro','Filas excluidas'],1145,440,35,gap=18,color='white')
  motor(im,960,483,t,.48)
  panel(im,(80,669,1840,865));txt(im,'ISOLATION FOREST · DOS REFERENCIAS',110,698,27,True,'muted')
  txt(im,'OBSERVABLE → principal',110,759,37,True,'cyan',maxw=800)
  txt(im,'IDEAL → análisis separado',1005,759,37,True,'purple',maxw=790)
  txt(im,'Ninguno de estos selectores es un predictor.',110,818,26,color='muted')
 elif kind=='alerts':
  txt(im,'ABRIR: 3 DE LAS ÚLTIMAS 5 POSICIONES',80,302,30,True,'cyan')
  vals=[True,False,True,None,True]
  for j,val in enumerate(vals):
   x=160+j*240;y=473;on=u>.8+j*.55;col='line' if not on else 'muted' if val is None else 'cyan' if val else 'purple'
   d.ellipse((x-62,y-62,x+62,y+62),outline=C[col],width=4)
   if on and val:d.ellipse((x-46,y-46,x+46,y+46),fill=C['cyan'])
   txt(im,'?' if val is None else '+' if val else '–',x,y-26,48,True,'bg' if on and val else col,center=True)
   txt(im,f'{j*15} min',x,566,27,color='muted',center=True)
  arrow(d,(1220,474),(1350,474),'cyan')
  panel(im,(1395,390,1840,568),'cyan');txt(im,'AVISO',1617,441,65,True,'cyan',center=True,alpha=ease((u-3.1)/.5))
  panel(im,(80,677,930,868),'amber');txt(im,'1–24 h',115,708,77,True,'amber');txt(im,'de anticipación útil',115,809,31)
  panel(im,(970,677,1840,868),'cyan');txt(im,'≤ 1 falsa alerta',1005,708,61,True,'cyan',maxw=780);txt(im,'por 1.000 horas operativas',1005,809,31)
  txt(im,'Esquema ilustrativo de persistencia',80,620,22,color='muted')
 elif kind=='compare':
  labs=['Constante','Regla de condición','Historial y carga']
  for j,l in enumerate(labs):
   x=80+j*600;panel(im,(x,330,x+560,494));txt(im,l,x+280,386,40,True,'white',maxw=505,center=True)
  txt(im,'COMPARADORES OBLIGATORIOS',960,532,27,True,'muted',center=True)
  panel(im,(80,608,1840,861),'cyan');txt(im,'≥ 5 puntos',115,643,78,True,'cyan');txt(im,'de mejora en sensibilidad',115,750,31,maxw=750)
  lines(im,['Intervalo pareado positivo','Mismo límite de falsas alertas','Resultados por demostrar'],1040,642,35,color='white',gap=29,maxw=740)
 elif kind=='evidence':
  vals=[705,91,44,762,64,27];labs=['Datos, etiquetas y causalidad','Catálogo y segmentos','Pruebas del protocolo','Correcciones y referencias','Llegada de datos','PostgreSQL local']
  for j,(n,l) in enumerate(zip(vals,labs)):
   y=338+j*80;txt(im,l,80,y+5,29,maxw=580)
   d.rounded_rectangle((670,y,1280,y+37),radius=8,fill='#102b3b');p=ease((u-.5-j*.18)/2.1)
   if p>0:d.rounded_rectangle((670,y,670+610*(n/762)*p,y+37),radius=8,fill=C['cyan'] if j%2==0 else C['purple'])
   txt(im,str(round(n*p)),1330,y-1,36,True,maxw=140)
  panel(im,(1480,328,1840,591),'cyan');txt(im,f'{round(1693*q):,}'.replace(',','.'),1660,367,78,True,'cyan',center=True,maxw=310)
  txt(im,'correctas',1660,475,31,center=True);txt(im,'0 fallidas',1660,527,29,color='muted',center=True)
  panel(im,(1480,620,1840,841),'purple');txt(im,'77 / 77',1660,666,57,True,'purple',center=True,maxw=310);txt(im,'archivos idénticos',1660,750,25,center=True)
  txt(im,'Son pruebas técnicas, no ensayos estadísticos independientes.',80,859,25,color='muted')
 elif kind=='uncertainty':
  txt(im,'7',100,328,230,True,'amber');lines(im,['combinaciones de','partición y modo','con menos de 20 sucesos'],355,364,47,color='white',gap=24,maxw=1060)
  # Count symbols denote the seven strata, not individual events.
  for j in range(7):
   x=135+j*250;y=714;p=ease((u-.6-j*.18)/.9);d.rounded_rectangle((x,y,x+150,y+100),radius=16,fill=mix(C['panel'],C['amber'],p*.45),outline=C['amber'],width=2)
   txt(im,str(j+1),x+75,y+20,49,True,'amber',center=True)
  txt(im,'Resultados descriptivos · incertidumbre visible',960,841,36,True,'white',center=True)
 elif kind=='limits':
  labs=[('MODELOS','XGBoost e Isolation Forest','todavía sin entrenar','cyan'),('DESTINO','Windows / Spyder y Neon','todavía sin verificar','purple'),('IMPACTO REAL','Predicción, ahorro y fiabilidad','todavía sin demostrar','amber')]
  for j,(a,b,c,col) in enumerate(labs):
   x=80+j*600;panel(im,(x,350,x+560,810),col);txt(im,a,x+35,393,30,True,col)
   yy=492
   for line in wrap(b,39,490):txt(im,line,x+35,yy,39,True,maxw=490);yy+=53
   for k,line in enumerate(wrap(c,34,490)):txt(im,line,x+35,660+k*48,34,color='muted',maxw=490)
  txt(im,'Tampoco está verificado el dashboard final.',960,850,29,color='muted',center=True)
 elif kind=='outro':
  motor(im,1530,532,t,1.15)
  words=[('CONOCIMIENTO','Entender y hacer visibles los límites.','cyan'),('DESARROLLO','Código, datos y protocolo reproducibles.','purple'),('IMPACTO','Una hipótesis que habrá que evaluar.','amber')]
  for j,(a,b,col) in enumerate(words):
   p=ease((u-.3-j*.6)/.8);y=260+j*185;txt(im,a,80,y,70,True,col,maxw=1230,alpha=p);txt(im,b,85,y+91,32,color='white',maxw=1240,alpha=p)
  txt(im,'APTO PARA INICIAR EL EXPERIMENTO SINTÉTICO',80,832,30,True,'cyan',maxw=1700)
 caption(im,s,u)
 # cinematic dip transitions, preserving full readability in the hold section
 fade=min(ease(u/.55),ease((s['duration']-u)/.45))
 if fade<1:im=Image.blend(Image.new('RGB',(W,H),C['bg']),im,fade)
 return im

def audio():
 rate=48000;n=int(DURATION*rate);mixbuf=np.zeros((n,2),dtype=np.float32)
 # Original ambient electronic harmony. No sampled recordings.
 chords=[(164.8138,195.9977,246.9417),(130.8128,164.8138,195.9977),(146.8324,184.9972,220),(123.4708,146.8324,184.9972)]
 block=10
 for start in range(0,DURATION,block):
  length=min(block,DURATION-start);tt=np.arange(int(length*rate))/rate
  env=np.minimum(1,tt/1.5)*np.minimum(1,(length-tt)/2)
  chord=chords[(start//block)%4];sig=np.zeros_like(tt)
  for f in chord:sig+=.04*np.sin(2*np.pi*f*tt+.5*np.sin(tt*.4))+.013*np.sin(2*np.pi*f*2*tt)
  sig*=env*(.7+.3*np.sin(tt*.18)**2);i=int(start*rate);mixbuf[i:i+len(tt),0]+=sig;mixbuf[i:i+len(tt),1]+=sig*.95
 # A restrained pulse, one beat per second; stereo panning of gentle accents.
 for k in range(DURATION):
  length=.45;tt=np.arange(int(length*rate))/rate;freq=chords[(k//10)%4][k%3]*2
  a=.025*np.sin(2*np.pi*freq*tt)*np.exp(-tt*10)*np.minimum(tt/.015,1)
  i=k*rate;mixbuf[i:i+len(a),k%2]+=a
 rng=np.random.default_rng(101)
 for point in STARTS[1:-1]:
  tt=np.arange(int(.65*rate))/rate;noise=rng.normal(0,.008,len(tt));noise=np.convolve(noise,np.ones(12)/12,mode='same')
  hit=.045*np.sin(2*np.pi*(64*tt+30*(1-np.exp(-tt*5))))*np.exp(-tt*8)
  env=np.sin(np.pi*tt/.65)**2;signal=noise*env+hit;i=int(point*rate);mixbuf[i:i+len(tt)]+=signal[:,None]
 time=np.arange(n)/rate;fade=np.minimum(1,time/3)*np.minimum(1,(DURATION-time)/4)
 mixbuf*=fade[:,None];mixbuf=np.clip(mixbuf,-.85,.85)
 path=R/'assets/banda_original.wav'
 with wave.open(str(path),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate);w.writeframes((mixbuf*32767).astype('<i2').tobytes())
 return path

def subtitles():
 rows=[]
 def stamp(t):return f'{int(t)//3600:02d}:{(int(t)//60)%60:02d}:{int(t)%60:02d},000'
 for i,s in enumerate(SCENES):rows.append(f'{i+1}\n{stamp(STARTS[i])} --> {stamp(STARTS[i+1])}\n'+s['title'].replace('\n',' ')+'\n'+s['caption']+'\n')
 (R/'output/Auditoria_ACB_v3_1.srt').write_text('\n'.join(rows),encoding='utf-8')

def render():
 (R/'output').mkdir(exist_ok=True);audio_path=audio();subtitles()
 output=R/'output/Auditoria_ACB_v3_1_Animacion_1080p.mp4'
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(audio_path),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-t',str(DURATION),'-metadata','title=Auditoría ACB v3.1 - Datos antes de modelos','-metadata','comment=Animación basada en el informe de cierre de auditoría del 05/11/2026. Datos sintéticos, sin modelos entrenados.',str(output)]
 with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
  for i in range(DURATION*FPS):
   proc.stdin.write(frame(i/FPS).tobytes())
   if i% (FPS*10)==0:print(f'{i/FPS:.0f}/{DURATION} segundos',flush=True)
  proc.stdin.close();code=proc.wait()
  if code:raise RuntimeError(f'FFmpeg {code}')
 print(output,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');a=p.parse_args()
 if a.preview:
  (R/'qa').mkdir(exist_ok=True)
  for i,s in enumerate(SCENES):frame(float(STARTS[i])+s['duration']*.65).save(R/f'qa/escena_{i+1:02d}.png')
  print('Previews',len(SCENES),'duración',DURATION)
 else:render()
