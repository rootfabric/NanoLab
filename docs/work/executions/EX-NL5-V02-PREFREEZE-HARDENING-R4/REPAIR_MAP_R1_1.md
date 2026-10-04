# EX-NL5-V02-PREFREEZE-HARDENING-R4 — Repair Map R1.1 (R4.1: reviewer corrections M-1..M-4 + m-1)

Дата: 2026-10-04. Ветка: `repair/nl5-v02-prefreeze-hardening-r4-r1`.
Base: tip `work/nl5-v02-prefreeze-hardening-r4` = `1964bb51915fb0850f7f34b99d6774c48af5bf60`
(post-terminal evidence-only tip; reviewed product subject = `62f65612…` / tree `a45f8295…`),
reviewer branch `review/nl5-v02-prefreeze-hardening-r4-r1` head `2729b9c4744339a188c222e8b0fae74fc7c50c62`
интегрирована `--no-ff` (merge `61aa6eb2`), история сохранена, reviewer evidence не изменялись.
Класс: PRE-DATA tooling/protocol-candidate repair; **научных прогонов 0**; candidate **NOT FROZEN**;
исторические R1/R2/R3/R4 verdicts и evidence не изменялись. START marker — append-only event
`0004-continuation-r4-1-repair-started` (до substantive edits; terminal HANDOFF event 0003 не тронут).

## Базлайн reviewer verdict

`docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/REVIEWER_VERDICT_R1.{md,json}`:
FAIL / FIX_REQUIRED на exact R4 subject. Blocking: M-1 (dispatch принимает NOT_FROZEN),
M-2 (replacement pools не replay-доказаны, нет R4 integrity digest), M-3 (легитимность
collision skips не привязана к freeze gate), M-4 (ledger leg-level, повторный replacement
на один failed attempt). Minor: m-1 (equivalence wording «неотличимость от нуля»).

## M-1 — PREFREEZE_VALIDATION отделена от DISPATCH_READY

| | |
|---|---|
| Дефект | `build_execution_plan()` строил `nanolab_v02_dispatch_execution_plan` для committed контракта с `freeze_status = NOT_FROZEN`; positive tests требовали exit 0 |
| Repair | Fail-closed two-stage authority. `validate_freeze_contract`/`freeze_gate`/новая `prefreeze_validation` — ТОЛЬКО внутренняя консистентность (`validation_stage = PREFREEZE_VALIDATION_PASS`, `dispatch = DISPATCH_BLOCKED`, `dispatch_ready = false` в каждом PASS-отчёте). Новый versioned machine-readable объект `nanolab_v02_dispatch_authority` (`validate_dispatch_authority`) машинно требует: `freeze_status == FROZEN` + frozen subject HEAD/TREE pins (contract ↔ authority ↔ freeze record); Director FREEZE record (path+sha256, decision=FREEZE, exact contract+record digests); HG-B `APPROVED` binding rule_id/candidate_revision; fresh review `PASS` + fresh verify `VERIFIED` на frozen subject HEAD/TREE; R2 `ACTIVE` + executors `AUTHOR_U1`/`EXTERNAL_U2` + executor policy: оба плеча allowed; sha256 exact contract file + seed record. Каждый referenced record обязан существовать на диске с bound digest и совпадать байт-в-байт со встроенной копией. `build_execution_plan()` требует authority (без него — `DISPATCH_BLOCKED`); fixture-authorities second-class: rejected без `allow_fixture=True`, план помечается `synthetic_test_fixture_only`. CLI: `plan --authority` обязателен; новый subcommand `prefreeze` |
| Fake-evidence запрет | Real PASS-records для тестов НЕ создавались; positive dispatch fixture — только в тестах, генерируется в tmp и явно помечен `SYNTHETIC TEST FIXTURE ONLY` (`fixture=true`), реального dispatch не авторизует |
| Tests | `DispatchAuthorityTest` (13): NOT_FROZEN→REJECTED, missing authority→REJECTED, HG-B≠APPROVED→REJECTED, subject mismatch→REJECTED, review≠PASS→REJECTED, verify≠VERIFIED→REJECTED, R2≠ACTIVE→REJECTED, executor mismatch→REJECTED, policy leg forbidden→REJECTED, contract digest mismatch→REJECTED, tampered record→REJECTED, missing key→REJECTED, synthetic fixture→PLAN. Изменены positive: `test_dispatch_plan_built_only_from_valid_package` → `test_prefreeze_package_cannot_produce_dispatch_plan`; `test_cli_gate_exit_zero_and_plan_exit_zero` → gate exit 0 + plan REJECTED |
| Evidence | `evidence/r4-1-prefreeze-validation-PASS-R4_1.json`, `evidence/r4-1-dispatch-blocked-PRE_DATA_R4_1.json` |

## M-2 — bit-exact replacement pool replay + R4 integrity digests

| | |
|---|---|
| Дефект | Validator проверял cursor/length/disjointness, но не доказывал, что pool — deterministic stream; hand-pick seed stream проходил |
| Repair | `replay_replacement_stream(anchor, variant, start_index, quota, skipped)`: независимая регенерация `for index from start_index: derive; drop только recorded skips; until quota`. Каждый skip entry — strict `{"index","seed","reason":"SEED_COLLISION_TREE"}` (exact keys, missing/extra → fail; seed обязан re-derive из stream; reason другой → fail; duplicate/до start_index/после последнего consumed → fail). Контракт+record содержат `replacement_pool_sha256` (digest по normalized pools) и полный `record_r4_sha256` / `seed_record_r4_sha256` (все identities+pools+skips+cursors); взаимные binding'и проверяются. Исторический R3 logical digest `eb4ab3f8…` сохранён без изменений как provenance — он больше не считается R4 integrity protection |
| Tests | `ReplacementReplayTest` (10): bit-exact clean replay PASS; изменённый seed в contract+record согласованно → REJECT; wrong skipped seed → REJECT; wrong reason → REJECT; extra key → REJECT; fake skip с истинным продолжением → REJECT (digest+coverage); wrong cursor → REJECT; stale pool digest → REJECT; record/contract pool drift → REJECT; stale record digest → REJECT; confirmatory skip не re-derive → REJECT |
| Регенерация | `scripts/nl5/repro_v02_r41_package.py` (committed, воспроизводимо): проверяет bit-exact replay, строит manifest, перепривязывает digests. Новые digests: `replacement_pool_sha256 = 369a63c05592c400a2d6c160ecad940d1b0654948c1165650dbd1cce6a7ee821`, `record_r4_sha256 = 51a8819236bd780b6034e83e3b89f4594ac176df3397a9c6b47806e09651fe91`, `seed_record_file_sha256 = 8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28` |

## M-3 — доказательство реальности каждого collision skip

| | |
|---|---|
| Дефект | Accepted identities сканировались clean, но recorded skip indices принимались на доверии → возможен hand-pick: удобный seed, предыдущий candidate помечается SEED_COLLISION_TREE |
| Repair | Machine-bound `collision_scan_manifest` (kind `nanolab_v02_collision_scan_manifest`): pin, exact allowlist, accepted confirmatory (148) + replacement (28) CLEAN вне allowlist, каждый recorded skip с `hit_paths` + `non_allowlisted_hit_count >= 1`, `manifest_sha256` над canonical content; contract binding `collision_scan_manifest: {path, sha256}`. Authoritative пути (`freeze_gate`, `prefreeze`, dispatch; CLI по умолчанию) RE-RUN pinned scan для каждого skip: fabricated skip на чистом candidate → `FREEZE_GATE_FAIL` даже при самосогласованной правке contract+record+manifest. Git error / missing object / timeout / non-repo → `collision-skip proof BLOCKED` (fail-closed, никогда не «clean»). Сгенерировано production-сканом по pinned tree `a9d7d07…`: 148+28 CLEAN, 41/41 skips с реальными non-allowlisted hits |
| Tests | `CollisionSkipProofTest` (8): CRITICAL fabricated skip (полностью self-consistent package, перезаписанные digests+manifest) → FAIL «found NO collision»; manifest digest mismatch → REJECT; incomplete coverage → REJECT; non-repo rerun → BLOCKED; pin mismatch → REJECT; missing manifest binding → REJECT; tampered manifest file (после binding) → REJECT; committed manifest доказывает все 41 skip + полный rerun PASS |

## M-4 — pair-level ReplacementLedger

| | |
|---|---|
| Дефект | Leg-level ledger позволял повторно вызвать replacement для одного failed attempt |
| Repair | Pair-level state machine: `pair_id` уникален; seed identity принадлежит ровно одному pair; attempt_id глобально уникален; author+external legs одной pair; состояния `PAIR_RUNNING / PAIR_COMPLETED / PAIR_FAILED_TECHNICAL / PAIR_REPLACED / PAIR_ABORTED`; replacement ТОЛЬКО для terminal `PAIR_FAILED_TECHNICAL` с ОБЕИМИ ногами (missing counterpart → REJECT); максимум ОДНА replacement assignment на failed pair (повтор → REJECT, cursor+quota не трогаются); replacement потребляет следующий frozen seed по порядку, создаёт NEW pair, планирует ОБЕ ноги (outcome-driven выбор невозможен конструктивно); second failure обязан ссылаться на replacement pair, не на исходную |
| Tests | `PairLedgerTest` (11): double replacement request (cursor/quota unchanged); author failed/external completed → replacement pair с обеими ногами; external failed mirror; missing counterpart → REJECT; variant mismatch → REJECT; seed/pair mismatch → REJECT; one-leg-only → REJECT; second failure → только NEW replacement pair; quota exhaustion без расширения; attempt-id uniqueness/формат; terminal pair не принимает legs |

## m-1 — equivalence wording

Candidate doc: PASS/`EQUIVALENT` теперь = «CI90 медианного парного сдвига целиком лежит
внутри заранее определённого equivalence interval (−δ·s_eff, +δ·s_eff)»; явно указано
«equivalence ≠ statistical non-significance vs zero» (сдвиг может отличаться от 0 и быть
practically equivalent). §4 hypotheses переведены на standard TOST: H0 = non-equivalence,
H1 = equivalence; механическое decision rule §9.2 остаётся authoritative. HG-B proposal:
append-only Addendum §9 (числа §8 не менялись). Тест `EquivalenceWordingTest` (3).

## Сохранено (границы R4 не тронуты)

PRIMARY N = 64/64, CONTROL N = 10/10; N_min = 52/8; replacement quota pairs = 12/12/2/2;
replacement cap = 56; max_runs = 352; δ = 0.5; paired design; R3 confirmatory identities
bit-exact; R3 logical digest `eb4ab3f8…` preserved; pinned-tree scan semantics (a9d7d07);
exact path allowlist; next_candidate_index = 75/76/21/21; outenemy = EXTERNAL_U2_ONLY;
R2 = WAITING_HOST / NOT_ACTIVE; candidate = PRE-DATA / NOT FROZEN. Dormant ветка
`repair/nl5-acceptance-policy-r4-power-gate-r1` НЕ смешивалась (Director sequencing).
Научные прогоны: 0. NL5 = IN_PROGRESS; external_reproductions = 0; NL6-001 = LOCKED;
HG-B = WAITING_OWNER; AUTHOR_U1 = NOT_ASSIGNED.

## Валидация (фактическая поверхность)

```text
python3 -m unittest discover -s tests -t .   → Ran 557 tests … OK (было 513; +44 R4.1 regressions)
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .  → ok:true
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .          → blocking: 0
PYTHONPATH=scripts python3 -m harness.work_cli validate (все EX-*, 49 dirs) → все OK
```

Hosted CI: **NOT_RUN** (TR-PR draft — следующий актор после fresh Reviewer PASS).
Новый exact subject — HEAD/TREE текущей ветки (см. event 0005 и финальный handoff).

## Супersed-пометка к историческим R4 evidence

`evidence/r4-dispatch-plan-PRE_DATA_R4.json` (R4) — исторический артефакт, демонстрировавший
именно M-1 дефект (plan из NOT_FROZEN). Он НЕ является действующим фактом после R4.1;
действующие факты dispatch — `r4-1-dispatch-blocked-PRE_DATA_R4_1.json`. Файл сохранён без
изменений (append-only evidence discipline).
