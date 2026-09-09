# NL1-002 — Независимый VERIFIER verdict (E1-R1)

Роль: независимый VERIFIER (fresh session). Дата: 2026-09-09. Репозиторий: rootfabric/NanoLab.
Метод: свежий клон, detached checkout exact HEAD, все хэши — на байтах, извлечённых из Git через cmd-redirect (`git show`), без PowerShell-пайплайнов; upstream — fetch exact pinned commit в отдельный пустой репозиторий.

## Exact subject верификации

- Ветка: `work/nl1-002-reference-run-r1`. Первый ls-remote на старте сессии: `ec67752d98856383c9c9301ecd0488f40e1c5a7f` (совпадал с ожидаемым `ec67752`). Во время верификации ветка продвинулась: финальный ls-remote — `ec7e3edc83a3434d96222a0a8a94b03f7fa10e23` (коммиты `ea465ac` «record run resource evidence» и `ec7e3ed` «record post-handoff resource evidence checkpoint»). Факт зафиксирован; верификация продолжена от нового HEAD.
- Проверка дельты `ec67752..ec7e3ed`: только `docs/evidence/NL1-002/run-resources/**` (time.log/stdout.log ×4), `docs/work/SESSION_LOG.md` (M), событие `0005-resource-evidence-committed.json` — все в allowed_paths; `ec67752` является предком `ec7e3ed` (merge-base exit 0, history не переписывалась); `experiments/evidence/**` в дельте не менялся (0 diff-путей) — все проверки артефактов/анализа, выполненные на `ec67752`, действительны дословно и перепроверены на `ec7e3ed` (16/16 хэшей MATCH).
- Проверяемый checkout: detached `ec7e3edc83a3434d96222a0a8a94b03f7fa10e23`.
- Base: `71535d00a2e729349eea2337217a2c591ed9317d` — подтверждён предком HEAD (`git merge-base --is-ancestor`, exit 0).
- Engine (по evidence): oxDNA `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`, campaign-бинарь `ffc80b1a7abe2a06bea601ac7f730e26c0e5c09c33a9e8c7c5f7a96a4848579f` (3375976 B); логи прогонов подтверждают `GIT COMMIT: 00dc7fb`, `RELEASE: v3.7`, `COMPILED ON: 09/09/26`.

## Вердикт: **PASS**

Evidence-пакет NL1-002 (EX-NL1-002-R1) в проверенной части консистентен, артефакты байт-точно соответствуют манифестам, observables воспроизводятся committed-скриптом до последнего знака, входы байт-идентичны upstream-блобам pinned commit, scope-дисциплина и claim-ceiling (NOT_EVALUATED, отсутствие self-acceptance) соблюдены. Проверка (f) пересборки engine не выполнялась — NOT_CHECKED (см. Findings).

## Таблица проверок

| # | Проверка | Ожидание | Факт | Результат |
|---|---|---|---|---|
| 1 | ls-remote HEAD ветки | `ec67752…` или новее | старт: `ec67752d98856383c9c9301ecd0488f40e1c5a7f` == ожидаемый; финальный: `ec7e3edc83a3434d96222a0a8a94b03f7fa10e23` (дельта проверена, см. Exact subject) | OK |
| 2 | Fresh clone + detached checkout exact HEAD | HEAD == ls-remote | clone → detached `ec7e3ed…` (после дельты; на `ec67752` проверено до её появления), rev-parse совпал | OK |
| 3 | Ancestry base | `71535d00…` ∈ HEAD | `merge-base --is-ancestor` exit 0 | OK |
| 4a | Scope diff `71535d0..HEAD` | все пути в allowed_paths паспорта | 73 файла; только `docs/work/WO-NL1-002.md`, `docs/research/PREREGISTRATION_E1_R2.md`, `docs/experiments/E1_REFERENCE_REPRODUCTION.md` (M), `docs/work/SESSION_LOG.md` (M), `EX-NL1-002-R1/**`, `docs/evidence/NL1-002/**` (включая post-handoff `run-resources/**`), `E1/E1-R1/**`; программный фильтр по allowed_paths: «no paths outside allowed_paths» | OK |
| 4b | Blob-идентичность control-файлов | state.json/plan.json/config идентичны base | `project/state.json` 66df364e, `project/plan.json` c3e854da, `project-goals.v1.json` c48ac533, `checkpoint-catalog.v1.json` bf7189e1 — identical base/HEAD; путей `project/`, `config/` в diff нет | OK |
| 4c | Отсутствие вендоренных upstream-входов в дереве HEAD | grep `dsdna8|init.dat|quick_input|quick_compare` не даёт входных файлов | единственный матч `docs/evidence/NL1-001/smoke-run/quick_input_smoke` — модифицированный smoke-вход NL1-001 (435 B, steps=1e4, SHA-256 `6c4371c7…`), существовал в base, этим WO не добавлялся, upstream-блобу (533 B, `8935c4bc…`) не равен | OK (см. F2) |
| 5 | Артефакты vs artifacts.manifest.json (4 runs × 4 файла) | SHA-256 + size совпадают для 16 committed-блобов | 16/16 MATCH (log/energy/trajectory/last_conf для S001, P001, P002, P003; извлечение `git show` через cmd-redirect; перепроверено на `ec7e3ed`) | OK |
| 6a | Пересчёт observable committed-скриптом (WSL bash, `analyze_energy.sh` на извлечённых energy.dat) | значения evidence-map | S001: rows=1001, avg_col2=−1.39393635864, delta=−0.01423379720, IN_BAND; P001: −1.37730121179, +0.00240134965, IN_BAND; P002: −1.39389370430, −0.01419114286, IN_BAND; P003: −1.38687945155, −0.00717689011, IN_BAND — все exit=0 | OK |
| 6b | NaN/Inf в energy.dat | 0 | script guard не сработал ни на одном run (exit 3 не возвращался), exit=0 ×4 | OK |
| 6c | Конфигураций в trajectory.dat | 10 | `grep -c '^t = '` = 10 ×4 | OK |
| 7a | Seeds из log.dat vs evidence-map.json | −200619630 / −473348953 / −547126645 / −1610133928 | `INFO: seeding the RNG with` совпадает во всех 4 логах | OK |
| 7b | GIT COMMIT и N в логах | `00dc7fb`, `N: 16` в каждом | `GIT COMMIT: 00dc7fb` ×4; `N: 16, N molecules: 2` ×4; `END OF THE SIMULATION, everything went OK!` ×4; T=0.097717 | OK |
| 8a | Upstream pinned commit | FETCH_HEAD == `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` | rev-parse FETCH_HEAD совпал | OK |
| 8b | `quick_input` (verbatim-вход прогонов) | `8935c4bc623ca96d406429c3c5177901f12540ffe61bcd3299931f0689af74a2` (533 B) | `git show` pinned tree → SHA-256 совпал, 533 B | OK |
| 8c | `dsdna8.top` / `init.dat` | `f1aded90…` (148 B) / `0ff76d54…` (4498 B) | оба SHA-256 и size совпали | OK |
| 8d | `quick_compare` (источник оракула) | `86a8b6ac…` (51 B) | SHA-256 совпал; содержимое verbatim `ColumnAverage::energy.dat::2::-1.37970256144::0.15` | OK |
| 9 | Пересборка engine по ENGINE_ENVIRONMENT_R1 §3 | BUILD_EXIT=0, bin/oxDNA 3375976 B | NOT_CHECKED — по решению диспетчера: пересборка независимо подтверждена в верификации NL1-001; косвенные факты (COMPILED ON 09/09/26, GIT COMMIT 00dc7fb, размеры/флаги в логах) согласуются с claim | NOT_CHECKED |
| 10a | Все JSON парсятся | 0 ошибок | 28 JSON-файлов, ConvertFrom-Json без ошибок | OK |
| 10b | Нумерация событий | runs 0001–0003; execution монотонная | S001/P001/P002/P003: `0001-started, 0002-run-completed, 0003-analysis-completed`; execution: `0001-work-order-started … 0004-handoff-completed, 0005-resource-evidence-committed` — монотонно | OK |
| 10c | Полнота artifacts.manifest.json | sha256+size+producer+storage для 4 файлов × 4 runs | 16/16 полны; run_id манифеста == каталогу; хэши в `0002-run-completed` events == манифестам (16/16) | OK |
| 10f | Post-handoff resource-evidence (дельта `ea465ac`) | time.log == таблице ресурсов; stdout пуст (no_stdout_energy=1) | S001 13.13 s / 6304 KB; P001 11.08 / 6328; P002 11.74 / 6700; P003 12.56 / 6520; все Exit status 0; stdout.log = 0 B ×4 — совпадает с evidence-map.json и IMPLEMENTER_EVIDENCE | OK |
| 10d | Отсутствие self-acceptance | нет ACCEPTED от implementer на NL1-002 | 5 вхождений «ACCEPTED» — все относятся к NL1-001/ENGINE_ENVIRONMENT_R1 (предыдущий, принятый checkpoint) | OK |
| 10e | scientific_outcome = NOT_EVALUATED консистентно | во всех текстах | 23 вхождения NOT_EVALUATED; T1-факт публикуется как execution fact; паспорт E1-статуса: RUN, приёмка → NL2-002 | OK |

## Findings

| ID | Severity | Описание |
|---|---|---|
| F1 | INFO | Рабочая копия `analyze_energy.sh` в Windows-checkout (core.autocrlf=true) получает CRLF и не запускается в bash (`set: pipefail: invalid option name`). Committed-блоб LF-чистый (0 CR-строк) — верификация выполнена по извлечённому блобу. На evidence не влияет; нюанс окружения для будущих Windows-верификаций. |
| F2 | INFO | `docs/evidence/NL1-001/smoke-run/quick_input_smoke` матчится grep-паттерном fixture-входов, но является документированным модифицированным smoke-входом NL1-001 (435 B, steps=1e4; SHA-256 `6c4371c7…` ≠ upstream `8935c4bc…`), присутствовал в base `71535d0` и не добавлялся этим WO. Не вендоринг upstream-фикстуры кампанией E1-R1. |
| F3 | INFO | `passport.json` execution'а остаётся `status: IN_PROGRESS` на handoff-HEAD — согласуется с политикой «state объявляет main; обновление — отдельный control commit при acceptance», дефектом не является. |
| F4 | INFO | Финальный upstream-fetch выполнялся как `git fetch --depth 1 --filter=blob:none` (дважды полный `--depth 1` fetch обрывался по сети: `unexpected disconnect while reading sideband packet`); блобы затем извлечены штатным `git show` из pinned tree, FETCH_HEAD == `00dc7fb9…`. Байт-точность не пострадала; отмечено как метод, не как отклонение evidence. |
| F5 | INFO | Во время верификации ветка продвинулась `ec67752` → `ec7e3ed` (post-handoff публикация производных resource-логов, event 0005). Дельта в allowed_paths, history не переписана, `experiments/evidence/**` не менялся; все проверки перепроверены на финальном HEAD. Вердикт публикуется от `ec7e3ed`. |

Примечание (не finding): SHA-256 пересобранного бинаря не проверялся и проверяться не должен — oxDNA встраивает дату сборки (COMPILED ON), что задокументировано в protocol.json `binary_hash_note`.

## Ограничения верификации

- Пересборка engine (check f) — NOT_CHECKED (перенесена на верификацию NL1-001, где независимо подтверждена).
- Verifier не запускал oxDNA-прогоны и не воспроизводил симуляции — воспроизведён только анализ committed-артефактов (по мандату).
- Frozen-before-run подтверждён порядком коммитов (`1fa43e9` → `5c8774f` (freeze) → `9cc83e8` (pre-run repair) → `ec67752` results) и таймстемпами событий; криптографическое доказательство времени прогона в Git невозможно по природе системы.

## Заключение

Публикуемые execution facts (4/4 прогона COMPLETED; T1 S001 IN_BAND при avg_col2 = −1.39393635864; пилоты P001–P003 IN_BAND; R_confirm = 3 в E1-PROTO-R2) подтверждаются committed-артефактами и независимым пересчётом. Campaign-level scientific_outcome корректно остаётся NOT_EVALUATED (критерий §9 — T1 + все T2, кампания NL2-002). Препятствий для передачи на REVIEWER/Director checkpoint и Human Gate merge нет.
