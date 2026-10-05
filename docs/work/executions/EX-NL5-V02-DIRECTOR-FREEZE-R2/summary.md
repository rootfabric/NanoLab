# EX-NL5-V02-DIRECTOR-FREEZE-R2 — Summary

Corrected immutable **FROZEN_R2** package after fresh Scientific Reviewer R1
verdict **FIX_REQUIRED** on FROZEN_R1 (`F1 = cb91ade761f6802fc40c500761d3e35022408822`,
tree `ad21ce39b42681f581da996b2805a5b2fb49111f`).

- **WO:** `docs/work/WO-NL5-V02-DIRECTOR-FREEZE-R2.md`
- **Branch:** `repair/nl5-v02-director-freeze-r2` (base `49bda9bad9110c4598d10aa20a28cf5b062acf13`,
  reviewer branch merged `--no-ff`)
- **Claim ceiling:** C0_SOFTWARE_ONLY; **scientific runs: 0**

## Defect M-1 (review `FRESH_SCIENTIFIC_REVIEW_R1.md`)

FROZEN_R1 protocol §6 declared the collision-scan exact allowlist as the later
frozen-package paths, while the authoritative contract preserves the approved R4
pinned-tree allowlist (`a9d7d07fa264e9907b67ca244b00ba2da3430b0f`):

```text
docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/
repro-v0-2-seed-record-PRE_DATA_R4.json
```

FROZEN_R1 and Director Freeze R1 remain immutable historical evidence of a
reviewed FAIL freeze revision; they are not amended.

## Repair phases

1. **Phase A** — fail-closed FROZEN-only `scan-allowlist-v1` protocol declaration
   machine-bound to `contract["seed_generation"]["scan_allowlist_paths_exact"]`
   (+ regression tests: missing/duplicate/malformed/order-drift/frozen-package
   paths → `FREEZE_GATE_FAIL`; PRE-DATA R4 historical package stays PASS).
2. **Phase B/C** — FROZEN_R2 protocol/contract/seed-record; seed record
   byte-identical to R4/F1; contract delta only the 3 allowlisted
   `scientific_subject` leaves; full frozen gate + M-1 negative control.
3. **Phase D/E** — immutable `F2` commit; later `DIRECTOR_FREEZE_R2` record
   commit pinning F2.

## Status

IN_PROGRESS (START recorded before substantive edits).
