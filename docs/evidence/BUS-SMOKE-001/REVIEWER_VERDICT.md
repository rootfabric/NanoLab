# BUS-001 Implementation Review — Fresh Reviewer R1 (CONTINUATION, interim)

Status: **IN_PROGRESS** — промежуточный CONTINUATION-коммит; финальный вердикт
публикуется в этом же файле отдельным коммитом.

Reviewer: независимая fresh-сессия (P1.2 из `GIT_TASK_BUS_POST_PILOT_CORRECTION_R1.md`).
Reviewed subject: `control/git-task-bus-r1` @ `60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c` (PR #20 draft).
Worktree: `C:\NanoLab\review-bus-001` (detached от exact HEAD, затем ветка `review/bus-001-r1`).

## Выполненные проверки (на момент коммита)

1. Прочитаны control-документы main @ `57c1e63`: `AGENTS.md`, `HARNESS_CONTROL.md`,
   `PROJECT_CONTROL.md`, `docs/control/*` (review/evidence, branching, autonomy, harness).
2. Прочитан полный диф `main..control/git-task-bus-r1` (9 коммитов, +2951 строк):
   `tools/task_bus.py`, `tests/task_bus/test_task_bus.py`, `config/control/task-bus/*`,
   `docs/control/GIT_TASK_BUS_*.md`, `DIRECTOR.md`, evidence `EX-BUS-001-R1`/`EX-BUS-002-R1`.
3. Статический аудит broker'а по bounded scope: state/evidence sync, lease/fencing,
   CAS claim race, retry/idempotency, subject drift, role separation, repair loops,
   negative controls. Промежуточные выводы:
   - CAS: non-FF push commit'а с единственным родителем = прочитанный HEAD; при
     конфликте — fresh re-read и повторная валидация перехода reducer'ом. Корректно.
   - Fencing: lease token = event id claim'а; все операции, кроме claim/reclaim/
     resume/cancel/invalidate, требуют совпадения actor+token и `at < until`.
     Старый token после reclaim/release/invalidate отвергается
     (`STALE_OR_FOREIGN_LEASE`). Покрыто тестами.
   - Idempotency: `append` дедуплицирует по event id с контролем содержимого
     (`IDEMPOTENCY_KEY_COLLISION`); CLI сохраняет pending message-id и переиспользует
     его при повторе; потерянный ACK восстанавливается поиском id в журнале.
   - Role separation: `phase == role`, `approvals` не принимает повторного actor,
     реализация FAIL сбрасывает approvals/subject, бюджет repairs учитывается.
   - Subject drift: `check_subject` на каждом `finish` заново fetch-ит candidate ref;
     head/tree/ancestry/scope/mode проверяются; drift после PASS инвалидирует
     старый verdict (reducer'ом + transport-проверкой).
   - State/evidence sync: blob-хэши `tools/task_bus.py`/`tests/` в
     `EX-BUS-001-R1/evidence/validation.json` совпадают с HEAD
     (`a3d0556…`, `7f8c939…`); код после `99a93c0` не менялся; stale-статусы
     live trial явно superseded `GIT_TASK_BUS_POST_PILOT_CORRECTION_R1.md` и
     `DIRECTOR.md` §8; `live-queue-snapshot.json` помечен как неавторитетный.
4. Тест-прогон (Windows, Python 3.11.8, Git 2.53.0.windows.1):
   `python -m pytest tests/task_bus/ -v` → **1 failed, 38 passed, 1 skipped**.
   Лог: `pytest-run-r1.log` (рядом с этим файлом).
   - FAILED `test_independent_clones_full_cycle_and_main_untouched`:
     AssertionError на `run_git(<bare remote>, "rev-parse", "main")` —
     `fatal: cannot use bare repository … (safe.bareRepository is 'explicit')`.
     Root cause подтверждён на scratch bare repo: в глобальном конфиге
     пользователя `C:/Users/root/.gitconfig` задано `safe.bareRepository = explicit`;
     `git -C <bare>` (implicit discovery) отвергается, `git --git-dir=<bare>` работает.
     Падает тестовая обвязка (обращение к bare remote через `-C`), а не broker:
     `tools/task_bus.py` работает только с non-bare клонами и не затронут.
     Это ровно та зона «safe.bareRepository behavior», которая заявлена в
     POST_PILOT_CORRECTION §6 как обязательная adversarial area.
   - SKIPPED `test_symlink_candidate_and_local_smoke_are_rejected`:
     `Platform does not permit unprivileged symlinks` (Windows) — ожидаемый skip.
   - Ссылочный результат имплементёра 40/40 (Linux, Git 2.47.3,
     `evidence/tests-published.log`) остаётся историческим evidence; расхождение
     объясняется средой, не изменением кода.

## Дальнейшие шаги (следующий коммит)

- Независимые CLI-пробы negative-кейсов на scratch remote: повторный claim,
  finish с истёкшим lease, finish с чужим subject, повтор init.
- Финальный вердикт PASS / FIX_REQUIRED / FAIL + findings по severity и claim ceiling.

## Ограничения

- Linux/ссылочная среда не воспроизводилась; Git 2.53 Windows + user gitconfig
  отличаются от ссылочных Python 3.13.5 / Git 2.47.3 / Linux.
- Сетевые операции ограничены работой с origin GitHub (fetch/push) в рамках
  разрешённого review workflow.
