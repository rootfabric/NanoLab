# Control Schemas — `config/control/harness/`

Схемы в этом каталоге — машиночитаемые контракты (JSON Schema draft 2020-12) control-поверхности harness'а. README фиксирует их отношение к механическому валидатору и известные расхождения. Обновлено контрольным WO `EX-CTRL-LINTSCHEMA-R1` («lint fail-closed hardening + schema sync», branch `control/lint-schema-sync-r1`).

## Иерархия: схема (ceiling) и валидатор (floor)

```text
work-event.schema.v1.json            execution-passport.schema.v1.json
  контракт-потолок (ceiling)           контракт-потолок (ceiling)
            │                                      │
            ▼                                      ▼
scripts/harness/work_cli.py  —  enforcement floor (hosted-ci Check 3/5)
```

**Ни один механизм CI сейчас не валидирует events/passports против JSON-схем механически** (проверено при INFRA1-002, `VALIDATION_GATES_R1.md` §2.4): авторитативная механическая проверка — `work_cli` (правила см. `docs/infra/VALIDATION_GATES_R1.md` §2). Схема строже валидатора там, где валидатор несёт legacy-tolerance; валидатор может быть строже схемы в семантических правилах (порядок событий, роли, монотонность timestamps), которых схема не выражает.

## work-event.schema.v1.json

- `event_type` — enum, синхронизирован с `ALLOWED_EVENTS` валидатора, включая **`REVIEW_CORRECTIONS`** (schema sync, `EX-CTRL-LINTSCHEMA-R1`; ранее enum отставал от валидатора после repair R1 INFRA1-002). Семантика: dedicated post-terminal review-corrections marker; валидатор дополнительно требует размещение только после terminal/handoff события и роль автора `REVIEWER`/`VERIFIER`/`DIRECTOR` (`VALIDATION_GATES_R1.md` §2.1).
- `subject_sha` — **строго `^[0-9a-f]{40}$`** (полный 40-hex git SHA) для каждого события.
- `CONTINUATION_CHECKPOINT` остаётся в enum как легаси-написание corrections-класса, уже опубликованное в canonical main (см. `VALIDATION_GATES_R1.md` §2.1).

## execution-passport.schema.v1.json

- `checkpoint` — паттерн **`^(NL[0-8]|INFRA[0-7])$`**: научные checkpoint'ы `NL0..NL8` и compute-capability checkpoint'ы `INFRA0..INFRA7`. До `EX-CTRL-LINTSCHEMA-R1` паттерн был `^NL[0-8]$` и не покрывал INFRA-исполнения (`EX-INFRA0-001-R1`, `EX-INFRA1-001-R1`, `EX-INFRA1-002-R1` несут `checkpoint: INFRA*`) — REVIEWER R1 NOTE-4, «третий INFRA-прецедент подряд»; настоящий sync закрывает прецедент (четвёртый не накапливается). Практический валидатор паттерн `checkpoint` не проверяет — расхождение было без функционального конфликта.
- `base_sha` — строго `^[0-9a-f]{40}$`.

## Известное расхождение floor/ceiling: 4 легаси-события с 7-hex `subject_sha`

В immutable-событиях canonical main опубликованы сокращённые SHA; редактировать их запрещено (AGENTS.md: corrections — только новым event). Валидатор `work_cli` принимает abbreviated `7..39`-hex **только** для exact-пар `(execution_id, event_id)` из `LEGACY_ABBREVIATED_SHA_EVENTS` (provenance: скан `docs/work/executions/EX-*/events/*.json` на canonical `a4533ab`, 2026-09-09; других сокращённых SHA нет):

| execution_id | event_id | subject_sha |
|---|---|---|
| `EX-NL1-002-R1` | `0002-campaign-runs-completed` | `9cc83e8` |
| `EX-NL1-002-R1` | `0003-validation-recorded` | `9cc83e8` |
| `EX-NL1-002-R1` | `0004-handoff-completed` | `9cc83e8` |
| `EX-NL1-002-R1` | `0005-resource-evidence-committed` | `9cc83e8` |

**Эти 4 события остаются невалидными по данной схеме** (`^[0-9a-f]{40}$`) — это приёмлемое, осознанное расхождение: схема — потолок для новых событий, валидатор — enforcement floor с explicit whitelist'ом выше схемы (whitelist в `work_cli` выше схемы). Переиспользование легаси-значения или пары `(execution_id, event_id)` в другом исполнении tolerated не является. Все прочие события — строго 40-hex. Сверка схемы с whitelist'ом и синхронизация enum/паттернов выполнены `EX-CTRL-LINTSCHEMA-R1`; после изменения схем все валидаторы на всех `EX-*` дают 10/10 OK (hosted-ci Check 3 остаётся зелёным).
