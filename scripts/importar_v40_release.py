"""Import the already-uploaded v4.0 archives; no training or full regeneration."""
from pathlib import Path
import ast
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = "JsphLynx/ML-Predecir-Fallos-Maquinaria-Industrial-4.0"
ASSETS = [
    (776087326, "ACB_Motor_Rodamientos_Sintetico_v4_0_Parte_1.zip", 441246147, "31ade7f26bf96f2cba7dbe9c5ab7d8f92ed757cc862e89d5c75532cabe3c7638"),
    (776087871, "ACB_Motor_Rodamientos_Sintetico_v4_0_Parte_2.zip", 437652006, "717fdc28ab2dec079672d54c97ded9a8484781ea0a524642751d6904edcb4ffb"),
]
def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def write(path, data):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")

def main():
    assert os.environ.get("GITHUB_REPOSITORY") == REPO
    assert os.environ.get("GITHUB_REF") == "refs/heads/portfolio/v4.0-preparacion"
    old_manifest = json.loads((ROOT / "PORTFOLIO_SHA256.json").read_text())
    # Preserve every protected pre-v4 original.
    for name, expected in old_manifest.items():
        if name.startswith(("versions/v1/", "versions/v2/", "versions/v3/", "versions/v3.1/")):
            assert sha(ROOT/name) == expected, name
    with tempfile.TemporaryDirectory(prefix="v40-import-") as folder:
        work = Path(folder)
        extracted = work/"original"
        seen = {}
        duplicates = []
        records = []
        for asset_id, name, size, digest in ASSETS:
            dest = work/name
            with dest.open("wb") as stream:
                subprocess.run(["gh", "api", f"repos/{REPO}/releases/assets/{asset_id}", "-H", "Accept: application/octet-stream"], stdout=stream, check=True)
            assert dest.stat().st_size == size, name
            assert sha(dest) == digest, name
            print("ZIP verificado:", name, flush=True)
            records.append(dict(version="v4.0", filename=name, bytes=size, sha256=digest, release_asset_id=asset_id, release_tag="portfolio-v4.0", status="uploaded_draft", published_url=None))
            with zipfile.ZipFile(dest) as archive:
                for member in archive.infolist():
                    path = (extracted/member.filename).resolve()
                    assert path.is_relative_to(extracted.resolve()), member.filename
                    assert not ((member.external_attr >> 16) & 0o170000) == 0o120000, "symlink"
                    if member.is_dir():
                        continue
                    content = archive.read(member)
                    h = hashlib.sha256(content).hexdigest()
                    if member.filename in seen:
                        assert seen[member.filename] == h, member.filename
                        duplicates.append(member.filename)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(content)
                        seen[member.filename] = h
        source = extracted/"ACB_Motor_Rodamientos_Sintetico_v4_0"
        manifest = json.loads((source/"SHA256.json").read_text())
        assert len(manifest) == 182
        for name, expected in manifest.items():
            p = (source/name).resolve()
            assert p.is_relative_to(source.resolve())
            assert sha(p) == expected, name
        print("Manifiesto original: 182/182; cero diferencias", flush=True)
        catalog = []
        copied = 0
        for p in sorted(source.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(source)
            in_git = not (rel.parts[0] in ("data", "sim_truth") or (rel.parts[0] == "ml" and rel.suffix == ".parquet"))
            if in_git:
                dest = ROOT/"versions/v4.0"/rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(p, dest)
                assert sha(dest) == sha(p)
                copied += 1
            catalog.append(dict(version="v4.0", path=str(rel), bytes=p.stat().st_size, sha256=sha(p), location="git" if in_git else "original_package"))
        assert len(catalog) == 183 and copied == 90
        for name in ["Informe_Mejora_Dataset_v4_0.pdf", "Informe_Investigacion_Sestao_SMS_Contraste_v3_1.pdf"]:
            shutil.copyfile(source/"docs"/name, ROOT/"docs/reports"/name)
        write("docs/v4.0/LEEME_EXTRACCION_DOS_PARTES.txt", (extracted/"LEEME_EXTRACCION_DOS_PARTES.txt").read_text())
        write("docs/v4.0/SHA256SUMS.txt", "".join(f"{digest}  {name}\n" for _,name,_,digest in ASSETS))
        cp = ROOT/"docs/catalogo_archivos_versiones.csv"
        with cp.open(newline="") as f:
            previous = [row for row in csv.DictReader(f) if row["version"] != "v4.0"]
        with cp.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["version","path","bytes","sha256","location"])
            writer.writeheader()
            writer.writerows(previous+catalog)
        releases = json.loads((ROOT/"data/releases.json").read_text())
        write("data/releases.json", json.dumps([x for x in releases if x["version"]!="v4.0"]+records, indent=2)+"\n")
        # Syntax is checked without executing the imported generator or training.
        parsed = 0
        for p in (ROOT/"versions/v4.0").rglob("*.py"):
            ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
            parsed += 1
        launcher = (ROOT/"scripts/probar_protocolo.py").read_text().replace("v3.1", "v4.0")
        write("scripts/probar_protocolo_v40.py", launcher)
        report = dict(date="2026-11-21", runner="GitHub Actions", run_id=os.environ.get("GITHUB_RUN_ID"), original_manifest_entries=182, matched=182, differences=[], package_files=183, files_in_git=90, files_in_archives_only=93, duplicate_paths_identical=duplicates, python_files_parsed=parsed, models_trained=False, full_regeneration=False, source_zip_assets=records)
        write("docs/verification/importacion_v4_0.json", json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    # Only imported files and editorial material change; earlier versions stay intact.
    all_files = subprocess.check_output(["git","ls-files","--cached","--others","--exclude-standard","-z"], cwd=ROOT).decode().split("\0")
    new_manifest = {name: sha(ROOT/name) for name in sorted(set(all_files)) if name and name!="PORTFOLIO_SHA256.json" and (ROOT/name).is_file()}
    write("PORTFOLIO_SHA256.json", json.dumps(new_manifest, ensure_ascii=False, indent=2)+"\n")
    subprocess.run([sys.executable, str(ROOT/"scripts/verificar_portfolio.py")], check=True)
    print(json.dumps(report, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
