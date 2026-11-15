from pathlib import Path
import json,hashlib,zipfile
import pandas as pd
R=Path(__file__).resolve().parent;S=R/'source/inspeccion'
t=pd.read_parquet(S/'data/telemetria/R01.parquet').iloc[:288]
cols=['bearing_temperature_de_c','bearing_temperature_nde_c','vibration_de_mm_s','vibration_nde_mm_s']
d={'telemetry':json.loads(t[['timestamp']+cols].to_json(orient='records',date_format='iso')),'scenarios':pd.read_csv(S/'resultados/escenarios_salud.csv').to_dict('records'),'partitions':pd.read_csv(S/'resultados/particiones.csv').groupby('partition')['usable_rows'].sum().to_dict(),'references_if':pd.read_csv(S/'resultados/referencias_if.csv').groupby('reference')['rows'].sum().to_dict(),'dictionary':{'definitions':len(pd.read_csv(S/'docs/diccionario_datos.csv')),'tables':pd.read_csv(S/'docs/diccionario_datos.csv')['table'].nunique()}}
(R/'assets/chart_data.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
zp=R/'source/ACB_Motor_Rodamientos_Sintetico_v3_1.zip';h=json.loads((S/'SHA256.json').read_text());bad=[]
with zipfile.ZipFile(zp) as z:
 for p,expected in h.items():
  if hashlib.sha256(z.read('ACB_Motor_Rodamientos_Sintetico_v3_1/'+p)).hexdigest()!=expected:bad.append(p)
(R/'source/inspeccion_zip.json').write_text(json.dumps({'files_in_manifest':len(h),'hash_differences':bad,'zip_sha256':hashlib.sha256(zp.read_bytes()).hexdigest()},indent=2))
assert not bad
assert len(pd.read_parquet(S/'data/fallos.parquet'))==404
assert pd.read_csv(S/'resultados/cohortes_eventos.csv')['descriptive_only'].sum()==7
print('Datos extraídos; manifiesto',len(h),'sin diferencias.')
