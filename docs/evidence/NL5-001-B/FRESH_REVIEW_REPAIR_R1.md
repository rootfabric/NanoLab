# Fresh Reviewer R1 — NL5-001-B Repair R1.2 / Clean Integration Re-review

## Verdict

**PASS**

Роль: Fresh Reviewer (re-review repaired subject). Эта сессия не выполняла implementation
`WO-NL5-001-B-REPAIR-R1` и не наследует вердиктов предыдущего review. Independence
caveat: fresh role/session, но тот же GitHub installation/account; actor identity не
является доказательством независимого executor identity (см. HARNESS_REVIEW_AND_EVIDENCE_RU).

Scientific conclusion предмета не меняется: `NOT_EVALUATED`, claim ceiling
`C0_SOFTWARE_ONLY` — это software/release-contract subject, физика не запускалась.

## Exact subjects

- subject head (reviewed): `a9950dc87760986a2987a7b61131a417243a8c2b`
- subject tree: `8b2e96339e7a91feb67683d33caefa0d5c8598b2`
- base: `9de094c8d423574568e62832854664b577e9f282` (main после merge PR #39 + квантов #37/#40)
- branch: `work/nl5-001-clean-integration-r1` (clean integration rebuild, event `0004-clean-integration-rebuild`)
- PR: #41 (`repair: NL5-001-A/B/R1.2 clean integration candidate (a9950dc)`), draft, head/base сверены через GitHub API
- hosted CI: run `35090409941` (workflow `hosted-ci`, event `pull_request`) на exact head `a9950dc` — completed success; шаги Check 1/5..5/5 — все success
- предок repaired-стека (handoff): `66e2270d07b2e7936257dfe2c028f65746e4048f` = parent of `a9950dc`
- старый stacked subject: `dc3063b7cf9cc1584e9a1141252862e32128adf4` (repair/nl5-001-b-library-r1, PR #38)
- исходный reviewed subject до ремонта: `628526594784ded8bb2067976cefbe53c4ac0e48` (FIX_REQUIRED, FRESH_REVIEW_R1)

Live-сверка после `git fetch origin` (exit 0):

```text
origin/work/nl5-001-clean-integration-r1 = a9950dc87760986a2987a7b61131a417243a8c2b  (== exact head)
origin/main                              = 9de094c8d423574568e62832854664b577e9f282  (== base)
merge-base --is-ancestor 9de094c a9950dc -> OK (base — предок head)
rev-list --count 9de094c..a9950dc        = 40  (39 cherry-pick + 1 event-0004 record commit)
git diff a9950dc origin/work/nl5-001-clean-integration-r1 -> пусто (ветка == exact head)
```

## Scope

`git diff --name-status 9de094c..a9950dc` = 72 файла. Все попадают в NL5-поверхности,
разрешённые паспортами EX-NL5-001-A-R1/B-R1/REPAIR-R1 (`docs/release/**`,
`releases/nanolab-components-v0.1/**`, `scripts/release/**`, `examples/release/**`,
`schemas/**`, `tests/test_release_*`, `docs/work/WO-NL5-001-*`,
`docs/work/executions/EX-NL5-001-*`). Два файла вне первичного паттерна
(`docs/control/OWN_LICENSE_OPTIONS_MEMO_R1.md`, `schemas/components/component-card.v1.json`)
явно разрешены A-паспортом и внесены исходным A-коммитом `bd12f3f`.

Запрещённые поверхности — 0 изменений: `project/state.json`, `project/plan.json`,
`docs/ROADMAP*`, `config/control/harness/checkpoint-catalog.v1.json`, `.github/**`,
`EX-POST-MVP-ROUTE-R1` — grep по diff-списку дал 0 совпадений.

## Repaired-point checks a)–g)

### a) Reproduction criterion (F-B3) — PASS

- `docs/release/REPRODUCTION_RULE_V0_1.md`: статус **FROZEN BEFORE NL5-001-C DATA** (строка 3);
  правило не использует pooled bootstrap CI как tolerance; outcome-набор MATCH/MISMATCH/INCONCLUSIVE
  с сохранённым INCONCLUSIVE и раздельной фиксацией technical failures; `74b` явно исключён.
- `scripts/release/reproduction_rule.py`: `RULE_ID = "NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE"`;
  classify(): technical_ok=False → INCONCLUSIVE; integrity_analysis_complete=False → INCONCLUSIVE;
  <3 replica medians → INCONCLUSIVE; statistic внутри envelope → MATCH; полная directional
  separation → MISMATCH; иначе INCONCLUSIVE. Static review логики — корректно.
- Карточки 0b/11b/32b/53b (MEASURED): `reproduction.expected` содержит
  `rule_id`, `reference_replica_medians_deg` (3 значения), `reference_replica_envelope_deg`,
  `bootstrap_ci_role = DESCRIPTIVE_ONLY_NOT_A_REPRODUCTION_TOLERANCE`,
  `required_fresh_replicas = 3`; `tolerance_policy` ссылается на rule id.
- Числа сверены с опубликованным evidence: per-replica medians карточки 32b ==
  `docs/work/executions/EX-NL3-002-PARAM-32B-R1/evidence/PARAM-32B-summary.json`
  (79.877463339 / 77.4927314 / 77.794798276; MATCH: True); envelope и campaign statistic
  пересчитаны и совпали; `reference_observable_estimate_deg ==` estimate карточки.
  Для 0b/11b/32b/53b это закреплено тестом `test_temp_build_reads_protocol_pins_from_evidence`
  и идентичностью `measured_observables` vs reviewed subject (см. Claim discipline).
- Старое правило «pooled median внутри bootstrap CI95» удалено: grep по пакету находит
  CI95 только в descriptive-описаниях статистики опубликованного evidence.
- Тесты: `python3 -m unittest tests.test_release_repair_r12` → Ran 10, OK, exit 0.
  Ключевой control case: fresh replica 65.50 вне старого pooled CI [65.6749, 66.3183] →
  **MATCH** (не автоматический mismatch) — ровно требование REPAIR_MAP R1.

Команды: `python3 -m unittest tests.test_release_repair_r12 tests.test_release_planning_refs -v` → exit 0.

### b) Evidence provenance (F-B1) — PASS

- `provenance.generation` всех карточек: `assembled by release.build_library_r12.py
  (WO-NL5-001-B-REPAIR-R1); scientific/protocol machine fields are evidence-derived; ...`.
- Тест читает protocol pins **из файлов evidence** (не из hardcoded EXPECTED-констант):
  0b — `EX-NL3-002-SUMMARY-R1/evidence/component-card-0b.json` (steps/seeds/print_conf_interval/
  print_energy_every/salt_concentration); 11b/32b/53b — `PARAM-*-summary.json`
  (seeds по run_reports, steps_requested) → OK, exit 0.
- Собственная сверка (32b): seeds/steps карточки == run_reports evidence; платформа/temperature
  аннотированы источником (`WSL2 Ubuntu 24.04 (ENGINE_ENVIRONMENT_R1; ...)`,
  `300 K (авторская установка конфига; decision rule E2-SETUP-R1 §5 ...)`).
- `releases/nanolab-components-v0.1/provenance/source-digests.json` присутствует:
  pinned upstream commit `23fd1ff7731e9017bd776f49206dc42d70d9fe91`, digest vocabulary
  blob_sha1/sha256_status, REFERENCE_ONLY download-on-run.
- Тесты: `python3 -m unittest tests.test_release_library tests.test_release_contract` → Ran 38, OK, exit 0.

### c) Deterministic manifest (F-B2) — PASS

- `RELEASE_MANIFEST.json`: ключей `generated_at_utc` нет; `generated_by =
  release.build_library_r12 deterministic-r1.2`; files = 20.
- `PYTHONPATH=scripts python3 -m release.build_library_r12 check` → `ok: true, problems: []`, exit 0.
- Полный rebuild в disposable-копии worktree: `PYTHONPATH=scripts python3 -m
  release.build_library_r12 build` → exit 0, после него `git status --porcelain` **пуст**
  (нулевой drift, включая манифест) — ровно отсутствие дрейфа.
- Тест `test_two_full_builds_are_byte_identical_including_manifest`: два temp-build
  байт-идентичны, `generated_at_utc` отсутствует → OK.

### d) R1.2 contract synchronization (F-B4) — PASS

- `docs/release/RELEASE_CONTRACT_V0_1.md`: Revision history содержит R1.2 / B-Repair-R1
  (frozen reproduction rule, deterministic full-package manifest, fail-closed
  duplicate/unsafe paths, evidence-derived pins, stale planning reference удалён);
  раздел «Digest semantics R1.1» (sha256 только в паре с sha256_status) и правило
  `S5 | sha256 ↔ sha256_status` в таблице — контракт/схема/линтер согласованы
  (S1..S5; card_lint и schema snapshot проходят весь suite).

### e) Manifest hardening (F-B6) — PASS

- `card_lint.manifest_verify()`: явный duplicate-path rejection до dict-преобразования
  (`duplicate path entry`) + `_check_rel_path` на каждый entry (empty/absolute/backslash/`..`).
- Negative-тесты (все OK, exit 0): `test_duplicate_identical_path_rejected`,
  `test_duplicate_conflicting_path_rejected` (sha256-конфликт), `test_unsafe_paths_rejected`
  (`/absolute`, `../escape`, `dir\file` → ok:false, ошибки по path).

### f) Planning refs (F-B5) — PASS

- Stale-литерал `POST_MVP_EXECUTION_PROGRAM_R1` в дереве — только в immutable
  START-событии A и в константе STALE самого теста.
- Immutable START-событие A не редактировалось: `git diff 6285265..a9950dc -- .../EX-NL5-001-A-R1/events/0001-work-order-started.json` пусто; `--diff-filter=M` по `EX-NL5-001-A-R1/events/` — 0 коммитов.
- Digest-pin сверен: sha256 файла == `26f939d551576b0fdea93784eaf5977a8f0af057a7835a3a3c713abf9ea41fa2` (пин в тесте) — любой дрейф байтов = fail closed.
- Паспорта A/B исправлены protocol-корректно: `corrections` с corrected_value
  `POST_MVP_DEVELOPMENT_ROUTE_R1.md` и объяснением; исторические события не тронуты.
- `python3 -m unittest tests.test_release_planning_refs` → OK, exit 0.

### g) 74b (claim discipline) — PASS

- `74b.card.json`: `measurement_status = NOT_MEASURED`, `measured_observables = {}`
  (ноль выдуманных значений), `known_gaps = [G-74B-ARM-MANIFEST, status KNOWN_GAP,
  blocking_release=false]`, runs NOT_RUN (`frames_valid 0/0 (NOT_RUN)`),
  `scientific_outcome = NOT_MEASURED`, `claim_ceiling = C0_SOFTWARE_ONLY`,
  `reproduction.expected = {}` — исключён из reproduction-классификации; правило
  (REPRODUCTION_RULE_V0_1.md, обязательные условия) явно запрещает классифицировать 74b.
- Числовые поля 74b идентичны reviewed subject 6285265 (см. ниже).

## Rebuild integrity (clean integration)

- Эквивалентность patch-ей SHA-карты (5 пар, `git diff <old>^ <old>` vs `git diff <new>^ <new>`
  без index-строк — байт-идентичные патчи): `be73c54→2377f62`, `798be15→3a8b037`,
  `1606231→81aa78f`, `54d8e03→2181b8f`, `dc3063b→66e2270` — все IDENTICAL.
- `git diff dc3063b7c..66e2270` (всё дерево): единственное различие —
  `EX-POST-MVP-ROUTE-R1/events/0002-handoff-completed.json` (косметическое форматирование
  JSON-массива; JSON-семантика старого/нового файла — EQUAL, проверено python-парсингом);
  diff по всем NL5-поверхностям — пуст. Claims события 0004 подтверждены.
- Упакованный rule-документ байт-идентичен frozen-документу:
  sha256 `6b70dfc26764c8a21d006824f00e485df9abec8b020e67de5a9709acea793e78` для
  `docs/release/REPRODUCTION_RULE_V0_1.md` и
  `releases/nanolab-components-v0.1/reproduction/REPRODUCTION_RULE_V0_1.md`.

## Full local validation (exact head a9950dc)

```text
python3 -m unittest discover -s tests -t .                       -> Ran 360 tests, OK, exit 0
PYTHONPATH=scripts python3 -m release.build_library_r12 check    -> ok=true, problems=[], exit 0
disposable full rebuild + git status --porcelain                 -> пусто (нулевой drift)
PYTHONPATH=scripts python3 -m release.card_lint package releases/nanolab-components-v0.1
                                                                 -> ok=true, errors=[], ровно 1 warning
                                                                    (D2 owner license decision), exit 0
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .   -> exit 0
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .           -> exit 0, blocking 0
for d in docs/work/executions/EX-*: work_cli validate $d         -> 36 каталогов, 0 failures
```

Hosted CI на exact head: run `35090409941`, workflow `hosted-ci`, event `pull_request`,
conclusion success; шаги Check 1/5..5/5 — success (GitHub API).

## Negative controls

1. Duplicate path (identical metadata) → rejected. 2. Duplicate path (conflicting sha256)
→ rejected. 3. Unsafe paths (`/absolute`, `../escape`, `dir\file`) → rejected. 4. Control case
репродукционного правила: fresh replica вне старого pooled CI95 → MATCH (правило не
использует CI как tolerance). 5. Insufficient replicas (2) → INCONCLUSIVE; technical
failure → INCONCLUSIVE (fail-closed, не PASS). 6. Digest-pin immutable события: дрейф
байтов → fail (проверена сверка текущего sha256 с пином). 7. Tamper-detection манифеста —
в составе 360-тестового suite (test_release_library/contract) — OK.

## Claim discipline

- **Научные числа не менялись**: `measured_observables` всех 5 карточек (0b/11b/32b/53b/74b)
  байт-значностно идентичны reviewed subject `6285265`; per-replica medians прослежены до
  опубликованного evidence (EX-NL3-002-PARAM-32B-R1 и тест по 11b/32b/53b + 0b summary).
  Diff карточек ограничен reproduction-блоком, provenance.generation, evidence-аннотациями
  protocol pins — ровно зоны ремонта.
- **C0_SOFTWARE_ONLY**: claim ceiling карточек и класс исполнения паспорта не превышены;
  reproduced rule — операциональное сравнение, не физическое утверждение.
- **74b NOT_MEASURED / KNOWN_GAP** сохранён честно, blocking_release=false.
- **Физика не запускалась**: в diff 9de094c..a9950dc нет новых simulation evidence/runs —
  только release-конвейер, тесты и control-документы; REPAIR/Passport это декларируют,
  наблюдение согласуется.
- D2 (лицензия владельца) остаётся открытым гейтом: lint предупреждение ровно одно и явное.

## Event 0004 / SHA-map facts vs live

| Claim события/карты | Наблюдение |
|---|---|
| subject_sha 66e2270 | = parent of a9950dc ✓ |
| Base 9de094c (main после PR #39, #37, #40) | = origin/main live ✓ |
| 39 cherry-pick коммитов | rev-list 9de094c..a9950dc = 40 = 39 + event-коммит ✓ |
| NL5-surface diff dc3063b7..66e2270 пуст | ✓ (воспроизведено) |
| Единственное целое дерево-различие — 0002-handoff-completed.json, косметика | ✓ (JSON-семантика EQUAL) |
| unittest 360 OK; builder check ok; card_lint ok=true + D2; consistency/workflow ok; EX-* ok | ✓ (все воспроизведены, те же числа) |
| json.tool sweep 1030 файлов | tracked *.json сейчас 1035 = 1030 + 4 pinned + сам event-0004 ✓ |
| hosted CI 5/5 на замороженном head | run 35090409941 success, Check 1..5/5 success ✓ |

## Independence caveat

Fresh сессия/контекст; implementation-чат и предыдущий review мне не передавались; вердикты
не наследовались — все проверки выше выполнены заново на exact head. Ограничение: тот же
GitHub installation/account, что и остальной конвейер; по HARNESS это не доказательство
независимой executor identity. Fresh exact-head Verifier после этого review остаётся
обязательным шагом.

## Remaining risks

- Публикация пакета остаётся заблокированной: D2 (лицензионное решение владельца) + NL5-001-D.
- `74b` — известный гэп (arm-manifest-v2, будущий bounded WO); в v0.1 не блокирует release.
- `NL5-001-C` нельзя запускать до Fresh Verifier PASS и Human Gate merge; правило заморожено,
  но его применение к clean-room кампании — предмет отдельного Work Order (fresh seeds,
  дизайн реплик).
- Исторические durable-копии FRESH_REVIEW_R1/REPAIR_MAP_R1 не лежат в дереве subject
  (они и не лежали в стеке ремонта) — они durable на `origin/review/nl5-001-b-r1` (0761e53/ab55eb5)
  и в carry-коммите `42ddf38` на `origin/work/nl5-001-b-library-assembly-r1`; WO/паспорт
  ссылаются на них корректно по review-ветке. Observation уровня LOW/INFO, не blocking.
- Поля `base_branch`/`branch` паспортов A/B/REPAIR указывают на исторические stack-ветки;
  это явно раскрыто в event 0004 (паспорта не редактировались; интеграционный носитель —
  `work/nl5-001-clean-integration-r1`).

## Verdict rationale

Все шесть blocking findings исходного FIX_REQUIRED (F-B1..F-B6) закрыты по существу,
каждый закреплён исполняемыми regression-тестами; новый negative-control слой
(duplicates/unsafe paths, digest-pin immutable события, control-case правила репродукции)
работает fail-closed. Rebuild в чистой интеграции эквивалентен reviewed repair-стеку по
всем NL5-поверхностям (пустой diff), единственное целое дерево-различие — косметическое
и семантически идентичное, каноничен уже review-verified вариант PR #40. Scope чист,
canonical не тронут, научные числа не менялись, 74b честен, физика не запускалась, D2
остаётся за владельцем. Full local suite (360 OK), builder byte-identity (нулевой drift),
package lint (ok, единственный ожидаемый D2-warning), consistency/workflow lint, 36 EX-*
validate и hosted CI 5/5 на exact head — зелёные и воспроизведены в этой сессии.

**REVIEW_VERDICT = PASS**

Next action (per harness): Fresh exact-head Verifier на `a9950dc87760986a2987a7b61131a417243a8c2b`,
затем Human Gate merge PR #41. NL5-001-C не стартует до этого.
