# REPAIR MAP — F1/F-1: тест-харнесс ломается при `safe.bareRepository=explicit` (R1)

- Finding: **F1 (MEDIUM)** из `VERIFIER_VERDICT.md` §5 (ветка `verify/bus-001-r1` @ `ae472f1`):
  1 failed при дефолтном user gitconfig; зелёный только при `GIT_CONFIG_GLOBAL=NUL`.
- PR: #20 (draft), ветка `control/git-task-bus-r1`, база ремонта: `60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c`.
- Worktree ремонта: `C:\NanoLab\bus-repair-f1`.
- Дата: 2026-09-10 (UTC+3). Окружение: Windows, Python 3.11.8, pytest 8.3.3, git 2.53.0.windows.1.

## 1. Root cause

`GitIntegrationTests.run_git` строит все вызовы как `git -C <cwd> …`. Единственное место,
где `<cwd>` — это **bare**-репозиторий: строка 326 (до ремонта) — финальная assertion
`test_independent_clones_full_cycle_and_main_untouched`:

```python
self.assertEqual(self.run_git(self.remote, "rev-parse", "main"), self.base)
```

При `safe.bareRepository=explicit` (умолчание свежих Git for Windows) git отвергает
**discovery** bare-репозитория через cwd (`-C`/chdir), но разрешает **explicit**-адресацию.
Отсюда: `fatal: cannot use bare repository … (safe.bareRepository is 'explicit')`.
Все остальные `run_git`-вызовы идут в non-bare рабочие клоны или `self.root`
(`init --bare`/`clone` адресуют remote путём-аргументом — discovery не затрагивается),
поэтому падает ровно один тест, и только собственная assertion теста: полный
4-ролевой цикл брокера к этому моменту уже успешно завершён (подтверждено верификатором,
Run A исходного вердикта). Брокер `tools/task_bus.py` к дефекту отношения не имеет.

## 2. Fix (что сделано)

Минимальный дифф только в `tests/task_bus/test_task_bus.py` (8+/3−):

1. `run_git(cwd, *args)` → `run_git(cwd, *args, git_dir=None)`: при `git_dir` вызов строится
   как `git --git-dir=<path> …` вместо `git -C <path> …`.
2. Единственный bare-обращающийся call-site переведён на явную форму:
   `self.run_git(None, "rev-parse", "main", git_dir=self.remote)`.

Обоснование выбора паттерна: `safe.bareRepository=explicit` — это не поломка, а
политика: git требует адресовать bare-репозиторий явно. Паттерн `--git-dir`:

- соответствует самой политике (ничего не выключает — user gitconfig остаётся активным
  во всех остальных вызовах, сьют продолжает исполняться в реалистичном окружении);
- кроссплатформенный (никаких `NUL`/`/dev/null`-развилок);
- зеркалит паттерн самого брокера: верификатор подтвердил, что брокер адресует
  bare remote аргументом (URL/путь) и потому политикой не блокируется;
- эмпирически проверен (§3, проба P-3) и доказан обоими прогонами (§4).

Эмпирические пробы паттернов (scratch bare, git 2.53.0.windows.1, `safe.bareRepository=explicit`):

| # | Паттерн | Результат |
|---|---|---|
| P-1 | `git -C <bare> rev-parse HEAD` | `fatal: cannot use bare repository …` (воспроизведение F1) |
| P-2 | `git -C <bare> -c safe.bareRepository=all …` (и обратный порядок аргументов) | работает, но отклонено (§3-A) |
| P-3 | `git --git-dir=<bare> rev-parse HEAD` | **работает — выбрано** |
| P-4 | `GIT_CONFIG_GLOBAL=NUL git -C <bare> …` | работает, но отклонено (§3-B) |
| P-5 | `safe.directory`-настройка | отклонено: не тот переключатель (§3-C) |

## 3. Отклонённые альтернативы

- **A. `-c safe.bareRepository=all` в `run_git`** (работает — пробы P-2). Отклонено:
  это выключение политики, а не comply с ней; `run_git` — общий хелпер всех git-вызовов
  сьюта, так что побочный эффект — легализация bare-discovery для всего харнесса и
  маскировка будущих регрессий того класса, который §6 коррекции объявляет
  adversarial-зоной (`safe.bareRepository behavior`); плюс зависимость от исключения
  «`-c` уважается для safe.bareRepository, но игнорируется для safe.directory» — хрупко
  между версиями git.
- **B. `GIT_CONFIG_GLOBAL=<null-device>` в env `run_git`** (кроссплатформенный вариант
  через `os.devnull`). Отклонено: выключает весь user gitconfig для всех git-вызовов
  сьюта — сьют перестаёт исполняться в реалистичном окружении, хотя именно реалистичный
  user-конфиг и вскрыл F1. Это контрольное условие верификатора (Run B вердикта),
  доказательство диагноза, а не ремонт; оставлено как контрольный прогон, не как фикс.
- **C. `safe.directory` для bare-пути теста.** Отклонено: не тот переключатель —
  `safe.directory` управляет ownership-доверием, а не bare-discovery. Эмпирически:
  в падающем окружении user gitconfig уже содержит `safe.directory=*`, и падение
  сохраняется (P-5 = сам факт F1 на этом окружении).

Не добавлялся и «негативный» тест, утверждающий отказ `git -C <bare>`: он тестировал бы
сам git, а не харнесс, и падал бы на машинах без этой политики (типичный Linux CI).

## 4. Evidence (новые прогоны, после ремонта)

Оба прогона — `python -m pytest tests/task_bus/ -v` в worktree ремонта, 40 тестов собрано:

| Прогон | Условия | Результат |
|---|---|---|
| Run A — `logs/pytest-repair-r1a-default-config.log` | дефолтный user gitconfig, `safe.bareRepository=explicit` | **39 passed, 1 skipped, exit 0** (45.69 c); `test_independent_clones_full_cycle_and_main_untouched` — PASSED |
| Run B — `logs/pytest-repair-r1b-GIT_CONFIG_GLOBAL-NUL.log` | `GIT_CONFIG_GLOBAL=NUL` (контроль вердикта) | **39 passed, 1 skipped, exit 0** (45.57 c) |

Skipped в обоих прогонах: `test_symlink_candidate_and_local_smoke_are_rejected` —
известное F2 (Windows без привилегии symlink), вне scope данного ремонта и не им
порождено. Дополнительно: `python -m py_compile tools/task_bus.py tests/task_bus/test_task_bus.py`
→ exit 0.

## 5. Что НЕ менялось (границы ремонта)

- `tools/task_bus.py` — брокер не тронут (ни логика, ни git-обвязка); дифф ремонта
  не содержит ни одного файла вне `tests/` и `docs/evidence/BUS-SMOKE-001/`.
- Policies, control-документы (`docs/control/*`), `config/control/task-bus/` — без изменений.
- Frozen-объекты пилота (`work/bus-smoke-001-r1`, `control/task-bus-pilot-r1`) — не затронуты.
- Assert-семантика теста сохранена: та же assertion `rev-parse main == base` на bare remote,
  изменён только безопасный способ адресации.

## 6. Остаточные риски / заметки для P1.4

- Verbatim-вердикт P1.3 привязан к exact HEAD `60bdca6…`; настоящий ремонт добавляет
  новые коммиты, поэтому формально требуется fresh re-verification нового HEAD
  (subject drift по correction §7) — это ожидаемый процесс, а не регрессия.
- F2 (symlink-тест skipped на Windows) остаётся открытым наблюдением — вне этого ремонта.
- Паттерн `--git-dir` для bare-адресации стоит считать обязательным соглашением для
  будущих тестов/скриптов харнесса на Windows-агентах (вместо `GIT_CONFIG_GLOBAL=NUL`).
