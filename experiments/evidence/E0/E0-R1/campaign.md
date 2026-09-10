# Campaign E0-R1 — Контроль измерительного тракта (negative/geometric controls, units, statuses)

Experiment: `E0` ([паспорт](../../../docs/experiments/E0_PIPELINE_VALIDATION.md)). Протокол: `E0-PROTO-R1` ([PREREGISTRATION_E0_R1](../../../docs/research/PREREGISTRATION_E0_R1.md), machine binding: [protocol.json](protocol.json), дайджесты: [input_digests.json](input_digests.json)). Work Order: `NL2-001` ([WO-NL2-001](../../../docs/work/WO-NL2-001.md)). Исполнение: `EX-NL2-001-R1`. Claim ceiling: `C0_SOFTWARE_ONLY`; campaign-level scientific_outcome = `NOT_EVALUATED`.

## Вопрос кампании

Обнаруживает ли измерительный тракт NanoLab (машинные схемы + CLI-валидаторы + дисциплина manifest/event на frozen base) неправильные входы, корректные единицы и раздельные статусы прежде, чем результаты будут переданы ИИ?

## Состав (frozen до первого запуска)

```text
E0-R1-N001..N009  NEG    дегенеративные/пустые/повреждённые входы -> валидаторы обязаны fail-closed
E0-R1-U001..U002  UNIT   pinned-конверсия T=20C -> 0.097717 принимается; подделки отвергаются
E0-R1-G001..G003  GEO    SYNTHETIC-геометрии с аналитически известными значениями; нулевая ось -> ANGLE_UNDEFINED
E0-R1-S001..S003  STATUS технический outcome != научный conclusion (+ gap-проба S003)
E0-R1-POS001      POS    позитивный контроль: собственная evidence E0-R1 проходит валидаторы чисто
```

Каждый случай — уникальный run ID с собственным manifest.json / events / artifacts.manifest.json (контрактная форма-массив по ремонту NL1-002 R2). Фикстуры — SYNTHETIC, помечены явно, физическими данными не являются.

## Среда

Локальная Windows-станция, Python 3.11.8, jsonschema 4.22.0, git 2.53.0. Инструмент (`scripts/harness/**`, `config/control/harness/**`) заморожен бит-в-бит на base `15a2c9b1b5c095e24e2e1c24afd77feef5361102`. Фикстуры/инструменты извлекаются runner'ом сырыми блобами subject-коммита (байт-точно; CRLF рабочих копий не используется).

## Пререгистрация и границы

Все случаи, ожидания, tolerances (5e-7 units — из точности печати engine; 1e-12 — запас float64) и семантика исходов зафиксированы в `E0-PROTO-R1` ДО первого прогона. Pinned-факт единиц: ENGINE_ENVIRONMENT_R1 §6 (лог OBSERVED, NL1-001 ACCEPTED) — не выводится заново. Отрицательные результаты сохраняются; повторов под тем же run ID нет; post-hoc исключений нет. Приёмка E0 — независимые REVIEWER + VERIFIER и Director checkpoint; implementer не self-accept.

## Известные ограничения

- Engine-coupled случаи E0-дока (топология oxDNA, trajectory) — вне R1 (runtime отсутствует); см. §11 пререгистрации.
- Одна среда исполнения (Windows/Python 3.11.8).
- Gap-проба S003 может документировать отсутствие механического разделения статусов в валидаторе — это результат, а не сбой кампании.
