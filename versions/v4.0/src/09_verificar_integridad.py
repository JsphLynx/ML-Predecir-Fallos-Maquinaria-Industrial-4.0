"""Verifica SHA256.json antes de regenerar. No cambia archivos."""
import argparse
from pathlib import Path
import json
from comun import ROOT,sha

def main(root=ROOT):
    root=Path(root);manifest=json.loads((root/'SHA256.json').read_text(encoding='utf-8'))
    bad=[p for p,h in manifest.items() if not (root/p).is_file() or sha(root/p)!=h]
    print('Archivos comprobados:',len(manifest),'Diferencias:',bad)
    if bad:raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));a=p.parse_args();main(a.root)
