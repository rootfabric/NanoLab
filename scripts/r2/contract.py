"""Run contract primitives: attempt IDs, append-only ledger, artifact manifests.

Contract (mission 2026-09-30 §12, §13; WO-NATIVE-UBUNTU-EXECUTOR-R1 §6 NC-U5):
- every run belongs to an execution (execution_id) and a logical run (run_base);
- the first physical attempt is identified by ``<run_base>``, retries by
  ``<run_base>-R1``, ``<run_base>-R2``, ...;
- an attempt ID is NEVER reused, not even after FAILED_TECHNICAL;
- technical outcome is recorded separately from scientific outcome; this
  tooling layer always records scientific_outcome = NOT_EVALUATED;
- every attempt produces raw artifacts under
  ``<raw_root>/<execution-id>/<attempt-id>/`` plus an artifact manifest with
  sha256/size/producer/retention per file and a digest of the manifest itself;
- Git stores compact evidence only (the ledger lives outside the repo).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TECHNICAL_OUTCOMES = ("COMPLETED", "FAILED_TECHNICAL", "ABORTED", "BLOCKED_ENVIRONMENT")
SCIENTIFIC_OUTCOME_TOOLING = "NOT_EVALUATED"
RETENTION_DEFAULT = "raw-local-persistent"


class AttemptReuseError(RuntimeError):
    """Raised when an attempt ID would be reused (hard rule: never reuse)."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def attempt_id(run_base: str, attempt: int) -> str:
    """Return the physical attempt identifier for a logical run."""
    if attempt < 0:
        raise ValueError("attempt must be >= 0")
    if not run_base or "/" in run_base or run_base.startswith("."):
        raise ValueError("run_base must be a non-empty path-safe identifier")
    return run_base if attempt == 0 else f"{run_base}-R{attempt}"


def next_attempt_id(run_base: str, ledger: "AttemptLedger") -> str:
    """Return the next free attempt ID for a logical run (retry discipline)."""
    number = 0
    while attempt_id(run_base, number) in ledger.known_attempt_ids():
        number += 1
    return attempt_id(run_base, number)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_artifact_manifest(
    root: Path,
    producer: str,
    retention: str = RETENTION_DEFAULT,
) -> list[dict[str, Any]]:
    """Describe every file under ``root`` with sha256/size/producer/retention."""
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            entries.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "sha256": sha256_file(path),
                    "size": path.stat().st_size,
                    "producer": producer,
                    "retention": retention,
                }
            )
    return entries


def manifest_digest(entries: list[dict[str, Any]]) -> str:
    return hashlib.sha256(canonical_json(entries).encode("utf-8")).hexdigest()


@dataclass
class AttemptRecord:
    execution_id: str
    attempt_id: str
    run_base: str
    attempt: int
    command: list[str]
    seed: Any = None
    subject_pins: dict[str, Any] = field(default_factory=dict)
    started_utc: str = ""
    ended_utc: str = ""
    exit_code: int | None = None
    technical_outcome: str = "FAILED_TECHNICAL"
    scientific_outcome: str = SCIENTIFIC_OUTCOME_TOOLING
    workspace: str = ""
    raw_dir: str = ""
    manifest_digest: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AttemptLedger:
    """Append-only JSONL ledger of attempt records.

    The ledger is durable memory outside Git (compact evidence goes to Git;
    the ledger itself stays with the raw tree). Appending is the only mutation;
    duplicate attempt IDs are rejected.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def known_attempt_ids(self) -> set[str]:
        if not self.path.exists():
            return set()
        known: set[str] = set()
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            known.add(str(record["attempt_id"]))
        return known

    def entries(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        result = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                result.append(json.loads(line))
        return result

    def append(self, record: AttemptRecord | dict[str, Any]) -> dict[str, Any]:
        payload = record.to_dict() if isinstance(record, AttemptRecord) else dict(record)
        attempt = str(payload.get("attempt_id", ""))
        if not attempt:
            raise ValueError("record is missing attempt_id")
        if attempt in self.known_attempt_ids():
            raise AttemptReuseError(f"attempt_id already recorded: {attempt}")
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        return payload
