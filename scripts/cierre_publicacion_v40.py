"""Verify the import on the preparation branch; publish only after merge to main."""
from pathlib import Path
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REPO = "JsphLynx/ML-Predecir-Fallos-Maquinaria-Industrial-4.0"
RELEASE_ID = 453805961
def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()
def write(path, data):
    p = ROOT/path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data, encoding="utf-8")
def dump(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2)+"\n")
def api(path, patch=None):
    args = ["gh", "api", path]
    kw = {}
    if patch is not None:
        args += ["--method", "PATCH", "--input", "-"]
        kw["input"] = json.dumps(patch)
    result = subprocess.run(args, text=True, capture_output=True, check=True, **kw)
    return json.loads(result.stdout)
def refresh_manifest():
    files = subprocess.check_output(["git","ls-files","--cached","--others","--exclude-standard","-z"],cwd=ROOT).decode().split("\0")
    dump("PORTFOLIO_SHA256.json", {f:sha(ROOT/f) for f in sorted(set(files)) if f and f!="PORTFOLIO_SHA256.json" and (ROOT/f).is_file()})
    subprocess.run([sys.executable,str(ROOT/"scripts/verificar_portfolio.py")], check=True)
def main():
    assert os.environ.get("GITHUB_REPOSITORY") == REPO
    ref = os.environ["GITHUB_REF"]
    assert ref in ["refs/heads/portfolio/v4.0-preparacion", "refs/heads/main"]
    packages = json.loads((ROOT/"data/releases.json").read_text())
    v4 = [p for p in packages if p["version"]=="v4.0"]
    assert len(v4)==2
    release = api(f"repos/{REPO}/releases/{RELEASE_ID}")
    assets = {a["name"]:a for a in release["assets"]}
    for p in v4:
        a=assets[p["filename"]]
        assert a["state"]=="uploaded" and a["size"]==p["bytes"]
        assert a["digest"]=="sha256:"+p["sha256"]
    if ref.endswith("/main"):
        report=json.loads((ROOT/"docs/verification/cierre_v4_0.json").read_text())
        assert report["status"]=="verified" and report["fixtures"]["failed"]==0
        subprocess.run([sys.executable,str(ROOT/"scripts/verificar_portfolio.py")],check=True)
        if release["draft"]:
            release=api(f"repos/{REPO}/releases/{RELEASE_ID}",dict(draft=False,target_commitish=os.environ["GITHUB_SHA"],make_latest="true"))
        assert not release["draft"]
        assets={a["name"]:a for a in release["assets"]}
        for p in v4:
            a=assets[p["filename"]]
            assert a["digest"]=="sha256:"+p["sha256"] and a["size"]==p["bytes"]
            p.update(status="published",published_url=a["browser_download_url"],release_url=release["html_url"],verified_at="2026-11-21",verification="GitHub asset size and SHA-256 match both original ZIPs")
        dump("data/releases.json",packages)
        text="**Dataset v4.0 publicado:** [descargar las dos partes y hashes]("+release["html_url"]+"). Código, ejemplos y los informes internos del paquete están incorporados."
        for name in ["README.md","docs/v4.0/PUBLICACION.md"]:
            p=ROOT/name
            write(name,re.sub(r"<!-- release-status -->[\s\S]*?<!-- /release-status -->","<!-- release-status -->\n"+text+"\n<!-- /release-status -->",p.read_text()))
        ev=json.loads((ROOT/"docs/v4.0/evidencia_documental.json").read_text())
        ev["this_github_import"].update(release_assets_published=True,status="published")
        dump("docs/v4.0/evidencia_documental.json",ev)
        report["release_published"]=True
        report["release_url"]=release["html_url"]
        report["publication_run_id"]=os.environ["GITHUB_RUN_ID"]
        dump("docs/verification/cierre_v4_0.json",report)
        refresh_manifest()
        print("RELEASE PUBLICADA",release["html_url"],flush=True)
        return
    original=json.loads((ROOT/"versions/v4.0/SHA256.json").read_text())
    verified=0
    for p in (ROOT/"versions/v4.0").rglob("*"):
        if p.is_file():
            rel=str(p.relative_to(ROOT/"versions/v4.0"))
            if rel!="SHA256.json":
                assert rel in original and sha(p)==original[rel],rel
                verified+=1
    assert verified==89
    previous=json.loads((ROOT/"PORTFOLIO_SHA256.json").read_text())
    for name,expected in previous.items():
        if name.startswith(("versions/v1/","versions/v2/","versions/v3/","versions/v3.1/")):
            assert sha(ROOT/name)==expected,name
    parsed=0
    for parent in ["versions/v4.0","scripts"]:
        for p in (ROOT/parent).rglob("*.py"):
            ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
            parsed+=1
    with tempfile.TemporaryDirectory(prefix="v40-test-") as d:
        env=Path(d)/"venv"
        subprocess.run([sys.executable,"-m","venv",str(env)],check=True)
        python=env/"bin/python"
        subprocess.run([str(python),"-m","pip","install","-r",str(ROOT/"versions/v4.0/requirements_auditoria.txt")],check=True)
        result=subprocess.run([str(python),str(ROOT/"scripts/probar_protocolo_v40.py")],text=True,capture_output=True,check=True)
        print(result.stdout,flush=True)
        fixtures=json.loads(result.stdout.strip().splitlines()[-1])
        assert fixtures["checks"]==44 and fixtures["passed"]==44 and fixtures["failed"]==0
        write("docs/verification/v4.0/protocolo_publicacion.log",result.stdout)
        freeze=subprocess.check_output([str(python),"-m","pip","freeze"],text=True)
        write("docs/verification/v4.0/entorno_publicacion.txt",freeze)
    ev=json.loads((ROOT/"docs/v4.0/evidencia_documental.json").read_text())
    ev["this_github_import"].update(original_archives_extracted=True,original_hashes_rechecked=True,code_imported=True,status="verified_ready_to_publish")
    dump("docs/v4.0/evidencia_documental.json",ev)
    report=dict(date="2026-11-21",runner="GitHub Actions",run_id=os.environ["GITHUB_RUN_ID"],status="verified",original_files_in_git_checked=90,protected_content_hashes_checked=89,original_manifest_preserved=True,python_files_parsed=parsed,fixtures=fixtures,models_trained=False,full_dataset_regenerated=False,live_postgresql_executed=False,windows_spyder_executed=False,release_assets_matched=True,release_published=False)
    dump("docs/verification/cierre_v4_0.json",report)
    editorial=["README.md","docs/DESCARGAS.md","docs/VERIFICACION.md","docs/v4.0/README.md","docs/v4.0/PORTFOLIO.md","docs/v4.0/RESUMEN_EN.md","docs/v4.0/PUBLICACION.md","docs/v4.0/VALIDACION.md","docs/ROADMAP.md","docs/REPRODUCIBILIDAD.md"]
    checked=0
    for name in editorial:
        for target in re.findall(r"\]\(([^)]+)\)",(ROOT/name).read_text()):
            target=target.strip().split(" ",1)[0]
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:",target) or target.startswith("#"):
                continue
            target=unquote(target.split("#")[0])
            p=((ROOT/name).parent/target).resolve()
            assert p.is_relative_to(ROOT.resolve()) and p.exists(),(name,target)
            checked+=1
    report["relative_links_checked"]=checked
    report["broken_links"]=0
    dump("docs/verification/cierre_v4_0.json",report)
    refresh_manifest()
    print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":
    main()
