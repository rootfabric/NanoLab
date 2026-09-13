# WO-POST-MVP-EXECUTION-PROGRAM-R1 — Подготовить исполнительную программу post-MVP

## Паспорт

- Work Order: `WO-POST-MVP-EXECUTION-PROGRAM-R1`
- Checkpoint: control/planning, следующий за `WO-POST-MVP-ROUTE-R1`; НЕ меняет canonical state
- Base: `control/post-mvp-route-r1 @ e05793cc8ff03b3b1af2d81b38e39d82cd7527d6` (PR #37 head)
- Branch: `control/post-mvp-execution-program-r1` (stacked; merge строго после PR #37)
- Risk: `LOW` — один новый planning-документ + harness-записи; без кода/физики/state
- Claim: без повышения scientific claim

## Цель

Декомпозировать зафиксированную стратегию `POST_MVP_DEVELOPMENT_ROUTE_R1` в
исполнительную программу: Gate 0 приёмки PR #37, трек NL5-001 (A..D),
NL5-002 external reproduction, параллельная линия INFRA2→INFRA3, вход в
NL6-001/E5 и NL6-002/E3-R2, owner decision register, метрики, риски и
стоп-условия.

## Allowed paths

- `docs/control/POST_MVP_EXECUTION_PROGRAM_R1.md`
- `docs/work/WO-POST-MVP-EXECUTION-PROGRAM-R1.md`
- `docs/work/executions/EX-POST-MVP-EXECUTION-PROGRAM-R1/**`

## Forbidden scope

- любые изменения `project/state.json`, `project/plan.json`, `docs/ROADMAP.md`,
  `docs/work/WORK_QUEUE.md`, checkpoint catalog (это территория PR #37);
- physics/runtime/analysis code; новые научные запуски;
- изменение принятых NL0–NL4 evidence;
- merge/direct push в `main`; push в `control/post-mvp-route-r1`;
- принятие owner-решений (D1..D7) вместо владельца.

## Требуемые изменения

1. Программный документ: треки, входные/выходные условия, DoD, гейты, метрики,
   риски, стоп-условия — без новых сроков и недоказанных значений.
2. Явная подчинённость route R1: программа не создаёт альтернативных статусов
   и не меняет acceptance.

## Validation

- Новый документ ссылается на существующие canonical файлы корректно.
- Никакие canonical файлы не изменены (diff — только новые файлы).
- Harness-записи проходят `CONTROL_WORK.sh validate`.

## Human gate

Merge в `main` (после merge PR #37) — только после owner review.
