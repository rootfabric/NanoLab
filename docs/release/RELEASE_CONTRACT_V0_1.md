# NanoLab Component Release Contract v0.1

Статус: **нормативный контракт** для `NL5-001` component library / release package.
Ревизия: R1 (WO-NL5-001-A-R1). Подчинён: [POST_MVP_DEVELOPMENT_ROUTE_R1](../control/POST_MVP_DEVELOPMENT_ROUTE_R1.md) Phase B и [POST_MVP_EXECUTION_PROGRAM_R1](../control/POST_MVP_EXECUTION_PROGRAM_R1.md) §3 (NL5-001-A).
Канонические совместимые источники: [DATA_CONTRACTS](../DATA_CONTRACTS.md), [E2_SOURCE_RIGHTS_G1_DECISION_R1](../control/E2_SOURCE_RIGHTS_G1_DECISION_R1.md), [LICENSE_POLICY](../../LICENSE_POLICY.md), `docs/research/E2_PROTO_R1.md`.

Изменение контракта после публикации данных = новая ревизия контракта + новая версия пакета, никогда не правка задним числом.

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

Линтер: `PYTHONPATH=scripts python3 -m release.card_lint card|rights|manifest|package …`.
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
- `source_provenance.digest_gates` — для каждого upstream-входа: `size_bytes`,
  `blob_sha1` (40 hex), `sha256` (64 hex).
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
  `reproduce.py verify`).

## 8. Reproduction interface

`reproduction/reproduce.py` (stdlib-only): `verify` — целостность пакета;
`plan` — план по карточкам (engine pins, шаги, expected, права); `self-test`.
Helper **не** скачивает входы и **не** запускает движок в v0.1: download-on-run,
исполнение и сравнение с `expected` по `tolerance_policy` выполняет внешний
воспроизводитель. Расхождение вне полосы — `REPRODUCTION_MISMATCH`, честный
сохраняемый исход.

## 9. Acceptance NL5-001-A → передача в NL5-001-B

A закрыт, когда: (1) все три схемы + линтер + тесты в `main` (после review);
(2) пример-пакет проходит `card_lint package`; (3) memo D2 опубликовано и
owner-решение получено ИЛИ явно отложено с блокировкой только публикации;
(4) настоящий контракт принят review без открытых FIX_REQUIRED.

B начинает сборку реальной библиотеки (0b/11b/32b/53b/74b) на этом контракте;
карточки B генерируются из evidence, все числа verbatim, каждая карточка
проходит линтер.
