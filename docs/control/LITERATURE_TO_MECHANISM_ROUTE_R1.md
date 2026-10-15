# Literature-to-Mechanism Route R1 — NanoLab

**Назначение:** предложенная владельцем корректировка научно-продуктовой дорожной карты от воспроизведения отдельных DNA-компонентов к сборке и испытанию новых наномеханизмов. Подготовлена 2026-10-11; до independent review/verify и Human Gate merge — **проектное решение, C0_SOFTWARE_ONLY**, а не научная приёмка.

## 1. Цель и границы

Создать путь: **открытые результаты → versioned source pack → механическая деталь с молекулярными интерфейсами → проверяемая сборка → нагрузочные эксперименты → новые варианты с воспроизводимым evidence**. Переиспользовать oxDNA/oxpy, scadnano/caDNAno, oxView, анализ и существующий NanoLab harness. Не строить второй движок или универсальную САПР до необходимости. CAD-сборка, стабильность в coarse-grained модели и изготовимость в лаборатории — три независимых утверждения.

Не менять научные факты: на базе `main@8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad` стадии `NL0–NL4=ACCEPTED`, `NL5=IN_PROGRESS`, `NL5-001=ACCEPTED`; `NL5-002=WAITING_HUMAN` после verified terminal MISMATCH / NOT accepted, `external_reproductions=0`. Frozen NL5 v0.2 R2 не равен запуску новой науки: независимый native Ubuntu U1 и полная активация R2 нужны отдельно. **NL6/E5 нельзя начинать, пока NL5 научно не принят и U1/R2 не разрешён.** Frozen протоколы, пороги, исходы и исторические данные не пересматривать.

## 2. Впитать результаты исследователей

| Приоритет | Источник | Что использовать | Что проверить до интеграции |
|---|---|---|---|
| Осуществлено в NanoLab | S16 Shi–Castro–Arya DNA hinges | Парсеры, варианты, topology/mapping, E2 observables | `REFERENCE_ONLY`/права; вариант 74b остаётся `NOT_MEASURED` |
| **P0** | **S17 Centola leaf-spring nanoengine**: Nanobase structure 196, Zenodo 8248808, `sulcgroup/hinges` | Известный дизайн, пружинный привод, пассивный follower, методы анализа — базовый E5/NL7 benchmark | Exact input pins + SHA; исходные модели/условия/права; внешнее усилие не равно химической автономии |
| P1 | S18 Madhvacharyula mechanical frustration, 2025 | Распределение деформаций, связь узлов, free-energy states | Source Data vs полный simulation pack; правовой и format audit |
| P2 | S19 Pfeiffer spring-loaded arrays, 2025 | Подпружиненные состояния, защёлки, управление каскадом, механическая логика | Large raw dataset не доказывает готовый импортный дизайн; проверить methods/rights |
| P2 optional | S20 Generative SNUPI, 2026 | Генератор кандидатов из целевой геометрии, export oxDNA/CanDo | Linux/NVIDIA GPU/deps/weights/домен применимости; независимая oxDNA-проверка обязательна |
| P2 optional | S21 MagicDNA, 2021 | Графическая многокомпонентная сборка и идеи форматов | MATLAB dependency, source/rights; не обязательный runtime |

Магнитные муфты, ДНК-турбины, молекулярные шестерни на поверхности и белковые шагоходы — ценные идеи, но **не совместимые с oxDNA компоненты по умолчанию**. Новый физический движок появляется только demand-driven, с новым эталоном, границами применимости и правами.

Уровни получения научного source pack:
`BIBLIOGRAPHIC → RIGHTS_AND_INPUTS_AUDITED → PINNED_IMPORT_VERIFIED → MODEL_REPRODUCED → COMPONENT_CHARACTERIZED → ASSEMBLY_VALIDATED`.
Авторская публикация/эксперимент и независимое воспроизведение NanoLab записываются раздельно. Публичный URL не означает права на перераспространение; неопределённые входы остаются ссылками, не vendored files. Большие raw outputs — вне Git, с URI, checksum, size, producer и retention.

## 3. Что конкретно построить (future contracts)

- **KnowledgePack v1**: source ID/DOI, exact commit/version, файловые манифесты SHA-256, лицензии, provenance, model/env, protocol/observable definitions, missing data и rights limitations.
- **MechanicalComponentSpec v1**: versioned DNA topology и design mapping, local coordinate frame, `ports[]` с anchors (молекулярные/цепные IDs), orientation, типом связи и механическими DOF, допустимые нагрузки/среда и явные UNKNOWN; ссылка на существующий `component-card.v1`, без его ретроактивной замены.
- **AssemblySpec v1**: экземпляры и версии деталей, transforms, `connections[]`, разрешённые edits цепей/связей, общая topology/config, модель и единицы.
- **TestRigSpec v1**: preregistered drive/load/no-drive/no-load controls, state distributions, return/reversibility, repeated cycles, integrity, uncertainty, budget/seeds, success/failure/stop rules.
- **ReducedModelCard v1**: DOFs, подход к coarse model, точные detailed training sources, область применимости, независимый hold-out и ошибки.
- **Generator adapter (optional)**: алгоритм выдаёт гипотезу/кандидата, но не уровень научной истины.

Компилятор сборки сначала должен **fail closed** проверять порты, систему координат, идентификаторы молекул, валентность/топологию связей, единицы, запрещённые соединения, столкновения, loss of mapping, недопустимые модели и права. Первый MVP поддерживает **один известный тип DNA-соединения**, а не произвольное соединение любых нанодеталей.

Пример:
```text
published components → KnowledgePacks → ComponentSpecs
  → select compatible anchors/ports → AssemblySpec
  → validated complete oxDNA topology+configuration
  → preparation/relaxation → pre-registered TestRig
  → independent simulation/analysis → evidence + new variant release
```

## 4. Исполняемый маршрут и acceptance gates

| Работа | Вход и измеримый выход | Gate |
|---|---|---|
| **PREP-S17 (parallel docs/tooling; NOT scientific execution)** | Проверить Nanobase 196/Zenodo 8248808/analysis repo: скачать где законно, pin/digest, methods, observables, failed/missing inputs; согласовать прототип структуры портов | Только source/rights/topology audit; статус `NOT_DISPATCHED` до отдельного WO, не закрывает NL5 |
| **NL6-001 / E5** | Установленный published-driven benchmark, control-эксперимент без внешней силы, задаваемые нагрузка/активация, возврат, повторные циклы, структурная сохранность, доверительные оценки | `NL5` accepted + approved native U1/R2 + preregistered scientific protocol; driven component, НЕ автономный motor; отрицательный итог сохраняется |
| **NL7-001 / composition** | Конструктор DNA портов + сборка driver→follower из проверенного published template, затем один ограниченный вариант; проверки topology и работы целой системы | После **NL6-001**, без зависимости от NL6-002; quantify coupling/back-reaction, failures, load transfer; reduced models проверены на hold-out detailed calculations |
| **NL6-002 / E3-R2 (parallel, non-gating)** | Random/grid/BO/LLM-guided поиск параметров при равном бюджете/информации, с anti-bias fresh revalidation | После NL6-001; `NO_ADVANTAGE` допустим; AI benchmark не нужен для входа в NL7 |
| **NL8-001** | Программируемая система из нескольких связанных функций (привод, защёлка/переключатель, output), источник энергии, управление и failure model | После NL7; наблюдаемая работа, полный цикл, ограничения, внешнее экспериментальное сравнение по доступности; wet lab только через отдельный Human/domain gate |

`E4` — targeted free-energy challenge по вопросу из NL6/NL7. `E6` и атомистика — поздние demand-driven варианты, не mandatory gates. Нельзя объявлять полезную энергию, реальные секунды, КПД или автономность без отдельной проверки модели энергии/времени. Successful CI/рендер/релаксация не означает научной поддержки.

## 5. Первый полезный пользовательский сценарий

Исследователь открывает опубликованный компонент, видит provenance/rights/claim level, выбирает совместимый follower, задаёт ports/attachments, меняет один разрешённый параметр, получает корректную топологию, задаёт нагрузку и контроль, запускает независимые repeats на разрешённом scientific executor, сравнивает с исходной сборкой и сохраняет воспроизводимый **assembly package**. Отчёт содержит результаты и отрицательные outcomes, модель, ограничения, манифест данных и план экспериментальной проверки; физическая изготовимость НЕ гарантируется.

## 6. Control fences и следующая задача

После приёмки roadmap меняются только планируемые зависимости:
```text
NL5-002 → NL6-001 → NL7-001 → NL8-001
                 └── NL6-002 (non-gating)
```
В `project/plan.json` и checkpoint catalog меняются описания и границы будущих этапов; `project/state.json` и старые NL5/E2 frozen evidence **не изменяются**. Historical [POST_MVP_DEVELOPMENT_ROUTE_R1](POST_MVP_DEVELOPMENT_ROUTE_R1.md) остаётся для provenance; данная версия уточняет его после Human Gate merge. Требуется отдельный bounded WO для **PREP-S17**, затем другой scientific WO с полной preregistration и review/verify после разблокировки NL5/U1.

**Следующее действие:** независимый Reviewer + exact-head Verifier данного документационного PR, затем Human Gate merge; после merge открыть PREP-S17 как подготовительное задание, не запускать E5 преждевременно.
