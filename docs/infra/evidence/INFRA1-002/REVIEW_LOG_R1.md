# Reviewer Reproduction Log — INFRA1-002 (EX-INFRA1-002-R1 review)

**Роль:** независимый FRESH REVIEWER (контекст имплементёра недоступен).
**Дата:** 2026-09-09. **Субъект:** substantive HEAD `0330d15b8af4858596664ed25a9317843c8389df` ветки `infra/infra1-validation-gates-r1`; tip `97ac978` (bookkeeping: `VALIDATION_GATES_R1.md`, events 0002–0004, summary, passport HANDOFF_READY). **Base:** `15a2c9b1b5c095e24e2e1c24afd77feef5361102`.
**Метод:** собственный worktree `C:\NanoLab\review-infra-1-002` @ `0330d15`, все прогоны воспроизведены локально (Windows, Python 3.11.8, stdlib-only), плюс целевые пробы за пределами штатных тестов. Tip-состояние проверено через временный detached worktree @ `97ac978`.

## 1. Scope-аудит

`git diff --name-status 15a2c9b..0330d15` (и до tip `97ac978`) — ровно allowed_paths паспорта:

```text
M  .github/workflows/hosted-ci.yml
A  config/infra/validation-gates.v1.json
A  docs/infra/VALIDATION_GATES_R1.md            (только на tip)
A  docs/work/executions/EX-INFRA1-002-R1/**     (свой execution; 1 event на 0330d15, 4 + summary на tip)
M  scripts/harness/work_cli.py                  (+62/-…)
A  scripts/harness/workflow_lint.py             (+503)
A  tests/__init__.py, tests/test_infra_workflow_lint.py, tests/test_work_cli_corrections.py
```

`project/infra-state.json`, `project/state.json`, science-файлы, чужие `EX-*` — не тронуты ни на 0330d15, ни на tip. Drift base vs `origin/main` (`a4533ab` = base + PR #27, science addendum) задокументирован имплементёром (event 0001, VALIDATION_GATES_R1 §8.1); merge-base = base → diff PR чистый. Нарушений scope не обнаружено.

## 2. Блокирующий критерий (a): NC-1 механический тест

Среда: `$env:PYTHONPATH='scripts'`; конфиг `config/infra/validation-gates.v1.json`.

| Проба | Команда (сокр.) | Результат |
|---|---|---|
| Позитив: реальный workflow | `python -m harness.workflow_lint --root .` | `"ok": true`, 0 violations, **exit 0** |
| Негатив NC-1: `runs-on: nanolab-cpu` | fixture из копии hosted-ci.yml (replace) | **exit 1**, `NC1_SELF_HOSTED_LABEL`: «an untrusted PR route cannot select trusted nodes» |
| Негатив NC-1: `runs-on: self-hosted` | там же | **exit 1**, `NC1_SELF_HOSTED_LABEL` |
| Обход-проба: `runs-on: &cpu nanolab-cpu` + `runs-on: *cpu` (валидный GitHub-синтаксис алиасов) | fixture `probe-alias-valid.yml` | **exit 0, ok=true — ОБА job'а не пойманы** (→ MAJOR-2) |
| Обход-проба: `on: [push, pull_request_target]` | fixture `probe-on-list.yml` | **exit 0 — forbidden-триггер не пойман**, правила триггеров целиком пропущены (→ MAJOR-1) |
| Обход-проба: `on: push` (scalar) | fixture `probe-on-scalar.yml` | exit 0 — то же семейство пропуска (→ MAJOR-1) |
| Обход-проба: `${{ secrets['DEPLOY_TOKEN'] }}` на compliant-каркасе | fixture `probe-secrets-bracket2.yml` | **exit 0 — NC7_SECRETS_REFERENCE отсутствует** (→ MINOR-1) |
| Multi-doc (`---` два документа, второй с pull_request_target + nanolab-cpu + contents:write) | fixture `probe-multidoc.yml` | exit 1: нарушения ОБОИХ документов слиты в один отчёт (пересечение/перезапись ключей) — недetection-дыры нет, но семантика расхождения с GitHub-парсером не определена (→ NOTE-3) |
| Tab-индентация | fixture `probe-tabs.yml` | exit 1, unparseable — fail closed корректен |

Полнота правил: NC-1 (literal labels, префикс `nanolab-hpc-`, case-insensitive, `${{ }}`, missing runs-on), NC-2 (mapping-форма `on:`), NC-4 (workflow+job, write/read-all/none), NC-6 (int, [1,60], required), NC-7 (dot-форма), pin 40-hex/digest, NOTE-3, fail-closed на непарсируемом — подтверждены штатными тестами и моими прогонами. Дыры — только в формах, перечисленных в findings.

## 3. Блокирующий критерий (b): corrections-aware validate

| Проба | Результат |
|---|---|
| `work_cli validate` по всем 10 `EX-*` (worktree @ 0330d15) | **10/10 OK** (`pass=10 fail=0`) |
| Базовый валидатор (`git show 15a2c9b:scripts/harness/work_cli.py`) на `EX-NL1-002-R1` | **exit 3, ровно 5 residual ошибок**: 4× `invalid subject_sha` (0002–0005, фактический SHA в файлах = `9cc83e8`, 7-hex) + `terminal/handoff event must be last` (0005/0006 — пост-терминальные CONTINUATION_CHECKPOINT) |
| Тот же каталог новым валидатором | OK (0 ошибок, `has_post_terminal_corrections=true`) |
| Негатив: unmarked post-terminal (`HANDOFF_COMPLETED` → `VALIDATION_RECORDED`) | **FAIL** с «must be review-corrections events» (проба + unit-тесты) |
| Второй terminal после corrections; `REVIEW_CORRECTIONS` до handoff | FAIL (unit-тесты) |
| Пробa: `REVIEW_CORRECTIONS` с timestamp 2020 при handoff 2026 | OK — timestamp хвоста не сравнивается с terminal-событием (осознанно, легаси `EX-NL1-002-R1` 0005=11:16:30Z < 0004=11:30:00Z; задокументировано §2.1 доки) (→ NOTE-2) |
| Проба: `REVIEW_CORRECTIONS` от `actor_role=IMPLEMENTER` | OK — роль не ограничена (→ MINOR-3) |
| Проба: `REVIEW_CORRECTIONS` с 7-hex SHA у **нового** события | OK — tolerance применён ко всем событиям, не только легаси (→ MINOR-2) |
| Tip: `EX-INFRA1-002-R1` @ 97ac978 (events 0001–0004, HANDOFF_COMPLETED последним) | `ok: true` |

Ослабление обычного потока: НЕ обнаружено (terminal-last сохранён для исполнений без corrections; unmarked после terminal — hard error).

## 4. Тесты, интеграция, схемы

- `python -m unittest discover -s tests -t .` → **Ran 34 tests, OK** (20 lint + 14 corrections).
- hosted-ci.yml @ 0330d15: Check 3 — все `EX-*`, отсутствие каталогов → exit 1; Check 4 — lint blocking; Check 5 — unittest; все через `set -euo pipefail` (exit-коды не глотаются `tee`). `permissions: contents: read`, `timeout-minutes: 15`, concurrency, pin `actions/checkout@93cb6ef…`/`upload-artifact@330a01c…`, `persist-credentials: false` — не деградировали. `ready_for_review` добавлен (NOTE-3 закрыт).
- Схемы: `work-event.schema.v1.json` по-прежнему `^[0-9a-f]{40}$` и enum без `REVIEW_CORRECTIONS`; `execution-passport.schema.v1.json` — `checkpoint` `^NL[0-8]$` против `checkpoint: "INFRA1"` в паспорте (третий INFRA-прецедент подряд; механической валидации по схеме нет — расхождение без функционального конфликта, sync — control WO, зафиксировано в `non_goals`).

## 5. Артефакты проб

Fixtures и probe-скрипты — во временном каталоге (`%TEMP%\lfx-e330d99b46be4adaba1fd15debf2a21b`), в репозиторий не вносятся; команды в этом логе воспроизводимы дословно.
