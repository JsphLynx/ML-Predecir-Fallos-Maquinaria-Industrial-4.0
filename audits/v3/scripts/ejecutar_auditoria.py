"""Runner reproducible que conserva el dataset original."""
import argparse, shutil, subprocess, sys
from pathlib import Path

def main(dataset,work,reproducir=False):
    dataset=dataset.resolve();work=work.resolve()
    work.mkdir(parents=True,exist_ok=False)
    clone=work/'dataset_copia';shutil.copytree(dataset,clone)
    evidence=work/'evidence';evidence.mkdir()
    calls=[('validacion_original',[sys.executable,str(clone/'src/04_validar_dataset.py'),'--root',str(clone)]),
           ('catalogo_original',[sys.executable,str(clone/'src/11_validar_catalogo.py'),'--root',str(clone)]),
           ('auditoria_independiente',[sys.executable,str(Path(__file__).with_name('auditar_v3.py')),'--root',str(dataset),'--out',str(evidence)])]
    if reproducir:calls.append(('reproduccion_completa',[sys.executable,str(clone/'src/10_reproducibilidad.py'),'--root',str(clone),'--out',str(work/'reproduccion')]))
    for name,cmd in calls:
        with (evidence/(name+'.log')).open('w') as f:
            subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
    for name in ['validacion.json','validacion_catalogo_segmentos.json']+(['reproducibilidad.json'] if reproducir else []):
        shutil.copyfile(clone/'resultados'/name,evidence/name)
    print('Auditoría terminada. Revisar passed/failed en los JSON:',evidence)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--reproducir',action='store_true');a=p.parse_args();main(a.dataset,a.work,a.reproducir)
