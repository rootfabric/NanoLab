# EX-NL5-001-C-R1 — Clean release reproduction (summary)

## Execution facts

- **WO:** `NL5-001-C-R1` (frozen protocol `docs/work/WO-NL5-001-C-R1.md`), branch `work/nl5-001-c-clean-reproduction-r1`
- **Subject package:** `releases/nanolab-components-v0.1` (main `6577f8b` lineage; frozen candidate `a9950dc`, PR #41 merged)
- **Engine:** oxDNA `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`, CPU double precision (provenance `~/nl5-001-c-env/BUILD_PROVENANCE.md`; rebuild check byte-identical)
- **Inputs:** `gauravarya77/DNA-hinge-simulations @ 23fd1ff7`, download-on-run, 12/12 size+blob_sha1 gates PASS (`evidence/input-download-verification.json`), durable cache forbidden
- **Runs:** 12 (4 MEASURED variants × 3 fresh-seed replicas), started 12:45Z 2026-09-16, finished 02:39Z 2026-09-17; **all engine exit=0, no budget abort** (`evidence/run-reports.json`)
- **Raw artifacts:** disposable run dir outside Git, 112 entries digested in `evidence/artifact-manifest.json` (missing: none)

## Analysis (frozen convention)

Window `t ≤ 150000` steps → 37 frames per replica; frame gates (lbf ≤ 0.1078 / pf_v2 ≥ 0.50 / disp ≤ 20.0): **37/37 valid on every replica**; per-replica median over valid in-window frames; campaign statistic = median of three replica medians; bootstrap CI descriptive only.

## Classification (`NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`)

| variant | fresh replica medians (deg) | campaign statistic (deg) | reference envelope (deg) | outcome |
|---|---|---|---|---|
| 0b  | 66.159296437, 67.279863514, 65.350402836 | 66.159296437 | [65.095434789, 67.236579608] | **MATCH** |
| 11b | 75.514562357, 72.834291464, 75.636625463 | 75.514562357 | [72.165683993, 74.533109426] | **INCONCLUSIVE** |
| 32b | 78.939838677, 78.096569929, 73.050085356 | 78.096569929 | [77.4927314, 79.877463339] | **MATCH** |
| 53b | 133.109255574, 130.592247501, 132.575590442 | 132.575590442 | [131.049227687, 135.285186059] | **MATCH** |

- **11b INCONCLUSIVE** — campaign statistic outside the reference envelope without complete directional separation (S002 below `ref_max`; S001/S003 above `ref_min`). Preserved as a durable honest outcome; the rule's conservative middle region exists precisely because the reference has only three replicas. No additional replicas may be launched without a new protocol revision (no post-hoc threshold/tuning changes).
- **74b** remains `NOT_MEASURED / KNOWN_GAP`; not classified.

## Technical vs scientific outcome

- `execution_outcome`: **COMPLETED** (12/12 runs, integrity/analysis surface complete).
- `scientific_outcome`: recorded per-variant as the classification facts above; interpretation and acceptance belong to Fresh Reviewer → Fresh Verifier → Human Gate, not to this execution record.

## Open risks

1. Interpretation of 11b INCONCLUSIVE (within-rule outcome; no physics claim beyond it).
2. Merge decision — Human Gate (owner pre-approval applies to this mission chain).
3. Raw trajectories are NOT archived (REFERENCE_ONLY inputs; disposable run dir) — digests recorded in the artifact manifest.
