"""Verify committed source and media bytes; does not certify predictive validity."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'PORTFOLIO_SHA256.json').read_text())
    errors = []
    for name, expected in manifest.items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            errors.append(name)
            continue
        with path.open('rb') as file:
            actual = hashlib.file_digest(file, 'sha256').hexdigest()
        if actual != expected:
            errors.append(name)
    if errors:
        raise SystemExit('Archivos ausentes o modificados:\n' + '\n'.join(errors))
    print(f'OK: {len(manifest)} archivos coinciden con el manifiesto del portafolio.')


if __name__ == '__main__':
    main()
