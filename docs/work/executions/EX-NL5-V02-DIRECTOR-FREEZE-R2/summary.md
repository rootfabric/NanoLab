# EX-NL5-V02-DIRECTOR-FREEZE-R2 — Summary (HANDOFF_READY)

Corrected immutable **FROZEN_R2** package after fresh Scientific Reviewer R1
verdict **FIX_REQUIRED** on FROZEN_R1 (`F1 = cb91ade761f6802fc40c500761d3e35022408822`,
tree `ad21ce39b42681f581da996b2805a5b2fb49111f`).

- **WO:** `docs/work/WO-NL5-V02-DIRECTOR-FREEZE-R2.md`
- **Branch:** `repair/nl5-v02-director-freeze-r2` (base handoff
  `control/nl5-v02-director-freeze-r1` @ `49bda9bad9110c4598d10aa20a28cf5b062acf13`;
  reviewer branch merged `--no-ff`, merge `8ec75bc0d7ab076ec72a3f0fdb370d7ee66f3674`)
- **Claim ceiling:** C0_SOFTWARE_ONLY; **scientific runs: 0**

## Commit chain

```text
3801f16  START (EX passport + event 0001)
8ec75bc  merge of reviewer branch (FIX_REQUIRED / M-1)
db8227a  Phase A tooling repair: fail-closed scan-allowlist-v1 binding + 12 regressions  (pushed)
60da9a8  F2 = immutable FROZEN PACKAGE COMMIT (FROZEN_R2)                                (pushed)
a2f7304  D2 = Director FREEZE R2 record (strict descendant of F2)                        (pushed)
<this>   handoff bookkeeping (event 0003, summary, WORK_QUEUE)
```

## Defect M-1 → FIXED

FROZEN_R1 protocol §6 declared the collision-scan exact allowlist as the later
frozen-package paths; the authoritative contract preserves the approved R4
pinned-tree allowlist (`a9d7d07fa264e9907b67ca244b00ba2da3430b0f`):

```text
docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/
repro-v0-2-seed-record-PRE_DATA_R4.json
```

Repair (map: `evidence/REPAIR_MAP_M1.md`):

1. Fail-closed FROZEN-only `scan-allowlist-v1` protocol declaration, machine-bound
   ordered-exact to `contract["seed_generation"]["scan_allowlist_paths_exact"]`
   (`scripts/nl5/repro_v02_freeze_contract.py`); PRE-DATA R4 historical documents untouched.
2. `FROZEN_R2` protocol/contract/seed-record: seed record **byte-identical** to
   R4 / FROZEN_R1 (same Git blob `0164e0e3…`, sha256 `8e844bff…`); contract delta
   = exactly the 3 allowlisted `scientific_subject` leaves (307/310 unchanged).
3. FROZEN_R1 / Director FREEZE R1 preserved unamended as historical immutable
   attempt (review FAIL), superseded for dispatch by FROZEN_R2.

## F2 (immutable, exact review/verify target)

```text
F2_HEAD  = 60da9a846511265a8ac7564da088c3d74cb073f0
F2_TREE  = e565c8a6cee9e829fac14008ebc9c2ea1609931d
protocol    blob 4835719622bae49a8e8b480536a482b4b222d408  sha256 2658ee3e…
contract    blob d6a9ccde4d1dadf42d1a8cd9b88faa02646cf70b  sha256 7e647654…
seed record blob 0164e0e3f5dda6dbf63174df3730b1bd921d2c76  sha256 8e844bff…
```

`DIRECTOR_FREEZE_R2_COMMIT = a2f7304ebbb5973b81cf49dee60c21c85c6a974d`
(record JSON blob `68d8b868bc0a4a4d4fa02c07d81ce9832a48c37a`, canonical
sha256 `766ed0602ec68797738985621785178d3867062f80c233776423cc10ff0ead93`).

## Gates (final)

```text
FROZEN_GATE          = PASS (PREFREEZE_VALIDATION_PASS / FROZEN / DISPATCH_BLOCKED /
                       dispatch_ready false; full pinned-scan re-run)
ALLOWLIST_REGRESSION = PASS (positive PASS + negatives FREEZE_GATE_FAIL/exit 3;
                       evidence m1-negative-control-R2.json)
NEGATIVE_WRONG_ALLOWLIST = FREEZE_GATE_FAIL / exit 3
unittest             = 605 OK (was 593; +12 ScanAllowlistBindingTest)
check-consistency    = ok (0 errors / 0 warnings)
workflow_lint        = blocking 0
work_cli             = 51/51 EX-* ok
SCIENTIFIC_RUNS      = 0
```

## State ceiling (unchanged)

```text
HG-B = APPROVED; NL5 = IN_PROGRESS; NL6-001 = LOCKED; AUTHOR_U1 = NOT_ASSIGNED;
R2 = WAITING_HOST / NOT_ACTIVE; external_reproductions = 0;
machine_launch_authorized = false; launch_gate = HUMAN_PROTECTED_WRITER
```

## Next actor

**fresh SCIENTIFIC REVIEWER(F2)** — pin exact `F2_HEAD/F2_TREE` above (not F1,
not D2/bookkeeping commits); then fresh independent VERIFIER(F2); then the
authority-builder WO (A). **DO NOT START SCIENCE.**
