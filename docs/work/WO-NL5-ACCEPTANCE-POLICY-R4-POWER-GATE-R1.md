# Work Order WO-NL5-ACCEPTANCE-POLICY-R4-POWER-GATE-R1

Status: **STARTED / PRE-DATA / NOT FROZEN**  
Parent: `WO-NL5-ACCEPTANCE-POLICY-R2` / candidate R3.1 @ `290cba6e4be40d3afa91e670ab50e58f7bbd7d35`  
Base scientific facts: unchanged.  
Risk: **HIGH** (future acceptance/protocol design). Claim ceiling: **C0_SOFTWARE_ONLY**.

## 1. Trigger

Fresh R3 review/verification accepted the machine consistency of candidate R3, but the
reviewer surfaced a material design risk: at the selected `N=64`, its planning
Monte-Carlo estimate gave approximately **6% WO-level probability of REPRODUCED under
ideal equivalence**. A CI-width feasibility gate alone therefore does not establish
that the future campaign is decision-useful.

This repair is opened **before freeze and before any v0.2 confirmatory simulation**.

## 2. Immutable boundaries

Do not change or reinterpret:

- NL5-002 terminal VERIFIED MISMATCH / NOT ACCEPTED.
- NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE.
- PLATFORM-SENSITIVITY-R1 = PLATFORM_INSENSITIVE / FULLY VERIFIED.
- NL5 = IN_PROGRESS; external_reproductions = 0; NL6-001 = LOCKED.
- Windows/WSL = HISTORICAL_ONLY; outenemy = EXTERNAL_U2.
- No v0.2 scientific run is allowed by this WO.
- R3/R3.1 evidence is append-only historical evidence.

## 3. Purpose

Add a **pre-data decision-power gate** in addition to the existing CI-width
feasibility gate. The campaign may become a freeze candidate only when both gates
pass.

The repair must answer:

> If U1 and U2 are genuinely equivalent under the planning model, is the frozen
> decision procedure sufficiently likely to return EQUIVALENT for both primaries,
> rather than merely having a narrow expected CI?

## 4. Power target (candidate R4 planning contract)

Before running the R4 power calculations, pin:

```text
per-primary target:
    P(EQUIVALENT(v) | ideal equivalence planning model) >= 0.90

WO-level guaranteed target:
    >= 0.80
```

The 0.80 WO-level target is obtained conservatively from the per-primary 0.90
requirements by the union bound; no independence assumption between variant
outcomes is required.

A jointly simulated WO probability may also be published, but it is secondary to
the conservative per-primary gate.

These are **design/power targets**, not scientific acceptance thresholds.

## 5. Planning model

Use only committed historical R1 platform-study paired medians. No future v0.2
confirmatory data exist or may be used.

For each primary variant independently:

1. Load the ten committed pairs `(A_i, B_i)`.
2. Compute `m = median(B_i - A_i)`.
3. Construct an ideal-equivalence planning support:
   ```text
   A*_i = A_i + m/2
   B*_i = B_i - m/2
   ```
   This preserves each platform's spread and pair structure while forcing the
   paired median shift to zero.
4. The power model must sample **paired indices**, preserving the paired design.
5. Every random stream must have a deterministic, predeclared RNG seed derived from
   the protocol anchor and label; no hand-picked random seeds.

Reviewer may propose a stricter model, but any replacement must be committed before
its result is inspected and must remain based only on historical planning evidence.

## 6. Exact future rule binding

The power evaluator must evaluate pseudo-experiments with the same scientific
classification rule intended for confirmatory data:

- `d_i = B_i - A_i`;
- `Delta_hat = median(d_i)`;
- `s = pooled within-platform SD(n-1)`;
- `s_eff = max(s, 0.01 deg)`;
- equivalence margin = `+-0.5*s_eff`;
- paired percentile CI90 for median difference;
- EQUIVALENT only when CI90 is wholly inside the margin.

If a computational approximation is used for the large N-grid, it must be
predeclared and independently validated against the exact future rule at the
selected/boundary N before PASS is possible.

## 7. Declared power-search grid

Do not silently reuse the R3 N=64 result.

Before calculating power, commit the search grid and selection rule. Recommended
bounded grid:

```text
N = {64, 80, 96, 128, 160, 192, 256}
```

Selection rule:

```text
minimal N for which:
  existing CI-width feasibility gate passes for both primaries
  AND
  R4 per-primary power >= 0.90 for both primaries
```

If no N in the declared grid passes, record
`DESIGN_INFEASIBLE_AT_CURRENT_RULE`; do not alter delta, variants, or thresholds
merely to obtain PASS.

## 8. Budget rule

For any selected N, recompute all linked surfaces mechanically:

- seed cardinalities;
- fresh-seed record;
- N_min;
- confirmatory run count;
- <=20% FAILED_TECHNICAL replacement ceiling;
- wall/CPU budget;
- freeze consistency gate.

If the selected N exceeds an owner-authorized resource ceiling, the result is
`BLOCKED_BUDGET`, not a scientific failure.

Paid compute remains forbidden without owner authorization.

## 9. Required machine gates

R4 must add fail-closed checks for:

1. protocol N == seed-record N == execution N == budget N == N_min basis;
2. power-model source digest equals committed historical evidence;
3. power configuration (outer trials, inner/bootstrap procedure, RNG derivation,
   quantile convention) is machine-readable and pinned;
4. result is deterministic from pinned inputs;
5. per-primary power target is checked mechanically;
6. CI-width gate still passes;
7. changing a power result/evidence digest causes the freeze gate to fail.

## 10. Required evidence

Publish append-only evidence containing the complete declared grid, including all
failed rows, and at least:

```text
N
P_EQUIVALENT_0B
P_EQUIVALENT_32B
conservative_WO_lower_bound
joint_MC_estimate (if computed)
CI-width ratios
budget
gate_pass
```

Do not drop inconvenient rows.

## 11. Review requirements

Fresh Scientific Reviewer must independently reproduce the power calculation and
explicitly answer:

- Does the power model use only historical planning data?
- Is ideal equivalence imposed without shrinking historical variability?
- Is the future decision rule faithfully represented?
- Is the target chosen pre-data and applied mechanically?
- Is the selected N the minimum passing declared-grid value?
- Would an actually equivalent system have a useful probability of resolving NL5?

Fresh Verifier must independently regenerate power evidence, seed cardinalities,
budget and both feasibility gates on the exact reviewed HEAD.

No self-review/self-verification.

## 12. Stop conditions

Stop and preserve evidence if any applies:

- no declared-grid N passes;
- estimated power cannot be reproduced;
- exact-rule validation disagrees materially with an approximation;
- required N violates resource policy;
- any request is made to change delta/decision thresholds after examining future
  confirmatory data.

## 13. Completion

This WO completes at:

```text
R4 candidate PRE-DATA / NOT FROZEN
+ deterministic power evidence
+ both feasibility gates PASS (or honest infeasible result)
+ Fresh Reviewer PASS
+ Fresh Verifier VERIFIED
```

Only then may HG-B consider R4 as a freeze basis. This WO itself does not freeze
v0.2, activate R2, run physics, accept NL5 or unlock NL6.
