# NL5-002 — Fresh Independent Integration/Tooling Review R1

```text
Review id: NL5-002/FRESH_INTEGRATION_REVIEW_R1
Date (UTC): 2026-09-20T10:50:04Z
Reviewer role: REVIEWER (fresh independent session)
Review verdict: REVIEW_VERDICT = PASS  (policy verdict: PASS)
Reviewed integration head: REVIEWED_INTEGRATION_HEAD = 4c67e211f0db78c90366d32f643de92089ed190c
Reviewed tree: REVIEWED_TREE = 641c9cc71545b0bafda039ee0c37c437a638d117
Review base (delta origin): 33935ae
Review scope: TOOLING ONLY (validator/schema/tests); no scientific claim is touched
```

## Независимость

Настоящий review выполнен свежей независимой сессией REVIEWER. Рецензент не является
автором коммитов `616ecea` ("work_cli external execution profile") и `932481e`
("batch-timestamp repeats check reaches external profile"). Ни одно из ранее
опубликованных scientific review/verify заключений кампании NL5-002 не
пересматривалось и не наследовалось: все выводы этого документа получены
собственными механическими проверками рецензента (чтение кода, собственные
эксперименты, собственные negative controls в `/tmp/nc-review-*`, собственные
запуски project gates в собственном detached worktree на exact subject).

## Граница review (claim ceiling)

Review ограничен tooling-дельтой интеграционной ветки `integration/nl5-002-r1`
(`git diff 33935ae..4c67e211`, ровно 3 файла). Научные утверждения кампании
NL5-002 (включая вердикт MISMATCH внешней кампании воспроизведения) данным
review не оцениваются и не затрагиваются. Scientific claim не повышается.

## Reviewed delta

```text
config/control/harness/work-event.schema.v1.json |  4 +-   (2+/2-)
scripts/harness/work_cli.py                       | 55 ++++- (48+/7-)
tests/test_work_cli_external_profile.py           | 165 ++++++++ (new, 9 tests)
3 files changed, 218 insertions(+), 6 deletions(-)
```

Ссылки на код ниже даны для `scripts/harness/work_cli.py` на `4c67e211`
(если не указано иное).

## Результаты по обязательным проверкам (checks 1–8)

### Check 1 — ровно один opener EXTERNAL_EXECUTOR_DISPATCHED, и он лексически первый — PASS

- Выбор профиля: строка 203 `is_external_profile = bool(event_types) and event_types[0] == EXTERNAL_OPENER`; список событий строится из `sorted(events_dir.glob("*.json"))` (строка 136), поэтому `event_types[0]` — лексически первое событие. Opener, не являющийся первым, переводит каталог в standard-профиль, где внешняя лексика отвергается (см. Check 4).
- Ровно один opener: строка 214, `event_types.count(EXTERNAL_OPENER) != 1` → ошибка "external execution profile requires exactly one EXTERNAL_EXECUTOR_DISPATCHED opener". Второй opener (в любом месте, включая post-terminal) — ошибка.
- Negative controls: NC-E1 (дубликат opener — отвергнут), NC-E4 (opener не первый — каталог ушёл в standard-профиль, внешние события отвергнуты как `unsupported event_type`), NC-E9 (opener с event_id `0000-…`, лексически первый, count=1 — валидно).

### Check 2 — ровно один терминал EXTERNAL_RUN_COMPLETED — PASS

- Строки 216–217: `event_types.count(EXTERNAL_TERMINAL) != 1` → ошибка "external execution profile requires exactly one EXTERNAL_RUN_COMPLETED terminal event". 0 терминалов и >=2 терминалов дают одну и ту же ошибку.
- Negative controls: NC-E2 (терминал удалён — отвергнуто), NC-E3 (второй терминал — отвергнуто).

### Check 3 — ORCHESTRATOR только во внешнем профиле — PASS

- Строки 204–205 и 209–211: `allowed_roles` = `EXTERNAL_ALLOWED_ROLES = {"ORCHESTRATOR"}` (строка 28) только при `is_external_profile`; иначе `ALLOWED_ROLES` (строка 18), где ORCHESTRATOR отсутствует → "unsupported actor_role".
- Дополнительно: внешний профиль строг в обратную сторону — любая standard-роль (REVIEWER и т.д.) внутри внешнего каталога отвергается (NC-E8).
- Negative controls: NC-S1 (ORCHESTRATOR в standard-каталоге — отвергнут), NC-S9 (ORCHESTRATOR + CONTINUATION в standard-каталоге — отвергнуты обе оси), NC-E8.

### Check 4 — внешняя лексика отвергается standard-профилем — PASS

- `EXTERNAL_ALLOWED_EVENTS = {"EXTERNAL_EXECUTOR_DISPATCHED", "CONTINUATION", "EXTERNAL_RUN_COMPLETED"}` (строка 27) не пересекается с `ALLOWED_EVENTS` (строка 17); при standard-профиле любое внешнее событие даёт "unsupported event_type" (строки 206–208).
- Negative controls: NC-S2 (EXTERNAL_RUN_COMPLETED в standard-каталоге — отвергнут), NC-E4 (профиль standard_work_order, внешние события отвергнуты).

### Check 5 — standard-профиль поведенчески не изменён — PASS

- Метод: старый валидатор извлечён как `git show 33935ae:scripts/harness/work_cli.py` и запущен против нового на всех 42 опубликованных каталогах `docs/work/executions/EX-*`; сравнивались exit code, `ok` и полный список `errors`.
- Результат: на всех standard-каталогах поведение идентично (ok и список ошибок совпадают 1:1). Различие только на `EX-NL5-002-B-R1` и `EX-NL5-002-B-R2` — и это цель ремонта: старый валидатор их отвергал ("unsupported event_type"/"unsupported actor_role" + "WORK_ORDER_STARTED must be the first event"), новый принимает как `external_execution`.
- Legacy-пути (grandfathering) реально задействованы опубликованными каталогами и вошли в сравнение: сокращённый SHA `9cc83e8` — события 0002–0005 `EX-NL1-002-R1` (`LEGACY_ABBREVIATED_SHA_EVENTS`); batch-timestamp whitelist — 3 события `EX-NL2-002-R1` (`LEGACY_BATCH_TIMESTAMP_EVENTS`). Оба каталога валидируются одинаково старым и новым кодом.
- Добавленное поле вывода `"profile"` (строки 225, 285) — аддитивное; единственный потребитель `inspect_execution` — сам CLI `work_cli` (печать JSON + exit code), CI Check 3 использует exit code. Поведение close-режима не изменено.

### Check 6 — batch-timestamp защита сохранена для обоих профилей — PASS

- Проверка "constant copy timestamp across >= 3 events" (строки 179–199) выполняется ДО ветвления профиля (первая строка ветвления — 203) и накапливает ошибки в общий список `errors`, который возвращается обеими ветками (внешняя ветка возвращает тот же список, строки 219–231). Внешний профиль не может её обойти.
- Negative control: NC-E5 (4 события внешнего каталога с одним timestamp — отвергнуто: "constant copy timestamp across 4 events"). Тест `test_batch_timestamp_repeats_check_reaches_external_profile` (tests/test_work_cli_external_profile.py:150) покрывает то же самое.

### Check 7 — post-terminal CONTINUATION ограничен — PASS

- После терминала во внешнем профиле структурно возможны ТОЛЬКО события `CONTINUATION`: словарь событий закрыт (3 значения, строка 27), а вторые opener/терминал в любом месте отвергаются проверками "ровно один" (строки 214–217). Роль любого post-terminal события обязана быть ORCHESTRATOR (строка 28). Флаг `has_post_terminal_corrections` (строка 229) явно маркирует post-terminal CONTINUATION.
- Это тот же append-only corrections-паттерн, что и в standard-профиле (CONTINUATION_CHECKPOINT/REVIEW_CORRECTIONS после HANDOFF_COMPLETED; строки 245–257); количество post-terminal records нигде не лимитировалось и раньше — новым не является.
- Negative controls: NC-E6 (post-terminal REVIEW_CORRECTIONS — отвергнут как "unsupported event_type"), NC-E3 (post-terminal второй терминал — отвергнут), NC-E1 (post-terminal второй opener — отвергнут), NC-E7 (post-terminal CONTINUATION — валидно, `has_post_terminal_corrections=True`); опубликованный `EX-NL5-002-B-R2` (0005-timestamp-errata) валидируется OK с post-terminal errata.

### Check 8 — схема расширена только необходимыми enum-значениями — PASS

- Метод: структурный JSON-diff `33935ae` vs `4c67e211` для `config/control/harness/work-event.schema.v1.json` (полное дерево, включая `required`).
- Результат: `event_type.enum` +3 (`EXTERNAL_EXECUTOR_DISPATCHED`, `CONTINUATION`, `EXTERNAL_RUN_COMPLETED`), `actor_role.enum` +1 (`ORCHESTRATOR`); прочие изменения — только текст `description` этих двух свойств (документация). `required` идентичен; ни одного другого ослабления ограничений нет.

## Negative controls

Все контролы выполнены в одноразовых копиях под `/tmp/nc-review/fixtures/`
(базы: опубликованные `EX-NL5-002-C-R1` для standard-профиля и
`EX-NL5-002-B-R1` для внешнего), валидатор — CLI `python3 -m harness.work_cli
validate` на `4c67e211`. Ничего из этого не коммитилось.

| Control | Ожидание | Факт |
|---|---|---|
| PC-std: опубликованный standard-каталог | OK | OK (exit 0) — MATCH |
| PC-ext: опубликованный внешний каталог | OK, profile=external_execution | OK, external_execution — MATCH |
| NC-S1: ORCHESTRATOR в standard-каталоге | FAIL, unsupported actor_role | FAIL, 0002-…: unsupported actor_role — MATCH |
| NC-S2: внешнее событие в standard-каталоге | FAIL, unsupported event_type | FAIL, 0003-…: unsupported event_type — MATCH |
| NC-S3: удалено обязательное поле subject_sha | FAIL, missing subject_sha | FAIL, missing subject_sha — MATCH |
| NC-S4: filename != event_id | FAIL, filename must equal event_id | FAIL, сообщение точное — MATCH |
| NC-S5: execution_id события != passport | FAIL, execution_id differs from passport | FAIL, сообщение точное — MATCH |
| NC-S6: дубликат event_id | FAIL, duplicate event_id | FAIL, duplicate event_id — MATCH |
| NC-S7: нарушен лексический порядок | FAIL, events are not lexically ordered | FAIL, сообщение точное — MATCH |
| NC-S8: subject_sha не 40-hex (7-hex, не из whitelist) | FAIL, invalid subject_sha | FAIL, invalid subject_sha — MATCH |
| NC-S9: ORCHESTRATOR+CONTINUATION в standard-каталоге | FAIL по обеим осям | FAIL: unsupported event_type + unsupported actor_role — MATCH |
| NC-E1: дубликат opener | FAIL, exactly one EXTERNAL_EXECUTOR_DISPATCHED | FAIL, сообщение точное — MATCH |
| NC-E2: отсутствует терминал | FAIL, exactly one EXTERNAL_RUN_COMPLETED | FAIL, сообщение точное — MATCH |
| NC-E3: дубликат терминала | FAIL, exactly one EXTERNAL_RUN_COMPLETED | FAIL, сообщение точное — MATCH |
| NC-E4: opener не лексически первый | FAIL; profile=standard_work_order; внешняя лексика отвергнута | FAIL, стандартный профиль, unsupported event_type — MATCH |
| NC-E5: batch-timestamp (>=3 одинаковых) во внешнем профиле | FAIL, constant copy timestamp | FAIL, "constant copy timestamp across 4 events" — MATCH |
| NC-E6: post-terminal событие вне внешнего словаря | FAIL, unsupported event_type | FAIL, 0005-…: unsupported event_type — MATCH |
| NC-E7: post-terminal CONTINUATION (errata) | OK, has_post_terminal_corrections=True | OK, флаг поднят — MATCH |
| NC-E8: standard-роль (REVIEWER) во внешнем каталоге | FAIL, unsupported actor_role | FAIL, сообщение точное — MATCH |
| NC-E9: opener переименован в 0000-… (всё ещё первый, count=1) | OK | OK — MATCH |

Итог: 21/21 контролов MATCH (ожидание = факт по каждому).

## Project gates (собственный запуск на 4c67e211)

```text
python3 -m unittest discover -s tests -t .            -> Ran 369 tests ... OK (exit 0)
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .  -> ok=true, errors=[] (exit 0)
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .          -> ok=true, violations=0, blocking=0 (exit 0)
```

База для сравнения: на `33935ae` тот же набор тестов даёт `Ran 360 tests ... OK`
(дельта +9 = 8 тестов в 616ecea + 1 тест в 932481e, ровно 9 методов в
tests/test_work_cli_external_profile.py).

## Оставшиеся риски / ограничения

- Свободный текст `summary` внутри структурно валидных событий валидатором не
  контролируется (как и в standard-профиле); от искажений содержимого защищает
  неизменяемость git-истории, а не валидатор.
- Внешний профиль не наследует семантические проверки corrections-tail
  standard-профиля (непротиворечивость/монотонность timestamp post-terminal
  CONTINUATION относительно терминала). Словарь и роль ограничены (Check 7), но
  хронология post-terminal errata держится только дисциплиной кампании.
- Ровно один opener/терминал контролируется по числу событий; "правильность"
  момента терминала (что кампания действительно завершена) — научный вопрос вне
  tooling-review.
- Review выполнен на локальной копии exact subject (detached worktree);
  hosted-CI запуск не воспроизводился, но локально проверены те же gates, что
  выполняет hosted-ci.yml (Checks 2, 3, 4, 5).

## Вердикт

```text
REVIEW_VERDICT = PASS
Обязательные проверки 1-8: PASS (8/8)
Negative controls: 21/21 MATCH
Gates: 369 tests OK; consistency ok=true; workflow lint violations=0
Claim ceiling: tooling-only review; scientific claims NL5-002 не затронуты и не повышаются
```
