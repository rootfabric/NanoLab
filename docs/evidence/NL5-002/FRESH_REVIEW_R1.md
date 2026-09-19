# FRESH_REVIEW_R1 — NL5-002 (независимое fresh review цепочки external reproduction)

Review id: `NL5-002/FRESH_REVIEW_R1`
Дата review (UTC): 2026-09-19
Reviewer: fresh independent Reviewer (отдельная сессия; не участвовал в execution, repair, comparison, orchestration этой цепочки; к чатам/сессиям Implementer/Executor/Orchestrator доступа не имеет)
Subjects: ветки `work/nl5-002-a-protocol-freeze-r1`, `work/nl5-002-b-external-run-r1`, `work/nl5-002-c-compare-repair-r1`, `work/nl5-002-b-r2-external-run-r1`, `work/nl5-002-c2-compare-r2-r1` (все от `main @ 48c55b3…`)

```
REVIEW_VERDICT = PASS
REVIEWED_BASE  = 48c55b3c4acdd2264527083e3072757be8bd9ada (main @ origin/main, tree 7aca3577e86b21ed8d22fb2742352fd29c3264dd)
```

Live-freshness: `git fetch origin --prune` выполнен в начале и повторно перед созданием этой ветки; `origin/main = 48c55b3…`; все пять subject-веток: local HEAD == origin HEAD (совпадение попарно, см. §2). Subject не STALE.

## 0. Вердикт

```
REVIEW_VERDICT = PASS
```

Основания (кратко): subject-цепочка точно идентифицирована и линейна; протокол заморожен до данных и после данных не менялся; честный отрицательный результат B-R1 (INCONCLUSIVE + PORTABILITY_FINDING) и честный научный MISMATCH B-R2 (0b, 32b) сохранены как есть; bounded repair v0.1.1 научные числа не менял (`reproduction.expected` карточек byte-identical v0.1.0); мой независимый пересчёт классификации из per-frame данных 12/12 реплик совпал с исполнителем и с C2 (4/4 карты); пороги/envelope нигде не подгонялись (запрет compliance); все findings — process/packaging уровня LOW/INFO, ни один не влияет на научный исход. Merge в `main` остаётся Human Gate; далее — отдельный fresh exact-head Verifier.

## 1. Independence statement

- Reviewer — fresh-сессия: фазы A/B/B-R2/C/C2 не выполнял, repair не выполнял, comparison не выполнял, orchestration не выполнял.
- Все факты ниже получены самостоятельно из живого Git (fetch origin --prune; bare store `.git-store/repo.git` + worktrees) и из ingested evidence; заявленные в ветках результаты НЕ наследовались: классификация пересчитана мною из per-frame углов (`EXTERNAL-*_analysis.json`), манифесты пересчитаны из git-блобов, валидаторы переисполнены локально (§14).
- Мой расчётный инструмент — собственный скрипт (statistics.median по валидным кадрам окна → median-of-3 → включительное envelope-правило), НЕ packaged-код исполнителя.

## 2. Проверка идентичности subject (пункт 1)

| Ветка | HEAD (local == origin) | TREE |
|---|---|---|
| `work/nl5-002-a-protocol-freeze-r1` | `a41c4502a436b4bc3ee5ecf9e015baf44ef8eea5` | `021f496d3aca2ad9f31a0b544698c35d59a907e2` |
| `work/nl5-002-b-external-run-r1` | `10b4deb8847794e95c20bc6597ba9d2526f5ee19` | `bb722fb9391cd956cb45d77de5415958006f33e5` |
| `work/nl5-002-c-compare-repair-r1` | `a1ba5173d7d78fd944da31cc7b5c2c476d423427` | `e474f9e680d96de8414822e7d0f10021dae84d2d` |
| `work/nl5-002-b-r2-external-run-r1` | `a8dfe8ce220c73131e08f4ab806618a2c0400b16` | `0c940f3e3bd7ec2722be454be56d70033d76f01c` |
| `work/nl5-002-c2-compare-r2-r1` | `b0aff56845fd67a4b410db9b2b932ee6b50a5eb5` | `66523e017f970ab7982e5a36acf8e20757281752` |

- Ancestry: `git merge-base --is-ancestor 48c55b3… <branch>` = да для всех пяти.
- Линейность: `git log --merges 48c55b3..<branch>` = 0 у всех; `rev-list --parents` — у каждого коммита ровно 1 родитель (fork-point = 48c55b3); commits: A=3, B=5, C=2, B-R2=5, C2=5. Force-push признаки отсутствуют: опубликованный origin-HEAD байт-в-байт совпадает с локальным, история строго линейна от main.
- Conventional Commits: все 20 коммитов в формате `type(scope): description` (`work(nl5-002-*)`; тип `work` — устоявшийся в репозитории прецедент execution-веток).
- planning-документ `docs/control/NL5_NL8_EXECUTION_PLAN_R1.md` в `main @ 48c55b3` ОТСУТСТВУЕТ и в пяти ветках отсутствует; существует только на `docs/nl5-nl8-execution-plan-r1` (blob `d1159388…`). Ссылки на него в WO корректно понимаются как planning evidence вне canonical main (учтено; см. FR-6).

## 3. Протокол заморожен до данных (пункт 2)

- Факты времени (author dates — авторитетные времена, см. §11):
  - A: START `f440f4c` = 2026-09-18T13:48:42Z; freeze `2108ea7` = 13:53:36Z (WO + Appendix A + шаблон отчёта + mapping); bookkeeping `a41c450` = 13:53:49Z (только `evidence-map.json` + `summary.md`; `git diff 2108ea7..a41c450 -- WO/template` = пусто).
  - B-R1: dispatch `68ae37d` = 13:56:14Z; кампания по отчёту B-R1 13:57:34Z → 00:55:17Z. Freeze (13:53:36Z) < dispatch < данные. ✓
  - C: `a1ba517` = 2026-09-19T01:17:38Z; B-R2: dispatch `b01f3ba` = 01:21:28Z; seeds frozen 02:08:21Z; первые запуски 02:30:08Z. ✓
  - C2: процедура `90e1d80` = 14:17:05Z < packaged analysis 16:22:33Z < terminal ingest 16:52:09Z. ✓
- Mapping не менялся после данных: `WO-NL5-002-A-R1.md` и `EXTERNAL_REPRO_REPORT_TEMPLATE_R1.md` созданы в `2108ea7` и ни одной веткой цепочки больше не менялись (проверено: `git diff 48c55b3..{B,C,B-R2,C2}` по этим путям = NONE; внутри A — см. выше). WO-level mapping (`REPRODUCED / REPRODUCED_WITH_DEVIATION / INCONCLUSIVE / FAILED_TECHNICAL / MISMATCH`) и per-card правило `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` зафиксированы в WO-A до любых запусков.
- WO-C2 (`процедура ниже заморожена ДО публикации per-card классификаций B-R2`) создан в `90e1d80` и после данных не менялся (проверено).

## 4. B-R1 сохранён честно (пункт 3)

- Terminal event `0004-external-run-completed` (`EXTERNAL_RUN_COMPLETED`): 12 реплик исполнены = FAILED_TECHNICAL (терминированы средой на 128k–138.8k шагов, exit codes ненаблюдаемы); scientific_outcome = **INCONCLUSIVE** по frozen таксономии; per-card 0b/11b/32b/53b = INCONCLUSIVE; **WO-level = INCONCLUSIVE + PORTABILITY_FINDING** (root cause: package under-specification — arm manifests, convention docs, detector reference implementation, engine URL, root README отсутствуют в пакете); 74b = N/A NOT_MEASURED (значения не производились, входы не скачивались).
- Evidence не переписана: `docs/work/executions/EX-NL5-002-B-R1/**` не изменялся ни одной последующей веткой (проверено: `git diff 48c55b3..{C,B-R2,C2}` = NONE). Единственная правка на самой ветке B-R1 после terminal — `10b4deb` (JSON syntax: raw TAB в event 0004), semantic content unchanged, оригинальные байты в истории (`82ad7bd`), факт задокументирован в поле `corrections` самого события.
- INCONCLUSIVE не был «улучшен» до PASS: фаза C классифицирована как bounded repair, а не перезапуск той же кампании.

## 5. Repair v0.1.1 не менял науку (пункт 4)

Diff `releases/nanolab-components-v0.1` (main) → `releases/nanolab-components-v0.1.1` (ветка C): 36 новых файлов (v0.1.0 не переписывался). Проверка научных поверхностей по git-блобам:

| Поверхность | v0.1.0 → v0.1.1 |
|---|---|
| `families/dna_hinge/cards/74b.card.json` | IDENTICAL (blob `7d4a3c74…`) |
| `families/dna_hinge/family.json` | IDENTICAL (`839c1a10…`) |
| `reproduction/REPRODUCTION_RULE_V0_1.md` | IDENTICAL (`114aaeb6…`) |
| `reports/evidence/confirmatory-summary.json` | IDENTICAL (`e935fddb…`) |
| `reports/evidence/parametric-summary.json` | IDENTICAL (`08194286…`) |
| `reports/family-report.md` | IDENTICAL (`27554a0f…`) |
| `provenance/source-digests.json` | IDENTICAL (`8d67d941…`) |
| `schema/components/component-card.v1.json` | IDENTICAL (`15d5073b…`) |
| карточки 0b/11b/32b/53b | blob отличается; leaf-level diff = ровно 4 строковых поля на карточку: `reproduction.requires` (добавлен URL/tarball движка), `reproduction.steps` пп.3–5 (ссылки на packaged convention), `reproduction.tolerance_policy` (путь правила «docs/release/…» → «packaged»), `protocol_pins.notes` (overlay-описание конфига). **`reproduction.expected` (включая envelope) byte-identical по всем четырём.** |

Новые файлы v0.1.1 — packaging/docs/convention/tooling: `README.md`, `convention/OBSERVABLE_CONVENTION_V0_1.md`, `convention/analyze_hinge.py`, `convention/nlbl_convention/*` (stdlib reference implementation), `convention/arm-manifest-{0b,11b,32b,53b}.json`, `convention/run_arm_manifest.py`. Проверено independently: все четыре packaged arm-manifest — **byte-identical копии** frozen манифестов NL3 (`EX-NL3-002-PROTO-R1/evidence/arm-manifest-0b.json`, `EX-NL3-002-PARAM-{11B,32B,53B}-R1/evidence/arm-manifest-<v>.json`). `RELEASE_MANIFEST.json` v0.1.1: `sha256 = 88c1f58061f15fde44225900f0577acbf2634d3f4a75fb96a2cedca24fd1bfef` — совпадает с пином dispatch B-R2 (event 0001). Независимый пересчёт манифеста из git-контента: **35/35 non-pyc записей byte-exact (sha256+size)**; 7 pyc-записей — см. FR-3.

## 6. Envelope'ы v0.1.1 == использованные в классификации R2 (пункт 5)

`card_reference.reference_replica_envelope_deg` в `evidence/analysis/campaign_<v>.json` (B-R2) == `reproduction.expected.reference_replica_envelope_deg` карточек v0.1.1 — программное сравнение **4/4 OK** (0b [65.095434789, 67.236579608]; 11b [72.165683993, 74.533109426]; 32b [77.4927314, 79.877463339]; 53b [131.049227687, 135.285186059]). Классификация R2 выполнена по тем же числам, что опубликованы в пакете; подмены envelope нет.

## 7. Независимость исполнителя B-R2 (пункт 6)

- Independence statement в отчёте (§1): delegated fresh subagent; полный список входов = package copy (read-only) + `EXECUTOR_PROTOCOL_R2.md` + `REPORT_TEMPLATE.md` + публичный интернет (прокси) + системные инструменты; явно перечислено недоступное (авторские репозитории/кэши, подсказки, GPU, paid, durable-cache); platform честно зафиксирована как отличная от авторской (Ubuntu 22.04/gcc 11.4 vs WSL2 Ubuntu 24.04/gcc 13.3; `env/environment_fingerprint.txt`).
- Passport B-R2: `executor.isolation` = «вход ТОЛЬКО /home/rdpuser/nl5-002-external-r2/{package,EXECUTOR_PROTOCOL_R2.md,REPORT_TEMPLATE.md}; доступ к NanoLab repo/worktrees/внутренним evidence и отчёту B-R1 запрещён»; `staging_pins_verified: true`; `release_manifest_sha256` = `88c1f580…` (совпадает с веткой C, §5).
- Administrative watcher restart (event 0003, факт 14:03:46Z): только administrative checks; научные подсказки/интерпретации явно отсутствуют; перезапущен исходный скрипт исполнителя без изменений (watcher лишь опрашивает `exit_code.txt` и запускает packaged-анализ); detached-прогоны не пострадали; лог `logs/watcher_recovery_nohup.log` в evidence. Научные пороги/envelope/seeds не затронуты (см. также D2, §12).

## 8. Полнота кампании и дайджесты (пункт 7)

- **12/12 валидных прогонов**: `EXTERNAL-0b-1..3`, `EXTERNAL-11b-1..3`, `EXTERNAL-32b-1R..3R`, `EXTERNAL-53b-1R..3R` — ровно этот набор в `run_output_digests.json` (84 записи = 12 прогонов × 7 файлов: traj.dat, energy.dat, last_conf.dat, log.dat, run_meta.json, stderr.log, stdout.log; uniform, дубликатов нет, все записи с sha256+size+run_id). Exit codes НАБЛЮДАЕМЫЕ: `exit_code.txt` wrapper'ов, 12/12 = 0 (event 0003: 6/6 32b/53b-R прочитаны до завершения 0b/11b; event 0004: 12/12); независимо мною: `engine_exit_code=0` во всех 12 `*_analysis.json`.
- Raw trajectories в Git НЕ попадают — корректно по политике: адресация через `run_output_digests.json` (84) + `artifact_manifest.json` (**427 записей**, {path, sha256, size, producer}); внутренняя консистентность: все 427 путей уникальны; выборочная сверка ingested-байтов с манифестом — совпадение (4/4 проверенных `analysis/EXTERNAL-*_analysis.json` byte-exact; отчёт `EXTERNAL_REPRODUCTION_REPORT.md` sha256 = `5aee793479292eafa6095f91533aca949bfbad596949d19fd7ee8daca910f421` == заявке event 0004).
- `EVIDENCE_SHA256SUMS.txt`: `sha256sum -c` по рабочей копии evidence — **72/72 OK**.
- Wave-1 aborts: `logs/aborted_attempts.json` — 6 записей (`EXTERNAL-32b-1..3`, `EXTERNAL-53b-1..3`, `ABORTED_BY_EXECUTOR_AT_LAUNCH_STRATEGY_CHANGE`, 02:44:22Z, причина: 12-way parallelism → rate ~2.1 steps/s, ETA 26h > 20h kill); эти ID в кампанию НЕ входят (отсутствуют в run_output_digests и analysis); перезапуски — под новыми ID с суффиксом `-R`, те же frozen seeds (reuses нет; правило «DO NOT REUSE A FAILED RUN ID» соблюдено).

## 9. Analysis convention (пункт 8)

- Analysis выполняется packaged-конвенцией v0.1.1 (`analyze_hinge.py` + `nlbl_convention/`), изъятой из пакета исполнителем; `completeness.txt`: все 12 analyze exit=0 + 4 campaign exit=0; валидные кадры в окне: **0b 50/50/50 (200000), 11b 37/37/37, 32b 37/37/37, 53b 37/37/37 (150000)** — совпадает с моим независимым подсчётом из `frames` каждого `_analysis.json`.
- Окна: per-card (0b 200000; остальные 150000) — отклонение N1 от A-R1, оценено в §12 (verdict-инвариантно).
- Классификационное правило в packaged-коде (`nlbl_convention/reproduction_rule.py::classify`) прочитано мною: envelope = [min, max] reference replica medians; MATCH при `ref_lo <= stat <= ref_hi` (включительно); MISMATCH при всех fresh строго по одну сторону; иначе INCONCLUSIVE — соответствует frozen формулировке WO-A и моему пересчёту.
- Эквивалентность packaged-конвенции авторской (использованной для reference envelope'ов) подтверждена frame0 oracle: 4/4 EXACT совпадение с `design.angle_frame0_deg` карточек (`logs/frame0_oracle_summary.json`).

## 10. Независимый пересчёт классификации (пункт 9) — МОИ ЧИСЛА

Метод: из каждого `EXTERNAL-<v>-<r>_analysis.json` взяты `frames[]`; фильтр `valid==true AND angle_status=="OK" AND time<=window`; per-replica median; campaign statistic = median трёх; классификация по включительному envelope карточки v0.1.1 (MATCH: stat внутри; MISMATCH: все 3 строго по одну сторону; иначе INCONCLUSIVE).

| карта | окно | valid frames | мои per-replica medians (deg) | мой median-of-3 | envelope карточки | МОЙ исход | executor (campaign JSON) | C2 comparison.json |
|---|---|---|---|---|---|---|---|---|
| 0b | ≤200000 | 50/50/50 | 68.3897817955 / 69.6002966125 / 67.5862756410 | **68.3897817955** | [65.095434789, 67.236579608] | **MISMATCH** (все 3 строго выше) | MISMATCH (68.389781796) | MISMATCH |
| 11b | ≤150000 | 37/37/37 | 72.2552098670 / 73.5606098140 / 75.3561779500 | **73.5606098140** | [72.165683993, 74.533109426] | **MATCH** (stat внутри, включительно) | MATCH (73.560609814) | MATCH |
| 32b | ≤150000 | 37/37/37 | 75.1801383430 / 74.7130507210 / 76.1006977870 | **75.1801383430** | [77.4927314, 79.877463339] | **MISMATCH** (все 3 строго ниже) | MISMATCH (75.180138343) | MISMATCH |
| 53b | ≤150000 | 37/37/37 | 132.4118851400 / 130.2441728980 / 136.1690877140 | **132.4118851400** | [131.049227687, 135.285186059] | **MATCH** | MATCH (132.41188514) | MATCH |

- Согласование: мой пересчёт == executor == C2 recalc — **4/4**, числа совпадают до 1e-9 (у исполнителя округление до 9 знаков: 68.3897817955 → 68.389781796).
- **WO-level по frozen mapping WO-A** (`MISMATCH`: ≥1 карта MISMATCH, все 3 реплики строго по одну сторону): **MISMATCH** — совпадает с C2 (`wo_level.verdict = MISMATCH`, mismatch_cards [0b, 32b]); REPRODUCED/REPRODUCED_WITH_DEVIATION недоступны (требуют 0b/32b/53b MATCH).
- Направление Separation: 0b — fresh выше reference (68.39–69.60 против envelope ≤ 67.24); 32b — fresh ниже (74.71–76.10 против envelope ≥ 77.49). 11b MATCH впервые (в B-R1 был INCONCLUSIVE из-за portability, не чисел).

## 11. Честность timestamp-errata (пункты 10, часть)

Проверено независимо против author dates коммитов (UTC):

| event | заявленный timestamp | фактическое (author date) | статус |
|---|---|---|---|
| B-R2 0001 dispatch | 2026-09-19T01:20:40Z | 01:21:28Z (`b01f3ba`) | ok |
| B-R2 0002 continuation | 05:10:00Z | 05:53:39Z (`0fb7df0`) | ok |
| B-R2 0003 recovery | 14:20:00Z | **14:12:58Z** (`70f08c7`) | FUTURE |
| B-R2 0004 terminal | 17:20:00Z | **16:52:09Z** (`9556d0f`) | FUTURE |
| C2 0001 start | 14:45:00Z | **14:17:05Z** (`90e1d80`) | FUTURE |
| C2 0002 comparison | 17:55:00Z | **16:55:44Z** (`4cbf913`) | FUTURE |
| C2 0003 handoff | 18:05:00Z | **16:56:13Z** (`9161c95`) | FUTURE |

- Ровно те 5 событий, что объявлены errata (event 0005 на B-R2; секция §6 summary.md на C2), содержат future timestamps; заявленные errata «фактические времена» совпадают с author dates байт-в-байт. Errata append-only, исходные байты в git-истории, содержание событий не менялось. **Errata честная и фактическая точная.**
- Freeze-critical свойство подтверждается фактическими временами: C2 frozen 14:17:05Z ДО per-card данных (16:22:33Z / 16:52:09Z).
- Это процессная ошибка orchestration (оценка времени вместо чтения часов), задокументированная append-only с процессным исправлением (дальнейшие события — `date -u`); научного содержания не касается. Дополнительно см. FR-5 (удаление corrections-события на C2 последующим коммитом).

## 12. Отклонения (пункт 10)

| id | содержание (как заявлено) | моя проверка | оценка |
|---|---|---|---|
| D1 | wave-1 `EXTERNAL-32b-1..3/53b-1..3` остановлены исполнителем 02:44Z при смене launch-стратегии (ETA 26h > 20h kill), перезапуск под новыми ID `-R`, те же frozen seeds, по protocol §9 | `aborted_attempts.json` 6 записей; seeds в перезапусках == `seeds_frozen.json` (32b 174329/285637/396421; 53b 507283/618457/729613); aborted ID вне кампании | процессуальное, научные входы/analysis идентичны; принято |
| D2 | потеря executor-сессии ~05:48Z; watcher умер; административный перезапуск orchestration 14:03:46Z без изменения скрипта | event 0003 (facts+команды); gap в `wait_and_analyze_progress.txt` (последняя строка до 05:48:17Z, следующая 14:03:44Z pending=6); `watcher_recovery_nohup.log`; прогоны detached, не пострадали; научных подсказок нет | процессуальное, принято; science unaffected |
| D3 | warnings/stderr отсутствуют | мой подсчёт: все 16 `*_stderr.txt` в evidence/analysis = 0 байт; все 12 `runs/*/stderr.log` size=0 в дайджестах | подтверждено |
| N1 | per-card окна (0b 200000; 11b/32b/53b 150000) против универсального `t<=150000` из A-R1 | применено окно published-контракта v0.1.1 (0b: «envelope basis: confirmatory 200k basis, 50 frames/replica»); мой sensitivity-пересчёт: 0b при окне 150k → medians 67.570367/69.393552/67.977185, stat 67.977184957 → всё равно MISMATCH; 11b при 200k → stat 72.839262336 → всё равно MATCH. **Классификации и WO-verdict инвариантны к выбору окна**; observable/threshold/envelope не затронуты | допустимое процессное отклонение, verdict-инвариантное; пометить для будущей protocol-revision синхронизации A↔package |
| F-orch1 | RELEASE_MANIFEST.json v0.1.1 пинует 7 `convention/nlbl_convention/__pycache__/*.pyc`, отсутствующих в git-дереве | **подтверждено мною**: манифест 42 записи, из них 7 pyc (`__init__/canonical/hf_canonical/observables/oxdna_conf/oxdna_topology/reproduction_rule .cpython-310.pyc`); `git ls-tree` release — 0 pyc; v0.1.0 манифест — 0 pyc. Следствие: fresh `reproduce.py verify` на git-checkout падает (missing files); в рабочей копии verify проходил (42/42, `logs/verify.json`) и ломается после реимпорта. Мой пересчёт: **35/35 non-pyc записей byte-exact из git-контента** | packaging-дефект, НАУКУ НЕ ЗАТРАГИВАЕТ: все научные поверхности (analyze_hinge.py, arm-manifests ×4 — byte-identical frozen копии, карточки ×5, rule, reports) pinned верно и проверены; кандидат в bounded v0.1.2 (exclude `__pycache__` + генерация манифеста до первого импорта) |
| F1 (executor) | RIGHTS.json `package_version: 0.1.0` при VERSION 0.1.1 | подтверждено мною в ветке C | косметика метаданных; кандидат в v0.1.2 |
| F2 (executor) | echo last_step в completeness.txt — некалиброванная dt-эвристика (t_traj/0.005 = 40000000 вместо шагов 200000) | подтверждено по тексту; гейтом не является: полнота считается packaged analyze_hinge (`frames_valid_in_window`, engine_exit_code) | информационное |
| F3 (executor) | git-транспорт нестабилен → карточный tarball-путь (codeload) с sha256 | разрешён карточкой v0.1.1 (reproduction.requires добавлен именно для этого) | окружение; принято |
| F4 (executor) | последний кадр 148000 при steps=150000 (print interval 4000) — не дефект | подтверждено: frames_in_window = 37 = frames_total | наблюдение |

## 13. 74b unchanged (пункт 11)

- Карточка 74b: blob **идентичен** v0.1.0→v0.1.1 (`7d4a3c74…`), `measurement_status: NOT_MEASURED`, `reproduction.expected: {}`, шаги требуют arm-manifest-v2 WO.
- `family.json` (идентичен в обеих версиях): `74b: NOT_MEASURED (KNOWN_GAP: arm-manifest-v2 pending)`.
- B-R1 event 0004: «74b = N/A NOT_MEASURED (значения не производились, входы не скачивались)»; B-R2 отчёт (строки 71, 300): NOT_MEASURED, значения не производились; B-R2 evidence: 0 файлов с 74b; C2 comparison.json: `74b: NOT_MEASURED / KNOWN_GAP (no values produced)`.
- Значений 74b нет нигде в цепочке. Честный gap сохранён.

## 14. Механические проверки (пункт 13) и claim ceiling (пункт 12)

| Команда | Где | Результат |
|---|---|---|
| `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-002-C2-R1` | worktree `nl5-002-c2-compare` @ `b0aff56` (**без `git pull`**) | **ok=true**, `HANDOFF_READY`, terminal handoff есть, `has_post_terminal_corrections=false`, exit 0 |
| `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | main checkout @ `48c55b3` | **ok=true**, 0 errors / 0 warnings, exit 0 |
| `work_cli validate EX-NL5-002-A-R1`, `EX-NL5-002-C-R1` | соответствующие worktrees | ok=true (статусы STARTED — handoff-записи в WO-виде; ошибок нет) |
| `work_cli validate EX-NL5-002-B-R1`, `EX-NL5-002-B-R2` | соответствующие worktrees | ok=**false** — см. FR-2 (event-словарь вне стандартной схемы валидатора) |

Claim ceiling: во всех пяти паспортах `claim_class = C1_COMPUTATIONAL_REPRODUCTION`, `risk_class = MEDIUM`; WO-level MISMATCH не повышает claims карточек и не поднимает frontier. Canonical main не тронут: `git diff 48c55b3..` по `project/`, `docs/control/`, `docs/work/WORK_QUEUE.md` — пусто для всех пяти веток; `project/state.json` на main: `NL5-002: READY`, `execution.external_reproductions = 0` (до merge — корректно: критерий NL5 данной кампанией НЕ выполнен, disposition C2 §4 это честно фиксирует).

## 15. Честное сохранение MISMATCH и отсутствие threshold tuning (явное подтверждение)

1. **MISMATCH — сохранённый научный результат**: 0b (все 3 реплики строго выше envelope) и 32b (все 3 строго ниже) зафиксированы как MISMATCH в executor self-assessment, в терминальном событии B-R2, в C2 comparison.json/summary.md; disposition открытo: «критерий приёмки NL5 данной кампанией НЕ выполнен; NL5-002 = terminal MISMATCH; external_reproductions остаётся 0; решение — Human Gate». Никакой переклассификации в MATCH/INCONCLUSIVE/REPRODUCED_WITH_DEVIATION нет; мой независимый пересчёт подтверждает исход.
2. **Threshold tuning отсутствует**: (a) envelope'ы карточек byte-identical v0.1.0→v0.1.1 (§5); (b) mapping WO-A не менялся после данных (§3); (c) campaign JSONs классифицированы ровно по карточным envelope'ам (§6); (d) правило в packaged-коде включает строгую directional separation для MISMATCH и включительность для MATCH (§9); (e) MISMATCH явно объявлен «не repairится порогами», автоматический R3 не запущен (C2 summary §4, owner mission §12).
3. **B-R1 INCONCLUSIVE + PORTABILITY_FINDING** сохранён без перезаписи (§4); repair пошёл новым пактом v0.1.1, а не правкой старого.

## 16. Findings (сводка, severity)

| id | severity | сущность | суть |
|---|---|---|---|
| FR-1 | LOW | C2 comparison.json | `integrity_gates.upstream_digest_gates.all_pass=false` противоречит фактическому gate-логу (`upstream_digest_gate.json`: 12/12 строк PASS по обязательным size+blob_sha1; sha256 совпадают с published) и собственному summary C2 («9/9 PASS»). Вероятная причина: булево посчитано по `published_sha256_status=CONTENT_VERIFIED` (6/12 строк). На классификацию/WO-verdict не влияет (пересчитано мною независимо из per-frame данных). Рекомендация: исправить новой errata-записью (не правкой). |
| FR-2 | LOW | B-R1/B-R2 execution records | event_type/actor_role (`EXTERNAL_EXECUTOR_DISPATCHED`, `EXTERNAL_RUN_COMPLETED`, `ORCHESTRATOR`) вне стандартного словаря `work_cli` → generic validate даёт schema-ошибки (COMPLETED_MISMATCH/COMPLETED_INCONCLUSIVE); у B-R1 нет summary.md. Полнота evidence обеспечена passport+events+digests; C2/A/C валидны. Рекомендация: отдельная external-campaign схема или расширение словаря валидатора. |
| FR-3 | LOW (packaging) | v0.1.1 RELEASE_MANIFEST | 7 `__pycache__/*.pyc` запинены, в git-дереве отсутствуют (F-orch1, подтверждено); fresh-checkout verify падает; научные поверхности pinned корректно (35/35 non-pyc byte-exact моим пересчётом). Кандидат в bounded v0.1.2. |
| FR-4 | LOW (packaging) | v0.1.1 RIGHTS.json | `package_version: 0.1.0` при VERSION 0.1.1 (executor F1, подтверждено). Кандидат в v0.1.2. |
| FR-5 | INFO (process, honest) | errata | 5 future-timestamps подтверждены и честно исправлены append-only (§11). Дополнительно: на C2 ранее опубликованное corrections-событие (`d34a4c1`, 0004-timestamp-errata.json) удалено последующим коммитом (`b0aff56`) с переносом содержания в summary.md (причина задокументирована: конфликт с validator-правилом «corrections timestamp ≥ terminal timestamp»; оригинальные байты в git-истории). Пограничное относительно идеала «events не редактируются», но самодокументировано и научно нейтрально. |
| FR-6 | INFO | planning doc | `NL5_NL8_EXECUTION_PLAN_R1.md` отсутствует в canonical main и в пяти ветках; ссылки WO резолвятся только на `docs/nl5-nl8-execution-plan-r1` (planning evidence). Сам WO самодостаточен; учесть при merge-упорядочивании. |
| — | принято | D1, D2, D3, N1, F1–F4 | см. §12; N1 — verdict-инвариантно (мой sensitivity-пересчёт); F-orch1/F1 — packaging-only. |

## 17. Remaining risks

- Научная интерпретация MISMATCH (platform/FP-чувствительность хаотических MD-траекторий при узких 3-репличных envelope) — гипотеза, не вердикт; исследовательская ветка — отдельное решение Human Gate.
- Булевы integrity-флаги в machine-записях (FR-1) и валидаторный словарь (FR-2) стоит привести в порядок до следующей внешней кампании.
- 74b остаётся NOT_MEASURED до arm-manifest-v2 WO (вне NL5-002).

## 18. Вердикт

```
REVIEW_VERDICT = PASS
CLAIM_CEILING  = C1_COMPUTATIONAL_REPRODUCTION (внешнее statement; не поднимает claims карточек)
```

Основания: пять subject-веток точно идентифицированы (HEAD/TREE выше), линейны от свежего `origin/main`, Conventional Commits; протокол и mapping заморожены до данных и не менялись; B-R1 (INCONCLUSIVE + PORTABILITY_FINDING) и B-R2 (terminal EXTERNAL_RUN_COMPLETED, 12/12, научный MISMATCH 0b/32b при MATCH 11b/53b) сохранены честно и без перезаписи; repair v0.1.1 научные числа не менял (byte-identity `reproduction.expected` и всех опорных поверхностей подтверждена поблочно); мой независимый пересчёт из per-frame данных 12/12 реплик совпал с исполнителем и C2 (4/4 карты, до 1e-9); механические проверки (validate C2, check-consistency main) — ok; все findings — LOW/INFO process/packaging, ни один не подрывает научный исход и не требует переклассификации. Merge в `main` остаётся Human Gate; далее — отдельный fresh exact-head Verifier.

*Review evidence: этот файл + живой Git; расчёты воспроизводимы из `docs/work/executions/EX-NL5-002-B-R2/evidence/analysis/*_analysis.json` (блобов ветки `work/nl5-002-b-r2-external-run-r1`) и карточек `releases/nanolab-components-v0.1.1` (ветки `work/nl5-002-c-compare-repair-r1`).*
