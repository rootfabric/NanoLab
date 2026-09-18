# EXECUTION_PLAN_NL5_NL8_R1 — план реализации дорожной карты от NL5-002 до NL8

- Base: `main @ 48c55b3` (NL5-001 ACCEPTED, frontier `NL5`, `next_work_order = NL5-002`)
- Branch: `docs/nl5-nl8-execution-plan-r1`
- Тип: control-план; не меняет canonical state (`project/state.json`, `project/plan.json` не тронуты)
- Продолжает: `POST_MVP_DEVELOPMENT_ROUTE_R1.md` (выбор depth-first DNA-вертикали), [ROADMAP](../ROADMAP.md), [WORK_QUEUE](../work/WORK_QUEUE.md)
- Статус: предложен владельцу; исполнение начинается после подтверждения

---

## 0. Каноническая точка старта

```text
NL0–NL4  = ACCEPTED          (MVP COMPLETE)
NL5-001  = ACCEPTED          (nanolab-components 0.1.0 опубликован; PR #42, 3fb6dc1)
NL5-002  = READY             ← единственная текущая научная работа
NL5       = IN_PROGRESS

NL6-001 / NL6-002 / NL7-001 / NL8-001 = PLANNED
E0–E3 = RUN; E4/E5/E6 = NOT_RUN
external_reproductions = 0

INFRA (параллельная линия): INFRA0/1 ACCEPTED; INFRA2 IN_PROGRESS; INFRA3 PLANNED
```

Опорные факты release-пакета, от которых стартует NL5-002:

```text
пакет            = releases/nanolab-components-v0.1 (VERSION 0.1.0)
публичный интерфейс воспроизведения =
  reproduction/reproduce.py verify | plan  + карточки + RELEASE_MANIFEST.json
замороженное правило = NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE (docs/release/REPRODUCTION_RULE_V0_1.md)
опубликованные классификации карт:
  0b MATCH · 11b INCONCLUSIVE · 32b MATCH · 53b MATCH · 74b NOT_MEASURED/KNOWN_GAP
права upstream   = REFERENCE_ONLY, download-on-run, durable_cache запрещён (G1)
engine pin       = oxDNA 00dc7fb9…, CPU, double precision
upstream pin     = gauravarya77/DNA-hinge-simulations @ 23fd1ff7…
```

## 1. Управляющие правила плана

План исполняется существующими инвариантами проекта, дополнительная политика не вводится:

```text
WORK ORDER IS THE EXECUTION UNIT          — каждый этап ниже = bounded child WO
FREEZE BEFORE DATA                        — протокол/пороги/классификация до запусков
IMPLEMENTER CANNOT SELF-ACCEPT            — Fresh Reviewer (+ Verifier) → Director
EXIT CODE 0 IS NOT A SCIENTIFIC PASS      — execution/scientific outcome раздельно
NEGATIVE/INCONCLUSIVE RESULTS ARE DURABLE — честный исход не «ремонтируется» Threshold'ами
ROLE ACTOR IDENTITY ≠ EXECUTOR IDENTITY   — независимость описывается фактической средой
INFRASTRUCTURE ≠ SCIENTIFIC TRUTH         — INFRA не закрывает NL*
```

Ключевое правило очерёдности: **E5 не стартует, пока NL5-002 не принят.** Именно
external reproduction превращает библиотеку из «мы умеем воспроизводить её сами»
в переносимый научный продукт.

---

## 2. NL5-002 — внешнее воспроизведение (текущая работа)

Цель: доказать, что опубликованный `nanolab-components 0.1.0` воспроизводим вне
авторской среды, стартуя только с публичного пакета. Родитель: Work ID `NL5-002`;
исполнение дробится на дочерние WO `A→B→C→D` (по образцу цепочки NL5-001).

### 2.1 WO-NL5-002-A-R1 — заморозить протокол external reproduction

Bounded WO (risk MEDIUM, claim ceiling `C1_COMPUTATIONAL_REPRODUCTION`,
external statement only — не поднимает claims карточек). До любого запуска
фиксируются:

```text
package        = nanolab-components 0.1.0 (exact tree из RELEASE_MANIFEST.json)
starting point = только публичный release package
executor       = fresh / external; внутренние NanoLab worktrees, scripts,
                 команды и evidence (в т.ч. WO-NL5-001-C-R1) запрещены как вход
OS/runtime     = записываются executor'ом, НЕ подгоняются под авторскую среду
oxDNA          = version/build строго из release instructions пакета
upstream inputs= download-on-run по pinned commit + digest gates (REFERENCE_ONLY)
внутренние подсказки («на самом деле надо запускать вот эту внутреннюю команду»)
                 — запрещены в любую сторону
```

Классификация внешнего прогона (уровень WO), замораживается здесь же:

```text
REPRODUCED                — численное сравнение всех MEASURED карт согласовано
                            с опубликованным reproduction contract
REPRODUCED_WITH_DEVIATION — воспроизведено при задокументированных средовых/
                            tooling отклонениях, без изменения научных порогов
INCONCLUSIVE              — по замороженному правилу классифицировать нельзя
FAILED_TECHNICAL          — среда/engine/digest-отказы; не научный результат
MISMATCH                  — численный результат вне envelope по замороженному правилу
```

Соответствие пер-карточному правилу: численной инстанцией остаётся замороженный
`NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` (per-card `MATCH | MISMATCH | INCONCLUSIVE`),
публикуемый в пакете. Внешний вердикт WO-уровня вычисляется из per-card исходов и
записанных отклонений среды. `74b` = `NOT_MEASURED / KNOWN_GAP`: значения для него
в external reproduction появиться не могут.

Deliverables A: `docs/work/WO-NL5-002-A-R1.md` (полный WO по шаблону),
протокол внешнего прогона + бланк external execution report (команды, окружение,
digests, отклонения), критерии приёмки внешнего результата.

### 2.2 NL5-002-B — независимый запуск (fresh external executor)

Внешний исполнитель действует как настоящий пользователь пакета:

1. создаёт чистую среду (fresh machine/user/container; фактический уровень
   независимости фиксируется честно — отдельная машина ≠ свежий локальный user);
2. получает только публичный release package;
3. читает `README`, `RIGHTS.json`, `reproduction/README.md`, карточки;
4. самостоятельно устанавливает зависимости;
5. скачивает разрешённые upstream inputs (download-on-run, digest gates);
6. проверяет digests;
7. запускает воспроизведение по шагам карточек (`verify` → `plan` → карточка);
8. сохраняет реальные команды (все, включая неудачные попытки);
9. сохраняет environment fingerprint (OS, compiler, cmake, python, CPU);
10. сохраняет все ошибки и отклонения от instructions.

Budget: ориентир — масштаб NL5-001-C (12 runs × 150k–200k steps); бюджет внешней
среды записывается, не подгоняется; paid compute не требуется.

### 2.3 NL5-002-C — сравнение с release и bounded repair при portability gap

Сравнение внешнего результата с опубликованным reproduction contract как минимум
по `0b / 11b / 32b / 53b`; `74b` остаётся `NOT_MEASURED / KNOWN_GAP` и не должен
появиться. Portability gap — не провал проекта; bounded repair:

```text
external finding → root cause → исправление packaging/docs/tooling
→ новая package revision при необходимости (0.1.1) → свежий внешний повтор
```

Запрещено: менять научную tolerance/envelope потому, что внешний результат
«неудобный»; подсказывать внешнему исполнителю внутренние команды; чинить пакет
тихими правками без записи отклонения.

### 2.4 NL5-002-D — review / verify / Director acceptance

После успешного внешнего прогона:

```text
Fresh Reviewer → Fresh Verifier (exact-head) → Director checkpoint
```

Только тогда в canonical state:

```text
execution.external_reproductions = 1
NL5-002 = ACCEPTED
NL5     = ACCEPTED
frontier = NL6; next_work_order = NL6-001
```

Приёмка NL5 требует, чтобы независимость проверки была описана честно; вердикты
`INCONCLUSIVE / MISMATCH / FAILED_TECHNICAL` запускают repair-петлю (C) или
фиксируются как durable honest outcome — но NL5 тогда не закрывается.

---

## 3. NL6-001 — E5 driven DNA component (следующий большой научный этап)

Hinge-компоненты пока проверены как структурно-механические объекты; E5 добавляет
явное управление/воздействие. Основной вопрос (не называть «наномотором»):

> Может ли проверенный DNA hinge воспроизводимо выполнять управляемый цикл при
> заданном внешнем воздействии и нагрузке, сохраняя структурную целостность модели?

Паспорт эксперимента: [E5_DRIVEN_COMPONENT](../experiments/E5_DRIVEN_COMPONENT.md).
HIGH scientific work: Reviewer + Verifier + Director; preregistration протокола
`E5-PROTO-R1` обязательна до confirmatory data.

### 3.1 E5-A — выбрать один driven experiment

Один простой механизм воздействия, не универсальная система:

```text
hinge + external force / torque / restraint / field-like control
      ↓
open → hold/load → return
```

Заморозить: actuation variable, load, initial state, target state, cycle
definition, simulation duration, replicas. Возможности движка — по [S01](../research/SOURCES.md).

### 3.2 E5-B — измеряемые величины и исходы (до confirmatory runs)

Минимум наблюдаемых:

```text
angle/state distribution · transition success · time-to-response
return/reversibility · structural integrity · failure mode
input/work convention · load response · replica variability · resource cost
```

Заранее определить, что считается `SUCCESS / FAILURE / INCONCLUSIVE /
TECHNICAL_FAILURE`. Не смешивать удерживающие силы подготовки с приводом
исследуемого устройства (правило паспорта E5); реальные скорости/мощность не
заявляются без калибровки динамики.

### 3.3 E5-C — pilot

Небольшой pilot: проверить, что observable работает, диапазон воздействия
разумен, симуляция стабильна, нагрузка измеряется, confirmatory protocol имеет
смысл. После pilot разрешено уточнить протокол — **затем он замораживается**
(изменение критериев после данных = новая ревизия протокола, прежняя кампания
сохраняется).

### 3.4 E5-D — confirmatory campaign

```text
fresh replicas · frozen seeds policy · frozen thresholds · frozen budget
```

Проверяются минимум: actuation, response, return, repeatability, integrity,
failures. Допустимые научные исходы (все — результаты):

```text
открывается, но не возвращается          → результат
возвращается только с разрушением        → результат
не работает вообще                       → результат
```

### 3.5 E5-E — acceptance

Fresh scientific Reviewer + Fresh Verifier → Director. После acceptance:

```text
NL6-001 = ACCEPTED; E5 = RUN (verdict по протоколу); NL6-002 = READY
```

---

## 4. NL6-002 — E3-R2: повторная проверка пользы ИИ на богатом пространстве

Первый E3 дал честный negative-on-AI-advantage в маленьком дискретном
пространстве — повторять тот же benchmark бессмысленно. E3-R2 идёт **после E5**.
Паспорт: [E3_AI_BENCHMARK](../experiments/E3_AI_BENCHMARK.md) (правила равных
условий и контролей наследуются).

### 4.1 R2-A — enriched design space (bounded)

Например: hinge geometry, actuation strength, actuation position, load, cycle
timing, boundary conditions. Пространство остаётся ограниченным; тысячи
свободных параметров не открывать.

### 4.2 R2-B — заранее замороженный benchmark

Стратегии: `random · structured/grid · optimization (BO) · LLM-guided`.
Для всех одинаковые: compute budget, число experiments, доступная информация,
starting conditions. Иначе benchmark не имеет смысла (уроки NL4-002
обязательны: LLM не видит скрытых оценок; offline replay маркируется отдельно).

### 4.3 R2-C — campaign через один научный executor

Каждая стратегия предлагает эксперименты; контроллер запускает их через один и
тот же scientific executor. Измеряется не только лучший score:

```text
experiments-to-good-solution · compute cost · LLM cost
failures · invalid proposals · information efficiency
```

### 4.4 R2-D — anti-selection-bias revalidation (обязательный урок E3)

Победившая точка НЕ принимается по тем же данным: fresh seeds, fresh runs.
Итоговые вердикты: `LLM_ADVANTAGE | NO_ADVANTAGE | INCONCLUSIVE`
(`NO_ADVANTAGE` — нормальный результат).

### NL6 acceptance

NL6 закрывается только одновременно: `NL6-001 E5 accepted` + `NL6-002 E3-R2
accepted` → `NL6 = ACCEPTED`, frontier `NL7`.

---

## 5. NL7-001 — composition: из компонента в механизм

После принятого driven component собираем не одиночный компонент, а механизм:

```text
validated driven hinge + second element / load / interface → composed mechanism
```

### 5.1 NL7-A — простая композиция (одна)

Из: `hinge + load · hinge + second hinge · hinge + compliant element ·
hinge + constrained payload`. Первая композиция — из двух понятных частей,
не «наноробот».

### 5.2 NL7-B — формализованные интерфейсы

```text
force transfer · attachment · degrees of freedom · load path
energy/input transfer · failure propagation
```

### 5.3 NL7-C — detailed simulation

Проверить: coupling, back-reaction, load redistribution, structural integrity,
failure propagation. Главный вопрос: поведение сборки соответствует ожиданиям
от отдельных компонентов?

### 5.4 NL7-D — reduced model (после detailed evidence)

```text
detailed oxDNA → reduced mechanical representation
```

Reduced model валидируется на данных detailed simulation (не наоборот);
измеренная ошибка обязательна; узкий диапазон применимости фиксируется.

### 5.5 NL7-E — acceptance

После acceptance: `NL7 = ACCEPTED`, `NL8 = READY`.

---

## 6. NL8-001 — специализированная наномашина

Цель уровня «наномашины» формулируется только здесь — как конкретная проверяемая
машина, не универсальный наноробот:

```text
input → controlled transition → mechanical action → load/output → return/reset
```

### 6.1 NL8-A — одна функция

`перемещение · переключение · захват · открытие/закрытие · механическое
преобразование сигнала` — одна, не несколько.

### 6.2 NL8-B — энергетика (обязательно)

```text
откуда энергия · как вводится · сколько требуется · куда рассеивается
```

Без этого «наномашина» остаётся кинематической анимацией.

### 6.3 NL8-C — полный цикл

`state A → actuation → state B → useful action/load → reset → state A`,
повторные циклы, не одно движение.

### 6.4 NL8-D — статистика ошибок

```text
misfire · failed transition · structural damage · incomplete reset
drift · load failure
```

### 6.5 NL8-E — physical-validation plan

До этого момента всё — computational evidence. Выход к физической проверке —
отдельный новый gate: `simulation → experimental design → wet-lab/hardware
validation`; по правилам harness такие работы `CRITICAL` и требуют отдельного
human/domain gate (физический эксперимент из computational harness не запускается).

---

## 7. Условные треки (не запускаются автоматически)

### E4 — free-energy challenge

Открывается только если E5 или NL7 создаёт конкретный вопрос:

```text
почему система предпочитает state A? · есть ли barrier A→B?
какова вероятность перехода? · почему hysteresis? · какие metastable states?
```

Тогда free-energy calculation получает конкретную цель. Не запускать E4
«потому что он есть в roadmap».

### E6 — atomistic/materials adapter

Нужен, только если coarse-grained DNA model перестаёт отвечать на конкретный
вопрос: `local chemistry · surface interaction · atomistic binding ·
material-specific effect`. До этого вторая большая physics-линия невыгодна.

---

## 8. Параллельная линия INFRA2 → INFRA3

Развивается одновременно с NL5/NL6, не блокируя науку ([infra/ROADMAP](../infra/ROADMAP.md);
текущий frontier `INFRA2`, `INFRA2-001 = READY`):

```text
INFRA2  protected self-hosted CPU execution:
        isolated scientific runner · exact subject checkout · resource budgets
        · trusted dispatch · artifact collection · security boundary

INFRA3  reproducible scientific executor:
        campaign → clean environment → predictable setup → run → artifacts → provenance
```

INFRA3 напрямую полезен E5 и E3-R2 (fresh replicas, единый executor, budget
 discipline), но научный WO не ждёт INFRA: если эксперимент корректно исполняется
существующим способом, блокировки нет. INFRA никогда не закрывает `NL*`.

---

## 9. Практическая последовательность и переходы состояния

```text
СЕЙЧАС
├─ NL5-002-A  Freeze external reproduction protocol      (child WO, MEDIUM)
├─ NL5-002-B  Fresh external executor run
├─ NL5-002-C  Compare / bounded repair portability gaps
├─ NL5-002-D  Fresh Reviewer + Verifier + Director
└─ NL5 = ACCEPTED
        ▼
NL6-001 / E5: choose experiment → observables → pilot → freeze → confirmatory → accept
        ▼
NL6-002 / E3-R2: enriched space → equal-budget benchmark → strategies → fresh revalidation
        ▼  (NL6 = ACCEPTED)
NL7-001: composition → interfaces → detailed → reduced model → validation
        ▼  (NL7 = ACCEPTED)
NL8-001: one function → energy → full cycle → load/output → reset → failure stats
          → physical-validation plan
```

Переходы `project/state.json` (только через Director acceptance records):

| Событие | Изменение canonical state |
|---|---|
| NL5-002-D accepted | `NL5-002 = ACCEPTED`; `NL5 = ACCEPTED`; `frontier = NL6`; `next_work_order = NL6-001`; `external_reproductions = 1` |
| старт NL6-001 | `NL6-001 = READY→IN_PROGRESS`; `stage_status.NL6 = IN_PROGRESS` |
| NL6-001 accepted | `NL6-001 = ACCEPTED`; `E5 = RUN`; `NL6-002 = READY` |
| NL6-002 accepted | `NL6-002 = ACCEPTED`; `NL6 = ACCEPTED`; `frontier = NL7`; `next = NL7-001` |
| NL7-001 accepted | `NL7 = ACCEPTED`; `frontier = NL8`; `NL8-001 = READY` |
| NL8-001 accepted | `NL8 = ACCEPTED` (физическая валидация — отдельный будущий gate) |

## 10. Что запрещено / не сейчас

```text
НЕ начинать E5 до принятия NL5-002
НЕ передавать внешнему executor'у внутренние команды/скрипты NL5-001-C
НЕ менять научные tolerance/envelope из-за «неудобного» внешнего результата
НЕ производить значения для 74b (NOT_MEASURED/KNOWN_GAP до arm-manifest-v2)
НЕ менять критерии после просмотра данных без новой ревизии протокола
НЕ активировать E4/E6 без конкретного научного триггера
НЕ позволять INFRA блокировать научную линию
НЕ называть E5-результат наномотором/автономным нанороботом
```

## 11. Немедленные следующие действия

1. Владелец подтверждает план R1 (или правит; правка = R2 этого документа).
2. Открыть `WO-NL5-002-A-R1` (ветка `work/nl5-002-a-protocol-freeze-r1` от свежего
   `main`): полный Work Order по шаблону, freeze-блоки §2.1, бланк external
   execution report.
3. Подготовить внешнего executor'а: fresh среда + инструкция «только публичный
   пакет»; внутренние материалы NanoLab недоступны как вход.
4. После вердикта B — сравнение (C), при gap — bounded repair loop с новой
   package revision и свежим внешним повтором.
5. Свежие Reviewer/Verifier сессии → Director record → переход состояния NL5.
