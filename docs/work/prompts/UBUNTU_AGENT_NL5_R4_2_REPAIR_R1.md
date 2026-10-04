# NanoLab — Ubuntu IMPLEMENTER prompt: R4.2 narrow repair

Источник истины:

```text
repo = rootfabric/NanoLab
review branch = review/nl5-v02-prefreeze-hardening-r4-1-r2
review verdict = docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/REVIEWER_VERDICT_R2.md
reviewed subject = 7406b5a1755b7c025f6e10010be48a7fd231c9be
reviewed tree = 8c6a9ba988fa3c539a2cecbba816a92d905e0495
verdict = FIX_REQUIRED
```

Сначала fresh fetch и проверка, что R4.2 уже не выполняется. Если active repair существует — продолжать его, не создавать дубль.

Рекомендуемый branch:

```text
repair/nl5-v02-prefreeze-hardening-r4-r2
```

База: актуальный tip `repair/nl5-v02-prefreeze-hardening-r4-r1`, затем интегрировать reviewer branch `review/nl5-v02-prefreeze-hardening-r4-1-r2` через `--no-ff`. No squash, no force, no rewrite.

До substantive edits — append-only continuation/review-correction event в `EX-NL5-V02-PREFREEZE-HARDENING-R4`.

## Scope

Исправить ТОЛЬКО:

```text
M-5 = real Git/provenance binding for dispatch authority
M-6 = atomic pair replacement mutation
m-2 = open_pair snapshot must not expose internal legs
```

Не менять уже принятые:

```text
M-2 replacement replay = PASS
M-3 collision proof = PASS
TOST/equivalence wording = PASS
N = 64/64/10/10
N_min = 52/52/8/8
replacement quotas = 12/12/2/2
replacement cap = 56
max_runs = 352
delta = 0.5
paired design
R3 confirmatory identities
PRE-DATA / NOT FROZEN
R2 WAITING_HOST / NOT_ACTIVE
scientific runs = 0
```

## M-5 — immutable Git / authority provenance

Текущий `validate_dispatch_authority()` не должен принимать 40-hex строки как доказательство существования frozen subject.

Production path должен механически проверить:

1. `subject_head` существует как Git commit.
2. `git rev-parse <subject_head>^{tree}` ровно равен `subject_tree`.
3. frozen protocol/contract/seed-record привязаны к exact Git blobs этого subject или к явно разрешённым immutable artifact refs.
4. Каждый authority record содержит immutable source binding, минимум:
   ```text
   source_commit
   path
   git_blob_sha1
   canonical_sha256
   kind/schema
   ```
5. Байты читать из Git object (`git show <commit>:<path>` / cat-file), а не доверять mutable worktree.
6. HG-B/review/verify/R2 records должны иметь явный provenance/issuer class. Если инфраструктура пока не умеет доказать owner/independent identity, machine conclusion НЕ называть `DISPATCH_AUTHORIZED`; максимум `DISPATCH_PRECONDITIONS_RECORDED`, а реальный launch остаётся за Human/Protected-Writer gate.
7. Fixture path должен оставаться test-only и не превращаться в production одним `fixture=false`.

Negative tests:

```text
nonexistent 40-hex head -> reject
existing head + wrong tree -> reject
record only in dirty worktree -> reject
source_commit/path/blob mismatch -> reject
fake non-fixture local APPROVED/PASS/VERIFIED/ACTIVE JSON -> reject
contract/protocol/record blob not in frozen subject -> reject
```

Positive fixture может использовать временный synthetic Git repo с НАСТОЯЩИМИ commits/trees/blobs.

## M-6 — transactional ReplacementLedger

Сейчас `request_replacement()` может мутировать quota/cursor/source pair ДО того, как `open_pair` или `_bind_attempt` завершатся.

Сделать двухфазно:

```text
PHASE 1 VALIDATE (no mutation):
  source pair
  variant
  quota/pool
  replacement_pair_id free
  replacement seed not owned
  author attempt id valid + unused
  external attempt id valid + unused
  ids distinct
  both legs valid
  construct prospective events/state

PHASE 2 COMMIT:
  advance cursor/quota
  mark source pair replaced
  create replacement pair
  bind both scheduled legs
  append events
```

Любой validation failure => состояние идентично до вызова.

Добавить test helper snapshot, который сравнивает:

```text
pairs
attempts
seed_owner
used_pairs
pool_cursor
ledger events
source pair state
```

до/после rejected call.

Обязательные negatives:

```text
duplicate replacement_pair_id
duplicate author attempt id
duplicate external attempt id
invalid author id format
invalid external id format
replacement seed already owned
second-leg conflict
```

Во всех случаях:
```text
no cursor movement
no quota consumption
no source state change
no new pair
no new attempt
no new ledger event
```

## m-2 — snapshot safety

`open_pair()` не должен возвращать shallow copy с общим `legs`.

Вернуть независимый snapshot, например:
```python
result = dict(pair)
result["legs"] = dict(pair["legs"])
```

Тест:
```text
returned = open_pair(...)
mutate returned["legs"]
internal pair(...) unchanged
```

Проверь также публичные `ledger`/snapshot getters на утечки mutable nested state.

## Validation

```bash
python3 -m unittest discover -s tests -t . -v
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .
# validate all EX-* exactly as hosted workflow
```

Никаких scientific runs.

## Handoff

Сохранить новый exact:

```text
R4_2_HEAD =
R4_2_TREE =
M-5 =
M-6 =
m-2 =
TEST_COLLECTION =
HARNESS =
SCIENTIFIC_RUNS = 0
CANDIDATE = PRE-DATA / NOT FROZEN
HG-B = WAITING_OWNER
R2 = WAITING_HOST / NOT_ACTIVE
NEXT_ACTOR = fresh REVIEWER
```

Verifier не запускать до fresh Reviewer PASS.
