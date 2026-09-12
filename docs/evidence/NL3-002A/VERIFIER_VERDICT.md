# VERIFIER-вердикт — EX-NL3-002A-R1

- **Execution**: `EX-NL3-002A-R1` (`docs/work/executions/EX-NL3-002A-R1/`)
- **Exact HEAD проверен**: `b6e99269c7671343ff37de811014e35bd1685cad` (ветка `verify/nl3-002a-pre-e2-r1` создана от `b6e9926`; `git rev-parse HEAD` сверен при создании worktree)
- **Дата**: fresh-сессия верификатора
- **Роль**: независимый VERIFIER — повторно исполнил все проверки и сравнил результаты с published evidence (не документационный review)
- **Independance caveat**: fresh-сессия, тот же физический хост/исполнитель — actor identity не доказывает независимый executor identity.

## Результаты воспроизведений

| # | Проверка | Команда | Результат | Расхождение |
|---|----------|---------|-----------|-------------|
| 0 | Exact-head binding | `git worktree add -b verify/nl3-002a-pre-e2-r1 b6e9926`; `git rev-parse HEAD` | `b6e99269c7671343ff37de811014e35bd1685cad` | нет |
| 1 | Тесты | `$env:PYTHONPATH='...\scripts'; python -m unittest discover -s tests -t .` | **Ran 227 tests — OK (skipped=1)** | нет (ожидание 227 OK, 1 skip) |
| 2 | Real-data cross-check ре-ран | `python docs/work/executions/EX-NL3-002A-R1/evidence/run_real_data_checks.py` + байтовое сравнение с `git show HEAD:...real-data-cross-check-report.json` | отчёт ре-рана **байт-идентичен** published (16647 B); все три pinned-файла проходят digest-гейт (blob SHA-1, SHA-256, размер), `retained: false` (durable-кэша нет) | нет |
| 3 | Независимый digest-гейт (свой код, без скриптов репо) | python urllib: загрузка `MD_Hinges/0b.top` и `MD_Hinges/pro_CPU.in` на pinned commit `23fd1ff7731e9017bd776f49206dc42d70d9fe91`; git-blob SHA-1 (`sha1(b"blob %d\0"+data)`) + SHA-256; файлы удалены после проверки | `0b.top`: 120204 B, blob `84edad43...743e44b`, sha256 `cd046127...aae01f` **MATCH**; `pro_CPU.in`: 933 B, blob `89d76310...c43fa735`, sha256 `bd6cd418...7f5e673` **MATCH** | нет |
| 4 | Cost probe ре-ран (+ проверка engine HEAD) | `wsl git -C /home/yurig/nl1-002/oxdna-src rev-parse HEAD` → `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` ✓; `cost_probe.run_probe(...bin/oxDNA, /home/yurig/verify-nl3-002a-probe, .../DSDNA8, 5000, 'E2A-PROBE-VERIFY-R1')` | `probe_completed: True`, `exit_code: 0`, `stdout_tail: PROBE_OK`; дайджесты фикстуры `dsdna8.top`/`init.dat` совпадают с пинами; выходные дайджесты `probe_last.dat` `4028e5b3...`, `probe_energy.dat` `396f12af...` **бит-идентичны** published probe (E2A-PROBE-S001); wall time 0.137 s (отличается — ожидаемо); probe-каталог удалён | нет (только wall-clock) |
| 5 | Научная стерильность | `git diff ff9e147..HEAD --stat`; `git diff 6190a85..b6e9926 --stat -- project experiments 'docs/evidence/**'` | Нет изменений `experiments/**` и `docs/evidence/**` в обоих диапазонах; нет изменений `project/**` в 6190a85..b6e9926; единственное изменение `project/state.json` (ff9e147..HEAD) — снятие двух resolved `open_decisions` (процессуальное bookkeeping, не experiments/evidence); симуляций источника не запускалось; probe использует engine-owned DSDNA8 (GPL-3.0, права CLEAR per NL0-002), не источник шарнира | нет |
| 6 | Контракты | `PYTHONPATH=scripts python -m harness.work_cli validate docs/work/executions/EX-NL3-002A-R1`; `python -m harness.cli check-consistency` | validate `ok: true` (status HANDOFF_READY, passport sha256 `98545813...a9828`); check-consistency `ok: true` (0 errors, 0 warnings; frontier NL3, head b6e9926, tree `81a8596f...`) | нет |
| 7 | Mapping-санити (пересчёт арифметики из report JSON) | python-пересчёт чисел ассоциации | exact counts `[4,17,2,5,1,1,13,1,1,1,29,16]` сумма **91** ✓; scaffold split `4266 = 51+51+51+60+103+126+126+210+210+210+420+434+434+568+568+644` ✓; merges **19→568** (сумма design_lengths = 568 = topology_length) и **3→126** (35+42+49=126) ✓; unresolved design 36+42+49+49=**176** = unresolved topology 54+61+61=**176** ✓; тоталы **118** design paths (91+1+19+3+4) и **112** strands (91+16+1+1+3), подтверждены длинами списков в отчёте ✓ | нет |

## Расхождения

Материальных нет. Только ожидаемые недетерминированные отличия:
- wall time cost-probe (0.137 с в ре-ране vs published) — явно вне зоны воспроизводимости (wall-clock исключён);
- время выполнения тестов (53.1 с).

## Вердикт

**PASS**

## Claim ceiling

Проверено на exact HEAD `b6e9926` собственным исполнением верификатора: тесты зелёные (227/227, 1 skip), отчёт real-data cross-check байт-воспроизводим через сетевую загрузку по политике G1 decision B download-on-run (без durable-кэша), независимый digest-гейт подтверждает оба проверенных пина на pinned upstream commit, cost probe воспроизводит бит-идентичные выходные дайджесты движка на pinned сборке, контракты валидны, published mapping-арифметика внутренне согласована. Утверждения о научных результатах самих симуляций шарнира **не** покрываются (симуляция источника не запускалась — by design, стерильность pre-E2). Независимость — с оговоркой выше: fresh-сессия, тот же физический хост/исполнитель.
