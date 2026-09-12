# Сводка параметрической серии E2 (общее окно t ≤ 150000)

EX-NL3-002-SUMMARY-R1. Без новых прогонов физики: только чтение опубликованных evidence JSON. Канонические числа: `parametric-summary.json` (рядом); детерминизм билдера — байт-в-байт (два прогона → идентичный JSON, SHA-256 `58260815…`).

Метод ре-среза: у каждого кадра в published analysis JSON записано поле `time` (шаги oxDNA, print_conf_interval = 4000); окно — кадры с `time ≤ 150000`, per-replica. Индексная реконструкция времени не потребовалась; raw-траектории не читались. Статистика — frozen §6 (median/IQR/q5–q95 + bootstrap CI95 медианы, 10000 resamples, seed 424242), та же реализация, что в confirmatory-анализе.

## Таблица серии (параметр → угол)

| Вариант | Steps-режим | N валидных кадров в окне | Median (окно 150k) | IQR (окно) | Bootstrap CI95 (окно) | Published (без среза): N / median / CI95 |
|---|---|---|---|---|---|---|
| **0b** | 200000 confirmatory (frozen; срез — вторичная таблица §8 п.3) | 111 (37×3; last t=148000) | **65.87°** | [64.98, 66.58]° | [65.61, 66.12]° | 150 / 65.98° / [65.67, 66.32]° |
| **11b** | 200000 requested → truncated ~184000 (ABORTED_BUDGET_INTERRUPT, окно покрыто) | 111 (37×3; last t=148000) | **73.93°** | [73.06, 74.55]° | [73.71, 74.12]° | 138 / 73.98° / [73.77, 74.17]° |
| **32b** | 150000 (addendum §8) | 111 (37×3; last t=148000) | **78.09°** | [77.04, 79.78]° | [77.79, 78.67]° | 111 / 78.09° / [77.79, 78.67]° (= окно) |
| **53b** | 150000 (addendum §8) | 111 (37×3; last t=148000) | **132.36°** | [131.31, 134.41]° | [131.78, 132.99]° | 111 / 132.36° / [131.78, 132.99]° (= окно) |
| **74b** | not run (blocked до прогонов) | — | **NOT_MEASURED** | — | — | — |

Доля валидных кадров в окне: **100%** у всех измеренных вариантов (0b/11b: 111/111 в окне; 32b/53b: все кадры в окне, invalid 0). Per-replica медианы и полные q5–q95 — в `parametric-summary.json`.

## Статус 74b

**BLOCKED, honest gap**: детерминированный отказ деривации arm-манифеста (arm-manifest-v1, `FAILED_TWO_DOMINANT_BLOCKS`, две попытки — байт-идентичная ошибка) до любых прогонов; runs NOT_RUN. Per-variant stop rule WO-NL3-002-PARAM: серия продолжена без 74b. Failure-report: `docs/work/executions/EX-NL3-002-PARAM-74B-R1/evidence/arm-manifest-74b-failure.json`.

## Расхождения ре-среза / cross-checks

- 32b, 53b: recomputed common-window == published (медиана и CI совпали точно) — данные целиком в окне.
- 0b: 111 кадров окна из 150 опубликованных (срез отбрасывает t ∈ {152000…200000}); published-значения приведены рядом без пересмотра.
- 11b: 111 кадров окна из 138 опубликованных (срез отбрасывает t ∈ {152000…184000}).
- Гэпов и допущений нет: время кадра взято из published JSON; индексное восстановление (index×4000) не понадобилось.

## Ссылки на execution'ы

- 0b confirmatory: `docs/work/executions/EX-NL3-002-R1/` (frozen манифест рук: `EX-NL3-002-PROTO-R1/evidence/arm-manifest-0b.json`)
- 11b: `docs/work/executions/EX-NL3-002-PARAM-11B-R1/`
- 32b: `docs/work/executions/EX-NL3-002-PARAM-32B-R1/`
- 53b: `docs/work/executions/EX-NL3-002-PARAM-53B-R1/`
- 74b (BLOCKED): `docs/work/executions/EX-NL3-002-PARAM-74B-R1/`
- Манифест-сводка (arm_a/arm_b/coverage/угол frame 0 по вариантам): `parametric-summary.json` → `arm_manifest_summary`.

## Интерпретации

Cross-variant сравнения, тренды и выводы о параметр→угол зависимости — вне scope этого execution (Director-level). Claim: измеренные распределения, MEASURED.
