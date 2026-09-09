# Summary — EX-INFRA1-002-R1 (INFRA1-002 «Add PR validation gates»)

**Ветка:** `infra/infra1-validation-gates-r1` · **Base:** `15a2c9b1b5c095e24e2e1c24afd77feef5361102` (exact) · **Substantive HEAD:** `0330d15b8af4858596664ed25a9317843c8389df` (tree `c4a0e8283418f2f2fa94fe81891d08de263db7d6`) · **Статус:** `HANDOFF_READY` (PROPOSED; self-accept запрещён) · **Claim:** `C0_SOFTWARE_ONLY`

## Что сделано

| Коммит | Содержание |
|---|---|
| `c7930e5` | START: паспорт `EX-INFRA1-002-R1` + event `0001` (до substantive work) |
| `636ca82` | `feat(harness)`: corrections-aware `work_cli` + 14 unittest |
| `14c4c9c` | `feat(infra)`: workflow NC-линт `scripts/harness/workflow_lint.py` + эталон `config/infra/validation-gates.v1.json` + 20 unittest |
| `0330d15` | `ci(infra1)`: hosted-ci — `ready_for_review` (NOTE-3), Check 3 → все EX-*, новые блокирующие Check 4/5 (NC-линт) и Check 5/5 (unittest) |
| bookkeeping | `docs/infra/VALIDATION_GATES_R1.md`, events `0002–0004`, `summary.md`, паспорт → `HANDOFF_READY` |

## Blocking-критерии приёмки (DIRECTOR_ACCEPTANCE_R1 INFRA1-001)

1. **(a) Механический NC-1-тест** — `NC1_SELF_HOSTED_LABEL` (+dynamic expression / missing runs-on) — блокирующее правило Check 4/5; обязательный негативный тест: fixture `runs-on: nanolab-cpu` → MUST FAIL (exit 1). Эталон: `config/infra/validation-gates.v1.json`.
2. **(b) Corrections-aware `work_cli`** — явный класс `{CONTINUATION_CHECKPOINT, REVIEW_CORRECTIONS}` после terminal/handoff при семантической валидности (валидный git SHA, парсимый timestamp, монотонность хвоста); unmarked пост-терминальные события — FAIL; terminal-last обычного потока сохранён. `EX-NL1-002-R1`: 5 residual ошибок → OK; `EX-INFRA0-001-R1`, `EX-NL1-001-R1` → OK.

## Локальная верификация (на `0330d15`, Windows/Python 3.11)

| Чек | Результат |
|---|---|
| 1/5 json syntax (108 файлов) | OK, 0 bad |
| 2/5 `check-consistency` | `ok=true`, errors/warnings пусто |
| 3/5 `work_cli validate` (10 EX-*) | 10/10 OK (включая 3 легаси-проблемных) |
| 4/5 `workflow_lint --root .` | `ok=true`, 0 violations |
| 5/5 unittest (validator+lint) | 34/34 OK |

Негативные прогоны зафиксированы в тестах: unmarked post-terminal event → FAIL; `nanolab-cpu` → FAIL; `pull_request_target`/`workflow_run`/`schedule`/внешний reusable workflow/`contents: write`/`secrets.*`/no-timeout/timeout 120/тег-pinned action/missing `ready_for_review`/unparseable YAML — все FAIL.

## Открытые риски / ограничения (для review)

1. YAML читается собственным stdlib subset-парсером; непонятный синтаксис — блокирующее `WORKFLOW_UNPARSEABLE` (fail closed), покрытие ограничено подмножеством (VALIDATION_GATES §8.5).
2. Tolerance abbreviated `subject_sha` (7..40 hex) — legacy-compat для immutable событий; новые события обязаны использовать 40-hex по схеме; JSON-схемы не синхронизированы (control WO).
3. NC-5 — review-пункт при INFRA1/2; NC-3 — INFRA2-002; полный NC-6 — INFRA6.
4. Base drift миссии: ветка от exact `15a2c9b` (по директиве); `origin/main` = `a4533ab` (+1 science-коммит PR #27); merge-base = base → diff PR чистый; локальный ref `main` (`6796531`) сознательно не тронут.
5. Owner actions (repo default token read-only, branch protection) — вне git, выполняются владельцем (`HOSTED_CI_R1.md` §6).

## Next action (один)

Независимый REVIEWER на exact substantive HEAD `0330d15b8af4858596664ed25a9317843c8389df`: воспроизвести 5 чеков (`PYTHONPATH=scripts python3 -m harness.workflow_lint --root .`; `python3 -m unittest discover -s tests -t .`; `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-<имя>`) и проверить diff на соответствие allowed_paths паспорта; затем VERIFIER и Director checkpoint; merge — Human Gate.
