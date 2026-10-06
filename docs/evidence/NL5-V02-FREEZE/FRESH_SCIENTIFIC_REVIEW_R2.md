# NL5 v0.2 FROZEN_R2 — Fresh Scientific Reviewer R1

```text
REVIEW_ID =
NL5-V02-FROZEN-R2/SCIENTIFIC_REVIEW_R1

VERDICT =
PASS

REVIEWED_HEAD =
60da9a846511265a8ac7564da088c3d74cb073f0

REVIEWED_TREE =
e565c8a6cee9e829fac14008ebc9c2ea1609931d

PROTOCOL_BLOB =
4835719622bae49a8e8b480536a482b4b222d408

CONTRACT_BLOB =
d6a9ccde4d1dadf42d1a8cd9b88faa02646cf70b

SEED_RECORD_BLOB =
0164e0e3f5dda6dbf63174df3730b1bd921d2c76

SCIENTIFIC_RUNS =
0
```

## 1. Scope

Fresh scientific/protocol review of the exact immutable FROZEN_R2 package commit only.

The reviewed subject is F2 itself. Later Director FREEZE R2 and handoff commits are control evidence and are not substituted for the frozen scientific subject.

## 2. Previous blocker M-1

### Verdict: PASS

FROZEN_R1 failed review because protocol prose changed the collision-scan exact allowlist from the approved R4 pinned-tree paths to later frozen-package paths while the authoritative contract retained the correct approved allowlist.

FROZEN_R2 now states, in exactly one machine-readable `scan-allowlist-v1` block:

```text
path_1 = docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
path_2 = docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/repro-v0-2-seed-record-PRE_DATA_R4.json
```

This ordered exact list equals:

`contract.seed_generation.scan_allowlist_paths_exact`.

The protocol also explicitly explains the semantics: the collision proof scans pinned historical tree `a9d7d07fa264e9907b67ca244b00ba2da3430b0f`; later FROZEN_R2 artifact paths are not substitutes for allowlist entries in that historical tree.

## 3. Fail-closed regression

PASS.

The validator now requires exactly one FROZEN-only `scan-allowlist-v1` block and compares it ordered-exact against the contract.

Reviewed regression classes include:

```text
correct frozen allowlist                          -> PASS possible
FROZEN_R1-style frozen-package paths              -> FREEZE_GATE_FAIL
raw historical FROZEN_R1 protocol                 -> FREEZE_GATE_FAIL
missing block                                     -> FREEZE_GATE_FAIL
duplicate block                                   -> FREEZE_GATE_FAIL
extra exact path                                  -> FREEZE_GATE_FAIL
order drift                                       -> FREEZE_GATE_FAIL
malformed declaration                             -> FREEZE_GATE_FAIL
non-consecutive path indices                      -> FREEZE_GATE_FAIL
PRE-DATA R4 without frozen-only block              -> remains PASS
frozen-only block injected into PRE-DATA package   -> FREEZE_GATE_FAIL
CLI wrong frozen allowlist                         -> exit 3
```

The committed M-1 negative-control evidence records the original defect class as mechanically rejected.

## 4. Scientific delta

PASS.

The frozen contract delta against the approved R4 PRE-DATA contract remains exactly:

```text
scientific_subject.candidate_doc_path
scientific_subject.freeze_status
scientific_subject.seed_record_path
```

```text
unchanged leaves = 307 / 310
unexpected scientific delta = NONE
```

No approved scientific/statistical parameter changed.

## 5. Seed identity

PASS.

The FROZEN_R2 seed record is the exact same Git blob as FROZEN_R1 and has the same SHA-256 as the approved R4 PRE-DATA record:

```text
blob =
0164e0e3f5dda6dbf63174df3730b1bd921d2c76

sha256 =
8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28
```

Confirmatory seeds, bootstrap seeds, replacement pools, skips, cursors, exclusions and integrity digests are unchanged.

## 6. Scientific design

PASS.

Preserved:

```text
rule = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL
candidate basis = R4
N = 64 / 64 / 10 / 10
N_min = 52 / 52 / 8 / 8
replacement quotas = 12 / 12 / 2 / 2 pairs
confirmatory = 296
replacement cap = 56
max_runs = 352
delta = 0.5
paired design
standard TOST-equivalence interpretation
bootstrap = 10,000 paired resamples
replacement only FAILED_TECHNICAL
74b excluded
```

Decision-rule semantics remain conservative and predeclared. Technical failure remains separate from scientific mismatch.

## 7. Freeze / provenance sequencing

PASS.

```text
F2_HEAD =
60da9a846511265a8ac7564da088c3d74cb073f0

F2_TREE =
e565c8a6cee9e829fac14008ebc9c2ea1609931d
```

F2 is a real immutable Git commit.

Director FREEZE R2 is recorded later at:

```text
a2f7304ebbb5973b81cf49dee60c21c85c6a974d
```

and pins F2 HEAD/TREE plus the exact protocol/contract/seed Git blob and SHA-256 identities.

FROZEN_R1 / Director R1 remain preserved as immutable historical evidence and are not rewritten.

## 8. Gate / state ceiling

Frozen gate evidence:

```text
gate = PASS
validation_stage = PREFREEZE_VALIDATION_PASS
freeze_status = FROZEN
dispatch = DISPATCH_BLOCKED
dispatch_ready = false
```

State remains:

```text
SCIENTIFIC_RUNS = 0
AUTHOR_U1 = NOT_ASSIGNED
R2 = WAITING_HOST / NOT_ACTIVE
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED
machine_launch_authorized = false
```

No science was started.

## 9. Execution evidence

The implementer reports on the final repair line:

```text
605 tests OK
check-consistency = PASS
workflow_lint = PASS
work_cli = 51/51 EX-* PASS
```

This Scientific Reviewer independently inspected the exact remote Git subject, frozen bytes, repair logic and committed negative controls. It does not claim an independent full-suite execution rerun.

## 10. Conclusion

```text
M-1 collision allowlist binding = PASS
scientific parameter fidelity   = PASS
seed identity fidelity          = PASS
decision rule                   = PASS
freeze sequencing               = PASS
state ceiling                   = PASS

SCIENTIFIC_REVIEW_VERDICT = PASS
```

The frozen scientific subject remains exactly:

```text
60da9a846511265a8ac7564da088c3d74cb073f0
e565c8a6cee9e829fac14008ebc9c2ea1609931d
```

Next actor:

```text
fresh independent VERIFIER(F2)
```

The verifier must independently reproduce the frozen package gate, M-1 positive/negative controls, Git-object bindings and full validation surface on exact F2.

Do not start science.
