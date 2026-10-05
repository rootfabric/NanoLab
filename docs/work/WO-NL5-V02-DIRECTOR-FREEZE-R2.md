# WO-NL5-V02-DIRECTOR-FREEZE-R2 — Correct frozen collision-allowlist binding

Status: **PLANNED / REPAIR REQUIRED AFTER FROZEN_R1 REVIEW FAIL**
Risk: **HIGH** — frozen scientific protocol integrity.
Claim ceiling: **C0_SOFTWARE_ONLY**.
Scientific runs: **0**.

## Trigger

Fresh Scientific Reviewer R1 on exact frozen subject:

```text
FROZEN_R1_HEAD =
cb91ade761f6802fc40c500761d3e35022408822

FROZEN_R1_TREE =
ad21ce39b42681f581da996b2805a5b2fb49111f

VERDICT =
FIX_REQUIRED
```

Finding M-1: FROZEN_R1 protocol `6 declares collision-scan exact allowlist as
the new frozen protocol/seed paths, while the authoritative contract correctly
preserves the approved R4 allowlist in pinned historical tree `a9d7d07...`:
candidate protocol + PRE_DATA_R4 seed-record paths.

FROZEN_R1 and DIRECTOR_FREEZE_R1 are immutable historical evidence and must not
be amended or rewritten.

## Goal

Create a corrected immutable **FROZEN_R2** package with no scientific/numeric
changes, plus a fail-closed validator regression that prevents future protocol /
contract allowlist drift.

Required history:

```text
F1 = FROZEN_R1 (immutable, review FAIL)
D1 = Director FREEZE R1 (immutable)

tooling repair commit
  ↓
F2 = corrected FROZEN_R2 package commit
  ↓
D2 = Director FREEZE R2 record
  ↓
fresh Scientific Reviewer(F2)
  ↓
fresh independent Verifier(F2)
```

## Scientific ceiling

No changes to:

```text
rule_id
candidate revision R4
N = 64/64/10/10
N_min = 52/52/8/8
replacement quotas = 12/12/2/2
confirmatory = 296
replacement cap = 56
max_runs = 352
delta = 0.5
paired TOST
bootstrap seeds/resamples
confirmatory identities
replacement identities/cursors/skips
historical exclusions
analyzer/environment pins
74b exclusion
```

Seed record remains byte-identical to approved R4/FROZEN_R1.

## Correct allowlist

The collision proof scans pinned tree:

```text
a9d7d07fa264e9907b67ca244b00ba2da3430b0f
```

Therefore the exact approved allowlist is:

```text
docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md

docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/
repro-v0-2-seed-record-PRE_DATA_R4.json
```

These paths exist in the pinned historical scan tree and contain the generated
seed literals that are intentionally excluded from collision detection.

FROZEN_R2 package paths are later Git objects and are NOT substitutions for the
allowlist of that pinned historical scan.

## Validator hardening

Before creating F2, add a fail-closed FROZEN-only protocol/contract check for
`scan_allowlist_paths_exact`.

Do not rewrite the historical PRE-DATA R4 candidate merely to satisfy a new
parser.

Recommended shape: introduce a deterministic FROZEN-only marked declaration
(e.g. `scan-allowlist-v1`) in the frozen protocol; parse exactly one such
declaration and compare its ordered exact paths against
`contract.seed_generation.scan_allowlist_paths_exact`.

Required tests:

```text
FROZEN protocol exact allowlist == contract allowlist -> may PASS

FROZEN protocol uses frozen-package protocol/seed paths while contract uses
approved R4 pinned-tree paths -> FREEZE_GATE_FAIL

missing FROZEN allowlist declaration -> FREEZE_GATE_FAIL
duplicate/extra/malformed allowlist declaration -> FREEZE_GATE_FAIL
path-order or exact-string drift according to chosen canonical semantics -> reject
```

PRE-DATA R4 historical validation remains green.

## FROZEN_R2 artifacts

Recommended:

```text
docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md

docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/
repro-v0-2-freeze-contract-FROZEN_R2.json

docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/
repro-v0-2-seed-record-FROZEN_R2.json
```

The FROZEN_R2 contract must be derived from the approved PRE_DATA_R4 contract
and differ only in freeze-package metadata/path leaves:

```text
scientific_subject.candidate_doc_path
scientific_subject.freeze_status
scientific_subject.seed_record_path
```

All 307 scientific/control leaves that were preserved in R1 remain preserved.

## Director R2 record

Create only after F2 exists:

```text
docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R2.md
docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R2.json
```

It must pin exact F2 HEAD/TREE and protocol/contract/seed blob identities.

## State ceiling

Always:

```text
SCIENTIFIC_RUNS = 0
AUTHOR_U1 = NOT_ASSIGNED
R2 = WAITING_HOST / NOT_ACTIVE
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED
dispatch = BLOCKED
```

## Acceptance

Ready for review only when:

- F1/D1 unchanged;
- validator regression catches the M-1 class;
- full tests/harness/work_cli green;
- F2 exists as immutable real Git commit;
- D2 exists in strict descendant commit and pins F2;
- no science or status inflation.

Next: fresh Scientific Reviewer(F2), then fresh Verifier(F2).
