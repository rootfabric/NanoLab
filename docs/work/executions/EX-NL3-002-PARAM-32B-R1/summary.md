# EX-NL3-002-PARAM-32B-R1 — summary (NL3-002-PARAM, вариант 32b, frozen E2_PROTO_R1 inherited + addendum §8)

**Класс**: параметрический батч 32b; outcome = измеренные распределения; scientific_outcome = **MEASURED**. Научные выводы и любые кросс-вариантные сравнения (с 11b/0b) не делаются в этом исполнении — их делает Director после всех батчей серии. `project/state.json` не менялся.

## Что делалось

Параметрический батч **32b** по `docs/work/WO-NL3-002-PARAM.md` (наследование frozen `docs/research/E2_PROTO_R1.md` + **addendum §8: steps = 150000**, единое окно сравнения t ≤ 150000; гейты §4 / статистика §6 / seeds-тройка / бюджет ≤3.5 ч — без изменений): манифест рук 32b ДО прогонов (definition-before-data), затем 3 реплики PARAM-32B-S001..S003 (seeds 201004/202008/203012, print_conf_interval 4000, print_energy_every 100). Входы: `32b.top` + `32b.conf` verbatim + `pro_CPU.in` — digest-gated download-on-run (G1=B) по pinned commit `23fd1ff`; обязательные гейты size+blob_sha1 PASS 3/3; sha256-пины 32b NOT_VERIFIED — вычислены при первой загрузке и записаны в evidence (`sha256_computed_at_first_download`: top b230ee96…, conf 9b9db169…), без претензии к реестру; pro_CPU.in полный пин PASS. Все входы скопированы в каталоги ранов byte-verified (F-1). Отклонения от `pro_CPU.in` — ровно протокольные (`PARAM-32B-S00X_deviations.json`: steps 150000 / seed / имена outputs / print intervals / lastconf_file / subject 74b→32b).

## Манифест рук 32b (arm-manifest-v1, frozen деривация, frame 0)

Два доминирующих блока выделяются — **PASS** (threshold 0.9; ядра 2552/1458; second/third = 1458/156 ≈ 9.35 ≥ 3.0): **arm_a = 4814 нт, arm_b = 3190 нт**; coverage 8004/8008 парных = **99.95%** (93.40% топологии из 8570 нт); pair graph greedy 4004 пар. Два прогона деривации байт-идентичны (sha256 2e542a61…). Угол frame 0 = **77.48°** (конвенция [0,180]).

## Прогоны — все 3 реплики завершены штатно (COMPLETED)

3 параллельных WSL oxDNA (00dc7fb9), старт 15:40:51 UTC, надёжный запуск через setsid/nohup-лаунчер (уроки инцидентов 11b учтены: движки в собственных сессиях, exit-коды/epochs в файлах, обёртка не участвует — инцидентов нет). **3/3 exit = 0; wall 8086/8116/8078 s (2.25 h ≤ 3.5 ч бюджета — PASS; ~0.0539 s/step на 8570 нт)**; energy 1501/1501 строк (полный ран); 37 кадров/реплику (t = 0…148000: 150000 не делится на 4000, кадр финального шага не печатается — truncation нет); lastconf записан. Крэшей движка нет.

| Run | Seed | Exit | Wall | Кадров | Energy rows |
|---|---|---|---|---|---|
| PARAM-32B-S001 | 201004 | 0 | 8086 s (2.25 h) | 37 | 1501/1501 |
| PARAM-32B-S002 | 202008 | 0 | 8116 s (2.26 h) | 37 | 1501/1501 |
| PARAM-32B-S003 | 203012 | 0 | 8078 s (2.24 h) | 37 | 1501/1501 |

## Измеренные распределения (MEASURED; интерпретаций нет)

Detector v2 **mutual-nearest** (frozen); reference pairs frame 0: 3292/3312/3279. Угол — манифест 32B (arm_a 4814 / arm_b 3190), конвенция [0,180]. **Гейты §4: 0 STRUCTURALLY_INVALID из 111 кадров; доля валидных 1.00 в каждой реплике.**

| Run | Угол median (валидные) | IQR | bootstrap 95% CI медианы | pf_v2 first→last (min) | lbf max | disp max | energy drift |
|---|---|---|---|---|---|---|---|
| S001 | 79.88° | 79.06–80.39 | 79.45–80.25 | 1.000→0.984 (0.982) | 0.0575 | 11.32 | 0.0147 |
| S002 | 77.49° | 76.70–78.04 | 76.95–77.95 | 1.000→0.987 (0.982) | 0.0562 | 11.21 | 0.0080 |
| S003 | 77.79° | 76.56–79.16 | 76.91–78.31 | 1.000→0.983 (0.981) | 0.0575 | 12.76 | 0.0123 |
| **Пул (111)** | **78.09°** | **77.04–79.78** | q5–q95 **75.75–81.21**; CI95 **77.79–78.67** (min 73.98 / max 81.54) | — | — | — | — |

Bootstrap: 10000 ресемплов, seed 424242, статистика = медиана, percentile CI. Детерминизм анализа: повторный полный прогон S001 байт-идентичен (sha256 2bf78173…). No optional stopping; исключений по гейтам нет.

## Артефакты

WSL `/home/yurig/nl3-002-param-32b/runs/PARAM-32B-S001..003/` (вне Git; траектории ~87 MB/ран), манифесты SHA-256+size+location: `evidence/s00X-artifacts.manifest.json` (11 файлов/ран, вкл. exit_code.txt). Полные per-frame трейсы и сводные: `evidence/s00X-analysis.json`, `evidence/PARAM-32B-analysis.json`, `evidence/PARAM-32B-summary.json` (canonical JSON). Временные исходники `%TEMP%\nl3-002-param-32b-src` и read-кэш удалены (U4 = NO).

## Чеки

work_cli validate/close ok; check-consistency ok; unittest discover — зелёные (см. 0005). Отклонений от протокола нет: все реплики полные (150000 шагов), бюджет ≤3.5 ч выполнен, digest-гейты и манифест PASS.

## Next

Батчевый REVIEWER (один fresh-Reviewer на серию 11b/32b/53b/74b) на exact HEAD `work/nl3-002-param-32b-r1` после завершения серии → Director: сводная серии → карточка компонента → NL3-002 acceptance → merge (Human Gate). Остальные варианты серии (53b/74b) — отдельные fresh-сессии; бюджетная калибровка 32b (~0.054 s/step при 3 параллельных) доступна для их планирования.
