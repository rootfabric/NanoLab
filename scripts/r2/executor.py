"""Scientific run executor: launches commands, captures raw evidence.

Design (mission §11/§12/§13; WO-NATIVE-UBUNTU-EXECUTOR-R1 §3/§5):
- scientific runs NEVER depend on an SSH session, an agent process, a
  terminal or a CI runner: on U1 they are launched through systemd
  (transient service/scope via systemd-run); the direct launcher exists for
  dev-host unit tests only and refuses to run under an ineligible host check
  performed by the CLI layer;
- every attempt gets a fresh attempt ID (never reused, see contract.py);
- every attempt writes stdout/stderr/exit metadata plus an artifact manifest
  (path/sha256/size/producer/retention) into
  ``<raw_root>/<execution-id>/<attempt-id>/``;
- nonzero exit, timeout or deliberate kill => technical_outcome
  FAILED_TECHNICAL with the attempt preserved in the append-only ledger;
  the retry receives a NEW attempt ID (-R1, -R2, ...);
- the executor layer records scientific_outcome = NOT_EVALUATED always.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from . import TOOLING_VERSION
from .contract import (
    AttemptLedger,
    AttemptRecord,
    AttemptReuseError,
    build_artifact_manifest,
    canonical_json,
    manifest_digest,
    attempt_id as format_attempt_id,
    utc_now_iso,
)


class LauncherProtocol(Protocol):
    def run(
        self,
        argv: list[str],
        stdout_path: Path,
        stderr_path: Path,
        timeout_seconds: int | None,
        working_directory: Path | None,
    ) -> dict[str, Any]:
        """Return {'returncode': int|None, 'killed': bool, 'note': str}."""


class DirectLauncher:
    """Subprocess launcher for dev-host tests of the tooling itself."""

    def run(
        self,
        argv: list[str],
        stdout_path: Path,
        stderr_path: Path,
        timeout_seconds: int | None,
        working_directory: Path | None,
    ) -> dict[str, Any]:
        with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
            process = subprocess.Popen(
                argv,
                stdout=out,
                stderr=err,
                cwd=str(working_directory) if working_directory else None,
            )
            try:
                returncode = process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                return {"returncode": None, "killed": True, "note": "timeout-kill"}
        return {"returncode": returncode, "killed": False, "note": ""}


class SystemdTransientLauncher:
    """Launch through systemd-run transient unit (session-independent).

    The argv builder is pure and unit-tested; actual execution happens only
    on a host that passed validate_native_u1 (CLI-layer guard).

    ``user_manager=False`` (default) targets the system manager (unit owned
    by PID 1). ``user_manager=True`` emits ``systemd-run --user``: the mode
    verified working unprivileged on the U2 platform (outenemy, linger=yes);
    see supervisor.transient_service_argv for the machine facts.
    """

    def __init__(self, unit_prefix: str = "nanolab-run", user_manager: bool = False):
        self.unit_prefix = unit_prefix
        self.user_manager = user_manager

    def unit_name(self, execution_id: str, attempt: str) -> str:
        safe = f"{execution_id}-{attempt}".replace("/", "-")
        return f"{self.unit_prefix}-{safe}"

    def argv(
        self,
        unit: str,
        command: list[str],
        working_directory: Path | None = None,
        collect: bool = True,
    ) -> list[str]:
        base = ["systemd-run"]
        if self.user_manager:
            base.append("--user")
        if collect:
            base.append("--collect")
        base += [f"--unit={unit}"]
        if working_directory is not None:
            base.append(f"--working-directory={working_directory}")
        base += ["--wait", "--pipe"]
        return base + list(command)

    def run(
        self,
        argv: list[str],
        stdout_path: Path,
        stderr_path: Path,
        timeout_seconds: int | None,
        working_directory: Path | None,
    ) -> dict[str, Any]:
        raise RuntimeError(
            "SystemdTransientLauncher.execute is only available on an "
            "eligible U1 host; use the CLI (guarded by host validation)"
        )


@dataclass
class RunSpec:
    execution_id: str
    run_base: str
    attempt: int
    command: list[str]
    seed: Any = None
    subject_pins: dict[str, Any] = field(default_factory=dict)
    workspace: Path | None = None
    raw_root: Path | None = None
    timeout_seconds: int | None = None
    launcher: LauncherProtocol | None = None


class RunExecutor:
    """Execute one attempt of a logical run and durably record the evidence."""

    def __init__(self, ledger: AttemptLedger, launcher: LauncherProtocol | None = None):
        self.ledger = ledger
        self.launcher = launcher or DirectLauncher()

    def raw_dir_for(self, raw_root: Path | None, execution_id: str, attempt: str) -> Path:
        root = raw_root or (self.ledger.path.parent / "raw")
        return Path(root) / execution_id / attempt

    def execute(self, spec: RunSpec) -> AttemptRecord:
        attempt = format_attempt_id(spec.run_base, spec.attempt)
        if attempt in self.ledger.known_attempt_ids():
            raise AttemptReuseError(f"attempt_id already recorded: {attempt}")

        raw_dir = self.raw_dir_for(spec.raw_root, spec.execution_id, attempt)
        workspace = spec.workspace or (raw_dir.parent.parent / "workspaces" / spec.execution_id / attempt)
        raw_dir.mkdir(parents=True, exist_ok=True)
        workspace.mkdir(parents=True, exist_ok=True)

        started = utc_now_iso()
        result = self.launcher.run(
            list(spec.command),
            stdout_path=raw_dir / "stdout.txt",
            stderr_path=raw_dir / "stderr.txt",
            timeout_seconds=spec.timeout_seconds,
            working_directory=workspace,
        )
        ended = utc_now_iso()

        killed = bool(result.get("killed"))
        returncode = result.get("returncode")
        if returncode == 0 and not killed:
            outcome = "COMPLETED"
        elif killed:
            outcome = "FAILED_TECHNICAL"
        else:
            outcome = "FAILED_TECHNICAL"

        exit_meta = {
            "execution_id": spec.execution_id,
            "attempt_id": attempt,
            "run_base": spec.run_base,
            "attempt": spec.attempt,
            "seed": spec.seed,
            "subject_pins": spec.subject_pins,
            "command": list(spec.command),
            "started_utc": started,
            "ended_utc": ended,
            "exit_code": returncode,
            "killed": killed,
            "technical_outcome": outcome,
            "scientific_outcome": "NOT_EVALUATED",
            "tooling_version": TOOLING_VERSION,
            "note": str(result.get("note", "")),
        }
        (raw_dir / "exit.json").write_text(
            json_dumps(exit_meta), encoding="utf-8"
        )

        manifest = build_artifact_manifest(raw_dir, producer=f"{spec.execution_id}/{attempt}")
        (raw_dir / "artifact-manifest.json").write_text(
            json_dumps({"manifest": manifest, "digest": manifest_digest(manifest)}),
            encoding="utf-8",
        )

        record = AttemptRecord(
            execution_id=spec.execution_id,
            attempt_id=attempt,
            run_base=spec.run_base,
            attempt=spec.attempt,
            command=list(spec.command),
            seed=spec.seed,
            subject_pins=dict(spec.subject_pins),
            started_utc=started,
            ended_utc=ended,
            exit_code=returncode,
            technical_outcome=outcome,
            scientific_outcome="NOT_EVALUATED",
            workspace=str(workspace),
            raw_dir=str(raw_dir),
            manifest_digest=manifest_digest(manifest),
            note=str(result.get("note", "")),
        )
        self.ledger.append(record)  # AttemptReuseError can never be silent
        return record


def json_dumps(value: Any) -> str:
    return canonical_json(value) + "\n"
