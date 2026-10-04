# NanoLab — Ubuntu IMPLEMENTER prompt: R4.3 frozen-package sequencing repair

Источник истины:

```text
repo = rootfabric/NanoLab
review branch = review/nl5-v02-prefreeze-hardening-r4-2-r3
review verdict = docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/REVIEWER_VERDICT_R3.md
reviewed subject = e58ac8225562995963c414e66b9b6ce6ea9ad55e
reviewed tree = 7f9f063e266d74cc7d6c6646a3022184a06bc976
verdict = FIX_REQUIRED
```

Сначала fresh fetch и проверка отсутствия активного R4.3 repair. Если уже есть — продолжать его, не открывать дубль.

Рекомендуемый branch:

```text
repair/nl5-v02-prefreeze-hardening-r4-r3
```

База: актуальный tip `repair/nl5-v02-prefreeze-hardening-r4-r2`, затем интегрировать reviewer branch `review/nl5-v02-prefreeze-hardening-r4-2-r3` через `--no-ff`. No squash, no force, no rewrite.

До substantive edits — append-only continuation/review-correction event в `EX-NL5-V02-PREFREEZE-HARDENING-R4`.

## Scope

Исправить ТОЛЬКО:

```text
M-7 = post-freeze Review/Verify must bind exact immutable frozen package
m-3 = remove “authorized plan produced” wording
```

Не менять уже PASS:

```text
M-2 replacement replay
M-3 collision proof
M-6 atomic pair ledger
m-2 snapshot safety
TOST/equivalence wording
Git object existence/byte binding
trust ceiling DISPATCH_PRECONDITIONS_RECORDED
machine_launch_authorized=false
HUMAN_PROTECTED_WRITER launch gate
```

Science parameters неизменны.

## M-7 — break the freeze/review self-reference cycle

Текущая двухкоммитная схема неверна:

```text
R = pre-freeze reviewed subject
E = FROZEN bytes + review/verify records that still point to R
```

Она доказывает review R, но не review frozen bytes E.

Новая модель должна иметь отдельный immutable frozen package commit.

### Required lifecycle

```text
S = PRE-FREEZE candidate subject
    PRE-DATA / NOT FROZEN

HG-B APPROVED

F = FROZEN PACKAGE COMMIT
    exact frozen protocol
    exact frozen contract
    exact seed record
    no self-reference to its own commit SHA

R = REVIEW RECORD COMMIT
    review PASS pins F HEAD/TREE

V = VERIFIER RECORD COMMIT
    verify VERIFIED pins F HEAD/TREE

A = AUTHORITY / READINESS EVIDENCE
    references F + immutable HG-B + Review + Verify + R2 records
```

Главное:

```text
reviewed_head == F
verified_head == F
NOT S
```

### Remove self-reference

Frozen contract/package не должен требовать хранить собственный Git commit SHA внутри самого себя.

Предпочтительно:
- exact frozen HEAD/TREE хранить во внешнем Director freeze / authority record;
- contract содержит freeze_status=FROZEN + rule/revision + package digests + generation pins;
- старые frozen_subject_head/tree либо удалить из authoritative contract schema, либо сделать non-authoritative compatibility fields.

## Authority records

Больше НЕ требовать, чтобы все records жили в одном freeze-evidence commit.

Каждый record имеет своё immutable binding:

```text
source_commit
path
git_blob_sha1
canonical_sha256
record_kind
issuer_class
```

Проверять:
- frozen package commit F exists;
- Review record source commit не предшествует F и pins F;
- Verify record source commit не предшествует F и pins F;
- authority/readiness evidence binds exact record blobs;
- если ветки review/verify независимы, допускаются разные commits/refs, но оба exact-subject = F.

## Frozen artifact binding

`frozen_subject_binding` должен связывать contract/protocol/seed-record с commit F, не с authority/evidence commit.

Проверки:

```text
git cat-file -t F == commit
git rev-parse F^{tree} == frozen_tree
F:path -> exact blob SHA
SHA-256 exact
validated input bytes == F blob bytes
```

## Required tests

1. review/verify -> S, frozen blobs -> F => REJECT
2. review -> F, verify -> S => REJECT
3. review/verify -> F, artifact binding -> other commit => REJECT
4. review source predates F => REJECT
5. verify source predates F => REJECT
6. review/verify exact F in later immutable records => PASS preconditions
7. authority binds exact review/verify blob refs => PASS
8. tampered verdict source blob/path/digest => REJECT
9. nonexistent F / wrong tree => REJECT
10. frozen bytes only in worktree, not F => REJECT

Synthetic positive fixture должен использовать реальные временные Git commits в порядке:

```text
S -> F -> Review/Verify evidence -> authority
```

No fake real-world authorization.

## Trust ceiling stays

```text
status = DISPATCH_PRECONDITIONS_RECORDED
machine_launch_authorized = false
launch_gate = HUMAN_PROTECTED_WRITER
```

Не возвращать DISPATCH_AUTHORIZED.

## m-3 wording

Исправить module/CLI documentation.

НЕ:

```text
0 = PASS / authorized plan produced
```

А:

```text
0 = validation/preconditions recorded;
    machine launch remains false;
    HUMAN_PROTECTED_WRITER required
```

Prepared execution plan != launch authorization.

## Validation

```bash
python3 -m unittest discover -s tests -t . -v
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .
# validate all EX-* same as hosted workflow
```

Никаких scientific runs.

## Handoff

```text
R4_3_HEAD =
R4_3_TREE =
M-7 =
m-3 =
TEST_COLLECTION =
HARNESS =
SCIENTIFIC_RUNS = 0
CANDIDATE = PRE-DATA / NOT FROZEN
HG-B = WAITING_OWNER
R2 = WAITING_HOST / NOT_ACTIVE
NEXT_ACTOR = fresh REVIEWER
```

Verifier не запускать до fresh Reviewer PASS.
