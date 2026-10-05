# EX-NL5-V02-PREFREEZE-HARDENING-R4 — Repair Map R2 (R4.2 narrow repair: M-5 + M-6 + m-2)

Дата: 2026-10-04. Ветка: `repair/nl5-v02-prefreeze-hardening-r4-r2`.
Base: tip `repair/nl5-v02-prefreeze-hardening-r4-r1` = `7406b5a1755b7c025f6e10010be48a7fd231c9be`
(tree `8c6a9ba988fa3c539a2cecbba816a92d905e0495` — exact reviewed R4.1 subject),
reviewer branch `review/nl5-v02-prefreeze-hardening-r4-1-r2` head `2be5c8f35d88af069a5ac40eac73979df34e81cf`
интегрирована `--no-ff` (merge `5ea37a41671d82ab4576f4affbc5eda453d64436`), история сохранена,
reviewer evidence не изменялись. Класс: PRE-DATA control-plane repair; **научных прогонов 0**;
candidate **NOT FROZEN**; START marker — append-only event
`0006-continuation-r4-2-repair-started` (до substantive edits; events 0003/0005 не тронуты).

## Базлайн reviewer verdict

`docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/REVIEWER_VERDICT_R2.{md,json}`:
FAIL / FIX_REQUIRED на exact R4.1 subject. Подтверждено закрытыми (не переделывалось):
R1 M-2 replacement replay = PASS, R1 M-3 collision proof = PASS, R1 m-1 equivalence/TOST
wording = PASS. Blocking: **M-5** (dispatch authority принимает 40-hex строки без
механического доказательства существования frozen subject в Git), **M-6**
(`request_replacement` мутирует quota/cursor/source pair до завершения `open_pair`/
`_bind_attempt`), **m-2** (`open_pair` возвращает shallow copy с общим `legs`).

## M-5 — immutable Git/provenance binding dispatch authority

| | |
|---|---|
| Дефект | `validate_dispatch_authority()` проверял `subject_head`/`subject_tree` только как 40-hex строки и cross-сравнивал одни и те же строки между records; реальность Git-объектов не доказывалась: несуществующий head, неверное дерево, записи из dirty worktree и подделанные локальные JSON проходили бы при самосогласованных строках |
| Repair | **Subject existence (механически):** `git cat-file -t <subject_head>` обязан быть `commit`; `git rev-parse <subject_head>^{tree}` обязан равняться pinned `subject_tree`. **Immutable record bindings (schema_version 2):** каждый authority record (Director FREEZE, HG-B, review, verify, R2) обязан нести `source_commit` + `path` + `git_blob_sha1` + `canonical_sha256` + `record_kind`/`issuer_class`; все пять records привязаны к ОДНОМУ freeze-evidence commit; байты читаются из Git object database (`git rev-parse <commit>:<path>` / `git cat-file blob`), НЕ из mutable worktree; blob sha1 и sha256 обязаны совпадать с bound; встроенная копия обязана байт-точно соответствовать JSON из Git object (включая `record_kind`/`issuer_class` — provenance class неотделим от опубликованных байт). **Frozen artifact binding:** `frozen_subject_binding` связывает contract/protocol/seed-record как exact immutable Git blobs (source_commit + path + git_blob_sha1 + canonical_sha256) того же evidence commit и обязан совпадать байт-в-байт с валидируемыми входами (contract file, protocol text, seed record file). Модель: subject = reviewed commit (реальный, дерево сверяется), freeze fill-in (FROZEN контракт с пинами subject + records) = freeze-evidence commit — subject-коммит не может содержать собственный хэш внутри контракта, ровно как в реальном Director freeze-потоке. **Trust ceiling (M-5 item 6):** у инфраструктуры нет криптографически доказуемого trusted writer ⇒ machine conclusion жёстко capped: `status = DISPATCH_PRECONDITIONS_RECORDED`, `machine_launch_authorized = false`, `launch_gate = HUMAN_PROTECTED_WRITER` — `DISPATCH_AUTHORIZED` больше не существует ни на одном пути; реальный launch остаётся за внешним Human/Protected-Writer gate. **Fixture isolation (item 7):** fixture остаётся test-only (`fixture=true` + SYNTHETIC TEST FIXTURE ONLY marker + `allow_fixture=True`); positive fixture теперь использует ВРЕМЕННЫЙ НАСТОЯЩИЙ Git repo (реальные commits/trees/blobs) — флип `fixture=false` не даёт авторизации, а требует реальных Git bindings; schema downgrade до 1 отклоняется (fail-closed эволюция) |
| Negative tests | `DispatchAuthorityGitBindingTest` (11): positive fixture на реальном synthetic Git repo → план с `DISPATCH_PRECONDITIONS_RECORDED`/`machine_launch_authorized=false`; self-consistent несуществующий 40-hex head → REJECT «does not exist as a Git commit»; существующий head + неверное дерево → REJECT «subject_tree mismatch»; запись только в dirty worktree (rebind digest'ов, коммит старый) → REJECT «immutable source binding mismatch»; `source_commit` другой реальный commit → REJECT «freeze-evidence commit»; path↔blob mismatch (blob freeze-записи на пути hg_b) → REJECT; полностью git-bound локальный package с `fixture=false` → статус capped, `DISPATCH_AUTHORIZED` отсутствует во всём отчёте; artifact path вне evidence commit → REJECT «immutable artifact binding failed»; artifact source_commit mismatch → REJECT; worktree-контракт с самосогласованными digest'ами, но не frozen blob → REJECT «frozen artifact bytes mismatch»; schema_version 1 → REJECT. Плюс в `DispatchAuthorityTest`: positive план больше не содержит `DISPATCH_AUTHORIZED` (никогда) |
| Совместимость | `_authority_path_digest` (disk-based) удалён; `validate_dispatch_authority` получил kwarg `protocol_path` (backwards-compatible default `None`); `build_execution_plan` передаёт protocol path и добавляет в план `machine_launch_authorized=false` + `launch_gate` |

## M-6 — transactional ReplacementLedger

| | |
|---|---|
| Дефект | `request_replacement()` валидировал частично и мутировал quota/cursor/source pair ДО `open_pair`/`_bind_attempt`; дубликат replacement_pair_id, занятый replacement seed, невалидный/занятый attempt id второй ноги или отказ второй ноги оставляли ledger в неконсистентном состоянии (квота потрачена, pair заменён, одна нога) |
| Repair | Двухфазная транзакция. **PHASE 1 VALIDATE (zero mutation):** terminal `PAIR_FAILED_TECHNICAL` + обе ноги + не был заменён; variant; quota; pool cursor; `replacement_pair_id` — непустая строка и свободна; формат ОБОИХ attempt id по `ATTEMPT_ID_RE`; глобальная уникальность ОБОИХ attempt id; различие author/external; replacement seed (identity под курсором) не принадлежит другому pair. **PHASE 2 COMMIT (после всех проверок):** cursor/quota, source pair → `PAIR_REPLACED`, новый replacement pair, обе ноги SCHEDULED, события — под rollback guard: полный deep-enough snapshot всех мутабельных структур (`_snapshot_state`) до коммита и `_restore_state` при любом исключении — состояние восстанавливается бит-в-бит, исключение пробрасывается. Любой отказ ⇒ ledger структурно идентичен состоянию до вызова |
| Test helper | Новый публичный `ReplacementLedger.state_snapshot()`: независимые deep-enough копии `pairs` (обе ноги), `attempts`, `seed_owner`, `used_pairs`, `pool_cursor`, `quota_pairs`, `ledger` events — сравнение до/после rejected call |
| Tests | `PairReplacementAtomicityTest` (13): duplicate replacement_pair_id; duplicate author attempt id; duplicate external attempt id; invalid author/external id format; replacement seed already owned; simulated second-leg failure (mock `_bind_attempt` отказывает на external) ⇒ rollback всего: cursor/quota/source pair/без нового pair/без новых attempt/без новых events (snapshot equal); успешный replacement остаётся полным (обе ноги, 7 events); `state_snapshot` покрывает все поверхности и независим; double-rejection after успешного replacement; кластер существующих `PairLedgerTest` (11) без изменений — PASS |

## m-2 — snapshot safety

| | |
|---|---|
| Дефект | `open_pair()` возвращал `dict(pair)` с общим вложенным `legs` — мутация возвращённого значения изменяла internal state в обход state machine |
| Repair | `open_pair()` возвращает независимый snapshot (`legs` копируется, как уже делал `pair()`); дополнительно защищены остальные публичные getters: `ledger` теперь возвращает `[dict(event) for …]` (мутация события не доходит до internal), `pair()` уже копировал `legs` — покрыт тестом |
| Tests | `test_open_pair_returns_independent_snapshot` (мутация returned["legs"]/["state"] не влияет на internal); `test_ledger_property_returns_independent_event_snapshots`; `test_pair_property_deep_copies_legs` |

## Сохранено (accepted surfaces R4/R4.1 не тронуты)

R1 M-2 replacement replay, R1 M-3 collision proof, equivalence/TOST wording — код этих
поверхностей не изменялся; committed PRE-DATA package (contract/record/manifest digests)
байт-в-байт тот же (проверено digest'ами в свежем evidence); N = 64/64/10/10; N_min = 52/52/8/8;
replacement quotas = 12/12/2/2 пар; replacement cap = 56; max_runs = 352; δ = 0.5; paired design;
R3 confirmatory identities bit-exact; next_candidate_index = 75/76/21/21; pinned scan a9d7d07;
outenemy = EXTERNAL_U2_ONLY. Dormant `repair/nl5-acceptance-policy-r4-power-gate-r1` НЕ
смешивалась (Director sequencing). Научные прогоны: 0. NL5 = IN_PROGRESS;
external_reproductions = 0; NL6-001 = LOCKED; HG-B = WAITING_OWNER; AUTHOR_U1 = NOT_ASSIGNED;
R2 = WAITING_HOST / NOT_ACTIVE; CANDIDATE = PRE-DATA / NOT FROZEN; hosted CI = NOT_RUN.

## Валидация (фактическая поверхность)

```text
python3 -m unittest discover -s tests -t .   → Ran 580 tests … OK (было 557; +23 net R4.2)
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .  → ok:true
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .          → blocking: 0
PYTHONPATH=scripts python3 -m harness.work_cli validate (49 EX-*)     → все ok:true, errors:[]
prefreeze (committed package, pinned-scan rerun)                      → exit 0,
  PREFREEZE_VALIDATION_PASS / DISPATCH_BLOCKED (evidence r4-2-prefreeze-validation-PASS-R4_2.json)
```

## Итог R4.2

```text
M-5 Git/provenance binding  = FIXED — subject existence + tree equality механически;
                              records/artifacts = immutable Git objects evidence commit;
                              bytes из Git object database; issuer/provenance classes;
                              ceiling DISPATCH_PRECONDITIONS_RECORDED +
                              machine_launch_authorized=false + Human/Protected-Writer gate;
                              fixture остаётся test-only на реальном synthetic repo
M-6 atomic replacement      = FIXED — two-phase validate/commit + rollback guard;
                              state structurally unchanged после каждого rejection
m-2 snapshot safety         = FIXED — open_pair/ledger/pair возвращают независимые snapshots
Валидация                   = 580 tests OK; consistency ok; workflow_lint blocking 0;
                              49/49 EX-* ok; prefreeze PASS/DISPATCH_BLOCKED; hosted CI = NOT_RUN
```

Статусы НЕ меняются. NEXT_ACTOR = fresh independent REVIEWER на новый exact R4_2 HEAD/TREE
(см. event 0007). Verifier — только после Reviewer PASS.
