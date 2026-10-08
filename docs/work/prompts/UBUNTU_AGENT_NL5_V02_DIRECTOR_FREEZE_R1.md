# NanoLab Ubuntu IMPLEMENTER — create v0.2 immutable FROZEN PACKAGE F

You are the Ubuntu IMPLEMENTER for `rootfabric/NanoLab`.

Read first:

```text
AGENTS.md
DIRECTOR.md
PROJECT_CONTROL.md
HARNESS_CONTROL.md
docs/work/WO-NL5-V02-DIRECTOR-FREEZE-R1.md
docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.{md,json}
scripts/nl5/repro_v02_freeze_contract.py
tests/test_nl5_v02_prefreeze_r4.py
```

## Binding

Expected preparation branch:

```text
control/nl5-v02-director-freeze-r1
```

Expected prep base:

```text
main =
549b687a9171ea3636dbb00078d7018f619cebd3

tree =
5bfb2411d6283420e9067850807c6650725d838b
```

Fresh fetch first. If main moved, compare the delta. If anything changed the v0.2 scientific/freeze subject, STOP with SUBJECT_DRIFT. Otherwise continue the existing preparation branch; do not create a duplicate.

## Mission

Create the real immutable **FROZEN PACKAGE COMMIT F**, then create the Director FREEZE record in a strictly later commit.

No science.

## Step 1 — exact source inputs

Source contract:

```text
docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/
repro-v0-2-freeze-contract-PRE_DATA_R4.json
```

Source seed record:

```text
docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/
repro-v0-2-seed-record-PRE_DATA_R4.json
```

Source candidate:

```text
docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
```

HG-B record:

```text
docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.json
```

Verify all approved parameters against these files before editing anything.

## Step 2 — create frozen artifacts

Create:

```text
docs/research/NANOLAB_REPRO_V0_2_FROZEN_R1.md

docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/
repro-v0-2-freeze-contract-FROZEN_R1.json

docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/
repro-v0-2-seed-record-FROZEN_R1.json
```

### Seed record

Prefer an exact byte-for-byte copy of the R4 seed record.

Prove:

```bash
cmp -s SOURCE_SEED FROZEN_SEED
sha256sum SOURCE_SEED FROZEN_SEED
```

If bytes differ, STOP unless the repository validator explicitly requires a metadata-only change. No seed identity, cursor, pool, skip, bootstrap value or digest may drift.

### Contract

Copy the PRE-DATA R4 contract and change only the scientific-subject binding needed for the frozen package:

```text
candidate_doc_path =
docs/research/NANOLAB_REPRO_V0_2_FROZEN_R1.md

candidate_revision =
R4

seed_record_path =
docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/
repro-v0-2-seed-record-FROZEN_R1.json

seed_record_file_sha256 =
actual SHA-256 of the frozen seed file

freeze_status =
FROZEN

frozen_subject_head =
null

frozen_subject_tree =
null
```

All other scientific/statistical values must be structurally identical to the source R4 contract.

Write a small comparison script if useful and fail on any unexpected delta.

### Protocol

Create a clean frozen protocol document from the approved R4 basis.

Requirements:

```text
status = FROZEN / PRE-DATA
rule_id = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL
candidate revision = R4
HG-B = APPROVED
zero confirmatory data at freeze
post-freeze edits require new revision
```

It must contain all scientific decision-rule details and the exact machine block required by the validator.

IMPORTANT: the validator rejects a FROZEN protocol if the literal phrase:

```text
NOT FROZEN
```

appears anywhere in the file, even in historical commentary.

Therefore do not copy stale historical status prose verbatim. Reference the candidate/history by commit/path instead.

Do not embed F_HEAD in the frozen protocol.

## Step 3 — validate frozen bytes before commit

Run:

```bash
PYTHONPATH=scripts python3 -m nl5.repro_v02_freeze_contract gate \
  --contract docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/repro-v0-2-freeze-contract-FROZEN_R1.json \
  --protocol docs/research/NANOLAB_REPRO_V0_2_FROZEN_R1.md \
  --record docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/repro-v0-2-seed-record-FROZEN_R1.json \
  --repo-root .
```

Require:

```text
gate = PASS
freeze_status = FROZEN
dispatch = DISPATCH_BLOCKED
dispatch_ready = false
```

Also run all tests/harness/work_cli.

Do not continue on any failure.

## Step 4 — create F

Commit the finalized frozen artifacts and any execution bookkeeping that does not depend on F's SHA.

Suggested message:

```text
freeze(nl5): create immutable v0.2 FROZEN PACKAGE F
```

Immediately record:

```bash
F_HEAD=$(git rev-parse HEAD)
F_TREE=$(git rev-parse HEAD^{tree})

git cat-file -t "$F_HEAD"
git rev-parse "$F_HEAD^{tree}"

git rev-parse "$F_HEAD:docs/research/NANOLAB_REPRO_V0_2_FROZEN_R1.md"
git rev-parse "$F_HEAD:docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/repro-v0-2-freeze-contract-FROZEN_R1.json"
git rev-parse "$F_HEAD:docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/repro-v0-2-seed-record-FROZEN_R1.json"
```

Read bytes for SHA-256 from the Git object database, not the mutable worktree:

```bash
git cat-file blob "$F_HEAD:<path>" | sha256sum
```

Push non-force.

After this point, never amend/rewrite F.

## Step 5 — Director FREEZE record in later commit

Create:

```text
docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R1.md
docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R1.json
```

It must state:

```text
record_kind = DIRECTOR_FREEZE_RECORD
issuer_class = DIRECTOR
director = DIRECTOR
decision = FREEZE
subject_head = F_HEAD
subject_tree = F_TREE
contract_sha256 = exact Git-object SHA-256 of F:contract
seed_record_sha256 = exact Git-object SHA-256 of F:seed-record
protocol_sha256 = exact Git-object SHA-256 of F:protocol
HG-B = APPROVED
SCIENTIFIC_RUNS_AT_FREEZE = 0
```

Also record all three F blob SHA-1 values and paths.

The Director record itself is committed only AFTER F.

Suggested message:

```text
control(nl5): record Director FREEZE decision for v0.2 package F
```

After that commit exists, record its own commit/blob identity in a separate machine-binding evidence file or later authority-builder input. Do not self-reference the same commit from inside its own bytes.

The freeze-record source commit must be a strict descendant of F.

## Step 6 — update execution bookkeeping

Append valid events, never rewrite old ones:

```text
0002 = FROZEN PACKAGE F created
0003 = Director FREEZE record created / handoff
```

Use schema-supported event types. If no specific FREEZE event exists, use valid CONTINUATION_CHECKPOINT entries with explicit machine-readable summary.

Update summary and WORK_QUEUE:

```text
HG-B = APPROVED
F = CREATED
Director FREEZE = RECORDED
SCIENCE = 0
NEXT = fresh Reviewer(F) + fresh Verifier(F)
parallel = R2 activation
```

Passport may finish in the existing schema-supported handoff state, normally HANDOFF_READY.

## Step 7 — final validation

Run again after Director record commit:

```bash
python3 -m unittest discover -s tests -t . -v
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .
```

Validate all EX-*.

Re-run the frozen package gate from the final worktree and prove it still validates.

Do NOT try to build a real dispatch plan yet. It must remain blocked because:

```text
fresh Reviewer(F) = missing
fresh Verifier(F) = missing
R2 ACTIVE = false
AUTHOR_U1 = NOT_ASSIGNED
```

## Final handoff

Return:

```text
NANOLAB V0.2 DIRECTOR FREEZE HANDOFF

VERDICT =
FROZEN_PACKAGE_CREATED_READY_FOR_REVIEW

BASE_MAIN =
BRANCH =

F_HEAD =
F_TREE =

F_PROTOCOL_PATH =
F_PROTOCOL_BLOB_SHA1 =
F_PROTOCOL_SHA256 =

F_CONTRACT_PATH =
F_CONTRACT_BLOB_SHA1 =
F_CONTRACT_SHA256 =

F_SEED_RECORD_PATH =
F_SEED_RECORD_BLOB_SHA1 =
F_SEED_RECORD_SHA256 =

SEED_RECORD_BYTE_IDENTICAL_TO_R4 =
YES/NO

DIRECTOR_FREEZE_RECORD_COMMIT =
DIRECTOR_FREEZE_RECORD_PATH_MD =
DIRECTOR_FREEZE_RECORD_PATH_JSON =
DIRECTOR_FREEZE_RECORD_BLOB_SHA1 =
DIRECTOR_FREEZE_RECORD_SHA256 =

HG-B =
APPROVED

FROZEN_GATE =
PASS

DISPATCH =
BLOCKED

SCIENTIFIC_RUNS =
0

AUTHOR_U1 =
NOT_ASSIGNED

R2 =
WAITING_HOST / NOT_ACTIVE

NL5 =
IN_PROGRESS

external_reproductions =
0

NL6-001 =
LOCKED

TEST_COLLECTION =
CHECK_CONSISTENCY =
WORKFLOW_LINT =
WORK_CLI_ALL_EX =

NEXT_ACTOR =
fresh SCIENTIFIC REVIEWER(F)

NEXT_AFTER_REVIEW =
fresh independent VERIFIER(F)

DO NOT START SCIENCE
```

Do not merge main in this session.
