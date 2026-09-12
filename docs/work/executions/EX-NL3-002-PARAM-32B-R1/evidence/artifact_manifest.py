"""Artifact manifests for EX-NL3-002-PARAM-32B-R1 runs: SHA-256 + size of every
run input/output (WSL side, outside Git; trajectories stay out of Git)."""
import json
import os
import subprocess
import sys

REPO = r"C:\NanoLab\nl3-002-param-32b"
EX = os.path.join(REPO, "docs", "work", "executions", "EX-NL3-002-PARAM-32B-R1")
sys.path.insert(0, os.path.join(REPO, "scripts"))
from e2.canonical import canonical_json  # noqa: E402

WSL_ROOT = "/home/yurig/nl3-002-param-32b/runs"
RUNS = [
    {"run_id": "PARAM-32B-S001", "prefix": "s001", "seed": 201004},
    {"run_id": "PARAM-32B-S002", "prefix": "s002", "seed": 202008},
    {"run_id": "PARAM-32B-S003", "prefix": "s003", "seed": 203012},
]


def wsl_stat(wsl_dir, name):
    out = subprocess.run(
        ["wsl", "-e", "bash", "-c",
         f"cd '{wsl_dir}' && sha256sum '{name}' && stat -c %s '{name}'"],
        capture_output=True, text=True, timeout=600,
    )
    if out.returncode != 0:
        return {"file": name, "error": out.stderr.strip()}
    digest = out.stdout.splitlines()[0].split()[0]
    size = int(out.stdout.splitlines()[1].strip())
    return {"file": name, "role": "input" if name in ("32b.top", "32b.conf", "pro_CPU.in", "input.in")
            else "output", "sha256": digest, "size_bytes": size, "location": wsl_dir}


def main() -> int:
    for run in RUNS:
        wsl_dir = f"{WSL_ROOT}/{run['run_id']}"
        p = run["prefix"]
        files = ["32b.top", "32b.conf", "pro_CPU.in", "input.in",
                 f"{p}_traj.dat", f"{p}_energy.dat", f"{p}_last.dat", f"{p}_log.dat",
                 "engine_stdout.txt", "engine_stderr.txt", "exit_code.txt"]
        manifest = {
            "schema_version": 1,
            "kind": "e2_param_artifacts_manifest",
            "execution_id": "EX-NL3-002-PARAM-32B-R1",
            "run_id": run["run_id"], "seed": run["seed"],
            "storage_location": wsl_dir + " (WSL, outside Git; raw artifacts not committed)",
            "files": [wsl_stat(wsl_dir, name) for name in files],
        }
        path = os.path.join(EX, "evidence", f"{p}-artifacts.manifest.json")
        with open(path, "w", encoding="utf-8", newline="\n") as h:
            h.write(canonical_json(manifest) + "\n")
        print(f"{run['run_id']}: manifest {len(manifest['files'])} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
