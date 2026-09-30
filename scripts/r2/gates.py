"""R2 validation gates (U1-U5), negative controls (NC-U1..U5) and the
activation decision machine.

Contract: docs/research/ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md §6-§9 and
docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md §1. Policy invariant is
ENFORCED HERE IN CODE: ``R2_ACTIVATED = YES`` requires

    every gate PASS
    AND every negative control PASS
    AND a frozen native-eligible fingerprint (outenemy can never qualify)
    AND fresh review verdict PASS
    AND fresh verify verdict VERIFIED
    AND human_gate_approved = true.

Otherwise the status stays "WAITING_HOST / NOT_ACTIVE" with explicit unmet
reasons. PASS statuses require evidence that actually exists on disk.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import TOOLING_VERSION
from .contract import utc_now_iso
from .fingerprint import validate_native_u1

GATES: tuple[tuple[str, str], ...] = (
    ("U1", "engine build (CPU/DOUBLE=ON/CUDA=OFF/MPI=OFF, clean)"),
    ("U2", "package verify (nanolab-components; documented v0.1.x pyc findings tolerated)"),
    ("U3", "frame0 oracle: 0b/11b/32b/53b exact; 74b NOT_MEASURED"),
    ("U4", "technical oxDNA smoke: exit=0, finite outputs, expected files (NOT a scientific claim)"),
    ("U5", "repository harness: unit tests, check-consistency, workflow lint, work_cli"),
)

CONTROLS: tuple[tuple[str, str], ...] = (
    ("NC-U1", "SSH/session close: disposable job keeps running"),
    ("NC-U2", "agent process restart: job survives"),
    ("NC-U3", "GitHub runner service restart: job survives"),
    ("NC-U4", "CI workspace cleanup: scientific workspace/raw intact"),
    ("NC-U5", "deliberate kill: FAILED_TECHNICAL, attempt preserved, retry gets new ID"),
)

GATE_STATUSES = ("WAITING_HOST", "PASS", "FAIL")
R2_STATUS_WAITING = "WAITING_HOST / NOT_ACTIVE"
R2_STATUS_ACTIVE = "ACTIVE"


class GateError(ValueError):
    """Raised on invalid gate IDs, statuses or missing evidence."""


class GateReport:
    """Durable JSON state of all gates and negative controls."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.state: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        entries: dict[str, Any] = {}
        for gate_id, title in GATES:
            entries[gate_id] = {"title": title, "status": "WAITING_HOST", "evidence_ref": "", "recorded_utc": ""}
        for control_id, title in CONTROLS:
            entries[control_id] = {"title": title, "status": "WAITING_HOST", "evidence_ref": "", "recorded_utc": ""}
        return {
            "schema_version": 1,
            "kind": "r2_gate_report",
            "tooling_version": TOOLING_VERSION,
            "entries": entries,
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def entry(self, gate_id: str) -> dict[str, Any]:
        try:
            return self.state["entries"][gate_id]
        except KeyError as error:
            raise GateError(f"unknown gate/control id: {gate_id}") from error

    def set_status(self, gate_id: str, status: str, evidence_ref: str) -> dict[str, Any]:
        if status not in GATE_STATUSES:
            raise GateError(f"invalid status {status!r}; expected one of {GATE_STATUSES}")
        entry = self.entry(gate_id)
        if status == "PASS":
            if not evidence_ref:
                raise GateError(f"{gate_id}: PASS requires a non-empty evidence_ref")
            evidence = Path(evidence_ref)
            if not evidence.is_file():
                raise GateError(f"{gate_id}: PASS evidence file does not exist: {evidence_ref}")
            if evidence.stat().st_size == 0:
                raise GateError(f"{gate_id}: PASS evidence file is empty: {evidence_ref}")
        entry["status"] = status
        entry["evidence_ref"] = evidence_ref
        entry["recorded_utc"] = utc_now_iso()
        self.save()
        return dict(entry)

    def all_gates_pass(self) -> bool:
        return all(self.entry(gate_id)["status"] == "PASS" for gate_id, _ in GATES)

    def all_controls_pass(self) -> bool:
        return all(self.entry(control_id)["status"] == "PASS" for control_id, _ in CONTROLS)

    def unmet(self) -> list[str]:
        pending = []
        for gate_id, _ in GATES:
            status = self.entry(gate_id)["status"]
            if status != "PASS":
                pending.append(f"{gate_id}={status}")
        for control_id, _ in CONTROLS:
            status = self.entry(control_id)["status"]
            if status != "PASS":
                pending.append(f"{control_id}={status}")
        return pending


def activation_decision(
    report: GateReport,
    fingerprint: dict[str, Any] | None,
    review_verdict: str | None,
    verify_verdict: str | None,
    human_gate_approved: bool = False,
) -> dict[str, Any]:
    """Compute the R2 activation decision from durable facts only.

    This function never mutates state and never takes the operator's word:
    each precondition is checked mechanically, and any unmet precondition
    keeps R2 in WAITING_HOST / NOT_ACTIVE.
    """
    unmet: list[str] = []
    unmet += [f"gate {item}" for item in report.unmet()]

    fingerprint_valid = False
    if fingerprint is None:
        unmet.append("fingerprint frozen (no fingerprint provided)")
    else:
        ok, reasons = validate_native_u1(fingerprint)
        fingerprint_valid = ok
        if not ok:
            unmet.append("fingerprint native-U1 invalid: " + "; ".join(reasons))

    if review_verdict != "PASS":
        unmet.append(f"fresh review verdict {review_verdict!r} != PASS")
    if verify_verdict != "VERIFIED":
        unmet.append(f"fresh verify verdict {verify_verdict!r} != VERIFIED")
    if not human_gate_approved:
        unmet.append("human gate not approved")

    activated = (not unmet) and fingerprint_valid
    return {
        "r2_activated": activated,
        "r2_status": R2_STATUS_ACTIVE if activated else R2_STATUS_WAITING,
        "author_u1": fingerprint["parsed"]["hostname"] if activated and fingerprint else "NOT_ASSIGNED",
        "unmet": unmet,
        "decided_utc": utc_now_iso(),
        "tooling_version": TOOLING_VERSION,
    }
