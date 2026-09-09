# NL1-002 — REPAIR MAP R2→R1 (исправления по VERIFIER VERDICT R2 = FIX_REQUIRED)

- Repair execution: `EX-NL1-002-R1-REPAIR1` (ветка `work/nl1-002-reference-run-r1`, режим «corrections — новым evidence/event», история не переписывается).
- Основание: `docs/evidence/NL1-002/VERIFIER_VERDICT_R2.md` на `verify/nl1-002-reference-run-r2` @ `149feda3fe16ce63afaecf52a4d4b8ae83325dd7` (superseding R1-вердиктов по основанию role-mixing).
- Ремонтируемый subject: `ec7e3edc83a3434d96222a0a8a94b03f7fa10e23` (base `71535d00a2e729349eea2337217a2c591ed9317d`).
- Фактический старт ремонта: HEAD ветки `c44b2091d183be55e8accd47e845c0511c041083` = subject + 4 коммита superseded R1-вердиктов (`7b12012`, `b405a7e`, 2 merge); work-content бит-в-бит идентичен subject; R1-вердикт-файлы (`REVIEWER_VERDICT.md`, `VERIFIER_VERDICT.md` на этой ветке) сохраняются как история, не используются и не редактируются.
- Метод: воспроизведение находок R2 на свежем worktree → минимальный контрактный ремонт → повторный прогон обоих валидаторов. Научное содержание не пересматривалось (оно подтверждено R2 полностью, §4 вердикта).

## 1. Root cause (по находкам R2)

| ID | Находка | Root cause |
|---|---|---|
| F-1 (MAJOR) | `CONTROL_EXPERIMENT validate` падал на всех 4 run-каталогах: `AttributeError: 'str' object has no attribute 'get'`, exit 1; `manifest.json` без `subject_sha`/`claim_ceiling`/`model`/`observables`/`stop_conditions` (на пилотах и без `resource_budget`); события без `experiment_id`/`subject_sha` | `artifacts.manifest.json` писался в прозаической форме `{"artifacts": {имя: …}}` (форма из prose-контракта `EXPERIMENT_HARNESS_RU`), а машинный контракт (`config/control/harness/artifact-manifest.schema.v1.json` + `scripts/harness/experiment_cli.py`, бит-в-бит идентичен base) требует массив записей; машинные поля манифестов/событий на момент исполнения не были формализованы. Provenance присутствовал и верифицирован (R2 D1: 16/16), но контрольная поверхность не проходила механически |
| F-2 (MINOR) | `CONTROL_WORK validate EX-NL1-002-R1` → ok=false, exit 3: в событиях `0002`–`0005` `subject_sha: "9cc83e8"` (7 знаков) | События ссылались на freeze-commit `9cc83e8599c76366a6ba8c5bc49f7398f5fca64f` в сокращённой форме; контракт требует 40 lowercase hex |
| F-3 (MINOR) | Тот же validate: `terminal/handoff event must be last` — после `0004-handoff-completed` опубликован `0005-resource-evidence-committed` | Post-handoff checkpoint (допустимый по духу «corrections — новым event») нарушает букву машинного контракта, где терминальное событие обязано быть последним |

## 2. Что изменено (все коммиты — новые поверх c44b209, без rewrite)

| Коммит | Изменение |
|---|---|
| `ac5c6cbe761532918dd3f43f5722fa6996d55910` | **F-1, run-манифесты (×4: E1-R1-S001/P001/P002/P003):** (а) `artifacts.manifest.json` переписан в контрактную форму: `{"schema_version": 1, "artifacts": [ {name, sha256, size_bytes, producer_run_id, subject_sha, storage_location, producer_command} ]}`; отображение без потерь: `producer_run`→`producer_run_id`, `producer_tool`→`producer_command`, `storage`→`storage_location`; все `sha256`/`size_bytes` сохранены 1:1 (программная проверка перед коммитом); `subject_sha = 9cc83e8599c76366a6ba8c5bc49f7398f5fca64f` (полная форма замороженного subject, см. §3). Исходные объектные формы сохранены бит-в-бит рядом: `artifacts.manifest.v1-superseded.json` (4/4 проверены byte-equal к blob до ремонта — «старый манифест не удалён, помечен superseded» в допустимой вариации: валидатор жёстко требует контрактный файл именно по пути `artifacts.manifest.json`). (б) `manifest.json` дополнен контрактными полями — СТРОГО аддитивно: S001 +5 ключей (`subject_sha`, `claim_ceiling`, `model`, `observables`, `stop_conditions`), P001–P003 +6 (те же + `resource_budget`); ни один существующий ключ не изменён (программная проверка) |
| `6b6dab46c6020632ed6751767c1dfbd03aa1624e` | **F-1, события прогонов:** события `0001-started`/`0002-run-completed`/`0003-analysis-completed` всех 4 прогонов дополнены идентификаторами `experiment_id: "E1"` и `subject_sha` (полная 40-hex форма) — строго аддитивно: 12 файлов, +24 строки, 0 удалений, ни одно значение не изменено. В каждом run-каталоге опубликован НОВЫЙ event `0004-repair-manifest-contract` (RUN_CHECKPOINT), документирующий ремонт данного прогона |
| `f78a182ebc3167a0a8b99d2d3f248b4188263fed` | **F-2/F-3 erratum:** новый event `docs/work/executions/EX-NL1-002-R1/events/0006-repair-completed.json` (CONTINUATION_CHECKPOINT, `subject_sha` полной формы): фиксирует полную форму `9cc83e8…` для событий `0002`–`0005` (сами события не редактировались) и признаёт отклонение terminal-last. События `0001`–`0005` и `summary.md` execution `EX-NL1-002-R1` не изменялись |
| `4a1b5d5a8d1b41ef4bd95a68cd33394d5a5055b8` | **F-3 surface:** открыто execution `EX-NL1-002-R1-REPAIR1` (passport + события `0001`–`0003`) — контракт-чистая последовательность публикации: первый event `WORK_ORDER_STARTED`, терминальное событие будет последним, все `subject_sha` полные 40-hex. Это execution — superseding-поверхность ДЛЯ ВАЛИДАЦИИ (не для научных фактов) в духе прецедента `EX-NL0-002-R1-REPAIR1` |
| (этот коммит) | `docs/evidence/NL1-002/REPAIR_MAP_R2_R1.md` — настоящая карта |

## 3. Решение по `subject_sha` (полная форма)

Везде в новых/дополняемых записях используется `9cc83e8599c76366a6ba8c5bc49f7398f5fca64f` — полная 40-hex форма freeze-commit, который R2 подтвердил как frozen-before-run subject кампании (верdict §2, D5b: freeze `5c8774f9…` → repair `9cc83e85…` (S001 started-event) → прогоны `ec67752…`). Это то же значение, которое старые work-события публиковали сокращённо как `9cc83e8`. `manifest.json` каждого прогона, все записи `artifacts`, все новые эксперимент-события и event `0006` согласованы по этому значению (validator-warning «subject_sha differs» отсутствует). Subject самой ветки/верификации (`ec7e3ed…`) остаётся идентификатором кандидата на review и в эксперимент-поверхность не вносится.

## 4. Результаты валидаторов (полные логи: `C:\NanoLab\scratch\nl1-002-repair-r2\`, disposable)

**До ремонта (воспроизведено на c44b209 перед изменениями):**

| Команда | Результат |
|---|---|
| `CONTROL_EXPERIMENT validate` ×4 run-каталогов | `AttributeError: 'str' object has no attribute 'get'`, **exit 1** на всех 4 — совпадает с F-1 |
| `CONTROL_WORK validate EX-NL1-002-R1` | ok=false, **exit 3**: 4× `invalid subject_sha` (0002–0005) + `terminal/handoff event must be last` — совпадает с F-2/F-3 |

**После ремонта (HEAD `4a1b5d5a…` перед публикацией карты):**

| Команда | Результат |
|---|---|
| `CONTROL_EXPERIMENT.ps1 validate …/E1-R1-S001` | **ok=true, errors=[], warnings=[], exit 0** |
| `CONTROL_EXPERIMENT.ps1 validate …/E1-R1-P001` | **ok=true, errors=[], warnings=[], exit 0** |
| `CONTROL_EXPERIMENT.ps1 validate …/E1-R1-P002` | **ok=true, errors=[], warnings=[], exit 0** |
| `CONTROL_EXPERIMENT.ps1 validate …/E1-R1-P003` | **ok=true, errors=[], warnings=[], exit 0** |
| `CONTROL_WORK.ps1 validate docs/work/executions/EX-NL1-002-R1-REPAIR1` | **ok=true, errors=[], exit 0** (pre-terminal) |
| `CONTROL_WORK.ps1 validate docs/work/executions/EX-NL1-002-R1` | ok=false, exit 3 — **остаточное задокументированное отклонение**, см. §5 |
| `CONTROL_DEVELOPMENT.ps1 -CheckConsistency` | ok=true, errors=[], warnings=[], exit 0 |

Финальные прогоны после терминального события `EX-NL1-002-R1-REPAIR1` (validate + close на полном наборе) фиксируются в `summary.md` этого execution и в его терминальном event.

## 5. Остаточные отклонения (намеренно НЕ устраняемые правкой истории)

`CONTROL_WORK validate EX-NL1-002-R1` остаётся **exit 3** ровно с 5 ошибками, все — в опубликованных событиях `0002`–`0005`, которые по правилу «старые события не редактируются» исправлены erratum-ом (`0006-repair-completed`), а не правкой:

1. 4× `invalid subject_sha` — сокращённая форма `9cc83e8`; полная форма опубликована в `0006-repair-completed.json`.
2. `terminal/handoff event must be last` — механически неустранимо новыми событиями: добавление нового терминального события нарушает правило «не более одного terminal/handoff», а перемещение/правка `0004` — переписывание истории. Контракт-чистая последовательность публикации перенесена в execution `EX-NL1-002-R1-REPAIR1` (ok=true), что и есть разрешённый WO путь «устрани новой последовательностью событий».

Научно-содержательных отклонений не осталось: R2 подтвердил все исполнительные и числовые факты пакета (§4 вердикта) и требовал именно контрактной починки.

## 6. Что НЕ менялось (гарантии)

- **Научные артефакты:** `energy.dat`, `trajectory.dat`, `last_conf.dat`, `log.dat` всех 4 прогонов — 0 изменений в git (проверка: 16/16 SHA-256+size манифестов совпадают с сырыми git-blob байтами после ремонта, тот же критерий, что R2 D1).
- **Статистика/анализ:** `analyze_energy.sh`, значения observable, `evidence-map.json`, `campaign.md` — не изменялись.
- **`protocol.json`** (включая оракул `ColumnAverage::energy.dat::2::-1.37970256144::0.15`) — не изменялся; acceptance-критерии не пересматривались.
- **Старые события:** 12 эксперимент-событий — только аддитивные идентификаторы (значения нетронуты, diff +2 строки/файл); 5 work-событий `EX-NL1-002-R1` и его `summary.md`/`passport.json` — не изменялись вовсе.
- **Вердикты:** R1-файлы на ветке сохранены как superseded история; вердикты R2 (на `verify/*`/`review/*`) не затронуты.
- **`project/state.json`, `project/plan.json`, документы контроля** — не изменялись.
- **Engine/пины:** пины upstream `00dc7fb9…`, бинаря, входных фикстур (4 digest) — не изменялись.
- Симуляции не запускались; новых научных claims не выставляется; campaign-level `scientific_outcome` остаётся `NOT_EVALUATED`.

## 7. Коммиты ремонта (ветка `work/nl1-002-reference-run-r1`)

```text
c44b209  (старт) merge: record independent verifier verdict R1 (PASS)  [superseded R1, сохранён]
ac5c6cb  experiment(E1): complete run manifests to machine contract (R2 F-1)
6b6dab4  experiment(E1): annotate run events with contract identifiers (R2 F-1)
f78a182  work(NL1-002): erratum event 0006-repair-completed in EX-NL1-002-R1 (R2 F-2/F-3)
4a1b5d5  work(NL1-002): open repair execution EX-NL1-002-R1-REPAIR1 (R2 F-1..F-3)
<этот коммит>  docs(NL1-002): repair map R2->R1 (F-1..F-3 validator evidence)
<terminal commit>  work(NL1-002): REPAIR1 validation event, terminal handoff, HANDOFF_READY
```

## 8. Next action

FRESH VERIFIER: независимая повторная проверка только исправленных поверхностей (R2 §5: «повторная проверка — только исправленных поверхностей») на exact HEAD терминального коммита `EX-NL1-002-R1-REPAIR1`; merge в main — Human Gate.
