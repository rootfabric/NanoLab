## Identity

- Work Order / checkpoint:
- Execution ID:
- Risk class / claim class:
- Exact base SHA:
- Exact head SHA / tree:

## Goal and scope

Что должно быть доказано/реализовано. Allowed paths и явно незатронутые направления.

## Durable execution report

- START commit/passport:
- CONTINUATION checkpoints:
- HANDOFF/BLOCKED event:
- `CONTROL_WORK close` result:

## Changes

Код, документация, data contracts или protocol. Изменился ли scientific observable/acceptance criterion/model?

## Validation

Точные команды, exit codes, test summaries и evidence paths. Отдельно указать невыполненные проверки и skips.

## Experiments

Campaign/run IDs, frozen subjects, protocol revisions, artifact manifests/digests. Разделить execution outcome и scientific outcome. Отрицательные/inconclusive runs перечислить явно.

## Review

Reviewer/Verifier verdict, freshness exact-head evidence, remaining required fixes и claim ceiling.

## Risks / rights / resources

Model limitations, licenses, compute cost, secrets, large artifacts и external storage.

## Handoff

Обновлены только подтверждённые project/state поля. Одно следующее действие. Merge в `main` — Human Gate, если явно не разрешён текущей mission.
