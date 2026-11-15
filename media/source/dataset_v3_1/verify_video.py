from pathlib import Path
import subprocess,json,hashlib,struct
from PIL import Image
R=Path(__file__).resolve().parent;p=next((R/'output').glob('*.mp4'))
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
scenes=json.loads((R/'storyboard.json').read_text());duration=sum(s['duration'] for s in scenes)
assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'30/1')
assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p' and a['codec_name']=='aac'
assert int(v['nb_frames'])==duration*30 and abs(float(meta['format']['duration'])-duration)<.05
check=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p),'-f','null','-'],capture_output=True,text=True);assert check.returncode==0,check.stderr
volume=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','volumedetect','-vn','-sn','-dn','-f','null','-'],capture_output=True,text=True)
vol=[l.strip() for l in volume.stderr.splitlines() if 'mean_volume' in l or 'max_volume' in l]
boxes={}
with p.open('rb') as f:
 while True:
  pos=f.tell();b=f.read(8)
  if len(b)<8:break
  size,typ=struct.unpack('>I4s',b)
  if size==1:size=struct.unpack('>Q',f.read(8))[0]
  if size==0:break
  boxes[typ.decode('ascii')]=pos;f.seek(pos+size)
assert boxes['moov']<boxes['mdat']
cur=0;frames=[]
for s in scenes:frames.append(int((cur+s['duration']*.65)*30));cur+=s['duration']
expr='+'.join(f'eq(n\\,{n})' for n in frames)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(p),'-vf',f'select={expr},scale=640:360','-fps_mode','vfr',str(R/'qa/encoded_%02d.jpg')],check=True)
sheet=Image.new('RGB',(1920,((len(scenes)+2)//3)*360),'#07121e')
for i in range(len(scenes)):sheet.paste(Image.open(R/f'qa/encoded_{i+1:02d}.jpg'),((i%3)*640,(i//3)*360))
sheet.save(R/'qa/encoded_contact_sheet.jpg')
qa={'file':p.name,'duration_seconds':duration,'scenes':len(scenes),'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':v['nb_frames'],'codec_video':v['codec_name'],'codec_audio':a['codec_name'],'channels':a['channels'],'pixel_format':v['pix_fmt'],'decode_exit_code':check.returncode,'decode_errors':check.stderr,'faststart':True,'audio_volume':vol,'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'encoded_review_frames':len(scenes),'scope':'Validación audiovisual. No reejecución de pruebas del dataset ni entrenamiento.'}
(R/'qa/validacion_video.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps(qa,ensure_ascii=False,indent=2))
