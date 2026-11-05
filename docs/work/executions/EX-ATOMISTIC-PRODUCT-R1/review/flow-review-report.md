# FLOW-R1 — независимый Reviewer R1

Вердикт: **FAIL / FIX_REQUIRED**. На exact subject подтверждён один MEDIUM дефект в классификации publication-only; исправление ограничено helper и negative test. Научный conclusion: **NOT_EVALUATED**; claim ceiling **C0_SOFTWARE_ONLY**. Этот отчёт не разрешает merge, запуск science, активацию R2 или Task Bus.

## Subject и независимость

- PR: `rootfabric/NanoLab#95`.
- Base main: `3b567ae33f247b182b2ae451d2cc4598a9e76019`.
- Reviewed HEAD: `ddbc5cb68a5b720cbbaaadeba96f087d82d82732`.
- Reviewed TREE: `4042874fa5dfc39b2defc7f6a5e0b8b955aea67f`.
- Reviewer session/agent: **`/root/flow_review`**, роль REVIEWER. Это отдельная назначенная agent session; Reviewer не автор проверяемой реализации и не выполнял product repair.
- Worktree: `/workspace/scratch/48cb7a65c9c0/NanoLab-flow-review`, detached exact HEAD.
- Executor host/container: `8988315495f9`, Python `3.12.14`. Сессии команды используют общий host и filesystem. **Независимый физический host не заявляется**; отдельная сессия не доказывает external reproduction.
- `git status --porcelain` после проверок: пусто. Product files не изменялись. Все mutation/race/Git fixtures создавались во временных каталогах.

Прочитаны AGENTS, PROJECT_CONTROL, HARNESS_CONTROL, FLOW_THROUGHPUT_R1, текущие state/plan/operational cards, WO-FLOW-THROUGHPUT-R1, HARNESS_REVIEW_AND_EVIDENCE_RU, DEVELOPMENT_HARNESS_RU, HARNESS_AUTONOMOUS_EXECUTION_RU, BRANCHING_AND_GIT_RU; для CI/resource scope — SECURITY_MODEL, EXECUTION_BACKENDS, INFRA ROADMAP/state/plan и RESOURCE_PLAN_CORRECTIONS_R1. Просмотрен полный список diff `base..HEAD`, source diff writer/validator/queue/CI/review-impact/resource, risk/review policies и изменения control/roadmap.

## Finding FLOW-REV-01 — MEDIUM, требуется исправление

**Место:** `scripts/harness/review_impact.py:48–51` (классификация формируется на строках 52–61).

Helper проверяет, что разрешённый publication file имеет mode `100644 blob`, только в **head**. Существующий в base исполняемый `summary.md` с mode `100755` проходит как административное исключение, если в head снять executable bit. Git обозначает такой переход как `M`, поэтому проверка статусов на строках 46–47 его допускает. Путь исключается из обоих subject digests, и helper ошибочно возвращает:

```json
{
  "subject_equivalent": true,
  "classification": "PUBLICATION_ONLY_CANDIDATE",
  "required_action": "Independent delta review and reference existing valid subject evidence"
}
```

Воспроизводимый diff:

```text
:100755 100644 011dbbb 011dbbb M docs/work/executions/EX-TEST/summary.md
```

Содержимое обоих blobs одинаково: `#!/bin/sh\necho executable report\n`. Меняется только Git executable mode.

Это противоречит собственному ограничению helper «symlinks/executable files are not report-only» и позволяет выдать доказанную subject equivalence для изменения существующего executable surface. Изменение режима исполнения может менять поведение вызывающего процесса, поэтому прежнее product evidence нельзя маршрутизировать к облегчённому пути только по допустимому имени файла. Independent delta review и `merge_authorized=false` ограничивают последствия, но не исправляют ложную классификацию.

**Ожидаемое исправление:** для изменённого существующего publication path проверять допустимый regular non-executable blob mode в обоих trees; для нового path base absence допустим. Любой mode/type transition — `FULL_REVIEW`, `subject_equivalent=false`. Добавить negative regression `100755 → 100644`; сохранить уже существующую проверку `100644 → 100755`, symlink, deletion, historical event mutation и product input change.

**Воспроизведение:** `PYTHONPATH=scripts python3 /workspace/scratch/48cb7a65c9c0/flow-review-adversarial.py IndependentFalsifiers.test_review_executable_base_must_not_be_report_only`. На reviewed subject exit **1**, assertion получает `PUBLICATION_ONLY_CANDIDATE` вместо `FULL_REVIEW`.

В текущей публикации PR #95 этот переход не использован. Finding относится к поставляемому reuse/gate helper, не к уже выполненной научной приёмке. Прямого автоматического merge/acceptance helper не выдаёт.

## Команды и результаты

Все команды выполнялись из exact worktree, кроме указанного пути самостоятельного adversarial script.

| Команда / проверка | Exit / результат |
|---|---|
| `git worktree add --detach ../NanoLab-flow-review ddbc5cb68a5b720cbbaaadeba96f087d82d82732` | 0; exact checkout |
| `git rev-parse HEAD HEAD^{tree}` | 0; совпадают с HEAD/TREE выше |
| `git diff --stat 3b567ae33f247b182b2ae451d2cc4598a9e76019..HEAD` и source diff reads | 0; 48 changed files, 2326 insertions, 754 deletions |
| `PYTHONPATH=scripts python3 -m unittest tests.test_flow_throughput -v` | **0; 54 tests PASS**, 1.012 s |
| `PYTHONPATH=scripts python3 -m unittest discover -s tests -t .` | **0; 1026 tests PASS**, 32.836 s |
| `PYTHONPATH=scripts python3 -m harness.cli drive --root .` | 0; `ok=true`, canonical NL5-002 WAITING_HUMAN, `dispatchable=false`, actor HUMAN; READY C0 показаны отдельно; execution/merge authorization false |
| `PYTHONPATH=scripts python3 -m harness.batch_validate json --root .` | **0; 1519 tracked JSON**, 4 pinned non-JSON digests проверены, errors=[] |
| `check_executions(Path('.').resolve())` из `harness.batch_validate` | **0; 67 execution dirs**, ok=true, errors=[] |
| `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | **0; 1 workflow, 0 violations/blocking** |
| `PYTHONPATH=scripts python3 /workspace/scratch/48cb7a65c9c0/flow-review-adversarial.py` | **1; 7 tests: 6 PASS, 1 FAIL (FLOW-REV-01)**; полный log сохранён |
| `git status --porcelain` | 0; пусто |

Полный unittest запуск использует существующие mock fixtures и расчёт/анализ сохранённых данных; новых scientific engine runs не выполнялось. Paid compute, действия на U1/U2, remote messages и merge отсутствуют.

## Дополнительные adversarial результаты

Самостоятельный код проверки: `/workspace/scratch/48cb7a65c9c0/flow-review-adversarial.py`; полный stdout/stderr: `/workspace/scratch/48cb7a65c9c0/flow-review-adversarial.log`.

- **49 995** комбинаций `used/available/target` проверены независимо через `fractions.Fraction`: рассчитанное освобождение достигает target, на один байт меньше при положительном результате — нет. Всё PASS.
- Исторический P2 source SHA-256 `8cdad386602a08aae4b28885156109a1f3cf7e242c2089d1507ef1e05631258f` подтверждён. Результат `p2_estimate` поблочно совпадает с published addendum. Две df corrections и ratio после старого proposed free перепроверены рациональной арифметикой.
- Реальная конкуренция восьми writer threads: **1 publication, 7 FileExistsError от lock**. После завершения одна непрерывная история; первоначальный START побайтово неизменен, lock снят. Конкурирующее событие не частично опубликовано.
- Девять malformed-card mutations (`status=[]`, `actor={}`, boolean priority/schema version, scientific permission `0`, unfinished dependency, READY blocker, C1 claim, invalid timestamp) отвергнуты с `ok=false`.
- Batch execution validator с BAD-A, GOOD-B, BAD-C проверил **все три**; результат `[false,true,false]`. Первый malformed passport не скрывает следующие директории.
- Added normal summary даёт только publication **candidate**, без approval; executable head, deletion и product change дают FULL_REVIEW. Обратный mode transition выявил FLOW-REV-01.
- Сохранение исторических документов проверено побайтовым сравнением `git show base:path` с new history paths: ROADMAP, WORK_QUEUE, DIRECTOR — идентичны. SHA-256 соответственно `8e63c9d7c22dd39eb4abaa71bbc44f766e1a553431431dc50de735646a6107f8`, `9dfabc8f3f2d0f9b3faf371c220d9613ed9701f05dbc9e75ae2a63f2d5bafd97`, `21edefcb2fcce35fc7d247c9950f0f805c9b4b6f27ee21c659dfe831e8d20ed8`.

## Ограничения и следующее действие

Положительные tests подтверждают программную регрессию и арифметику; они не доказывают host readiness, scientific validity или внешнюю физическую независимость. HIGH gate для FLOW-R1 сохраняется: отдельный Verifier, Director и действующий Human merge gate. Existing frozen scientific / Task Bus gates новым документом не заменяются.

**Одно next action:** автору исправить FLOW-REV-01 и добавить focused negative regression; затем тот же независимый Reviewer может перепроверить чужой repair на новом exact HEAD/TREE. До этого Reviewer PASS не выдан.
