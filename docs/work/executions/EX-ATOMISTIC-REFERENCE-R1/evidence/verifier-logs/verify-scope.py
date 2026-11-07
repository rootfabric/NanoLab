"""Independent candidate scope, merge readback and scientific state checks."""
import ast
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

base = "ddf8a25cdd95a1598338816f6a585ffdde1e0f2a"
start = "69a25429c9237bcd0b6084ed1e9215cfafd770fc"
head = sys.argv[1]
def git(*args):
    return subprocess.check_output(["git", *args]).decode().strip()
def current(path):
    return json.loads(Path(path).read_bytes())
def previous(path):
    return json.loads(git("show", f"{base}:{path}"))

assert git("rev-parse", "HEAD") == head
assert git("rev-parse", f"{start}^") == base
assert git("merge-base", base, head) == base
assert "Merge pull request #96 " in git("show", "-s", "--format=%s", base)
assert git("rev-parse", f"{base}^2") == "db0a691a99f28b0d8e0e8dd9b8dcb3edd79d4821"
assert git("rev-parse", f"{base}^{{tree}}") == git("rev-parse", f"{base}^2^{{tree}}")
assert not git("diff", "--check", base, head)

changes = git("diff", "--name-status", base, head).splitlines()
allowed = {
    "docs/ROADMAP.md", "docs/atomistic/MODEL_CARD.md", "docs/atomistic/README.md",
    "docs/work/WO-ATOMISTIC-REFERENCE-R1.md", "scripts/atomistic/reference.py",
    "tests/test_atomistic_reference.py", "project/product-plan.json", "project/product-state.json",
    "project/operations/FLOW-R1.json",
}
allowed_prefix = ("docs/atomistic/reference/cu-r1/", "docs/work/executions/EX-ATOMISTIC-REFERENCE-R1/", "project/operations/ATOMISTIC-")
for entry in changes:
    status, path = entry.split("\t", 1)
    assert status in {"M", "A"}, entry
    assert path in allowed or path.startswith(allowed_prefix), entry
    print(entry)

for path in ("project/state.json", "project/plan.json", "experiments", "data", "config", "examples", ".github"):
    assert git("ls-tree", base, "--", path) == git("ls-tree", head, "--", path), path
assert git("diff", "--name-only", base, head, "--", "scripts") == "scripts/atomistic/reference.py"
assert not git("diff", "--name-only", base, head, "--", "docs/work/executions/EX-ATOMISTIC-PRODUCT-R1")
assert not git("diff", "--name-only", start, head, "--", "docs/work/executions/EX-ATOMISTIC-REFERENCE-R1/events/0001-work-order-started.json")
print("PASS diff scope, no runtime/CI/historic state/frozen input or old evidence changes")

state = current("project/product-state.json")
old_state = previous("project/product-state.json")
plan = current("project/product-plan.json")
old_plan = previous("project/product-plan.json")
for field in ("frontier", "stage_status", "accepted_stages", "canonical_acceptance", "demonstrated_results",
              "scientific_validation_status", "material_validation", "technical_review", "independent_verification", "mission_run_summary"):
    assert state[field] == old_state[field], field
assert state["frontier"] == "P0" and state["stage_status"]["P0"] == "OPEN"
assert state["material_validation"] == "NOT_EVALUATED"
assert state["accepted_stages"] == [] and state["canonical_acceptance"] is False
assert state["reference_preparation"]["physics_runs"] == 0
assert state["delivery_merge"]["merge_commit"] == base
assert state["delivery_merge"]["pull_request"].endswith("/96")
merge_evidence = current("docs/work/executions/EX-ATOMISTIC-REFERENCE-R1/evidence/pr96-merge.json")
assert state["delivery_merge"]["merged_at_utc"] in merge_evidence.values()
assert base in merge_evidence.values()
merge_time = datetime.fromisoformat(state["delivery_merge"]["merged_at_utc"].replace("Z", "+00:00"))
assert abs((merge_time - datetime.fromisoformat(git("show", "-s", "--format=%cI", base))).total_seconds()) <= 2
assert plan["engineering_launch_profile"] == old_plan["engineering_launch_profile"]
assert plan["stages"] == old_plan["stages"]
for name in ("ATOMISTIC-ADAPTER-PREP", "ATOMISTIC-APP-PREP", "FLOW-R1"):
    card = current(f"project/operations/{name}.json")
    assert card["status"] == "DONE" and not card["blockers"]
    assert base in card["next_action"] and "P0" in card["next_action"]
    assert card["scientific_runs_allowed"] is False
ref_card = current("project/operations/ATOMISTIC-REFERENCE-PREP.json")
benchmark = current("project/operations/ATOMISTIC-BENCHMARK-PREP.json")
assert ref_card["scientific_runs_allowed"] is False and benchmark["scientific_runs_allowed"] is False
assert benchmark["status"] == "PLANNED" and benchmark["depends_on"] == [ref_card["id"]]
for record in plan["nearest_tasks"]:
    if record["id"] in {"AP-P0-REFERENCE", "AP-P0-BENCHMARK"}:
        assert record["run_authority"] is None
print("PASS merge #96 delivery readback, no launch authority or acceptance, benchmark PLANNED")

package = Path("docs/atomistic/reference/cu-r1")
for rel, expected in (
    ("sources.json", "9a01999e6dee15f5f0d06358137ae6e089b825a58885c94a4da96011da9c1716"),
    ("source-artifacts/overton-gaffney-1955-facts.json", "674d2903462c56447da195907b5127630d1249854c89096612d8a9ea62f21f9c"),
):
    assert hashlib.sha256((package / rel).read_bytes()).hexdigest() == expected
    print(f"PASS candidate exact {rel} matches independently verified source bytes: {expected}")
for path in (package / "protocol.json", package / "PROTOCOL.md", package / "SOURCES.md"):
    print(f"exact {path}: {hashlib.sha256(path.read_bytes()).hexdigest()}")

module = ast.parse(Path("scripts/atomistic/reference.py").read_text())
imports = set()
for node in ast.walk(module):
    if isinstance(node, ast.Import):
        imports.update(name.name.split(".")[0] for name in node.names)
    elif isinstance(node, ast.ImportFrom):
        imports.add(node.module.split(".")[0])
assert imports <= {"argparse", "decimal", "hashlib", "json", "pathlib", "re", "sys", "urllib"}, imports
assert not any(Path(p).suffix.lower() in {".pdf", ".whl", ".gz", ".zip"} for p in git("ls-files", str(package)).splitlines())
print("PASS reference validator stdlib only; no published PDF/wheel/sdist")
