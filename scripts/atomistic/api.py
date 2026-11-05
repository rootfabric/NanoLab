"""Stdlib-only validation, isolated execution and integrity contract."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

CLAIM = "SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED"
PINS = {"ase": "3.26.0", "numpy": "2.2.6", "scipy": "1.15.3", "matplotlib": "3.10.3"}
MAX_ATOMS = 4096
MAX_MD_STEPS = 2000
MAX_FRAMES = 201
MAX_WALL_SECONDS = 120
MAX_OUTPUT_BYTES = 256 * 1024 * 1024
MAX_MEMORY_BYTES = 2 * 1024**3


class ValidationError(ValueError):
    pass


class RunError(RuntimeError):
    pass


def _keys(value, expected, name):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValidationError(f"{name}: expected exactly {sorted(expected)}")


def _number(value, low, high, name, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{name}: expected number")
    if not low <= value <= high or not math.isfinite(value):
        raise ValidationError(f"{name}: expected finite value in [{low}, {high}]")
    if integer and not isinstance(value, int):
        raise ValidationError(f"{name}: expected integer")
    return value


def validate_config(config):
    """Strict units and allowlist; never import a simulation dependency."""
    _keys(config, ["schema_version", "material", "model", "structure", "relaxation", "md"], "config")
    if config["schema_version"] != "atomistic-config-v1":
        raise ValidationError("unsupported config schema")
    if config["material"] != "Cu" or config["model"] != "ASE_EMT_Cu":
        raise ValidationError("only Cu with ASE_EMT_Cu is allowed")
    s, r, m = config["structure"], config["relaxation"], config["md"]
    _keys(s, ["kind", "size", "lattice_constant_angstrom"], "structure")
    if s["kind"] != "fcc_cuboid" or not isinstance(s["size"], list) or len(s["size"]) != 3:
        raise ValidationError("structure: expected fcc_cuboid with three cell counts")
    for count in s["size"]:
        _number(count, 1, 16, "structure.size", integer=True)
    if 4 * math.prod(s["size"]) > MAX_ATOMS:
        raise ValidationError("atom cap exceeded")
    _number(s["lattice_constant_angstrom"], 3.4, 3.8, "lattice_constant_angstrom")
    _keys(r, ["max_steps", "fmax_ev_per_angstrom"], "relaxation")
    _number(r["max_steps"], 1, 500, "relaxation.max_steps", integer=True)
    _number(r["fmax_ev_per_angstrom"], 0.001, 0.1, "fmax_ev_per_angstrom")
    _keys(m, ["steps", "timestep_fs", "temperature_k", "friction_per_fs", "sample_interval", "seed"], "md")
    _number(m["steps"], 1, MAX_MD_STEPS, "md.steps", integer=True)
    _number(m["sample_interval"], 1, MAX_MD_STEPS, "sample_interval", integer=True)
    if math.ceil(m["steps"] / m["sample_interval"]) + 1 > MAX_FRAMES:
        raise ValidationError("trajectory frame cap exceeded; increase sample_interval")
    _number(m["timestep_fs"], 0.1, 2.0, "timestep_fs")
    _number(m["temperature_k"], 1, 600, "temperature_k")
    _number(m["friction_per_fs"], 0.0001, 0.1, "friction_per_fs")
    _number(m["seed"], 0, 2**32 - 1, "seed", integer=True)
    return json.loads(json.dumps(config, allow_nan=False))


def read_config(path):
    path = Path(path)
    if path.stat().st_size > 65536:
        raise ValidationError("config exceeds 64 KiB")
    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValidationError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return validate_config(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates))


def write_json(path, data):
    # Every run directory is new; files are finalized before manifest creation.
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def digest(path):
    path = Path(path)
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "size_bytes": path.stat().st_size}


def _safe_root(path):
    path = Path(path).absolute()
    if ".." in path.parts:
        raise ValidationError("parent traversal in output_root")
    for component in [path, *path.parents]:
        if component.is_symlink():
            raise ValidationError("symlinks in output_root are forbidden")
    path.mkdir(parents=True, exist_ok=True)
    return path


def _subject():
    root = Path(__file__).resolve().parents[2]
    result = {"adapter_sources": {p.name: digest(p) for p in sorted(Path(__file__).parent.glob("*.py")) if p.name != "web.py"}}
    try:
        result["git_head"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, timeout=5).strip()
        result["git_tree"] = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=root, text=True, timeout=5).strip()
        result["dirty_tracked_files"] = subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=root, text=True, timeout=5).splitlines()
    except (OSError, subprocess.SubprocessError):
        result["git_head"] = None
    return result


def protocol(config, run_id, timeout_seconds):
    import importlib.metadata
    try:
        distribution = importlib.metadata.distribution("ase")
        model_digest = digest(distribution.locate_file("ase/calculators/emt.py"))
    except (importlib.metadata.PackageNotFoundError, OSError):
        model_digest = None  # stdlib unit-test paths can still record failed launch
    return {
        "schema_version": "atomistic-protocol-v1", "revision": "CU-EMT-DEMO-R1",
        "run_id": run_id, "claim_ceiling": CLAIM, "scientific_outcome": "NOT_EVALUATED",
        "objective": "Bounded real Cu cluster relaxation and short MD software demonstration",
        "config": config, "source_model": {"id": "ASE_EMT_Cu", "ase_version": PINS["ase"], "module_digest": model_digest, "calculator": "ase.calculators.emt.EMT(asap_cutoff=False)", "boundary": "nonperiodic finite FCC cuboid", "license": "LGPL-2.1-or-later (ASE distribution)", "upstream_source": "https://gitlab.com/ase/ase/-/blob/3.26.0/ase/calculators/emt.py"},
        "dependency_pins": PINS, "subject": _subject(),
        "observables": {"positions": "angstrom", "energy": "eV total", "temperature": "K, ASE 3N kinetic definition", "time": "fs since MD start", "max_force": "eV/angstrom"},
        "analysis": "Record every MD step in metrics; trajectory interval plus initial/final. No equilibrium or uncertainty inference.",
        "numerical_control": {"method": "central difference of Cu EMT energy at displaced atom x coordinate", "displacement_angstrom": 1e-5, "absolute_force_tolerance_ev_per_angstrom": 1e-4, "interpretation": "same-engine internal derivative consistency, not independent material validation"},
        "budget": {"max_atoms": MAX_ATOMS, "max_md_steps": MAX_MD_STEPS, "max_frames": MAX_FRAMES, "wall_seconds": timeout_seconds, "cpu_seconds": MAX_WALL_SECONDS, "address_space_bytes": MAX_MEMORY_BYTES, "output_bytes": MAX_OUTPUT_BYTES, "threads": 1},
        "stop_conditions": ["nonfinite positions/forces/energy/temperature", "relaxation not converged", "force derivative check failed", "integrity failure", "timeout/resource cap/cancellation"],
        "seed_policy": "single exploratory seed from config; no retries or replicas within run ID",
        "exclusions": "none; failed IDs retained and never overwritten",
        "limitations": ["Engineering demonstration only", "No reviewed external material benchmark", "No E6/P0 or NL checkpoint acceptance", "Short thermostat trajectory is not a stability or equilibrium result", "Current container is not accepted U1/U2"]}


def verify_run(run_dir):
    """Verify exact bytes and structural completeness without executing ASE."""
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text())
    if manifest.get("schema_version") != "atomistic-manifest-v1" or manifest.get("claim_ceiling") != CLAIM:
        raise RunError("invalid manifest contract")
    required = {"config.json", "protocol.json", "worker.log", "metrics.json", "trajectory.json", "report.md", "environment.json", "numerical-control.json", "relaxation.json", "relaxation.log"}
    if manifest.get("status") == "COMPLETED" and not required.issubset(manifest["files"]):
        raise RunError("incomplete successful manifest")
    for name, expected in manifest["files"].items():
        if not isinstance(name, str) or Path(name).name != name or name in {".", "..", "manifest.json"}:
            raise RunError("unsafe manifest path")
        target = run_dir / name
        if target.is_symlink() or not target.is_file() or digest(target) != expected:
            raise RunError(f"artifact integrity failure: {name}")
    return manifest


def run(config, output_root, run_id, *, timeout_seconds=MAX_WALL_SECONDS, cancel_event=None):
    config = validate_config(config)
    if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", run_id):
        raise ValidationError("unsafe run_id")
    _number(timeout_seconds, 1, MAX_WALL_SECONDS, "timeout_seconds", integer=True)
    run_dir = _safe_root(output_root) / run_id
    try:
        run_dir.mkdir()  # exclusive, no overwrite, including failed IDs
    except FileExistsError as exc:
        raise ValidationError("run_id already exists; use a new ID") from exc
    started = datetime.now(timezone.utc).isoformat()
    write_json(run_dir / "config.json", config)
    frozen = protocol(config, run_id, timeout_seconds)
    frozen["input_config"] = dict(digest(run_dir / "config.json"), filename="config.json")
    write_json(run_dir / "protocol.json", frozen)
    manifest = {"schema_version": "atomistic-manifest-v1", "run_id": run_id, "status": "STARTED", "execution_outcome": "RUNNING", "scientific_outcome": "NOT_EVALUATED", "claim_ceiling": CLAIM, "started_utc": started, "subject": frozen["subject"], "source_model": frozen["source_model"], "dependency_pins": PINS, "files": {}}
    write_json(run_dir / "manifest.json", manifest)
    from . import budget
    try:
        reservation = budget.reserve(run_dir, timeout_seconds, MAX_OUTPUT_BYTES)
    except Exception as exc:
        manifest.update(status="FAILED", execution_outcome="BLOCKED_ENVIRONMENT", failure_class="MISSION_BUDGET_BLOCKED", failure_detail=str(exc))
        manifest["files"] = {p.name: digest(p) for p in run_dir.iterdir() if p.is_file() and p.name != "manifest.json"}
        write_json(run_dir / "manifest.json", manifest)
        raise RunError(f"mission budget blocked: {exc}; retained evidence: {run_dir}") from exc
    manifest["mission_id"] = budget.MISSION_ID
    manifest["reservation_id"] = reservation
    env = {key: value for key, value in os.environ.items() if key in {"PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "SYSTEMROOT"}}
    for key in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"]:
        env[key] = "1"
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    env["PYTHONNOUSERSITE"] = "1"
    t0, failure, code = time.monotonic(), None, None
    child = None
    try:
        with (run_dir / "worker.log").open("xb") as log:
            child = subprocess.Popen([sys.executable, "-m", "atomistic.worker", str(run_dir)], env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            while child.poll() is None:
                if cancel_event is not None and cancel_event.is_set():
                    failure = "CANCELLED"
                    break
                if time.monotonic() - t0 > timeout_seconds:
                    failure = "WALL_TIMEOUT"
                    break
                if sum(p.stat().st_size for p in run_dir.iterdir() if p.is_file()) > MAX_OUTPUT_BYTES:
                    failure = "OUTPUT_CAP"
                    break
                time.sleep(0.05)
            if failure:
                child.terminate()
                try:
                    child.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    child.kill()
            code = child.wait(timeout=5)
        if code != 0 and failure is None:
            failure = "WORKER_FAILED"
        if failure is None:
            for name in ["metrics.json", "trajectory.json"]:
                data = json.loads((run_dir / name).read_text())
                json.dumps(data, allow_nan=False)
    except Exception as exc:
        if child is not None and child.poll() is None:
            child.kill()
            child.wait()
        failure = failure or f"EXECUTION_ERROR:{type(exc).__name__}"
    manifest.update(status="FAILED" if failure else "COMPLETED", execution_outcome="FAILED_TECHNICAL" if failure else "COMPLETED", failure_class=failure, exit_code=code, ended_utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic() - t0)
    manifest["files"] = {p.name: digest(p) for p in sorted(run_dir.iterdir()) if p.is_file() and p.name != "manifest.json"}
    write_json(run_dir / "manifest.json", manifest)
    budget.finish(reservation, manifest["status"], manifest["wall_seconds"], sum(p.stat().st_size for p in run_dir.iterdir() if p.is_file()))
    verify_run(run_dir)
    if failure:
        raise RunError(f"{failure}; retained evidence: {run_dir}")
    return {"run_id": run_id, "run_dir": str(run_dir), "status": "COMPLETED", "trajectory": json.loads((run_dir / "trajectory.json").read_text()), "metrics": json.loads((run_dir / "metrics.json").read_text()), "manifest": manifest}
