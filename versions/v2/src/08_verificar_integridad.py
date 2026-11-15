"""Comprueba archivos entregados respecto a SHA256.json, antes de regenerar."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
if __name__=='__main__':
    manifest=json.loads((ROOT/'SHA256.json').read_text())
    bad=[p for p,h in manifest.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    print('Archivos comprobados:',len(manifest),'Diferencias:',bad)
    if bad:raise SystemExit(1)
