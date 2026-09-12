# Карточка компонента: DNA Hinge / 0b

Каноническая машиночитаемая версия: `component-card-0b.json` (рядом). Все числа — из frozen опубликованных evidence; ни одно число не оценено. Scientific outcome: **MEASURED** (измеренные распределения; интерпретации угла и соответствия статье запрещены до отдельного решения; claim ceiling `C0_SOFTWARE_ONLY`/measured-only).

Семейство: Shi–Castro–Arya DNA hinge (DOI 10.1021/acsnano.7b00242; регистрация `HINGE_FAMILY_R1.md`).

## Геометрия

- Топология: **8378 нт, 112 стрендов** (`MD_Hinges/0b.top`).
- Манифест рук (frozen, arm-manifest-v1, definition-before-data): **arm_a 4006 нт / arm_b 3942 нт**; манифест покрывает 7948 нт = 99.97% парных нуклеотидов (94.87% топологии; непарный остаток — 1 неассоциированная цепочка).
- Угол frame 0 по манифесту: **66.89°** (конвенция [0,180]°, PCA-оси).
- Источник: `docs/work/executions/EX-NL3-002-PROTO-R1/evidence/arm-manifest-0b.json`.

## Среда

- Движок: **oxDNA @ 00dc7fb9**, CPU-сборка, double precision (`ENGINE_ENVIRONMENT_R1`: WSL2 Ubuntu 24.04, gcc 13.3.0, cmake 3.31.6 user-local).
- Модель: **DNA2**, salt **0.5**, T **300 K** (авторская установка конфига; decision rule `E2-SETUP-R1` §5 — reproduction arm verbatim).
- Confirmatory: **200000 steps**, print_conf_interval 4000, print_energy_every 100, dt 0.005.

## Распределение угла (confirmatory, 200k)

Frozen протокол `E2_PROTO_R1`; детектор v2 mutual-nearest + frozen манифест рук; конвенция [0,180]°, PCA-оси (erratum R1 §2.5). Источник: `confirmatory-summary.json` (EX-NL3-002-R1).

| Статистика (150/150 валидных кадров, пул 3 реплик) | Значение |
|---|---|
| Median (pooled) | **65.98°** |
| IQR | [64.94, 67.06]° |
| q5–q95 | [63.00, 68.41]° |
| Bootstrap CI95 (median) | [65.67, 66.32]° (10000 resamples, seed 424242) |
| Per-replica median | C001 65.10° / C002 65.71° / C003 67.24° |

## Стабильность

- Гейты целостности §4: **pass 150/150 кадров** (lbf ≤ 0.1078, pf_v2 ≥ 0.50, disp ≤ 20.0).
- pairs_fraction_v2 min ≥ **0.9809**; long_bond_fraction max 0.0560; displacement max 8.40.
- Энергия: max |drift| total ≤ **0.00986** по всем репликам (2001 строка energy на реплику).

## Confidence симуляции

- **R_confirm = 3**, независимые seeds **201004 / 202008 / 203012**.
- Все параметры статистики и гейтов заморожены в `E2_PROTO_R1` **до** прогонов (§4, §6); обсервабли — `E2_OBSERVABLES_R2.md`.

## Строка parameter → response (общее окно 150k)

| Вариант | N валидных в окне | Median (окно 150k) | Bootstrap CI95 |
|---|---|---|---|
| **0b** | 111 | **65.87°** | [65.61, 66.12]° |

Вторичное кросс-вариантное окно (addendum §8 п.3); первичный confirmatory-результат 0b (200k) не пересматривается. Полная таблица серии: `parametric-summary.json`, `series-summary.md`.

## Известные ограничения

1. Конвенция угла [0,180] по PCA-осям не имеет прямого соответствия SI статьи; U-obs-1 закрыт first-principles решением (`E2_OBS1_SI_DECISION_R1.md`), не подгонкой.
2. v2-детектор пар (mutual-nearest, window + antiparallel a1) — инструментальная конвенция NanoLab, не авторский код.
3. Coarse-grained модель oxDNA DNA2: количественное соответствие эксперименту не claim'ится (ceiling C0/measured-only).
4. lbf-baseline авторского конфига зафиксирован как есть (≤ гейта); денатюрация отдельно не моделировалась.
5. T 300 K vs авторские 298 K в части конфигов закрыта decision rule `E2-SETUP-R1` §5 (reproduction arm = verbatim).

## Source provenance

- Upstream: `gauravarya77/DNA-hinge-simulations` @ **23fd1ff7731e9017bd776f49206dc42d70d9fe91**, режим **REFERENCE_ONLY** (G1 = B: download-on-run, без durable-кэша, удаление после execution).
- Digest-гейты (size + blob_sha1 обязательны, sha256 верифицирован): `0b.top` 120204 / blob `84edad43…5e44b` / sha256 `cd046127…aae01f`; `0b.conf` 2294162 / blob `181373f0…4da` / sha256 `506c41fc…d263`; `pro_CPU.in` полный пин. Гейт 3/3 PASS.
- Raw-артефакты (траектории) вне Git; манифесты SHA-256+size — `c00X-artifacts.manifest.json`.

## Воспроизведение

```text
1. python docs/work/executions/EX-NL3-002-R1/evidence/download_and_verify.py
   # download-on-run + digest-гейт (size+blob_sha1+sha256 против source_pins.json)
2. python docs/work/executions/EX-NL3-002-R1/evidence/build_confirm_inputs.py
   # 0b.top/0b.conf verbatim + pro_CPU.in; seeds 201004/202008/203012; copy-checks SHA-256
3. python docs/work/executions/EX-NL3-002-R1/evidence/run_confirm.py
   # CPU oxDNA @ 00dc7fb9 (WSL), 3 параллельные реплики, 200000 steps, бюджет 3.5 ч/реплику
4. python docs/work/executions/EX-NL3-002-R1/evidence/confirm_analysis.py
   # frozen-анализ: v2 mutual + гейты §4 + статистика §6 (bootstrap 10000, seed 424242)
5. python docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/param_summary_build.py
   # ре-срез общего окна t <= 150000 по времени кадра, тот же статистический метод
```

Детерминизм анализа и сводки — байт-в-байт (два прогона → идентичный JSON).
