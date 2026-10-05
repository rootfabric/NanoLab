# EX-NL5-V02-PREFREEZE-HARDENING-R4 — Repair Map R1 (F1–F4)

Дата: 2026-10-03. Ветка: `work/nl5-v02-prefreeze-hardening-r4`.
Base main: `87298b36431045474d3784adf5cee8c9a64d0fc9`. Реализация: `962cc24`.
Класс: PRE-DATA tooling/protocol-candidate repair; **научных прогонов 0**;
candidate **NOT FROZEN**; исторические R1/R2/R3 evidence/verdicts не изменялись.

## Baseline (до ремонта)

`docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/audit/reproduce_findings.py` на
exact audited blobs воспроизвёл все находки (exit 0):
8 fail-open PASS-классов F1; `git grep` exit 128 → `collision_count = 0` и
worktree-слепота F2; повторный выбор confirmatory identities по правилу N+1 у
всех 4 вариантов F3; 51/64 = 0.796875 и 60/296 = 0.2027 F4.
Evidence: `evidence/r4-baseline-reproduction-F1-F3.json`.

## F1 — fail-closed freeze/dispatch contract

| | |
|---|---|
| Дефект | `freeze_consistency_gate()` R3 возвращал PASS на пустых control-массивах, дубликатах, historical seed, stale digest, отсутствующем bootstrap, противоречащих полях протокола |
| Repair | Новый versioned machine-readable контракт `scripts/nl5/repro_v02_freeze_contract.py` (`contract_revision = r4`) — единственный authoritative source freeze/dispatch: schema/kind/revision; exact key sets (extra/missing → FAIL); строгие типы (bool ≠ int); int32 range; длины == N; глобальная уникальность; disjoint fresh/bootstrap/replacement/historical; digest; bit-exact replay регенерации из cursor+skips; machine block документа; бюджет из одной политики. `load_*`/read ошибки, malformed JSON, unknown revision → `ContractError` (fail-closed) |
| Bypass-proof | Dispatch entrypoint `build_execution_plan()` сам вызывает полный `validate_freeze_contract`; PASS-ветка единственная; CLI `plan` exit ≠ 0 при FAIL. Negative tests: `test_dispatch_refuses_corrupted_contract`, `test_dispatch_refuses_missing_record`, `test_dispatch_refuses_*` |
| Tests | `ContractMalformedTest` (6), `SeedIntegrityNegativeTest` (13), `ProtocolDeclarationNegativeTest` (9) |
| Evidence | `evidence/r4-freeze-gate-PASS-R4.json`, `evidence/r4-dispatch-plan-PRE_DATA_R4.json`, `evidence/repro-v0-2-freeze-contract-PRE_DATA_R4.json` |

## F2 — immutable pinned-tree collision scan

| | |
|---|---|
| Дефект | `literal_tree_collision_scan` не различал exit 128 и no-match (fail-open), сканировал mutable worktree, prefix-исключения |
| Repair | Сканирование pinned commit (`git grep … <commit> --`); семантика: exit 0 = hits, 1 = clean, любой иной код / missing object / non-repo / timeout / broken git = `TreeScanError` (никогда `collision_count = 0` при неполной проверке); EXACT path allowlist (set membership, без prefix); worktree-режим явно `non_authoritative`; `make_pinned_tree_scanner` для fail-closed генерации |
| Tests | `CollisionScanNegativeTest` (4: non-repo, missing object, timeout, true no-match) + seeds-тесты: pinned-vs-dirty-worktree, exact-exclusion no-prefix |
| Evidence | `evidence/r4-collision-scan-R4.json` — 176 fresh identities на pinned tree `a9d7d07fa264e9907b67ca244b00ba2da3430b0f` = CLEAN; bootstrap provenance отдельным блоком (детерминистичны по anchor; легитимное повторение в R1/R2 records — не fresh identities) |

## F3 — deterministic replacement pool/cursor

| | |
|---|---|
| Дефект | Текстовое правило «N+1, N+2, …» повторно выбирало уже потреблённые confirmatory identities (0b idx 65 → seed 1960729465 и т.д.), т.к. R3 skips уже потребили индексы до 74/75/20/20 |
| Repair | `generate_replacement_pool(start_index = next_candidate_index)`: frozen pool продолжают deterministic поток СТРОГО после последнего потреблённого candidate index (включая skips); record/contract хранят `indices_consumed` / `next_candidate_index` / pool cursors; `ReplacementLedger`: attempt id уникальны навсегда (reuse → ValueError), replacement ТОЛЬКО для `FAILED_TECHNICAL` (outcome-driven выбор запрещён), потребление пула по порядку (детерминизм), исчерпание квоты → `ReplacementBudgetExhausted` без расширения; глобальный anti-collision против confirmatory+bootstrap+historical |
| Tests | `ReplacementStreamTest` (5: F3-наблюдение аудита отвергнуто, pool после cursor, taken-rejection, bit-exact replay, R3-наследование), `ReplacementLedgerTest` (6) |
| Evidence | `evidence/repro-v0-2-seed-record-PRE_DATA_R4.json` (pools 12/12/2/2; start 75/76/21/21) |

## F4 — integer rounding policy + scientific wording

| | |
|---|---|
| Дефект | `N_min=51` назывался «80% от 64» (51/64 = 79.6875% < 80%); replacement cap 60 при «≤20%» (60/296 = 20.27% > 20%); округления несогласованны; wording «гарантированно feasible» |
| Repair | Единая явно названная политика **`ceil-nmin-floor-replacement-pairs-v1`**: `n_min = ceil(0.80·N)` → 52/8; per-cell replacement quota = `floor(0.20·N)` пар → 12/12/2/2; replacement runs = 2/пара → cap 56; `max_runs = 296 + 56 = 352` (ужесточение с 356); все поверхности (gate, contract, doc machine block, тесты) производны от одного кода. Wording (candidate revision R4, явная таблица изменений R3→R4, append-only по отношению к истории): feasibility = «feasible на committed planning-данных», НЕ гарантия исхода новых данных; median-shift тест ≠ проверка всех свойств распределения (§3 scope-ограничение); исторический terminal MISMATCH NL5-002 и PLATFORM_INSENSITIVE не пересматриваются |
| Owner decision delta | Addendum в `docs/control/NL5_ACCEPTANCE_PRINCIPLE_HG_B_PROPOSAL_R1.md` (§Addendum R4): N_min 51→52, replacement cap 60→56, max_runs 356→352 — pre-data tightening из literal %-границ; HG-B остаётся WAITING_OWNER |
| Tests | `IntegerPolicyTest` (3), контрактные проверки (`test_wrong_nmin_value_fails`, `test_wrong_replacement_cap_fails`, machine-block contradictions) |

## Валидация (реальная hosted-test surface)

```text
python3 -m unittest discover -s tests -t .   → Ran 513 tests … OK
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .  → ok: true
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .          → blocking: 0
PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-*  → все ok
```

Hosted CI run для exact HEAD: **NOT_RUN** (gh-клиент не аутентифицирован;
draft PR → TR-PR маршрут — действие следующего актора). Локальная коллекция
не заменяет hosted CI fact и не заявляется таковой.

## Не изменено (границы)

`NL0–NL4/NL5-001 ACCEPTED`; NL5-002 terminal MISMATCH; PLATFORM_INSENSITIVE;
P1_RAW_GAP = CLOSED; 74b = NOT_MEASURED/KNOWN_GAP; frozen v0.1 envelopes;
исторические EX-* каталоги и events; merged PR #47 `scripts/r2/**` и
`config/infra/r2-activation.v1.json`; `project/state.json` / `infra-state.json`
(Director gate); `ENGINE_ENVIRONMENT_R1.md`. Новых scientific runs: 0.
NL5 = IN_PROGRESS; external_reproductions = 0; NL6-001 = LOCKED.
