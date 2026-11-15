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
 txt(im,f'{index+1:02d} / {len(SCENES)}',1755,46,23,mono=True)
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

