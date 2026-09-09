# NL1-002 — Независимый Reviewer Verdict (R1)

**Verdict: PASS**

- Reviewer: независимая fresh-сессия (REVIEWER). Дата: 2026-09-09.
- Reviewed subject: `work/nl1-002-reference-run-r1` @ **`ec67752d98856383c9c9301ecd0488f40e1c5a7f`** (на момент завершения review `git ls-remote origin work/nl1-002-reference-run-r1` = `ec67752` — ветка не продвинулась в ходе review).
- Base: `71535d00a2e729349eea2337217a2c591ed9317d` (fresh canonical main, ACCEPTED NL1-001); проверено `git merge-base --is-ancestor 71535d0 HEAD` → exit 0.
- Evidence-пакет: `docs/work/WO-NL1-002.md`, `docs/work/executions/EX-NL1-002-R1/**`, `experiments/evidence/E1/E1-R1/**`, `docs/research/PREREGISTRATION_E1_R1.md` (§2.2, §3, §5, §6, §7, §9, §10), `docs/research/PREREGISTRATION_E1_R2.md`, `docs/research/ENGINE_ENVIRONMENT_R1.md`, `docs/experiments/E1_REFERENCE_REPRODUCTION.md`, `docs/evidence/NL1-002/IMPLEMENTER_EVIDENCE.md`, `project/state.json`.
- Campaign-level scientific_outcome остаётся **NOT_EVALUATED**; настоящий verdict — оценка дисциплины design/метода/статистики/evidence, не научная приёмка E1.

## 1. Проверки и результаты

### 1.1 Scope и границы (PASS)

- `git diff --name-status 71535d0 HEAD` → 52 пути, все внутри `allowed_paths` паспорта EX-NL1-002-R1 (WO, PREREGISTRATION_E1_R2, E1_REFERENCE_REPRODUCTION, SESSION_LOG, EX-NL1-002-R1/**, docs/evidence/NL1-002/**, experiments/evidence/E1/E1-R1/**).
- `project/state.json`, `project/plan.json`, policies — **не изменены** (отсутствуют в diff; E0–E6 остаются NOT_RUN, physics_runs=0 — консистентно с правилом «статусы объявляет main»).
- Upstream-файлы (`dsdna8.top`, `init.dat`, `quick_input`, `quick_compare`) **не вендорены**: `git ls-tree -r HEAD` + поиск по именам → единственное совпадение `docs/evidence/NL1-001/smoke-run/quick_input_smoke` — pre-existing артефакт NL1-001 (blob `1c31ab64`, модифицированная smoke-копия; ≠ pinned blob `07eef592`; в этом diff не менялся).
- `docs/work/SESSION_LOG.md` — append-only (+8/−0).

### 1.2 Verbatim-дисциплина входов (PASS, верифицировано против upstream)

- Дайджесты консистентны во всех документах: `protocol.json input_digests_sha256` = пины `E1-PROTO-R1` §2.2 = `inputs` всех 4 run-манифестов (4/4 позиции).
- **Независимая upstream-верификация**: `git fetch --depth 1 origin 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` в probe-clone `lorenzo-rovigatti/oxDNA`; SHA-256 сырых blob'ов, извлечённых `git cat-file blob` + cmd-redirect: 4/4 MATCH пинам §2.2 (размеры 148/4498/533/51 B); blob SHA-1 в pinned tree 4/4 MATCH (`1811af7e`, `856be187`, `07eef592`, `74a088ec`).
- `quick_compare` verbatim: `ColumnAverage::energy.dat::2::-1.37970256144::0.15` — оракул в `analyze_energy.sh` и документах совпадает байт-в-байт.
- `quick_input` (533 B) соответствует расшифровке §3 R1: `steps=1e6`, `print_energy_every=1e3`, `print_conf_interval=1e5`, `thermostat=john`, `#seed`/`#pt` закомментированы и др.
- Заявление modifications=NONE подтверждаемо по evidence: манифесты (4/4 одинаковые дайджесты входов), started-events (команда `git cat-file blob` + sha256sum 4/4 на месте перед прогоном), независимая внутренняя согласованность: начальная строка energy.dat (t=0, U/N=−1.345520) идентична во всех 4 прогонах при различных кинетических колонках — ожидаемая картина verbatim-входов + случайных скоростей (`refresh_vel=1`) по разным seed.
- Полоса/оракул/критерий §5.1 не менялись: `E1-PROTO-R1` отсутствует в diff.

### 1.3 Frozen-before-run (PASS; см. MINOR-1)

- Порядок коммитов: `1fa43e9` 20:19:21 +1000 (START: WO + passport + WO-started event) → `5c8774f` 20:23:16 (freeze: campaign.md, protocol.json, analyze_energy.sh, манифесты + started-events P001–P003, S001 manifest) → `9cc83e8` 20:23:51 (+35 c: пропущенный S001 `events/0001-started.json`, только этот файл) → `ec67752` 20:30:57 (артефакты, terminal/analysis events, R2 freeze, handoff).
- Пропуск S001-event в freeze-коммите починен **отдельным коммитом до запуска прогона** (по заявленной хронологии) и прозрачно задокументирован в самом event (NOTE-поле), IMPLEMENTER_EVIDENCE, summary и SESSION_LOG — требование EXPERIMENT_HARNESS_RU «subject в Git до запуска» на уровне Git-коммитов соблюдено; ремонт аудируем, история не переписывалась.

### 1.4 Целостность артефактов и пересчёт чисел (PASS)

- 16/16 артефактов (4 прогона × log/energy/trajectory/last_conf) извлечены байт-точно `cmd /c "git show HEAD:<path> > file"`; SHA-256 и размер **16/16 MATCH** `artifacts.manifest.json`; дайджесты в `0002-run-completed` events 16/16 консистентны с манифестами; файлы LF-only (CRLF не обнаружен).
- Пересчёт собственным скриптом репозитория `analyze_energy.sh` (WSL bash) на байт-точных `energy.dat`:

| Run | rows | avg col2 (пересчёт) | опубликовано | NaN/Inf | конфигураций | seed из log.dat |
|---|---|---|---|---|---|---|
| E1-R1-S001 | 1001 | **−1.39393635864** | −1.39393635864 ✓ | 0 | 10 | −200619630 ✓ |
| E1-R1-P001 | 1001 | **−1.37730121179** | −1.37730121179 ✓ | 0 | 10 | −473348953 ✓ |
| E1-R1-P002 | 1001 | **−1.39389370430** | −1.39389370430 ✓ | 0 | 10 | −547126645 ✓ |
| E1-R1-P003 | 1001 | **−1.38687945155** | −1.38687945155 ✓ | 0 | 10 | −1610133928 ✓ |

- Независимый пересчёт вторым методом (python3, `math.fsum`) совпал 4/4 с опубликованными значениями до всех 11 знаков; delta от оракула и IN_BAND 4/4 подтверждены.
- Pilot-статистика пересчитана: mean −1.38602478921, выборочное SD 0.00832919790, размах 0.01659249251, SD/полоса 0.0555 — 4/4 совпадают с evidence-map и E1-PROTO-R2 §1.
- Логи всех 4 прогонов: `GIT COMMIT: 00dc7fb`, «END OF THE SIMULATION, everything went OK!», `N: 16, N molecules: 2`.

### 1.5 Критерий, статистика, claim-дисциплина (PASS)

- `E1-PROTO-R2` superseding **только §6.4** (назначение R_confirm); §5.1/§3/§9/§10 R1 наследуются без изменений; полоса и оракул не тронуты.
- R_confirm = 3 ≥ минимум §6.4.3 (2) — консервативность не уменьшена; обоснование использует пилот-факты (SD, 3/3 IN_BAND, стоимость ~12 c) и зафиксировано ДО confirmatory кампании; §5.1 R1 не затронут.
- Запрет повторного использования пилотов как T2 сформулирован явно (R2 §3); пилоты помечены `counts_toward_evidence=false` в protocol.json, манифестах и evidence-map; использование пилот-данных для обоснования R_confirm — разрешённая §6.4 функция пилота, не «превращение в evidence».
- campaign-level scientific_outcome = NOT_EVALUATED проведён консистентно: все 4 `0003-analysis-completed`, evidence-map.json, campaign.md, protocol.json, summaries, IMPLEMENTER_EVIDENCE. T1 IN_BAND везде сформулирован как execution fact, не acceptance; превышения claim не обнаружено (публикуются C0-факты, потолок C1).

### 1.6 События, схемы, ресурсы (PASS; см. MINOR-1, NOTE-2)

- 27/27 JSON-файлов diff валидны (`ConvertFrom-Json`); execution events 0001→0004 монотонны; run events 0001→0003 во всех 4 директориях; terminal event один (`RUN_COMPLETED`, `terminal_execution_event: true`), scientific outcome не смешивается с техническим.
- ACCEPTED от implementer нет: все вхождения «ACCEPTED» относятся к статусу NL1-001 из main.
- Elapsed/RSS согласованы между событиями, run-summary, evidence-map и IMPLEMENTER_EVIDENCE (13.13 s/6304 KB; 11.08/6328; 11.74/6700; 12.56/6520; суммарно ~48.5 c ≪ 1 core-hour budget; stop conditions не активированы; failed/excluded = 0).

## 2. Findings

### BLOCKER

Нет.

### MAJOR

Нет.

### MINOR

- **MINOR-1 (transparentность времени событий):** заявленные `timestamp_utc` событий систематически не согласуются с временем Git-коммитов, их содержащих. Примеры: `0001-work-order-started` (10:26Z) закоммичен в `1fa43e9` в 10:19:21 UTC; S001 `0001-started` (10:50Z) закоммичен в `9cc83e8` в 10:23:51 UTC; `0002-run-completed` (11:05Z) и `0004-handoff-completed` (11:30Z) содержатся в `ec67752`, закоммиченном в 10:30:57 UTC. По заявленным временам P001 стартовал (10:41Z) раньше S001 (10:50Z), хотя WO перечисляет T1 первым (порядок протоколом не mandate — нарушений нет, но это ещё один признак ручного ввода времён). Вывод: внутриминутная хронология кампании из событий невоспроизводима и частично противоречит Git; claim «subject в Git до запуска» подтверждается на уровне порядка коммитов (проверяемого), но точные declare-минуты следует считать оценочными. Рекомендация: генерировать `timestamp_utc` машиной (`date -u`) в момент записи события. На научные результаты не влияет (артефакты/дайджесты/анализ воспроизводятся независимо).

### NOTE

- **NOTE-1:** сырые выводы `/usr/bin/time -v` не заархивированы как артефакты (wall/RSS присутствуют как цитаты в `command_refs` событий). Значения кросс-документно согласованы; рекомендуется в NL2-002 сохранять raw time-лог в artifacts.manifest.
- **NOTE-2:** двухкоммитный freeze (пропуск S001-event в `5c8774f`, ремонт `9cc83e8`) — задокументирован честно и не ослабляет гарантию subject-in-Git до запуска; учитывать при подготовке NL2-002 (чек-лист START-коммита).
- **NOTE-3:** energy.dat не имеет заголовка; семантика колонки 2 = U/N подтверждена ссылкой `ENGINE_ENVIRONMENT_R1` §6 (OBSERVED-in-source), критерий от интерпретации не зависит (механическое правило §5.1) — корректная обработка ASSUMED→подтверждено без изменения критерия.
- **NOTE-4:** в пересчитанных артефактах начальная строка (t=0) идентична по позициям во всех 4 прогонах при разных скоростях/seed — косвенное подтверждение verbatim-входов и заявленной seed-политики.

## 3. NOT_CHECKED (вне reviewer-scope, передаётся VERIFIER)

- Пересборка engine из pinned commit `00dc7fb9` и воспроизведение/проверка SHA-256 бинаря `ffc80b1a…579f` — **NOT_CHECKED** (зона VERIFIER per WO-маршрут; текстовые факты логов проверены).
- Физическое повторное исполнение прогонов и проверка на campaign-машине — **NOT_CHECKED** (невозможно и не требуется для reviewer; прогоны не запускались).
- Время push'ей (публичность freeze до прогона на стороне GitHub) — **NOT_CHECKED** локально; проверен порядок коммитов.
- Сверка цитируемых wall/RSS с engine-внутренними таймерами — **NOT_CHECKED** (второстепенно; внутренние I/O-статы в логах присутствуют).

## 4. Claim ceiling

Публикуются execution facts (C0-дисциплина). Потолок кампании: **C1_COMPUTATIONAL_REPRODUCTION** — достижим только по полному критерию §9 R1 (T1 PASS + все T2-реплики в полосе) в NL2-002 с R_confirm=3. Настоящий PASS — вердикт по evidence-дисциплине NL1-002, не научная приёмка E1; merge в `main` — Human Gate.

## 5. Следующее действие (одно)

Независимый VERIFIER: fresh checkout `ec67752d98856383c9c9301ecd0488f40e1c5a7f` → перепроверка дайджестов артефактов и upstream-пинов, пересборка engine по `ENGINE_ENVIRONMENT_R1` §3, повторение `analyze_energy.sh` → `docs/evidence/NL1-002/VERIFIER_VERDICT.md`; затем Director checkpoint.
