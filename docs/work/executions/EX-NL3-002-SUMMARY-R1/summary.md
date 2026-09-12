# EX-NL3-002-SUMMARY-R1 — сводка серии E2 + карточка компонента 0b

IMPLEMENTER fresh-сессия. Интеграционная ветка `work/nl3-002-summary-r1` от `bdbebfd` с merge четырёх параметрических веток (конфликты `SESSION_LOG.md` — union). **Прогонов физики: 0**; только чтение опубликованных evidence.

## Deliverables

1. `evidence/parametric-summary.json` — канонический JSON: per-variant common-window (t ≤ 150000) ре-срез (median/IQR/q5–q95/пул/bootstrap 10000 seed 424242, frozen-методика §6) + published-значения рядом + строка 74b NOT_MEASURED + манифест-сводка (arm_a/arm_b/coverage/угол frame 0). Время кадра — из published per-frame поля `time` (шаги); индексная реконструкция не потребовалась. Детерминизм: два прогона билдера → байт-идентичный JSON (SHA-256 `58260815A684A290E663214F6D881725DEE4D761E10E8B5B3839A676DF4F7B1A`). Cross-checks: 32b/53b recomputed == published (точно); 0b 111/150, 11b 111/138 в окне.
2. `evidence/component-card-0b.md` + `evidence/component-card-0b.json` — карточка компонента DNA Hinge / 0b: геометрия (8378 нт / 112 стрендов; arm_a 4006 / arm_b 3942), среда (oxDNA 00dc7fb9 CPU/double, DNA2, salt 0.5, 300 K, WSL), распределение угла confirmatory 200k (пул median 65.98°, CI95 [65.67, 66.32]), стабильность (гейты 150/150, pf_v2 ≥ 0.9809, energy drift ≤ 0.00986), confidence (R_confirm=3, seeds 201004/202008/203012, frozen протокол), строка parameter→response в окне 150k (65.87°, CI95 [65.61, 66.12]), ограничения, provenance (pinned 23fd1ff, digest-гейты 3/3, REFERENCE_ONLY), воспроизведение по шагам.
3. `evidence/series-summary.md` — human-сводка: таблица вариант → steps-режим → N валидных → median/IQR/CI (окно + published), статус 74b (BLOCKED honest gap), ссылки на все execution'ы. Без тренд-интерпретаций.

## Ключевые числа (общее окно 150k, пул 111 кадров)

0b 65.87° [65.61, 66.12] · 11b 73.93° [73.71, 74.12] · 32b 78.09° [77.79, 78.67] · 53b 132.36° [131.78, 132.99] · 74b NOT_MEASURED (BLOCKED).

## Исходы

- execution_outcome: COMPLETED (данные подготовлены; physics_runs = 0).
- scientific_outcome: MEASURED (агрегированные измеренные распределения; интерпретации/тренды — Director после review; implementer не self-accept).

## Ограничения

state.json не менялся; scripts/tests/docs/research не менялись; байты источника не читались за пределами published evidence. NEXT: батчевый REVIEWER серии → Director NL3-002 acceptance → merge (Human Gate).
