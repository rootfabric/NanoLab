#!/usr/bin/env python3
"""Build EX-NL5-001-C-R1 run inputs (4 variants x 3 fresh-seed replicas).

Same frozen deviation list from the pinned author pro_CPU.in as the reviewed
NL3-002 PARAM/CONFIRM builders (steps, per-run seed, output names,
print_conf_interval=4000, print_energy_every=100, lastconf_file added,
subject topology/conf_file). Seeds are the FROZEN fresh seeds of
WO-NL5-001-C-R1 (drawn before any run; reference seeds are NOT reused).
Each run dir receives byte-verified copies of the digest-gated upstream files.

Exit codes: 0 = built, 3 = failure.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
RUN_ROOT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None

VARIANTS = {
    "0b":  {"steps": 200000, "seeds": [170085, 157480, 561483],
            "manifest": "docs/work/executions/EX-NL3-002-PROTO-R1/evidence/arm-manifest-0b.json"},
    "11b": {"steps": 200000, "seeds": [373439, 592596, 456410],
            "manifest": "docs/work/executions/EX-NL3-002-PARAM-11B-R1/evidence/arm-manifest-11b.json"},
    "32b": {"steps": 150000, "seeds": [399746, 801667, 659403],
            "manifest": "docs/work/executions/EX-NL3-002-PARAM-32B-R1/evidence/arm-manifest-32b.json"},
    "53b": {"steps": 150000, "seeds": [511532, 979551, 175554],
            "manifest": "docs/work/executions/EX-NL3-002-PARAM-53B-R1/evidence/arm-manifest-53b.json"},
}
PRINT_CONF_INTERVAL = 4000
PRINT_ENERGY_EVERY = 100
REFERENCE_SEEDS = {201004, 202008, 203012}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_input(src_text: str, variant: str, steps: int, run: dict) -> tuple[str, list]:
    key_map = {
        "steps": str(steps),
        "seed": str(run["seed"]),
        "topology": f"{variant}.top",
        "conf_file": f"{variant}.conf",
        "trajectory_file": f"{run['prefix']}_traj.dat",
        "energy_file": f"{run['prefix']}_energy.dat",
        "log_file": f"{run['prefix']}_log.dat",
        "print_conf_interval": str(PRINT_CONF_INTERVAL),
        "print_energy_every": str(PRINT_ENERGY_EVERY),
        "lastconf_file": f"{run['prefix']}_last.dat",
    }
    added_lastconf = "lastconf_file" not in {ln.split("=", 1)[0].strip() for ln in src_text.splitlines() if "=" in ln}
    deviations = []
    out = []
    for line in src_text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in key_map:
                old = line.split("=", 1)[1].strip()
                new = key_map[key]
                out.append(f"{key} = {new}")
                deviations.append({"key": key, "author_value": old, "run_value": new,
                                   "reason": "E2_PROTO_R1 frozen protocol deviations (as reviewed NL3-002 builders) / NL5-001-C fresh seed + per-run naming"})
                continue
        out.append(line)
    if added_lastconf:
        out.append("lastconf_file = " + key_map["lastconf_file"])
        deviations.append({"key": "lastconf_file", "author_value": None, "run_value": key_map["lastconf_file"],
                           "reason": "absent in author input, added (same as reviewed NL3-002 builders)"})
    return "\n".join(out) + "\n", deviations


def main() -> int:
    if RUN_ROOT is None or not RUN_ROOT.is_dir():
        print("usage: build_run_inputs.py <repo_root> <run_root>", file=sys.stderr)
        return 3
    src_dir = RUN_ROOT
    index = {"kind": "nanolab_reproduction_run_inputs", "execution_id": "EX-NL5-001-C-R1", "runs": []}
    for variant, spec in VARIANTS.items():
        for i, seed in enumerate(spec["seeds"], start=1):
            if seed in REFERENCE_SEEDS:
                print(f"FAIL: seed {seed} collides with reference seeds", file=sys.stderr)
                return 3
            run = {"run_id": f"NL5-001-C-{variant.upper()}-S{i:03d}", "prefix": f"s{i:03d}", "seed": seed}
            run_dir = RUN_ROOT / run["run_id"]
            run_dir.mkdir(parents=True, exist_ok=True)
            src_text = (src_dir / f"MD_Hinges__pro_CPU.in").read_text(encoding="utf-8")
            input_text, deviations = build_input(src_text, variant, spec["steps"], run)
            (run_dir / "input.in").write_text(input_text, encoding="utf-8")
            copies = {}
            for src_name, dest_name in ((f"MD_Hinges__{variant}.conf", f"{variant}.conf"),
                                        (f"MD_Hinges__{variant}.top", f"{variant}.top"),
                                        ("MD_Hinges__pro_CPU.in", "pro_CPU.in")):
                data = (src_dir / src_name).read_bytes()
                (run_dir / dest_name).write_bytes(data)
                copies[dest_name] = {"sha256": sha256(data), "size_bytes": len(data)}
            record = {
                "run_id": run["run_id"], "variant": variant, "seed": run["seed"],
                "steps": spec["steps"], "arm_manifest": spec["manifest"],
                "input_sha256": sha256(input_text.encode("utf-8")),
                "source_copies": copies, "deviations": deviations,
            }
            (run_dir / "input-build.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
            index["runs"].append({k: record[k] for k in ("run_id", "variant", "seed", "steps")})
            print(f"built {run['run_id']} seed={seed} steps={spec['steps']}")
    (RUN_ROOT / "run-inputs-index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
