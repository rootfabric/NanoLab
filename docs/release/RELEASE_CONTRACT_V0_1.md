# NanoLab Component Release Contract v0.1

Статус: **нормативный контракт** для `NL5-001` component library / release package.
Ревизия: R1.2 (repair R1, WO-NL5-001-B-R1). Подчинён: [POST_MVP_DEVELOPMENT_ROUTE_R1](../control/POST_MVP_DEVELOPMENT_ROUTE_R1.md) Phase B (включая декомпозицию A..D).
Канонические совместимые источники: [DATA_CONTRACTS](../DATA_CONTRACTS.md), [E2_SOURCE_RIGHTS_G1_DECISION_R1](../control/E2_SOURCE_RIGHTS_G1_DECISION_R1.md), [LICENSE_POLICY](../../LICENSE_POLICY.md), `docs/research/E2_PROTO_R1.md`, [REPRODUCTION_RULE_R1](../research/REPRODUCTION_RULE_R1.md).

Изменение контракта после публикации данных = новая ревизия контракта + новая версия пакета, никогда не правка задним числом.

## Revision history

- **R1** (WO-NL5-001-A-R1): первоначальный контракт.
- **R1.1** (WO-NL5-001-B-R1, обнаружено при сборке библиотеки): digest-объект карточки —
  обязательны `size_bytes` + `blob_sha1` (registry-пин, Git blob SHA1); `sha256` опционален
  и допускается только вместе с `sha256_status ∈ {CONTENT_VERIFIED, COMPUTED_NOT_VERIFIED,
  UNKNOWN}` (семантика S5). Основание: у вариантов 11b/32b/53b/74b sha256 вычислен при
  скачивании (`COMPUTED_NOT_VERIFIED`, «recorded for future re-use; no registry claim»),
  content-verified — только входы 0b и `pro_CPU.in`. Добавлено необязательное поле
  `design` (факты arm-manifest варианта).
- **R1.2** (WO-NL5-001-B-R1 repair R1; Fresh Review R1 findings F-B1..F-B6, map
  `docs/evidence/NL5-001-B/REPAIR_MAP_R1.md`): (1) независимое воспроизведение
  сравнивается ТОЛЬКО по замороженному правилу [REPRODUCTION_RULE_R1](../research/REPRODUCTION_RULE_R1.md);
  pooled bootstrap CI95 исходной оценки — не полоса допуска (F-B3); (2) манифест —
  детерминированные release-метаданные: `generated_at_utc` — замороженный штамп сборки
  (не wall-clock), манифест входит в byte-for-byte проверку (F-B2); (3) научные/протокольные
  пины карточек выводятся builder-ом из evidence-артефактов с cross-check-гейтами;
  ручная транскрипция чисел запрещена (F-B1); (4) нормативный текст приведён к R1.1/S5
  (этот раздел, §4); (5) битая ссылка на `POST_MVP_EXECUTION_PROGRAM_R1.md` удалена —
  durable источник планирования: POST_MVP_DEVELOPMENT_ROUTE_R1 (F-B5); (6) `manifest verify`
  отвергает duplicate paths и нарушает path-семантику fail-closed до словарной свёртки (F-B6).

## 1. Назначение и границы

Контракт определяет формат публичного пакета **`nanolab-components-v0.1`**: проверенные
измеренные компоненты с машинно-читаемыми карточками, правами, provenance, manifest
и интерфейсом воспроизведения.

Не входит в контракт v0.1 (и не заявляется):

- автоматическое исполнение движка из пакета (исполнение — ответственность
  внешнего воспроизводителя по шагам карточки; автоматизация — NL5-001-C);
- научные интерпретации: карточка публикует измерения и их источники, не «смысл»;
- любые заявки сверх `claim_ceiling` карточки.

## 2. Layout пакета

```text
nanolab-components-v0.1/
  schema/                          # снимок нормативных схем (component-card, rights, manifest)
  families/<family_id>/
    family.json                    # декларация семейства и вариантов
    cards/<variant>.card.json      # карточки вариантов
  protocols/                       # pins протоколов, если не полностью в карточках
  reports/                         # человеческие сводки измерений
  provenance/                      # digest-метаданные входов (НЕ сами upstream-файлы)
  reproduction/
    README.md
    reproduce.py                   # stdlib-only: verify / plan
  RIGHTS.json
  CITATION.cff
  VERSION
  RELEASE_MANIFEST.json
```

Семантика: пакет распространяет **производные результаты NanoLab**; upstream-файлы
(REFERENCE_ONLY) в пакет не включаются — только их digest-метаданные и pins.

## 3. Нормативные схемы и исполнитель

| Артефакт | Схема |
|---|---|
| Карточка компонента | `schemas/components/component-card.v1.json` |
| `RIGHTS.json` | `schemas/release/rights.v1.json` |
| `RELEASE_MANIFEST.json` | `schemas/release/release-manifest.v1.json` |

Схемы написаны в подмножестве JSON Schema draft 2020-12 и исполняются
`scripts/release/mini_schema.py` (stdlib-only, **fail-closed**): ключевое слово вне
поддерживаемого подмножества — ошибка, а не молчаливое игнорирование. Hosted CI не
устанавливает сторонних пакетов, поэтому release-инструментарий не имеет права на
зависимости (тест-гвардеец `test_stdlib_only` следит за этим).

Линтер: `PYTHONPATH=scripts python3 -m release.card_lint card|rights|manifest|package …`
(`manifest create` требует явный замороженный `--generated-at-utc`, F-B2).
Exit-коды: `0` ok, `3` validation failure, `2` usage.

## 4. Карточка компонента: политика полей

- `schema_version: 1`, `kind: "nanolab_component_card"` — идентификация формата.
- Идентичность: `family` + `variant`; `component_id = "<family>/<variant>"`.
- `function`, `interfaces`, `operating_range` — назначение/интерфейсы/измеренная
  область; неизмеренное помечается явным `UNKNOWN`. Отсутствие проверки **никогда**
  не кодируется как PASS (правило `DATA_CONTRACTS`).
- `measurement_status`: `NOT_MEASURED | MEASURED | MEASURED_STATISTICALLY_VALIDATED`.
- `claim_ceiling`: `C0_SOFTWARE_ONLY | C1_COMPUTATIONAL_REPRODUCTION`. Новое значение
  потолка = новая ревизия схемы, не расширение на месте.
- `measured_observables` — только числа из опубликованного evidence; каждое значение
  несёт `source` (путь к evidence), `units`, `convention`, `uncertainty`, `n`.
  Выхолопливание/пересчёт «для красоты» запрещён: расхождение карточки и evidence =
  review-fail.
- `protocol_pins` — engine/engine_commit/model обязательны; seeds/steps/platform/options.
  Все научные/протокольные значения выводятся из frozen evidence-артефактов
  (run-config входы, сводки кампаний, environment-записи) и кросс-проверяются;
  ручная транскрипция чисел в builder запрещена (R1.2, F-B1). Код-own константы —
  только release/contract metadata (version, замороженный штамп манифеста,
  именование движка/конвенции/observable-идентификаторов), явно классифицированные
  в docstring builder-а.
- `source_provenance.digest_gates` — для каждого upstream-входа ОБЯЗАТЕЛЬНЫ
  `size_bytes` + `blob_sha1` (registry-пин, 40 hex); `sha256` (64 hex) —
  ОПЦИОНАЛЕН и допускается только вместе с `sha256_status` (amendment R1.1, S5).
  Значения `sha256_status`:
  - `CONTENT_VERIFIED` — sha256 сверен с registry/content-claim (например,
    R1_TREE_LISTING для 0b и `pro_CPU.in`);
  - `COMPUTED_NOT_VERIFIED` — sha256 вычислен при скачивании для будущего
    переиспользования; registry-claim нет (словарь G1);
  - `UNKNOWN` — уровень доказанности не установлен.
  Отсутствие `sha256` не ослабляет digest-гейт: registry-пин — `blob_sha1`.
- `known_gaps` / `known_limitations` — честные гэпы и ограничения; NOT_RUN не
  кодируется ни как PASS, ни как отрицательный научный результат.
- `reproduction` — `requires`, `steps`, `expected`, `tolerance_policy`,
  `rights_constraints`.
- `provenance.card_generated_from` — пути evidence, из которых собрана карточка.

### Семантические правила (card_lint; вне выразимости подмножества схемы)

| ID | Правило |
|---|---|
| S1 | `MEASURED*` → `measured_observables` непусто, каждый observable с `source`, `reproduction.expected` непусто |
| S2 | `NOT_MEASURED` → `known_gaps` непусто (гэп объявлен явно) |
| S3 | `rights_mode ∈ {REFERENCE_ONLY, DOWNLOAD_ON_RUN, MIXED}` → `upstream_repo` + `pinned_commit` (40-hex), `durable_cache = FORBIDDEN` (G1) |
| S4 | `claim_ceiling = C1_COMPUTATIONAL_REPRODUCTION` → есть измеренные данные |
| S5 | `sha256` и `sha256_status` в digest-объекте разрешены только вместе (amendment R1.1; обязательный registry-пин — `blob_sha1`) |

## 5. Семейство и варианты

Публикуется **одно семейство с вариантами**, не набор независимых компонентов.
Инварианты (enforced `card_lint package`):

- **I1** каждый вариант, объявленный в `family.json`, имеет `cards/<variant>.card.json`
  (измеренную или KNOWN_GAP);
- **I2** каждая карточка объявлена в `family.json`;
- `variant_status` покрывает ровно множество `variants`.

Правило `74b`: вариант без измерений выпускается карточкой `NOT_MEASURED` с
`known_gaps` (`status: KNOWN_GAP`, `blocking_release: false`) — гэп не задерживает
release, но и не прячется.

## 6. RIGHTS.json / CITATION.cff / VERSION

- `RIGHTS.json`: `own_code_license` / `own_docs_data_license` — только owner-решение
  (программа D2; `LICENSE_POLICY.md`: агент лицензию не назначает). Значение
  `UNDECIDED_PENDING_OWNER_DECISION` легально для draft-пакета; линтер даёт warning,
  а **публикация** пакета в этом состоянии запрещена. Item-правила: путь — POSIX
  relative, без `..`; `REFERENCE_ONLY` → `upstream_repo` + `pinned_commit`;
  `policy.durable_cache` по умолчанию `FORBIDDEN`, `download_on_run: true` для
  REFERENCE_ONLY-источников. `UNKNOWN` прав не является разрешением.
- `CITATION.cff`: title/version/message; `license`, `authors`, `date-released`
  заполняются на момент публикации (NL5-001-D), не раньше.
- `VERSION`: содержимое = semver (`MAJOR.MINOR.PATCH[-rcN]`).

## 7. Версионирование и неизменяемость

- Пакет: semver. До 1.0.0 ломающие изменения схемы/формата = минорный бамп.
- Карточка варианта **неизменяема после релиза**: исправление измерения/ошибки =
  новая версия пакета + changelog + сохранение прежней карточки (правило
  «отрицательные/промежуточные результаты не стираются»).
- `RELEASE_MANIFEST.json`: `sha256` + `size_bytes` каждого файла (кроме самого
  манифеста), роль файла; верификация — перерасчёт (`manifest verify`,
  `reproduce.py verify`). Дубликаты `path` и нарушения path-семантики
  (absolute/backslash/`..`) отвергаются fail-closed до любых свёрток (R1.2, F-B6).
- Детерминизм (R1.2, F-B2): манифест генерируется builder-ом как чистая функция
  payload + frozen release metadata. `generated_at_utc` — замороженный штамп
  сборки пакета (классифицированные release-метаданные), НЕ wall-clock;
  `card_lint manifest create` требует явный штамп. `build_library check`
  сравнивает ВЕСЬ пакет byte-for-byte, включая манифест: регенерация манифеста
  воспроизводима байт-в-байт.

## 8. Reproduction interface

`reproduction/reproduce.py` (stdlib-only): `verify` — целостность пакета;
`plan` — план по карточкам (engine pins, шаги, expected, права); `evaluate` —
сравнение отчёта независимой кампании с карточкой по замороженному правилу;
`self-test`. Helper **не** скачивает входы и **не** запускает движок в v0.1:
download-on-run, исполнение и оценку выполняет внешний воспроизводитель.

Сравнение независимой кампании с карточкой выполняется **исключительно** по
замороженному правилу [REPRODUCTION_RULE_R1](../research/REPRODUCTION_RULE_R1.md)
(копия в пакете: `reproduction/REPRODUCTION_RULE_R1.md`; нормативный исполнитель
в авторском репозитории: `scripts/release/reproduction.py`; conformance между
исполнителями закреплена тестами):

- полоса допуска — `[min, max]` пер-репличных медиан исходной кампании из
  карточки (k ≥ 2); статистика новой кампании — медиана пер-репличных медиан
  ≥ 3 валидных реплик;
- pooled bootstrap CI95 исходной оценки — характеристика точности исходной
  оценки и **не** является полосой допуска / prediction interval (F-B3);
- вердикты: `REPRODUCTION_MATCH`, `REPRODUCTION_MISMATCH` (честный сохраняемый
  исход), `INCONCLUSIVE` (меньше трёх валидных реплик — явный не-PASS),
  `TECHNICAL_FAILURE` (технический отказ, не научный mismatch);
- пороги заморожены до наблюдения новых данных; изменение = новая ревизия
  правила, никогда не правка задним числом.

## 9. Acceptance NL5-001-A → передача в NL5-001-B

A закрыт, когда: (1) все три схемы + линтер + тесты в `main` (после review);
(2) пример-пакет проходит `card_lint package`; (3) memo D2 опубликовано и
owner-решение получено ИЛИ явно отложено с блокировкой только публикации;
(4) настоящий контракт принят review без открытых FIX_REQUIRED.

B начинает сборку реальной библиотеки (0b/11b/32b/53b/74b) на этом контракте;
карточки B генерируются из evidence, все числа verbatim, каждая карточка
проходит линтер.
