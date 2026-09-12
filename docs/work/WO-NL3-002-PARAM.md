# Work Order NL3-002-PARAM — E2 параметрическая серия (11b/32b/53b/74b × 3, frozen protocol)

Статус: READY (Author: Director 2026-09-12; owner authorization: «11b+32b+53b+74b × 3 (Recommended)»). Родитель: NL3-002, issue #7. Пререгистрационная база: `E2_PROTO_R1.md` (FROZEN) — гейты, статистика, steps, seeds-политика наследуются БЕЗ изменений; этот WO добавляет только смену subject'а внутри зарегистрированного семейства (`HINGE_FAMILY_R1`, пять опубликованных вариантов; выбор вариантов зафиксирован до данных в NL0-001/NL3-001).

## Child executions (по одной fresh-сессии на вариант, батчи последовательно)

`EX-NL3-002-PARAM-11B-R1` → `EX-NL3-002-PARAM-32B-R1` → `EX-NL3-002-PARAM-53B-R1` → `EX-NL3-002-PARAM-74B-R1`. Ветки `work/nl3-002-param-<variant>-r1` от свежего main на момент dispatch.

## Наследование frozen протокола (без изменений)

- steps = 200000; print_conf_interval = 4000; print_energy_every = 100; R_confirm = 3; **seeds 201004 / 202008 / 203012 на каждый вариант** (симметрия протокола, документированное решение — одинаковые seeds на разных системах допустимы).
- Гейты валидности: lbf(t) > 0.1078 / pairs_fraction_v2(t) < 0.50 / displacement_max(t) > 20.0.
- Статистика: median/IQR/q5-95/bootstrap CI (10000, seed 424242), no optional stopping; конвенция угла [0,180].
- Бюджет: ≤ 3.5 ч wall/реплику, ≤ 4 ч/батч; общий ≤ ~14 ч.

## per-variant добавления (каждый до своих прогонов — definition-before-data)

1. **Входы**: `MD_Hinges/<V>.top` + `MD_Hinges/<V>.conf` + `pro_CPU.in`, download-on-run по exact pinned commit, digest-гейт по `scripts/hinge_family/source_pins.json`: blob SHA-1 + size — обязательный гейт; SHA-256 пины для 11b–74b имеют provenance NOT_VERIFIED — при первой загрузке вычислить, записать в evidence и сверять при повторных использованиях (расширение реестра — отдельный control WO, НЕ в этом).
2. **Манифест рук**: `scripts/e2/arm_manifest.py` (та же frozen деривация arm-manifest-v1) на frame 0 данного варианта ДО прогонов варианта; отчёт (размеры блоков, coverage, angle frame 0) — в evidence; байт-детерминизм двух прогонов. Если деривация не даёт двух доминирующих блоков → BLOCKED этого варианта (честный gap), остальные продолжаются.
3. **Runs**: `PARAM-<V>-S001..S003`; отклонения от `pro_CPU.in` — как в E2_PROTO_R1 §3 (steps/seed/outputs/print-интервалы/lastconf), топология/конф — вариантные; всё в `<run>_deviations.json`.
4. **Анализ**: гейты §4 frozen; per-variant распределения; сводная таблица `parameter → median/IQR/CI` (без подгонки тренда — интерпретация вне исполнения).

## Маршрут и приёмка

IMPLEMENTER (fresh на вариант) → батчевый REVIEWER (один fresh-Reviewer на все 4 execution'а после завершения серии — протокол идентичен, различия только в subject; решение Director'а, зафиксировано здесь) → Director: сводная серия → карточка компонента → NL3-002 acceptance. Merge — Human Gate. campaign-level: MEASURED per variant; NL3-002 acceptance критерии — WORK_QUEUE.

## Стоп-условия

Как в E2_PROTO_R1 §4/§5 + per-variant: digest FAIL, деривация манифеста FAILED, крэш ≥ 2 реплик варианта → BLOCKED варианта (серия продолжается по остальным), логи сохраняются.

## Бюджет

≤ 4 ч wall на вариант; суммарно ≤ ~16 ч с анализом. Локальный WSL CPU; paid services: нет.
