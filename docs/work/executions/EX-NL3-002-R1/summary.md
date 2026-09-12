# EX-NL3-002-R1 — summary (NL3-002, E2-R1 confirmatory campaign, frozen E2_PROTO_R1)

**Класс**: E2-R1 confirmatory; outcome = измеренные распределения; scientific_outcome = **MEASURED**. Научные выводы не делаются; acceptance NL3-002 — Director после REVIEWER (fresh). `project/state.json` не менялся (E2-статус объявит Director).

## Что делалось

Confirmatory-кампания по замороженному `docs/research/E2_PROTO_R1.md` (FROZEN, параметры не менялись): 3 реплики × 200000 steps на первом шарнире `0b` (авторские `0b.top`+`0b.conf` verbatim, digest-gated download-on-run G1=B по pinned commit `23fd1ff`, size+blob_sha1+sha256 PASS 3/3; durable-кэш запрещён, временные исходники удалены после execution). Engine: pinned oxDNA `00dc7fb9` (build-source verified), CPU/double, WSL. Все digest-gated входы скопированы в каталоги ранов и byte-verified (урок F-1). Отклонения от `pro_CPU.in` — ровно протокольные (steps/seed/имена outputs/print_conf_interval=4000/print_energy_every=100/lastconf_file + subject 74b→0b): `evidence/c00X_deviations.json`.

## Прогоны (параллельные WSL-процессы; бюджет ≤3.5 ч/реплика — не превышён)

| Run | Seed | Exit | Wall | s/step | Кадров | Energy rows |
|---|---|---|---|---|---|---|
| E2-R1-C001 | 201004 | 0 | 11146 s (3.10 h) | 0.0557 | 50 | 2001 |
| E2-R1-C002 | 202008 | 0 | 10885 s (3.02 h) | 0.0544 | 50 | 2001 |
| E2-R1-C003 | 203012 | 0 | 11134 s (3.09 h) | 0.0557 | 50 | 2001 |

Общий calendar wall ≈ 3.1 h (старт 14:31, финиш 17:37 local). Инцидент без влияния на раны: родительский Python run-обёртки упал на bookkeeping-баге (`del` на `set`) после финиша первой реплики — движки продолжили и завершились штатно (exit 0 ×3 по exit_code.txt), wall восстановлен по ФС (birth energy-файла → mtime exit_code.txt; кросс-чек C002: in-process 10710.2 s vs 10885 s).

## Измеренные распределения (MEASURED; интерпретаций нет)

Detector v2 **mutual-nearest** (frozen); reference pairs frame 0: 3292/3301/3294 (калибровка PROTO 3300). Угол — ЗАМОРОЖЕННЫЙ `arm-manifest-0b.json` (arm_a 4006 / arm_b 3942), конвенция [0,180] (erratum R1 §2.5).

**Гейты §4** (lbf > 0.1078 / pairs_fraction_v2 < 0.50 / displacement_max > 20.0): **0 STRUCTURALLY_INVALID из 150 кадров**; доля валидных 1.00 в каждой реплике.

| Run | Угол median (валидные) | IQR | q5–q95 | bootstrap 95% CI медианы | pf_v2 first→last (min) | lbf max | disp max | energy drift |
|---|---|---|---|---|---|---|---|---|
| C001 | 65.10° | 63.47–66.02 | — | 64.17–65.57 | 1.000→0.986 (0.982) | 0.0556 | 7.43 | 0.0099 |
| C002 | 65.71° | 64.90–66.37 | — | 65.28–66.17 | 1.000→0.989 (0.985) | 0.0560 | 7.91 | 0.0066 |
| C003 | 67.24° | 66.31–67.95 | — | 66.68–67.52 | 1.000→0.988 (0.981) | 0.0555 | 8.40 | 0.0046 |
| **Пул (150)** | **65.98°** | **64.94–67.06** | **63.00–68.41** | **65.67–66.32** (min 61.77 / max 69.20) | — | — | — | — |

Bootstrap: 10000 ресемплов, seed 424242, статистика = медиана, percentile CI. No optional stopping; исключений по гейтам нет.

## Артефакты

WSL `/home/yurig/nl3-002-confirm/runs/E2-R1-C001..003/` (вне Git; траектории ~130 MB суммарно), манифесты SHA-256+size+location: `evidence/c00X-artifacts.manifest.json` (10 файлов/ран: входы + traj/energy/last/log + engine std). Полные per-frame трейсы и сводка: `evidence/c00X-analysis.json`, `evidence/confirmatory-summary.json` (canonical JSON). Временные каталоги исходников `%TEMP%\nl3-002-confirm-src` и read-кэш удалены (U4 = NO).

## Чеки

work_cli validate/close ok; check-consistency ok; unittest discover — все зелёные (см. 0005). Отклонений от протокола нет (инцидент с обёрткой задокументирован, на данные не повлиял).

## Next

REVIEWER (fresh-сессия) на exact HEAD `work/nl3-002-confirm-r1` → Director: E2-R1 outcome + решение NL3-002 acceptance по критериям WORK_QUEUE → merge (Human Gate).
