"""Generate v3.1 in a new directory without changing historical snapshots."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    destination = args.out.resolve()
    source = ROOT / 'versions/v3.1'
    if destination.exists():
        raise SystemExit('Elige una carpeta de destino inexistente; no se sobrescriben datos.')
    destination.mkdir(parents=True)
    for name in ['src', 'config']:
        shutil.copytree(source / name, destination / name)
    for name in ['requirements.txt', 'requirements_sql_opcional.txt', 'README.md', 'AVISO_DE_USO.md']:
        shutil.copyfile(source / name, destination / name)
    scripts = destination / 'src'
    subprocess.run([sys.executable, str(scripts / '01_generar_dataset.py'),
                    '--config', str(destination / 'config/escenario.json'), '--out', str(destination)], check=True)
    for name in ['02_construir_variables.py', '03_etiquetas_particiones.py',
                 '04_validar_dataset.py', '05_documentar_sql.py']:
        subprocess.run([sys.executable, str(scripts / name), '--root', str(destination)], check=True)
    print(f'Datos generados en {destination}. No se han entrenado modelos.')


if __name__ == '__main__':
    main()
