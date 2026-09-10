# E0-PROTO-R1 — Пререгистрация E0: контроль измерительного тракта контрактов (negative/geometric controls, units, statuses)

Идентификатор протокола: `E0-PROTO-R1`. Статус: **PREREGISTERED, НЕ ВЫПОЛНЕН**. Work Order: `NL2-001`. Исполнение: `EX-NL2-001-R1`. Ветка: `work/nl2-001-contracts-e0-r1`, base `15a2c9b1b5c095e24e2e1c24afd77feef5361102`. Дата фиксации: 2026-09-09.

Этот документ — постановка, зафиксированная **до первого прогона** кампании E0-R1. Ни один случай E0 не исполнялся: `E0 = NOT_RUN`. Machine-binding кампании: [protocol.json](../experiments/evidence/E0/E0-R1/protocol.json) (та же дата фиксации; кратности описаний не расходятся).

## 0. Правила версии

1. Все случаи, ожидания (expected), критерии, tolerances и семантика исходов зафиксированы **до первого исполнения** и не могут быть изменены после просмотра результатов иначе как новой версией `E0-PROTO-R2` с явным superseding event.
2. Новые схемы/контракты в этом WO не создаются: используются только существующие машинные схемы `config/control/harness/*.v1.json` и существующие CLI-валидаторы `scripts/harness/`. Документированный gap E0 («точные fixtures и численные допуски ещё не разработаны», [E0_PIPELINE_VALIDATION](../experiments/E0_PIPELINE_VALIDATION.md)) закрывается именно этой пререгистрацией.
3. Инструмент (schemas + validators) заморожен бит-в-бит на base; любое его изменение в середине кампании = остановка (instrument drift → BLOCKED), а не «подстройка под результат».

## 1. Вопрос, назначение и потолок утверждения

**Вопрос (из [E0](../experiments/E0_PIPELINE_VALIDATION.md)):** обнаруживает ли измерительный тракт NanoLab неправильные входы, корректные единицы и раздельные статусы прежде, чем результаты будут переданы ИИ?

**Что проверяется в R1.** Физический runtime ещё не реализован (`runtime_implemented = false`), поэтому «измерительным трактом» в R1 является контрольная поверхность контрактов: машинные схемы + CLI-валидаторы + дисциплина manifest/event. Кампания проверяет четыре свойства тракта:

1. **NEG**: дегенеративные/пустые/повреждённые входы отвергаются (fail-closed), валидатор никогда не сообщает `ok:true` на некорректной поверхности;
2. **UNIT**: единицы — pinned-engine факт конверсии `T = 20C → 0.097717` propagated консистентно, а кандидаты-подделки отвергаются;
3. **GEO**: геометрический анализ на синтетических объектах с аналитически известными значениями точен, вырожденная геометрия (нулевая ось) классифицируется `ANGLE_UNDEFINED`, смена ориентации даёт предсказанное заранее значение;
4. **STATUS**: технический outcome ≠ научный conclusion — словарь научных исходов закрыт, а разделение технического и научного либо механически обеспечено, либо его отсутствие задокументировано как gap-результат.

**Что успех НЕ доказывает:** физическую валидность oxDNA, корректность будущих engine-coupled парсеров/анализа (случаи E0-дока «повреждённая топология», «оборванный output» требуют runtime и остаются вне R1 — задокументированное ограничение §11), готовность к ИИ-оптимизации как научное утверждение. **Claim ceiling кампании: `C0_SOFTWARE_ONLY`.** Campaign-level scientific_outcome = `NOT_EVALUATED` (приёмка — независимые REVIEWER + VERIFIER, затем Director; implementer не self-accept).

## 2. Субъект и входы

- **Инструмент (заморожен):** `scripts/harness/{cli,contracts,work_cli,experiment_cli}.py` + `config/control/harness/*.schema.v1.json` на base `15a2c9b1b5c095e24e2e1c24afd77feef5361102`; SHA-256/размеры — `input_digests.json` (генерируется из сырых блобов freeze-коммита).
- **Фикстуры (SYNTHETIC, заморожены до прогонов):** `experiments/evidence/E0/E0-R1/fixtures/**` — синтетические повреждённые/валидные поверхности контрактов, табличные units-пробы и геометрии с аналитически известными значениями. Все синтетические данные явно помечены (`SYNTHETIC_TEST_GEOMETRY` / fixture-namespace `EX-FIXTURE-000`) и **не являются физическими данными**; публикация их как физики запрещена.
- **Pinned-факт единиц:** `T = 20C → 0.097717` — [ENGINE_ENVIRONMENT_R1](ENGINE_ENVIRONMENT_R1.md) §6, строка лога pinned engine `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`, OBSERVED, NL1-001 ACCEPTED. Значение не выводится заново и не пере-подгоняется.
- **Среда:** локальная Windows-станция, Python 3.11.8, `jsonschema 4.22.0`, git 2.53.0. Сеть для гейтящих шагов не нужна.

## 3. Случаи (полный список; каждый — уникальный run ID)

Полные ожидания — в protocol.json `cases`; ниже — сводная таблица. **Критерии зафиксированы до прогона; изменение после просмотра результатов запрещено.**

| Run ID | Семья | Вход | Ожидаемое поведение (frozen) |
|---|---|---|---|
| E0-R1-N001 | NEG | пустой passport.json (0 B) | валидатор fail-closed: exit ≠ 0, никогда `ok:true` |
| E0-R1-N002 | NEG | обрезанный JSON | то же |
| E0-R1-N003 | NEG | passport `{}` (все поля отсутствуют) | мягкое отвержение: exit 3, `ok:false`, errors непуст |
| E0-R1-N004 | NEG | имя файла события ≠ event_id | exit 3, `ok:false` |
| E0-R1-N005 | NEG | первое событие ≠ WORK_ORDER_STARTED | exit 3, `ok:false` |
| E0-R1-N006 | NEG | артефакт: sha256 `deadbeef`, size −1, чужой producer, 6-hex subject | exit 3, `ok:false` (provenance-контракт) |
| E0-R1-N007 | NEG | legacy объектная форма artifacts.manifest.json | fail-closed: exit ≠ 0, никогда `ok:true` (контрактная форма — массив; ремонт NL1-002 R2 F-1) |
| E0-R1-N008 | NEG | терминальное событие не последним | exit 3, `ok:false` |
| E0-R1-N009 | NEG | невалидный base_sha (контракт exit-кода) | exit 3 + программный сигнал `ok:false` в stdout |
| E0-R1-U001 | UNIT | заявленная конверсия 0.097717 | ACCEPTED (полоса 5e-7); tier-2 (негейтящий) — механический поиск ветки конверсии в pinned-исходниках |
| E0-R1-U002 | UNIT | кандидаты 20 / 293.15 / 0.29315 / 0.0978 | все REJECTED |
| E0-R1-G001 | GEO | SYNTHETIC: расстояние A–C, угол при B | |Δ| ≤ 1e-12 к √2 и 90° |
| E0-R1-G002 | GEO | SYNTHETIC: нулевое плечо | расстояние = 0.0 (не NaN); вердикт `ANGLE_UNDEFINED`, число не выдаётся |
| E0-R1-G003 | GEO | SYNTHETIC: смена ориентации плеча | 60° и 120° (аналитика до прогона), |Δ| ≤ 1e-12, без тихого перескока ветви |
| E0-R1-S001 | STATUS | ANALYSIS_COMPLETED без scientific_outcome | exit 3, `ok:false` |
| E0-R1-S002 | STATUS | ANALYSIS_COMPLETED c scientific_outcome `PASS` | exit 3, `ok:false` (словарь исходов закрыт) |
| E0-R1-S003 | STATUS | RUN_COMPLETED с scientific_outcome `SUPPORTED` (gap-проба) | контрактное ожидание — инструмент помечает смешение технического и научного; фактическое поведение фиксируется как есть; тихий пропуск = NOT_SUPPORTED, сохраняется как задокументированный gap |
| E0-R1-POS001 | POS | собственная evidence E0-R1 (17 run-каталогов + EX-NL2-001-R1 + check-consistency) | все валидации ok:true, warnings пусты, exit 0 |

## 4. Observables и правила сравнения (зафиксированы до данных)

- **NEG/STATUS:** наблюдаемые = {exit code, `ok` поле stdout, наличие подстрок}; критерий случая — побитное совпадение наблюдаемых с ожиданием §3.
- **UNIT:** вердикты `ACCEPTED/REJECTED` инструмента `units_check.py`; полоса принятия `|Δ| ≤ 5e-7` — **выведена из точности печати engine (6 значащих цифр, половина ULP последней цифры)** и зафиксирована в инструменте до прогонов; не подобрана под результат. Reference-значение 0.097717 — единственное, из pinned-источника §2.
- **GEO:** значения `geometry_check.py` (расстояния — абстрактные единицы, углы — градусы [0,180], через `atan2(|a×b|, a·b)`); допуск `1e-12` — запас арифметики float64 для аналитических координат, зафиксирован до прогонов. Ожидаемые значения (√2, 90°, 60°, 120°, 0.0) выведены из замороженных координат фикстур аналитически и записаны в protocol.json до прогона.
- **POS:** чистота валидаций (ok:true, warnings=[], exit 0) всех опубликованных поверхностей кампании.

## 5. Статистика и повторы

Все случаи детерминированы (subprocess-вызовы без RNG) — повторная реплика статистического смысла не имеет; каждый случай исполняется **ровно один раз**. Seed-политика: NOT_APPLICABLE. Повтор после `RUN_FAILED_TECHNICAL` — только под новым run ID с записанной причиной (запрещено переиспользовать ID).

## 6. Среда исполнения

Runner `tools/e0_runner.py` (заморожен до прогонов): извлекает фикстуры **сырыми блобами subject-коммита** (`git cat-file blob`, правило [ENGINE_ENVIRONMENT_R1](ENGINE_ENVIRONMENT_R1.md) §5 — рабочие копии и CRLF не считаются каноничными), сверяет sha256/size, исполняет валидаторы/инструменты как subprocess, машинно (jsonschema Draft 2020-12 + format check) валидирует каждый публикуемый JSON по v1-схемам, пишет только пост-стартовые поверхности (0002/0003-события, artifacts, artifacts.manifest.json, summary.md). Замороженные manifest.json/0001-started.json не изменяются. Timestamps — машинные (рекомендация review NL1-002). Scratch: `C:\NanoLab\scratch\nl2-001\` (disposable, вне Git).

## 7. Resource budget

CPU ≤ 120 c суммарно (локальный, sub-second на случай; U001 tier-2 — сетевой таймаут ≤ 300 c, негейтящий). Storage ≤ ~2 MB в Git. GPU/paid services — нет. Превышение → stop condition.

## 8. Семантика исходов (зафиксирована до данных)

| Исход | Условие | Фиксация |
|---|---|---|
| Случай SUPPORTED | наблюдаемые факты = ожиданию §3/§4 | execution fact; не является acceptance |
| Случай NOT_SUPPORTED | наблюдаемые ≠ ожиданию | **сохраняетсяverbatim** (negative results must be preserved); повтор «до успеха» под тем же ID запрещён |
| Технический сбой | дайджест-мисматч, crash инструмента/runner'а | `RUN_FAILED_TECHNICAL`, analysis `NOT_EVALUATED`; повтор — новый ID + причина |
| Campaign-level | всегда в этом WO | `NOT_EVALUATED` — приёмка E0 независимым review + Director |

`EXIT CODE 0` валидатора не является научным PASS; NOT_SUPPORTED — нормальный preserved-исход для gap-пробы S003, а не «неудача кампании».

## 9. Исключения и stop conditions

Post-hoc исключения запрещены; публикуются все исполненные случаи. Stop: instrument drift (sha256 инструмента ≠ input_digests.json); ≥ 2 технических сбоя внутри одной семьи → BLOCKED + repair analysis; превышение budget; изменение forbidden-поверхностей.

## 10. Границы (запрещено)

- Изменять `project/state.json`, `project/plan.json` (и на main, и в ветке), `config/**`, `scripts/harness/**` после freeze.
- Выполнять любые E1-прогоны или трогать `experiments/evidence/E1/**`, `docs/research/PREREGISTRATION_E1_*.md` (acceptance E1 = NL2-002), поверхности E2.
- Публиковать SYNTHETIC-фикстуры как физические данные; выставлять ACCEPTED/E-статусы; merge в main без Human Gate.

## 11. Известные ограничения R1

| # | Ограничение | Куда переносится |
|---|---|---|
| 1 | Engine-coupled случаи E0-дока (повреждённая топология oxDNA, оборванный trajectory, несогласованный nucleotide mapping, исчерпание бюджета) требуют runtime/парсера — их нет | следующая E0-revision после NL2-003 (runtime/provenance) |
| 2 | Windows/Python 3.11.8 — единственная среда исполнения R1 | повтор на Linux-пути при появлении CI-требования (INFRA-линия) |
| 3 | Валидаторы проверяют структуру, но не все семантические инварианты (проверяется gap-пробой S003) | задокументированный результат для NL2-003 |
| 4 | U001 tier-2 зависит от сети (GitHub через proxy); негейтящий | при недоступности — INCONCLUSIVE-заметка внутри evidence U001, tier-1 не меняется |

## 12. Связи

[WO-NL2-001](../work/WO-NL2-001.md) · [E0 doc](../experiments/E0_PIPELINE_VALIDATION.md) · [protocol.json](../experiments/evidence/E0/E0-R1/protocol.json) · [SCIENTIFIC_METHOD](../SCIENTIFIC_METHOD.md) · [ENGINE_ENVIRONMENT_R1](ENGINE_ENVIRONMENT_R1.md) · [REPAIR_MAP_R2_R1](../evidence/NL1-002/REPAIR_MAP_R2_R1.md) (контрактная форма манифестов) · [EXPERIMENT_HARNESS](../control/EXPERIMENT_HARNESS_RU.md) · [PROJECT_CONTROL](../../PROJECT_CONTROL.md).
