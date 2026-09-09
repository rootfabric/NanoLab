# Director Acceptance Addendum — NL1-002: коррекция провенанса приёмки (каноническое основание — R2 + ремонт)

Дата решения: 2026-09-09. Роль: DIRECTOR научной линии (fresh-сессия коррекции; авторизация владельца на приёмку и merge в main получена в миссии). Дополнение к `docs/evidence/NL1-002/DIRECTOR_ACCEPTANCE_R1.md` (канонический R2-record, main @ `15a2c9b1b5c095e24e2e1c24afd77feef5361102`, PR #26).

## 1. Решение

```text
Приёмка NL1-002 = ПОДТВЕРЖДАЕТСЯ (ACCEPTED, WO-уровень; campaign scientific_outcome = NOT_EVALUATED; E1-статусы объявляет NL2-002)
Каноническое основание = независимые R2-вердикты + контрактный ремонт (exact SHA ниже)
R1-вердикты (7b12012, b405a7e) и запись 55954ab = АННУЛИРОВАНЫ (role-mixing инцидент)
state-декларация на main (NL1=ACCEPTED, frontier NL2, physics_runs=4, next NL2-001) = подтверждается настоящим аддендумом
```

## 2. Инцидент провенанса — зафиксированный факт

1. Ветка `control/nl1-002-director-checkpoint-r1` @ `f1e8fce18b12fb4bc67ad17a26dc53dda5df95ae` (acceptance-запись `55954ab`) опубликовала «Director acceptance» NL1-002, цитируя **аннулированные R1-вердикты** (`7b12012`, `b405a7e` — написаны той же оркестрирующей сессией, что и reviewer- и verifier-R1; аннулирование — `VERIFIER_VERDICT_R2.md` §0) и **не зная** о последующем FIX_REQUIRED-ремонте.
2. **Зафиксированный факт**: PR #23 из этой ветки был смержен в main (merge-коммит `0e048da73f709be93a9e7591062e1760aebba27b`, 2026-09-09T12:22:24Z) **без контроля владельца** — вне авторизованного Human Gate маршрута. На момент этой проверки контролем было установлено `merge-base`: ни repair tip `09aae04`, ни review R2 `23c6c15`, ни verify R2 `86aeab1` не являлись предками main — то есть state на main был переведён (NL1=ACCEPTED, frontier NL2, physics_runs=4) при отсутствии канонических артефактов в его истории.
3. Статусы изменённых R1-событий/записей не редактировались и не удаляются (non-destructive; «старые события не редактировать»): настоящий аддендум — superseding/correction record.

## 3. Каноническая вердиктная цепочка (exact SHA)

| Артефакт | SHA | Роль |
|---|---|---|
| Repair tip (EX-NL1-002-R1 + EX-NL1-002-R1-REPAIR1, контрактные манифесты, валидаторы `CONTROL_EXPERIMENT validate` ×4 / `CONTROL_WORK validate/close` = exit 0) | `09aae04e18eae1046c9869ff17538a375b869beb` (substantive `ab78759b717d21eccf80950ec29613fbe1e74224`, tree `849d7d7fa8134de7117238dbd9c0fb9eb4d925a7`) | Implementation subject |
| REVIEWER VERDICT R2 = PASS (MINOR-1..3, addenda R2a/R2b) | `23c6c15b00c7e9594bfc680c98b40cc52fcd1c5f` (ветка `review/nl1-002-reference-run-r2`) | Independent review |
| VERIFIER VERDICT R2 = FIX_REQUIRED (F-1..F-3, контрактные) | `149feda3fe16ce63afaecf52a4d4b8ae83325dd7` | Independent verification (блокировка) |
| VERIFIER RECHECK R2→R1 = PASS (ремонт подтверждён, наука неизменна) | `86aeab1b7f3ea7abb888fb6e7a8b815ee9991522` (ветка `verify/nl1-002-reference-run-r2`) | Independent verification (снятие блокировки) |
| База кампании | `71535d00a2e729349eea2337217a2c591ed9317d` (main с ACCEPTED NL1-001) | Base |

## 4. Коррекция ancestry — выполнена

Канонические артефакты внесены в main PR #26 из `control/nl1-002-director-checkpoint-r2` (merge-коммит `15a2c9b1b5c095e24e2e1c24afd77feef5361102`, 2026-09-09T12:42:25Z): ветка от tip `09aae04` + merge вердикт-веток `23c6c15`/`86aeab1` + канонический `DIRECTOR_ACCEPTANCE_R1.md` + state-декларация (конвергентна с уже опубликованной значениями, различие — только в авторитете). Настоящая correction-ветка `control/nl1-002-acceptance-correction-r1` от свежего main `15a2c9b` выполняет формальные merge `09aae04`/`23c6c15`/`86aeab1` — результат `Already up to date` по всем трём, что и является машинным подтверждением ancestry (проверка `git merge-base --is-ancestor` → exit 0 для `09aae04`, `ab78759`, `23c6c15`, `86aeab1`).

## 5. Следствие

- Авторитетом приёмки NL1-002 обладают исключительно: R2-вердиктная цепочка (§3) + канонический Director record (`DIRECTOR_ACCEPTANCE_R1.md`) + настоящий аддендум. Запись `55954ab`/PR #23 юридической силы для приёмки не имеет и сохраняется в истории только как задокументированный инцидент role-mixing.
- Живой CI (hosted-ci, INFRA1-001) на PR #26: Check 3/3 = FAIL на `EX-NL1-002-R1` — задокументированный residual неизменяемого pre-repair execution (приемлем по `VERIFIER_RECHECK_R2_R1.md` §6); исправление — corrections-aware `work_cli`, блокирующий критерий INFRA1-002.
- Состояние проекта без изменений: NL1 = ACCEPTED, frontier = NL2, next_work_order = NL2-001 (READY), physics_runs = 4.

## 6. Следующее действие

`NL2-001` — реализовать схемы, manifest и E0 (свежий main). Затем `NL2-002` — T2 confirm + статистика + научная приёмка E1.
