# NL1-002 — Независимый Fresh Reviewer Verdict (R2)

**Verdict: PASS**

- Reviewer: независимая fresh-сессия (REVIEWER, R2). Дата: 2026-09-09. Контекст имплементёра не использовался — только Git-факты и документы ветки.
- Reviewed subject: `work/nl1-002-reference-run-r1` @ **`ea465acf27c33c087fab0a4fa54328377c7314a6`** (base `71535d00a2e729349eea2337217a2c591ed9317d` = canonical main c ACCEPTED NL1-001; `git merge-base --is-ancestor 71535d0 HEAD` → exit 0).
- Дельта к R1: коммит `ea465ac` добавляет ровно 8 файлов `docs/evidence/NL1-002/run-resources/<run>/{time.log,stdout.log}` (§4); всё остальное идентично диапазону, проверенному R1-вердиктом (`7b12012`, subject `ec67752`, PASS). Настоящий R2 **не** является продолжением той же сессии: все проверки ниже воспроизведены независимо собственными скриптами (пересчёт SHA-256 из git-blob'ов, механический анализ energy.dat, статистика пилота); вывод R1 PASS подтверждается и расширяется на `ea465ac`.
- Среда ревью: путь `C:\NanoLab\review-nl1-002` и ветка `review/nl1-002-reference-run-r1` заняты worktree R1-сессии (HEAD `7b12012`, чужой gitdir) — R2 выполнен в `review-nl1-002-r2`, ветка `review/nl1-002-reference-run-r2` от exact `ea465ac`. Push на `review/nl1-002-reference-run-r1` невозможен без force (наверху чужой `7b12012`, не входящий в subject-историю) — force запрещён, публикуется новая ветка.
- Campaign-level scientific_outcome остаётся **NOT_EVALUATED**; настоящий вердикт — оценка дисциплины scope/метода/статистики/evidence, не научная приёмка E1.

## 1. Scope и границы (PASS)

- `git diff --name-status 71535d0..ea465ac` → 64 пути; механическая проверка по `allowed_paths` паспорта EX-NL1-002-R1: **64/64 внутри** (WO-NL1-002, PREREGISTRATION_E1_R2, E1_REFERENCE_REPRODUCTION, SESSION_LOG, EX-NL1-002-R1/**, docs/evidence/NL1-002/**, experiments/evidence/E1/E1-R1/**).
- Протокол **E1-PROTO-R1 не изменён**: blob `docs/research/PREREGISTRATION_E1_R1.md` идентичен на base и subject (`e04c6882…` = `e04c6882…`).
- `project/state.json`, `project/plan.json`, policies, `config/control/**` — не в diff (статусы объявляет main; E0–E6 не тронуты).
- `docs/work/SESSION_LOG.md` — append-only (+8/−0). `docs/experiments/E1_REFERENCE_REPRODUCTION.md` — статус NOT_RUN → RUN с явным «campaign-level scientific_outcome = NOT_EVALUATED» (превышения claim нет).
- Upstream-файлы не вендорены: в дереве отсутствуют `dsdna8.top`/`init.dat`/`quick_input`/`quick_compare` как файлы; только дайджесты и команды (правило DOWNLOAD_ON_SETUP соблюдено).

## 2. Протокольная дисциплина (PASS)

- **Verbatim-входы**: `protocol.json input_digests_sha256` = пинам E1-PROTO-R1 §2.2 (4/4); в манифестах всех 4 прогонов те же дайджесты; `modifications: NONE`; правило `git cat-file blob` (не working-tree) задокументировано в protocol.json и events. Независимую сверку с upstream-объектами (fetch pinned commit) делит с VERIFIER — см. §6 NOT_CHECKED.
- **Критерий применён как пререгистрирован**: оракул `ColumnAverage::energy.dat::2::-1.37970256144::0.15` байт-согласован в E1-PROTO-R1 §5.1, protocol.json и `analyze_energy.sh`; колонка/усреднение/полоса не менялись; критерий механический (среднее колонки 2 по всем строкам).
- **Уникальные run ID**: в evidence-дереве ровно `E1-R1-S001, P001, P002, P003`; на base main ID кампании E1-R1 отсутствуют; failed-прогонов нет (failed/excluded = 0) — повторное использование ID исключено. (Строки `E1-R1-S002/S003` в дереве — только иллюстративный пример структуры кампании в docs/control/EXPERIMENT_HARNESS_RU.md; коллизии нет — NOTE-3.)
- **Technical vs scientific**: терминальные события `RUN_COMPLETED` (`0002`, terminal_execution_event=true) не содержат scientific_outcome; scientific_outcome=`NOT_EVALUATED` публикуется только в `0003-analysis-completed`, evidence-map и summaries. Смешения нет.
- **Никаких ACCEPTED/self-acceptance**: все вхождения «ACCEPTED» в добавленных строках diff относятся к статусу NL1-001 из main; паспорта/протоколы/summary статус NL1-002 не повышают (passport status=IN_PROGRESS, implementation summary=IMPLEMENTED/handoff).
- **Статистика по пререгистрации**: pilot ровно 3 (§6.4.1), distinct seeds из log.dat (−473348953 / −547126645 / −1610133928), `counts_toward_evidence=false` в protocol.json/манифестах/evidence-map; повторное использование пилотов как T2 явно запрещено (E1-PROTO-R2 §3). Между-репликационная статистика опубликована полностью (все значения + mean/SD/range), малое n оговорено (§6.3).
- **R_confirm freeze**: `E1-PROTO-R2` superseding **только §6.4**; R_confirm=3 ≥ минимум §6.4.3 (2) — консервативность не снижена; обоснование (SD 0.00833 = 5.6% полосы, 3/3 IN_BAND, ~12 c/прогон) зафиксировано **до** confirmatory кампании NL2-002; полоса §5.1 и семантика §9 R1 не тронуты (blob R1 неизменен).
- **Frozen-before-run**: порядок коммитов `1fa43e9` (START, 10:19:21Z) → `5c8774f` (freeze, 10:23:16Z) → `9cc83e8` (repair S001-event, 10:23:51Z) → `ec67752` (артефакты/terminal/analysis, 10:30:57Z); repair одного пропущенного started-event — отдельным коммитом до прогона, прозрачно задокументирован в самом event. На уровне порядка коммитов гарантия «subject в Git до запуска» выполняется (метки времени внутри событий — см. MINOR-1).
- **Claim ceiling**: публикуются execution facts (C0-дисциплина текстов), потолок кампании C1_COMPUTATIONAL_REPRODUCTION; T1-факт IN_BAND везде сформулирован как execution fact, не acceptance; полный критерий §9 (T1 + все T2) отложен в NL2-002. Превышения claim не обнаружено.

## 3. Консистентность и независимый пересчёт (PASS)

- **SHA-256 артефактов**: 16/16 (4 прогона × log/energy/trajectory/last_conf) извлечены байт-точно из git-blob'ов `ea465ac`; SHA-256 и размер **16/16 MATCH** `artifacts.manifest.json` **и** `0002-run-completed.artifacts_sha256` (двойная сверка).
- **Пересчёт observable** (независимый скрипт ревьюера, math.fsum, полная точность): среднее колонки 2 совпало с опубликованным до всех 11 знаков 4/4; delta от оракула совпала 4/4; |Δ|max = 0.01423379720 ≤ 0.15 → IN_BAND 4/4 (S001 −1.39393635864; P001 −1.37730121179; P002 −1.39389370430; P003 −1.38687945155).
- **Целостность §5.2**: energy.dat 1001 строка (protocol note: 1 initial + 1000 prints; критерий не менялся) и 10 конфигураций trajectory — 4/4; NaN/Inf = 0 — 4/4; seed из log.dat = опубликованному — 4/4; в логах `GIT COMMIT: 00dc7fb`, `END OF THE SIMULATION, everything went OK!`, `N: 16, N molecules: 2` — 4/4.
- **Пилот-статистика пересчитана**: mean −1.38602478921, выборочное SD 0.00832919790, размах 0.01659249251, SD/полоса 0.0555 — 4/4 поля совпадают с evidence-map и E1-PROTO-R2 §1.
- **Ресурсы**: time.log дельты (§4) согласованы с событиями, evidence-map, IMPLEMENTER_EVIDENCE и run-summaries: 13.13 s/6304 KB; 11.08/6328; 11.74/6700; 12.56/6520; Exit status 0 — 4/4; суммарно 48.51 s ≈ «~48.5 c», budget 1 core-hour не превышен.
- **События**: 27/27 JSON-файлов diff валидны; EX-цепочка 0001→0004 монотонна; run-цепочки 0001→0003 × 4; паспорт EX-NL1-002-R1 полностью валиден против `execution-passport.schema.v1.json` (все required, без лишних полей). Конформность остальных JSON схемам — MINOR-2.

## 4. Дельта ec67752..ea465ac — run-resources (PASS, с MINOR-3)

- `git diff --stat ec67752 ea465ac`: ровно 8 новых файлов `docs/evidence/NL1-002/run-resources/<run>/{time.log,stdout.log}`; events/protocol/manifests/analysis/артефакты **не тронуты** — все проверки §2–§3 (включая 16/16 дайджестов и пересчёт средних) выполнены на `ea465ac` и остаются в силе.
- Файлы — **производные evidence** прогонов (raw-вывод `/usr/bin/time -v`, захваченный stdout), не upstream-фикстуры: правило vendoring FORBIDDEN не затронуто; allowed_paths паспорта покрывают `docs/evidence/NL1-002/**`.
- time.log 4/4 совпадают с задокументированными wall/RSS/exit (см. §3); команда в `Command being timed` соответствует задокументированной (`/usr/bin/time -v …/bin/oxDNA quick_input`).
- stdout.log 4/4 пустые (0 B) — согласовано с `no_stdout_energy = 1` и строкой log.dat `0.000  B written to stdout/stderr` (проверено в blob'ах); это осмысленная фиксация факта, не дефект (NOTE-1).
- Дельта адресует NOTE-1 R1 (raw time-output не архивировались) в правильном направлении. **MINOR-3**: на subject `ea465ac` файлы run-resources не включены ни в один манифест/документ (нет ссылок в events/evidence-map/IMPLEMENTER_EVIDENCE/SESSION_LOG — проверено `git grep`). После subject, на work-ветке (`ec7e3ed`, вне данного ревью), появился event `0005-resource-evidence-committed`, процессно закрывающий этот gap.

## 5. Findings

### BLOCKER / MAJOR

Нет.

### MINOR

- **MINOR-1 (метки времени событий; наследован от R1 MINOR-1, на `ea465ac` не устранён):** заявленные `timestamp_utc` систематически не согласуются с датами содержащих их коммитов: `0001-work-order-started` (10:26:00Z) закоммичен в `1fa43e9` в 10:19:21Z; S001 `0001-started` (10:50:00Z) — в `9cc83e8` в 10:23:51Z; `0002/0003/0004` (11:15/11:20/11:30Z) — в `ec67752` в 10:30:57Z. Внутриминутная хронология из событий невоспроизводима и частично противоречит Git; гарантия freeze-before-run подтверждается порядком коммитов (проверяемо), точные declare-минуты считать оценочными. Рекомендация: машинные `date -u` метки в момент записи. Научные результаты не затронуты.
- **MINOR-2 (конформность схем campaign-слоя):** (a) EX-события `0002/0003/0004` используют `subject_sha: "9cc83e8"` — нарушение паттерна `^[0-9a-f]{40}$` схемы `work-event.schema.v1.json` (`0001` валиден; принятый прецедент NL1-001 везде использовал полный SHA); (b) 12 run-событий не соответствуют `experiment-event.schema.v1.json`: отсутствуют обязательные `experiment_id` и `subject_sha`, присутствуют поля вне схемы (`work_order_id`, `command_refs`, `evidence_refs`, `blocker`, `lifecycle_state`, `run_type`, `terminal_execution_event`, `execution_outcome`, `engine_observations`, `artifacts_sha256`, `analysis_tool`, `observable`, `comparison`); (c) 4 × `artifacts.manifest.json` не соответствуют `artifact-manifest.schema.v1.json` и `review-policy.v1.json artifact_reuse_requires`: `artifacts` — map вместо массива, `producer_run` вместо `producer_run_id`, отсутствует per-artifact `subject_sha`; (d) `evidence-map.json` структурно не соответствует `evidence-map.schema.v1.json` (нет `checkpoint`, `claim_class`, `subject_sha`, `changed_surfaces`, `experiment_runs`, `validation`, `artifacts`, `review_verdict`, `scientific_conclusion`, `claim_ceiling`). Смягчение: это первая experiment-кампания в истории репозитория (прецедента нет), provenance прослеживается по существу (producer_run + producer_tool с SHA бинаря + storage + дайджесты; манифесты сами лежат в subject-дереве), научное содержание не затронуто. Рекомендация: в NL2-002 либо нормализовать campaign-файлы к схемам, либо явно ревизовать схемы под campaign-слой (добавив недостающие поля в схемы), не постфактум перекраивая существующие events.
- **MINOR-3 (ссылочная целостность дельты):** run-resources на subject не упоминаются ни одним событием/документом/манифестом (детали в §4); рекомендуется сохранять адресацию нового evidence в event/SESSION_LOG в момент коммита (что и сделано позже в `0005` на work-ветке).

### NOTE

- **NOTE-1:** пустые stdout.log — согласованы с `no_stdout_energy=1` и log.dat (`0.000 B written to stdout/stderr`); проверено по blob'ам.
- **NOTE-2:** `core.autocrlf=true`: рабочие копии evidence-артефактов на Windows отличаются от blob'ов (CRLF; например energy.dat 50050 B в дереве vs 49049 B в blob). Hash-верификация корректна только через `git cat-file`/`git show` (как сделано в этом ревью); наивная сверка Get-FileHash по рабочему дереву даст ложные несовпадения. Рекомендация: `.gitattributes` (`*-dat text eol=lf` или `binary`) для evidence-путей.
- **NOTE-3:** `E1-R1-S002/S003` встречаются в дереве только как иллюстрация структуры кампании в control-документе; реальных run с этими ID нет, коллизии/переиспользования ID нет.
- **NOTE-4 (среда ревью):** ветка/путь R1 заняты чужим worktree; в 21:30:05 внешний процесс выполнил `git reset` ветки R2 на `ec7e3ed` (reflog); ветка возвращена на exact `ea465ac` перед фиксацией вердикта. На вердикт не влияет (все проверки — по blob'ам `ea465ac`).

## 6. NOT_CHECKED (зона VERIFIER, вне reviewer-scope)

- Независимый fetch upstream pinned commit `00dc7fb9` и сверка 4 входных blob'ов с пинами §2.2 (здесь приняты по внутренней согласованности документов/манифестов).
- Пересборка engine по `ENGINE_ENVIRONMENT_R1` §3 и проверка бинаря `ffc80b1a…579f`; физическое повторное исполнение прогонов.
- Время push'ей (публичность freeze на стороне GitHub); сверка wall/RSS с внутренними таймерами engine.

## 7. Claim ceiling и следующее действие

- Публикуются execution facts; campaign-level scientific_outcome = **NOT_EVALUATED**; потолок кампании **C1_COMPUTATIONAL_REPRODUCTION** достижим только по полному критерию §9 R1 (T1 PASS + все T2-реплики в полосе при R_confirm=3) в NL2-002. Настоящий **PASS** — вердикт по evidence-дисциплине NL1-002 @ `ea465ac`; merge в `main` — Human Gate.
- Следующее действие (одно): независимый VERIFIER — fresh checkout `ea465ac` → upstream-пины, пересборка engine, повторение `analyze_energy.sh`, дайджесты → `docs/evidence/NL1-002/VERIFIER_VERDICT.md`; затем Director checkpoint.
