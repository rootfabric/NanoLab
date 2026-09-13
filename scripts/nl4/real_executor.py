"""Real ExecutorAdapter for NL4 (WO-NL4-002): oxDNA via WSL, digest-gated inputs.

Implements the same ``ExecutorAdapter`` interface as ``MockExecutor``
(``estimate_wall_seconds`` / ``run``), so the Controller can drive it
unchanged. Per run:

1. digest-gated download-on-run of the variant ``top``/``conf`` (plus
   ``pro_CPU.in`` once) against ``scripts/hinge_family/source_pins.json``
   (size + blob SHA-1 mandatory; SHA-256 compared when pinned, otherwise
   computed at first download and recorded);
2. input build from the verbatim ``pro_CPU.in`` template (E2_PROTO style:
   DNA2 / salt 0.5 / 300K / CPU / double; steps / seed / per-run output
   names / print_conf_interval=4000 / print_energy_every=100 /
   lastconf_file; every deviation recorded);
3. launch of the pinned WSL oxDNA binary in
   ``/home/yurig/nl4-002-e3/runs/<RUN_ID>/`` (setsid/nohup launcher, exit
   code to file, hard wall cap);
4. analysis via ``scripts/e2/observables.py`` v2 (mutual) with the frozen
   per-variant arm manifest + E2_PROTO_R1 §4 frame gates.

``run_parallel`` executes a whole arm (5 runs) concurrently; the results are
then replayed through the Controller for canonical budget accounting.

Source bytes live only in a Windows temp dir outside Git (G1 = B, no durable
cache) and are deleted by the runner after the execution.

stdlib-only plus the frozen e2/hinge_family toolchain; no physics here
beyond invoking the pinned engine.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import shutil
import subprocess
import sys
import time
import urllib.request

try:
    from .controller import ExecutorAdapter
except ImportError:  # direct module import during bring-up / tests
    ExecutorAdapter = object

try:
    from e2.canonical import canonical_json
except ImportError:  # pragma: no cover - path setup handled by caller
    from ..e2.canonical import canonical_json

try:
    from e2.digests import git_blob_sha1, sha256_bytes
except ImportError:  # pragma: no cover
    from ..e2.digests import git_blob_sha1, sha256_bytes

try:
    from e2 import observables as obs
    from hinge_family.oxdna_topology import Topology
except ImportError:  # pragma: no cover
    from ..e2 import observables as obs
    from ..hinge_family.oxdna_topology import Topology

# ------------------------------------------------------------------ constants
ENGINE = "/home/yurig/nl1-002/build-oxdna-cpu/bin/oxDNA"
ENGINE_SOURCE_COMMIT = "00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591"
WSL_RUNS_ROOT = "/home/yurig/nl4-002-e3/runs"
DOWNLOAD_BASE = (
    "https://raw.githubusercontent.com/gauravarya77/"
    "DNA-hinge-simulations/23fd1ff7731e9017bd776f49206dc42d70d9fe91/"
)
SOURCE_TEMP_SUBDIR = "nl4-002-e3-src"

STEPS_FIXED = 50000  # WO-NL4-002: 5 runs x 50000 steps per agent
PRINT_CONF_INTERVAL = 4000
PRINT_ENERGY_EVERY = 100
RUN_WALL_CAP_S = 1.2 * 3600  # WO-NL4-002 hard cap per run

# E2_PROTO_R1 §4 frozen frame gates (mirrored by nl4.scoring)
GATE_LBF_MAX = 0.1078
GATE_PF2_MIN = 0.50
GATE_DISP_MAX = 20.0

# frozen arm manifests, relative to the repo root
ARM_MANIFESTS = {
    "0b": "docs/work/executions/EX-NL3-002-PROTO-R1/evidence/arm-manifest-0b.json",
    "11b": "docs/work/executions/EX-NL3-002-PARAM-11B-R1/evidence/arm-manifest-11b.json",
    "32b": "docs/work/executions/EX-NL3-002-PARAM-32B-R1/evidence/arm-manifest-32b.json",
    "53b": "docs/work/executions/EX-NL3-002-PARAM-53B-R1/evidence/arm-manifest-53b.json",
}
# 74b is excluded from the E3 candidate space at the runner level (BLOCKED
# status in EX-NL3-002-PARAM-74B-R1); allowlist.json itself is NOT modified.
E3_VARIANTS = ("0b", "11b", "32b", "53b")

DEVIATION_REASON = "WO-NL4-002 E3 frozen protocol / per-run naming"


def now_utc() -> str:
    import datetime

    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def candidate_digest(candidate: dict) -> str:
    """Same canonical candidate digest the mock executor uses."""
    return hashlib.sha256(
        canonical_json(
            {
                "variant": candidate["variant"],
                "steps": candidate["steps"],
                "seed": candidate["seed"],
            }
        ).encode("utf-8")
    ).hexdigest()


def to_wsl_path(win_path: str) -> str:
    return win_path.replace("\\", "/").replace("C:", "/mnt/c")


def wsl(cmd: str, timeout: int = 300) -> str:
    res = subprocess.run(
        ["wsl", "-e", "bash", "-c", cmd], capture_output=True, text=True, timeout=timeout
    )
    if res.returncode != 0:
        raise RuntimeError(f"wsl command failed: {cmd}\nstdout: {res.stdout}\nstderr: {res.stderr}")
    return res.stdout


def wsl_read(path_wsl: str, tmp_root: str) -> str:
    """Copy a file from the WSL filesystem to Windows temp and read it."""
    os.makedirs(tmp_root, exist_ok=True)
    local = os.path.join(tmp_root, path_wsl.replace("/", "__"))
    src = path_wsl.replace("/home/yurig", r"\\wsl.localhost\Ubuntu\home\yurig")
    shutil.copyfile(src, local)
    with open(local, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


# ------------------------------------------------------------ digest gating
def verify_source_bytes(name: str, data: bytes, pin: dict) -> dict:
    """Digest gate for one downloaded source file.

    size + blob SHA-1 are mandatory; SHA-256 is compared when the registry
    pins a verified value, otherwise the computed-at-first-download value is
    recorded (NOT_VERIFIED entries in source_pins.json).
    """
    size_ok = len(data) == pin["size_bytes"]
    blob = git_blob_sha1(data)
    blob_ok = blob == pin["blob_sha1"]
    sha = sha256_bytes(data)
    pinned_sha = pin.get("sha256")
    sha_entry = {
        "computed": sha,
        "pinned": pinned_sha,
        "provenance": pin.get("sha256_provenance"),
        "match": (pinned_sha == sha) if pinned_sha is not None else None,
    }
    gate_pass = size_ok and blob_ok and (sha_entry["match"] is not False)
    return {
        "file": name,
        "size_bytes": len(data),
        "size_expected": pin["size_bytes"],
        "size_match": size_ok,
        "blob_sha1": blob,
        "blob_sha1_expected": pin["blob_sha1"],
        "blob_sha1_match": blob_ok,
        "sha256": sha_entry,
        "digest_gate": "PASS" if gate_pass else "FAIL",
    }


# ------------------------------------------------------------- input builder
def build_input_text(pro_cpu_text: str, variant: str, seed: int, steps: int, prefix: str):
    """Build one run input from the verbatim pro_CPU.in template.

    Returns ``(input_text, deviations)``; deviations record every change
    against the author file (same convention as EX-NL3-002-R1).
    """
    key_map = {
        "steps": str(steps),
        "seed": str(seed),
        "topology": f"{variant}.top",
        "conf_file": f"{variant}.conf",
        "trajectory_file": f"{prefix}_traj.dat",
        "energy_file": f"{prefix}_energy.dat",
        "log_file": f"{prefix}_log.dat",
        "print_conf_interval": str(PRINT_CONF_INTERVAL),
        "print_energy_every": str(PRINT_ENERGY_EVERY),
    }
    out = []
    deviations = []
    seen = set()
    for line in pro_cpu_text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in key_map:
                value = key_map[key]
                author = line.split("=", 1)[1].strip()
                if author != value:
                    deviations.append(
                        {"key": key, "author": author, "confirm": value, "reason": DEVIATION_REASON}
                    )
                out.append(f"{key} = {value}")
                seen.add(key)
                continue
        out.append(line)
    missing = [k for k in key_map if k not in seen]
    if missing:  # fail closed: template must contain every overridden key
        raise RealExecutorError(f"pro_CPU.in template missing keys: {missing}")
    out.append(f"lastconf_file = {prefix}_last.dat")
    deviations.append(
        {
            "key": "lastconf_file",
            "author": None,
            "confirm": f"{prefix}_last.dat",
            "reason": "author input has no lastconf_file; protocol records final configuration",
        }
    )
    deviations.sort(key=lambda d: d["key"])
    return "\n".join(out) + "\n", deviations


class RealExecutorError(Exception):
    pass


# ------------------------------------------------------------------ analysis
def quantile_sorted(sorted_vals, q):
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def parse_energy(text: str) -> dict:
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 4:
            try:
                rows.append([float(x) for x in parts])
            except ValueError:
                continue
    if not rows:
        raise RealExecutorError("energy file has no numeric rows")
    totals = [r[3] for r in rows]
    return {
        "columns": ["time", "potential", "kinetic", "total"],
        "rows_total": len(rows),
        "time_first": rows[0][0],
        "time_last": rows[-1][0],
        "total_energy_first": totals[0],
        "total_energy_last": totals[-1],
        "total_energy_min": min(totals),
        "total_energy_max": max(totals),
        "max_abs_drift_total": max(abs(t - totals[0]) for t in totals),
    }


def _median(values):
    if not values:
        return None
    return quantile_sorted(sorted(values), 0.5)


def analyse_trajectory(topology_text: str, traj_text: str, manifest: dict) -> dict:
    """v2 (mutual) observables + §4 frame gates + angle stats over valid frames."""
    topology = Topology.parse(topology_text)
    topology.check_chain_integrity()
    frames = list(obs.iter_frames(traj_text))
    ref = frames[0]
    ref.check_orientation()
    ref_pairs = obs.reference_pairs_v2(ref, topology)  # mutual-nearest (frozen)
    frame_rows = []
    for pos, conf in enumerate(frames):
        conf.check_orientation()
        angle = obs.hinge_angle(conf, manifest)
        pairs = obs.pairs_fraction_v2(conf, ref_pairs)
        bonds = obs.bonded_integrity(conf, topology)
        disp = obs.displacement_max(ref, conf)
        reasons = []
        if bonds["long_bond_fraction"] > GATE_LBF_MAX:
            reasons.append("long_bond_fraction")
        if pairs["pairs_fraction"] is None or pairs["pairs_fraction"] < GATE_PF2_MIN:
            reasons.append("pairs_fraction_v2")
        if disp["displacement_max"] > GATE_DISP_MAX:
            reasons.append("displacement_max")
        frame_rows.append(
            {
                "frame": pos,
                "time": conf.time,
                "angle_deg": angle["angle_deg"] if angle["status"] == "OK" else None,
                "angle_status": angle["status"],
                "pairs_fraction_v2": pairs["pairs_fraction"],
                "long_bond_fraction": bonds["long_bond_fraction"],
                "displacement_max": disp["displacement_max"],
                "valid": not reasons,
                "invalid_reasons": reasons,
            }
        )
    valid = [f for f in frame_rows if f["valid"]]
    valid_angles = [f["angle_deg"] for f in valid if f["angle_deg"] is not None]
    s = sorted(valid_angles)
    return {
        "detector": "v2 mutual-nearest (frozen, E2_OBSERVABLES_R2 + E2_PROTO_R1 §2)",
        "angle_convention": "[0,180] deg, PCA axes, erratum R1 §2.5",
        "gates": {
            "long_bond_fraction_max": GATE_LBF_MAX,
            "pairs_fraction_v2_min": GATE_PF2_MIN,
            "displacement_max_max": GATE_DISP_MAX,
        },
        "reference_pairs_v2_count": len(ref_pairs),
        "frames_total": len(frame_rows),
        "frames_valid": len(valid),
        "valid_frame_fraction": (len(valid) / len(frame_rows)) if frame_rows else None,
        "angle_stats_valid_frames": {
            "n_frames": len(s),
            "median_deg": _median(s),
            "min_deg": s[0] if s else None,
            "max_deg": s[-1] if s else None,
        },
        # run-level summary over the frames the score is computed from
        "summary_valid_frames": {
            "median_angle_deg": _median(s),
            "long_bond_fraction": _median([f["long_bond_fraction"] for f in valid]),
            "pairs_fraction_v2": _median([f["pairs_fraction_v2"] for f in valid]),
            "displacement_max": _median([f["displacement_max"] for f in valid]),
        },
        "frames": frame_rows,
    }


# ================================================================== adapter
class RealExecutorAdapter(ExecutorAdapter):
    """ExecutorAdapter implementation backed by the pinned WSL oxDNA build."""

    executor_id = "real-oxdna-wsl-r1"
    backend = f"oxDNA {ENGINE_SOURCE_COMMIT[:7]} CPU/double via WSL (pinned build, digest-gated inputs)"

    def __init__(
        self,
        repo_root: str,
        evidence_dir: str,
        run_prefix: str,
        run_wall_cap_s: float = RUN_WALL_CAP_S,
    ):
        self.repo_root = os.path.abspath(repo_root)
        self.evidence_dir = os.path.abspath(evidence_dir)
        os.makedirs(self.evidence_dir, exist_ok=True)
        self.run_prefix = run_prefix
        self.run_wall_cap_s = run_wall_cap_s
        self.source_dir = os.path.join(
            os.environ.get("TEMP", r"C:\Windows\Temp"), SOURCE_TEMP_SUBDIR
        )
        self.tmp_read_dir = os.path.join(
            os.environ.get("TEMP", r"C:\Windows\Temp"), "nl4-002-e3-read"
        )
        with open(
            os.path.join(self.repo_root, "scripts", "hinge_family", "source_pins.json"),
            "r",
            encoding="utf-8",
        ) as handle:
            self.pins = json.load(handle)
        self._sources_ok: dict[str, dict] = {}
        self._download_report: dict = {
            "schema_version": 1,
            "kind": "nl4_e3_source_download_verification",
            "download_base": DOWNLOAD_BASE,
            "dest_dir": self.source_dir,
            "durable_cache": False,
            "gate_policy": "size + blob_sha1 mandatory; sha256 compared when pinned, else computed-at-first-download recorded",
            "files": {},
        }

    # ------------------------------------------------------------ sources
    def _local_source(self, name: str) -> str:
        return os.path.join(self.source_dir, name.replace("/", "__"))

    def ensure_sources(self, variant: str) -> None:
        """Digest-gated download-on-run for one variant (idempotent)."""
        needed = [f"MD_Hinges/{variant}.top", f"MD_Hinges/{variant}.conf"]
        if not os.path.exists(self._local_source("MD_Hinges/pro_CPU.in")):
            needed.append("MD_Hinges/pro_CPU.in")
        os.makedirs(self.source_dir, exist_ok=True)
        for name in needed:
            if name in self._sources_ok:
                continue
            pin = self.pins["files"][name]
            url = DOWNLOAD_BASE + name
            with urllib.request.urlopen(url, timeout=180) as resp:
                data = resp.read()
            entry = verify_source_bytes(name, data, pin)
            with open(self._local_source(name), "wb") as handle:
                handle.write(data)
            entry["local_path"] = self._local_source(name)
            self._download_report["files"][name] = entry
            self._sources_ok[name] = entry
            if entry["digest_gate"] != "PASS":
                self._write_download_report()
                raise RealExecutorError(f"digest gate FAIL for {name}: {entry}")
        self._write_download_report()

    def _write_download_report(self) -> None:
        report = dict(self._download_report)
        report["digest_gate_all"] = (
            "PASS"
            if all(e["digest_gate"] == "PASS" for e in report["files"].values())
            else "FAIL"
        )
        with open(
            os.path.join(self.evidence_dir, "source-download-verification.json"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            handle.write(canonical_json(report) + "\n")

    def load_arm_manifest(self, variant: str) -> dict:
        path = os.path.join(self.repo_root, ARM_MANIFESTS[variant])
        with open(path, "r", encoding="utf-8", newline="") as handle:
            manifest = json.load(handle)["arms"]
        for name in ("arm_a", "arm_b"):
            if name not in manifest or "nucleotides" not in manifest[name]:
                raise RealExecutorError(f"arm manifest for {variant} missing {name}.nucleotides")
        return manifest

    # ------------------------------------------------------------- prepare
    def prepare_run(self, candidate: dict, run_id: str, prefix: str) -> dict:
        """Create the WSL run dir, copy digest-gated inputs, build input.in."""
        variant = candidate["variant"]
        if variant not in ARM_MANIFESTS:
            raise RealExecutorError(f"variant {variant} outside E3 space {list(ARM_MANIFESTS)}")
        self.ensure_sources(variant)
        wsl_dir = f"{WSL_RUNS_ROOT}/{run_id}"
        wsl(f"mkdir -p '{wsl_dir}'")
        copies = {
            f"MD_Hinges/{variant}.top": f"{variant}.top",
            f"MD_Hinges/{variant}.conf": f"{variant}.conf",
            "MD_Hinges/pro_CPU.in": "pro_CPU.in",
        }
        for src_name, dest in copies.items():
            wsl(f"cp '{to_wsl_path(self._local_source(src_name))}' '{wsl_dir}/{dest}'")
        with open(self._local_source("MD_Hinges/pro_CPU.in"), "r", encoding="utf-8") as handle:
            pro_cpu_text = handle.read()
        input_text, deviations = build_input_text(
            pro_cpu_text, variant, candidate["seed"], candidate["steps"], prefix
        )
        run_evidence = os.path.join(self.evidence_dir, run_id)
        os.makedirs(run_evidence, exist_ok=True)
        with open(
            os.path.join(run_evidence, "deviations.json"), "w", encoding="utf-8", newline="\n"
        ) as handle:
            handle.write(
                canonical_json(
                    {
                        "schema_version": 1,
                        "kind": "nl4_e3_input_deviations",
                        "run_id": run_id,
                        "source_input": "MD_Hinges/pro_CPU.in @ 23fd1ff (digest-gated, verbatim base)",
                        "deviations": deviations,
                    }
                )
                + "\n"
            )
        win_input = os.path.join(run_evidence, "input.in")
        with open(win_input, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(input_text)
        wsl(f"cp '{to_wsl_path(win_input)}' '{wsl_dir}/input.in'")
        # verify byte-identical copies (lesson F-1)
        checks = {}
        for src_name, dest in copies.items():
            with open(self._local_source(src_name), "rb") as handle:
                win_sha = hashlib.sha256(handle.read()).hexdigest()
            wsl_sha = wsl(f"sha256sum '{wsl_dir}/{dest}'").split()[0]
            checks[dest] = {"expected_sha256": win_sha, "copy_sha256": wsl_sha, "match": win_sha == wsl_sha}
        wsl_sha = wsl(f"sha256sum '{wsl_dir}/input.in'").split()[0]
        win_input_sha = hashlib.sha256(input_text.encode("utf-8")).hexdigest()
        checks["input.in"] = {"expected_sha256": win_input_sha, "copy_sha256": wsl_sha, "match": win_input_sha == wsl_sha}
        if not all(c["match"] for c in checks.values()):
            raise RealExecutorError(f"run copy verification FAIL for {run_id}: {checks}")
        return {"run_id": run_id, "wsl_dir": wsl_dir, "copy_checks": checks, "run_evidence": run_evidence}

    # -------------------------------------------------------------- launch
    def launch(self, wsl_dir: str):
        cmd = (
            f"cd '{wsl_dir}' && setsid nohup '{ENGINE}' input.in "
            f"> engine_stdout.txt 2> engine_stderr.txt; echo EXIT:$? > exit_code.txt"
        )
        return subprocess.Popen(["wsl", "-e", "bash", "-c", cmd]), time.perf_counter()

    def wait(self, run_id: str, proc, started: float) -> dict:
        """Wait for one run; enforce the hard wall cap (kill + record on breach)."""
        wsl_dir = f"{WSL_RUNS_ROOT}/{run_id}"
        interrupted = False
        while True:
            rc = proc.poll()
            if rc is not None:
                break
            if time.perf_counter() - started > self.run_wall_cap_s:
                subprocess.run(
                    ["wsl", "-e", "bash", "-c", f"pkill -f 'runs/{run_id}' || true"], timeout=120
                )
                proc.wait()
                interrupted = True
                break
            time.sleep(20)
        wall = time.perf_counter() - started
        exit_code = None
        out = wsl(f"cat '{wsl_dir}/exit_code.txt' 2>/dev/null || true")
        for line in out.splitlines():
            if line.startswith("EXIT:"):
                exit_code = int(line.split(":", 1)[1])
        return {
            "exit_code": exit_code,
            "interrupted_budget": interrupted,
            "wall_seconds": round(wall, 2),
            "per_step_s": round(wall / float(STEPS_FIXED), 6),
        }

    # ------------------------------------------------------------- analyse
    def analyse_run(self, candidate: dict, prep: dict, engine_out: dict) -> dict:
        run_id = prep["run_id"]
        wsl_dir = prep["wsl_dir"]
        run_evidence = prep["run_evidence"]
        report = {
            "schema_version": 1,
            "kind": "nl4_e3_run_analysis",
            "run_id": run_id,
            "candidate": dict(candidate),
            "executor": self.executor_id,
            "engine": ENGINE,
            "engine_source_commit": ENGINE_SOURCE_COMMIT,
            "wsl_dir": wsl_dir,
            "exit_code": engine_out["exit_code"],
            "interrupted_budget": engine_out["interrupted_budget"],
            "wall_seconds": engine_out["wall_seconds"],
            "per_step_s": engine_out["per_step_s"],
        }
        failed = engine_out["exit_code"] != 0 or engine_out["interrupted_budget"]
        if failed:
            stderr_tail = wsl(f"tail -c 2000 '{wsl_dir}/engine_stderr.txt' 2>/dev/null || true")
            report["status"] = "FAILED"
            report["engine_stderr_tail"] = stderr_tail
            analysis_summary = {
                "median_angle_deg": None,
                "long_bond_fraction": None,
                "pairs_fraction_v2": None,
                "displacement_max": None,
            }
        else:
            variant = candidate["variant"]
            topology_text = wsl_read(f"{wsl_dir}/{variant}.top", self.tmp_read_dir)
            traj_text = wsl_read(f"{wsl_dir}/{run_id.lower()}_traj.dat", self.tmp_read_dir)
            manifest = self.load_arm_manifest(variant)
            analysis = analyse_trajectory(topology_text, traj_text, manifest)
            energy = parse_energy(wsl_read(f"{wsl_dir}/{run_id.lower()}_energy.dat", self.tmp_read_dir))
            report["status"] = "ANALYSED"
            report["arm_manifest"] = ARM_MANIFESTS[variant] + " (frozen)"
            report["energy"] = energy
            report.update(analysis)
            summary = analysis["summary_valid_frames"]
            analysis_summary = {
                "median_angle_deg": summary["median_angle_deg"],
                "long_bond_fraction": summary["long_bond_fraction"],
                "pairs_fraction_v2": summary["pairs_fraction_v2"],
                "displacement_max": summary["displacement_max"],
            }
        # artifacts manifest: sha256 + size + location of every input/output
        artifacts = {}
        listing = wsl(f"cd '{wsl_dir}' && for f in *; do [ -f \"$f\" ] && sha256sum \"$f\" && stat -c '%s %n' \"$f\"; done")
        lines = listing.splitlines()
        for i in range(0, len(lines) - 1, 2):
            sha_line, stat_line = lines[i], lines[i + 1]
            fname = sha_line.split(None, 1)[1].strip()
            size = int(stat_line.split()[0])
            artifacts[fname] = {
                "sha256": sha_line.split()[0],
                "size_bytes": size,
                "location": f"{wsl_dir}/{fname}",
            }
        report["artifacts"] = artifacts
        with open(
            os.path.join(run_evidence, "analysis.json"), "w", encoding="utf-8", newline="\n"
        ) as handle:
            handle.write(canonical_json(report) + "\n")
        controller_result = {
            "run_id": run_id,
            "executor": self.executor_id,
            "backend": self.backend,
            "candidate": dict(candidate),
            "input_digest_sha256": candidate_digest(candidate),
            "wall_seconds": engine_out["wall_seconds"],
            "analysis": analysis_summary,
            "status": report["status"],
            "wsl_dir": wsl_dir,
            "exit_code": engine_out["exit_code"],
            "evidence": f"evidence/{run_id}/analysis.json",
        }
        return controller_result

    # ---------------------------------------------- ExecutorAdapter surface
    def estimate_wall_seconds(self, candidate: dict):
        """Measured-cost estimate: 0.052-0.066 s/step depending on variant size."""
        per_step = {"0b": 0.052, "11b": 0.066, "32b": 0.070, "53b": 0.074}
        return round(per_step.get(candidate["variant"], 0.075) * candidate["steps"], 1)

    def run(self, candidate: dict, run_seq: int) -> dict:
        """Sequential single run (smoke path)."""
        run_id = f"{self.run_prefix}-R{run_seq:03d}"
        prefix = run_id.lower()
        prep = self.prepare_run(candidate, run_id, prefix)
        proc, started = self.launch(prep["wsl_dir"])
        engine_out = self.wait(run_id, proc, started)
        return self.analyse_run(candidate, prep, engine_out)

    def run_parallel(self, candidates: list) -> list:
        """Execute a whole arm concurrently; results in candidate order.

        RUN IDs are assigned in candidate order (run_seq 1..n), matching the
        order the deterministic baseline agent proposes them, so the
        Controller replay reproduces the same run_id mapping.
        """
        preps = []
        for idx, candidate in enumerate(candidates, start=1):
            run_id = f"{self.run_prefix}-R{idx:03d}"
            prefix = run_id.lower()
            preps.append((candidate, self.prepare_run(candidate, run_id, prefix)))
        launched = []
        for candidate, prep in preps:
            proc, started = self.launch(prep["wsl_dir"])
            launched.append((candidate, prep, proc, started))
            print(f"[real_executor] launched {prep['run_id']}", flush=True)
        results = [None] * len(launched)
        pending = set(range(len(launched)))
        while pending:
            for idx in list(pending):
                candidate, prep, proc, started = launched[idx]
                if proc.poll() is not None:
                    engine_out = self._collect(prep["run_id"], proc, started)
                    results[idx] = self.analyse_run(candidate, prep, engine_out)
                    print(
                        f"[real_executor] finished {prep['run_id']} exit={engine_out['exit_code']} "
                        f"wall={engine_out['wall_seconds']}s",
                        flush=True,
                    )
                    pending.discard(idx)
                elif time.perf_counter() - started > self.run_wall_cap_s:
                    # hard per-run wall cap (WO-NL4-002): interrupt and record
                    run_id = prep["run_id"]
                    subprocess.run(
                        ["wsl", "-e", "bash", "-c", f"pkill -f 'runs/{run_id}' || true"],
                        timeout=120,
                    )
                    proc.wait()
                    engine_out = self._collect(run_id, proc, started, interrupted=True)
                    results[idx] = self.analyse_run(candidate, prep, engine_out)
                    print(
                        f"[real_executor] BUDGET-INTERRUPTED {run_id} "
                        f"wall={engine_out['wall_seconds']}s",
                        flush=True,
                    )
                    pending.discard(idx)
            if pending:
                time.sleep(20)
        return results

    def _collect(self, run_id: str, proc, started: float, interrupted: bool = False) -> dict:
        wall = time.perf_counter() - started
        exit_code = None
        out = wsl(f"cat '{WSL_RUNS_ROOT}/{run_id}/exit_code.txt' 2>/dev/null || true")
        for line in out.splitlines():
            if line.startswith("EXIT:"):
                exit_code = int(line.split(":", 1)[1])
        return {
            "exit_code": exit_code,
            "interrupted_budget": interrupted,
            "wall_seconds": round(wall, 2),
            "per_step_s": round(wall / float(STEPS_FIXED), 6),
        }


# ------------------------------------------------------------- replay layer
class ReplayExecutor(ExecutorAdapter):
    """Replays precomputed RealExecutor results through the Controller.

    The mechanical arms are non-adaptive (their proposal sequence is fixed at
    construction), so executing the runs in parallel first and then replaying
    the identical action stream through the Controller yields exactly the
    sequential-session report while respecting the parallel-runs wall budget
    of WO-NL4-002.
    """

    executor_id = "real-oxdna-wsl-r1"
    backend = RealExecutorAdapter.backend

    def __init__(self, results: list):
        self._by_digest = {r["input_digest_sha256"]: r for r in results}
        self._order = list(results)
        self._cursor = 0

    def estimate_wall_seconds(self, candidate: dict):
        return self._order[self._cursor]["wall_seconds"] if self._cursor < len(self._order) else None

    def run(self, candidate: dict, run_seq: int) -> dict:
        result = self._by_digest[candidate_digest(candidate)]
        self._cursor += 1
        return result
