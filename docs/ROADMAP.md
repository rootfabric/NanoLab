# Дорожная карта NanoLab

**Текущий frontier: `NL5` — внешнее воспроизведение release-пакета; `NL5-002` исполнен с terminal `MISMATCH` (verified, 2026-09-19) и находится в `WAITING_HUMAN` (disposition — Human Gate). `NL0–NL4` приняты целиком (NL4 = AI NanoLab MVP COMPLETE); `NL5-001` принят (2026-09-18): опубликован пакет `nanolab-components 0.1.0` с финализированными лицензиями (код Apache-2.0; docs/data CC-BY-4.0; сторонние права не перелицензованы) и clean reproduction классификацией 0b/32b/53b MATCH, 11b INCONCLUSIVE, 74b honest gap до arm-manifest-v2; NL5-002 external reproduction (пакет v0.1.1 после bounded repair): 11b/53b MATCH, 0b/32b MISMATCH по frozen rule (пороги не менялись; Fresh Reviewer PASS be945f1 + Verifier PASS 4116468) — NL5 acceptance НЕ объявлен; статусы экспериментов: `E0 = RUN`, `E1 = SUPPORTED`, `E2 = RUN`, `E3 = RUN` (честный negative-on-AI-advantage).** Актуальные статусы хранятся в [state.json](../project/state.json), зависимости работ — в [plan.json](../project/plan.json), post-MVP решение — в [POST_MVP_DEVELOPMENT_ROUTE_R1](control/POST_MVP_DEVELOPMENT_ROUTE_R1.md), сводка приёмок — в [WORK_QUEUE](work/WORK_QUEUE.md). Сроки и стоимость устанавливаются по измерениям, а не по обещанию ускорения от ИИ.

```text
NL0  Научная постановка и доступные эталоны
 ↓
NL1  Первый исполняемый физический эксперимент без ИИ
 ↓
NL2  Проверяемость, статистика, происхождение данных
 ↓
NL3  Параметризованная лаборатория нанокомпонента
 ↓
NL4  AI NanoLab MVP и измерение вклада ИИ
 ↓
NL5  Проверенная библиотека и внешнее воспроизведение
 ↓
NL6  Управляемый DNA-компонент (E5) + E3-R2 на богатом design space
 ↓
NL7  Составные системы и проверенные упрощённые модели
 ↓
NL8  Исследование специализированных наномашин
```

## Выбранная post-MVP траектория

После закрытия MVP проект развивается **depth-first по DNA nanomechanics**:

```text
NL5-001  component library + release package
   ↓
NL5-002  external reproduction
   ↓
NL6-001  E5 driven DNA component
   ↓
NL6-002  E3-R2 richer-space AI benchmark
   ↓
NL7-001  composition + reduced models
   ↓
NL8      specialized nanomachine study
```

`E4` free-energy challenge не отменён: он открывается targeted, если E5/NL7 создаёт конкретный вопрос о состояниях, переходах, барьерах или sampling. `E6` atomistic adapter остаётся поздним/demand-driven расширением и не должен задерживать основную DNA-механическую вертикаль до NL7.

Параллельная capability-линия `INFRA2 → INFRA3` может развиваться одновременно с NL5, но INFRA не владеет scientific truth и не закрывает NL5/NL6 автоматически.

## Этапы и условия завершения

| Этап | Результат | Проверяемая граница |
|---|---|---|
| NL0 | Выбран небольшой эталон E1 и кандидат семейства шарниров E2; проверены источники, доступ и права | Есть исходные файлы либо явно оформленный путь их получения; определения наблюдений и предварительные критерии сравнения; нет скрытых допущений |
| NL1 | Зафиксированная среда, запуск oxDNA без ИИ, первичный анализ | Исходный файл → подготовка → расчёт → сохранённый результат проходит в чистой среде; измерена стоимость |
| NL2 | Контракты, provenance, E0, статистический анализ и воспроизведение E1 | Обнаруживаются заданные ошибки; повторный запуск подтверждает вывод в согласованных пределах; исходники и анализ связаны с результатом |
| NL3 | Семейство допустимых шарниров и воспроизводимая серия E2 | Определено распределение угла, оценены целостность и статистика, получена зависимость от параметров без заранее навязанного тренда |
| NL4 | Пользовательская цель → ограниченный агент → расчёты → отчёт | Выполнен E3, работают бюджеты и восстановление; вклад ИИ измерен относительно контроля; готов публичный воспроизводимый сценарий |
| NL5 | Несколько карточек/вариантов в честно оформленном component package, эталоны и архивы | Хотя бы один release package воспроизведён вне авторской среды; независимость проверки описана честно; rights/claim ceiling явны |
| NL6 | E5 driven DNA component + E3-R2 на обогащённом post-E5 design space | Управляемый цикл проверен под явным воздействием/нагрузкой; ошибки и целостность измерены; AI benchmark повторён при равном бюджете и fresh revalidation победителя |
| NL7 | Соединённые компоненты и модели уменьшенной сложности | Поведение сборки проверено относительно подробных расчётов; учтены нагрузка, среда, coupling и обратное влияние |
| NL8 | Конкретная специализированная наномашина как исследовательская задача | Определены источник энергии, полный цикл, управление, ошибки и физическая проверка; критерии уточняются после NL7 |

**NL4 — закрытая граница первого продукта.** Следующее развитие не должно превращать NanoLab в широкий набор несвязанных physics adapters до проверки основной DNA-механической вертикали.

## Ближайший план действий

### 1. Control/release hygiene (текущее состояние)

- `project/state.json` синхронизирован: `NL5-001 = ACCEPTED`, `next = NL5-002`, лицензионное open decision закрыто (D2);
- owner decision по лицензии получен 2026-09-18 (D2): код Apache-2.0; документация + derived data CC-BY-4.0; сторонние права не перелицензованы;
- stale PR/старые control surfaces закрывать или supersede отдельным housekeeping решением;
- protection/required checks для `main` усилить отдельным bounded control/infra WO.

### 2. NL5-001 — component library v0.1 (ВЫПОЛНЕНО и ПРИНЯТО, 2026-09-18)

Release `nanolab-components 0.1.0` включает machine-readable schema, family/variant cards, protocols, reports, provenance, reproduction, rights, citation/version и детерминированный release manifest. Первое DNA hinge family опубликовано как **одно семейство с измеренными вариантами**; clean reproduction: 0b/32b/53b MATCH, 11b INCONCLUSIVE, 74b `KNOWN_GAP / NOT_MEASURED` — честное состояние v0.1 (arm-manifest-v2 — отдельный будущий WO).

### 3. NL5-002 — external reproduction (ИСПОЛНЕН: terminal MISMATCH, WAITING_HUMAN)

Цепочка 2026-09-19: A frozen protocol → B-R1 INCONCLUSIVE+PORTABILITY_FINDING (сохранён) → C bounded repair v0.1.1 (science byte-identical) → B-R2 12/12 валидных реплик exit=0 → C2 binding MISMATCH (0b/32b вне frozen envelopes, 11b/53b MATCH; 74b NOT_MEASURED; threshold tuning отсутствует). Fresh Reviewer PASS `be945f1`, Fresh Verifier PASS `4116468`; integration candidate `integration/nl5-002-r1 @ 33935ae`. Приёмка NL5 требует успешного воспроизведения — НЕ выполнено; disposition (platform-sensitivity research WO / optional packaging v0.1.2 / acceptance policy) — Human Gate: `docs/evidence/NL5-002/DIRECTOR_DECISION_R1.md`.

### 4. Параллельно INFRA2 → INFRA3

Подготовить protected self-hosted CPU route и reproducible scientific executor. Это capability work, а не scientific acceptance.

### 5. NL6-001 — E5 driven DNA component

Отдельный HIGH scientific Work Order и preregistration: явное внешнее воздействие, нагрузка, state/angle distributions, success/failure rule, return/reversibility, repeated cycles, structural integrity, uncertainty и ограничения модели. Результат называется externally driven component, не автономным мотором/нанороботом.

### 6. NL6-002 — E3-R2

Только после E5 сформировать более богатое пространство параметров и сравнить random/grid/optimization/LLM-guided стратегии при равном бюджете и информации. Победитель обязательно получает anti-selection-bias revalidation на fresh seeds. `NO_ADVANTAGE` остаётся допустимым исходом.

### 7. NL7 — composition

Соединить проверенные компоненты/нагрузки/интерфейсы; измерять coupling, back-reaction, failure propagation и проверять reduced models относительно detailed evidence.

### 8. E4/E6 по условию

E4 подключается для конкретного free-energy/state-transition вопроса из E5/NL7. E6 — позже либо при явном внешнем спросе, когда его проверяемая ценность выше стоимости расширения physics stack.

## Связь с экспериментами

E0 проверяет программный измерительный тракт, E1 — небольшой известный физический пример, E2 — шарнир и параметрическую зависимость, E3 — пользу ИИ в первом MVP. E5 становится основной следующей научной специализацией; E3-R2 повторно проверяет пользу ИИ уже на более содержательном post-E5 пространстве. E4 исследует сложный свободноэнергетический ландшафт по конкретной необходимости; E6 — второй физический адаптер. [Подробная программа](experiments/README.md).

Простой запуск E1 относится к NL1. Его научная приёмка со статистикой и проверками относится к NL2. Это разные результаты, а не двойной подсчёт одного успеха.

## Правила продвижения

Завершение стадии требует ссылок на конкретный commit/tree, протоколы, исходные данные и отчёт. Документ, PR или сообщение агента сами по себе стадию не закрывают. Неудача гипотезы может быть полноценным научным результатом, если метод прошёл проверки.

Изменение критерия после просмотра результатов оформляется новой версией протокола. Предыдущая кампания остаётся доступной. При нехватке статистики результат — INCONCLUSIVE, при недоступном оборудовании — BLOCKED_ENVIRONMENT, а не научное опровержение.

## Параллельная работа

До NL4 разрешались ограниченные вспомогательные работы: библиография, проверка прав, независимые тестовые данные, рецензирование критериев и документация. После MVP научный runtime по-прежнему сохраняет одну основную вертикаль; параллельно может развиваться INFRA capability line и bounded release/reproduction work без конфликтующих scientific subjects.

Параллельные агенты не меняют одни контракты, не запускают одну кампанию дважды и не создают альтернативную систему статусов.

После NL5 направление научного расширения в R1 уже выбрано: **E5 driven DNA component**, затем E3-R2 и NL7 composition. Пересмотр возможен только новым durable roadmap decision при появлении существенного evidence, blocker или внешнего спроса. Планируемые наноматериалы, наноэлектроника, сенсоры и машинные компоненты сохранены в [портфеле исследований](RESEARCH_PORTFOLIO.md).
