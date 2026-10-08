# REPAIR_MAP_M1 — Director Freeze R2 (FROZEN_R1 review FIX_REQUIRED)

Review subject: **FROZEN_R1 = F1** `cb91ade761f6802fc40c500761d3e35022408822`
(tree `ad21ce39b42681f581da996b2805a5b2fb49111f`) — verdict
`FAIL / FIX_REQUIRED`, evidence `docs/evidence/NL5-V02-FREEZE/FRESH_SCIENTIFIC_REVIEW_R1.{md,json}`.

FROZEN_R1 and Director FREEZE R1 (`4236e0c7cfb19de2687a8f0d3be3641cc1b000d4`)
are NOT amended: they remain immutable historical evidence of a reviewed FAIL
freeze revision, superseded for dispatch by FROZEN_R2.

## M-1 — frozen protocol collision-scan allowlist contradicts the authoritative contract

```text
Finding    FROZEN_R1 protocol §6 declared exact path allowlist =
           {seed record path, frozen protocol path of the package}
Authoritative (approved R4, correct) contract
           seed_generation.scan_allowlist_paths_exact =
           docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
           docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/
             repro-v0-2-seed-record-PRE_DATA_R4.json
Reason     the collision scan is a search of the PINNED historical tree
           a9d7d07fa264e9907b67ca244b00ba2da3430b0f; the allowlisted
           locations are the ones existing in that tree; later frozen-package
           paths are not allowlist substitutes
Escape     _validate_protocol() did not machine-bind the declared allowlist
```

## Fix map

| # | Change | Surface |
|---|--------|---------|
| 1 | `scan-allowlist-v1` FROZEN-only marked block parser (`_scan_allowlist_blocks`, `parse_protocol_scan_allowlist`): single-instance, `path_N` consecutive `1..K`, repo-relative exact paths, ordered | `scripts/nl5/repro_v02_freeze_contract.py` |
| 2 | `_validate_protocol()` FROZEN-only binding: exactly one block required; ordered exact equality with `contract["seed_generation"]["scan_allowlist_paths_exact"]`; PRE-DATA protocols must NOT carry the block (historical R4 documents untouched) | same |
| 3 | Regression class `ScanAllowlistBindingTest` (12 tests): correct allowlist PASS (incl. full `freeze_gate` scan re-run); M-1 frozen-package paths FAIL; missing/duplicate/malformed/non-consecutive/extra/order-drift FAIL; PRE-DATA R4 PASS; CLI exit 3 | `tests/test_nl5_v02_prefreeze_r4.py` |
| 4 | Synthetic dispatch-authority fixture carries the canonical block for FROZEN subjects (fixtures satisfy the strengthened gate; negative authority tests unaffected) | same test file |
| 5 | New immutable corrected revision `FROZEN_R2` (`docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md`): §6 allowlist prose corrected, machine-readable `scan-allowlist-v1` block added, explicit pinned-tree explanation, revision/provenance metadata; scientific content identical | `docs/research/` |
| 6 | `FROZEN_R2` contract derived from approved `PRE_DATA_R4` contract with ONLY the three allowlisted `scientific_subject` leaves changed (307/310 leaves unchanged — `frozen-package-delta-check-R2.json`) | `EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/` |
| 7 | `FROZEN_R2` seed record byte-identical to R4 / FROZEN_R1 (`cmp` clean, SHA-256 `8e844bff…` — `seed-record-identity-R2.json`) | same |

## Negative controls (all must fail closed — proven)

```text
frozen protocol declares frozen-package paths            -> FREEZE_GATE_FAIL / exit 3
raw historical FROZEN_R1 protocol (no block)             -> FREEZE_GATE_FAIL / exit 3
duplicate scan-allowlist-v1 block                        -> FREEZE_GATE_FAIL
malformed content line / non-consecutive path_N          -> FREEZE_GATE_FAIL
extra path / order drift (ordered exact semantics)       -> FREEZE_GATE_FAIL
scan-allowlist-v1 in a PRE-DATA protocol                 -> FREEZE_GATE_FAIL
```

## Scientific delta ceiling

```text
scientific parameters      UNCHANGED (R4 basis; see frozen-package-delta-check-R2.json)
seed record                BYTE-IDENTICAL to R4 / FROZEN_R1
scientific runs            0
```
