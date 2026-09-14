"""Frozen independent-reproduction rule REPRODUCTION_RULE_R1 (stdlib-only).

Normative executor of docs/research/REPRODUCTION_RULE_R1.md (repair R1, finding
F-B3): compares an independent replication campaign against a published
component card WITHOUT misusing the card's pooled bootstrap CI95 as a
prediction band. The pooled CI95 quantifies the uncertainty of the original
estimate; the acceptance band below is derived from the ORIGINAL campaign's
own between-replica spread.

Frozen constants (docs/research/REPRODUCTION_RULE_R1.md §2) MUST NOT be tuned
after replication data have been observed; a change requires rule revision R2.

Verdict order is fixed: TECHNICAL_FAILURE -> INCONCLUSIVE -> MATCH/MISMATCH.
Pure function of (card, candidate_report); deterministic; no I/O.
"""

from __future__ import annotations

import json
from typing import Any

RULE_ID = "REPRODUCTION_RULE_R1"
MIN_VALID_REPLICAS = 3
MIN_REFERENCE_REPLICAS = 2

VERDICT_MATCH = "REPRODUCTION_MATCH"
VERDICT_MISMATCH = "REPRODUCTION_MISMATCH"
VERDICT_INCONCLUSIVE = "INCONCLUSIVE"
VERDICT_TECHNICAL = "TECHNICAL_FAILURE"


class RuleError(ValueError):
    """Malformed input that the frozen rule cannot evaluate (caller error)."""


def _median(sorted_values: list[float]) -> float:
    count = len(sorted_values)
    middle = count // 2
    if count % 2 == 1:
        return float(sorted_values[middle])
    return (float(sorted_values[middle - 1]) + float(sorted_values[middle])) / 2.0


def _reference_medians(observable: dict[str, Any]) -> dict[str, float]:
    distribution = observable.get("distribution") or {}
    medians = distribution.get("per_replica_median_deg")
    if not isinstance(medians, dict):
        return {}
    return {str(key): float(value) for key, value in medians.items()}


def _select_observable(card: dict[str, Any], candidate: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Select the reference observable for the comparison.

    Deterministic order: candidate pin, then reproduction.expected keys, then
    remaining observables. Only observables publishing at least
    MIN_REFERENCE_REPLICAS per-replica medians can define a band; ambiguity is
    a caller error, absence falls through to the INCONCLUSIVE path.
    """
    observables = card.get("measured_observables")
    if not isinstance(observables, dict) or not observables:
        raise RuleError("card has no measured_observables (NOT_MEASURED: reproduction is n/a)")
    expected = (card.get("reproduction") or {}).get("expected") or {}
    ordered = [key for key in expected if key in observables] + [
        key for key in observables if key not in expected
    ]
    requested = candidate.get("observable")
    if requested is not None:
        if requested not in observables:
            raise RuleError(f"candidate pins observable {requested!r} which the card does not publish")
        return str(requested), observables[requested]
    qualifying = [
        key
        for key in ordered
        if len(_reference_medians(observables[key])) >= MIN_REFERENCE_REPLICAS
    ]
    if len(qualifying) == 1:
        return qualifying[0], observables[qualifying[0]]
    if len(qualifying) > 1:
        raise RuleError(
            f"ambiguous reference observable {qualifying!r}: candidate report must pin 'observable'"
        )
    return ordered[0], observables[ordered[0]]


def evaluate(card: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a replication campaign report against a published card.

    candidate_report: {"rule": "REPRODUCTION_RULE_R1", "card": "<component_id>",
        "replicas": [{"replica_id", "median_deg", "frames_valid", "frames_total",
        "gates_passed": bool}, ...]}
    """
    if str(candidate.get("rule", "")) != RULE_ID:
        raise RuleError(f"candidate report must declare rule {RULE_ID!r}")
    expected_card = candidate.get("card")
    if expected_card is not None and str(expected_card) != str(card.get("component_id")):
        raise RuleError(
            f"candidate report targets card {expected_card!r}, got {card.get('component_id')!r}"
        )

    name, observable = _select_observable(card, candidate)
    reference = _reference_medians(observable)
    if len(reference) < MIN_REFERENCE_REPLICAS:
        return _verdict(
            VERDICT_INCONCLUSIVE,
            [
                f"reference card publishes {len(reference)} per-replica median(s); "
                f"frozen rule requires >= {MIN_REFERENCE_REPLICAS} to derive the band",
            ],
            name,
            reference,
            observable,
            None,
        )
    reference_values = sorted(reference.values())
    band_min, band_max = reference_values[0], reference_values[-1]

    replicas = candidate.get("replicas")
    if not isinstance(replicas, list) or not replicas:
        return _verdict(
            VERDICT_TECHNICAL,
            ["candidate report has no replicas: nothing was executed (TECHNICAL_FAILURE, not a scientific outcome)"],
            name,
            reference,
            observable,
            None,
        )

    excluded: list[str] = []
    valid: list[float] = []
    for replica in replicas:
        replica_id = str(replica.get("replica_id", f"replica-{len(valid) + len(excluded) + 1}"))
        if replica.get("gates_passed") is not True:
            excluded.append(replica_id)
            continue
        if not isinstance(replica.get("median_deg"), (int, float)) or isinstance(replica.get("median_deg"), bool):
            raise RuleError(f"replica {replica_id!r}: median_deg must be a number")
        valid.append(float(replica["median_deg"]))

    if not valid:
        return _verdict(
            VERDICT_TECHNICAL,
            [f"all {len(replicas)} replicas failed protocol/integrity gates: TECHNICAL_FAILURE, not a scientific mismatch"],
            name,
            reference,
            observable,
            {"excluded": excluded, "n_reported": len(replicas), "n_valid": 0},
        )
    if len(valid) < MIN_VALID_REPLICAS:
        return _verdict(
            VERDICT_INCONCLUSIVE,
            [
                f"only {len(valid)} valid replica(s) of {len(replicas)} reported; frozen J_min = {MIN_VALID_REPLICAS}",
                f"excluded by gate failure: {excluded or 'none'}",
            ],
            name,
            reference,
            observable,
            {"excluded": excluded, "n_reported": len(replicas), "n_valid": len(valid)},
        )

    median_of_medians = _median(sorted(valid))
    inside = band_min <= median_of_medians <= band_max
    verdict = VERDICT_MATCH if inside else VERDICT_MISMATCH
    reasons = [
        f"M_new (median of {len(valid)} valid replica medians) = {median_of_medians!r} deg",
        f"reference band [min, max] of {len(reference)} original replica medians = [{band_min!r}, {band_max!r}]",
    ]
    if excluded:
        reasons.append(f"excluded by gate failure: {excluded}")
    reasons.append(
        "pooled bootstrap CI95 of the original estimate is informational only; "
        "ci95_is_not_acceptance_band"
    )
    return _verdict(
        verdict,
        reasons,
        name,
        reference,
        observable,
        {
            "excluded": excluded,
            "n_reported": len(replicas),
            "n_valid": len(valid),
            "median_of_replica_medians_deg": median_of_medians,
            "inside_band": inside,
        },
    )


def _verdict(
    verdict: str,
    reasons: list[str],
    observable_name: str,
    reference: dict[str, float],
    observable: dict[str, Any],
    candidate_statistic: dict[str, Any] | None,
) -> dict[str, Any]:
    reference_values = sorted(reference.values())
    return {
        "rule": RULE_ID,
        "verdict": verdict,
        # "ok" = scientific pass ONLY; MISMATCH / INCONCLUSIVE /
        # TECHNICAL_FAILURE are honest non-pass outcomes.
        "ok": verdict == VERDICT_MATCH,
        "observable": observable_name,
        "reasons": reasons,
        "candidate_statistic": candidate_statistic or {},
        "reference_band": {
            "min_deg": reference_values[0] if reference_values else None,
            "max_deg": reference_values[-1] if reference_values else None,
            "k": len(reference),
            "source": "measured_observables.*.distribution.per_replica_median_deg",
        },
        "reference_pooled_median_deg": observable.get("estimate"),
        # Informational only: the CI95 of the ORIGINAL estimate is NOT the
        # acceptance band (docs/research/REPRODUCTION_RULE_R1.md §1).
        "reference_pooled_ci95": observable.get("uncertainty"),
        "ci95_is_not_acceptance_band": True,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI: evaluate CARD_JSON CANDIDATE_JSON (prints the verdict report)."""
    import argparse
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(prog="release.reproduction", description=f"Frozen reproduction rule {RULE_ID}")
    parser.add_argument("card", help="path to component card JSON")
    parser.add_argument("candidate", help="path to replication campaign report JSON")
    args = parser.parse_args(argv)
    try:
        card = json.loads(Path(args.card).read_text(encoding="utf-8"))
        candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
        report = evaluate(card, candidate)
    except (RuleError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"rule": RULE_ID, "verdict": "RULE_ERROR", "ok": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # Harness exit-code style: 0 = scientific pass (MATCH), 3 = honest
    # non-pass (MISMATCH / INCONCLUSIVE / TECHNICAL_FAILURE), 2 = rule error.
    return 0 if report.get("verdict") == VERDICT_MATCH else 3


if __name__ == "__main__":
    raise SystemExit(main())
