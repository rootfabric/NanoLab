"""Exercise independent CLI corruptions in scratch copies, no calculator."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

origin = Path("docs/atomistic/reference/cu-r1")
env = {**os.environ, "PYTHONPATH": "scripts", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1"}

def write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")

def load_json(path):
    return json.loads(path.read_bytes())

def update_pin(pinned_file, ref):
    raw = pinned_file.read_bytes()
    ref.update(sha256=hashlib.sha256(raw).hexdigest(), size_bytes=len(raw))

def sources_mutation(folder, action):
    source_path = folder / "sources.json"
    source = load_json(source_path)
    action(source, folder)
    write_json(source_path, source)
    protocol_path = folder / "protocol.json"
    protocol = load_json(protocol_path)
    update_pin(source_path, protocol["source_manifest"])
    write_json(protocol_path, protocol)

def uncertainty(source, folder):
    obs = source["observables"][0]
    obs["source_uncertainty"]["basis"] = "0.34% is the independently established isothermal uncertainty."
    source_record = source["sources"][0]
    facts = folder / source_record["artifact"]["local_path"]
    data = load_json(facts)
    data["observable"]["source_uncertainty"] = obs["source_uncertainty"]
    write_json(facts, data)
    update_pin(facts, source_record["artifact"])

def force_launch(folder):
    path = folder / "protocol.json"
    data = load_json(path)
    data["scientific_runs_allowed"] = True
    write_json(path, data)

def expand_budget(folder):
    path = folder / "protocol.json"
    data = load_json(path)
    data["proposed_future_budget"]["max_static_evaluations"] = 42
    write_json(path, data)

def html_source(source, _):
    url = source["sources"][0]["url"]
    source["sources"][0]["url"] = url.replace("journals.aps.org", "example.org")

def theory_doi(source, _):
    source["model"]["theory_doi"] = None

cases = (
    ("primary locators replaced and ledger rehashed", lambda folder: sources_mutation(folder, html_source)),
    ("theory DOI absent and ledger rehashed", lambda folder: sources_mutation(folder, theory_doi)),
    ("wrong source uncertainty basis, all downstream SHA repinned", lambda folder: sources_mutation(folder, uncertainty)),
    ("human protocol changed without re-pinning", lambda folder: (folder / "PROTOCOL.md").write_text("Unreviewed replacement\n")),
    ("force launch", force_launch),
    ("expand future budget from 41 to 42", expand_budget),
)

for title, action in cases:
    with TemporaryDirectory(prefix="nanolab-reference-neg-") as td:
        package = Path(td) / "cu-r1"
        shutil.copytree(origin, package)
        action(package)
        completed = subprocess.run([sys.executable, "-m", "atomistic.reference", "--package", str(package)],
                                   env=env, capture_output=True, text=True, timeout=10)
        print(f"{title}: exit={completed.returncode}; stderr={completed.stderr.strip()!r}")
        assert completed.returncode == 1 and not completed.stdout and "INVALID_PACKAGE:" in completed.stderr
print(f"PASS {len(cases)} independent negative CLI cases; physics runs=0")
