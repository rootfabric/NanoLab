# BUS-001 — результат подготовки Git Task Bus

Статус: **HANDOFF_READY**, не ACCEPTED. Claim: C0_SOFTWARE_ONLY.

## Subjects

- Исходный main: `95b1319600bcc64572d84c0456acb927802ab806`.
- Durable START: `6fb0290a116cb62dc2e1d1aaa59de761acff8bfc`.
- Код, тесты, протокол и prompts: `99a93c0f44d0cbc3c0a4ab5cca1f6d5095963024`.
- Code tree: `cc810266bc506917b738ca9bdccd789dfacfe698`.
- Implementation branch: `control/git-task-bus-r1`.
- Live queue branch: `control/task-bus-pilot-r1`.
- Seed queue commit: `d23407843185391ec54de11f98c9211da95ecfce`.
- Snapshot очереди: `evidence/live-queue-snapshot.json`; актуальный state читать только из bus branch.

## Реализовано

Python CLI без сторонних пакетов: role/capability routing, зависимости,
append-only event replay, атомарные competing claims через non-force Git push,
lease/heartbeat/reclaim и fencing, idempotent retry включая потерю ответа,
repair/block/resume/cancel, exact candidate HEAD/TREE и scope guard.
Отчёты встроены в события bus и не меняют проверяемый candidate HEAD.

Инструкции: `docs/control/GIT_TASK_BUS_RU.md` и
`docs/control/GIT_TASK_BUS_PROMPTS_RU.md`. Сравнены первичные источники Beads,
MCP Agent Mail, Gas Town, GitHub Agentic Workflows. Upstream-код не копировался.

## Проверено

`python -m py_compile tools/task_bus.py tests/task_bus/test_task_bus.py`: exit 0.
`python -m unittest discover -s tests/task_bus -v`: **40 tests, 0 failures,
0 errors, 0 skips**, exit 0. Среда: Python 3.13.5 / Git 2.47.3 / Linux.
Повторный прогон выполнен на байтах, чьи Git blob SHA совпали с публикацией.
SHA-256 и команды: `evidence/validation.json`; полный stdout/stderr:
`evidence/tests-published.log`.

Реальная конкурентная запись тестировалась через отдельные clones общего
локального bare remote: два одновременных claim дают одного победителя;
разные задачи сохраняют обе записи. Проверены потерянный ACK, stale token,
expired lease, неправильная роль, повторный message ID, subject drift,
выход из scope, имя файла с начальным пробелом, symlink и dirty worktree.

`evidence/local-cycle.json` — сохранённый девятисобытийный прогон через четыре
скриптовые роли. Все SHA внутри него относятся к **синтетическим локальным
репозиториям**, а не к NanoLab remote. Это не независимое AI review.
Первоначальная ошибка test discovery (неверный parent для пути TOOL) сохранена
в `evidence/tests-initial-failure.log`; исправление подтверждено полными прогонами.

## Live trial

В очереди опубликовано одно событие open для `BUS-SMOKE-001`.
Ожидаемая роль IMPLEMENTER, lease отсутствует, candidate отсутствует.
Ни одна независимая AI-сессия ещё не выполняла live цикл. Задача намеренно
оставлена доступной следующему агенту. Ожидаемый финал: COMPLETED_SANDBOX,
не canonical acceptance и не изменение научной дорожной карты.

## Epoch drift

Во время работы main продвинулся внешним исполнением NL0-002 до
`81e299f1924e50bcff1bc5c893bccd934ef2883d` (15 commits от исходной базы).
Проверены changed paths, обновлённые LICENSE_POLICY и scheduler policy.
Решение: **CONTINUE** — с файлами пилота и обязательными role/merge правилами
пересечения нет; scheduler переводит научный приоритет на NL0-003.
Пилот научные задачи не запускает, сторонние данные не копирует.
Frozen base не меняется. Записей в main со стороны этого исполнения: **0**.
Нельзя утверждать, что глобальный main вообще не менялся: он изменился извне.

## Ограничения и непройденные gates

Independent Reviewer/Verifier самой реализации: NOT_RUN. Live multi-agent
trial: NOT_RUN. Full repository Harness regression: NOT_RUN. Windows: NOT_RUN.
GitHub Actions и внешние агенты не запускались. Из контейнера сетевой clone
GitHub недоступен; чтение/публикация выполнены GitHub connector, тесты — локально.
Не заявляется полная проверка остальных файлов репозитория.

Профили cooperative: разные actor_id не доказывают независимость сессий.
Protected writer/credentials, unattended launcher, production roadmap adapter,
external-job exactly-once, высокая нагрузка и main acceptance не реализованы.
Эти границы описаны в протоколе; лимиты пилота: log 2 MB, 16 claims, 2 repairs.

## Единственное следующее действие

Новая сессия DIRECTOR читает `status/history` BUS-SMOKE-001, затем запускает
отдельный IMPLEMENTER доступным исполнителем либо завершает проход с
WAIT_EXTERNAL. Полные задания четырёх ролей уже опубликованы. Implementation
PR остаётся draft до independent review и разрешения Human Gate; bus branch
никогда не сливается в main.
