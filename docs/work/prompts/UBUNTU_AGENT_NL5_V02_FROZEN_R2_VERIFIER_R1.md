# NanoLab — Fresh independent Verifier for FROZEN_R2 (F2)

Role: **fresh independent VERIFIER**.

Do not trust implementer or reviewer conclusions. Reproduce every verification fact independently on the exact immutable F2 subject.

## Binding

```text
repo = rootfabric/NanoLab

F2_HEAD =
60da9a846511265a8ac7564da088c3d74cb073f0

F2_TREE =
e565c8a6cee9e829fac14008ebc9c2ea1609931d

F2_PROTOCOL =
docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md

F2_CONTRACT =
docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/
repro-v0-2-freeze-contract-FROZEN_R2.json

F2_SEED_RECORD =
docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/
repro-v0-2-seed-record-FROZEN_R2.json

DIRECTOR_FREEZE_R2_COMMIT =
a2f7304ebbb5973b81cf49dee60c21c85c6a974d

SCIENTIFIC_REVIEW =
PASS

REVIEW_BRANCH =
review/nl5-v02-frozen-r2-scientific-review-r1
```

Fresh fetch first. If F2 object/tree does not match exactly, STOP with SUBJECT_DRIFT.

The verifier branch must be based from exact F2, not from Director/handoff/reviewer tips.

Recommended:

```text
verify/nl5-v02-frozen-r2-r1
```

## 1. Immutable Git identity

Independently prove:

```bash
git cat-file -t 60da9a846511265a8ac7564da088c3d74cb073f0
git rev-parse 60da9a846511265a8ac7564da088c3d74cb073f0^{tree}
```

Expected tree:

```text
e565c8a6cee9e829fac14008ebc9c2ea1609931d
```

Resolve all F2 artifact blobs from the Git object database and recompute SHA-256 from Git blob bytes.

Expected:

```text
protocol blob =
4835719622bae49a8e8b480536a482b4b222d408

protocol sha256 =
2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d

contract blob =
d6a9ccde4d1dadf42d1a8cd9b88faa02646cf70b

contract sha256 =
7e6476544e82af73d5d7e0672666ece99bf4d499a0da30645b02886bcdc45b3a

seed blob =
0164e0e3f5dda6dbf63174df3730b1bd921d2c76

seed sha256 =
8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28
```

## 2. Director sequencing

Verify Director FREEZE R2 is a strict descendant of F2:

```text
a2f7304ebbb5973b81cf49dee60c21c85c6a974d
```

and its JSON pins exact F2 HEAD/TREE and exact artifact blobs/digests.

Verify FROZEN_R1 / Director R1 history is unchanged and preserved as historical FIX_REQUIRED attempt.

## 3. Scientific delta

Independently compare F2 contract against approved PRE_DATA_R4 source contract.

Expected changed leaf paths only:

```text
scientific_subject.candidate_doc_path
scientific_subject.freeze_status
scientific_subject.seed_record_path
```

Expected:

```text
307 / 310 leaves unchanged
unexpected scientific delta = NONE
```

Verify all approved values remain exact:

```text
N = 64 / 64 / 10 / 10
N_min = 52 / 52 / 8 / 8
replacement quotas = 12 / 12 / 2 / 2 pairs
confirmatory runs = 296
replacement cap = 56
max_runs = 352
wall = 560 h/platform
delta = 0.5
paired TOST
bootstrap = 10000
74b excluded
replacement only FAILED_TECHNICAL
```

## 4. Seed identity

Prove F2 seed record is byte-identical to:

```text
approved R4 PRE_DATA seed record
FROZEN_R1 seed record
```

Use `cmp`, blob identity and SHA-256.

Verify seeds, replacement pools, skips, cursors, exclusions, bootstrap values and record digests.

## 5. M-1 allowlist binding — principal verification gate

Contract exact allowlist must be:

```text
1. docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
2. docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/repro-v0-2-seed-record-PRE_DATA_R4.json
```

Pinned scan tree:

```text
a9d7d07fa264e9907b67ca244b00ba2da3430b0f
```

Independently parse F2 protocol and prove it has exactly one `scan-allowlist-v1` block, whose ordered exact paths equal the contract.

Reproduce negative controls:

```text
FROZEN_R1-style frozen package paths -> FREEZE_GATE_FAIL
raw FROZEN_R1 protocol               -> FREEZE_GATE_FAIL
missing block                        -> FREEZE_GATE_FAIL
duplicate block                      -> FREEZE_GATE_FAIL
extra exact path                     -> FREEZE_GATE_FAIL
order drift                          -> FREEZE_GATE_FAIL
malformed line                       -> FREEZE_GATE_FAIL
non-consecutive path_N               -> FREEZE_GATE_FAIL
frozen-only block in PRE-DATA R4     -> FREEZE_GATE_FAIL
CLI wrong frozen allowlist           -> exit 3
```

And positive controls:

```text
F2 exact block == contract -> PASS possible
historical PRE_DATA R4 without frozen-only block -> PASS
```

## 6. Frozen gate

Run the real authoritative gate with pinned collision-scan rerun:

```bash
PYTHONPATH=scripts python3 -m nl5.repro_v02_freeze_contract gate \
  --contract docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-freeze-contract-FROZEN_R2.json \
  --protocol docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md \
  --record docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-seed-record-FROZEN_R2.json \
  --repo-root .
```

Required:

```text
gate = PASS
validation_stage = PREFREEZE_VALIDATION_PASS
freeze_status = FROZEN
dispatch = DISPATCH_BLOCKED
dispatch_ready = false
```

Do not misinterpret `PREFREEZE_VALIDATION_PASS`: the authoritative freeze fact is F2 + Director FREEZE R2.

## 7. Full repository validation

Run:

```bash
python3 -m unittest discover -s tests -t . -v
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .
```

Validate every `EX-*` using the same loop as hosted CI.

Report actual counts; do not hardcode historical 605/51 if repository state differs.

## 8. Authority / dispatch ceiling

Do not fabricate R2 or launch authorization.

Prove current blockers still include:

```text
fresh Verifier(F2) not yet recorded before this verdict
R2 ACTIVE = false
AUTHOR_U1 = NOT_ASSIGNED
```

Expected scientific/status ceiling:

```text
SCIENTIFIC_RUNS = 0
R2 = WAITING_HOST / NOT_ACTIVE
AUTHOR_U1 = NOT_ASSIGNED
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED
machine_launch_authorized = false
launch_gate = HUMAN_PROTECTED_WRITER
```

## 9. Output evidence

Write independent verifier evidence under:

```text
docs/evidence/NL5-V02-FREEZE/
```

Suggested:

```text
FRESH_VERIFIER_R2.md
FRESH_VERIFIER_R2.json
verify_frozen_r2/
```

The machine-readable record must include:

```text
record_kind = VERIFIER_VERDICT
issuer_class = INDEPENDENT_VERIFIER
verdict = VERIFIED or NOT_VERIFIED
verified_head = F2_HEAD
verified_tree = F2_TREE
```

Do not put impossible self-source binding into the same record commit; later authority evidence can bind the record to its source commit/path/blob/digest.

Verdict only:

```text
VERIFIED
NOT_VERIFIED
```

No soft PASS.

If VERIFIED:

```text
NEXT_ACTOR = DIRECTOR / integration preparation
NEXT_ACTION = integrate F2 tooling + FROZEN_R2 + D2 evidence through PR/hosted CI, preserving exact F2 review/verify bindings; in parallel continue R2 native Ubuntu activation
```

Do not start science. Do not activate R2. Do not accept NL5. Do not unlock NL6.
