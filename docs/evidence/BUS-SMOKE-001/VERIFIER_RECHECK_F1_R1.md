# VERIFIER RE-CHECK — F1 Repair R1 (аддендум к VERIFIER_VERDICT.md)

- Verdict по ремонту: **PASS** (ремонт принят; исходный PASS P1.3 по брокеру остаётся в силе)
- Re-verified subject: `control/git-task-bus-r1` @ `4d7febd` (223d49b test-fix + 4d7febd Repair Map/evidence; база ремонта `60bdca6…` — предок, подтверждено)
- Verifier: та же fresh-сессия P1.3; дата: 2026-09-10; окружение не изменилось: Windows, Python 3.11.8, git 2.53.0.windows.1, user gitconfig `safe.bareRepository=explicit`
- Метод: свежее исполнение в этом worktree (detached checkout `4d7febd`), собственные логи ниже; логи ремонта из PR #20 не использовались как доказательство

## 1. Суть ремонта (по REPAIR_MAP_F1_R1.md и диффу)

Только `tests/task_bus/test_task_bus.py` (8+/3−): `run_git` получил `git_dir=None`-параметр
(`git --git-dir=<bare>` вместо `git -C <bare>` — явная адресация вместо discovery),
единственный bare-обращающийся call-site переведён на эту форму. Assert-семантика
(`rev-parse main == base`) сохранена. Брокер `tools/task_bus.py` не тронут — проверено:
blob на `4d7febd` = `a3d0556717f3320e885f4092f242bed53bf0584f` = исходный subject-блоб.

Отклонённые альтернативы (§3 Repair Map) признаю обоснованными: `-c safe.bareRepository=all`
и `GIT_CONFIG_GLOBAL=null` выключали бы политику/весь user gitconfig, вместо comply с ней;
`safe.directory` — не тот переключатель. Выбор `--git-dir` зеркалит адресацию самого брокера
и сохраняет реалистичность окружения сьюта.

## 2. Свежие прогоны (этот re-check)

| Прогон | Условия | Результат |
|---|---|---|
| A — `logs/pytest-f1-recheck-default-config.log` | default user gitconfig, `safe.bareRepository=explicit` | **39 passed, 1 skipped** (42.45 c) |
| B — `logs/pytest-f1-recheck-GIT_CONFIG_GLOBAL-NUL.log` | `GIT_CONFIG_GLOBAL=NUL` (контроль) | **39 passed, 1 skipped** (43.19 c) |

Ключевой тест `GitIntegrationTests::test_independent_clones_full_cycle_and_main_untouched`:
**PASSED в обоих прогонах** (ранее — единственный FAIL при default-конфиге).
Skipped в обоих: symlink-тест (известное F2, вне scope ремонта).

## 3. Выводы и заметки для P1.4

- F1 закрыт ремонтом: зелёный прогон достигается на реалистичном default-окружении
  без отключения пользовательской политики; контрольный прогон B — тоже зелёный.
- F2 (symlink skipped на Windows) остаётся открытым наблюдением — как и указано в Repair Map.
- Verbatim-оговорка Repair Map §6 верна: этот PASS относится к `4d7febd` и подтверждает
  только сам ремонт тест-харнесса (единственный файл `tests/`) плюс неизменность брокера
  (blob-identity). Полная fresh exact-head re-verification нового HEAD для целей P1.4 —
  отдельный процесс по correction §7 (запрошена отдельно).
- Соглашение «bare-адресация только через `--git-dir`/аргумент-путь» — принято к
  применению в будущих скриптах харнесса на Windows-агентах.
