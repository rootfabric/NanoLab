# Campaign E0-R4 — Контроль измерительного тракта (исполнение исправленным инструментом; ожидания 1:1)

Experiment: `E0`. Протокол: `E0-PROTO-R4` ([PREREGISTRATION_E0_R4](../../../docs/research/PREREGISTRATION_E0_R4.md); machine binding: [protocol.json](protocol.json)). Work Order: `NL2-001`. Исполнение: `EX-NL2-001-R1`. Claim ceiling: `C0_SOFTWARE_ONLY`; campaign-level scientific_outcome = `NOT_EVALUATED`.

## Почему R4

R1 (emit repo-root) и R2 (materialize путей фикстур + зашитый campaign_id) — технические отказы, сохранены с причинами. R3 исполнена, но с erratum: 8 каталогов-фикстур (N004..N008, S001..S003) материализовались неполными (только перечисленные файлы), S003/S003-RETRY1 — артефакты того дефекта; R3 сохранена как есть. R4 — исполнение всех 18 случаев исправленным runner'ом (полные поддеревья фикстур; dry-run в scratch перед пререгистрацией).

## Состав (frozen)

```text
E0-R4-N001..N009  NEG    fail-closed обязательна на повреждённых поверхностях
E0-R4-U001..U002  UNIT   T=20C -> 0.097717 принимается; подделки отвергаются
E0-R4-G001..G003  GEO    аналитические SYNTHETIC-геометрии; ANGLE_UNDEFINED; ориентация
E0-R4-S001..S003  STATUS технический outcome != научный conclusion (+ gap-проба S003)
E0-R4-POS001      POS    позитивный контроль собственной evidence E0-R4
```

## Поверхности

Фикстуры/инструменты — замороженные поверхности кампании R1 (`../E0-R1/fixtures/`, `../E0-R1/tools/`), schemas/валидаторы — бит-в-бит base. Дайджесты — `input_digests.json` (subject-коммит). Run-каталоги — `runs/`. Scratch: `C:\NanoLab\scratch\nl2-001\`.

## Границы

Все правила §0/§8/§9/§10 `E0-PROTO-R1` действуют. Приёмка — независимый review + Director; implementer не self-accept.
