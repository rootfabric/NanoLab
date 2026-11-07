"""Execute hosted workflow's five gates once in a clean detached clone."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import time

logs = Path(__file__).resolve().parent
assert len(sys.argv) == 2
expected = sys.argv[1]
assert subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() == expected
assert not subprocess.check_output(["git", "status", "--porcelain"], text=True)
assert importlib.util.find_spec("ase") is None, "ASE must be unavailable during gates"

env = os.environ.copy()
for name in ("NANOLAB_REAL_ATOMISTIC_TEST", "NANOLAB_ATOMISTIC_OUTPUT_ROOT", "NANOLAB_ATOMISTIC_RUN_ID", "PYTHONPATH", "VIRTUAL_ENV"):
    env.pop(name, None)
env["PYTHONDONTWRITEBYTECODE"] = "1"
env["PYTHONNOUSERSITE"] = "1"
module_env = {**env, "PYTHONPATH": "scripts"}
commands = (
    ("check-json", [sys.executable, "-m", "harness.batch_validate", "json", "--root", "."], module_env),
    ("check-consistency", [sys.executable, "-m", "harness.cli", "check-consistency", "--root", "."], module_env),
    ("check-executions", [sys.executable, "-m", "harness.batch_validate", "executions", "--root", "."], module_env),
    ("check-workflow-lint", [sys.executable, "-m", "harness.workflow_lint", "--root", "."], module_env),
    ("check-unittest", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-v"], env),
    ("reference-cli", [sys.executable, "-m", "atomistic.reference"], module_env),
)

def run(spec):
    name, argv, execution_env = spec
    start = time.monotonic()
    result = subprocess.run(argv, env=execution_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
    elapsed = time.monotonic() - start
    payload = result.stdout
    (logs / f"{name}.txt").write_bytes(payload)
    return name, argv, execution_env.get("PYTHONPATH", ""), result.returncode, elapsed, hashlib.sha256(payload).hexdigest(), len(payload)

print("UTC", datetime.now(timezone.utc).isoformat(), flush=True)
print("Python", sys.version.replace("\n", " "), flush=True)
print("subject", expected, subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip(), flush=True)
print("NANOLAB_REAL_ATOMISTIC_TEST unset; ASE not available; PYTHONNOUSERSITE=1", flush=True)
with ThreadPoolExecutor(max_workers=len(commands)) as pool:
    results = list(pool.map(run, commands))
for name, argv, path, code, elapsed, digest, size in results:
    print(f"{name}: exit={code} elapsed_s={elapsed:.3f} log_sha256={digest} log_bytes={size} PYTHONPATH={path!r} argv={argv!r}")
assert not subprocess.check_output(["git", "status", "--porcelain"], text=True)
print("clean detached checkout unchanged")
sys.exit(int(any(code for _, _, _, code, _, _, _ in results)))
