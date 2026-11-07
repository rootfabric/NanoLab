# AP-P0-REFERENCE — подготовка Cu bulk reference R1

Подготовлены источники, draft protocol и offline-валидатор для одного свойства массивной меди. Результат software preparation: IMPLEMENTED / independent Reviewer PASS / Verifier PASS. Научный результат NOT_EVALUATED; P0 OPEN; новых физических расчётов 0. Это завершение ближайшей подготовки, не завершение материальной валидации.

## Subject и результат

Base main: `ddf8a25cdd95a1598338816f6a585ffdde1e0f2a` (merge PR #96). START: `69a25429c9237bcd0b6084ed1e9215cfafd770fc`. Независимо проверенный implementation subject: `7c3391696a788ca15d92139adc5a184928a0a67b`, TREE `861af479f3465d85acbd9d804dfaa8437dc808cc`. Следующий publication commit добавляет только отчёты/логи/handoff и статус подготовки; это не новая версия физического протокола.

- Первичный источник: Overton–Gaffney 1955, Table II, 0 K, K^T=142.03 GPa. Значение экстраполировано из низкотемпературных измерений; число 0.34% не выдаётся за uncertainty K^T. Зафиксированы источник, условия, единицы, доступ и права.
- ASE 3.26.0 / EMT(asap_cutoff=False): шесть пинов архивов/модуля/лицензионных файлов сверены по байтам. Оригинальный APS PDF не скопирован; source fact extract имеет собственный digest, не притворяется оригинальным PDF. Прямой PDF endpoint 401/403; первичная таблица прочитана через индекс издателя независимо.
- Протокол задаёт bulk EOS, до 41 статической геометрии, контроль окна/формы fit/размера/конечных разностей. Engineering tolerance 10% и numerical sensitivity 1% разделены, как и возможная калибровочная зависимость/нулевые колебания/неизвестная experimental uncertainty. Все это draft до отдельного freeze и launch gate.
- `scripts/atomistic/reference.py` проверяет целостность JSON/Markdown, условия, единицы, fixed R1 provenance и запрет превращать preparation в launch authority. Он stdlib-only, не импортирует ASE, не обращается к сети и не считает энергию/силы. Remote pins в CLI лишь declared; независимая byte-check отдельно в отчётах.
- Исправлены review findings (evidence/repair-map.md): посторонние locators/DOI, неверная трактовка погрешности с перепинованными фактами, непроверяемый текст алгоритма. Отрицательные observations сохранены.
- Устаревшие merge blockers PR #96 сняты у adapter/app/FLOW. Добавлен один конкретный следующий AP-P0-BENCHMARK, PLANNED: generator/analysis + synthetic tests + frozen launch package. P2 по-прежнему требует material/P1 acceptance.

## Проверки

Отдельные Sol implementer/source, Reviewer и Verifier. Verifier использовал свежий clone и detached exact subject; это независимая software/source проверка на общем доступном окружении, не external physics reproduction.

| Проверка | Результат |
|---|---|
| `PYTHONPATH=scripts python3 -S -m atomistic.reference` | PACKAGE_VALID; без site-packages/ASE; NOT_EVALUATED; physics_runs=0 |
| Новые reference tests | 10/10 PASS, включая отрицательные случаи |
| Полный unittest | 1069 tests, OK, 1 явный skip actual-MD; MD не запускался |
| Все пять локальных CI gates | PASS: JSON, consistency, executions, workflow security, unittest |
| Независимые negative CLI mutations | 6/6 отклонены |
| Hosted CI implementation subject | [SUCCESS](https://github.com/rootfabric/NanoLab/actions/runs/42367292185/job/128387935790) |

Исходные отчёты без переписывания: `review/reference-review.md`, `review/reference-verifier.md`. Raw commands/logs: `evidence/verifier-logs/`. Абсолютные пути в старших логах — producer locations; durable копии лежат здесь с теми же байтами. Верхний artifacts.manifest.json фиксирует размеры и SHA-256 published evidence/reports. Исторические science state/plan, frozen NL5, runtime calculator/web/worker и прежние run artifacts не изменены.

## Ограничения и одно следующее действие

Физическая точность EMT ещё не оценивалась; agreement по fit-sensitive bulk observable не равен independent predictive validation и не переносится на наночастицы, поверхности, MD или механизмы. Numerical convergence/budget будущей кампании ещё не измерены. Протокол не заморожен, P0 не принят, текущий контейнер не признан U1/U2. C0 card не разрешает запуск.

Следующее действие: Human merge reviewable [PR #97](https://github.com/rootfabric/NanoLab/pull/97), затем AP-P0-BENCHMARK. Для actual campaign потребуются код расчёта/анализа, frozen model/inputs/environment, разрешённый executor и действующий launch gate; PREP не повторяет неизменные source audits. Merge approval PR #96 не переносится автоматически на новый PR или scientific launch.
