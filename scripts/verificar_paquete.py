"""Check one original ZIP against the published release manifest."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('zip', type=Path)
    args = parser.parse_args()
    entries = json.loads((ROOT / 'data/releases.json').read_text())
    matches = [x for x in entries if x['filename'] == args.zip.name]
    if len(matches) != 1:
        raise SystemExit('Nombre de paquete no reconocido; conserva el nombre original.')
    entry = matches[0]
    if args.zip.stat().st_size != entry['bytes']:
        raise SystemExit('Tamaño incorrecto: descarga incompleta o archivo diferente.')
    with args.zip.open('rb') as file:
        digest = hashlib.file_digest(file, 'sha256').hexdigest()
    if digest != entry['sha256']:
        raise SystemExit('SHA-256 incorrecto: no es el paquete original registrado.')
    print(f"OK {entry['version']}: tamaño y SHA-256 coinciden.")


if __name__ == '__main__':
    main()
