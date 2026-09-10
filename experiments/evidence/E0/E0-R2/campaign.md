# Campaign E0-R2 — Контроль измерительного тракта (повтор E0-R1 после технического отказа; ожидания 1:1)

Experiment: `E0` ([паспорт](../../../docs/experiments/E0_PIPELINE_VALIDATION.md)). Протокол: `E0-PROTO-R2` ([PREREGISTRATION_E0_R2](../../../docs/research/PREREGISTRATION_E0_R2.md), superseding `E0-PROTO-R1` только в части идентичности кампании; machine binding: [protocol.json](protocol.json)). Work Order: `NL2-001` ([WO-NL2-001](../../../docs/work/WO-NL2-001.md)). Исполнение: `EX-NL2-001-R1`. Claim ceiling: `C0_SOFTWARE_ONLY`; campaign-level scientific_outcome = `NOT_EVALUATED`.

## Почему R2

Попытка `E0-R1`: 18/18 `RUN_FAILED_TECHNICAL` — emit-путь runner'а (repo-root off-by-one) падал до записи результатов; научной оценки не было. Отказы сохранены в `../E0-R1/runs/` с причиной в каждом run; run ID не переиспользуются → кампания перезапущена как `E0-R2` с новыми run ID. Ожидания/критерии/tolerances — дословно из `E0-PROTO-R1`.

## Состав (frozen до первого запуска)

```text
E0-R2-N001..N009  NEG    дегенеративные/пустые/повреждённые входы -> валидаторы обязаны fail-closed
E0-R2-U001..U002  UNIT   pinned-конверсия T=20C -> 0.097717 принимается; подделки отвергаются
E0-R2-G001..G003  GEO    SYNTHETIC-геометрии с аналитически известными значениями; нулевая ось -> ANGLE_UNDEFINED
E0-R2-S001..S003  STATUS технический outcome != научный conclusion (+ gap-проба S003)
E0-R2-POS001      POS    позитивный контроль: собственная evidence E0-R2 проходит валидаторы чисто
```

## Поверхности

Фикстуры и инструменты — замороженные файлы кампании R1 (`../E0-R1/fixtures/`, `../E0-R1/tools/`), reused по дайджестам (`input_digests.json`, сырые блобы subject R2); schemas/валидаторы — бит-в-бит base `15a2c9b1b5c095e24e2e1c24afd77feef5361102`. Run-каталоги — `runs/`. Scratch: `C:\NanoLab\scratch\nl2-001\` (disposable).

## Границы

Все правила §0/§9/§10 `E0-PROTO-R1` действуют: отрицательные результаты сохраняются; повторов под тем же run ID нет; instrument drift → BLOCKED; приёмка — независимый review + Director; implementer не self-accept.
