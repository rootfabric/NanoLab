# EX-NL4-002-E3-MECH-R1 — сводка

Статус: **HANDOFF_READY** (IMPLEMENTER; MEDIUM → Reviewer + Director далее по WO-NL4-002).
Claim ceiling: **C0_SOFTWARE_ONLY / E3 comparison measured, no physics-interpretation**. LLM-arm НЕ запускался (отдельный execution EX-NL4-002-E3-LLM-R1 в fresh-сессии после merge mech-ветки).

## Что сделано

1. **RealExecutorAdapter** (`scripts/nl4/real_executor.py`): тот же интерфейс `ExecutorAdapter`, что `MockExecutor` (`estimate_wall_seconds` / `run`), подмена — инжект в `Controller(goal, executor)`. Полный пайплайн: digest-gated download-on-run варианта top+conf (+pro_CPU.in один раз; size+blob_sha1 обязательны, sha256 сравнивается если pinned, иначе computed-at-first-download записывается) → input builder из verbatim pro_CPU.in (DNA2/salt 0.5/300K/CPU/double; steps=50000, seed, per-run имена, print_conf_interval=4000, print_energy_every=100, lastconf_file; все отклонения — deviations.json) → запуск WSL oxDNA (pinned build 00dc7fb9) в `/home/yurig/nl4-002-e3/runs/<RUN_ID>/` (setsid/nohup, exit-код в файл, копии входов верифицированы sha256) → анализ observables v2 (mutual) + замороженный arm-манифест варианта + гейты E2_PROTO_R1 §4. Параллельный батч `run_parallel` + `ReplayExecutor` для canonical-учёта бюджета контроллером.
2. **Smoke** E3-SMOKE-R001 (0b/201004/50000): exit 0, wall 2360 с, угол посчитан (median 65.93°), гейты в норме. Артефакты smoke очищены (манифест/логи сохранены).
3. **Arms** (равный бюджет 5×50000, параллельно, goal target 90°):

| Arm | Кандидат (variant/seed) | RUN_ID | median° | score | wall, с |
|---|---|---|---|---|---|
| RANDOM | 11b/203012 | E3-RANDOM-R001 | 74.00 | 16.00 | 4365 |
| RANDOM | 11b/201004 | E3-RANDOM-R002 | 73.77 | 16.23 | 4387 |
| RANDOM | 0b/201004 | E3-RANDOM-R003 | 65.93 | 24.07 | 4323 |
| RANDOM | 32b/201004 | E3-RANDOM-R004 | 78.32 | **11.68** | 4428 |
| RANDOM | 53b/203012 | E3-RANDOM-R005 | 133.77 | 43.77 | 4280 |
| GRID | 0b/201004 | E3-GRID-R001 | 65.93 | 24.07 | 4380 |
| GRID | 0b/202008 | E3-GRID-R002 | 66.04 | 23.96 | 4382 |
| GRID | 0b/203012 | E3-GRID-R003 | 67.31 | 22.69 | 4383 |
| GRID | 11b/201004 | E3-GRID-R004 | 73.77 | **16.23** | 4566 |
| GRID | 11b/202008 | E3-GRID-R005 | 73.28 | 16.72 | 4545 |

- Best RANDOM: **32b/201004, score 11.68** (|78.32 − 90|).
- Best GRID: **11b/201004, score 16.23** (|73.77 − 90|).
- Счётчики (оба arms): runs 5/5, invalid 0, failed 0, rejected 0; все кадры 12/12 валидны.
- Суммарный executor wall 44039.76 с (10 ранов параллельно, ~77 мин wall-часов всего).

## Отклонения (все — в E3-MECH-summary.json / events)

1. **Сужение пространства кандидатов** (runner-level): E3 = {0b,11b,32b,53b} × {50000} × {201004,202008,203012}; 74b исключён его BLOCKED-статусом (EX-NL3-002-PARAM-74B-R1); steps закреплены 50000 бюджетом WO. `scripts/nl4/allowlist.json` НЕ менялся (фильтрация в `e3_mech_runner.narrowed_allowlist`).
2. **Манифесты 11b/32b/53b**: оказались уже present at base SHA 592c4a1 (влиты в main из параметрических веток) — копирование не потребовалось (checkout из origin/work/nl3-002-summary-r1 был no-op, байты идентичны).
3. **Параллельный запуск**: невариативные агенты → 5 ранов arm'а одновременно (оба arms — 10 процессов); canonical-бюджет — через Controller replay с идентичным порядком действий.
4. **Wall-cap breach (главное)**: кап 1.2 ч/ран калиброван под соло (~0.8 ч); контеншн 10 параллельных ранов замедлил каждый до 4280–4566 с; 9/10 ранов > 4320 с (макс +5.7%). Все раны завершили полные 50000 шагов, exit 0, без потери данных; помечены `wall_cap_breach` в ledger. Interrupt-path параллельного лаунчера не был энфорсен (implementation gap; исправлен пост-фактум в `run_parallel`, данные не пересчитывались). Условия обоих arms идентичны → сравнение arms не смещено; финальное отношение к breach — Director/REVIEWER.

## Проверки

- `tests/test_nl4_real_executor.py` (5 тестов: digest-гейт, input builder, fail-closed, digest-конвенция mock-совместимость, сужение пространства) + полный suite — зелёные.
- `work_cli validate/close`, `check-consistency` — см. события/логи.
- state.json не менялся.

## Next action

Director: merge mech-ветки → dispatch LLM arm (fresh-сессия, ветка `work/nl4-002-e3-llm-r1`, bounded-интерфейс, последовательный propose→run→observe, бюджет 5×50000) → батчевый REVIEWER → winner + re-validation (seeds 204016/205020).
