# NanoLab — Fresh Verifier prompt for NL5 v0.2 R4.3

Роль: **fresh independent VERIFIER**. Не использовать implementer/reviewer verdict как доказательство; каждый verification fact получить заново на exact subject.

## Binding

```text
repo = rootfabric/NanoLab
subject branch = repair/nl5-v02-prefreeze-hardening-r4-r3
SUBJECT_HEAD = 39cc9809ad4b9ad61b2effd6dbcb8c9067848da0
SUBJECT_TREE = 10ba8bbffcae06ae7fad7135b2493494b0d4f9b1
review branch = review/nl5-v02-prefreeze-hardening-r4-3-r4
review verdict = PASS
review file = docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/REVIEWER_VERDICT_R4.md
```

Сначала fresh fetch. Проверить, что exact SHA/tree совпадают. Если subject изменился — STOP и вернуть SUBJECT_DRIFT; не переносить PASS на новый HEAD.

## Mandatory verification

### 1. Full real test surface

На чистом worktree exact HEAD:

```bash
python3 -m unittest discover -s tests -t . -v
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .
```

И loop всех EX-* точно как hosted workflow.

Не требовать исторически ровно 593: сообщить фактическое число.

### 2. Reproduce original audit / repair classes

Независимо проверить:

```text
F1 malformed/partial seed contract fails closed
F2 Git scan errors != CLEAN; pinned tree beats dirty worktree
F3 replacement pool starts after consumed cursor; no confirmatory reuse
F4 integer policy: N_min 52/8, quota 12/12/2/2, cap 56, max 352
```

### 3. R4.1 authority / integrity controls

Проверить:
- PRE-DATA / NOT_FROZEN package passes only PREFREEZE validation;
- PRE-DATA package cannot yield launch authorization;
- replacement pools bit-exact replay;
- fake replacement seed rejected;
- fake collision skip rejected;
- manifest/path/digest tampering rejected;
- pair ledger one-shot semantics.

### 4. R4.2 controls

Проверить M-6 transactional state directly:
- duplicate replacement pair id;
- duplicate/invalid author attempt;
- duplicate/invalid external attempt;
- replacement seed already owned;
- forced second-leg binding failure.

После каждого reject compare complete `state_snapshot()`: state must be identical.

Проверить public snapshot isolation.

### 5. R4.3 M-7 sequencing

Это главный exact verifier gate.

На real temporary Git repo mechanically reproduce lifecycle:

```text
S = pre-freeze candidate
H = HG-B/R2 pre-freeze records
F = immutable FROZEN PACKAGE COMMIT
R = review record pinning F
V = verify record pinning F
A = readiness/authority
```

Positive:

```text
subject_head = F
subject_tree = tree(F)
frozen artifacts are exact blobs of F
reviewed_head/tree = F/tree(F)
verified_head/tree = F/tree(F)
review/verify/freeze source commits strictly descend from F
records have exact immutable blob refs
status = DISPATCH_PRECONDITIONS_RECORDED
machine_launch_authorized = false
launch_gate = HUMAN_PROTECTED_WRITER
```

Negative controls required:

```text
schema v1 -> reject
schema v2 -> reject
review/verify -> S while artifacts -> F -> reject
review -> F, verify -> S -> reject
artifact binding -> another commit -> reject
review source before/unrelated to F -> reject
verify source before/unrelated to F -> reject
freeze source inside/before F -> reject
tampered review/verify path/blob/digest -> reject
nonexistent F -> reject
wrong tree(F) -> reject
worktree-only frozen bytes -> reject
legacy R4.2 two-commit shortcut -> reject
```

### 6. Trust ceiling

Search and execute enough controls to prove no production path returns:

```text
DISPATCH_AUTHORIZED
machine_launch_authorized = true
```

Expected ceiling:

```text
DISPATCH_PRECONDITIONS_RECORDED
machine_launch_authorized = false
HUMAN_PROTECTED_WRITER
```

String occurrences in historical reviewer docs/tests may exist as negative assertions; distinguish them from executable success paths.

### 7. Scientific/status boundaries

Verify exact subject still has:

```text
SCIENTIFIC_RUNS = 0
CANDIDATE = PRE-DATA / NOT FROZEN
HG-B = WAITING_OWNER
AUTHOR_U1 = NOT_ASSIGNED
R2 = WAITING_HOST / NOT_ACTIVE
external_reproductions = 0
NL5 = IN_PROGRESS
NL6-001 = LOCKED
```

No Windows/WSL new science. outenemy remains EXTERNAL_U2_ONLY.

### 8. Hosted CI

Do not fabricate hosted CI. If no TR-PR exists:

```text
HOSTED_CI = NOT_RUN
```

Verifier may finish VERIFIED before hosted CI if repository process defines hosted CI as next integration gate; record this explicitly. Draft PR/hosted CI happens only after VERIFIED.

## Output / Git evidence

Create independent verifier branch from exact SUBJECT_HEAD, recommended:

```text
verify/nl5-v02-prefreeze-hardening-r4-3-r1
```

Do not modify product subject.

Write verifier evidence under:

```text
docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/
```

Pin:

```text
VERIFIED_HEAD
VERIFIED_TREE
test command + actual count/result
harness results
targeted negative-control results
M-7 positive/negative sequencing results
status-boundary checks
HOSTED_CI status
```

Verdict only:

```text
VERIFIED
NOT_VERIFIED
```

No soft PASS.

If VERIFIED:

```text
NEXT_ACTOR = DIRECTOR / integration preparation
NEXT_ACTION = draft PR on exact reviewed+verified product subject, run TR-PR hosted CI, then Director readiness/Human Gate
```

If any blocker:

```text
NEXT_ACTOR = IMPLEMENTER
NEXT_ACTION = exact minimal repair
```

Do not merge main. Do not freeze protocol. Do not run scientific campaign.
