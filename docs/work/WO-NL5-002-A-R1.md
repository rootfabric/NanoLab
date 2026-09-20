# WO-NL5-002-A-R1 — Freeze external reproduction protocol (nanolab-components 0.1.0)

## Паспорт

- Work Order: `WO-NL5-002-A-R1` (`NL5-002-A`, parent `NL5-002`; декомпозиция A..D из `docs/control/NL5_NL8_EXECUTION_PLAN_R1.md` §2, §11 п.2)
- Base: `main @ 48c55b3c4acdd2264527083e3072757be8bd9ada`
- Branch: `work/nl5-002-a-protocol-freeze-r1`
- Risk: MEDIUM (заморозка протокола + подготовка dispatch; физические запуски — отдельная фаза B)
- Claim ceiling: `C1_COMPUTATIONAL_REPRODUCTION` (external statement only; не поднимает claims карточек)
- Owner directive (2026-09-18): реализовывать план по пунктам, commit+push после каждого пункта.

## Цель

Одно проверяемое предложение: **до любого внешнего запуска заморожен полный протокол external reproduction пакета `nanolab-components 0.1.0` — subject pins, executor constraints, seed policy, execution design, budget/stop conditions, classification с явным mapping, формат отчёта — так что фаза B исполняется без единого авторского решения, принятого после появления данных.**

## Frozen subject (до любого запуска)

```text
package        = nanolab-components 0.1.0
canonical path = releases/nanolab-components-v0.1 @ main 48c55b3c4acdd2264527083e3072757be8bd9ada
pins (content sha256):
  RELEASE_MANIFEST.json              f87134dedf11c279fcdddb47bac2a3cc32ea98f260232ac5457bba1c64a6b7fd
  VERSION                            e9dd8507f4bf0c6f42458e41aea833ad0bd3f6127272335eee9bf4d58541ed67
  RIGHTS.json                        5292781ac4448112b3f3ecdaa47aede3f6539f8a68c357808e28dc896fa9bebf
  reproduction/README.md             c60f6c1fdd30cd9d2b08dce1bdfc9c428c3d420aba711787e32ed10a2b5625a1
  reproduction/REPRODUCTION_RULE_…   6b70dfc26764c8a21d006824f00e485df9abec8b020e67de5a9709acea793e78
  families/dna_hinge/family.json     73edf747b9259614f81be5a41994cc8c65075b6c9ae66047fbcacdda12a93e98
  cards: 0b 06aa9eb8… · 11b d17a6533… · 32b 66fc6ca9… · 53b 460a89e7… · 74b 5894f420…
манифест пакета покрывает 20/20 файлов пакета; executor проверяет целостность
пакета сам (reproduction/reproduce.py verify) — результат фиксируется в отчёте
```

Изменение этих пинов после внешнего запуска = новая package revision и новый
fresh внешний повтор (план §2.3), а не правка этого протокола.

## Frozen executor constraints

```text
executor        = fresh external agent session (без контекста авторской сессии)
вход executor'а = ТОЛЬКО: (1) побайтовая копия пакета выше, (2) Appendix A
                  этого WO (self-contained), (3) шаблон отчёта (Appendix B)
запрещено executor'у как вход: NanoLab repository/любые worktrees, внутренние
                  evidence, internal scripts, команды/наработки NL5-001-C,
                  любые авторские подсказки по ходу запуска
OS/runtime      = записываются executor'ом как есть; НЕ подгоняются под авторскую среду
движок          = oxDNA @ commit 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591, CPU,
                  double precision (пин опубликован в карточках; сборка — забота executor'а)
upstream inputs = download-on-run по exact pinned commit 23fd1ff7731e9017bd776f49206dc42d70d9fe91,
                  mandatory size + blob_sha1 gates из provenance/source-digests.json,
                  durable_cache = FORBIDDEN (REFERENCE_ONLY, G1 decision B)
74b             = NOT_MEASURED / KNOWN_GAP: значения запрещено производить
```

Известное ограничение независимости (декларируется заранее, фиксируется в отчёте):
внешняя сессия исполняется на том же физическом хосте, но в чистой изолированной
рабочей области без доступа к авторским материалам; фактический уровень
независимости описывается честно в отчёте (independence statement).

## Frozen seed policy

```text
3 fresh seeds на каждую MEASURED карту (0b, 11b, 32b, 53b)
выбираются executor'ом ДО первого запуска и записываются в отчёт до execution
ограничение: целые числа, валидные для oxDNA; НЕ равны reference seeds
             201004 / 202008 / 203012 (публичны в карточках)
никакие иные ограничения seeds executor'у не передаются (изоляция)
```

## Frozen execution design

```text
12 независимых прогонов = 4 MEASURED варианта × 3 fresh replica
шаги: 0b 200000 · 11b 200000 · 32b 150000 · 53b 150000 (по protocol_pins карточек)
вход реплики: upstream-файлы verbatim (temperature/salt/precision без изменений),
              ЕДИНСТВЕННОЕ исключение seed = fresh seed реплики
execution: single-threaded процессы, параллельность разрешена (хост 64 ядер)
analysis window: t <= 150000 (общее кросс-вариантное окно, addendum §8)
campaign statistic: median трёх per-replica median (по валидным кадрам окна)
```

## Frozen budget и stop conditions

```text
per-replica hard kill 20 h  → FAILED_TECHNICAL (не научный исход)
campaign wall budget 48 h
paid compute: НЕТ; GPU: НЕТ; модификации upstream: ЗАПРЕЩЕНЫ
немедленный stop + запись: отказ digest gate; invalid output (NaN/truncated)
в >1 прогоне одного варианта
```

## Frozen classification

Per-card (числовая инстанция, опубликована в карточках):
`NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` → `MATCH | MISMATCH | INCONCLUSIVE`
против `reproduction.expected.reference_replica_envelope_deg`; bootstrap CI —
descriptive only, никогда не tolerance.

WO-level внешний вердикт (авторская сторона, после отчёта executor'а):

```text
REPRODUCED
  0b, 32b, 53b = MATCH; 11b ∈ {MATCH, INCONCLUSIVE}; integrity gates пройдены;
  отсутствуют отклонения, потребовавшие отступления от опубликованных steps
REPRODUCED_WITH_DEVIATION
  то же числовое условие, но при задокументированных отклонениях от published
  steps/tooling, при которых научные пороги/envelope не менялись
INCONCLUSIVE
  ≥1 карту невозможно классифицировать по frozen rule без технического отказа
  (напр., <3 валидных реплик или невыполнимый analysis как опубликован)
FAILED_TECHNICAL
  кампания не состоялась научно: среда/движок/digest-отказы
MISMATCH
  ≥1 карта MISMATCH по frozen rule (все 3 реплики строго по одну сторону envelope)
```

`INCONCLUSIVE`, вызванный отсутствием в пакете обязательных элементов
опубликованной конвенции, классифицируется дополнительно как **portability
finding** → Phase C bounded repair (root cause → packaging/docs/tooling fix →
package revision при необходимости → свежий внешний повтор). Это допустимый
честный исход, не провал проекта; scientific tolerance/envelope при этом
не меняются никогда.

## Frozen report requirements

Внешний отчёт составляется строго по
`docs/work/templates/EXTERNAL_REPRO_REPORT_TEMPLATE_R1.md` (Appendix B):
identity/independence, environment fingerprint, package verify, engine build
provenance, upstream digest gates, frozen seeds, 12 run-записей (команды включая
неудачные, exit codes, wall time, digests), analysis (что доступно/чего не
хватает из пакета), per-card классификации, deviations, portability findings,
artifact manifest (sha256/size), self-assessment WO-верdict (non-binding).

## Dispatch mechanics (авторская сторона)

```text
staging = /home/rdpuser/nl5-002-external/   (вне репозитория NanoLab)
  package/           — побайтовая копия пакета (пины выше проверяются до dispatch)
  EXECUTOR_PROTOCOL.md — дословная копия Appendix A
  REPORT_TEMPLATE.md   — дословная копия шаблона (Appendix B)
  workspace/         — чистая рабочая область executor'а
dispatch = fresh subagent session; в промпте только пути staging + запрет доступа
           к NanoLab материалам; научные подсказки запрещены
ingest   = отчёт/artifacts возвращаются в repo как execution evidence фазы B
           с sha256/size манифестом; raw trajectories в Git не попадают
```

## Allowed paths

- `docs/work/WO-NL5-002-A-R1.md`
- `docs/work/templates/EXTERNAL_REPRO_REPORT_TEMPLATE_R1.md`
- `docs/work/executions/EX-NL5-002-A-R1/**`

## Forbidden paths

- canonical state/plan/roadmap/WORK_QUEUE; physics runs (фаза B); правки пакета
  `releases/**`; threshold/envelope изменения; merge в `main`.

## Validation

- Appendix A самодостаточен: executor-протокол не ссылается ни на один внутренний
  путь/документ/команду; проверяется поиском по тексту перед dispatch.
- Пины staging-копии совпадают с пинами этого WO (sha256 сверка до dispatch).
- Ни один элемент протокола не создан/не изменён после появления внешних данных.

## Risks (зафиксированы ДО любых данных)

- R1: конвенция угла (PCA axes, detector v2, frozen arm manifest) опубликована в
  карточках по ссылке на internal protocol docs, которых в пакете нет → внешний
  analysis может оказаться невыполнимым как опубликован → ожидаемый честный исход
  `INCONCLUSIVE + portability finding` → Phase C repair. Заранее это НЕ чинится:
  фаза B должна испытать пакет как опубликован.
- R2: у пакета нет корневого README — executor стартует с `reproduction/README.md`,
  `RIGHTS.json`, `family.json`; friction фиксируется как finding.
- R3: wall time ~10–14 h/replica (калибровка NL5-001-C на этом хосте) → кампания
  ~15 h при 12 параллельных прогонах; бюджет 48 h достаточен.

## Human gates

- Merge в `main` — Human Gate; owner directive миссии (2026-09-18) разрешает
  commit+push веток по пунктам плана.
- Acceptance NL5-002/NL5 — только через фазу D: Fresh Reviewer + Fresh Verifier +
  Director checkpoint с canonical state change.

## Start record

`docs/work/executions/EX-NL5-002-A-R1/passport.json` + event `0001-work-order-started`
(commit `f440f4c`) до substantive work.

## Completion

Зафиксировать exact HEAD/TREE, evidence paths, risks R1–R3 (без изменений по
сути), одно next action: dispatch фазы B на замороженном протоколе.

---

# Appendix A — EXECUTOR_PROTOCOL (frozen; копируется дословно в staging)

Роль: вы — независимый внешний исполнитель (external reproduction executor).
Вы воспроизводите опубликованный пакет как обычный пользователь. Никакой связи
с авторской средой у вас нет, кроме самой копии пакета.

## Ваша рабочая область

- workspace: `/home/rdpuser/nl5-002-external/workspace/` — пишете только сюда;
- package: `/home/rdpuser/nl5-002-external/package/` — только чтение, не изменять;
- шаблон отчёта: `/home/rdpuser/nl5-002-external/REPORT_TEMPLATE.md`.

## Разрешённые входы

1. Копия пакета в `package/` (ваш единственный источник знаний о задаче);
2. публичный интернет — только для ресурсов, которые пакет прямо требует
   (upstream inputs по exact pinned commit; исходники движка по published commit);
3. системные инструменты для сборки/запуска, которые вы устанавливаете/используете
   самостоятельно в своей рабочей области.

## Запрещено

- Читать что-либо вне вашей рабочей области, кроме разрешённых входов: никакие
  другие проекты, репозитории, кэши или файлы этого компьютера не являются вашими
  входами и не должны открываться.
- Принимать чьи-либо подсказки по ходу работы. Если чего-то не хватает — это
  finding, а не вопрос авторам.
- Изменять пакет; производить значения для карточек в статусе NOT_MEASURED
  (`74b`); менять пороги/envelope; использовать durable-кэш для upstream файлов.
- Платные сервисы; GPU.

## Порядок работы

1. Целостность пакета: `python3 reproduction/reproduce.py verify` — сохраните вывод.
2. Прочитайте пакет: `reproduction/README.md`, `RIGHTS.json`,
   `families/dna_hinge/family.json`, карточки вариантов, `reports/`,
   `provenance/source-digests.json`, `schemas/`.
3. План: `python3 reproduction/reproduce.py plan` — сохраните вывод.
4. Чистая среда в workspace; запишите environment fingerprint (OS/kernel,
   компиляторы, cmake, python, CPU/RAM, сетевой доступ).
5. Соберите движок oxDNA строго по пинам карточек (CPU build, double precision,
   commit из карточек); сохраните build provenance (команды, флаги, warnings).
6. Upstream inputs (download-on-run) строго по пинам карточек и
   `provenance/source-digests.json` (exact pinned commit; файлы по путям карточек).
   Обязательные size + blob_sha1 gates против опубликованных pins; результаты —
   таблицей. Durable-кэш запрещён; скачивание — в disposable каталог workspace.
7. Выберите и заморозьте 3 fresh seeds на каждую MEASURED карточку (0b, 11b,
   32b, 53b) ДО запусков: целые числа, валидные для движка, НЕ равные reference
   seeds 201004, 202008, 203012. Запишите в отчёт до первого запуска.
8. 12 прогонов = 4 варианта × 3 seeds. Вход реплики: upstream-файлы verbatim,
   единственное изменение — seed; число шагов по `protocol_pins` карточки
   (0b 200000, 11b 200000, 32b 150000, 53b 150000); single-threaded; параллельно
   разрешено. На каждый прогон: уникальный ID, полная команда, exit code,
   wall time, digests выходов. Hard kill реплики на 20 h → `FAILED_TECHNICAL`.
   Бюджет кампании 48 h. Останов и фиксация: отказ digest gate; invalid output
   (NaN/truncated) более чем в 1 прогоне одного варианта.
9. Анализ: общее окно сравнения `t <= 150000` шагов; per-replica median угла по
   валидным кадрам окна; campaign statistic = median трёх per-replica medians.
   Конвенция угла описана в карточках (`measurement_interface`/observables).
   Если для реализации конвенции в пакете не хватает обязательных элементов —
   зафиксируйте `PORTABILITY_FINDING` (что отсутствует, что попробовали) и НЕ
   выдумывайте значения. Дополнительный анализ допускается только с явной пометкой
   `BEST_EFFORT_NOT_CONTRACT`.
10. Классификация каждой MEASURED карточки по rule_id из карточки
    (`reproduction.expected`: reference envelope, required_fresh_replicas):
    `MATCH` — campaign statistic внутри включительного envelope; `MISMATCH` —
    все три реплики строго по одну сторону envelope; `INCONCLUSIVE` — иначе или
    данных недостаточно. Bootstrap (10000 resamples, seed 424242) — descriptive
    only, не tolerance.
11. Отчёт заполняется по `REPORT_TEMPLATE.md` целиком: все команды (включая
    неудачные попытки), все отклонения, все findings, artifact manifest
    (sha256/size/path) всего сохранённого.
12. Отрицательные и `INCONCLUSIVE` исходы — полноценные результаты. Не сглаживать.

## Результат

- `/home/rdpuser/nl5-002-external/workspace/EXTERNAL_REPRODUCTION_REPORT.md`
  (+ машинные JSON по вашему усмотрению в workspace);
- independence statement: кто вы, что было доступно, что недоступно;
- полный список findings, включая portability.
