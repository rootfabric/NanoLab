# Fresh Verify — NL5-001-C (EX-NL5-001-C-R1): clean release reproduction

- **Verifier:** fresh independent VERIFIER (новая fresh-сессия; implementation/прогоны/анализ/review subject не выполнял, доступа к чатам Implementation/Reviewer не имел, чужие PASS не наследовал)
- **Дата verify:** 2026-09-17 (окно верификации 03:05–03:30 UTC)
- **Метод:** exact-head верификация — fresh detached worktree от exact subject, полные репозиторные проверки локальным эквивалентом hosted CI, выборочный независимо-вычисленный пересчёт результатов по raw-артефактам, negative controls, инварианты
- **VERIFY_VERDICT: PASS**

## Verdict

**PASS.** Subject идентифицирован точно (branch HEAD == remote HEAD == analyzed subject, tree идентичен, base — предок). Все 5 репозиторных проверок выполняются на этом subject с exit 0. Независимый пересчёт 4 реплик (по одной на вариант, в том числе не использовавшиеся reviewer'ом для frame-level таблицы) на живых raw-артефактах воспроизвёл published медианы с max Δ = 1.075e-10 deg ≤ 5e-10 (допуск round-9 публикации). Классификация воспроизведена вызовом frozen `classify()` для всех 4 вариантов: 3 MATCH + 1 INCONCLUSIVE, envelope/medians == карточкам. Evidence integrity: manifest spot-check 60/60 (включая 12 траекторий) sha256+size подтверждён, 112/112 файлов на месте; download-гейты 12/12 PASS; run-reports 12/12 exit=0 без budget abort. Оба negative controls сработали (детекторы выявляют внесённую порчу). Инварианты соблюдены; remote ref не двинулся. Findings — только observations, на classification facts не влияют.

## Exact subjects

| что | значение |
|---|---|
| Verified head (subject) | `work/nl5-001-c-clean-reproduction-r1` @ `b056db27a6cb9471f75fed33f0f7e062ecf6d3cc` |
| Verified tree | `7f786516ad2e180984fb370ff4cdf708d24668ea` (= tree of `origin/work/nl5-001-c-clean-reproduction-r1^{tree}` после `git fetch` 2026-09-17T03:10Z) |
| Base | `main` @ `6577f8bb5fcf5f97ad40fadfdbbc34e9f0c970fc`; `git merge-base --is-ancestor` → ok (предок head) |
| Remote refs (fetch 03:10Z, повторная сверка в конце верификации — без изменений) | `origin/work/nl5-001-c-clean-reproduction-r1` = `b056db27a6cb9471f75fed33f0f7e062ecf6d3cc`; `origin/main` = `6577f8bb5fcf5f97ad40fadfdbbc34e9f0c970fc` (не двинулся); `origin/review/nl5-001-c-r1` = `96975d13e198a96ef0cb854e31275d4475cb91ab` |
| Tree diff worktree ↔ origin-ветка | пуст (детач-чекаут чист, `git status --porcelain` пуст) |
| Rule | `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` (`docs/release/REPRODUCTION_RULE_V0_1.md`, FROZEN BEFORE DATA; `scripts/release/reproduction_rule.py`) |
| Raw artifacts (вне Git, read-only) | `/home/rdpuser/nl5-001-c-env/run-EX-NL5-001-C-R1/` (1.2 GB, 12 run-каталогов) |

Методическая заметка: при `git --git-dir=<store> rev-parse HEAD` символ `HEAD` резолвится в HEAD главного worktree (main), поэтому все сверка выполнялись по явным SHA и через собственный gitfile detached-чекаута.

## Checks (локальный эквивалент hosted CI, реальные exit codes)

Hosted CI на этот subject не запускался (PR не создавался; ветка не через PR-маршрут) — ниже полный локальный эквивалент всех 5 шагов `.github/workflows/hosted-ci.yml` на exact head, все exit 0:

| Check | Команда | Результат | Exit |
|---|---|---|---|
| 1/5 JSON syntax | логика CI: `git ls-files '*.json'` → `python3 -m json.tool` для каждого; 4 pinned non-JSON evidence пути — сверка sha256 пинов | 1062 tracked JSON: все parse OK; 4 pinned non-JSON fixtures sha256 совпали; 0 fails | 0 |
| 2/5 consistency | `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | ok | 0 |
| 3/5 work events | `work_cli validate` для КАЖДОГО из `docs/work/executions/EX-*` | 37/37 каталогов OK (включая `EX-NL5-001-C-R1`) | 0 |
| 4/5 workflow NC lint | `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | workflows=1, violations=0, blocking=0 | 0 |
| 5/5 unit tests | `python3 -m unittest discover -s tests -t .` | **Ran 360 tests — OK** (11.3s) | 0 |

## Независимый пересчёт результатов (главная проверка)

Метод: **собственный скрипт верификатора** (окно/гейты/медиана/сравнение реализованы независимо, НЕ копия `tools/analyze_all.py`), использующий только frozen-примитивы `scripts/e2/observables.py` (`iter_frames`, `reference_pairs_v2`, `hinge_angle`, `pairs_fraction_v2`, `bonded_integrity`, `displacement_max`) + `hinge_family.oxdna_topology.Topology` на exact head; frozen arm manifests из EX-NL3-002-*; параметры окна/гейтов взяты из текста WO (`t<=150000`, lbf≤0.1078, pf_v2≥0.50, disp≤20.0); медиана — собственная реализация (n=37 → 19-й элемент отсортированного списка). Выбраны реплики, которые reviewer НЕ использовал для своей frame-level таблицы: **0B-S002, 11B-S003, 32B-S002, 53B-S003** (по одной на вариант). Seeds каждой реплики сверены с frozen WO. Допуск: |verifier − published| ≤ 5e-10 (published округляется до 9 знаков, frozen round-9).

| variant | run_id | seed | frames tot/win/valid | verifier median (полная точность, deg) | published (deg) | Δ | Итог |
|---|---|---|---|---|---|---|---|
| 0b | NL5-001-C-0B-S002 | 157480 | 50/37/37 | 67.279863513981113 | 67.279863514 | 1.889e-11 | PASS |
| 11b | NL5-001-C-11B-S003 | 456410 | 50/37/37 | 75.636625462991105 | 75.636625463 | 8.896e-12 | PASS |
| 32b | NL5-001-C-32B-S002 | 801667 | 37/37/37 | 78.096569928892464 | 78.096569929 | 1.075e-10 | PASS |
| 53b | NL5-001-C-53B-S003 | 175554 | 37/37/37 | 132.57559044203413 | 132.575590442 | 3.413e-11 | PASS |

- **4/4 медианы воспроизведены, max Δ = 1.075e-10 ≤ 5e-10.**
- Frame-level spot-check: по 6 in-window кадров на реплику (позиции 1, 5, 10, 20, 30, 36; t = 8000…148000) — angle_deg, valid-флаг: **24/24 совпадений с published frames (Δ = 0 при round-9)**.
- Счётчики кадров воспроизведены (50 total → 37 in-window → 37 valid для 0b/11b; 37/37/37 для 32b/53b); `input.in seed == input-build.json seed` для всех 12 (см. Invariants).
- Корреляция с review: мои 4 значения совпадают с независимыми значениями reviewer'а до последнего знака (напр. 11B-S003 75.636625462991105 у обоих; reviewer max Δ 4.61e-10 по 12/12 — согласуется с моим max Δ 1.075e-10 по 4/4).

## Classification check (4/4)

Вызов frozen `classify()` из `scripts/release/reproduction_rule.py` (reference medians — из карточек `releases/nanolab-components-v0.1/families/dna_hinge/cards/<variant>.card.json`; fresh medians — из трёх published `NL5-001-C-*-analysis.json` каждого варианта):

| variant | classify() исход | campaign stat (deg) | envelope (deg) | envelope == карточка [min,max] | published classification | Согласовано |
|---|---|---|---|---|---|---|
| 0b | MATCH | 66.159296437 | [65.095434789, 67.236579608] | да | MATCH | да |
| 11b | INCONCLUSIVE | 75.514562357 | [72.165683993, 74.533109426] | да | INCONCLUSIVE | да |
| 32b | MATCH | 78.096569929 | [77.4927314, 79.877463339] | да | MATCH | да |
| 53b | MATCH | 132.575590442 | [131.049227687, 135.285186059] | да | MATCH | да |

- **4/4 классификаций воспроизведены: 3 MATCH + 1 INCONCLUSIVE**; reason-строки `classify()` совпадают с published; `card_reference` в classification-*.json deep-consistent с карточками.
- 11b INCONCLUSIVE — корректный промежуточный исход frozen правила: campaign stat 75.514562357 > ref_max 74.533109426 (вне envelope), но S002 72.834291464 < ref_max → полной directional separation нет → ровно INCONCLUSIVE, сохранён честно (не подтянут к MATCH, не объявлен MISMATCH).
- Дополнительно: таблица `summary.md` сверена с 12 published-анализами и 4 classification-записями — 4/4 согласовано (медианы, campaign stat, envelope, outcome).

## Evidence integrity

- **artifact-manifest.json** (112 записей, missing: none — подтверждено обходом всех путей на диске: 112/112 присутствуют): выборочная сверка sha256+size **60/60 OK**, включая **все 12 траекторий** (`*_traj.dat`), `*_last.dat`, `*_energy.dat`, `*_log.dat`, per-run JSON/txt каждого из 12 run-каталогов. Пример: `NL5-001-C-0B-S001/s001_traj.dat` sha256 `292b194820bd17346607e2a52348559f022531e0bdc00517990d6f236492f005`, size 114706021 — совпадает с живым файлом.
- **input-download-verification.json**: upstream `gauravarya77/DNA-hinge-simulations @ 23fd1ff7731e9017bd776f49206dc42d70d9fe91`, pin_source = пакетный `provenance/source-digests.json`, `durable_cache = false` (каталогов кэша в run-root нет) — **12/12 файлов `digest_gate=PASS`** (size_match=true + blob_sha1_match=true; для CONTENT_VERIFIED пинов sha256 сверен).
- **run-reports.json**: **12/12 `exit_code=0`, `budget_abort=false`** (wall-clock 35.8–50.7 ks < 20h kill-лимит); `engine_exit_code=0` подтверждён и в published-анализах.

## Negative controls (disposable-копии в /tmp, репозиторий и raw-артефакты не менялись; команды сами возвращают 0, «ожидаемый отказ» — это срабатывание детектора внутри)

- **NC-A (порча классификации):** disposable-копия `classification-11b.json` с изменённой одной цифрой `campaign_statistic_deg`: 75.514562357 → 75.514562957, затем повторная сверка с независимо пересчитанным `classify()` (fresh medians из 12 published-анализов + карточка 11b):
  `python3 /tmp/nl5-verify-ci/negctl_negctl.py` → `NC-A: tampered ... -> 75.514562957; recomputed classify()=75.514562357; discrepancy detected=True` — **расхождение выявлено**.
- **NC-B (подмена seed в input-пине):** disposable-копия `NL5-001-C-0B-S002/input-build.json` с seed 157480 → 157481, проверка против frozen seeds WO (0b: [170085, 157480, 561483]) и reference seeds [201004, 202008, 203012]:
  та же команда → `NC-B: tampered seed 157480 -> 157481 (WO frozen 157480); seed-vs-WO check fails=True; detector fired=True` — **нарушение выявлено**.
- Итог: `NEGATIVE_CONTROLS: PASS (both tamper detectors fired as expected)`; после контролов `git status --porcelain` worktree — пуст (порча только в /tmp).

## Invariants

- **74b NOT_MEASURED:** card `74b.card.json` `measurement_status=NOT_MEASURED` на head; в run-env и evidence нет ни одного 74b-артефакта (glob `*74*` пуст); правило 74b не классифицирует.
- **Reference seeds не использованы:** 12/12 `input.in` и `input-build.json` содержат frozen fresh seeds WO; пересечений с reference [201004, 202008, 203012] — 0; `input.in seed == input-build.json seed` 12/12.
- **Diff base..head только в allowed paths:** 34 файла, все под `docs/work/WO-NL5-001-C-R1.md` и `docs/work/executions/EX-NL5-001-C-R1/**`; вне — 0 файлов.
- **Canonical не тронут:** `git diff base..head -- releases/ docs/research/ project/ docs/release/ scripts/` — пуст (карточки, rule, observables, состояние проекта идентичны base).
- **Remote ref не двинулся:** повторная сверка после fetch в конце верификации — `origin/work/nl5-001-c-clean-reproduction-r1` == `b056db2`, `origin/main` == `6577f8b`.

## Corroboration

- **Fresh Reviewer:** `review/nl5-001-c-r1` @ `96975d13e198a96ef0cb854e31275d4475cb91ab`, `docs/evidence/NL5-001-C/FRESH_REVIEW_R1.md`, REVIEW_VERDICT=PASS; независимый пересчёт всех 12 реплик, max Δ 4.61e-10; мои независимые значения на пересекающихся объектах (4 медианы, frame-level spot-checks, классификации) совпали с reviewer'ом.
- **Hosted CI:** на этот subject **не запускался** (PR не создавался, push-маршрут на main не задействован) — все 5 проверок выполнены мной локально как эквивалент (см. Checks), на exact head, с реальными exit codes.
- **Междокументная согласованность:** summary.md ↔ 12 analyses ↔ 4 classifications ↔ карточки ↔ WO seeds — всё сходится (4/4, 12/12, 12/12).

## Independence caveat

Verifier выполнен в одной fresh-сессии на той же машине/окружении, где шла implementation (тот же хост, те же локальные копии raw-артефактов). Независимость обеспечена процедурно: fresh checkout exact head, собственные скрипты пересчёта (не копии tools/), доступ только к опубликованным durable-записям и raw-файлам, без доступа к чатам. Полная средовая независимость (отдельная машина/репликация прогонов с нуля) этим verify не заявляется.

## Открытые пункты (не влияют на verdict)

1. Интерпретация 11b INCONCLUSIVE — за Human Gate; любые дополнительные реплики только через новый protocol revision.
2. 11 replica-анализов + 4 classification не пересчитывались мной из raw-потоков напрямую (кроме 4 целевых реплик) — они покрыты review-пересчётом 12/12, согласованностью записей и integrity-проверками.

---

**VERIFY_VERDICT = PASS**
