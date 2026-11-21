"""Execute original v4.0 fixtures in isolation, preserving historical evidence."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'versions/v4.0'
    with tempfile.TemporaryDirectory(prefix='acb_protocol_') as directory:
        work = Path(directory) / 'v4.0'
        for name in ['src', 'config', 'ml']:
            shutil.copytree(source / name, work / name)
        subprocess.run([sys.executable, str(work / 'src/12_probar_protocolo.py')], check=True)
        result = json.loads((work / 'resultados/pruebas_protocolo.json').read_text())
        if result['failed'] or result['passed'] != result['checks']:
            raise SystemExit('Protocol verification failed')
        print(json.dumps({k: result[k] for k in ['checks', 'passed', 'failed', 'scope']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
