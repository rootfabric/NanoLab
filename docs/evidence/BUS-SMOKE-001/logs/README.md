# Логи pytest после ремонта F1 (repair-r1, ветка control/git-task-bus-r1)

База ремонта: `60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c` (exact HEAD вердикта P1.3).
Worktree: `C:\NanoLab\bus-repair-f1`. Окружение: Windows, Python 3.11.8, git 2.53.0.windows.1.
User gitconfig: `core.autocrlf=true`, `safe.bareRepository=explicit` (плюс `safe.directory=*`, что на политику bare-discovery не влияет).

## Run A — logs/pytest-repair-r1a-default-config.log (основной ремонтный прогон)

Команда: `python -m pytest tests/task_bus/ -v` (дефолтный user gitconfig, `safe.bareRepository=explicit` активен).
Результат: **39 passed, 1 skipped, exit 0** (45.69 c) — ЗЕЛЁНЫЙ.
`GitIntegrationTests::test_independent_clones_full_cycle_and_main_untouched` — PASSED
(до ремонта на этом же окружении — FAILED на строке 326: `git -C <bare> rev-parse main` →
`fatal: cannot use bare repository … (safe.bareRepository is 'explicit')`).
Skipped: `test_symlink_candidate_and_local_smoke_are_rejected` — известное F2 (Windows без
привилегии symlink), вне scope данного ремонта.

## Run B — logs/pytest-repair-r1b-GIT_CONFIG_GLOBAL-NUL.log (контрольный прогон)

Команда: `$env:GIT_CONFIG_GLOBAL='NUL'; python -m pytest tests/task_bus/ -v`.
Результат: **39 passed, 1 skipped, exit 0** (45.57 c) — ЗЕЛЁНЫЙ, идентичен Run A.
Контроль подтверждает: после ремонта сьют зелёный и при отключённом user gitconfig,
т.е. фикс не вносит зависимости от содержимого user-конфига.

## Вывод

Красно/зелёное условие F1 устранено: сьют зелёный при активной safe-политике
(Run A) и при её отключении вместе со всем user-конфигом (Run B). Брокер
`tools/task_bus.py` не менялся; дифф ремонта — только `tests/task_bus/test_task_bus.py`
(см. `../REPAIR_MAP_F1_R1.md`).
