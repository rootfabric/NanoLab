"""Tiny persistent mission quota shared by worktrees, CLI and UI. Not a scheduler."""
import contextlib
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
import uuid

MISSION_ID = "WO-ATOMISTIC-PRODUCT-R1"
MAX_RUNS = 8
MAX_SECONDS = 1200
MAX_BYTES = 2 * 1024**3


def mission_directory():
    # A changed output_root does not reset this mission's grant.
    explicit = os.environ.get("NANOLAB_ATOMISTIC_MISSION_ROOT")
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            raise RuntimeError("NANOLAB_ATOMISTIC_MISSION_ROOT must be absolute")
        return path
    root = Path(__file__).resolve().parents[2]
    try:
        common = subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=root, text=True, timeout=5).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("nonGit installation requires fixed NANOLAB_ATOMISTIC_MISSION_ROOT") from exc
    return (root / common).resolve() / "nanolab-atomistic"


@contextlib.contextmanager
def _locked():
    directory = mission_directory()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{MISSION_ID}.json"
    with (directory / f"{MISSION_ID}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.exists():
            data = json.loads(path.read_text())
            if data.get("mission_id") != MISSION_ID or data.get("schema_version") != "atomistic-mission-budget-v1" or not isinstance(data.get("runs"), list):
                raise RuntimeError("invalid persistent mission ledger; operator audit required")
        else:
            data = {"schema_version": "atomistic-mission-budget-v1", "mission_id": MISSION_ID, "max_runs": MAX_RUNS, "max_seconds": MAX_SECONDS, "max_output_bytes": MAX_BYTES, "runs": []}
        yield data
        temporary = directory / f".{MISSION_ID}.{uuid.uuid4().hex}.tmp"
        with temporary.open("x") as output:
            output.write(json.dumps(data, indent=2, allow_nan=False) + "\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)


def reserve(run_dir, seconds, max_output_bytes):
    with _locked() as ledger:
        runs = ledger["runs"]
        if any(row["status"] == "RUNNING" for row in runs):
            raise RuntimeError("mission already has an active reservation; stale reservations require operator audit")
        if len(runs) >= MAX_RUNS:
            raise RuntimeError("mission pilot count exhausted")
        if sum(row["charged_seconds"] for row in runs) + seconds > MAX_SECONDS:
            raise RuntimeError("mission compute budget exhausted")
        if sum(row["charged_bytes"] for row in runs) + max_output_bytes > MAX_BYTES:
            raise RuntimeError("mission output budget exhausted")
        reservation = uuid.uuid4().hex
        runs.append({"reservation_id": reservation, "run_dir": str(Path(run_dir).absolute()), "status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(), "owner_pid": os.getpid(), "charged_seconds": seconds, "charged_bytes": max_output_bytes})
        return reservation


def finish(reservation, status, wall_seconds, output_bytes):
    with _locked() as ledger:
        matches = [row for row in ledger["runs"] if row["reservation_id"] == reservation]
        if len(matches) != 1 or matches[0]["status"] != "RUNNING":
            raise RuntimeError("invalid mission reservation completion")
        row = matches[0]
        row.update(status=status, ended_utc=datetime.now(timezone.utc).isoformat(), charged_seconds=wall_seconds, charged_bytes=output_bytes)
