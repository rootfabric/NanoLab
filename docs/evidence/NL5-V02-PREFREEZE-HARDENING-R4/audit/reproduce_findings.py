"""Focused PRE-REPAIR audit on SHA-pinned NanoLab R3 modules.

This proves the old weaknesses; it is NOT an acceptance test for R4.
No oxDNA simulation, network request, or remote repository write is performed.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "source"))

import repro_v02_freeze_gate as gate
import repro_v02_seeds as seeds

SUBJECT = "ce13f0e9cb9536aaffddfff0a05c9a73f0870a21"
EXPECTED = {
    "repro_v02_freeze_gate.py": "3875167709de7db89ebb0ad4c33d5722a85621aa",
    "repro_v02_seeds.py": "81c1401c5d151202d6853cc46cdd81be0baff66a",
}

def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

for file, expected in EXPECTED.items():
    actual = blob_sha((ROOT / "source" / file).read_bytes())
    assert actual == expected, (file, actual, expected)

# Replay the exact committed R3 skip identities; not a new whole-tree scan.
skip_indices = {v: set(range(1, 11)) for v in seeds.DEFAULT_VARIANTS}
skip_indices["32b"].add(25)
skip_values = {
    seeds.derive_seed(seeds.DEFAULT_ANCHOR, seeds.replica_label(v, i))
    for v, indexes in skip_indices.items() for i in indexes
}
record = seeds.seed_record(tree_collision_scan=lambda value: value in skip_values)
assert record["record_sha256"] == "eb4ab3f891e17dd2b456a3870ed73b19e39d67bf51109b6cb47ca64524ce476b"
record_bytes = (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
assert blob_sha(record_bytes) == "0a8cd6ad5a6c0ccf1c70bceb4223c43339529a37"
(ROOT / "reconstructed_committed_seed_record_R3.json").write_bytes(record_bytes)

protocol = "0b = 64, 32b = 64, 11b = 10, 53b = 10\nN_min = 51\nwall budget = 560\nmax_runs = 356\n"
findings = []

def check(name: str, doc: str, rec: dict) -> None:
    result = gate.freeze_consistency_gate(doc, rec)
    findings.append({"test": name, "observed": result["gate"], "failures": result["failures"]})
    assert result["gate"] == "PASS", (name, result)

check("valid_committed_cardinalities_positive_control", protocol, record)
changed = copy.deepcopy(record); changed["seeds"]["11b"] = []; changed["seeds"]["53b"] = []
check("empty_both_control_seed_lists", protocol, changed)
changed = copy.deepcopy(record); changed["seeds"]["0b"][1] = changed["seeds"]["0b"][0]
check("duplicate_primary_seed_with_stale_digest", protocol, changed)
changed = copy.deepcopy(record); changed["record_sha256"] = "0" * 64
check("incorrect_record_digest", protocol, changed)
changed = copy.deepcopy(record); changed["bootstrap_seeds"] = {}
check("missing_bootstrap_seeds", protocol, changed)
changed = copy.deepcopy(record); changed["seeds"]["32b"][0] = 201004
check("historical_seed_in_primary", protocol, changed)
check("contradictory_protocol_nmin_wall_and_budget", protocol.replace("N_min = 51", "N_min = 64").replace("560", "1").replace("356", "1"), record)
check("contradictory_duplicate_cardinality_line", protocol + "0b = 1, 32b = 1, 11b = 1, 53b = 1\n", record)

with tempfile.TemporaryDirectory(prefix="nanolab-audit-") as directory:
    folder = Path(directory)
    scan = seeds.literal_tree_collision_scan(folder, [201004])
    process = subprocess.run(["git", "-C", str(folder), "grep", "-F", "-l", "--", "201004"], capture_output=True, text=True)
    assert process.returncode > 1 and scan["collision_count"] == 0
    findings.append({"test": "tree_scan_outside_git_repository", "git_exit_code": process.returncode, "observed": scan})
    subprocess.run(["git", "init", "-q", str(folder)], check=True)
    (folder / "evidence.txt").write_text("historical seed 201004\n")
    subprocess.run(["git", "-C", str(folder), "add", "evidence.txt"], check=True)
    subprocess.run(["git", "-C", str(folder), "-c", "user.name=Audit Fixture", "-c", "user.email=audit@example.invalid", "commit", "-qm", "fixture"], check=True)
    assert seeds.literal_tree_collision_scan(folder, [201004])["collision_count"] == 1
    (folder / "evidence.txt").write_text("worktree changed; canonical Git blob still contains the historical seed\n")
    dirty_scan = seeds.literal_tree_collision_scan(folder, [201004])
    assert dirty_scan["collision_count"] == 0
    findings.append({"test": "scan_observes_worktree_not_pinned_commit", "observed": dirty_scan})

replacement_collisions = {}
for variant, count in seeds.VARIANT_REPLICAS.items():
    index = count + 1
    value = seeds.derive_seed(seeds.DEFAULT_ANCHOR, seeds.replica_label(variant, index))
    assert value in record["seeds"][variant]
    replacement_collisions[variant] = {
        "documented_replacement_index_N_plus_1": index,
        "seed": value,
        "already_in_confirmatory_seed_set": True,
        "consumed_candidate_indices": count + len(skip_indices[variant]),
    }
findings.append({"test": "documented_N_plus_1_replacement_reuses_confirmatory_identity", "observed": replacement_collisions})
findings.append({"test": "integer_rounding_contract", "n_min_fraction": 51 / 64, "replacement_budget_fraction": 60 / 296})

output = {
    "subject_head": SUBJECT,
    "scope": "focused module-level audit; not full project tests, not scientific execution",
    "source_blob_sha1_verified": EXPECTED,
    "reconstructed_seed_record_blob_sha1": blob_sha(record_bytes),
    "defects_reproduced": True,
    "observations": findings,
}
(ROOT / "audit_results_reproduced.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(output, ensure_ascii=False, indent=2))
