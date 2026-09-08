# E1-PROTO-R1 — Пререгистрация протокола E1 (DSDNA8 / oxDNA upstream quick regression)

Идентификатор протокола: `E1-PROTO-R1`. Статус: **PREREGISTERED, НЕ ВЫПОЛНЕН**. Work Order: `NL0-003` (issue #4). Исполнение: `EX-NL0-003-R1`. Дата фиксации: 2026-09-08.

Этот документ — постановка, а не отчёт о запуске. Ни один oxDNA-прогон NanoLab не выполнялся: `E1 = NOT_RUN`, `physics_runs = 0`.

## 0. Правила версии

1. Все observables, критерии, правила исключения и семантика исходов ниже фиксируются **до первого оценочного прогона** и не могут быть изменены после просмотра результатов иначе как новой версией `E1-PROTO-R2` с явным superseding event.
2. Пилотные прогоны разрешены только в объёме §6.4 и не засчитываются как доказательство кампании.
3. Завершённый протокол не является выполненным E1: запуск, анализ и приёмка — отдельные Work Orders (NL1-002, NL2-002).

## 1. Научный вопрос и назначение

**Вопрос (из [E1](../experiments/E1_REFERENCE_REPRODUCTION.md)):** можно ли воспроизвести заранее выбранное наблюдение небольшой ДНК-системы по доступному upstream-протоколу?

**Что доказывает успех:** первый воспроизводимый NanoLab physical-model execution path — точные input-файлы → зафиксированный engine/model → run → количественное сравнение с upstream oracle → evidence.

**Что успех НЕ доказывает:** физическую валидность модели oxDNA (она проверена сообществом upstream и не проверяется этим протоколом заново), пригодность для других конструкций, самосборку, кинетику и любые claims уровня C2+. **Claim ceiling кампании: `C1_COMPUTATIONAL_REPRODUCTION`.**

## 2. Объект, входы и модель

### 2.1 Субъект

oxDNA upstream fixture `test/DNA/DSDNA8/MD` из официального репозитория `lorenzo-rovigatti/oxDNA`, pinned commit `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`. Выбор зафиксирован и принят в NL0-001 ([REFERENCE_SELECTION](REFERENCE_SELECTION.md), [SOURCES S15](SOURCES.md)); права подтверждены в NL0-002: **GPL-3.0, режим `DOWNLOAD_ON_SETUP`** — NanoLab скачивает fixture по exact commit при setup, не вендорит файлы в репозиторий.

### 2.2 Точные входы

Все четыре файла повторно скачаны и верифицированы 2026-09-08 в EX-NL0-003-R1 (см. event 0002): **SHA-256 MATCH по всем четырём позициям** против пинов NL0-001.

| Path (от корня upstream tree) | Git blob SHA-1 | Size, B | SHA-256 |
|---|---|---:|---|
| `test/DNA/DSDNA8/dsdna8.top` | `1811af7ea4bea8a86519456cba608d1e6d44ed3b` | 148 | `f1aded90b5f6e1d9adab0e55925bba778477467be2957b4093d1264160c03fc4` |
| `test/DNA/DSDNA8/init.dat` | `856be1878ece7115a91f988b2cbd7ad650daf2db` | 4498 | `0ff76d541728e0925f199970ff6296254fe6116d23e44fdf0d361d0f8891a9e0` |
| `test/DNA/DSDNA8/MD/quick_input` | `07eef592f070f9b8955f9001e0fd292de9862a4a` | 533 | `8935c4bc623ca96d406429c3c5177901f12540ffe61bcd3299931f0689af74a2` |
| `test/DNA/DSDNA8/MD/quick_compare` | `74a088ec4ceb1bc01ab2e385e4700eb2d3907f40` | 51 | `86a8b6ac50f382ba25e5aacbbef629cc5a1788f44e6c28d113509c8448e3ce27` |

Правило получения: checkout/fetch exact upstream commit; сравнение SHA-256 каждого файла до запуска; использование движущегося `master` запрещено.

### 2.3 Факты топологии и конфигурации (OBSERVED из файлов)

- `dsdna8.top`, первая строка: `16 2` — 16 нуклеотидов, 2 цепи. Далее построчно: цепь 1 = `A C G T A C G T`, цепь 2 = `A C G T A C G T` (в порядке строк файла). Комплементарность определяется моделью и геометрией конфигурации; NanoLab не пере-выводит и не «исправляет» последовательности.
- `init.dat`: заголовок `t = 329197`, box `b = 20 20 20` (единицы — внутренние единицы oxDNA; интерпретация фиксируется документацией pinned engine, см. §7).

### 2.4 Модель — зафиксированное и неизвестное

| Параметр | Значение | Статус |
|---|---|---|
| interaction_type | **не задан в `quick_input`** → default pinned engine | `UNKNOWN` до pinning engine (NL1-001); записывается при первом прогоне |
| соль | не задана → default engine | `UNKNOWN` до pinning |
| thermostat | `john` (PT-строка закомментирована: `#pt = 0.1`) → delta по умолчанию engine | `UNKNOWN` до pinning |
| seed | закомментирован: `#seed = 4982` → engine default/случайный | учтено в seed-политике §6 |
| units | внутренние единицы oxDNA | `ASSUMED`/to-confirm по документации pinned engine |

**Применимость:** укрупнённая модель oxDNA; объект — короткий дуплекс (16 nt). Ограничения интерпретации — [S02](SOURCES.md). Никаких extrapolations на другие системы этот протокол не даёт.

## 3. Условия прогона (verbatim)

Параметры `quick_input` воспроизводятся **дословно**, без модификаций, дополнений и «улучшений». Отклонение любого параметра = новая protocol revision.

```text
backend = CPU
#seed = 4982            (закомментировано upstream — сохраняется закомментированным)
steps = 1e6
newtonian_steps = 103
diff_coeff = 2.50
thermostat = john
T = 20C
dt = 0.005
verlet_skin = 0.05
topology = ../dsdna8.top
conf_file = ../init.dat
trajectory_file = trajectory.dat
refresh_vel = 1
log_file = log.dat
no_stdout_energy = 1
restart_step_counter = 1
energy_file = energy.dat
print_conf_interval = 1e5
print_energy_every = 1e3
time_scale = linear
external_forces = 0
```

(Закомментированные строки upstream-файла воспроизводятся как закомментированные; полный байт-точно файл — эталон, а не эта расшифровка.)

## 4. Подготовка

1. **Подготовки/релаксации со стороны NanoLab НЕТ.** `init.dat` — upstream starting point и используется как есть. Любая мутация геометрии = изменение исследуемого объекта = новая revision (запрещено в R1).
2. Импорт-проверки перед прогоном (go/no-go, не наука): topology разбирается как `16 2`; количество частиц в `init.dat` = 16; engine стартует без ошибок; первые строки `energy.dat` конечны (нет NaN/Inf).
3. `refresh_vel = 1` и `external_forces = 0` — часть upstream production-протокола; подготовительные ограничения в production не попадают, поскольку их нет.
4. Конфигурация используется «как собранная upstream» — это не моделирование самосборки, и выводы о сборке из него не делаются.

## 5. Observable и reference data

### 5.1 Первичный observable (единственный pass/fail)

**Определение (механическое):** среднее арифметическое значений **колонки 2** файла `energy.dat` по всем строкам production-прогона.

**Reference oracle (verbatim из pinned `quick_compare`):**

```text
ColumnAverage::energy.dat::2::-1.37970256144::0.15
```

**Критерий T1 (upstream-эквивалент):** `|ColumnAvg − (−1.37970256144)| ≤ 0.15`.

Источник значения и полосы — upstream-файл (SHA-256 выше), **не** выбор NanoLab. Порог не подбирается по результатам: он существует до любых прогонов NanoLab.

**Семантика колонки 2:** `ASSUMED` — потенциальная энергия на нуклеотид во внутренних единицах oxDNA (стандартный вывод `energy.dat`); **подтверждается по header фактического `energy.dat` и документации pinned engine при первом прогоне**. Правило сравнения механическое (та же колонка, среднее по всем строкам) и от интерпретации не зависит; если header pinned engine противоречит ASSUMED-семантике — это документируется и выносится на protocol note, критерий при этом не меняется post-hoc.

### 5.2 Диагностика целостности прогона (не pass/fail по науке)

- ожидаемое число строк `energy.dat`: `steps / print_energy_every` = 1000 (отклонение → техническая классификация §9);
- ожидаемое число конфигураций: `steps / print_conf_interval` = 10;
- отсутствие NaN/Inf во всех выводах;
- записаны engine version string, фактические effective defaults (interaction_type, thermostat delta, salt), seed, фактически использованный CPU.

### 5.3 Запрещено

Менять колонку, интервал усреднения, полосу или reference value после просмотра любых данных. Дополнительные observables могут **добавляться** только новой версией протокола и не могут задним числом стать критерием T1.

## 6. Статистика, повторы и пилот

### 6.1 Что известно (REPORTED/OBSERVED)

Upstream quick regression — однопрогонный тест; seed в upstream input закомментирован, т.е. разброс между прогонами с разными seed **встроен** в смысл upstream-полосы ±0.15.

### 6.2 Двухуровневая схема

- **T1 (обязательный):** один production run verbatim (§3) → критерий §5.1. Это прямое воспроизведение upstream-теста; число прогонов T1 не выдумывается — оно задано upstream.
- **T2 (robustness):** `R_confirm` независимых production-прогонов с различными фактически записанными seed. Критерий на каждую реплику тот же §5.1. Кампания объявляется SUPPORTED только при T1 = PASS **и** все T2-реплики в полосе (консервативно, не слабее upstream). Значения всех реплик публикуются полностью.

### 6.3 Разделение неопределённостей (требование issue #4)

- **Статистическая ошибка** = между-репликационный разброс ColumnAverage (публикуются все значения; при малом `n` — без претензии на точный CI);
- **Физическая флуктуация** = внутри-траектории (time series колонки 2; оценка корреляций/ESS — диагностически, инструменты уровня PyMBAR timeseries [S07], не gate);
- **Модельные ограничения** = §2.4 применимость (не численный критерий и не смешивается с двумя выше).

### 6.4 Пилот и момент freeze для R_confirm

`R_confirm` в R1 **не назначается** (не выдумывается). Процедура:

1. Pilot: ровно 3 независимых прогона (та же §3 конфигурация, разные seed), помечены `PILOT`, в evidence кампании не засчитываются.
2. По pilot-данным оценивается между-репликационный разброс относительно полосы ±0.15 и фактическая стоимость прогона.
3. `R_confirm ≥ 2` фиксируется в `E1-PROTO-R2` **до** confirmatory кампании с письменным обоснованием (разброс пилота, ресурсный бюджет). После старта confirmatory кампании `R_confirm` не уменьшается; полоса §5.1 не меняется никогда без superseding revision.

## 7. Среда и pinning

- Engine собирается/берётся **из pinned upstream commit `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`**; при прогоне записываются: version string, commit, build flags, backend, ОС/компилятор.
- Exact версия/окружение — предмет NL1-001; до его принятия прогон по этому протоколу не запускается.
- Если pinned engine недоступен/несобираем → `BLOCKED_ENVIRONMENT`. Тихая замена другой версией oxDNA запрещена.
- Backend — CPU (по input); GPU в R1 не используется.

## 8. Предварительная ресурсная оценка (ASSUMED, не измеренная)

- ASSUMED: 16 нуклеотидов, CPU, `1e6` steps — fixture задуман upstream как быстрый regression-тест, ожидание — минуты на одном CPU-ядре. **Измеренные** wall-time/RAM фиксируются при первом прогоне и заменяют оценку.
- Budget cap устанавливается в dispatch-документе кампании (NL1-002/E1 WO), а не здесь; превышение budget → остановка по stop conditions.
- Storage: сотни килобайт (10 конфигураций + energy/log); raw-артефакты сохраняются с manifest (SHA-256, size, producer run).

## 9. Семантика исходов (зафиксирована до данных)

| Исход | Условие | Научный outcome |
|---|---|---|
| Reproduction | Выполнение завершено; T1 PASS и все T2-реплики в полосе; целостность §5.2 OK | `SUPPORTED` (C1: воспроизведён upstream oracle) |
| Не воспроизведено | Выполнение завершено; целостность OK, но T1 или ≥1 T2-реплика вне полосы | `NOT_SUPPORTED` — негативный результат сохраняется, повтор «до успеха» запрещён |
| Технический сбой | Падение engine, NaN/Inf, неверное число строк, битые входы, несошедшийся SHA-256 | `FAILED_TECHNICAL` run с уникальным ID (сохраняется); допускается новый run с новым ID и записанной причиной; в научное сравнение не идёт |
| Среда | Pinned engine недоступен/несобираем | `BLOCKED_ENVIRONMENT` |
| Недостаток информации | Header/семантика колонки противоречит предположению; effective defaults неустановимы; окружение не пинится | `INCONCLUSIVE` с документированным ограничением |

`INCONCLUSIVE` ≠ `NOT_SUPPORTED`: первое — «мы не можем корректно судить», второе — «корректно судили, критерий не выполнен». Оба сохраняются в evidence. Exit code 0 сам по себе не научный PASS.

## 10. Исключения и stop conditions

- Post-hoc исключение прогонов из сравнения запрещено. Исключаются только прогоны, заранее классифицированные как `FAILED_TECHNICAL` по §9, и они остаются в evidence.
- Stop: превышение budget; ≥2 технических сбоя на одном этапе → фиксация `BLOCKED` + repair analysis; исчезновение pinned upstream objects → блок.

## 11. Известные ограничения и открытые UNKNOWN

| # | Неизвестное | Owner / момент закрытия |
|---|---|---|
| 1 | Effective `interaction_type`/salt/thermostat delta (defaults engine) | NL1-001 pinning; запись при первом прогоне |
| 2 | Engine version/build pin | NL1-001 |
| 3 | Семантика колонки 2 `energy.dat` | подтверждение header'ом при первом прогоне (§5.1) |
| 4 | `R_confirm` | `E1-PROTO-R2` после пилота (§6.4) |
| 5 | Измеренный budget | первый прогон / dispatch кампании |
| 6 | Физическая валидность oxDNA, сборка, кинетика | вне scope этого протокола (S02) |

## 12. Связи

[WO-NL0-003](../work/WO-NL0-003.md) · [E1 doc](../experiments/E1_REFERENCE_REPRODUCTION.md) · [SCIENTIFIC_METHOD](../SCIENTIFIC_METHOD.md) · [REFERENCE_SELECTION](REFERENCE_SELECTION.md) · [INPUT_AVAILABILITY](INPUT_AVAILABILITY.md) · [SOURCES S15](SOURCES.md) · [RIGHTS_AND_REDISTRIBUTION_AUDIT](RIGHTS_AND_REDISTRIBUTION_AUDIT.md) · [EXPERIMENT_HARNESS](../control/EXPERIMENT_HARNESS_RU.md).
