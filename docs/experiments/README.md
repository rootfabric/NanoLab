# Программа экспериментов

Здесь находятся исследовательские паспорта; актуальные historical scientific статусы — в `project/state.json`, где E0–E3 RUN, E4–E6 NOT_RUN. Это не перечень готовых input decks. Численные параметры фиксируются после выбора исходных данных и до оцениваемой кампании. Новый atomistic product status P0–P6 ведётся отдельно в `project/product-state.json`; engineering pilot не переименовывается в принятый научный E6.

| ID | Вопрос | Этап |
|---|---|---|
| [E0](E0_PIPELINE_VALIDATION.md) | Правильно ли работает измерительный и программный тракт? | NL2 |
| [E1](E1_REFERENCE_REPRODUCTION.md) | Воспроизводится ли небольшой известный физический пример? | NL1 smoke → NL2 acceptance |
| [E2](E2_HINGE_COMPONENT.md) | Как изменение конструкции влияет на распределение угла? | NL3 |
| [E3](E3_AI_BENCHMARK.md) | Даёт ли ИИ измеримый вклад относительно baselines? | NL4 |
| [E4](E4_FREE_ENERGY_CHALLENGE.md) | Выявляет ли метод расхождение с ожидаемой двухстабильностью? | После NL5, отдельное решение |
| [E5](E5_DRIVEN_COMPONENT.md) | Выполняет ли компонент управляемый цикл под нагрузкой? | NL6 или позднее |
| [E6](E6_ATOMISTIC_ADAPTER.md) | Работает ли общее ядро для атомистической специализации? | P0–P3 ACTIVE engineering route; E6 science NOT_RUN/NOT_ACCEPTED |

Текущий owner-directed приоритет — [P0–P3 atomistic product](../ROADMAP.md): один material reference, real atoms/relaxation/MD в приложении, ограниченный конструктор и сравнение. Прежнее общее отложенное «E6 после NL5» не является gate инженерной линии. Разрешение только на bounded engineering validation этой mission дано [WO](../work/WO-ATOMISTIC-PRODUCT-R1.md); scientific/material campaign остаётся отдельно gated. P0 OPEN и ни один P не принят; engineering demo может поставляться UNVERIFIED/UNVALIDATED, не ожидая scientific acceptance.

E4/E5 сохраняют свои старые зависимости. Историческому DNA MVP необходимы E0–E3; сложная свободная энергия не должна его задерживать. Новая P линия не меняет frozen DNA protocols и не разрешает NL5/E5 runs.

Для каждого опыта нужны source manifest, protocol version, model card, budget, inputs, analysis, raw data manifest и acceptance report. Подготовка, runtime-success, статистическая достаточность и физическое подтверждение — разные границы.

Общие правила: [SCIENTIFIC_METHOD](../SCIENTIFIC_METHOD.md). Источники: [SOURCES](../research/SOURCES.md). Требования к результатам: [evidence](../evidence/README.md).
