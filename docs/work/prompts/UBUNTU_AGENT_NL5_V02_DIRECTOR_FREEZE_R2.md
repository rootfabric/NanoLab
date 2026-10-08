# NanoLab Ubuntu IMPLEMENTER — FROZEN_R2 repair after Scientific Review M-1

Repository: `rootfabric/NanoLab`.

## Exact prior subjects

```text
canonical main =
549b687a9171ea3636dbb00078d7018f619cebd3

FROZEN_R1 =
cb91ade761f6802fc40c500761d3e35022408822

FROZEN_R1_TREE =
ad21ce39b42681f581da996b2805a5b2fb49111f

Director Freeze R1 commit =
4236e0c7cfb19de2687a8f0d3be3641cc1b000d4

R1 handoff branch tip =
control/nl5-v02-director-freeze-r1
49bda9bad9110c4598d10aa20a28cf5b062acf13

scientific review branch =
review/nl5-v02-frozen-r1-scientific-review-r1

review verdict =
FIX_REQUIRED
```

Read fully:

```text
docs/evidence/NL5-V02-FREEZE/FRESH_SCIENTIFIC_REVIEW_R1.md
docs/work/WO-NL5-V02-DIRECTOR-FREEZE-R2.md
docs/work/WO-NL5-V02-DIRECTOR-FREEZE-R1.md
scripts/nl5/repro_v02_freeze_contract.py
tests/test_nl5_v02_prefreeze_r4.py
```

## Git setup

Fresh fetch. Check whether an active R2 repair already exists. If yes, continue
it; do not duplicate.

Recommended branch:

```text
repair/nl5-v02-director-freeze-r2
```

Base it from current tip of `control/nl5-v02-director-freeze-r1`, then merge
the reviewer branch with `--no-ff`.

No force, no squash, no history rewrite.

FROZEN_R1 and Director Freeze R1 must remain byte-identical forever.

Create a new execution:

```text
EX-NL5-V02-DIRECTOR-FREEZE-R2
```

and append START before substantive repair edits.

## M-1 exact defect

Approved R4 / authoritative contract:

```text
scan_allowlist_paths_exact =
1. docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
2. docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/
   repro-v0-2-seed-record-PRE_DATA_R4.json
```

FROZEN_R1 protocol incorrectly states its exact allowlist as the later frozen
protocol + frozen seed-record paths.

Do NOT change the contract allowlist to match the bad frozen prose.

The contract is correct because the scan is against pinned tree:

```text
a9d7d07fa264e9907b67ca244b00ba2da3430b0f
```

and the approved candidate/PRE_DATA paths are the intentional allowlisted
locations in that tree.

## Phase A — fail-closed validator repair BEFORE F2

Implement a narrow FROZEN-only machine check that binds the frozen protocol's
declared scan allowlist to:

```python
contract["seed_generation"]["scan_allowlist_paths_exact"]
```

Do not force historical PRE-DATA R4 protocol to adopt a new frozen-only syntax.

A good implementation is a dedicated marked block in FROZEN protocols, e.g.:

```text
# scan-allowlist-v1
path_1 = docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
path_2 = docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/repro-v0-2-seed-record-PRE_DATA_R4.json
```

The exact syntax is implementation choice, but it must be deterministic,
single-instance and fail closed.

Regression tests must prove:

```text
correct FROZEN allowlist -> PASS possible
FROZEN_R1-style frozen-package paths -> FREEZE_GATE_FAIL
missing block -> FREEZE_GATE_FAIL
duplicate block -> FREEZE_GATE_FAIL
extra/malformed/drifted exact path -> FREEZE_GATE_FAIL
PRE-DATA R4 historical package -> still PASS
```

Commit and push this tooling/test repair before creating F2.

No scientific parameters may change.

## Phase B — create FROZEN_R2 package

Create:

```text
docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md

docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/
repro-v0-2-freeze-contract-FROZEN_R2.json

docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/
repro-v0-2-seed-record-FROZEN_R2.json
```

### Seed record

Must be byte-identical to R4 and FROZEN_R1.

Prove with `cmp` + SHA-256.

### Contract

Derive again from:

```text
docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/
repro-v0-2-freeze-contract-PRE_DATA_R4.json
```

Expected changed leaf paths remain only:

```text
scientific_subject.candidate_doc_path
scientific_subject.freeze_status
scientific_subject.seed_record_path
```

The contract's `scan_allowlist_paths_exact` remains exactly the approved R4
candidate/PRE_DATA paths.

### Protocol

FROZEN_R2 must be scientifically identical to approved R4/FROZEN_R1 except
for the correction of the scan-allowlist declaration and revision/provenance
metadata.

It must explicitly state that:

```text
scan tree = a9d7d07fa264e9907b67ca244b00ba2da3430b0f

allowlist is defined in that pinned tree, therefore:
candidate R1 path + PRE_DATA_R4 seed-record path

FROZEN_R2 package paths are later objects and are NOT allowlist entries for
that historical scan
```

Include the new machine-readable FROZEN-only allowlist declaration consumed by
the repaired validator.

Do not include the stale literal phrase that the FROZEN validator rejects.

## Phase C — validate BEFORE creating F2

Run the full frozen gate with scan rerun.

Required:

```text
gate = PASS
freeze_status = FROZEN
dispatch = DISPATCH_BLOCKED
dispatch_ready = false
```

Also execute the M-1 negative test against a temporary copy changed back to
FROZEN_R1-style frozen artifact paths and require:

```text
FREEZE_GATE_FAIL
exit 3
```

Run full unittest / consistency / workflow lint / all EX-*.

## Phase D — immutable F2 commit

Commit the finalized FROZEN_R2 artifacts in a dedicated commit after the
tooling repair commit.

Record:

```text
F2_HEAD =
F2_TREE =
```

and all 3 artifact blob SHA-1/SHA-256 values from the Git object database.

Push non-force. Never amend F2 after publication.

## Phase E — Director FREEZE R2 in later commit

Create:

```text
docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R2.md
docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R2.json
```

Pin F2, not F1.

Record FROZEN_R1 / Director R1 as:

```text
historical immutable attempt
scientific review = FIX_REQUIRED
superseded for dispatch by FROZEN_R2 after successful review
```

Do not delete or rewrite them.

Director R2 record source commit must strictly descend from F2.

## Final gates and handoff

Full tests/harness/work_cli again.

No science.

Return:

```text
NANOLAB V0.2 FROZEN_R2 REPAIR HANDOFF

VERDICT =
FROZEN_R2_CREATED_READY_FOR_REVIEW

BASE_HANDOFF =
REPAIR_BRANCH =
TOOLING_REPAIR_HEAD =

F1_HEAD =
cb91ade761f6802fc40c500761d3e35022408822
F1_UNCHANGED =
YES

M-1 =
FIXED

ALLOWLIST_CONTRACT =
<exact two paths>

ALLOWLIST_PROTOCOL =
<exact two paths>

ALLOWLIST_REGRESSION =
PASS

F2_HEAD =
F2_TREE =

F2_PROTOCOL_BLOB_SHA1 =
F2_PROTOCOL_SHA256 =
F2_CONTRACT_BLOB_SHA1 =
F2_CONTRACT_SHA256 =
F2_SEED_BLOB_SHA1 =
F2_SEED_SHA256 =

SEED_BYTE_IDENTICAL_R4_F1 =
YES

CONTRACT_UNEXPECTED_SCIENTIFIC_DELTA =
NONE

DIRECTOR_FREEZE_R2_COMMIT =
DIRECTOR_FREEZE_R2_JSON_SHA256 =

FROZEN_GATE =
PASS

NEGATIVE_WRONG_ALLOWLIST =
FREEZE_GATE_FAIL / exit 3

SCIENTIFIC_RUNS =
0

R2 =
WAITING_HOST / NOT_ACTIVE

AUTHOR_U1 =
NOT_ASSIGNED

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
fresh SCIENTIFIC REVIEWER(F2)

DO NOT START SCIENCE
```

Do not merge main.
