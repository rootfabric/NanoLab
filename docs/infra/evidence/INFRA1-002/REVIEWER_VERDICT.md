# Reviewer Verdict — INFRA1-002 «Add PR validation gates»

**Роль:** независимый FRESH REVIEWER (контекст имплементёра недоступен).
**Дата:** 2026-09-09. **Вердикт:** `FIX_REQUIRED` (оба блокирующих критерия приёмки воспроизведены успешно; отказ — из-за обходов блокирующего NC-линта конструкциями первой-class YAML/GitHub-синтаксиса — см. MAJOR-1/MAJOR-2).
**Субъект:** substantive HEAD `0330d15b8af4858596664ed25a9317843c8389df` (ветка `infra/infra1-validation-gates-r1`); tip `97ac978` отличается только bookkeeping (док `VALIDATION_GATES_R1.md`, events 0002–0004, summary, паспорт → `HANDOFF_READY`) и проверен отдельно.
**Base:** `15a2c9b1b5c095e24e2e1c24afd77feef5361102`. Репродукция всех прогонов: [`REVIEW_LOG_R1.md`](REVIEW_LOG_R1.md).

---

## 1. Итог по пунктам проверки

| # | Пункт | Результат |
|---|---|---|
| 1 | Scope diff `15a2c9b..0330d15` | **ЧИСТО** — ровно allowed_paths паспорта; state-файлы, science, чужие `EX-*` не тронуты (включая tip). Drift с `origin/main` (`a4533ab` = base + science-PR #27) задокументирован имплементёром, merge-base = base — не нарушение |
| 2a | Блокирующий критерий (a): NC-1 негатив/позитив | **ВОСПРОИЗВЕДЁН**: `runs-on: nanolab-cpu` и `runs-on: self-hosted` → exit 1 (`NC1_SELF_HOSTED_LABEL`); реальный hosted-ci.yml → exit 0. НО: см. MAJOR-1/MAJOR-2 — есть обходные формы |
| 2b | Блокирующий критерий (b): corrections-aware | **ВОСПРОИЗВЕДЁН**: 10/10 `EX-*` OK; базовый валидатор на `EX-NL1-002-R1` = ровно 5 residual-ошибок (4× abbreviated `subject_sha` `9cc83e8` в 0002–0005 + terminal-last) → новым валидатором OK; unmarked post-terminal → FAIL. Дыры класса «произвольное событие после handoff» нет: любой тип вне corrections-класса — hard error |
| 4 | YAML-subset парсер | Fail-closed **частично**: непарсируемое (табы, битые структуры) → `WORKFLOW_UNPARSEABLE` exit 1; но anchors/aliases, scalar/flow-форма `on:` и multi-doc молча разбираются в «не то, что исполнит GitHub» (MAJOR-1/MAJOR-2, NOTE-3) |
| 5 | Workflow-интеграция | **OK**: Check 3 — все `EX-*` fail-closed; новые Check 4 (lint, blocking) и Check 5 (unittest), всё под `set -euo pipefail`; NOTE-3 закрыт (`ready_for_review`); `permissions: contents: read`, `timeout 15`, concurrency, pin SHA, `persist-credentials: false` — не деградировали |
| 6 | Тесты | **34/34 OK**; покрытие негативов штатное — для literal-подмножества полное; негативы за пределами подмножества отсутствуют (они и не ловятся — см. findings) |
| 7 | Схемы/события/паспорт | `checkpoint: "INFRA1"` против `^NL[0-8]$` — **третий INFRA-прецедент подряд**, механической валидации схемы нет, sync отложен в control WO осознанно (зафиксировано в `non_goals` конфига) — к сведению, кандидат в control WO (расширение паттерна `(NL\|INFRA)[0-7]` + enum `REVIEW_CORRECTIONS`) |

## 2. Ответы на специальные вопросы review

**Коррекции-marker: не открывает ли дыру?** Механической дыры нет. После terminal/handoff валидны только `CONTINUATION_CHECKPOINT` (легаси-написание) и `REVIEW_CORRECTIONS`; любой другой тип — hard error (проверено негативом и пробой). Семантическая рыхлость есть (MINOR-3): тип-класс единственный критерий «коррекционности» — `CONTINUATION_CHECKPOINT` после handoff принимается с любым содержимым summary, роль автора не ограничена (проба: `REVIEW_CORRECTIONS` от `IMPLEMENTER` → OK), ссылка на исправляемое событие не требуется, timestamp хвоста не сравнивается с timestampом terminal-события (проба: 2020 при handoff 2026 → OK; легаси-мотив задокументирован имплементёром §2.1). Сдерживающие факторы: events immutable, git-durable, содержимое проходит review. Для R1 приемлемо; рекомендация — будущим control WO: для новых исполнений только `REVIEW_CORRECTIONS` (+ роль из `REVIEWER/VERIFIER/DIRECTOR` + поле `corrected_event_refs`).

**Tolerance `subject_sha` 7..40 — легитимен?** Да, как legacy-compat: 4 residual-ошибки `EX-NL1-002-R1` — это реальные immutable-события canonical main с `9cc83e8`; альтернатива (40-hex повсюду) делала бы каталог вечно красным. Осознанное отклонение от `work-event.schema.v1.json` (`^[0-9a-f]{40}$`) задокументировано (валидатор = floor, schema-sync — control WO). Но: tolerance механически применяется ко **всем** событиям, включая новые (проба: новое событие с 7-hex → OK), а «легаси-ограничение» существует только в тексте конфига/дока (MINOR-2).

**«Не ослабление ли валидатора?»** Обычный поток не ослаблен: terminal-last сохранён; unmarked post-terminal — FAIL; второй terminal — FAIL; `REVIEW_CORRECTIONS` до handoff — FAIL. Ослаблена только общая строгость `subject_sha` (MINOR-2).

## 3. Findings

### MAJOR-1 — обход NC-2/NOTE-3: `on:` в scalar/flow-форме полностью выводит триггеры из-под линта
`on: [push, pull_request_target]` и `on: push` — валидный GitHub workflow-синтаксис. Правила `NC2_FORBIDDEN_TRIGGER`, `NC2_TRIGGER_NEEDS_BASELINE_REVISION`, `NOTE3_PR_TYPES_READY_FOR_REVIEW` выполняются только при `isinstance(triggers, dict)` (`workflow_lint.py:349`) — иначе ветка молча пропускается. Проба: workflow с `on: [push, pull_request_target]` → **exit 0, ok=true**. Слияние в `main` такого файла проходит блокирующий Check 4, и после merge `pull_request_target` (FORBIDDEN_R1) активен. Противоречит заявке конфига `"blocking": true` для NC-2/NC-7 и док-строке «fail closed: всё, что парсер не понимает» (парсер это «понимает» — как не-словарь). **Минимальный ремонт:** при `on:` не-dict — либо проверить элементы списка против forbidden/reserved, либо блокирующее нарушение (fail-closed); плюс правило «`on:` обязан присутствовать».

### MAJOR-2 — обход NC-1: anchors/aliases в `runs-on`
`runs-on: &cpu nanolab-cpu` + второй job `runs-on: *cpu` — валидный GitHub workflow (GitHub резолвит anchors), линт: **exit 0, ok=true** — литерал `&cpu nanolab-cpu` не совпадает с forbidden-набором и не содержит `${{` (`workflow_lint.py:384-391`). NC-1 — заголовочный блокирующий критерий и будущий защитник label-namespace при INFRA2 (активация self-hosted) — не должен иметь форму молчаливого прохода. **Минимальный ремонт:** наличие `&`/`*`-якорных токенов в значениях `runs-on` (или вообще в разобранных скалярах) → блокирующее нарушение / `WORKFLOW_UNPARSEABLE` (fail-closed, соответствует заявленной семантике).

### MINOR-1 — NC-7: bracket-форма секретов не ловится
`${{ secrets['DEPLOY_TOKEN'] }}` — валидное expression; regex `SECRETS_REFERENCE` (`secrets\.[A-Za-z_]…`, `workflow_lint.py:34`) покрывает только dot-форму. Проба на compliant-каркасе: exit 0. Ремонт: добавить bracket-альтернативу `secrets\s*\[`. Индирекция через `env:` не линтабельна — принять и задокументировать.

### MINOR-2 — tolerance `subject_sha` 7..40 применён глобально, а не к легаси
`SUBJECT_SHA` заменяет `SHA40` для **всех** событий (`work_cli.py`), включая новые; конфиг-заметка «abbreviated accepted only as legacy» механически не обеспечена. Схема осталась 40-hex — расхождение floor/ceiling растёт. Ремонт (следующий раунд/control WO): 40-hex обязателен для событий с timestamp ≥ даты поставки этого WO, либо scope tolerance по execution-каталогам (`legacy_targets` уже перечислены в конфиге).

### MINOR-3 — семантика corrections-класса рыхлая (см. §2)
Класс-маркер по `event_type` только; `CONTINUATION_CHECKPOINT` продолжает работать как corrections без любого маркера намерения; роль/ссылки/timestamp-vs-handoff не ограничены. Для R1 — приемлемо (задокументировано), к следующей ревизии — см. §2.

### NOTE-1 — NOTE-3-правило перезаряжается на workflow без `pull_request`
Mapping-форма `on:` без `pull_request` (например, push-only) даёт ложное `NOTE3_PR_TYPES_READY_FOR_REVIEW` (`pr_types = None` → violation). Направление fail-closed (availability, не безопасность); уточнить формулировку правила.

### NOTE-2 — timestamps corrections-хвоста не сравниваются с terminal-событием
Осознанно (легаси `EX-NL1-002-R1`: 0005=11:16:30Z < handoff 0004=11:30:00Z, док §2.1). Зафиксировано как известное ограничение; не дефект текущей поставки.

### NOTE-3 — multi-doc и «валидный, но вне подмножества» YAML
`---`-документы молча сливаются (обе пробы нарушений видны — направление over-detection, дыры нет, но семантика расходится с single-document GitHub-парсером); экзотические, но валидные для GitHub конструкции (например, выравнивание элементов последовательности не под 2-пробельный паттерн парсера) дают ложный `WORKFLOW_UNPARSEABLE` — fail-closed ценой availability. Рекомендация: явно отвергать multi-doc; держать подмножество синхронизированным с фактическими workflows.

### NOTE-4 — `checkpoint: "INFRA1"` против `^NL[0-8]$` — третий INFRA-прецедент подряд
Известный класс (NOTE-1 Director-вердикта INFRA1-001); валидатор паспорта паттерн не проверяет, конфликта нет. Расширение схемы — control WO (так же, как enum `REVIEW_CORRECTIONS` + 40-hex sync). Кандидат накапливает повторения — предлагаю включить в ближайший control WO пакетно.

## 4. Вердикт и ремонтная карта

**`FIX_REQUIRED`** — приёмка INFRA1-002 в текущем виде невозможна: оба blocking-критерия (a)/(b) воспроизведены, corrections-семантика корректна и не ослаблена, интеграция в hosted-ci аккуратна, scope чист, документация честно фиксирует известные ограничения, — но сам линт, являющийся предметом поставки, имеет обходы (MAJOR-1/MAJOR-2), противоречащие его собственной fail-closed-заявке и статусу `blocking` в конфиге. Направление ремонта — точечное, без пересмотра архитектуры:

1. MAJOR-1: non-dict `on:` → проверки forbidden/reserved по элементам или fail-closed нарушение; absence of `on:` → нарушение. (+ негативные тесты scalar/flow-форм).
2. MAJOR-2: `&`/`*`-токены в `runs-on` (или в любых разобранных скалярах) → fail-closed нарушение. (+ негативный тест `runs-on: &cpu nanolab-cpu` / `*cpu`).
3. MINOR-1: bracket-секреты в regex NC-7 (+ тест).
4. MINOR-2/NOTE-4: отложить в control WO (schema/subject_sha/checkpoint-паттерн пакетно) либо ограничить tolerance легаси-каталогами в следующем раунде этого же WO.
5. Обновить `VALIDATION_GATES_R1.md` §3 (формулировка fail-closed) и `validation-gates.v1.json` — только новой фиксацией находок, без переписывания истории.

После ремонта — повторная негативная матрица reviewer'а (те же пробы `probe-*` из `REVIEW_LOG_R1.md` §2) и переход к Verifier/Director. Не merge'ить.

## 5. Границы проверки

Проверялись файлы ветки `0330d15`/`97ac978` и локальные прогоны; live-прогон GitHub-hosted runner недоступен reviewer'у (первый TR-PR прогон останется owner-evidence по HOSTED_CI_R1 §9). GitHub-поведение constructs (anchors/aliases, `on:`-формы, multi-doc) опирается на публичную семантику GitHub Actions; сторона линта всех утверждений воспроизведена локально exit-кодами.

**Exact HEADs:** subject `0330d15b8af4858596664ed25a9317843c8389df`; tip `97ac978`; эта ревизия — ветка `review/infra1-validation-gates-r1` (см. git log).
