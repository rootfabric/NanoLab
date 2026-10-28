# NanoLab — дорожная карта

Revision: FLOW-THROUGHPUT-R1, 28 октября 2026. Научные статусы — `project/state.json`, scientific dependencies — `project/plan.json`, оперативные C0 работы — `project/operations/*.json`.

## Цель

Лаборатория должна брать реальные доступные нанокомпоненты, воспроизводимо импортировать их, собирать ограниченные конструкции, рассчитывать наблюдаемые свойства и публиковать честный проверяемый результат. Статическая сборка не доказывает самосборку, передачу движения или изготовимость. Научная последовательность NL5 → NL6 → NL7 не отменяется подготовительными работами.

## Научная линия и неизменные критерии

| Стадия | Состояние | Результат / критерий |
|---|---|---|
| NL0–NL4 | ACCEPTED | Научный scope, эталон, validation/provenance, параметрика и AI NanoLab MVP |
| NL5-001 | ACCEPTED | Библиотека компонентов и воспроизводимый release package |
| NL5-002 | WAITING_HUMAN; NL5 IN_PROGRESS | Внешнее воспроизведение. v0.1 terminal MISMATCH сохранён; external_reproductions=0. Platform sensitivity завершена; v0.2 FROZEN_R2 подготовлен, исполнение требует U1/U2/R2/launch gates |
| NL6-001 | PLANNED, зависит от NL5-002 | E5: driven DNA component под заранее заданными drive/load, controls, cycles, integrity и uncertainty |
| NL6-002 | PLANNED, после NL6-001; не блокирует NL7 | Отдельное E3-R2 исследование вклада ИИ на расширенном design space |
| NL7-001 | PLANNED, зависит от NL6-001 | Реальная двухкомпонентная система: topology/ports, количественные load transfer/coupling/back-reaction; reduced model проверен на hold-out detailed data |
| NL8-001 | PLANNED, зависит от NL7-001 | Конкретный механизм с energy/control/cycle/failure/validation contracts |

Полные machine acceptance criteria сохранены в `config/control/harness/checkpoint-catalog.v1.json`. Ни одного scientific checkpoint этот пакет не закрывает. N, seeds, frozen criteria и budgets не смягчаются.

## Ближайшие параллельные работы

| Приоритет | Задача | Измеримый результат | Что блокирует |
|---|---|---|---|
| 1 | RESOURCE-R1 | Исправленные P1/P2 wall/storage estimates и план актуального профиля ресурсов | Scientific dispatch остаётся закрыт до host/authority gates |
| 1 | AUTHOR-U1 / EXTERNAL-U2 | Физический author U1 и разрешённая подготовка U2 с новыми измерениями | Решения владельца и реальные operator actions; не ещё один повтор аудита |
| 2 | INTEGRATION-R1 | Один совместимый C0 candidate и одна merge-рекомендация по явно перечисленному scope | Independent review и действующий Human merge gate |
| 3 | NL7-REAL-SOURCE | Реальные CAD/oxDNA файлы пары, права, provenance и import | Не более двух содержательных поисковых проходов без нового факта; затем alternate candidate или BLOCKED_SOURCE |
| 4 | NL7-OFFLINE-SLICE | Import → ports → assembly → .top/.dat → preview/export → receipt на реальной паре | Требует NL7-REAL-SOURCE, не требует преждевременного закрытия NL5 |
| Параллельно | NL6-TESTRIG-PREP | Программный стенд одиночного driver: drive/load/controls/observable и подготовка inputs | C0-only: ни MD, ни E5 acceptance. Отсутствие follower не блокирует весь стенд |

Текущие статусы не дублируются вручную: [CURRENT_QUEUE](work/CURRENT_QUEUE.md) и `harness.cli drive`. READY — доступная подготовка, не уже запущенный worker. Реальная S17 follower-модель остаётся NOT_RECONSTRUCTED; синтетический пример остаётся только проверкой программы. Другой кандидат не выдаётся за воспроизведение S17.

## Исполнение и проверки

[FLOW-THROUGHPUT-R1](control/FLOW_THROUGHPUT_R1.md) задаёт risk routing и delta review. Ordinary MEDIUM tooling получает одну независимую review-сессию + CI; HIGH science/inputs/authority/security сохраняет отдельные Reviewer/Verifier. После отчётного commit не перезапускать весь цикл без влияния на subject. Полный набор программных тестов сохранён; JSON/passport sweeps выполняются пакетно.

Интегратор — функция Director, не новая approval-ступень. Source worker оценивается реальными файлами и завершённым сценарием. Никакой скрытой активации Git Task Bus production. WIP ориентир — три содержательных C0 работы; waiting tasks сохраняются с actor/resume condition и не занимают активный слот.

## Инфраструктурные приоритеты

Сначала U1 (INFRA3-003), scoped U2 remediation и пригодное durable raw storage. INFRA6/AiiDA, общий scheduler и INFRA7/federation — по измеренной потребности, не ближайшие обязательные gates. [RESOURCE_PLAN_CORRECTIONS_R1](control/RESOURCE_PLAN_CORRECTIONS_R1.md) исправляет F05 P2 omission, df denominator и systemd vocabulary без изменения старых evidence.

## Как проверить ускорение

На следующих пяти реальных WOs измерять готово→взятие, последний содержательный diff→merge, полные повторы одинакового subject, повторные аудиты неизменного blocker, законченные пользовательские сценарии и дефекты после приёмки. Это неблокирующее наблюдение, не новая отчётная ступень.

## История и источники

[Предыдущая roadmap](ROADMAP_HISTORY_PRE_FLOW_R1.md) сохранена побайтово из `main@3b567ae33f247b182b2ae451d2cc4598a9e76019`; её промежуточные NEXT_ACTION исторические. [Очередь/хронология](work/WORK_QUEUE.md), [literature-to-mechanism route](control/LITERATURE_TO_MECHANISM_ROUTE_R1.md), [научный метод](SCIENTIFIC_METHOD.md), [INFRA roadmap](infra/ROADMAP.md). При конфликте приоритет имеет текущий canonical state и эта revision в её C0 scope; frozen научные требования не заменяются.
