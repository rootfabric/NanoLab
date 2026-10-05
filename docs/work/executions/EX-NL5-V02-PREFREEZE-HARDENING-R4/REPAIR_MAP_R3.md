# EX-NL5-V02-PREFREEZE-HARDENING-R4 — Repair Map R3 (R4.3 narrow repair: M-7 + m-3)

Дата: 2026-10-04. Ветка: `repair/nl5-v02-prefreeze-hardening-r4-r3`.
Base: tip `repair/nl5-v02-prefreeze-hardening-r4-r2` = `e58ac8225562995963c414e66b9b6ce6ea9ad55e`
(tree `7f9f063e266d74cc7d6c6646a3022184a06bc976` — exact reviewed R4.2 subject),
reviewer branch `review/nl5-v02-prefreeze-hardening-r4-2-r3` head `cfdd4cae0b12cffdeb05eb40a84108d7f2959ec1`
интегрирована `--no-ff` (merge `76e192a73b2d60273d1823d3df20586070a2d9a7`), история сохранена,
reviewer evidence не изменялись. Класс: PRE-DATA control-plane repair; **научных прогонов 0**;
candidate **NOT FROZEN**; START marker — append-only event
`0008-continuation-r4-3-repair-started` (до substantive edits; events 0003/0005/0007 не тронуты).

## Базлайн reviewer verdict

`docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/REVIEWER_VERDICT_R3.{md,json}`:
FAIL / FIX_REQUIRED на exact R4.2 subject. Подтверждено закрытыми (не переделывалось):
R2 M-6 atomic pair replacement = PASS, R2 m-2 snapshot safety = PASS, Git object
existence/byte binding = PASS, trust ceiling `DISPATCH_PRECONDITIONS_RECORDED` /
`machine_launch_authorized=false` / `HUMAN_PROTECTED_WRITER` = PASS. Blocking:
**M-7** (review/verify verdicts привязаны к pre-freeze subject, а не к frozen bytes;
все пять authority records принудительно в одном freeze-evidence commit —
«review exact frozen package» структурно невозможен). Minor: **m-3** (CLI/docstring
«0 = PASS / authorized plan produced»).

## M-7 — frozen-package review/verify sequencing (break the self-reference cycle)

| | |
|---|---|
| Дефект | Двухкоммитная схема R4.2 (R = pre-freeze reviewed subject; E = freeze-evidence commit с FROZEN байтами и review/verify records, указывающими на R) доказывала review R, но НЕ review frozen bytes E; все пять authority records обязаны были жить в одном E, что делает «review/verify exact frozen package» невозможным без self-reference |
| Required lifecycle | `S` = PRE-FREEZE candidate (PRE-DATA / NOT FROZEN; HG-B APPROVED) → `F` = FROZEN PACKAGE COMMIT (exact frozen protocol/contract/seed record; **без self-reference к собственному SHA**) → `R` = fresh review record (`reviewed_head/tree = F`) → `V` = fresh verify record (`verified_head/tree = F`) → `A` = authority/readiness evidence (binds F + exact R/V/HG-B/R2 record blobs) |
| Repair (validator) | `nanolab_v02_dispatch_authority` **schema_version 3** (schema 1 И 2 отклоняются — fail-closed, v2 two-commit shortcut больше не валиден). `subject_head`/`subject_tree` теперь пинуют именно FROZEN PACKAGE COMMIT F: `git cat-file -t F == commit`, `rev-parse F^{tree} == subject_tree`. `frozen_subject_binding` связывает contract/protocol/seed-record как exact immutable Git blobs **самого F** (не authority/evidence commit) и байт-в-байт с валидируемыми входами. Каждый authority record несёт СОБСТВЕННЫЙ immutable source binding (`source_commit`/`path`/`git_blob_sha1`/`canonical_sha256`/`record_kind`/`issuer_class`) — общий freeze-evidence commit больше не требуется; независимые review/verify commits/refs допускаются при exact-subject = F. Новая sequencing-проверка (`_validate_record_sequencing` + `git merge-base --is-ancestor`): source commits freeze/review/verify records обязаны быть СТРОГИМИ потомками F — record, предшествующий F, живущий на несвязанной истории или внутри самого F (self-reference cycle), отклоняется; HG-B/R2 records сознательно могут предшествовать F (lifecycle: S одобрен до freeze) — для них только binding-проверки |
| Repair (contract schema) | `scientific_subject.frozen_subject_head/tree` — **non-authoritative compatibility fields**: FROZEN-контракт канонически несёт `null` (F не может встроить собственный SHA), валидатор authority больше НЕ сравнивает их с authority pins; exact frozen HEAD/TREE хранятся во внешнем Director freeze / authority record (`freeze_record` pins + `subject_head`/`subject_tree` authority). NOT_FROZEN кандидат по-прежнему обязан нести `null` |
| Trust ceiling | Не изменён: `status = DISPATCH_PRECONDITIONS_RECORDED`, `machine_launch_authorized = false`, `launch_gate = HUMAN_PROTECTED_WRITER`, `identity_proof_ceiling = GIT_IMMUTABLE_RECORDS_ONLY`; `DISPATCH_AUTHORIZED` не существует ни на одном пути |
| Tests | Новый класс `FrozenPackageSequencingTest` (13) на РЕАЛЬНОМ временном Git repo с коммитами в порядке `S -> H -> F -> R -> V -> A`: lifecycle sequencing (S — корень, F — потомок S, R/V/A — строгие потомки F); FROZEN контракт внутри F не содержит self-SHA (compat поля = null); review/verify пинуют exact F и validation PASS с честным ceiling (exit 0 = preconditions recorded, НЕ авторизация); review/verify → S при frozen blobs → F ⇒ REJECT «review subject mismatch»; review → F, verify → S ⇒ REJECT «verify subject mismatch»; artifact binding → другой commit ⇒ REJECT «frozen artifacts must be exact blobs of the frozen package commit»; review/verify/freeze source на orphan-ветке (не потомок F, binding при этом бит-в-байт валиден) ⇒ REJECT «does not descend from the frozen package commit»; authority binds exact review/verify/freeze/hg_b/r2 blob refs (rev-parse `source_commit:path` == `git_blob_sha1`, sha256 == `canonical_sha256`); tampered verdict digest ⇒ REJECT «immutable source binding mismatch»; tampered verdict path ⇒ REJECT «immutable source binding failed»; nonexistent F ⇒ REJECT; wrong tree ⇒ REJECT; frozen bytes только в worktree ⇒ REJECT «frozen artifact bytes mismatch»; **legacy two-commit shortcut** (точная схема R4.2, self-consistent) ⇒ REJECT; HG-B/R2 до F — легальны (binding-only) |

## m-3 — remove «authorized plan produced» wording

| | |
|---|---|
| Дефект | Module docstring: `Exit codes: 0 = PASS / authorized plan produced` — противоречит removing machine authorization (R4.2) |
| Repair | Формулировка заменена: `0 = validation/preconditions recorded` (``prefreeze`` — internal-consistency PASS; ``plan`` — prepared execution plan при `machine_launch_authorized=false`); явный тезис «prepared plan is NOT a launch authorization: the real launch gate stays HUMAN_PROTECTED_WRITER»; docstrings `validate_dispatch_authority` / `build_execution_plan` синхронизированы с моделью M-7; grep по `scripts/`+`tests/` на «authorized plan» — 0 совпадений (кроме негативных упоминаний «NOT a launch authorization») |

## Сохранено без изменений (accepted surfaces)

M-2 replacement replay; M-3 collision proof; M-6 atomic pair ledger; m-2 snapshot
safety; TOST/equivalence wording; Git object existence/byte binding (механика M-5
сохранена, расширена sequencing'ем); trust ceiling DISPATCH_PRECONDITIONS_RECORDED;
`machine_launch_authorized=false`; HUMAN_PROTECTED_WRITER launch gate. Научные/
тулинг параметры не менялись: N = 64/64/10/10; N_min = 52/52/8/8; replacement
quotas = 12/12/2/2; replacement cap = 56; max_runs = 352; δ = 0.5; paired design;
R3 confirmatory identities. Committed PRE-DATA package (contract/record/manifest)
байт-в-байт тот же (digests сверены с `r4-2-prefreeze-validation-PASS-R4_2.json`).

## Валидация

```text
TEST_COLLECTION    = 593 tests OK (было 580; +13 net: FrozenPackageSequencingTest 13)
CHECK_CONSISTENCY  = ok (0 errors / 0 warnings)
WORKFLOW_LINT      = blocking 0 (violations 0)
WORK_CLI_ALL_EX    = 49/49 EX-* ok
PREFREEZE          = committed package: PREFREEZE_VALIDATION_PASS / DISPATCH_BLOCKED,
                     exit 0, budget 296/56/352/560 (evidence r4-3-prefreeze-validation-
                     PASS-R4_3.json, package digests unchanged)
SCIENTIFIC_RUNS    = 0
HOSTED_CI          = NOT_RUN
```
