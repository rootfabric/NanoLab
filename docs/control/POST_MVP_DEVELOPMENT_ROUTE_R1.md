# NanoLab — Post-MVP Development Route R1

Статус: **OWNER-DIRECTED CANDIDATE**, требует review/verifier и Human Gate merge в `main`.

Base: `main @ 50318c7b32576cf444f36a29ebd7c94a0cc38564` (`NL4 = MVP COMPLETE`).

## 1. Стратегическое решение

После первого MVP NanoLab развивается **depth-first по основной вертикали DNA nanomechanics**, а не breadth-first в универсальный набор несвязанных симуляторов.

Основная последовательность:

```text
NL5-001  validated component library + release package
   ↓
NL5-002  external reproduction
   ↓
NL6-001  E5 — driven DNA component under explicit actuation/load
   ↓
NL6-002  E3-R2 — AI benchmark on richer post-E5 design space
   ↓
NL7-001  composition + validated reduced models
   ↓
NL8      specialized nanomachine study
```

`E4` free-energy work открывается **targeted**, когда E5/NL7 создаёт конкретный вопрос о состояниях, переходах, барьерах или sampling. `E6` atomistic adapter остаётся поздним/demand-driven расширением и не должен задерживать DNA-механику до NL7.

## 2. Почему выбран этот путь

### NL5 сначала

MVP уже доказывает работоспособность конвейера, но перед расширением физики нужны:

- публичный воспроизводимый component/release package;
- machine-readable provenance/rights/claim ceiling;
- внешнее воспроизведение вне авторской среды;
- устранение control-state drift после NL4;
- owner license decision до публичного release собственных материалов NanoLab.

### E5 после NL5

Следующий научный прирост должен перевести проект от статического/равновесного свойства компонента к **контролируемому механическому действию**:

```text
structure → measured component → driven component → composed mechanism → nanomachine study
```

E5 должен измерять не красивую анимацию, а зарегистрированный цикл: actuation, load, response, return, integrity, failures, repeated cycles и ограничения модели.

### E3-R2 только после E5

Первый E3 честно показал отсутствие значимого преимущества LLM в небольшом дискретном пространстве. Повторять его на том же пространстве нецелесообразно.

E3-R2 открывается после E5, когда появляется более богатый design space, например:

- geometry parameter;
- actuation strength;
- attachment/drive position;
- load;
- environment/conditions в разрешённой модели.

Тогда сравнение `random / grid / BO / LLM-guided strategy` проверяет реальную приоритизацию экспериментов, а не выбор одной точки из малого allowlist.

## 3. Ближайший operational plan

### Phase A — control/release hygiene

1. Reconcile `project/state.json` после NL4:
   - убрать duplicate `NL5-001`;
   - `NL5-001 = READY`;
   - добавить принятые NL4 tasks в completed list;
   - `physics_runs = 35` по Director acceptance;
   - E3 отметить как выполненный execution fact;
   - не менять неоднозначные счётчики без отдельного evidence.
2. Закрыть/суперседить stale PR #16 отдельным housekeeping решением.
3. До публичного release получить owner decision по лицензии NanoLab.
4. Усилить protection/required checks для `main` отдельным control/infra WO; это желательно до внешнего release, но не должно превращаться в бесконечный блокер NL5.

### Phase B — NL5-001: component library v0.1

Минимальный release:

```text
nanolab-components-v0.1/
  schema/
  families/
  protocols/
  reports/
  provenance/
  reproduction/
  RIGHTS.json
  CITATION.cff
  VERSION
  RELEASE_MANIFEST.json
```

Первое семейство публикуется честно как **одно семейство DNA hinge с измеренными вариантами**, а не как несколько независимых изобретений.

Для каждого варианта: observables/distributions, integrity, protocol/model pins, provenance/digests, claim ceiling, known gaps, reproduction path и rights mode.

`74b`:
- если `arm-manifest-v2` закрывается малым bounded repair — включить измеренный результат;
- если repair разрастается — release v0.1 не задерживать, оставить `74b = KNOWN_GAP / NOT_MEASURED`.

### Phase C — NL5-002: external reproduction

External reproduction должен начинаться из release package, а не из внутренних знаний автора.

Зафиксировать:

- fresh environment;
- exact package/version;
- install/run commands;
- input retrieval and rights path;
- reproduced numerical/statistical result;
- deviations/failures;
- независимость executor/reviewer;
- repair, если выявлены portability gaps.

Приёмка NL5 требует хотя бы одного внешнего воспроизведения по canonical checkpoint contract.

### Parallel capability line — INFRA2 → INFRA3

INFRA развивается параллельно и не владеет scientific truth:

```text
INFRA2 protected self-hosted CPU route
   ↓
INFRA3 reproducible scientific executor
```

Цель — убрать зависимость кампаний от ручного состояния одной машины и подготовить repeatable execution для NL5/NL6. INFRA не закрывает NL5 автоматически.

### Phase D — NL6-001 / E5: driven DNA component

Открыть отдельный HIGH scientific Work Order с preregistration.

Первый bounded вопрос:

> Может ли проверенный DNA hinge выполнить воспроизводимый управляемый open/close (или другой выбранный) цикл при явно заданном внешнем воздействии и нагрузке, сохраняя structural integrity в пределах модели?

Минимальные измерения:

- state/angle distributions;
- actuation protocol and energy/input convention;
- load;
- success/failure definition frozen before confirmatory runs;
- return/reversibility;
- repeated cycles;
- integrity/failure modes;
- resource cost and uncertainty.

Не называть результат автономным мотором/нанороботом. Claim ceiling остаётся вычислительным до отдельной физической валидации.

### Phase E — NL6-002 / E3-R2: richer-space AI benchmark

После появления валидированного E5 design space заморозить benchmark:

- одинаковый бюджет между стратегиями;
- одинаковая доступная информация;
- random baseline;
- grid/structured baseline;
- Bayesian/optimization baseline, если применим;
- LLM-guided strategy;
- anti-selection-bias revalidation победителя на fresh seeds;
- стоимость LLM/compute учитывается;
- `NO_ADVANTAGE` остаётся допустимым результатом.

### Phase F — NL7: composition

Следующий продуктовый/научный вопрос:

```text
validated hinge/driven component
   +
second validated element or load/interface
   ↓
composed mechanism
```

Проверять coupling, back-reaction, loads, failure propagation и reduced models относительно detailed evidence.

### Phase G — targeted E4 и later E6

`E4` открывать, если требуется ответить на конкретный вопрос о free-energy landscape/transition/sampling, появившийся из E5/NL7.

`E6` открывать позже либо при явном внешнем спросе, когда ценность атомистического/materials workflow превышает стоимость расширения physics stack. Не создавать второй несовместимый orchestration core.

## 4. Ближайшая очередь выполнения

```text
NOW
  WO-POST-MVP-ROUTE-R1  ← этот control change

NEXT
  NL5-001-A  release contract + license/rights gate
  NL5-001-B  component library schema/package
  NL5-001-C  clean release reproduction
  NL5-001-D  review/verifier + release candidate

THEN
  NL5-002-A  external reproduction protocol
  NL5-002-B  independent reproduction
  NL5-002-C  deviation repair/recheck if needed
  NL5-002-D  NL5 acceptance

PARALLEL
  INFRA2 → INFRA3 bounded capability work

AFTER NL5
  NL6-001 / E5
  NL6-002 / E3-R2
  NL7-001
```

Дочерние suffix `A..D` — planning decomposition; canonical Work IDs создаются отдельными bounded Work Orders перед исполнением, чтобы не менять acceptance задним числом.

## 5. Stop / branch conditions

Путь пересматривается, если возникает хотя бы одно из условий:

- external reproduction показывает фундаментальную непереносимость MVP;
- права не позволяют выпустить полезный NL5 package;
- E5 невозможно корректно поставить в текущей модели без нового валидированного physics layer;
- появляется конкретный внешний пользователь/эксперимент, для которого E6 даёт существенно больший проверяемый научный эффект;
- E5/NL7 требует E4 до продолжения из-за неразрешённой state/free-energy неоднозначности.

Пересмотр фиксируется новой roadmap revision; отрицательный результат не стирает этот R1.

## 6. Что не меняется

- `NL4 = MVP COMPLETE` остаётся принятым.
- Первый E3 остаётся честным negative-on-AI-advantage result.
- `REFERENCE_ONLY` и другие rights restrictions сохраняются.
- E4/E6 не объявляются проваленными — только deferred/conditional.
- INFRA остаётся отдельной capability line.
- physical/wet-lab validation не заявляется без отдельного CRITICAL gate.
