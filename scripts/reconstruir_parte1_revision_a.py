"""Reconstruye la parte 1 auditada desde la parte 1 original y el ZIP de correcciones."""
import argparse
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

BASE = '31ade7f26bf96f2cba7dbe9c5ab7d8f92ed757cc862e89d5c75532cabe3c7638'
KIT = '60db3441d10b9a550d0edfbcc86f5a7aca3da36bebf82e3c5c25a042ffec7776'
RESULTADO = 'e6118efd0220477aad556f84fcdfa2a3849562f6d94fbf27bd29894d784c3b29'
RAIZ = 'ACB_Motor_Rodamientos_Sintetico_v4_0/'


def verificar(ruta, esperado):
    with ruta.open('rb') as archivo:
        if hashlib.file_digest(archivo, 'sha256').hexdigest() != esperado:
            raise ValueError(f'SHA-256 incorrecto para {ruta.name}')


def reconstruir(original, kit, destino):
    verificar(original, BASE)
    verificar(kit, KIT)
    if destino.exists():
        raise FileExistsError(destino)
    with TemporaryDirectory(dir=destino.parent) as temporal:
        salida = Path(temporal) / destino.name
        with ZipFile(original) as base, ZipFile(kit) as paquete, ZipFile(salida, 'w') as nueva:
            huellas = json.loads(paquete.read('huellas_correcciones.json'))
            revisados = {nombre: paquete.read('correcciones/' + nombre) for nombre in huellas}
            manifiesto = json.loads(base.read(RAIZ + 'SHA256.json'))
            revisados['SHA256.json'] = json.dumps(manifiesto | huellas, indent=2).encode()
            for entrada in base.infolist():
                if entrada.filename.removeprefix(RAIZ) not in revisados:
                    nueva.writestr(entrada, base.read(entrada))
            # Orden, marca temporal ZIP y permisos de la entrega auditada.
            for nombre, datos in revisados.items():
                entrada = ZipInfo(RAIZ + nombre, (2026, 11, 22, 13, 13, 54))
                entrada.create_system = 3
                entrada.external_attr = 0o100644 << 16
                entrada.compress_type = ZIP_DEFLATED
                nueva.writestr(entrada, datos)
        verificar(salida, RESULTADO)
        salida.rename(destino)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for argumento in ('original', 'kit', 'destino'):
        parser.add_argument(argumento, type=Path)
    args = parser.parse_args()
    reconstruir(args.original, args.kit, args.destino)
