# EX-NL3-002-PARAM-11B-R1 — summary (NL3-002-PARAM, вариант 11b, frozen E2_PROTO_R1 inherited)

**Класс**: параметрический батч 11b; outcome = измеренные распределения; scientific_outcome = **MEASURED** (по фактически записанным кадрам). Научные выводы не делаются; статус данных из-за бюджетного прерывания и acceptance — батчевый REVIEWER → Director. `project/state.json` не менялся.

## Что делалось

Параметрический батч **11b** по `docs/work/WO-NL3-002-PARAM.md` (наследование frozen `docs/research/E2_PROTO_R1.md` без изменений): манифест рук 11b ДО прогонов (definition-before-data), затем 3 реплики PARAM-11B-S001..S003 (seeds 201004/202008/203012, steps 200000, print_conf_interval 4000, print_energy_every 100). Входы: `11b.top` + `11b.conf` verbatim + `pro_CPU.in` — digest-gated download-on-run (G1=B) по pinned commit `23fd1ff`; обязательные гейты size+blob_sha1 PASS 3/3; sha256-пины 11b NOT_VERIFIED — вычислены при первой загрузке и записаны в evidence (`sha256_computed_at_first_download`: top 0a71e29c…, conf 8a29b2ea…), без претензии к реестру; pro_CPU.in полный пин PASS. Все входы скопированы в каталогы ранов byte-verified (F-1). Отклонения от `pro_CPU.in` — ровно протокольные (`PARAM-11B-S00X_deviations.json`).

## Манифест рук 11b (arm-manifest-v1, frozen деривация, frame 0)

Два доминирующих блока выделяются — **PASS** (threshold 0.95; ядра 1478/930, ratio 8.45 ≥ 3.0): **arm_a = 4218 нт, arm_b = 3722 нт**; coverage 7940/7940 парных = **100%** (94.03% топологии из 8444 нт); pair graph greedy 3970 пар. Два прогона деривации байт-идентичны (sha256 4078f285…). Угол frame 0 = **74.36°** (конвенция [0,180]).

## Прогоны — бюджетное прерывение (калибровочный исход, §5)

3 параллельных WSL oxDNA (00dc7fb9), старт 11:51:52 UTC. Скорость 11b ~0.066–0.067 s/step (0b был ~0.055) → полный ран ~3.6–3.7 ч > бюджета 3.5 ч. По протоколу §5 все движки SIGTERM-прерваны ровно на границе 12600 s (15:21:52 UTC): **46/50 кадров (93%)**, energy 1865/1867/1878 из 2001 строк, lastconf записан. Крэшей движка нет (0 < 2 — stop-условие не сработало). Инциденты (без влияния на данные движка, задокументированы): (1) родительская Python-обёртка погибла по таймауту harness-джоба — движки продолжили, wall восстановлен по ФС + кросс-чек log time_passed 12562–12570 s (прецедент F-3 из EX-NL3-002-R1); (2) pkill убил родительский bash → exit_code.txt не записан (exit_code = null, причина в run-reports.json). execution_outcome = **ABORTED_BUDGET_INTERRUPT**.

| Run | Seed | Exit | Wall | Кадров | Energy rows |
|---|---|---|---|---|---|
| PARAM-11B-S001 | 201004 | SIGTERM (budget) | 12472 s (3.46 h) | 46 | 1865 |
| PARAM-11B-S002 | 202008 | SIGTERM (budget) | 12448 s (3.46 h) | 46 | 1867 |
| PARAM-11B-S003 | 203012 | SIGTERM (budget) | 12401 s (3.44 h) | 46 | 1878 |

## Измеренные распределения (MEASURED; truncated 46/50; интерпретаций нет)

Detector v2 **mutual-nearest** (frozen); reference pairs frame 0: 3273/3269/3237. Угол — манифест 11B (arm_a 4218 / arm_b 3722), конвенция [0,180]. **Гейты §4: 0 STRUCTURALLY_INVALID из 138 кадров; доля валидных 1.00 в каждой реплике.**

| Run | Угол median (валидные) | IQR | bootstrap 95% CI медианы | pf_v2 first→last (min) | lbf max | disp max | energy drift |
|---|---|---|---|---|---|---|---|
| S001 | 74.36° | 73.85–74.75 | 74.12–74.57 | 1.000→0.985 (0.982) | 0.0556 | 7.32 | 0.0095 |
| S002 | 71.90° | 71.25–72.82 | 71.43–72.32 | 1.000→0.983 (0.983) | 0.0560 | 7.46 | 0.0062 |
| S003 | 74.47° | 73.99–74.97 | 74.11–74.69 | 1.000→0.988 (0.981) | 0.0560 | 8.04 | 0.0065 |
| **Пул (138)** | **73.98°** | **72.88–74.59** | q5–q95 **71.00–75.22**; CI95 **73.77–74.17** (min 70.27 / max 75.68) | — | — | — | — |

Bootstrap: 10000 ресемплов, seed 424242, статистика = медиана, percentile CI. Детерминизм анализа: повторный полный прогон S001 байт-идентичен (sha256 c4811ab3…). No optional stopping; исключений по гейтам нет.

## Артефакты

WSL `/home/yurig/nl3-002-param-11b/runs/PARAM-11B-S001..003/` (вне Git; траектории ~76 MB суммарно), манифесты SHA-256+size+location: `evidence/s00X-artifacts.manifest.json` (10 файлов/ран). Полные per-frame трейсы и сводные: `evidence/s00X-analysis.json`, `evidence/PARAM-11B-analysis.json`, `evidence/PARAM-11B-summary.json` (canonical JSON). Временные исходники `%TEMP%\nl3-002-param-11b-src` и read-кэш удалены (U4 = NO).

## Чеки

work_cli validate/close ok; check-consistency ok; unittest discover — зелёные (см. 0005). Отклонение от плана — только бюджетное прерывание 3/3 реплик на 93% длины (зафиксировано как калибровочный факт §5); остальные пункты протокола исполнены без изменений.

## Next

Батчевый REVIEWER (один fresh-Reviewer на серию 11b/32b/53b/74b) на exact HEAD `work/nl3-002-param-11b-r1` → Director: сводная серии → карточка компонента → NL3-002 acceptance → merge (Human Gate). Остальные варианты серии (32b/53b/74b) — отдельные fresh-сессии; бюджетная калибровка 11b (~0.066 s/step) доступна для их планирования.
