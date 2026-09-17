#!/usr/bin/env python3
"""Build the EX-NL5-001-C-R1 artifact manifest for raw run artifacts.

Raw trajectories/energies/logs live OUTSIDE Git (disposable run dir); this
manifest records sha256 + size + storage_location for every artifact so raw
data remains addressable by digest (provenance rule).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RUN_ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
RUNS = [f"NL5-001-C-{v}-S{i:03d}" for v in ("0B", "11B", "32B", "53B") for i in (1, 2, 3)]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    entries = {}
    for rid in RUNS:
        run_dir = RUN_ROOT / rid
        for name in (f"s{rid[-3:].lower()}_traj.dat", f"s{rid[-3:].lower()}_energy.dat",
                     f"s{rid[-3:].lower()}_log.dat", f"s{rid[-3:].lower()}_last.dat",
                     "engine_stdout.txt", "engine_stderr.txt", "exit_code.txt", "input.in",
                     "input-build.json"):
            p = run_dir / name
            if not p.is_file():
                entries[f"{rid}/{name}"] = {"status": "MISSING"}
                continue
            entries[f"{rid}/{name}"] = {
                "sha256": sha256(p), "size_bytes": p.stat().st_size,
                "storage_location": f"local:{str(p)}",
            }
    for name in ("run-reports.json", "run-reports-live.json", "input-download-verification.json",
                 "run-inputs-index.json"):
        p = RUN_ROOT / name
        if p.is_file():
            entries[name] = {"sha256": sha256(p), "size_bytes": p.stat().st_size,
                             "storage_location": f"local:{str(p)}"}
    manifest = {
        "schema_version": 1,
        "kind": "nl5_001_c_artifact_manifest",
        "execution_id": "EX-NL5-001-C-R1",
        "artifact_policy": "raw artifacts outside Git; digest+size+location recorded (provenance rule)",
        "durable_cache": "upstream inputs REFERENCE_ONLY: disposable run dir, not archived",
        "artifacts": entries,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"manifest: {len(entries)} entries -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
