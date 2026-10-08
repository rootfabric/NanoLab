# WO-NL5-V02-DIRECTOR-FREEZE-R1 — Freeze v0.2 package F

Status: **IN_PROGRESS / PRE-DATA / NO SCIENCE**  
Risk: **HIGH** — scientific protocol freeze / acceptance-control surface.  
Claim ceiling: **C0_SOFTWARE_ONLY**.  
Parent stage: **NL5**.

## 1. Canonical starting point

```text
BASE_MAIN =
549b687a9171ea3636dbb00078d7018f619cebd3

BASE_TREE =
5bfb2411d6283420e9067850807c6650725d838b

HG-B =
APPROVED

NL5 =
IN_PROGRESS

external_reproductions =
0

SCIENTIFIC_RUNS =
0

AUTHOR_U1 =
NOT_ASSIGNED

R2 =
WAITING_HOST / NOT_ACTIVE
```

HG-B decision:
`docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.{md,json}`.

Approved rule:
`NANOLAB_REPRO_V0_2_DISTRIBUTIONAL`, R4 scientific basis, post-R4.3 hardened control plane.

## 2. Goal

Create the first real immutable **FROZEN PACKAGE COMMIT F** for v0.2.

The required lifecycle is:

```text
S = current PRE-FREEZE state (HG-B approved)
F = immutable FROZEN PACKAGE COMMIT
D = later Director FREEZE record commit, pinning F
R = later fresh Reviewer record, reviewed_head/tree = F
V = later fresh Verifier record, verified_head/tree = F
A = later authority/readiness record
```

This WO performs **F + D preparation only**. It must NOT run science, activate R2, assign AUTHOR_U1, accept NL5, or unlock NL6.

## 3. Frozen package artifacts

The F commit must contain exact immutable Git blobs for:

```text
protocol =
docs/research/NANOLAB_REPRO_V0_2_FROZEN_R1.md

contract =
docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/
  repro-v0-2-freeze-contract-FROZEN_R1.json

seed record =
docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/
  repro-v0-2-seed-record-FROZEN_R1.json
```

The frozen seed record must be byte-for-byte identical to the accepted R4 PRE-DATA seed record unless the validator itself proves a required metadata-only transformation. Scientific identities MUST NOT change.

The frozen contract is derived from the accepted PRE-DATA R4 contract. Allowed scientific-subject changes are only:

```text
candidate_doc_path -> frozen protocol path
seed_record_path -> frozen seed-record path
seed_record_file_sha256 -> exact frozen seed-record file SHA-256
freeze_status -> FROZEN
frozen_subject_head -> null
frozen_subject_tree -> null
```

All scientific/statistical fields remain identical to the HG-B approved R4 basis.

## 4. Frozen scientific invariants

Must remain exact:

```text
rule_id = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL
candidate_revision = R4

N = 64 / 64 / 10 / 10
N_min = 52 / 52 / 8 / 8
replacement quota pairs = 12 / 12 / 2 / 2
confirmatory_runs = 296
replacement_runs_cap = 56
max_runs = 352
wall_hours_per_platform = 560

delta = 0.5
paired TOST
bootstrap resamples = 10000
integer policy = ceil-nmin-floor-replacement-pairs-v1
74b = excluded / NOT_MEASURED / KNOWN_GAP
replacement = FAILED_TECHNICAL only
```

Confirmatory seeds, bootstrap seeds, replacement streams, cursors, exclusions,
collision-scan manifest and analyzer/environment pins must remain exact.

## 5. Frozen protocol rules

The frozen protocol is a new immutable document derived from the approved R4 candidate.

It must:

- declare status **FROZEN / PRE-DATA**;
- contain the authoritative machine block expected by `repro_v02_freeze_contract.py`;
- preserve every approved scientific parameter and decision rule;
- record HG-B approval as the owner basis;
- state that **zero confirmatory data existed at freeze**;
- state that post-freeze scientific edits require a new revision;
- contain no ambiguous alternative criteria;
- contain no literal stale declaration `NOT FROZEN` (the current validator deliberately rejects that phrase in a FROZEN protocol);
- not embed its own future Git commit SHA.

Historical candidate/change-log detail may be referenced by immutable prior commits instead of copied verbatim if copying it would introduce stale pre-freeze declarations.

## 6. F commit rule

The actual F commit must be a dedicated commit whose tree already contains the final frozen protocol/contract/seed-record bytes.

After commit:

```bash
F_HEAD=$(git rev-parse HEAD)
F_TREE=$(git rev-parse HEAD^{tree})
```

Then prove:

```text
git cat-file -t F_HEAD = commit
git rev-parse F_HEAD^{tree} = F_TREE
F_HEAD:protocol = blob
F_HEAD:contract = blob
F_HEAD:seed record = blob
```

Compute each blob SHA-1 and SHA-256 from the Git object database.

Do not amend F after publishing it.

## 7. Director FREEZE record must be AFTER F

The Director record is NOT part of F.

After F exists, create a later commit containing:

```text
docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R1.md
docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R1.json
```

Machine record semantics:

```text
record_kind = DIRECTOR_FREEZE_RECORD
issuer_class = DIRECTOR
director = DIRECTOR
decision = FREEZE

subject_head = F_HEAD
subject_tree = F_TREE

contract_sha256 = exact SHA-256 of F:contract
seed_record_sha256 = exact SHA-256 of F:seed-record
```

The record's own immutable source binding is established only after the Director-record commit exists. Do not self-declare an impossible current-commit SHA inside its own bytes.

HG-B record binding must point to an actual immutable commit/blob containing the approved owner record.

## 8. Required validation before publishing F

Run on the final pre-commit frozen bytes:

```bash
PYTHONPATH=scripts python3 -m nl5.repro_v02_freeze_contract gate   --contract <frozen-contract>   --protocol <frozen-protocol>   --record <frozen-seed-record>   --repo-root .
```

Required:

```text
gate = PASS
validation_stage = PREFREEZE_VALIDATION_PASS
freeze_status = FROZEN
dispatch = DISPATCH_BLOCKED
dispatch_ready = false
```

The word PREFREEZE_VALIDATION_PASS is the validator's internal-consistency stage name;
it does not mean the package remains unfrozen. The authoritative freeze fact comes from F + the later Director record.

Then run:

```bash
python3 -m unittest discover -s tests -t . -v
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .
```

and validate all EX-* with `harness.work_cli`.

## 9. Negative controls

Must prove at least:

- frozen contract + protocol containing literal `NOT FROZEN` => reject;
- changed N / N_min / quota / delta => reject;
- changed confirmatory seed => reject;
- changed replacement pool/cursor => reject;
- wrong seed-record digest => reject;
- wrong/missing collision manifest => reject;
- nonexistent frozen artifact path => reject;
- dirty-worktree-only frozen bytes are not accepted as immutable subject in later authority binding;
- no dispatch plan can be produced now because review/verify(F) and R2 ACTIVE do not yet exist.

## 10. State ceiling

Even after F and Director freeze record:

```text
SCIENTIFIC_RUNS = 0
R2 = WAITING_HOST / NOT_ACTIVE
AUTHOR_U1 = NOT_ASSIGNED
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED
machine_launch_authorized = false
```

## 11. Acceptance of this WO

This WO reaches `READY_FOR_REVIEW` only when:

- F_HEAD/F_TREE are real Git objects and pushed;
- frozen artifacts are exact F blobs;
- Director FREEZE record exists in a later commit and pins F;
- full validations pass;
- no science/status inflation occurred.

Then next actors are:

```text
fresh SCIENTIFIC REVIEWER(F)
fresh independent VERIFIER(F)
```

They must review/verify F, not the Director-record commit.

Do not merge to main in this implementation session.
