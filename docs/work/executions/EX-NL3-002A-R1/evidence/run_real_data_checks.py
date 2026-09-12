"""EX-NL3-002A-R1 real-data cross-check (download-on-run, G1 = B).

Downloads the three pinned surfaces needed for the pre-E2 checks, verifies
every byte against scripts/hinge_family/source_pins.json (size + git blob
SHA-1 + SHA-256), runs the frozen pre-E2 tools on them, publishes only the
JSON reports, and deletes the downloaded bytes (no durable cache, U4 = NO).

Run from the repository root with PYTHONPATH=scripts:
    python docs/work/executions/EX-NL3-002A-R1/evidence/run_real_data_checks.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from e2 import compat_audit, restraints_inventory, topology_mapping  # noqa: E402
from e2.canonical import canonical_json  # noqa: E402
from e2.digests import git_blob_sha1, sha256_file  # noqa: E402
from hinge_family.cadnano_design import Design  # noqa: E402
from hinge_family.oxdna_topology import Topology  # noqa: E402

EVIDENCE_DIR = os.path.dirname(os.path.abspath(__file__))
PINS_PATH = os.path.join(ROOT, "scripts", "hinge_family", "source_pins.json")

WANTED = [
    "Design_Hinges/0b.json",
    "MD_Hinges/0b.top",
    "MD_Hinges/pro_CPU.in",
]


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "nanolab-pre-e2-check/1 (digest-gated)"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def main() -> int:
    with open(PINS_PATH, "r", encoding="utf-8", newline="") as handle:
        pins = json.load(handle)
    commit = pins["source"]["commit"]
    reports = {"schema_version": 1, "kind": "e2a_real_data_cross_check", "files": {}, "tools": {}}
    workdir = tempfile.mkdtemp(prefix="nl3-002a-src-")
    try:
        for path in WANTED:
            pin = pins["files"][path]
            url = f"https://raw.githubusercontent.com/{pins['source']['repository']}/{commit}/{path}"
            data = fetch(url)
            local = os.path.join(workdir, path.replace("/", "__"))
            with open(local, "wb") as handle:
                handle.write(data)
            facts = {
                "url": url,
                "size_bytes_expected": pin["size_bytes"],
                "size_bytes_actual": len(data),
                "blob_sha1_expected": pin["blob_sha1"],
                "blob_sha1_actual": git_blob_sha1(data),
                "sha256_expected": pin.get("sha256"),
                "sha256_actual": sha256_file(local),
                "retained": False,
            }
            facts["size_match"] = facts["size_bytes_expected"] == facts["size_bytes_actual"]
            facts["blob_match"] = facts["blob_sha1_expected"] == facts["blob_sha1_actual"]
            facts["sha256_match"] = (
                facts["sha256_expected"] in (None, facts["sha256_actual"])
            )
            facts["digest_gate"] = (
                facts["size_match"] and facts["blob_match"] and facts["sha256_match"]
            )
            if not facts["digest_gate"]:
                raise SystemExit(f"DIGEST_GATE_FAILED for {path}: {json.dumps(facts)}")
            reports["files"][path] = facts

        # compat audit + restraints on the pinned production input
        with open(os.path.join(workdir, "MD_Hinges__pro_CPU.in"), "r", encoding="utf-8", newline="") as handle:
            input_text = handle.read()
        reports["tools"]["compat_audit"] = compat_audit.audit(input_text, compat_audit.load_registry())
        reports["tools"]["restraints_inventory"] = restraints_inventory.combined(input_text, {})

        # design -> topology mapping on the real first hinge (gap G2)
        with open(os.path.join(workdir, "Design_Hinges__0b.json"), "r", encoding="utf-8", newline="") as handle:
            design_text = handle.read()
        with open(os.path.join(workdir, "MD_Hinges__0b.top"), "r", encoding="utf-8", newline="") as handle:
            topology_text = handle.read()
        mapping = topology_mapping.map_design_to_topology(
            Design.parse(design_text), Topology.parse(topology_text)
        )
        mapping["inputs"] = {
            "design": "Design_Hinges/0b.json",
            "topology": "MD_Hinges/0b.top",
            "digest_gate": "PASS (see files)",
        }
        reports["tools"]["topology_mapping"] = mapping
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        reports["cleanup"] = {"workdir_removed": True, "durable_cache": "none (U4 = NO)"}

    out_path = os.path.join(EVIDENCE_DIR, "real-data-cross-check-report.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json(reports))
    print(f"report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
