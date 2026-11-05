# NanoLab — дорожная карта

Revision: ATOMISTIC-PRODUCT-R1, 5 ноября 2026. Это candidate revision по [WO-ATOMISTIC-PRODUCT-R1](work/WO-ATOMISTIC-PRODUCT-R1.md), поверх явно названной FLOW-R1 dependency; принятие требует независимой проверки и canonical merge.

## Ближайший полезный продукт

Один исследователь создаёт ограниченную атомистическую структуру одного материала, выполняет реальную релаксацию/MD, просматривает траекторию и метрики, сохраняет воспроизводимый результат, затем сравнивает варианты. Первые P0–P3 — инженерный продукт. P4–P6 — исследования, продолжение которых зависит от физических результатов, проверенной модели и отдельного протокола; срок и успех заранее не обещаются.

Два научных представления развиваются отдельно: новая атомистическая product линия P0–P6 и историческая DNA линия NL0–NL8. Подготовка и узкий инженерный atomistic demo **не заблокированы DNA NL5**. Принятие старых NL checkpoints не доказывает атомистическую validation. E6 не переименован в P0, его прежние NL dependencies сохранены.

## Продуктовая линия P0–P6

| Этап | Результат и условие завершения | Зависимость / горизонт |
|---|---|---|
| P0 — эталон одного материала | Один материал и named/pinned модель; права/provenance, reference values, observables, единицы/boundary, tolerances/uncertainty и convergence checks зафиксированы до оценки; actual outputs и независимая validation | Нет NL5 dependency; ближайшая инженерная основа |
| P1 — атомы и расчёт в приложении | Создать структуру → actual relaxation/MD → trajectory/metrics → сохранить bundle с manifest; явные ошибки и limits, независимая проверка exact subject | Validated acceptance после P0; unvalidated engineering demo поставляется отдельно |
| P2 — ограниченный конструктор | Конечный family геометрий/параметров в области применимости выбранной модели; unsupported inputs отклоняются; geometry → actual calculation → result | После P1; ближайший продукт |
| P3 — сравнение экспериментом | Одна цель, comparator/controls, заранее фиксированные seeds/observables/budget; uncertainty, negative/failed outcomes и воспроизводимый отчёт; вклад ИИ отдельно от validation модели | После P2; ближайший продукт |
| P4 — функциональный компонент | Одна измеренная функция, actuation/energy/load, controls/cycles/integrity/failure envelope и uncertainty | После P3; условное исследование с отдельным протоколом |
| P5 — два компонента | Совместимые interfaces/topology, количественные coupling/load transfer/back-reaction; reduced model проверен на hold-out detailed data | После P4; условное исследование |
| P6 — специализированный механизм | Конкретные energy source/control/cycle/useful output/losses/errors и validation contracts | После P5 и отдельного решения о продолжении |

Машинные критерии, task dependencies, consumer/demo/budget/stop: [product-plan](../project/product-plan.json). Текущий product status: [product-state](../project/product-state.json). **Ни один P checkpoint не принят. P0 остаётся OPEN до проверенного material reference.** Software demo с ASE EMT Cu не является validated EAM, материальным эталоном или подтверждением свойств меди. P1 engineering demo допускает поставку до P0 как IMPLEMENTED_DEMO/UNVERIFIED с отдельным material status OPEN. Работающий P1 не переписывается и не перезапускается лишь потому, что P0 ещё не принят. Точный status adapter/app публикуется с actual evidence; изображение атомов само по себе P1 не закрывает.

## Ближайшая работа и демонстрация

| Работа | Потребитель / проверяемый результат | Бюджет и остановка |
|---|---|---|
| ATOMISTIC-REFERENCE-PREP | Исследователь/material reviewer: pinned source/model/rights и draft protocol одного material reference | Один материал; до двух содержательных source passes без нового факта; затем BLOCKED_SOURCE с точным missing input |
| ATOMISTIC-ADAPTER-PREP | Пользователь/приложение: структура Cu → actual relaxation/короткая MD → trajectory/metrics/manifest | Software contract и negative tests; actual runs только по нижеуказанному mission profile; stop при missing rights/pin, non-finite/integrity/budget failure |
| ATOMISTIC-APP-PREP | Исследователь: создать → рассчитать → просмотреть → сохранить, с честным claim ceiling | Один material/scenario, reuse actual outputs для UI; missing adapter/artifact даёт явную ошибку, без synthetic substitute |

Операционные карточки совместимы с существующим C0 registry и **не разрешают расчёт**. Отдельный [mission WO](work/WO-ATOMISTIC-PRODUCT-R1.md) разрешает только implementation validation нового adapter в disposable Linux: один материал/модель, до **4096 atoms**, **2000 MD steps/run**, **8 actual pilot runs суммарно**, **1200 секунд compute**, **2 GiB результатов**, последовательно, isolated venv. Все исполнители используют общий cumulative run ledger; новые IDs уникальны, failed outcomes сохраняются. Никаких paid compute/U1/U2 mutations/NL5/E5 dispatch. Stop при превышении бюджета, отсутствии pin/прав, non-finite forces/energies или failed integrity. Claim ceiling: `SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED`.

Это реальные атомистические расчёты, а не mock. Этот профиль не признаёт контейнер U1/U2 и не разрешает будущую material/scientific campaign: для неё нужен отдельный frozen protocol/model validation и принятая среда. Отсутствие validated benchmark оставляет P0 OPEN, сохраняя полезность честного инженерного demo.

## Историческая DNA линия

Научный status и счётчики остаются в `project/state.json`; NL0–NL8 dependencies/experiments — в `project/plan.json`; acceptance — в прежних `config/control/harness/project-goals.v1.json` и `checkpoint-catalog.v1.json`. Эти records не расширяются P-стадиями.

| Стадия | Состояние / gate |
|---|---|
| NL0–NL4, NL5-001 | Принятые исторические checkpoints; scope исходной DNA линии |
| NL5-002 | WAITING_HUMAN; NL5 IN_PROGRESS; terminal v0.1 MISMATCH сохранён, external_reproductions=0; v0.2 FROZEN_R2 требует U1/U2/R2/launch gates |
| NL6-001 | PLANNED после NL5-002: E5 driven DNA component, прежние controls/load/cycles/integrity/uncertainty |
| NL6-002 | PLANNED после NL6-001: отдельный non-gating E3-R2 AI benchmark |
| NL7-001 | PLANNED после NL6-001: two-component DNA assembly, coupling и validated reduced model |
| NL8-001 | PLANNED после NL7-001: специализированное mechanism research |

NL6 TestRig C0 PREP и NL7 real-source/offline slice могут идти параллельно по действующим карточкам. S17 follower остаётся NOT_RECONSTRUCTED. Нельзя заменять реальный source синтетическим примером. Waiting U1/U2 задачи не требуют повторного аудита без нового факта.

## Исполнение без лишней работы

[CURRENT_QUEUE](work/CURRENT_QUEUE.md) и `PYTHONPATH=scripts python3 -m harness.cli drive --root .` показывают доступную software работу отдельно от canonical NL5 gate. WIP — максимум три содержательные активные задачи; waiters сохраняют actor/resume condition. Каждая задача имеет consumer, demo, budget/stop. После двух repairs одной причины пересматривается контракт. Не вводить scheduler, новый task bus, новые отчётные ступени или каталоги моделей без работающего пользовательского сценария и измеренной потребности.

[FLOW-R1](control/FLOW_THROUGHPUT_R1.md) сохраняет risk-based review и publication delta review. HIGH scope этой mission требует независимых Reviewer/Verifier и действующего merge gate; implementer не принимает собственный результат. INFRA6/7/AiiDA scale-up — по измеренной необходимости, не hard gate первого atomistic demo. CI, host readiness и trajectory animation не являются scientific acceptance.

## История

[Pre-FLOW roadmap](ROADMAP_HISTORY_PRE_FLOW_R1.md), [WORK_QUEUE history](work/WORK_QUEUE.md), [DNA literature route](control/LITERATURE_TO_MECHANISM_ROUTE_R1.md), [научный метод](SCIENTIFIC_METHOD.md), [INFRA roadmap](infra/ROADMAP.md), [resource corrections](control/RESOURCE_PLAN_CORRECTIONS_R1.md). Frozen protocols, thresholds, seeds и scientific counters не изменяются этой revision.
