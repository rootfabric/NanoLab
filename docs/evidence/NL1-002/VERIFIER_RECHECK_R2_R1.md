# NL1-002 — VERIFIER RECHECK R2→R1 (повторная проверка исправленных поверхностей)

**Вердикт по ремонту: `PASS`** — все три находки R2 (F-1, F-2, F-3) устранены; научное содержание подтверждено неизменным. Аддендум к `VERIFIER_VERDICT_R2.md` (FIX_REQUIRED) @ `149feda3fe16ce63afaecf52a4d4b8ae83325dd7`; полный вердикт остаётся в силе, блокировка снята.

- Fresh-session VERIFIER R2 (та же независимая сессия, что вынесла FIX_REQUIRED; проверены ТОЛЬКО исправленные поверхности, как оговорено в вердикте §5).
- Проверяемое дерево: ветка `work/nl1-002-reference-run-r1`, repair-span `c44b209..09aae04` (7 коммитов, публично на origin, без rewrite — родитель `09aae04` = `ab78759` = parent-цепочка от `c44b209`).
- REPAIRED_CANDIDATE_HEAD: **`ab78759b717d21eccf80950ec29613fbe1e74224`** (substantive HEAD, tree `849d7d7fa8134de7117238dbd9c0fb9eb4d925a7`), tip **`09aae04e18eae1046c9869ff17538a375b869beb`** (добавляет только terminal event/summary/passport-status REPAIR1).
- Заметка к dispatch: в задании на recheck binding указан как `ab78759b717b21e…` — транскрипционная опечатка (b↔d); авторитетный источник — сама ветка: `git log` и self-binding в `EX-NL1-002-R1-REPAIR1/events/0005-handoff-completed.json` + `summary.md` фиксируют именно `…b717d21e…`, и проверка велась по нему.
- Метод: detached-worktree на candidate и на tip из bare-репозитория; валидаторы запущены из дерева ветки (`scripts/harness` бит-в-бит идентичны base — ремонт их не менял, `git diff c44b209..09aae04 -- scripts/ config/ docs/control/ project/` пуст).

## 1. Repair Map — прочитана и сверена

`docs/evidence/NL1-002/REPAIR_MAP_R2_R1.md` @ `09aae04`: root-cause F-1/F-2/F-3 соответствуют находкам R2 дословно (включая точные тексты ошибок валидаторов); заявленные изменения совпали с фактическим diff; раздел «Что НЕ менялось» подтверждён проверками §5 ниже; residual-политика (§5 карты) признана корректной (см. §6 аддендума).

## 2. F-1: artifacts.manifest.json ×4 — контрактная форма, отображение без потерь

- Все 4 файла на candidate HEAD — контрактный массив `{"schema_version":1,"artifacts":[…]}`; каждая запись содержит обязательные поля контракта: `name`, `sha256`, `size_bytes`, `producer_run_id`, `subject_sha`, `storage_location` (+ `producer_command`); `subject_sha` = полная форма `9cc83e8599c76366a6ba8c5bc49f7398f5fca64f` везде согласована.
- Дайджесты/размеры 16/16 сохранены 1:1 (сверка с манифестами R2 и сырыми git-blob байтами — §5).
- Superseded-оригиналы: `artifacts.manifest.v1-superseded.json` ×4 **byte-equal** blob'ам до ремонта (`git rev-parse c44b209:<path>` = `09aae04:<superseded>` по blob SHA-1, 4/4).
- `manifest.json` ×4 дополнены строго аддитивно: S001 +5 ключей (`subject_sha`/`claim_ceiling`/`model`/`observables`/`stop_conditions`), P001–P003 +6 (+`resource_budget`); существующие ключи не изменялись (проверен diff S001 — только добавления).
- События `0001`–`0003` ×4: строго аддитивно `experiment_id`/`subject_sha` (+2 строки/файл, значения нетронуты); опубликован новый event `0004-repair-manifest-contract` (RUN_CHECKPOINT) в каждом run-каталоге, filename = event_id.
- Контракт (`config/control/harness/artifact-manifest.schema.v1.json`) существовал ДО ремонта (есть в дереве `c44b209`) — ремонт конформен существующему контракту, контракт не подгонялся под пакет.

## 3. F-1: воспроизведение CONTROL_EXPERIMENT validate ×4 → exit 0

Чистый прогон на tip `09aae04` (та же команда, что давала exit 1/AttributeError в R2):

```text
CONTROL_EXPERIMENT validate E1-R1-S001 → ok=true, errors=[], warnings=[], exit 0
CONTROL_EXPERIMENT validate E1-R1-P001 → ok=true, errors=[], warnings=[], exit 0
CONTROL_EXPERIMENT validate E1-R1-P002 → ok=true, errors=[], warnings=[], exit 0
CONTROL_EXPERIMENT validate E1-R1-P003 → ok=true, errors=[], warnings=[], exit 0
```

Дополнительно `CONTROL_DEVELOPMENT --check-consistency` → ok=true, exit 0.

## 4. F-2/F-3: EX-NL1-002-R1-REPAIR1 — контракт-чистая поверхность

- `CONTROL_WORK validate` → **ok=true, exit 0**; `CONTROL_WORK close` → **ok=true, exit 0**.
- Последовательность событий: `WORK_ORDER_STARTED → CONTINUATION_CHECKPOINT → IMPLEMENTATION_COMMITTED → VALIDATION_RECORDED → HANDOFF_COMPLETED` — терминальное событие последнее, ровно одно; все `subject_sha` — полные 40-hex.
- `passport.json`: `repair_of: "EX-NL1-002-R1"`; `verdict_repaired: "FIX_REQUIRED (VERIFIER R2, verify/nl1-002-reference-run-r2 @ 149feda…)"`; `base_sha: ec7e3ed…`; `status: HANDOFF_READY` — **ACCEPTED/self-acceptance нет**; merge остаётся Human Gate.
- Terminal event `0005` привязывает repair к exact `ab78759b717d21e…` + tree `849d7d7f…`; `summary.md` содержит literal BASE_HEAD/REPAIRED_CANDIDATE_HEAD/REPAIRED_CANDIDATE_TREE — binding воспроизводим и совпал с фактическим git-состоянием.
- Erratum в старом execution: новый event `EX-NL1-002-R1/events/0006-repair-completed.json` (CONTINUATION_CHECKPOINT, полная 40-hex subject_sha) фиксирует полную форму `9cc83e8…` для событий `0002`–`0005` и признаёт отклонение terminal-last; сами старые события/summary/passport старого execution не редактировались (в diff отсутствуют).

## 5. Гарантии неизменности науки — подтверждены

- `git diff --name-status c44b209..09aae04` = 37 файлов, ровно заявленный ремонтный периметр (REPAIR_MAP, REPAIR1 execution ×8, erratum 0006, 4× artifacts.manifest.json, 4× superseded-копии, 12 событий ×аддитивно, 4× manifest.json, 4× new 0004-events). **НЕ** входят: `artifacts/energy.dat|trajectory.dat|log.dat|last_conf.dat`, `protocol.json` (оракул `−1.37970256144±0.15` нетронут), `evidence-map.json`, `campaign.md`, `analyze_energy.sh`, `summary.md` прогонов, `run-resources/**`, `docs/work/executions/EX-NL1-002-R1/{passport.json,summary.md,events/0001–0005}`, `scripts/`, `config/`, `docs/control/`, `project/state.json`, `project/plan.json`.
- Независимый повтор дайджест-проверки R2 (D1) на tip `09aae04`: **16/16 sha256+size MATCH** vs новые контрактные манифесты, 0 mismatches; деревья: `E1-R1` 52 файла (44 + 4 superseded + 4 new events), `docs/evidence/NL1-002` 12 (10 @ c44b209 + REPAIR_MAP).
- Научные значения не пересчитывались и не менялись: R2-факты (avg по 4 прогонам до 11 знаков, SD 0.00832919790, seeds, ресурсы) остаются привязанными к тем же blob-байтам; симуляции в ремонте не запускались; `scientific_outcome` остаётся `NOT_EVALUATED`; новых claims нет.

## 6. Остаточные отклонения старого EX-NL1-002-R1 — приемлемы

`CONTROL_WORK validate EX-NL1-002-R1` на tip → exit 3 ровно с 5 задокументированными ошибками (4× `invalid subject_sha` в `0002`–`0005` + `terminal/handoff event must be last`). Приёмлемость пути:
1. Правило харнеса «старые события не редактировать; corrections/superseding — новым event» исключает правку опубликованных событий — erratum `0006` есть корректная механика, полная форма `subject_sha` опубликована.
2. «Terminal-last» для старого execution механически неустранимо без rewrite: новый терминальный event нарушил бы «ровно один terminal», перемещение/правка `0004` — переписывание истории. Контракт-чистая последовательность публикации перенесена в `EX-NL1-002-R1-REPAIR1` (validate/close = exit 0), что и есть заявленный в R2 разрешённый путь починки «новым evidence, без переписывания истории».
3. Отклонение изолировано: это prose-исполнение того же WO, научные факты живут в experiment-поверхности E1-R1, которая валидаторно чиста (§3).

## 7. Итог

Ремонт выполнен в полном соответствии с Repair Map и требованием R2: F-1 устранён (валидаторы ×4 exit 0, контрактная форма, superseded-оригиналы byte-equal), F-2/F-3 устранены на новой контракт-чистой поверхности REPAIR1 (validate/close exit 0, terminal-last, `repair_of`/`verdict_repaired` присутствуют), остаточные 5 ошибок неизменяемого старого execution задокументированы и обработаны разрешённой механикой erratum/superseding. Наука подтверждена неизменной (diff-периметр + 16/16 дайджестов + аддитивность).

**Блокировка FIX_REQUIRED снята.** Subject `work/nl1-002-reference-run-r1` (REPAIRED_CANDIDATE_HEAD `ab78759b717d21eccf80950ec29613fbe1e74224`, tip `09aae04e18eae1046c9869ff17538a375b869beb`) готов к Director checkpoint; merge в main — Human Gate. Повторной научной верификации не требуется (R2 §5).

- Verifier evidence этого recheck: настоящий файл + `VERIFIER_VERDICT_R2.md` (база); disposable scratch верификатора: `C:\NanoLab\scratch\nl1-002-verify-r2\repair-wt{,-tip}` (detached worktrees), отчёты `digests_result_repair.json`.
- Next action: Director checkpoint NL1-002 (Human Gate для merge не изменён).
