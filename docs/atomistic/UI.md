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
применим `PYTHONPATH=scripts python -m atomistic.cli verify <directory>`. Перед экспортом
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

## Фактический UI smoke после repairs

Один разрешённый расчёт выполнен из clean detached source
`71bc62102cc36bf49b04d40d81d3070d87cccad6`, TREE
`f86af90728797541594396ac0bef0964d9f8dd28`. Run ID:
`ui-22337abacb144a9e88191bfc167c383b`. Конфигурация формы: 32 Cu атома,
`ASE_EMT_Cu`, 2×2×2 ячеек, 3.61 Å, relaxation max 100 steps / 0.05 эВ/Å,
MD 10 steps / 1 фс, 100 K, friction 0.01 фс⁻¹, sample every 2, seed 1729.
Нормализованная requested config сохранена до запуска. Backend записал
config/protocol/STARTED manifest до запуска физического worker.

Команда (из отдельного clean checkout frozen source):

```bash
NANOLAB_ATOMISTIC_MISSION_ROOT=/workspace/scratch/48cb7a65c9c0/NanoLab/.git/nanolab-atomistic PYTHONPATH=scripts /workspace/scratch/48cb7a65c9c0/atomistic-venv/bin/python /workspace/scratch/48cb7a65c9c0/ui-real-smoke.py
```

Playwright + isolated Chromium 153 открыли реальную форму и нажали запуск:
HTTP `POST /api/run` → 202, затем `completed`; backend wall time
0.655919482 с. Получены 6 фактических кадров, 11 MD metric rows; relaxation
сошлась за 10 steps. Playback изменил кадр 1/6 → 2/6; End выбрал 6/6 (10 фс).
Проверены drag rotation и zoom. JS page errors: 0. Скриншот полного UI просмотрен:
видны рассчитанные 32 атома, последний кадр, energy plot, статус и export.
Mobile mock check при ширине 390 px: horizontal overflow отсутствует.

ZIP скачан настоящим нажатием «Скачать результат», 13 815 байт, все 11 файлов
распакованы и `verify_run` завершился успешно с тем же run ID. SHA-256 ZIP:
`5b2b2c923203b9a81bff2644b0368e12d600fd97b96128746c95d3cd33681753`.
HTTP/UI evidence `http-ui.json`, 1826 байт, SHA-256
`375f6690509e1478e918143a41a6a4adea481ba505324b64d8af8fa4571523c6`.
Скриншот `ui-real.png`, 317615 байт, SHA-256
`09684dc10df672bebcf4d18d4ec18afcb1c76ee3466965bf81695b4cd1d6c421`.

Исходный run: `/workspace/scratch/48cb7a65c9c0/ui-real-runs/ui-22337abacb144a9e88191bfc167c383b`.
Пакет UI evidence: `/workspace/scratch/48cb7a65c9c0/ui-real-evidence/`,
включая summary.json с source HEAD/TREE, artifact sizes/digests, исходную
requested config, browser log, HTTP result, ZIP и его распакованные файлы.
Director публикует этот evidence отдельно; source/product после smoke не менялся.

Execution outcome: COMPLETED. Scientific outcome: NOT_EVALUATED.
Claim ceiling остаётся `SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED`.
Один UI attempt без retries; после него общий mission ledger содержал два
расчёта (первый CLI pilot + этот UI smoke). Слот передан независимому Verifier.
Ограничения: нет импорта прошлых runs в UI, точного процента backend, material
benchmark или внешней физической валидации. Следующее действие: независимый
review/verification frozen source и evidence, затем действующий merge gate.
