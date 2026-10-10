"""Frozen independent-reproduction classifier for NanoLab component release v0.1.

Rule: NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE.
Independent unit = replica median, never individual trajectory frames.
The original pooled bootstrap CI is descriptive evidence only and is NOT used
as a prediction/tolerance interval for a future campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Iterable

RULE_ID = "NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE"
DEFAULT_REQUIRED_REPLICAS = 3


@dataclass(frozen=True)
class ReproductionVerdict:
    rule_id: str
    outcome: str
    reason: str
    reference_envelope_deg: tuple[float, float] | None
    reference_campaign_statistic_deg: float | None
    reproduction_campaign_statistic_deg: float | None
    valid_replicas: int

    def as_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "outcome": self.outcome,
            "reason": self.reason,
            "reference_envelope_deg": list(self.reference_envelope_deg) if self.reference_envelope_deg else None,
            "reference_campaign_statistic_deg": self.reference_campaign_statistic_deg,
            "reproduction_campaign_statistic_deg": self.reproduction_campaign_statistic_deg,
            "valid_replicas": self.valid_replicas,
        }


def _clean(values: Iterable[float | int]) -> list[float]:
    cleaned = [float(v) for v in values]
    if any(v != v for v in cleaned):
        raise ValueError("NaN replica median is not allowed")
    return cleaned


def reference_rule_payload(reference_replica_medians: Iterable[float | int], required_replicas: int = DEFAULT_REQUIRED_REPLICAS) -> dict[str, object]:
    values = _clean(reference_replica_medians)
    if len(values) < required_replicas:
        raise ValueError(f"reference requires at least {required_replicas} replica medians, got {len(values)}")
    lo, hi = min(values), max(values)
    return {
        "rule_id": RULE_ID,
        "independent_unit": "replica_median_deg",
        "required_fresh_replicas": required_replicas,
        "reference_replica_medians_deg": values,
        "reference_replica_envelope_deg": [lo, hi],
        "reference_campaign_statistic_deg": float(median(values)),
        "bootstrap_ci_role": "DESCRIPTIVE_ONLY_NOT_A_REPRODUCTION_TOLERANCE",
    }


def classify(
    reference_replica_medians: Iterable[float | int],
    reproduction_replica_medians: Iterable[float | int],
    *,
    required_replicas: int = DEFAULT_REQUIRED_REPLICAS,
    technical_ok: bool = True,
    integrity_analysis_complete: bool = True,
) -> ReproductionVerdict:
    ref = _clean(reference_replica_medians)
    rep = _clean(reproduction_replica_medians)

    if len(ref) < required_replicas:
        raise ValueError(f"reference requires at least {required_replicas} replica medians, got {len(ref)}")

    ref_lo, ref_hi = min(ref), max(ref)
    ref_stat = float(median(ref))

    if not technical_ok:
        return ReproductionVerdict(
            RULE_ID,
            "INCONCLUSIVE",
            "technical execution did not complete; record execution failure separately",
            (ref_lo, ref_hi),
            ref_stat,
            None,
            len(rep),
        )

    if not integrity_analysis_complete:
        return ReproductionVerdict(
            RULE_ID,
            "INCONCLUSIVE",
            "frozen integrity/analysis surface is incomplete",
            (ref_lo, ref_hi),
            ref_stat,
            float(median(rep)) if rep else None,
            len(rep),
        )

    if len(rep) < required_replicas:
        return ReproductionVerdict(
            RULE_ID,
            "INCONCLUSIVE",
            f"requires at least {required_replicas} valid fresh replica medians, got {len(rep)}",
            (ref_lo, ref_hi),
            ref_stat,
            float(median(rep)) if rep else None,
            len(rep),
        )

    rep_stat = float(median(rep))
    if ref_lo <= rep_stat <= ref_hi:
        return ReproductionVerdict(
            RULE_ID,
            "MATCH",
            "fresh campaign replica-median statistic lies inside the preregistered empirical reference-replica envelope",
            (ref_lo, ref_hi),
            ref_stat,
            rep_stat,
            len(rep),
        )

    if all(v < ref_lo for v in rep) or all(v > ref_hi for v in rep):
        return ReproductionVerdict(
            RULE_ID,
            "MISMATCH",
            "all fresh replica medians are directionally separated from the reference envelope",
            (ref_lo, ref_hi),
            ref_stat,
            rep_stat,
            len(rep),
        )

    return ReproductionVerdict(
        RULE_ID,
        "INCONCLUSIVE",
        "campaign statistic is outside the reference envelope without complete directional separation",
        (ref_lo, ref_hi),
        ref_stat,
        rep_stat,
        len(rep),
    )
