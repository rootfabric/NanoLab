# Локальный атомистический интерфейс

Work Order: `WO-ATOMISTIC-PRODUCT-R1`. Исполнитель: UI implementer,
ветка `work/atomistic-ui-r1`, exact base `0d8537cc368dc03ee39a543c835f72c40b651ae6`.
Начало: 2026-11-05. Событие: `WORK_ORDER_STARTED` (подзадача общего mission).
Scope: `scripts/atomistic/web.py`, `scripts/atomistic/static/`,
`tests/test_atomistic_web.py`, этот документ. Backend разрабатывается отдельно.

Цель: локальная форма → ограниченный реальный backend → состояние → просмотр
траектории и энергии → экспорт. Claim ceiling:
`SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED`.
Синтетические данные допустимы только в тестах и не выдаются за результат расчёта.
Реальные расчёты UI executor самостоятельно не запускает; общий pilot budget
координирует Director. Merge и scientific acceptance здесь не выполняются.

Проверки: unit/HTTP negative tests без физики; визуальная проверка оболочки;
после интеграции — один явно учтённый backend smoke в общем бюджете mission.

## Запуск

После установки isolated environment по `docs/atomistic/README.md`:

```bash
PYTHONPATH=scripts .venv-atomistic/bin/python -m atomistic.web --port 8765 --output-root atomistic-runs
```

Открыть `http://127.0.0.1:8765`. Выбрать размер ГЦК-кристаллита Cu и параметры
релаксации/MD, нажать «Запустить расчёт». Расчёт выполняет настоящий backend
в ограниченном worker process. Статус показывает затраченное время; точный
процент и стадия backend пока недоступны. «Остановить» передаёт cancellation
event, backend завершает worker и сохраняет failed/cancelled evidence.

После успеха: вращение мышью/пальцем, масштаб колесом, воспроизведение и выбор
кадра. Сферы обозначают атомы Cu; связи не предполагаются. Камера сохраняет
масштаб/центр первого кадра. График показывает потенциальную и полную энергию
всей системы в эВ относительно времени MD в фс; релаксация в этот график не входит.

Конфигурация JSON сохраняется из формы независимо от запуска. ZIP результата содержит manifest и все объявленные исходные артефакты
(config, protocol, trajectory, metrics, environment, numerical control,
relaxation evidence, report и logs) с исходными байтами. После распаковки
применим `python -m atomistic.cli verify-run <directory>`. Перед экспортом
проверяются run ID, доверенный run directory, allowlist имён, отсутствие
symlink, размер и SHA-256 каждого файла. Нарушение целостности блокирует ZIP.
Последний результат доступен в текущем процессе; импорт старых runs через UI
пока не реализован. Исходные runs остаются в указанном output directory.

## Ограничения и защита

Сервер слушает только `127.0.0.1`; allowlist Host включает localhost и реальный
порт. Чужой Origin отклоняется; изменение состояния требует случайного токена
в HTTP header. CORS отсутствует. Статические URL и названия экспортируемых
артефактов фиксированы, чтения произвольных путей по HTTP нет. JSON ограничен
16 KiB, duplicate keys и nonfinite числа отклоняются. Конфигурация проходит
тот же backend validator, что CLI. Браузер не может указать command/output path.
Это локальный однопользовательский инструмент, не сетевой сервис.

Один worker на UI; не более 8 attempts и 20 минут в процессе, не более 120 с
на attempt. Дополнительно backend ведёт постоянный общий mission ledger для
CLI/UI/worktrees: рестарт UI и смена output directory не сбрасывают этот лимит.
Пределы backend: 4096 атомов, 2000 MD steps и 201 frame. Валидационные отказы
не запускают worker. Неудачный расчёт не перезапускается автоматически.

## Проверки реализации

На UI implementation subject выполнены:

```bash
PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_atomistic*.py' -v
node --check scripts/atomistic/static/app.js
```

28 tests: 27 PASS, один явно SKIPPED (реальная MD требует отдельного budget).
В том числе 16 HTTP tests с синтетическим runner: state/static, JSON+ZIP,
отсутствие подставного результата до запуска, Host/Origin/token, traversal,
nonfinite/duplicate JSON, body cap, реальная backend validation до worker,
single job/cancel, failed attempt без retry, session caps и loopback binding.
Добавлены SHA/size + byte-exact ZIP round-trip с `verify_run`, повреждённые
файлы/путь/manifest и проверка валидности default HTML числовых полей.
Синтетические fixtures не являются научным или material evidence.

Browser mock QA выполнена настоящим headless Chromium 153 через Playwright:
форма валидна, нажатие запуска достигает completed fixture, atom count 1,
pageerror отсутствуют; screenshots начального/готового состояния просмотрены.
Fixture намеренно синтетический, не физический run. Browser binary получен
из isolated npm `@sparticuz/chromium`; первоначальный Playwright CDN download
вернул неполный ZIP. Server/browser запускаются в одной exec network namespace;
cloud browser не имеет доступа к loopback container (`ERR_CONNECTION_REFUSED`).
Согласован один последующий реальный UI smoke после интеграции в общем budget.
Независимые review/verification остаются необходимы; это не self-acceptance.


## Repair map (до actual UI smoke)

1. Browser QA выявила default HTML friction step mismatch: min 0.0001 и step
   0.001 делали default 0.01 невалидным. Исправлен step 0.0001; generic
   Decimal-check всех default input min/max/step предотвращает повторение.
2. Независимый review выявил неполный ZIP и несовпадение manifest SHA из-за
   повторной JSON-сериализации. Источник ошибки — экспорт in-memory dictionaries
   вместо исходных артефактов. Каноническое исправление `LocalApp.export` читает
   только server-generated run directory и фиксированный набор объявленных
   файлов, сверяет байты с manifest и включает полный комплект без сериализации.
   Изменения касаются HTTP/export/UI; физическая модель и calculation inputs
   не изменены. Regression: fixture byte equality, SHA/size каждого файла,
   распаковка + verify_run, tamper/path/unknown entry rejection; 28 tests PASS/skip
   как выше. До публикации repaired exact source реальный UI smoke не запускался.
