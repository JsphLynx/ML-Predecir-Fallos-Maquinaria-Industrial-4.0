"""Regenera datos y snapshots en un directorio NUEVO y compara bytes SHA-256.
La comparación cubre todos los Parquet y el contrato de columnas ML.
Puede tardar varios minutos y requiere espacio para una segunda copia.
"""
import argparse
from pathlib import Path
import subprocess
import sys
from comun import ROOT,sha,dump

def main(root=ROOT,out=None):
    root=Path(root).resolve();dest=Path(out or root.parent/(root.name+'_reproduccion')).resolve()
    if dest.exists():raise FileExistsError('Elige una carpeta de reproducción inexistente: '+str(dest))
    scripts=Path(__file__).parent
    subprocess.run([sys.executable,str(scripts/'01_generar_dataset.py'),'--config',str(root/'config/escenario.json'),'--out',str(dest)],check=True)
    for name in ['02_construir_variables.py','03_etiquetas_particiones.py','04_validar_dataset.py','05_documentar_sql.py']:
        subprocess.run([sys.executable,str(scripts/name),'--root',str(dest)],check=True)
    files=sorted([p.relative_to(root) for folder in ['data','ml','sim_truth'] for p in (root/folder).rglob('*.parquet')])
    files.append(Path('ml/columnas_modelo.json'))
    differences=[p.as_posix() for p in files if not (dest/p).exists() or sha(root/p)!=sha(dest/p)]
    result={'compared_files':len(files),'identical_files':len(files)-len(differences),'differences':differences,
        'method':'Dos generaciones completas con misma configuración, dependencias y semilla; SHA-256 de bytes',
        'second_generation_validation':__import__('json').loads((dest/'resultados/validacion.json').read_text())['failed']==0}
    dump(result,root/'resultados/reproducibilidad.json');print(result)
    if differences:raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--out');a=p.parse_args();main(a.root,a.out)
