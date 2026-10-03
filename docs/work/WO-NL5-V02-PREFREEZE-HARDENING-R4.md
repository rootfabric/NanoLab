# NanoLab — новая миссия центрального агента
## NL5 v0.2: pre-freeze hardening R4 + отдельная активация native Ubuntu R2

Дата проверки: **3 октября 2026 года**.
Репозиторий: `rootfabric/NanoLab`.
Статус документа: **готовое задание для передачи агенту, не запись Human Gate**.

## 0. Роль и цель

Ты — **DIRECTOR / центральный агент NanoLab**. Организуй ограниченное исправление предрегистрационного пакета v0.2, доведи его до независимых проверок и подготовь решения владельцу. Параллельно восстанови фактическую готовность авторской Ubuntu-среды и продолжи разрешённую INFRA-активацию, когда доступен настоящий U1.

**Не начинай NL6, не повторяй R3 с нуля и не запускай подтверждающую научную кампанию.** Результат этого задания — проверенный пакет перед freeze и честный статус Ubuntu-активации, а не научное закрытие NL5.

Передача этой инструкции на исполнение разрешает bounded implementation/control work, публикацию evidence, scoped commits, non-force push и draft PR в рамках действующего Harness. Она **не означает** разрешения на merge, HG-B, платные вычисления, многочасовую научную кампанию или самостоятельное объявление R2 ACTIVE.

## 1. Проверенный исходный снимок — не заменять им свежую проверку

```text
CANONICAL_MAIN = 87298b36431045474d3784adf5cee8c9a64d0fc9
MAIN_TREE      = db19f9dd265873f99c995aa279ae5e0c5b21c330
MAIN_CI_RUN    = 36839661671 / SUCCESS
LAST_MERGE     = PR #47 / INFRA3 R2 activation tooling / 2026-10-01

POLICY_PR      = #48 / OPEN / DRAFT / NOT MERGED
POLICY_BRANCH  = integration/nl5-acceptance-policy-r3
POLICY_HEAD    = ce13f0e9cb9536aaffddfff0a05c9a73f0870a21
POLICY_BASE    = 8205781def7179d6bdfa6eb7ab2a84d46776649c
POLICY_CI_RUN  = 36804852475 / SUCCESS
COMPARE_TO_MAIN = 11 ahead / 9 behind / diverged

NL0..NL4              = ACCEPTED; MVP COMPLETE
NL5-001               = ACCEPTED; nanolab-components 0.1.0
NL5                    = IN_PROGRESS
NL5-002                = WAITING_HUMAN; terminal verified MISMATCH / NOT accepted
external_reproductions = 0
PLATFORM-SENSITIVITY-R1 = FULLY VERIFIED / PLATFORM_INSENSITIVE
P1_RAW_GAP             = CLOSED
NL6-001                = LOCKED

R3                    = PRE-DATA / NOT FROZEN / NO NEW SCIENCE
PRIMARY_N             = 64 for 0b and 32b
CONTROL_N             = 10 for 11b and 53b
FRESH_SEED_TOTAL      = 148 paired identities
R3_CONFIRMATORY_RUNS  = 296 across both platforms
R3_MAX_RUNS           = 356, including declared replacement allowance
R3_WALL_LIMIT         = 560 hours/platform (proposal, NOT current authorization)

AUTHOR_U1             = NOT_ASSIGNED
R2_STATUS             = WAITING_HOST / NOT_ACTIVE
R2_ACTIVATED          = NO
OUTENEMY_ROLE         = EXTERNAL_U2_ONLY
WINDOWS_WSL_EXECUTOR  = HISTORICAL_ONLY
NEW_SCIENCE           = HARD_BLOCKED without active R2 and frozen/reviewed protocol
```

R3 уже исправил старое расхождение между N протокола и генератором и сформировал 148 seeds. Его исторические review/verify PASS не стирать. Однако новая проверка выявила другие дефекты, поэтому **готовность к freeze в этой миссии оценивается как FIX_REQUIRED**. Это новая запись review, не задним числом изменённый старый verdict.

## 2. Обязательное восстановление

Прочитай `AGENTS.md`, `DIRECTOR.md`, `PROJECT_CONTROL.md`, `HARNESS_CONTROL.md` и обязательную цепочку документов, на которую они ссылаются. Особенно:

```text
project/state.json
project/plan.json
project/infra-state.json
project/infra-plan.json
docs/work/WORK_QUEUE.md
docs/ROADMAP.md
docs/control/GIT_TASK_BUS_POST_PILOT_CORRECTION_R1.md
docs/control/GIT_TASK_BUS_PROMPTS_RU.md
docs/control/HARNESS_REVIEW_AND_EVIDENCE_RU.md
docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md
docs/research/ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md
```

На exact subject PR #48 прочитай:

```text
docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
docs/control/NL5_ACCEPTANCE_PRINCIPLE_HG_B_PROPOSAL_R1.md
docs/evidence/NL5-ACCEPTANCE-POLICY/INTEGRATION_RECORD.md
scripts/nl5/repro_v02_seeds.py
scripts/nl5/repro_v02_freeze_gate.py
scripts/nl5/repro_v02_feasibility_gate.py
tests/test_nl5_repro_v02_seeds.py
docs/work/executions/EX-NL5-ACCEPTANCE-POLICY-R2/evidence/repro-v0-2-seed-record-PRE_DATA_R3.json
```

Выполни fresh fetch, зафиксируй полные `MAIN_HEAD`, `MAIN_TREE`, `PR_HEAD`, `PR_TREE`, merge-base, ahead/behind и CI exact subject. Прочитай активные execution/lease/handoff records. Не открывай дубликат уже выполняемой задачи. Если SHA изменились, сделай delta-review и выясни, какие findings ещё воспроизводятся; не сбрасывай чужой прогресс.

Task Bus использовать только в реально разрешённом режиме. Не повторять BUS-SMOKE-001 и не активировать P2 автоматически. Director не играет роли Implementer, Reviewer и Verifier под разными именами. При отсутствии отдельной исполняющей сессии — durable `WAIT_EXTERNAL`, а не выдуманный независимый PASS.

## 3. Новые findings, которые нужно сначала воспроизвести

### F1 — freeze consistency gate пропускает некорректный seed contract

В проверенном `scripts/nl5/repro_v02_freeze_gate.py`:

```text
GIT_BLOB_SHA1 = 3875167709de7db89ebb0ad4c33d5722a85621aa
```

`freeze_consistency_gate()` возвращает `PASS` для следующих негативных изменений при сохранённых metadata counts:

- оба контрольных массива `11b` и `53b` пусты;
- seed основной серии дублирован;
- в основную серию подставлен historical seed;
- `record_sha256` неверен;
- `bootstrap_seeds` пуст;
- в protocol text изменены N_min, wall budget и max_runs, но строка `0b = 64, 32b = 64, 11b = 10, 53b = 10` осталась;
- после этой строки добавлена другая, противоречащая ей cardinality declaration.

Это проверка функции, а не утверждение, будто текущий опубликованный seed record уже повреждён. Дефект — отсутствие обещанной защиты от повреждения и drift. Если защита заявлена другим слоем, покажи обязательную fail-closed связку этого слоя с freeze/dispatch; необязательный тест или ручная рекомендация недостаточны.

### F2 — collision scan не различает ошибку Git и отсутствие совпадений

В `scripts/nl5/repro_v02_seeds.py`:

```text
GIT_BLOB_SHA1 = 81c1401c5d151202d6853cc46cdd81be0baff66a
```

`literal_tree_collision_scan()` вне Git repository получает `git grep` exit=128, но возвращает `collision_count=0`. Функция не проверяет return code. Кроме того, поиск идёт по tracked working-tree содержимому, а не по явно pinned tree: локальная незакоммиченная замена файла скрывает seed, который остаётся в canonical blob.

### F3 — replacement N+1 конфликтует с уже потреблёнными identities

В протоколе §8 резервные seeds начинаются с индексов `N+1, N+2, ...`. Но R3 уже пропустил candidate indices из-за tree collisions. Поэтому N не равен последнему потреблённому индексу.

Проверенный R3 record имеет:

| Variant | N | Consumed indices | Первый резервный index по тексту | Seed уже находится в основной серии |
|---|---:|---:|---:|---:|
| 0b | 64 | 74 | 65 | 1960729465 |
| 32b | 64 | 75 | 65 | 411873937 |
| 11b | 10 | 20 | 11 | 1351266957 |
| 53b | 10 | 20 | 11 | 1321440826 |

Это конкретная коллизия правила, не результат запуска replacement jobs. Новая схема должна исключить неоднозначность до freeze.

### F4 — целочисленные границы и scientific wording требуют согласования

В R3 `N_min=51` назван 80% от 64, хотя `51/64 = 79.6875%`. `60/296 = 20.27027%`, хотя заявлен replacement cap ≤20%, в том числе по ячейкам. Код округляет N_min вниз, общий запас — вверх. Зафиксировать одно явно названное целочисленное правило во всех поверхностях.

Не менять научные параметры молча. Если сохраняется буквальное «не менее 80%», минимальное число пар — 52. Если сохраняется буквальное «не более 20% на ячейку», лимиты выводятся из целочисленных per-cell quotas, с учётом парности. Любые изменения оформить новой **pre-data candidate revision** с Repair Map и вынести в owner decision package; это не уже утверждённая политика.

На scientific review отдельно проверить определения H0/H1, область доказуемого вывода и обоснованность planning gate. Тест CI медианного парного сдвига сам по себе не должен рекламироваться как проверка всех свойств распределения. Прохождение planning bootstrap на исторических 10 парах не гарантирует исход новых данных. Формулировки «гарантированно feasible» и объяснение старого MISMATCH одной только формой v0.1 правила должны быть смягчены до того, что действительно установлено. Не переписывать само историческое наблюдение PLATFORM_INSENSITIVE.

## 4. Трек A — bounded pre-freeze hardening R4

Предлагаемые ID — перед открытием проверить отсутствие активных дублей:

```text
WO        = WO-NL5-V02-PREFREEZE-HARDENING-R4
EXECUTION = EX-NL5-V02-PREFREEZE-HARDENING-R4
BRANCH    = work/nl5-v02-prefreeze-hardening-r4
RISK      = HIGH for protocol integrity
CLAIM     = C0_SOFTWARE_ONLY / PRE-DATA
```

### A1. Контрольный старт и интеграция

Создать ветку от свежего exact `origin/main`. **До substantive edits** записать и опубликовать START с base SHA, scope, budget, findings и stop conditions. Затем интегрировать exact существующий subject R3 с сохранением истории (`--no-ff`, без squash/force-push), а не писать его заново.

PR #48 отстаёт от main с уже принятым PR #47. Не потерять `scripts/r2/`, Ubuntu policy, актуальные INFRA-строки WORK_QUEUE и activation evidence. Разрешение конфликтов — явная Repair Map. Старые review/verifier ветки сохраняются как verdict refs; их PASS не автоматически покрывают новый integration HEAD.

Не редактировать исторические R1/R2/R3 execution events, evidence JSON и verdict records. Создавать R4 evidence и addenda. Candidate-документ можно обновить как новую незамороженную ревизию, сохранив историю и явную таблицу изменений.

### A2. Один машинный источник для freeze/dispatch

Реализовать или выделить версионированный machine-readable contract. Не ограничиваться поиском первой regex-строки Markdown. Contract должен явно связывать:

```text
rule/revision + scientific subject pins
variant set + primary/control classification
N per variant + N_min + exact rounding policy
confirmatory + replacement seed pools
paired identity / attempt / replacement semantics
anchor + algorithm + consumed indices / next cursor
bootstrap seed set + bootstrap configuration
exclusion tree + historical exclusions + exact allowlisted paths
per-cell run caps + total run cap + wall cap
analyzer/convention/package/fingerprint requirements
feasibility planning evidence + full digests
execution-plan cardinalities and budget
```

Документируемые таблицы генерировать из contract или строго сверять с ним. Не допускать нескольких противоречащих authoritative declarations. Malformed JSON/тип, отсутствующее обязательное поле, extra variant, mismatch, ошибка чтения, неизвестная revision → явный fail-closed результат и ненулевой exit code, не PASS.

Проверять все четыре фактических массива, а не только metadata: длины; int32 range и положительность; отсутствие bool вместо integer; глобальную уникальность; disjoint primary/control/reserve/bootstrap/historical sets по утверждённой семантике; корректный digest и воспроизводимость генерации. Явно описать, что входит в logical record digest, и дополнительно фиксировать SHA-256 полных файлов без самоссылочного хеша.

Проверки обязательно вызываются реальным freeze/dispatch entrypoint. Отдельно доказать, что вызов execution нельзя провести в обход них.

### A3. Исправление collision scan

Выбрать и зафиксировать immutable exclusion tree/commit **до генерации**. Сканировать именно его, а не изменяемый worktree. Regeneration на тех же pins должна давать тот же record.

Для `git grep`: exit 0 — найдено, exit 1 — совпадений нет; иные коды, недоступный object/repo, ошибка декодирования/чтения, timeout, незапущенный Git — `SCAN_ERROR`/BLOCKED. Не возвращать «0 коллизий» при неполной проверке.

Пути-исключения фиксировать точно и обосновывать. Prefix-сравнение, позволяющее случайно исключить соседний evidence file, не использовать как authority. Не добавлять широкие исключения для достижения PASS. Опубликовать tree SHA, проверенные paths, результаты и scan scope.

Развести generation snapshot и последующую публикацию record/evidence так, чтобы сам факт публикации seed не бесконечно менял набор при каждом повторе проверки. Изменение exclusion tree — новая явно зафиксированная generation revision, не скрытый дрейф.

### A4. Резерв и attempts

Предпочтительно заранее сгенерировать и зафиксировать отдельные confirmatory и replacement pools. Альтернатива — полностью pinned deterministic cursor, но он должен начинаться **после последнего потреблённого candidate index**, не после количества принятых seeds.

Сохранять `indices_consumed`/`next_candidate_index` по каждому варианту. Для замен проверять глобальные коллизии со всеми основными и резервными identities. Связать оба плеча пары; определить, как технический отказ одной стороны расходует pair budget и что переисполняется. Attempt ID уникален; reuse ID и outcome-driven seed selection запрещены.

Замены разрешены только для frozen FAILED_TECHNICAL conditions, не для неудобных scientific outcomes. Параметры резерва и остановок фиксируются до данных.

### A5. Арифметика и статистические границы

Согласовать F4 до freeze. Не увеличивать N, δ, число вариантов, wall/runtime/paid limits ради достижения результата. Основной design `64/64/10/10`, δ=0.5, paired scheme и исторические критерии не менять без явного rationale и новой проверки.

Целочисленные quotas вывести из одной схемы; total budget не должен противоречить сумме per-cell caps. Обязательно различать proposed compute envelope, доступность машин и действительное разрешение владельца на кампанию.

Полный N-grid и исходные planning evidence сохранить. Воспроизводимость planning вычисления не выдавать за доказанную мощность на неизвестной будущей среде. Если scientific reviewer выявит необходимость изменить сам decision rule, это отдельное явно описанное pre-data изменение, а не незаметный tooling fix.

### A6. Негативные и позитивные тесты

Сначала показать воспроизведение F1–F3 на старом exact subject; затем **новые regression tests должны ожидать отклонения неправильного входа**, а не проверять старое ложное PASS.

Обязательные группы: empty/truncated controls; duplicate/historical/out-of-range seeds; bootstrap collision/missing bootstrap; stale digest; wrong counts/N_min/quotas/wall; extra/missing variants; conflicting protocol declarations; unavailable Git/object/non-repository/timeout; dirty worktree vs pinned tree; unsafe path exclusion; replacement after skips; reuse attempt ID; paired-budget exhaustion; mandatory dispatch gate failure.

Добавить позитивный clean case, regeneration bit-exact, корректный no-match scan и валидную замену после полного consumed stream. Fixtures синтетические или разрешённые historical data; никаких новых научных траекторий.

Прогнать штатные hosted gates, включая реальную команду коллекции:

```bash
python3 -m unittest discover -s tests -t .
```

Дополнительный pytest допустим, но он не заменяет доказательство, что новые тесты запускаются текущим hosted CI. Выполнить актуальные команды `check-consistency`, `workflow_lint`, `work_cli validate` согласно CLI репозитория; не выдумывать флаги. Проверить JSON/pins, все затронутые EX-* и отсутствие случайных изменений принятой science. Число тестов сообщать фактически, не требовать равенства историческим 403/427.

### A7. Независимые проверки и итог

```text
IMPLEMENTER
→ fresh SCIENTIFIC/PROTOCOL REVIEWER
→ отдельный fresh EXACT-HEAD VERIFIER
→ DIRECTOR readiness record
→ owner Human Gate package
```

Reviewer обязан рассмотреть F1–F4 и scope научного утверждения. Verifier независимо воспроизводит негативные контроли и проверяет фактический вызов gate в execution path. Один green unit-test report не заменяет их работу.

Новый commit после проверки требует проверки изменившегося subject. Pin полные implementation HEAD/TREE, integration HEAD/TREE, reports, CI run/head и base. Развести отчёт о проверенном product subject и последующий evidence-only commit, не заявляя coverage несуществующей самоссылочной ревизии.

Итог трека A до решения владельца:

```text
R4_TOOLING = REVIEWED_AND_VERIFIED              # только при фактических PASS
CANDIDATE  = PRE-DATA / NOT FROZEN
HG-B       = WAITING_OWNER
MERGE      = WAITING_HUMAN
SCIENCE    = NOT_STARTED
NL5        = IN_PROGRESS
NL6-001    = LOCKED
```

## 5. Трек B — native Ubuntu R2, не смешивать с научной приёмкой

Не повторять уже merged migration/tooling PR #46/#47. Сверить действующую R2 activation implementation, `config/infra/r2-activation.v1.json` и INFRA WO. Если авторский хост не назначен, не угадывать IP и не назначать outenemy автором.

Если реально назначенный и разрешённый U1 найден в текущем mission/config, проверить native Linux, native filesystem, systemd и независимость от U2. Снять фактический fingerprint. Нельзя объявлять eligibility по подставленному hostname или тестовому JSON.

В рамках отдельного INFRA WO выполнить предусмотренные контрактом U1–U5: pinned oxDNA build; package verify; frame0 fixtures; короткий **технический**, не confirmatory scientific smoke; harness gates. Далее NC-U1..NC-U5: устойчивость к завершению SSH/агента/runner, сохранность raw при CI cleanup, корректная фиксация deliberate kill. Такие проверки проводить на выделенных test jobs/services в согласованном scope, не перезапускать чужую продуктивную службу без разрешения.

Зафиксировать manifests с SHA-256/size/producer/retention, binary/source pins и реальные receipts. Unit/synthetic tests tooling не заменяют host gates. R2 ACTIVE возможно только после всех real gates + fresh review/verify + отдельного owner activation decision.

При отсутствии U1:

```text
AUTHOR_U1 = NOT_ASSIGNED
R2_STATUS = WAITING_HOST / NOT_ACTIVE
BLOCKER   = real authorized native Ubuntu author host is not assigned
```

Опубликовать готовый activation runbook и точный недостающий ресурс. Не блокировать этим завершение трека A. outenemy остаётся внешним U2; Windows/WSL — historical/UI only. Никакого silent fallback и новых платных ресурсов.

Согласовать WORK_QUEUE/roadmap/scheduler с уже состоявшимися merges. `infra-state` не повышать до scientific executor=true лишь на основании принятого tooling; отсутствие полного INFRA checkpoint acceptance сохранять явно. Любой canonical state update — отдельное reviewed proposal и разрешённый merge.

## 6. Неизменяемые границы

Сохранять прежние NL0–NL4/NL5-001 acceptance, NL5-002 terminal MISMATCH, PLATFORM_INSENSITIVE, P1_RAW_GAP=CLOSED и отрицательный результат E3. `74b = NOT_MEASURED / KNOWN_GAP`; не производить новые значения 74b. Код Apache-2.0; собственные docs/derived data CC-BY-4.0; сторонние права не менять. E2 acquisition только по действующему pinned download-on-run/REFERENCE_ONLY контракту; не создавать durable upstream cache без нового разрешения.

Не разрешены: direct push main; force-push; squash/rewrite evidence history; изменения frozen v0.1 thresholds; self-review/self-accept; повтор ранов ради лучших цифр; сбор новых confirmatory данных до freeze; разблокировка NL6; обновление движка без WO; wet-lab/hardware work; глобальные изменения системы владельца вне согласованного scope.

Не путать разные Human Gates:

```text
HG-MERGE-CANDIDATE : интеграция исправленного control/tooling пакета
HG-B              : принцип и параметры нового scientific acceptance
HG-R2-ACTIVATION  : активация реального авторского R2 host
HG-CAMPAIGN       : утверждённый execution WO и его ресурсы
HG-NL5-ACCEPTANCE : поздняя приёмка по новым результатам
```

Это описательные имена в данной миссии: сопоставить их с актуальными canonical gate IDs и decision subjects, не переопределять исторические HG-A/B/C. Одно approval нельзя автоматически переносить на остальные.

## 7. Deliverables и остановка

В Git на scoped ветках должны быть: mission/WO/START; Repair Map F1–F4; baseline repro; исправленный код и реально собираемые NC-тесты; R4 contract/seed/scan/budget evidence; независимые review/verifier records; CI evidence exact subject; refreshed integration record; HG-B proposal; R2 activation report либо точный WAITING_HOST; human-readable queue sync proposal.

Документы новые/append-only по отношению к историческим reports. Опубликовать CONTINUATION после каждого substantive этапа и перед каждым handoff. Не записывать сырой artifact как существующий без реального location/hash. Если настоящий внешний агент/host/Human Gate недоступен, остановить только соответствующую ветку выполнения и сохранить следующее действие.

Финальный отчёт:

```text
NANOLAB NEXT MISSION R4
VERDICT = FIX_REQUIRED | READY_FOR_REVIEW | READY_FOR_HUMAN_GATE | BLOCKED
MAIN_OBSERVED = ...
BASE_MAIN = ...
BRANCH = ...
PRODUCT_HEAD/TREE = ...
INTEGRATION_HEAD/TREE = ...
F1_FREEZE_CONTRACT = ...
F2_COLLISION_SCAN = ...
F3_REPLACEMENT_STREAM = ...
F4_ROUNDING_AND_CLAIMS = ...
TESTS_AND_COLLECTION = ...
HOSTED_CI_RUN/SUBJECT/RESULT = ...
REVIEW_SUBJECT/VERDICT/REF = ...
VERIFY_SUBJECT/VERDICT/REF = ...
CANDIDATE_FREEZE_STATUS = NOT_FROZEN | ...
AUTHOR_U1 = ...
R2_ACTIVATED = NO | ...
REAL_HOST_GATES = ...
HG_B = ...
MERGE_AUTHORIZATION = ...
NEW_SCIENTIFIC_RUNS = 0
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED
EVIDENCE_PATHS = ...
NEXT_ACTOR = ...
NEXT_ACTION = одно конкретное действие
```

Если одно направление готово, а другое ждёт машину, показывать оба статуса отдельно. Не объявлять всю миссию выполненной по одному лишь merge tooling или зелёному CI.

## 8. Путь после завершения этой миссии

Только после отдельных необходимых решений:

```text
reviewed R4 candidate + owner HG-B
→ Director freeze: protocol/contract/seeds/analyzer/inputs/budget
→ fresh review + exact-head verify frozen subject
+ real R2 ACTIVE and authorized campaign WO
→ author U1 leg + independent external U2 leg
→ raw reanalysis + scientific review + verification
→ отдельная NL5 acceptance decision
→ затем NL6-001 / E5 driven DNA component
```

Правило при MISMATCH/INCONCLUSIVE применяется механически и сохраняется. Успех не обещается заранее, критерии по новым данным не подгоняются.