# NL5-ACCEPTANCE-POLICY/VERIFIER_VERDICT — Fresh independent exact-head verification of EX-NL5-ACCEPTANCE-POLICY-R2 candidate R2

```text
VERIFIER_ID        = NL5-ACCEPTANCE-POLICY/VERIFIER_VERDICT
FRESH_VERIFY       = R1
VERIFY_VERDICT     = VERIFIED
VERIFY_DATE        = 2026-09-30
VERIFIED_SUBJECT   = a9d7d07fa264e9907b67ca244b00ba2da3430b0f
                     (= origin/control/nl5-acceptance-policy-r2, repair R2,
                      «feasibility gate»)
BASE               = 8205781def7179d6bdfa6eb7ab2a84d46776649c (= origin/main,
                     свежий `git fetch --all --prune`; merge-base совпадает)
REVIEW_CHAIN       = f07fe39 (fresh review FAIL @ 51ca09a, 3 MAJOR)
                     → c25bcd6 (review refresh R1 PASS @ 6e5287b, M-2 PARTIAL +
                       R-1..R-5)
                     → 61d8c67 (review refresh R2 PASS @ a9d7d07, R-1..R-5 CLOSED)
REVIEW_BRANCH_HEAD = 61d8c672458568f3ec8759c42d0e8229dbce3e7f
                     (review/nl5-acceptance-policy-r2)
CLAIM CEILING      = C0_SOFTWARE_ONLY — этот вердикт не создаёт научных
                     утверждений, не freeze'ит протокол NANOLAB_REPRO_V0_2 и не
                     объявляет NL5 acceptance; NL5-002 terminal MISMATCH /
                     NOT accepted остаётся каноническим
ROLE               = VERIFIER (fresh independent session; доверяю только Git-фактам
                     и собственным воспроизведённым проверкам; из брифа ничего
                     не принято на веру — включая заявленную топологию review-
                     ветки, см. finding V-1)
```

## 0. Заявление о независимости и метод

Я — свежая verifier-сессия. Каждое измерение ниже выполнено мной mechanically из
git-объектов exact `a9d7d07` (subject-ветка) в чистом detached worktree
(user CONTROL, `core.autocrlf false`, `core.safecrlf true`), либо независимо
воспроизведено (тесты, seed-регенерация, прогон pinned feasibility gate на
закоммиченных R1-данных, jsonschema-валидация). Верdict-файл review-цепочки
прочитан целиком на `61d8c67` до начала проверок; его утверждения проверены, а
не приняты. Полный diff `8205781..a9d7d07` — 20 файлов, +1391/−1.

## 1. Subject binding и фактическая топология (важно)

```text
origin/main = 8205781def7179d6bdfa6eb7ab2a84d46776649c                 — VERIFIED
merge-base(a9d7d07, origin/main) = 8205781def7179d6bdfa6eb7ab2a84d46776649c — VERIFIED
Цепочка subject-ветки: 8205781 → 793459d (START) → 3171564 (candidate R1)
  → ee40984 (continuation) → 51ca09a (handoff) → 6e5287b (repair R1 = candidate R2)
  → a9d7d07 (repair R2 = feasibility gate)                             — VERIFIED
  (parents сверены `git cat-file -p` для всех 9 коммитов истории)
Review-ветка review/nl5-acceptance-policy-r2 @ 61d8c67: 51ca09a → f07fe39
  → c25bcd6 → 61d8c67 — ПАРАЛЛЕЛЬНАЯ ветка от 51ca09a; a9d7d07 НЕ является
  предком 61d8c67 (`git merge-base --is-ancestor` → exit 1 в обоих
  направлениях; merge-base(a9d7d07, 61d8c67) = 51ca09a)                — ФАКТ
  (см. V-1: бриф ожидал «head — потомок a9d7d07»; фактическая конвенция
  проекта — review/verify-ветки висят на reviewed-хеде параллельно control-
  ветке; review-текст сам фиксирует эту конвенцию для f07fe39)
Верdict-файл append-only: текст f07fe39 (21 995 B) — байт-префикс c25bcd6
  (30 574 B), который — байт-префикс 61d8c67 (35 143 B); первичный текст
  review не переписан, refresh-секции только добавлены                 — VERIFIED
Ветка verify/nl5-acceptance-policy-r2 отсутствовала на origin до моего push
  (ls-remote: 0 совпадений)                                            — VERIFIED
```

## 2. Таблица проверок (все выполнены на exact a9d7d07)

| # | Проверка | Команда / метод | Факт | Статус |
|---|---|---|---|---|
| 1 | origin/main = base | `git rev-parse origin/main` | 8205781def7179d6bdfa6eb7ab2a84d46776649c | OK |
| 2 | merge-base = base | `git merge-base a9d7d07 origin/main` | 8205781def7179d6bdfa6eb7ab2a84d46776649c | OK |
| 3 | Diff ⊂ allowed_paths | `git diff --name-only 8205781..a9d7d07` против `passport.json → allowed_paths` (7 паттернов: WO, `EX-…R2/**`, HG-B proposal, candidate doc, `scripts/nl5/**`, tests, WORK_QUEUE) | 20/20 файлов внутри; WORK_QUEUE.md, HG-B proposal, candidate doc, `scripts/nl5/**`, tests, evidence — все в списке | OK |
| 4 | Protected paths | повербанный diff-анализ | `project/state.json`: 0 строк; `project/infra-state.json`: 0; `docs/evidence/NL5-002*`: 0; `docs/research/REPRODUCTION_RULE_V0_1.md`: 0; `docs/control/ENGINE_ENVIRONMENT_R1.md`: 0; release manifests/scientific executions: отсутствуют в diff (единственная модификация существующего файла — WORK_QUEUE, одна строка) | OK |
| 5 | M-1: exclusion 34 | `from nl5.repro_v02_seeds import HISTORICAL_SEEDS_V1` | len = **34**; история blob'а: 51ca09a=19, 6e5287b=34, a9d7d07=34 (файл менялся только в repair R1) | OK |
| 6 | M-1: независимая экстракция | собственный парсер evidence: B-R1 `frozen_seeds.json` (3: 510101/520202/530303), B-R2 `seeds_frozen.json` (12), `PREREGISTRATION_FREEZE_R1.md` S001–S010 (10), reference 201004/202008/203012 (3, сверены в обоих frozen-файлах), E3-reval {204016,205020,206024} (3; подтверждены в `NL4-003/BATCH_REVIEWER_VERDICT.md` §5 и PREREGISTRATION §43), E1 {−200619630, 319832093} (2; подтверждены в `NL2-002/IMPLEMENTER_EVIDENCE.md` + `VERIFIER_VERDICT.md`), bootstrap 902107 (1; PREREGISTRATION «RNG seed 902107 (frozen)») | union = **34**; EQUAL с tool-множеством; missing = ∅; extra = ∅ | OK |
| 7 | M-2: §9.1 пины | чтение candidate doc §9.1 | PAIRED bootstrap: `random.Random(bootstrap_seed_v)`, B = 10 000, quantile = «линейная интерполяция (numpy.quantile default 'linear')»; N = 40 fresh primaries; N_min = 32/8; s_eff = max(s, 0.01°) | OK |
| 8 | M-2: budget + gate | §12 | 200 confirmatory + ≤40 replacement = MAX 240; **MANDATORY FEASIBILITY GATE** two-estimate: оценка-1 DECISION = subsample n=40 pinned paired bootstrap; оценка-2 ADVISORY = √n-экстраполяция из полного n=10-bootstrap; gate PASS ⇔ ratio_1 ≤ 1.0 по обеим primaries; FAIL ⇒ INFEASIBLE → owner без подгонки | OK |
| 9 | M-3: §9.2 приоритеты | чтение | 1. n_valid < N_min → INCONCLUSIVE(v) (controls: n_valid < 8 → INCONCLUSIVE-CONTROLS, ИСКЛЮЧАЮТСЯ из downgrade §9.3); 2. CI90 ⊂ (−margin,+margin) → EQUIVALENT(v); 3. elif CI90 целиком вне полосы → NOT_EQUIVALENT(v) — точная формулировка; 4. иначе → INCONCLUSIVE(v) | OK |
| 10 | M-3: §9.3/§9.4 | чтение | WO-level приоритеты 1–6 (FAILED_TECHNICAL → … → MISMATCH → INCONCLUSIVE); gross control failure = \|d̂_control\| ≥ 1.0·s_eff(control) понижает REPRODUCED → REPRODUCED_WITH_DEVIATION, НЕ создаёт MISMATCH (противоречие R1 устранено явно); §9.4 замкнутый список {DEV-BUILD, DEV-ENV, DEV-TOOLING, DEV-OPS}, вне списка → STOP + новая revision | OK |
| 11 | R-1: HG-B §4.1 | чтение proposal §4.1 | числа присутствуют: 0b ratio 0.124 (subsample) / 0.207 (advisory √n) → FEASIBLE; 32b 1.298 / 0.907 → FEASIBILITY-UNCERTAIN (параметрика review 0.76–0.81); три owner-опции: (i) принять риск, (ii) R3 сузить primary до 0b, (iii) R3 расширить budget; «Пороги/статистика при этом не трогаются» | OK |
| 12 | R-5: WORK_QUEUE sync | `git diff 51ca09a..a9d7d07 -- docs/work/WORK_QUEUE.md` + reconstruction-тест | строка NL5-002 содержит «N=40 primaries/10 controls»; замена ТОЛЬКО фрагмента «N=10/ячейка» → «N=40 primaries/10 controls»: реконструкция «строка@51ca09a + fragment-swap» == строка@a9d7d07 **байт-в-байт** (True); «terminal verified MISMATCH / NOT ACCEPTED», «external_reproductions = 0», NL6-001-блокировка — сохранены | OK |
| 13 | Gate: воспроизведение | бриф-команда: `evaluate(src, {v: rec['bootstrap_seeds'][v] for v in ('0b','32b')}, ['0b','32b'])` | все **18 float-полей бит-в-бит равны** committed `repro-v0-2-feasibility-gate-R2.json` (max abs delta = **0.0e+00**, критерий ≤1e-12 перекрыт); единственное отличие — строковое поле `source` (см. V-2, environmental path, не content) | OK |
| 14 | Gate: числа | там же | 0b: s = 1.5566358620943725, margin = 0.7783179310471863, half_width_n40_subsample = 0.096231551999999, **ratio_subsample = 0.12364041500434719 (0.124) → gate_pass = true**; 32b: s = 1.8776395290783043, margin = 0.9388197645391522, half_width = 1.2190514775000096, **ratio_subsample = 1.298493623106047 (1.298) → gate_pass = false**; advisory: 0b ratio_sqrt = 0.2068032115531955 (0.207); 32b **ratio_sqrt = 0.9069914220095148 (0.907)**; **gate_pass_all = false** | OK |
| 15 | Gate: source pin | `sha256(paired_platform_sensitivity.json)` | 2b0df07deb62add319d8d12f29cde276d0288a38474760b36978f92adb953096 = committed `source_sha256` (и моё воспроизведение дало тот же digest) | OK |
| 16 | Gate: RNG-pinning | `seed_record()['bootstrap_seeds']` | 0b = 323707441, 32b = 1702258603, 11b = 404063983, 53b = 627625019 — ровно те seeds, что поданы в `evaluate` (равны committed record); бит-точное воспроизведение = следствие pinning | OK |
| 17 | Seed record: регенерация | `json.dumps(seed_record(), indent=2) + "\n"` vs committed `repro-v0-2-seed-record-PRE_DATA_R2.json` | **byte-identical** (sha256 файла 8184bd24ddc4365df3e82d6415a6785025036b186a9f1e09ed8d324f420963ae совпал у регенерации и коммита); `record_sha256` = **5c95664485e00069379e962f44b3ba247f00030e02a7375a27d3b4ab441f5a9c** | OK |
| 18 | Seed record: структура | programmatic | exclusion_list_size = **34**; 40 fresh + 4 bootstrap = 44 seeds, все positive int32 (< 2³¹), все уникальны; fresh ∩ exclusion34 = ∅; bootstrap ∩ exclusion34 = ∅; `exclusions_applied` = sorted(tool 34) | OK |
| 19 | Seed record: R1 vs R2 потоки | сравнение committed `…PRE_DATA.json` (R1) и `…PRE_DATA_R2.json` | seed-потоки ИДЕНТИЧНЫ (`seeds` и `bootstrap_seeds` равны как объекты); record_sha256 одинаков (5c956644… — digest не покрывает exclusion list, рост 19→34 поток не изменил); R1 exclusion_list_size = 19 | OK |
| 20 | Вне-tool ре-деривация | raw `hashlib.sha256` (0b/replica-0001, 32b/replica-0010, bootstrap-53b) | 3/3 совпали с record | OK |
| 21 | Тесты full | `python3 -m pytest tests/ -q` | **392 passed** (13.67s) | OK |
| 22 | Тесты seed-tool | `PYTHONPATH=scripts python3 -m pytest tests/test_nl5_repro_v02_seeds.py -q` | **18 passed** (14 seed-тестов + 4 gate-теста: quantile_linear, pooled_sd, half-width shrink, evaluate_variant fields) | OK |
| 23 | check-consistency | `bash CONTROL_DEVELOPMENT.sh --check-consistency` | `ok: true`, `errors: []`, head = a9d7d07, tree = b3b35d566d1a26f970225845a7b4ecf5ce63cb70 (предупреждение «git metadata unavailable» о branch-детекции в detached HEAD — non-blocking) | OK |
| 24 | workflow_lint | `python3 scripts/harness/workflow_lint.py` | `ok: true`; workflows = 1; violations = 0; **blocking = 0** | OK |
| 25 | work_cli validate | `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-ACCEPTANCE-POLICY-R2` | `ok: true`; **HANDOFF_READY**; **has_post_terminal_corrections = true** (events 0005/0006 — CONTINUATION_CHECKPOINT post-terminal corrections, валидный класс); event_types: START → CONT → VALIDATION → HANDOFF → CONT → CONT; passport_sha256 b24b85c6… | OK |
| 26 | jsonschema Draft202012 | `Draft202012Validator` (jsonschema 4.23.0) против `config/control/harness/execution-passport.schema.v1.json` и `work-event.schema.v1.json` | passport: **VALID** (0 ошибок); все **6/6 events: VALID** | OK |
| 27 | Секрет-скан | grep added-строк (`git diff 8205781..a9d7d07 \| grep '^+'`) по api-key/secret/password/token/PRIVATE KEY/AKIA/ghp | **0 совпадений** (+1391 строка просканирована) | OK |
| 28 | Commits | `git log --format` | 6/6 conventional: 4× `control(nl5): …`, 2× `repair(nl5): …`; git-времена монотонны (2026-10-01 00:57:42+10:00 → 02:26:06+10:00), согласованы с UTC event-stamp'ами (+10:00) | OK |
| 29 | Event-цепочка | чтение 6 events | 0001 WORK_ORDER_STARTED 14:56:00Z subject = 8205781 (base) → 0002 CONT 15:04:17Z subject = ee40984 → 0003 VALIDATION 15:04:54Z subject = ee40984 → 0004 HANDOFF_COMPLETED 15:05:37Z subject = ee40984 → 0005 CONT (post-terminal) 15:52:42Z subject = **f07fe39859bcf910f4ae8c95404e7d2f76dbbd02** (полный 40-hex) → 0006 CONT (post-terminal) 16:25:00Z subject = **c25bcd6ff0fbd6a95dfa47a658ab3e04d81d4734** (полный 40-hex); timestamps строго монотонны | OK |
| 30 | Научные границы | diff + тексты | NL5-002 terminal MISMATCH / NOT accepted — сохранён байт-в-байт (п.12) и каноничен; v0.1 envelope immutable (`REPRODUCTION_RULE_V0_1.md` 0-diff; candidate Appendix B «v0.1 (immutable)»; §10 запрет переписывания); PLATFORM_INSENSITIVE frozen R1 — не тронут; external_reproductions = 0 — сохранён; NL6-001 LOCKED — сохранён; `project/state.json` 0-diff | OK |
| 31 | Nothing frozen | тексты | candidate = «CANDIDATE / PRE-DATA / NOT FROZEN» (шапка + freeze status), freeze chain §13 полна (HG-B → Director FREEZE record с регенерацией seed record/34 exclusions/literal search/analyzer pin → fresh Reviewer+Verifier FROZEN → R2 ACTIVE → author leg U1 + external leg U2 → independent analysis) и В ЭТОЙ R1 НЕ ИСПОЛНЯЛАСЬ; вердикт review заявляет то же | OK |
| 32 | Никаких simulations/physics | scan | `scripts/nl5/` = только `repro_v02_seeds.py` (sha256-хеширование) + `repro_v02_feasibility_gate.py` (статистический bootstrap на закоммиченных данных R1); без subprocess/network/engine/physics; новых scientific runs нет; единственное слово «simulated» — docstring о subsample-размере статистической процедуры, не физическая симуляция | OK |
| 33 | Не объявляет acceptance | grep | единственные упоминания «NL5 = ACCEPTED» — условные (HG-B proposal §37: «объявляются ТОЛЬКО при…») или запрещающие (WO §27); нигде acceptance не объявлен | OK |

## 3. Triage findings верификатора

- **V-1 (procedural, зафиксирован как ФАКТ, не дефект контента).** Бриф
  ожидал, что head review-ветки (61d8c67) — потомок a9d7d07. Фактическая
  топология иная: review-ветка `51ca09a → f07fe39 → c25bcd6 → 61d8c67`
  параллельна repair-цепочке `51ca09a → 6e5287b → a9d7d07`; merge-base =
  51ca09a; `merge-base --is-ancestor a9d7d07 61d8c67` → exit 1 (проверено
  дважды, в обоих направлениях). Следствие: **дерево 61d8c67 НЕ содержит
  candidate-R2 контента** (в нём seed-tool с 19 значениями, нет gate-скрипта,
  нет event 0006). Это соответствует конвенции проекта (review-верdictы живут
  на отдельной ветке, подвешенной на reviewed-хеде; refresh R1 сам пишет:
  «f07fe39 — отдельная review-ветка, предком не является и не должен быть»),
  и refresh-секция R2 честно описывает REFRESHED_HEAD = a9d7d07 как внешнюю
  lineage. Все содержательные измерения review R2 о дереве a9d7d07 я
  независимо подтвердил. Все проверки этого вердикта выполнены на **exact
  a9d7d07** (отдельный detached worktree); данный verdict-файл закоммичен на
  verify-ветку от 61d8c67 по той же конвенции.
- **V-2 (cosmetic).** Committed gate evidence `repro-v0-2-feasibility-gate-R2.json`
  в поле `source` хранит абсолютный environmental путь
  (`/home/rdpuser/NanoLab/main/docs/...`) — артефакт машины имплементатора.
  Контент входа пинен `source_sha256` (совпал с sha256 закоммиченного paired
  JSON), воспроизведение бит-точное, integrity не затронута. Рекомендация:
  в будущих evidence — относительные пути.
- **V-3 (факт для протокола, ответ на открытый вопрос брифа).** Event 0005
  `subject_sha` = **f07fe39859bcf910f4ae8c95404e7d2f76dbbd02** (НЕ c25bcd6):
  repair-событие ссылается на review-коммит, вызвавший repair. Event 0006
  `subject_sha` = c25bcd6ff0fbd6a95dfa47a658ab3e04d81d4734 (review refresh R1).
  Чередование «repair → вызвавший его review-коммит» когерентно, оба — полные
  40-hex, work_cli принимает.
- **V-4 (minor staleness, non-blocking).** `summary.md` описывает R1-эпоху
  (§1 «exclusion list 19», §3 «387 passed»; errata §5 фиксирует 19→34 и
  14/388, но числа repair R2 — 18/392 — живут только в event 0006). Канонический
  machine-статус (work_cli HANDOFF_READY, passport без notes) зелёный;
  расхождения — документационная стагнация, не искажение фактов. Правка —
  при следующем touch поверхности.

## 4. Явные утверждения верификатора

1. Subject binding точен: `a9d7d07` — head origin/control/nl5-acceptance-policy-r2,
   потомок base `8205781` = origin/main, линейная 6-коммитная цепочка без
   side-мерджей; diff строго внутри allowed_paths паспорта; protected paths —
   0 строк.
2. Все фиксы review-цепочки фактически присутствуют в дереве a9d7d07:
   M-1 (34 seeds, независимо экстрагированы из 7 evidence-источников, множества
   EQUAL), M-2 (pinned paired статистика, N=40/32, budget 240, mandatory
   two-estimate gate), M-3 (механические §9.2/§9.3/§9.4), R-1 (числа и 3
   owner-опции в HG-B §4.1), R-5 (WORK_QUEUE sync — байт-точный fragment-swap).
3. Feasibility gate воспроизведён мной bit-exact: все 18 float-полей committed
   evidence равны моему прогону с delta = 0.0; 0b 0.124 PASS, 32b 1.298 FAIL,
   advisory 0.907, gate_pass_all = false; вход пинен sha256, RNG-pinned через
   seed record.
4. Seed record: регенерация byte-identical; record_sha256 5c956644… подтверждён;
   exclusion 34 подтверждена независимо (экстракция из evidence = tool-множество);
   все 44 fresh/bootstrap seeds — positive int32, уникальны, пересечения с
   exclusion = ∅; потоки R1- и R2-записей идентичны.
5. Machine-инварианты зелёные: 392/392 и 18/18 тестов; check-consistency ok:true;
   workflow_lint blocking=0; work_cli ok:true HANDOFF_READY
   has_post_terminal_corrections=true; passport + 6/6 events валидны по
   jsonschema Draft202012; секрет-скан 0; conventional commits; timestamps
   монотонны.
6. Научные границы неприкосновенны: NL5-002 terminal MISMATCH / NOT accepted,
   v0.1 envelope immutable, PLATFORM_INSENSITIVE frozen R1,
   external_reproductions = 0, NL6-001 LOCKED — не тронуты нигде (diff + тексты);
   nothing frozen; simulations/physics отсутствуют.
7. Расхождение с брифом ровно одно и оно задокументировано (V-1): review-ветка —
   параллельная, не потомок; это конвенция репозитория, а не дефект пакета.
8. ЭТОТ ВЕРДИКТ: не создаёт научных утверждений; не freeze'ит протокол
   NANOLAB_REPRO_V0_2 и не размораживает его; не объявляет NL5 accepted и не
   меняет NL5-002 terminal MISMATCH / NOT accepted, v0.1 envelope,
   PLATFORM-SENSITIVITY-R1, external_reproductions = 0, NL6-001 LOCKED;
   claim ceiling пакета остаётся C0_SOFTWARE_ONLY. HG-B остаётся отдельным
   owner-решением вне Git (включая пункт §4.1 о FEASIBILITY-UNCERTAIN 32b).

## 5. Вердикт

```text
VERIFY_VERDICT = VERIFIED
```

Обоснование в одну строку: candidate-пакет EX-NL5-ACCEPTANCE-POLICY-R2 на exact
`a9d7d07` точно соответствует заявленному binding'у, содержит все fixes
review-цепочки f07fe39 → c25bcd6 → 61d8c67, воспроизводится бит-в-бит
(pinned gate + seed record), машинно чист (392/392, schemas, lint, валидатор)
и не трогает ни одного канонического научного факта; единственное расхождение
с ожиданиями брифа — параллельная (не дочерняя) топология review-ветки —
зафиксировано как конвенция репозитория и не влияет на содержание верификации.

— Fresh independent Verifier (CONTROL), 2026-09-30
