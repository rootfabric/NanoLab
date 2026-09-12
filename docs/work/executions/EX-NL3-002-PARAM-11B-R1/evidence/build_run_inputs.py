"""Build PARAM-11B run inputs (EX-NL3-002-PARAM-11B-R1) from the pinned author pro_CPU.in.

Per E2_PROTO_R1 §3 (inherited by WO-NL3-002-PARAM), deviations from pro_CPU.in
verbatim are exactly: steps=200000, per-run seed, output file names,
print_conf_interval=4000, print_energy_every=100, lastconf_file (absent in
author input, added), plus the subject change topology/conf_file 74b->11b.
Every deviation is recorded in PARAM-11B-S00X_deviations.json. All digest-gated
inputs (11b.top, 11b.conf, pro_CPU.in) and the built input are copied into each
run directory (lesson F-1) and byte-verified.
"""
import hashlib
import json
import os
import subprocess
import sys

REPO = r"C:\NanoLab\nl3-002-param-11b"
EX = os.path.join(REPO, "docs", "work", "executions", "EX-NL3-002-PARAM-11B-R1")
sys.path.insert(0, os.path.join(REPO, "scripts"))
from e2.canonical import canonical_json  # noqa: E402

SRC = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "nl3-002-param-11b-src")
SRC_FILES = {
    "MD_Hinges/11b.top": "11b.top",
    "MD_Hinges/11b.conf": "11b.conf",
    "MD_Hinges/pro_CPU.in": "pro_CPU.in",
}
RUNS = [
    {"run_id": "PARAM-11B-S001", "prefix": "s001", "seed": 201004},
    {"run_id": "PARAM-11B-S002", "prefix": "s002", "seed": 202008},
    {"run_id": "PARAM-11B-S003", "prefix": "s003", "seed": 203012},
]
WSL_ROOT = "/home/yurig/nl3-002-param-11b/runs"
STEPS = 200000
PRINT_CONF_INTERVAL = 4000
PRINT_ENERGY_EVERY = 100
REASON = "E2_PROTO_R1 frozen protocol (inherited by WO-NL3-002-PARAM) / per-run naming"


def build_input(src_text: str, run: dict):
    deviations = []
    lines = src_text.splitlines()
    out = []
    seen = set()
    key_map = {
        "steps": str(STEPS),
        "seed": str(run["seed"]),
        "topology": "11b.top",
        "conf_file": "11b.conf",
        "trajectory_file": f"{run['prefix']}_traj.dat",
        "energy_file": f"{run['prefix']}_energy.dat",
        "log_file": f"{run['prefix']}_log.dat",
        "print_conf_interval": str(PRINT_CONF_INTERVAL),
        "print_energy_every": str(PRINT_ENERGY_EVERY),
    }
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in key_map:
                value = key_map[key]
                if line.split("=", 1)[1].strip() != value:
                    deviations.append({"key": key, "author": line.split("=", 1)[1].strip(),
                                       "run": value, "reason": REASON})
                out.append(f"{key} = {value}")
                seen.add(key)
                continue
        out.append(line)
    out.append(f"lastconf_file = {run['prefix']}_last.dat")
    deviations.append({"key": "lastconf_file", "author": None,
                       "run": f"{run['prefix']}_last.dat",
                       "reason": "author input has no lastconf_file; protocol records final configuration"})
    missing = sorted(set(key_map) - seen)
    if missing:
        raise RuntimeError(f"keys missing from author input: {missing}")
    deviations.sort(key=lambda d: d["key"])
    return "\n".join(out) + "\n", deviations


def wsl(cmd: str) -> str:
    res = subprocess.run(["wsl", "-e", "bash", "-c", cmd], capture_output=True, text=True, timeout=300)
    if res.returncode != 0:
        raise RuntimeError(f"wsl cmd failed: {cmd}\n{res.stderr}")
    return res.stdout


def main() -> int:
    with open(os.path.join(SRC, "MD_Hinges__pro_CPU.in"), "r", encoding="utf-8") as h:
        src_text = h.read()
    win_src = os.path.join(SRC, "").replace("\\", "/").replace("C:", "/mnt/c")
    report = {"schema_version": 1, "kind": "e2_param_input_build",
              "execution_id": "EX-NL3-002-PARAM-11B-R1", "variant": "11b",
              "protocol": "docs/research/E2_PROTO_R1.md (frozen, inherited)",
              "steps": STEPS, "print_conf_interval": PRINT_CONF_INTERVAL,
              "print_energy_every": PRINT_ENERGY_EVERY, "runs": {}}
    for run in RUNS:
        wsl_dir = f"{WSL_ROOT}/{run['run_id']}"
        wsl(f"mkdir -p '{wsl_dir}'")
        for src_name, dest in SRC_FILES.items():
            wsl(f"cp '{win_src}{src_name.replace('/', '__')}' '{wsl_dir}/{dest}'")
        text, deviations = build_input(src_text, run)
        with open(os.path.join(EX, "evidence", f"{run['run_id']}_deviations.json"), "w",
                  encoding="utf-8", newline="\n") as h:
            h.write(canonical_json({"schema_version": 1,
                                    "kind": "e2_param_input_deviations",
                                    "execution_id": "EX-NL3-002-PARAM-11B-R1",
                                    "run_id": run["run_id"],
                                    "source_input": "MD_Hinges/pro_CPU.in @ 23fd1ff (digest-gated, verbatim base)",
                                    "deviations": deviations}) + "\n")
        win_input = os.path.join(EX, "evidence", f"{run['prefix']}_input.in")
        with open(win_input, "w", encoding="utf-8", newline="\n") as h:
            h.write(text)
        wsl(f"cp '{win_input.replace(chr(92), '/').replace('C:', '/mnt/c')}' '{wsl_dir}/input.in'")
        checks = {}
        for src_name, dest in list(SRC_FILES.items()) + [("INPUT", "input.in")]:
            if src_name == "INPUT":
                win_sha = hashlib.sha256(open(win_input, "rb").read()).hexdigest()
            else:
                with open(os.path.join(SRC, src_name.replace("/", "__")), "rb") as h:
                    win_sha = hashlib.sha256(h.read()).hexdigest()
            wsl_sha = wsl(f"sha256sum '{wsl_dir}/{dest}'").split()[0]
            checks[dest] = {"expected_sha256": win_sha, "copy_sha256": wsl_sha,
                            "match": win_sha == wsl_sha}
        all_ok = all(c["match"] for c in checks.values())
        report["runs"][run["run_id"]] = {
            "wsl_dir": wsl_dir, "seed": run["seed"], "prefix": run["prefix"],
            "input_copied_and_verified": all_ok, "copy_checks": checks,
            "deviations_count": len(deviations),
        }
        print(run["run_id"], "copy_verify:", "PASS" if all_ok else "FAIL")
    report["all_inputs_verified"] = all(r["input_copied_and_verified"] for r in report["runs"].values())
    with open(os.path.join(EX, "evidence", "input-build.json"), "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(report) + "\n")
    return 0 if report["all_inputs_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
