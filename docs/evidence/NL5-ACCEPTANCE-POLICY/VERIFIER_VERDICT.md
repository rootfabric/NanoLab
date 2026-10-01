# NL5-ACCEPTANCE-POLICY/VERIFIER_VERDICT — Fresh independent verification of candidate R3 package (EX-NL5-ACCEPTANCE-POLICY-R2)

```text
VERIFIER_ID        = NL5-ACCEPTANCE-POLICY/VERIFIER_VERDICT (fresh verify R3)
VERIFIER_VERDICT   = VERIFIED
VERIFIER_DATE      = 2026-10-01
VERIFIED_SUBJECT   = 290cba6e4be40d3afa91e670ab50e58f7bbd7d35
                     (control/nl5-acceptance-policy-r3, post-repair; tree
                      0d0e171b917441dba9791bf050ab88a914c7f46b — сверен
                      git rev-parse 290cba6^{tree})
REVIEW_CHAIN       = review/nl5-acceptance-policy-r3:
                     846a5a2 (fresh review R3, PASS @ 2c3171e) →
                     fa30772 (review refresh R3.1, PASS @ 290cba6; head)
BASE               = 8205781def7179d6bdfa6eb7ab2a84d46776649c (= origin/main;
                     git fetch --all --prune выполнен в начале сессии)
CLAIM CEILING      = C0_SOFTWARE_ONLY — этот вердикт не создаёт научных
                     утверждений, НЕ freeze'ит протокол, НЕ объявляет NL5
                     acceptance; freeze = отдельная Director-запись после HG-B
ROLE               = VERIFIER (свежая независимая сессия; доверяю только
                     git-фактам и собственным воспроизведённым проверкам;
                     контекст имплементатора и review-сессии не наследовался)
```

## 0. Заявление о независимости и метод

Я — свежая verifier-сессия. Каждый факт ниже проверен механически из git-объектов
либо независимо воспроизведён мной в изолированных worktree:
`verify/nl5-acceptance-policy-r3` @ `fa30772` (review-хвост; verdict-коммит живёт
здесь), `temp-worktree @ 290cba6` (весь candidate-контент), `temp-worktree @
a9d7d07` (scan-дерево для регенерации seed record — ровно та процедура, которая
зафиксирована в протоколе §7 и применена review-сессией). user CONTROL /
`control@nanolab.local`, `core.autocrlf false`, `core.safecrlf true`. Ничего из
брифа и из REVIEWER_VERDICT не принято на веру: каждое число ниже — результат
моей собственной команды. Ветка `verify/nl5-acceptance-policy-r3` отсутствовала
на origin до верификации (`git ls-remote` — пусто).

## 1. Binding и sibling-топология review-цепочки

```text
merge-base(290cba6, origin/main) = 8205781def7179d6bdfa6eb7ab2a84d46776649c  — VERIFIED
родитель 290cba6 = 2c3171e (event 0007); родитель 846a5a2 = 2c3171e          — VERIFIED
⇒ 290cba6 и 846a5a2 — СИБЛИНГИ (оба дети candidate-head 2c3171e)             — VERIFIED
родитель fa30772 = 846a5a2 (refresh-хвост на review-ветке)                   — VERIFIED
корректный repair-scope R3.1 = git diff 2c3171e..290cba6                     — VERIFIED
tree(290cba6) = 0d0e171b…; tree(bc83af2) = 64a861c3…   — совпадают с заявленными в review — VERIFIED
origin control/nl5-acceptance-policy-r3 = 290cba6 (не двигался)              — VERIFIED
```

Сиблинг-топология структурно корректна: review-коммиты живут вне
candidate-цепочки; диапазон `846a5a2..290cba6` действительно содержит артефакт
сиблингства (удаление REVIEWER_VERDICT.md — файла, которого в candidate-дереве
нет), поэтому repair-scope корректно измеряется как `2c3171e..290cba6` —
подтверждаю поправку review-сессии к брифу. Ремонт R3.1 ссылается на review:
subject коммита 290cba6 называет 846a5a2; summary §7 — «post review R3 PASS
846a5a2».

## 2. Таблица проверок (все выполнены этой сессией)

| # | Проверка | Команда / метод | Результат |
|---|---|---|---|
| 1 | Binding merge-base | `git merge-base 290cba6 origin/main` | `8205781` — OK |
| 2 | Scope vs passport | `git diff --name-only 8205781..290cba6` (24 файла) ∩ `allowed_paths` паспорта | 24/24 внутри allowed_paths; out-of-scope = ∅ — OK |
| 3 | Protected paths | тот же diff против `project/state.json`, `project/infra-state.json`, `docs/evidence/**`, v0.1 envelope, REPRODUCTION_RULE, ENGINE_ENVIRONMENT_R2, `experiments/evidence`, `EX-NL5-002-{E,B-R1,B-R2}` | 0-diff по всем — OK |
| 4 | R1/R2 seed records не переписаны | `diff <(git show <intro>:$f) $f` | R1 byte-identical `ee40984`, R2 byte-identical `6e5287b`; `record_sha256 5c956644…` в обоих сохранён; R3 record/n-grid byte-identical `bc83af2` — OK |
| 5 | Repair-scope R3.1 | `git diff --stat 2c3171e..290cba6` | ровно 3 файла: protocol ±2 литерала, summary +11, tests +45 — OK |
| 6 | N-инвариант: protocol §7 | парсинг «0b = 64, 32b = 64, 11b = 10, 53b = 10 → fresh_seed_total = 148» | (64,64,10,10,148) — OK |
| 7 | N-инвариант: protocol §8 | «N = 64 fresh paired replicas», controls N = 10, N_min 51/8 | присутствуют — OK |
| 8 | N-инвариант: protocol §12.1 | grid {40,48,64,80,96,128}, headroom ≤ 0.80, «минимальный проходящий N» | присутствуют; SELECTED_N = 64 — вывод, не константа — OK |
| 9 | N-инвариант: protocol §12.2 | литералы 296 / MAX 356 / ≤ 560 ч | присутствуют; `derive_budget(2,2)` = {296, 60, 356, 560} — OK |
| 10 | N-инвариант: seed record | `variant_counts` {0b:64, 32b:64, 11b:10, 53b:10}; primary_replicas 64; control_replicas 10; fresh_seed_total 148; длины потоков 64/64/10/10 | совпадает — OK |
| 11 | N-инвариант: seeds.py | PRIMARY_REPLICAS=64, CONTROL_REPLICAS=10, VARIANT_REPLICAS 64/64/10/10, FRESH_SEED_TOTAL=148 | совпадает — OK |
| 12 | N-инвариант: freeze_gate.py | PRIMARY_N=64, CONTROL_N=10, N_MIN 51/8, REPLACEMENT 0.20, WALL 560 | совпадает — OK |
| 13 | Литералы «100 fresh» | grep по дереву 290cba6 | отсутствуют; оба «148 fresh» на месте (§7:157, Appendix B:398) — MINOR-1 закрыт — OK |
| 14 | Seed record: регенерация | `seed_record(DEFAULT_ANCHOR, tree_collision_scan=literal_tree_collision_scan(Path('.'), [seed]))` в worktree @ a9d7d07 | **byte-identical** committed JSON; `record_sha256 = eb4ab3f891e17dd2b456a3870ed73b19e39d67bf51109b6cb47ca64524ce476b` — OK |
| 15 | Уникальность/дизъюнктность | программные проверки множеств | fresh 148/148 unique; 34 exclusions ∩ fresh = ∅; bootstrap 4/4 unique; bootstrap ∩ fresh = ∅; bootstrap ∩ historical = ∅ — OK |
| 16 | Skips | сравнение regenerated vs committed + независимый скан | 0b 10 / 32b 11 / 11b 10 / 53b 10 воспроизведены; все 41 skip-литералов присутствуют в a9d7d07-tree, 0 из 148 emitted — присутствуют (источники: R1/R2 records того же потока + 32b idx 25 траекторный артефакт) — OK |
| 17 | Freeze-time scan | `literal_tree_collision_scan(290cba6-tree, 148 fresh, exclude seed-record/protocol paths)` | 0 коллизий — OK |
| 18 | N-grid: source digest | sha256 committed `paired_platform_sensitivity.json` | `2b0df07d…` == `source_sha256` evidence — OK |
| 19 | N-grid: bit-exact | мой прогон `run_n_grid` (committed R1 paired JSON + bootstrap seeds committed R3 record) vs committed `repro-v0-2-n-grid-R3.json` | все числовые/структурные поля bit-exact (|Δ| ≤ 1e-12); единственное различие — строка `source` (абсолютный путь окружения, не числовое) — OK |
| 20 | N-grid: семантика | разбор строк | N=40 FAIL (0.1236/1.2985) и N=48 FAIL честно сохранены; N=64 PASS (0.0714/0.7357) → selected_n=64; N=80/96/128 PASS (0.0192/0.1728); все ratio N=64..128 ≤ 0.80 — OK |
| 21 | Consistency gate: PASS | `freeze_consistency_gate(protocol@290cba6, committed record)` | PASS, failures=[], budget 296+60=356 — OK |
| 22 | Consistency gate: FAIL-направления | те же входы с мутациями | record 0b→10 → FREEZE_GATE_FAIL; protocol literal 40 → FREEZE_GATE_FAIL; budget drift (3 primaries) → FREEZE_GATE_FAIL — OK |
| 23 | Тесты gate/grid: покрытие | чтение `tests/test_nl5_repro_v02_seeds.py` | `test_pass_on_consistent_package` (PASS + пины budget 296/356), `test_fail_on_record_mismatch`, `test_fail_on_protocol_mismatch`; `NGridDeterminismTest` ×4 (constants, determinism, selected_n=64+documented, boundary ≤0.80 включительно) — осмысленные, не self-referential. Единственное направление без unit-теста — budget-drift FAIL (закрыто моим прогоном #22) — OK с остатком (см. §4) |
| 24 | No-accept-risk: протокол | §12.3 + §12.5 | «gate FAIL ⇒ execution = BLOCKED; путь "owner accepts risk…" ЗАПРЕЩЁН; разрешение ТОЛЬКО новой preregistered revision, которая САМА проходит gate»; §12.5 дублирует («без accept-risk обхода») — OK |
| 25 | No-accept-risk: HG-B | grep + чтение §4.1 | accept-risk опция отсутствует; §4.1 = «resolved by declared N-grid search», SELECTED_N = 64 (0b 0.071 / 32b 0.736), запретительный контекст «accepts risk … явно ЗАПРЕЩЁН»; единственные «accept»-вхождения в пакете — принцип NL5 acceptance и запреты — OK |
| 26 | Canonical N-текст | grep HG-B / protocol / WORK_QUEUE / record | «64 paired replicas/platform + controls 10» везде консистентен; в HG-B/протоколе/WORK_QUEUE stale «N=10/ячейка» отсутствует (одно остаточное вхождение в summary §1 — историческое, см. §4) — OK |
| 27 | Full test suite | `python3 -m pytest tests/ -q` @ 290cba6 | **403 passed** — OK |
| 28 | Seed-tool tests | `PYTHONPATH=scripts python3 -m pytest tests/test_nl5_repro_v02_seeds.py -q` | **29 passed** (25 + 4 новых N-grid) — OK |
| 29 | check-consistency | `./CONTROL_DEVELOPMENT.sh --check-consistency` | `ok: true, errors=[]`; head `290cba6`, tree `0d0e171b` — OK |
| 30 | workflow_lint | `PYTHONPATH=scripts python3 -m harness.workflow_lint` | `ok: true`, workflows=1, violations=0, **blocking=0** — OK |
| 31 | work_cli validate | `./CONTROL_WORK.sh validate docs/work/executions/EX-NL5-ACCEPTANCE-POLICY-R2` | `ok: true`, **HANDOFF_READY**, 7 событий, `has_post_terminal_corrections: true` — OK |
| 32 | События 0005–0007 | разбор JSON + `git log` subjects | 0005 subject `f07fe39` (review FAIL @51ca09a), 0006 subject `c25bcd6` (refresh R1 PASS), 0007 subject `bc83af2` (repair R3) — все существуют и корректны по lineage; timestamps строго монотонны 2026-09-30T14:56:00Z → 2026-10-01T01:21:10Z; терминальный HANDOFF 0004 не редактировался (post-terminal corrections append-only) — OK |
| 33 | jsonschema | jsonschema Draft7: passport + 7 events против `execution-passport.schema.v1.json` / `work-event.schema.v1.json` | passport VALID; events 7/7 VALID — OK |
| 34 | Секрет-скан | regex-скан полного diff `8205781..290cba6` | 0 попаданий — OK |
| 35 | Conventional commits | `git log 8205781..290cba6` | все 9 коммитов `control(nl5):`/`repair(nl5):`, автор CONTROL `<control@nanolab.local>` — OK |

## 3. Triage findings review-сессии (моё независимое подтверждение)

| Finding review | Статус @ 290cba6 | Моё измерение | Подтверждение |
|---|---|---|---|
| MINOR-1 (литералы «100 fresh») | CLOSED | grep 290cba6: «100 fresh» отсутствует; §7:157 и Appendix B:398 = «148 fresh»; diff протокола в R3.1 = ровно 2 литерала; gate PASS; record_sha256 eb4ab3f8… неизменен | **ПОДТВЕРЖДЕНО** |
| MINOR-2 (bootstrap seeds R1/R2-эры: {323707441, 1702258603, 404063983, 627625019}) | CLOSED (accepted/documented) | bootstrap = ровно эти 4 значения, byte-identical R1/R2-эре; уникальность и дизъюнктность (к fresh и historical) выполнены; влияние pre-data нулевое (RNG ресемплинга на planning-данных); задокументировано в summary §7 | **ПОДТВЕРЖДЕНО** (задокументированное переиспользование не нарушает letter контракта §7, scan покрывает fresh) |
| MINOR-3 (event 0007 заявлял несуществующие grid-тесты) | CLOSED | event 0007 — append-only historical record (не редактировался — корректная дисциплина); на head-дереве заявленные тесты теперь существуют: `NGridDeterminismTest` ×4 реально проверяют constants/determinism/selected_n=64+documented/boundary-семантику; 29/29 и 403/403 зелёные. Остаток: budget-drift FAIL-направление gate по-прежнему без unit-теста (проверено моим прогоном) | **ПОДТВЕРЖДЕНО** с остатком cosmetic-уровня |
| NOTE (P(EQUIV\|Δ=0) WO-level ≈ 6% на N=64) | SURFACED | текст в summary §7 присутствует с тем же числом; R-3-квантификация честно видна владельцу | **ПОДТВЕРЖДЕНО** |
| Поправка review к брифу (290cba6 — сиблинг 846a5a2; scope = `2c3171e..290cba6`; tests +45, не +23) | — | подтверждаю полностью моими git-измерениями (§1, проверка #5) | **ПОДТВЕРЖДЕНО** |

## 4. Собственные findings верификатора (все — non-blocking, freeze не блокируют)

1. **COSMETIC/stale-нарратив:** `summary.md` §1 («Что сделано») сохраняет
   описание исходного R1-era пакета: «exclusion list 19», «N=10/ячейка (N_min
   8…)», «budget 80+16 runs, wall ≤168ч». Это исторический нарратив первичного
   handoff внутри append-only errata-цепочки: секции §5/§6/§7 того же документа
   фиксируют R2 (40/cell, budget 240), R3 (64/10, 148, budget 356) и R3.1.
   Canonical N-текст во всех действующих поверхностях (протокол, HG-B, WORK_QUEUE,
   record, machine-константы) — 64/10; machine-контракты принуждают. Рекомендация:
   при следующем touch поверхности добавить в §1 пометку «состояние на момент
   R1-handoff, см. errata §5–§7».
2. **COSMETIC:** WORK_QUEUE NL5-002 содержит дубль фрагмента «…(declared grid)
   primaries/10 controls» — уже помечено review R3 как cosmetic; terminal
   MISMATCH/NOT ACCEPTED и вся гейт-цепочка строки сохранены байт-в-байт.
3. **RESIDUAL (от MINOR-3):** budget-drift FAIL-направление
   `freeze_consistency_gate` (primary_variants≠2) не покрыто unit-тестом; направление
   проверено моим прогоном (FREEZE_GATE_FAIL). Рекомендация: добавить тест до freeze.

## 5. Явные утверждения верификатора

1. Binding подтверждён: subject верификации = 290cba6 (tree 0d0e171b…), base =
   8205781 = origin/main, repair-цепочка a9d7d07 → bc83af2 → 2c3171e → 290cba6
   линейна; review-цепочка 846a5a2 (PASS @ 2c3171e) → fa30772 (PASS @ 290cba6)
   корректна, сиблинг-топология подтверждена; ветки candidate и review на момент
   моих проверок не двигались.
2. Все machine-инварианты зелёные (таблица §2, проверки 1–35): scope 24/24,
   protected 0-diff, N-инвариант согласован на 8 поверхностях (64/64/10/10 = 148;
   296+60 = 356; N_min 51/8; headroom 0.80; SELECTED_N = 64), seed record
   воспроизводится мной byte-identical с `record_sha256 eb4ab3f8…`, N-grid
   воспроизведён bit-exact, consistency gate PASS с FAIL на всех трёх классах
   мутаций, 403/403 и 29/29 тестов, check-consistency ok, lint blocking=0,
   work_cli ok HANDOFF_READY, события/схемы/секреты/коммиты чисты.
3. **Non-post-hoc подтверждение (моё, независимое):** confirmatory data кампании
   v0.2 не существуют (PRE-DATA; 0 simulations; единственные «данные» — committed
   HISTORICAL R1 paired medians, чьё planning-использование разрешено миссией).
   Побайтовым сравнением секций candidate-документа я подтвердил: §4 (δ=0.5),
   §9 (decision rule: margin ±δ·s_eff, приоритетная классификация 9.2/9.3,
   downgrade, s_floor, классы 9.4) и §10/11 — **byte-identical** между
   a9d7d07 (финальная R2-база) и 290cba6 (R3.1) — thresholds/δ не менялись в R3;
   §5 (variants) и §6 (observable convention) — byte-identical даже с 6e5287b.
   N изменился не вручную, а механическим выводом pre-declared grid-правила
   (grid + headroom + «минимальный проходящий») на разрешённых planning-данных,
   в консервативную сторону (N 40→64, budget 240→356 runs — дороже-и-надёжнее);
   правило не содержит свободных параметров и воспроизведено мной bit-exact.
   Seeds — детерминированный sha256-поток с pre-declared continuation-правилом;
   честная оговорка review о недоказуемости внутрикоммитного порядка
   «правило-до-вычислений» (текст и результаты grid в одном коммите bc83af2)
   остаётся честной и компенсирована (механичность, отсутствие confirmatory
   данных, совпадение с независимыми оценками review, dispatch-пересчёт §12.3,
   failsafe-gate). Ни δ, ни N, ни seeds, ни variants, ни thresholds не выбраны
   по несуществующим будущим данным.
4. Научные границы не тронуты: `project/state.json`/`project/infra-state.json` —
   0-diff к базе; NL5-002 terminal MISMATCH / NOT ACCEPTED сохранён
   (WORK_QUEUE, байт-в-байт); v0.1 envelope, REPRODUCTION_RULE_V0_1,
   ENGINE_ENVIRONMENT_R2, PLATFORM-SENSITIVITY-R1 evidence, EX-NL5-002-* —
   0-diff; `external_reproductions = 0`; NL6-001 остаётся LOCKED (HG-B §5:
   «не открывает NL6-001 автоматически»); R1/R2 seed records не переписаны.
5. Nothing frozen: candidate = CANDIDATE / PRE-DATA / NOT FROZEN; freeze chain
   §13 не исполнялась; ни один файл пакета не объявляет NL5 ACCEPTED и не
   поднимает claim (claim ceiling пакета C0_SOFTWARE_ONLY; claim у будущей
   кампании — C1, декларативно). Мой вердикт: не freeze'ит, не размораживает,
   не объявляет acceptance; merge = HG-C, HG-B = owner.
6. Замечания review-сессии воспроизведены: числа gate R2-эры (0b 0.124 / 32b
   1.298 / advisory 0.907) консистентны с committed `repro-v0-2-feasibility-gate-R2.json`
   и §12.3-историей; comment bc83af2 «25/402 tests green» — задокументированная
   самим пакетом cosmetic-неточность (факт: 25 seed / 399 full на bc83af2-эпоху,
   29/403 на 290cba6 — мои прогоны).

## 6. Вердикт

```text
VERIFIER_VERDICT = VERIFIED
```

Обоснование в одну строку: candidate R3 @ 290cba6 воспроизведён мной
целиком — binding/scope чисты, N-инвариант согласован на всех поверхностях,
seed record регенерируется byte-identical (eb4ab3f8…), N-grid bit-exact
(SELECTED_N = 64, честные FAIL-строки сохранены), mandatory gate FAIL⇒BLOCKED
без accept-risk, consistency gate PASS/FAIL-семантика подтверждена, 403+29
тестов и весь machine-слой зелёные, научные факты и PRE-DATA/NOT FROZEN статус
не тронуты; findings review R3/R3.1 закрыты или честно задокументированы;
остатки — cosmetic и перечислены в §4. Пакет готов к вынесению на HG-B с позиций
этой верификации. ЭТО ВЕРИФИКАЦИЯ: не создаёт научных утверждений, не freeze'ит
протокол, не объявляет NL5 acceptance, не меняет NL5-002 terminal MISMATCH /
NOT accepted, v0.1 envelope, PLATFORM-SENSITIVITY-R1 FULLY VERIFIED,
external_reproductions = 0, NL6-001 LOCKED; claim ceiling — C0_SOFTWARE_ONLY.

— Fresh independent Verifier (CONTROL), fresh verify R3, 2026-10-01
