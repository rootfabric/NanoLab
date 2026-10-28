# FLOW-THROUGHPUT-R1 — быстрый цикл без изменения scientific truth

Вступает в каноническую силу после review и merge этой revision. Реализация по запросу владельца от 28 октября 2026. Не закрывает NL5/NL6/NL7, не активирует R2 или Task Bus P2, не разрешает запуск science/paid compute/изменения узлов.

## 1. Один актуальный operational view

`project/state.json` хранит научную приёмку. `project/operations/<ID>.json` хранит одну C0 операционную задачу: actor, status, dependencies, blockers, resume condition и evidence. `project/plan.json` ссылается на registry. `python -m harness.cli drive` показывает canonical gate и доступные параллельные работы отдельно. `python -m harness.operations --format markdown` формирует текущую очередь; её не нужно вручную дублировать в WORK_QUEUE.md. Неизвестный статус/зависимость, cycle, READY с blocker или пустой registry блокируют рекомендации. Вывод CLI не запускает worker и не даёт launch/merge authority.

Исторический WORK_QUEUE.md сохраняется для provenance; его старые NEXT_ACTION не являются сегодняшним dispatch. На рабочей ветке карточки — candidate execution facts, не каноническая приёмка.

## 2. Review по влиянию, а не числу коммитов

| Изменение | Минимальный путь |
|---|---|
| LOW: действительно административная правка без изменения смысла протокола/вывода | Implementer + автоматические структурные проверки; действующий Human merge gate остаётся |
| MEDIUM: обычный tooling без влияния на scientific truth/допуск/безопасность | Implementer + один независимый Reviewer, выполняющий также механическую проверку, + CI |
| HIGH: протокол, observable, статистика, топология, единицы, преобразование данных, scientific inputs, права/происхождение входов, launch/acceptance/risk gates, безопасность runner | Отдельные Reviewer и Verifier + Director; профиль Work Order может требовать отдельный хост |
| CRITICAL: физический опыт, регулируемые риски, foundation authority, расширение бюджета | Прежний полный путь + Human |

C0 не означает LOW. Markdown может менять научный протокол. Implementer никогда не становится независимым Reviewer/Verifier собственной работы. Этот пакет меняет control/risk policy и сам проходит HIGH путь; новая политика не используется для его self-acceptance.

Повторный repair разрешено проверить тому же независимому Reviewer/Verifier, который проверял исходную работу, если он не автор repair. Обязательная новая сессия после каждого отчётного коммита отменяется для обычных WOs. Специальные frozen научные/Task Bus activation требования этой поправкой не изменяются.

## 3. Неизменный subject и новый publication commit

Разделять product/input/protocol/analysis subject и commit публикации отчёта. `harness.review_impact --base <reviewed-sha> --head <new-sha> --publication-path <exact-file>` сравнивает Git trees и хеш всех остальных путей/режимов/blobs. Исключения только явные summary/review/event файлы одного типа; не glob, не scientific evidence/config/protocol, не изменение исторического event. Удаления и неизвестные пути требуют полного review. Новые отчёты ещё требуют независимого delta review: изменение claim/authority в тексте не принимается автоматически. Вывод comparison не является ни PASS, ни разрешением merge.

При подтверждённом publication-only diff ссылаться на прежнее валидное evidence exact subject и проверять только новые сведения/структуру публикации. Изменение product, входов, протокола, анализа, dependencies либо неясное влияние требует affected rerun. Интеграция с изменившимся main получает полный интеграционный CI; не нужно заново вручную принимать неизменные части.

## 4. Work records без ручного JSON и выдуманных миллисекунд

Новые C0 executions создаются `harness.work_cli start`, далее `record`, `finish`, `correct`. Writer разрешает только существующий Git commit, использует машинное UTC, присваивает последовательность, валидирует staged запись до atomic no-overwrite publication и сериализует конкурирующих writers lock-файлом. Stale lock не снимается автоматически: оператор проверяет отсутствие владельца.

`event_ordering=sequence-v1`: sequence обязана быть 1..N и совпадать с event_id; UTC не убывает, равные timestamps допустимы. Полночь сама по себе не доказывает подделку. timestamp_source — декларация источника часов, не криптографическое доказательство независимого executor. Старые passports/events, scientific experiment validator и external profile не мигрируют и сохраняют прежние проверки. После terminal допускаются только прежние correction classes. Finish требует summary и не выставляет ACCEPTED. Review correction от Implementer запрещена; он публикует обычную continuation correction.

## 5. CI и бюджет

Сохраняются все JSON, pinned negative fixtures, все execution directories, consistency, workflow security lint и полный unittest discover. Два прохода исполняются в одном Python-процессе каждый; ошибки не маскируются. Никаких случайных выборок тестов, retries до зелёного, untrusted self-hosted fallback или токенов записи в PR job. Новые tests проверяют маршрутизацию, atomic writer, отрицательные случаи и арифметику.

## 6. Интегратор и source worker

Интегратор/диспетчер — функция текущего Director, не новая обязательная ступень review. Он читает актуальные карточки, готовит совместимый C0 пакет, использует уже действующие scoped разрешения при выполненных условиях, проверяет base/head/dependencies и формирует одну merge-рекомендацию. Самостоятельно расширять разрешение нельзя. Шесть административных частей одной поставки не требуют шести Human решений: готовится один candidate, а владелец принимает весь перечисленный scope.

Source worker получает ограниченную задачу: реальные файлы пары + rights/provenance + import/ports. Не больше двух содержательных поисковых проходов без нового факта; затем BLOCKED_SOURCE с resume condition либо обоснованный другой кандидат. Никакого SOURCE_VERIFIED из библиографии и никакого незаметного превращения reconstruction в CANDIDATE_DESIGN.

Пока нет отдельного launcher, READY/issue/карточка не означает, что агент реально запущен. Никакие новые workers этим пакетом не стартуют. WIP ориентир: не более трёх содержательных C0 работ одновременно; ожидающие человека/host задачи не занимают активный слот. После двух repairs по одной причине — пересмотр scope/контракта, не обход проверок.

## 7. Ближайшие результаты и оценка эффекта

Порядок: исправленный RESOURCE-R1 и U1/U2 → один реальный offline slice; NL6 TestRig PREP параллелен NL5, реальные научные E5/NL7 остаются последовательными и gated. INFRA6/7 и production Task Bus — по измеренной потребности.

В ближайших пяти реальных WOs фиксировать готово→взятие, последний содержательный diff→merge, количество повторных полных проверок одинакового subject, повторных аудитов без изменения blocker, законченные пользовательские сценарии и дефекты после приёмки. Это измерение эффекта, не новая блокирующая отчётная процедура. Прогноз процента ускорения заранее не заявляется.
