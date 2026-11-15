from pathlib import Path
import zipfile,json,hashlib
R=Path(__file__).resolve().parent
files=[R/n for n in ['render_video.py','motion_engine.py','prepare_chart_data.py','build_storyboard.py','verify_video.py','package_editables.py','storyboard.json','README.md','Guion_y_fuentes.md','assets/chart_data.json','source/inspeccion_zip.json','qa/validacion_video.json','qa/encoded_contact_sheet.jpg']]
files+=list((R/'assets/fonts').glob('*'))+list((R/'output').glob('*.srt'))
for folder in ['src','config','docs','resultados','sql','ml']:
 for p in (R/'source/inspeccion'/folder).rglob('*'):
  if p.is_file() and p.suffix in ['.py','.md','.csv','.json','.sql','.txt']:files.append(p)
files+= [R/'source/inspeccion'/n for n in ['README.md','CHANGELOG.md','AVISO_DE_USO.md','SHA256.json']]
files=sorted(set(files));assert all(p.exists() for p in files)
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
output=R/'output/Dataset_ACB_v3_1_Animacion_Fuentes_Editables.zip'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 for p in files:z.write(p,'Dataset_ACB_v3_1_Animacion/'+str(p.relative_to(R)))
 z.writestr('Dataset_ACB_v3_1_Animacion/MANIFEST.json',json.dumps(manifest,indent=2,ensure_ascii=False))
with zipfile.ZipFile(output) as z:assert z.testzip() is None
print(output,len(files),'archivos',output.stat().st_size,'bytes')
