# Multi-worktree layout NanoLab — рабочий стандарт

Статус: действующий стандарт расположения репозитория.

## Текущая структура

```text
C:\NanoLab\                          # PROJECT_ROOT — сам НЕ является Git repository
├── .git-store\
│   └── repo.git\                    # единый bare Git store (history, refs, objects, remotes)
├── .vscode\
│   └── settings.json                # настройки контейнера проекта для VS Code
├── main\                            # worktree ветки main
├── nl0-002\                         # worktree ветки work/nl0-002-license-rights-audit-r1
└── ...
```

Git store: `C:\NanoLab\.git-store\repo.git` (bare: true).
Backup миграции: `C:\.dsh-backups\NanoLab-pre-worktree-migration.bundle`.
Старая структура до полного подтверждения: `C:\NanoLab.__before-worktree-layout`.

## Базовые правила

1. **PROJECT_ROOT — не Git repository.** `git status` в корне законно возвращает `fatal: not a git repository`.
2. Все операции над общим хранилищем — через `--git-dir`:

   ```powershell
   $gd = 'C:\NanoLab\.git-store\repo.git'
   git --git-dir=$gd <команда>
   ```

3. Работа с кодом — только в конкретном worktree:

   ```powershell
   git -C C:\NanoLab\main status
   git -C C:\NanoLab\nl0-002 status
   ```

4. VS Code открывает **PROJECT_ROOT** (`code C:\NanoLab`), а не отдельный worktree. Source Control показывает каждый worktree отдельным repository.

## Как узнать зарегистрированные worktree

Перед любой работой агент/человек сначала смотрит список, а не предполагает:

```powershell
git --git-dir=C:\NanoLab\.git-store\repo.git worktree list
```

## Создание новой рабочей ветки (стандартный сценарий)

```powershell
$gd = 'C:\NanoLab\.git-store\repo.git'
$root = 'C:\NanoLab'

git --git-dir=$gd fetch origin
git --git-dir=$gd worktree add -b <branch-name> "$root\<dir-name>" origin/main
```

- `origin/main` — только если база действительно `main` (default branch: `main`, `origin/HEAD -> origin/main`).
- Каталог не обязан совпадать с именем ветки: `nl0-002\` ↔ `work/nl0-002-license-rights-audit-r1`.
- Один worktree = одна ветка = одно назначение. Не checkout одну обычную ветку в двух worktree.

## Существующая локальная ветка → worktree

```powershell
git --git-dir=$gd worktree add "$root\<dir-name>" <branch-name>
```

Без `-b`, если ветка уже существует.

## Remote-only ветка → worktree

```powershell
git --git-dir=$gd worktree add -b <branch-name> "$root\<dir-name>" origin/<branch-name>
```

## Reviewer / verifier worktree (detached HEAD)

```powershell
git --git-dir=$gd worktree add --detach "$root\task-review" origin/<branch>
git --git-dir=$gd worktree add --detach "$root\task-validation" <sha>
```

## Удаление worktree

```powershell
git -C C:\NanoLab\<dir> status --short        # должен быть clean
git --git-dir=$gd worktree remove C:\NanoLab\<dir>
git --git-dir=$gd worktree prune
```

Никогда не `rm -rf` для зарегистрированного worktree.

## Перемещение / восстановление worktree

```powershell
git --git-dir=$gd worktree move <старый-путь> <новый-путь>
git --git-dir=$gd worktree repair    # после внешних перемещений каталогов
```

## Политика `.env`

- `PROJECT_ROOT\.env` — общие runtime-значения (опционально).
- `WORKTREE\.env` — локальные overrides только по указанным ключам.
- Приоритет: process/shell env → `WORKTREE\.env` → `PROJECT_ROOT\.env` → defaults приложения.
- Двухслойная загрузка не работает «сама собой»: она настраивается явно в механизме загрузки проекта (python-dotenv, Compose, Makefile и т.п.).
- Tracked `.env` не переносится из репозитория автоматически; остаётся в своём worktree.

## Политика `.venv`

- Приоритет выбора: `WORKTREE\.venv` → `PROJECT_ROOT\.venv` → создать локальный.
- Если feature branch меняет dependency graph (`pyproject.toml`, `uv.lock`, `requirements*.txt`, `poetry.lock`) — **не** мутировать общий `PROJECT_ROOT\.venv`; использовать `WORKTREE\.venv`.
- Общие mutable build-каталоги (`node_modules`, `build`, `dist`, `target`) между worktree не делятся; глобальные content-addressed кэши (uv, pip, pnpm store) — можно.

## Запреты

```text
git reset --hard, git clean -fd/-fdx, git branch -D   — без отдельного обоснования
отдельный clone на каждую ветку                         — нет
force-push / history rewrite                            — нет (см. BRANCHING_AND_GIT_RU.md)
удаление старой структуры/backup до подтверждения       — нет
```

## Проверка здоровья layout

```powershell
$gd = 'C:\NanoLab\.git-store\repo.git'
git --git-dir=$gd rev-parse --is-bare-repository   # true
git --git-dir=$gd worktree list
git --git-dir=$gd remote -v
foreach ($w in (git --git-dir=$gd worktree list --porcelain | Where-Object {$_ -like 'worktree *'})) {
  $p = $w.Substring(9); git -C $p status --short; git -C $p branch --show-current
}
```

Все worktree должны указывать на один common dir: `C:\NanoLab\.git-store\repo.git`.
