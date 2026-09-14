#!/usr/bin/env python3
"""Standalone reproduction helper shipped inside a NanoLab component package.

Contract (docs/release/RELEASE_CONTRACT_V0_1.md in the NanoLab repo):
  * works from the PACKAGE ONLY, without internal knowledge of the author
    repository (fresh-environment rule, NL5-002);
  * stdlib-only (no third-party dependencies);
  * verify: recompute SHA-256 of every file listed in RELEASE_MANIFEST.json
    and compare sizes — detects a tampered/truncated package;
  * plan: print the per-card reproduction plan (engine pins, steps, expected
    values, rights constraints) so an external executor can run the engine
    without author knowledge;
  * evaluate: apply the FROZEN independent-reproduction rule
    REPRODUCTION_RULE_R1 (reproduction/REPRODUCTION_RULE_R1.md) to a
    replication campaign report against a card — the pooled bootstrap CI95 of
    the original estimate is informational and is NEVER an acceptance band;
  * this helper NEVER downloads upstream inputs and NEVER runs the physics
    engine by itself in v0.1; input retrieval and engine execution follow the
    per-card rights/reproduction sections and are executed by the external
    reproducer (clean-room, NL5-001-C / NL5-002).

Exit codes: 0 = ok/pass, 3 = verification failure or honest non-pass
(MISMATCH / INCONCLUSIVE / TECHNICAL_FAILURE), 2 = usage/rule error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

MANIFEST_NAME = "RELEASE_MANIFEST.json"
RULE_ID = "REPRODUCTION_RULE_R1"
MIN_VALID_REPLICAS = 3
MIN_REFERENCE_REPLICAS = 2


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(pkg_root: Path) -> dict:
    errors: list[str] = []
    manifest_path = pkg_root / MANIFEST_NAME
    if not manifest_path.is_file():
        return {"mode": "verify", "ok": False, "errors": [f"{manifest_path}: manifest not found"]}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest.get("files", []):
        rel, expected = entry["path"], entry["sha256"]
        path = pkg_root / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
            continue
        if (size := path.stat().st_size) != entry["size_bytes"]:
            errors.append(f"size mismatch: {rel} ({size} != {entry['size_bytes']})")
        if (digest := _sha256(path)) != expected:
            errors.append(f"sha256 mismatch: {rel} ({digest} != {expected})")
    return {"mode": "verify", "ok": not errors, "files": len(manifest.get("files", [])), "errors": errors}


def plan(pkg_root: Path) -> dict:
    plans: list[dict] = []
    errors: list[str] = []
    cards = sorted((pkg_root / "families").rglob("*.card.json")) if (pkg_root / "families").is_dir() else []
    if not cards:
        errors.append("no component cards found under families/")
    for path in cards:
        card = json.loads(path.read_text(encoding="utf-8"))
        measured = card.get("measurement_status")
        entry = {
            "card": path.relative_to(pkg_root).as_posix(),
            "component_id": card.get("component_id"),
            "measurement_status": measured,
            "claim_ceiling": card.get("claim_ceiling"),
            "rights_mode": (card.get("rights") or {}).get("rights_mode"),
            "engine_commit": (card.get("protocol_pins") or {}).get("engine_commit"),
            "steps": (card.get("reproduction") or {}).get("steps", []),
            "expected": (card.get("reproduction") or {}).get("expected", {}),
        }
        if measured == "NOT_MEASURED":
            entry["note"] = "NO MEASUREMENT TO REPRODUCE (KNOWN_GAP); do not fabricate values"
        plans.append(entry)
    return {"mode": "plan", "ok": not errors, "plans": plans, "errors": errors}


def _rule_median(sorted_values: list) -> float:
    count = len(sorted_values)
    middle = count // 2
    if count % 2 == 1:
        return float(sorted_values[middle])
    return (float(sorted_values[middle - 1]) + float(sorted_values[middle])) / 2.0


def _rule_observable(card: dict) -> tuple:
    observables = card.get("measured_observables") or {}
    if not observables:
        raise ValueError("card has no measured_observables (NOT_MEASURED: reproduction is n/a)")
    expected = (card.get("reproduction") or {}).get("expected") or {}
    ordered = [key for key in expected if key in observables] + [
        key for key in observables if key not in expected
    ]

    def _reference_count(observable: dict) -> int:
        medians = (observable.get("distribution") or {}).get("per_replica_median_deg")
        return len(medians) if isinstance(medians, dict) else 0

    qualifying = [key for key in ordered if _reference_count(observables[key]) >= MIN_REFERENCE_REPLICAS]
    if len(qualifying) == 1:
        return qualifying[0], observables[qualifying[0]]
    if len(qualifying) > 1:
        raise ValueError(f"ambiguous reference observable {qualifying!r}: candidate report must pin 'observable'")
    return ordered[0], observables[ordered[0]]


def evaluate(card: dict, candidate: dict) -> dict:
    """Frozen rule REPRODUCTION_RULE_R1 (reproduction/REPRODUCTION_RULE_R1.md).

    MUST stay semantically identical to scripts/release/reproduction.py in the
    author repository; a conformance test pins the two implementations
    together. Verdict order: TECHNICAL_FAILURE -> INCONCLUSIVE -> MATCH/MISMATCH.
    """
    if str(candidate.get("rule", "")) != RULE_ID:
        raise ValueError(f"candidate report must declare rule {RULE_ID!r}")
    expected_card = candidate.get("card")
    if expected_card is not None and str(expected_card) != str(card.get("component_id")):
        raise ValueError(f"candidate targets card {expected_card!r}, got {card.get('component_id')!r}")
    requested = candidate.get("observable")
    if requested is not None:
        if requested not in (card.get("measured_observables") or {}):
            raise ValueError(f"candidate pins unknown observable {requested!r}")
        name = str(requested)
        observable = card["measured_observables"][name]
    else:
        name, observable = _rule_observable(card)

    distribution = observable.get("distribution") or {}
    medians = distribution.get("per_replica_median_deg")
    reference = {str(key): float(value) for key, value in medians.items()} if isinstance(medians, dict) else {}
    reference_values = sorted(reference.values())

    def report(verdict: str, reasons: list, statistic: dict | None = None) -> dict:
        return {
            "rule": RULE_ID,
            "verdict": verdict,
            "ok": verdict == "REPRODUCTION_MATCH",
            "observable": name,
            "reasons": reasons,
            "candidate_statistic": statistic or {},
            "reference_band": {
                "min_deg": reference_values[0] if reference_values else None,
                "max_deg": reference_values[-1] if reference_values else None,
                "k": len(reference),
                "source": "measured_observables.*.distribution.per_replica_median_deg",
            },
            "reference_pooled_median_deg": observable.get("estimate"),
            "reference_pooled_ci95": observable.get("uncertainty"),
            "ci95_is_not_acceptance_band": True,
        }

    if len(reference) < MIN_REFERENCE_REPLICAS:
        return report(
            "INCONCLUSIVE",
            [f"reference card publishes {len(reference)} per-replica median(s); rule requires >= {MIN_REFERENCE_REPLICAS}"],
        )
    replicas = candidate.get("replicas")
    if not isinstance(replicas, list) or not replicas:
        return report("TECHNICAL_FAILURE", ["candidate report has no replicas: nothing was executed"])
    excluded: list = []
    valid: list = []
    for replica in replicas:
        replica_id = str(replica.get("replica_id", f"replica-{len(valid) + len(excluded) + 1}"))
        if replica.get("gates_passed") is not True:
            excluded.append(replica_id)
            continue
        value = replica.get("median_deg")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"replica {replica_id!r}: median_deg must be a number")
        valid.append(float(value))
    if not valid:
        return report(
            "TECHNICAL_FAILURE",
            [f"all {len(replicas)} replicas failed protocol/integrity gates: not a scientific mismatch"],
            {"excluded": excluded, "n_reported": len(replicas), "n_valid": 0},
        )
    if len(valid) < MIN_VALID_REPLICAS:
        return report(
            "INCONCLUSIVE",
            [f"only {len(valid)} valid replica(s) of {len(replicas)}; frozen J_min = {MIN_VALID_REPLICAS}"],
            {"excluded": excluded, "n_reported": len(replicas), "n_valid": len(valid)},
        )
    m_new = _rule_median(sorted(valid))
    band_min, band_max = reference_values[0], reference_values[-1]
    inside = band_min <= m_new <= band_max
    verdict = "REPRODUCTION_MATCH" if inside else "REPRODUCTION_MISMATCH"
    return report(
        verdict,
        [
            f"M_new = {m_new!r} deg",
            f"reference band [{band_min!r}, {band_max!r}] (k={len(reference)})",
            "pooled bootstrap CI95 of the original estimate is informational only",
        ],
        {
            "excluded": excluded,
            "n_reported": len(replicas),
            "n_valid": len(valid),
            "median_of_replica_medians_deg": m_new,
            "inside_band": inside,
        },
    )


def _self_test_evaluate() -> dict:
    card = {
        "component_id": "self-test/0b",
        "measured_observables": {
            "obs": {
                "estimate": 66.0,
                "uncertainty": [65.9, 66.1],
                "distribution": {"per_replica_median_deg": {"r1": 65.0, "r2": 66.0, "r3": 67.0}},
            }
        },
        "reproduction": {"expected": {"obs": 66.0}},
    }

    def candidate(medians: list, gates: list | None = None) -> dict:
        return {
            "rule": RULE_ID,
            "card": "self-test/0b",
            "replicas": [
                {"replica_id": f"c{index}", "median_deg": median, "gates_passed": True if gates is None else gates[index]}
                for index, median in enumerate(medians)
            ],
        }

    checks = {
        "match_outside_pooled_ci": evaluate(card, candidate([66.4, 66.7, 67.0]))["verdict"] == "REPRODUCTION_MATCH",
        "mismatch_outside_band": evaluate(card, candidate([67.6, 67.8, 68.0]))["verdict"] == "REPRODUCTION_MISMATCH",
        "inconclusive_on_insufficient": evaluate(card, candidate([66.0, 66.1, 66.2], [True, True, False]))["verdict"] == "INCONCLUSIVE",
        "technical_on_gate_failure": evaluate(card, candidate([66.0, 66.1, 66.2], [False, False, False]))["verdict"] == "TECHNICAL_FAILURE",
        "ci95_is_not_acceptance_band": evaluate(card, candidate([66.4, 66.7, 67.0]))["ci95_is_not_acceptance_band"] is True,
    }
    return {"mode": "self-test:evaluate", "ok": all(checks.values()), "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NanoLab component package reproduction helper")
    parser.add_argument("--package-root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("mode", choices=["verify", "plan", "evaluate", "self-test"])
    parser.add_argument("card", nargs="?", help="evaluate: path to the component card JSON")
    parser.add_argument("candidate", nargs="?", help="evaluate: path to the replication campaign report JSON")
    args = parser.parse_args(argv)
    pkg_root = Path(args.package_root).resolve()

    if args.mode == "verify":
        report = verify(pkg_root)
    elif args.mode == "plan":
        report = plan(pkg_root)
    elif args.mode == "evaluate":
        if not args.card or not args.candidate:
            parser.error("evaluate requires CARD_JSON and CANDIDATE_JSON paths")
        try:
            card = json.loads(Path(args.card).read_text(encoding="utf-8"))
            candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
            report = evaluate(card, candidate)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            print(json.dumps({"rule": RULE_ID, "verdict": "RULE_ERROR", "ok": False, "errors": [str(exc)]}, ensure_ascii=False))
            return 2
    else:
        report = {
            "mode": "self-test",
            "verify": verify(pkg_root),
            "plan": plan(pkg_root),
            "evaluate": _self_test_evaluate(),
        }
        report["ok"] = (
            report["verify"].get("ok", False)
            and report["plan"].get("ok", False)
            and report["evaluate"].get("ok", False)
        )

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.mode == "evaluate":
        return 0 if report.get("verdict") == "REPRODUCTION_MATCH" else 3
    return 0 if report.get("ok") else 3


if __name__ == "__main__":
    sys.exit(main())
