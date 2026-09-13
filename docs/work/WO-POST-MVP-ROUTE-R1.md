# WO-POST-MVP-ROUTE-R1 — Зафиксировать post-MVP траекторию NanoLab

## Паспорт

- Work Order: `WO-POST-MVP-ROUTE-R1`
- Checkpoint: control change после `NL4 = MVP COMPLETE`, перед `NL5-001`
- Base: `main @ 50318c7b32576cf444f36a29ebd7c94a0cc38564`
- Branch: `control/post-mvp-route-r1`
- Risk: `MEDIUM` — меняются canonical roadmap/state/plan, но не physics/runtime/analysis
- Claim: без повышения scientific claim

## Цель

Зафиксировать решение владельца о дальнейшей траектории развития NanoLab после MVP:

`NL5-001 release/library → NL5-002 external reproduction → NL6/E5 driven DNA component → E3-R2 на более богатом design space → NL7 composition → targeted E4 при научной необходимости; E6 atomistic adapter позже либо по внешнему спросу`.

Одновременно устранить обнаруженную рассинхронизацию canonical state после закрытия NL4, не выдумывая неподтверждённые счётчики.

## Allowed paths

- `docs/control/POST_MVP_DEVELOPMENT_ROUTE_R1.md`
- `docs/ROADMAP.md`
- `project/state.json`
- `project/plan.json`
- `config/control/harness/checkpoint-catalog.v1.json`
- `docs/work/WO-POST-MVP-ROUTE-R1.md`
- `docs/work/executions/EX-POST-MVP-ROUTE-R1/**`

## Forbidden scope

- physics/runtime/analysis code
- новые научные запуски
- изменение уже принятого NL0–NL4 evidence
- запуск E4/E5/E6/E3-R2
- merge/direct push в `main`
- выбор лицензии владельца вместо владельца

## Требуемые изменения

1. Устранить duplicate `NL5-001` в `project/state.json`; оставить `READY`.
2. Синхронизировать подтверждённые post-NL4 execution facts: NL4 tasks completed, `physics_runs = 35`, E3 больше не `NOT_RUN`. Не менять неоднозначные счётчики без доказательства.
3. Зафиксировать depth-first стратегию: DNA nanomechanics остаётся основной вертикалью до управляемого компонента и composition.
4. Специализировать `NL6-001` на E5 driven component; E4 и E6 оставить отложенными условными направлениями.
5. Зафиксировать E3-R2 как post-E5 benchmark ИИ на богатом параметрическом пространстве, а не как немедленный повтор E3.
6. Определить ближайший operational sequence для NL5-001/NL5-002 и параллельного INFRA2→INFRA3.

## Validation

- JSON-файлы синтаксически корректны и не содержат duplicate keys.
- `frontier = NL5`, `next_work_order = NL5-001`, `NL5-001 = READY` согласованы между state/roadmap/plan.
- NL6/E5 route согласован между roadmap/plan/checkpoint catalog.
- Существующие NL0–NL4 acceptance не понижены и не переписаны.
- Отрицательный E3 result сохранён; никаких заявлений о доказанном преимуществе ИИ.

## Human gate

Merge в `main` только после review/verifier и решения владельца.
