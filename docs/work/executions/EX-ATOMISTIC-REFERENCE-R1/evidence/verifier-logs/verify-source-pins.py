"""Read-only reference provenance verification; downloads package bytes without installation."""
import hashlib
import io
import json
import pathlib
import subprocess
import sys
import tarfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from urllib.request import urlopen

package = pathlib.Path("docs/atomistic/reference/cu-r1")
ledger = json.loads((package / "sources.json").read_bytes())
model = ledger["model"]
pins = model["artifacts"]

def download(url):
    with urlopen(url, timeout=20) as response:
        return response.read()

urls = sorted({p["url"] for p in pins} | {model["release_metadata_url"], model["upstream_url"]})
with ThreadPoolExecutor(max_workers=4) as pool:
    downloads = dict(zip(urls, pool.map(download, urls)))

metadata = json.loads(downloads[model["release_metadata_url"]])
assert metadata["info"]["version"] == model["ase_version"]
assert metadata["info"]["license_expression"] == model["license"]
releases = {f["url"]: f for f in metadata["urls"]}
pinned = {}
for pin in pins:
    archive = downloads[pin["url"]]
    published = releases[pin["url"]]
    assert hashlib.sha256(archive).hexdigest() == published["digests"]["sha256"]
    assert len(archive) == published["size"]
    payload = archive
    if member := pin.get("member"):
        if pin["url"].endswith(".whl"):
            with zipfile.ZipFile(io.BytesIO(archive)) as whl:
                payload = whl.read(member)
        else:
            with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as sdist:
                payload = sdist.extractfile(member).read()
    digest = hashlib.sha256(payload).hexdigest()
    assert digest == pin["sha256"] and len(payload) == pin["size_bytes"], pin["id"]
    pinned[pin["id"]] = payload
    print(f"PASS {pin['id']} sha256={digest} bytes={len(payload)}")

with tarfile.open(fileobj=io.BytesIO(pinned["ase-sdist"]), mode="r:gz") as sdist:
    module = sdist.extractfile("ase-3.26.0/ase/calculators/emt.py").read()
assert pinned["ase-emt-module"] == module == downloads[model["upstream_url"]]
assert b"License-Expression: LGPL-2.1-or-later" in pinned["ase-wheel-metadata"]
assert b"Version 2.1, February 1999" in pinned["ase-lgpl-text"]
assert b"either version 2.1 of the License, or" in pinned["ase-license-notice"]
assert b"'Cu':" in module and b"asap_cutoff" in module
print("PASS PyPI metadata; tagged raw = wheel EMT = sdist EMT; wheel notice and LGPL 2.1 text")

primary, = ledger["sources"]
assert not primary["rights"]["redistribute_full_text"]
assert primary["access"]["original_pdf_sha256"] is None
fact_pin = primary["artifact"]
fact_bytes = (package / fact_pin["local_path"]).read_bytes()
assert len(fact_bytes) == fact_pin["size_bytes"]
assert hashlib.sha256(fact_bytes).hexdigest() == fact_pin["sha256"]
facts = json.loads(fact_bytes)
obs, = ledger["observables"]
assert facts["source_id"] == primary["id"] == obs["source_id"]
assert facts["doi"] == primary["doi"]
assert facts["observable"] == {k: v for k, v in obs.items() if k not in {"source_id", "role"}}
assert Decimal(str(obs["original"]["value"])) * Decimal(10) == Decimal(str(obs["value"]))
assert obs["source_uncertainty"]["value"] is None
assert obs["unit"] == "GPa" and obs["temperature_k"] == 0
fact_paths = sorted(p.relative_to(package).as_posix() for p in (package / "source-artifacts").rglob("*") if p.is_file())
assert fact_paths == [fact_pin["local_path"]]
print(f"PASS only local sparse facts {fact_pin['local_path']} sha256={fact_pin['sha256']} bytes={len(fact_bytes)}; no original PDF hash")
print("PASS Decimal conversion 14.203 × 10 = 142.03 GPa; source K^T uncertainty null")
print("No archive installed or extracted to filesystem; physics runs=0")
