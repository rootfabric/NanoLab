# Campaign E0-R3 — Контроль измерительного тракта (третья попытка; ожидания 1:1 из E0-PROTO-R1)

Experiment: `E0`. Протокол: `E0-PROTO-R3` ([PREREGISTRATION_E0_R3](../../../docs/research/PREREGISTRATION_E0_R3.md), superseding `E0-PROTO-R2` только в части идентичности; machine binding: [protocol.json](protocol.json)). Work Order: `NL2-001`. Исполнение: `EX-NL2-001-R1`. Claim ceiling: `C0_SOFTWARE_ONLY`; campaign-level scientific_outcome = `NOT_EVALUATED`.

## Почему R3

R1: 18/18 FAILED_TECHNICAL (emit repo-root bug). R2: 17/18 FAILED_TECHNICAL (materialize передавал кампания-относительные пути фикстур в git cat-file; события несли зашитый campaign_id; POS-исход — артефакт отказа). Обе попытки сохранены с причинами; run ID не переиспользуются. Runner полностью параметризован (`87bf408`).

## Состав (frozen)

```text
E0-R3-N001..N009  NEG    fail-closed обязательна на повреждённых поверхностях
E0-R3-U001..U002  UNIT   T=20C -> 0.097717 принимается; подделки отвергаются
E0-R3-G001..G003  GEO    аналитические SYNTHETIC-геометрии; ANGLE_UNDEFINED; ориентация
E0-R3-S001..S003  STATUS технический outcome != научный conclusion (+ gap-проба S003)
E0-R3-POS001      POS    позитивный контроль собственной evidence E0-R3
```

## Поверхности

Фикстуры/инструменты — замороженные поверхности кампании R1 (`../E0-R1/fixtures/`, `../E0-R1/tools/`; fixture-base/tools-dir передаются runner'у явно), schemas/валидаторы — бит-в-бит base. Дайджесты — `input_digests.json` (subject-коммит). Run-каталоги — `runs/`.

## Границы

Все правила §0/§8/§9/§10 `E0-PROTO-R1` действуют без изменений. Приёмка — независимый review + Director; implementer не self-accept.
