# WO-NL5-001-B-R1 — Сборка component library v0.1 из опубликованного evidence

## Паспорт

- Work Order: `WO-NL5-001-B-R1` (canonical Work ID `NL5-001-B`; маршрут и декомпозиция A..D — [POST_MVP_DEVELOPMENT_ROUTE_R1](../control/POST_MVP_DEVELOPMENT_ROUTE_R1.md) Phase B).
  **Коррекция (repair R1, F-B5):** упоминание несуществующей «программы §3»
  (`POST_MVP_EXECUTION_PROGRAM_R1.md`) удалено; durable источник планирования —
  POST_MVP_DEVELOPMENT_ROUTE_R1.
- Checkpoint: `NL5 / NL5-001-B`
- Base: `work/nl5-001-a-release-contract-r1 @ 9cbde33b854eeeb00abde84346c17fe3080bbe50` (stacked на контракте A; A стекируется на PR #37)
- Branch: `work/nl5-001-b-library-assembly-r1`
- Risk: `MEDIUM` — первый реальный release-пакет проекта; без физики, без canonical state
- Claim: `C0_SOFTWARE_ONLY` (публикация измерений, не интерпретаций)

## Цель

Собрать `releases/nanolab-components-v0.1/` — библиотеку из **одного семейства `dna_hinge`
с вариантами `0b / 11b / 32b / 53b / 74b`** — детерминированным builder-скриптом из
опубликованного evidence (zero new physics, ноль ручных чисел).

## Allowed paths

```text
docs/work/WO-NL5-001-B-R1.md
docs/work/executions/EX-NL5-001-B-R1/**
releases/nanolab-components-v0.1/**
schemas/components/component-card.v1.json      # amendment R1.1 (sha256_status)
scripts/release/card_lint.py                   # semantic S5
scripts/release/build_library.py               # новый builder
examples/release/**                            # refresh схем-снапшотов и карточек под R1.1
docs/release/RELEASE_CONTRACT_V0_1.md          # запись amendment
tests/test_release_contract.py                 # S5-тесты
tests/test_release_library.py                  # новый
```

## Forbidden scope

- физические прогоны, запуск oxDNA, re-measurement (карточки только из evidence);
- canonical state/plan/roadmap/WORK_QUEUE/catalog;
- выбор лицензии (D2 остаётся у владельца; пакет собирается draft-only);
- публикация пакета наружу (Human Gate NL5-001-D);
- ремонт 74b arm-manifest (отдельный bounded WO arm-manifest-v2, вне этого WO).

## Contract amendment R1.1 (обнаружено при сборке)

`source_pins.json`: для 11b/32b/53b/74b верифицирован только `blob_sha1` (registry-пин,
R1_TREE_LISTING); `sha256` вычислен при скачивании, но помечен `COMPUTED_NOT_VERIFIED`
(«recorded for future re-use; no registry claim»); у 0b и pro_CPU.in — content-verified.
Схема A требовала sha256 безусловно — это неверно отражает уровни доказанности.

Amendment: в digest-объекте `sha256` становится опциональным, добавляется
`sha256_status ∈ {CONTENT_VERIFIED, COMPUTED_NOT_VERIFIED, UNKNOWN}`; семантика S5 в
линтере: `sha256` и `sha256_status` разрешены только вместе. Пример-пакет A обновляется
под R1.1 (снапшоты схем + статусы в digest + перегенерация манифеста).

## Требуемые изменения (Definition of Done)

1. Builder `scripts/release/build_library.py` — чистая функция evidence → пакет
   (байт-в-байт воспроизводим, режим `--check`), без ручных чисел.
2. Пакет: family.json + 5 карточек + provenance/source-digests.json + reports
   (снапшоты evidence) + protocols + reproduction + RIGHTS/CITATION/VERSION +
   RELEASE_MANIFEST.json (линтером). Все карточки проходят `card_lint package`.
3. 74b — карточка NOT_MEASURED/KNOWN_GAP с фактическим отказом
   (FAILED_TWO_DOMINANT_BLOCKS, 2 attempts, runs NOT_RUN) и ссылкой на будущий
   bounded arm-manifest-v2; release не задерживается.
4. Тесты: builder --check байт-идентичен; пакет линтер-чист; контрольные числа
   (0b 65.976921401; 11b 73.928725839; 32b 78.091845516; 53b 132.35778773; 74b без
   observables) сверяются с evidence; digest-таблица сверяется с source_pins.
5. Полный unittest-гейт зелёный; canonical не менялся.

## Human gate

Merge — после A (и транзитивно после Gate 0 PR #37), по стандартному Harness
(Reviewer MEDIUM+; Verifier рекомендован). Публичный release — отдельный Human Gate
(NL5-001-D) и требует owner-решения D2.

## Repair R1 (FIX_REQUIRED Fresh Review R1)

Статус-нот: исходный handoff B (exact head `6285265`) получил
**FIX_REQUIRED** (Fresh Reviewer, `review/nl5-001-b-r1 @ ab55eb5`; review map:
`docs/evidence/NL5-001-B/REPAIR_MAP_R1.md @ 0761e53`). Ремонт выполняется на
этой же ветке как continuation (события 0004+), старые события не редактируются.

Scope ремонта = canonical repair surfaces Repair Map (расширяет allowed_paths
выше по явному полномочию map): `docs/research/REPRODUCTION_RULE_R1.md`,
`scripts/release/reproduction.py`, `tests/test_reproduction_rule.py`,
`docs/evidence/NL5-001-B/**`, `docs/work/WO-NL5-001-A-R1.md` (только битая
ссылка), паспорта A/B (только program_reference), `examples/release/**`,
`releases/nanolab-components-v0.1/**`, `scripts/release/*`,
`docs/release/RELEASE_CONTRACT_V0_1.md`, `tests/test_release_*`.

Ключевые изменения семантики относительно исходной формулировки DoD:

1. Воспроизведение — по замороженному правилу `REPRODUCTION_RULE_R1`
   (band из пер-репличных медиан; CI95 — не полоса допуска), а не «pooled
   median в пределах bootstrap CI95».
2. Builder: научные/протокольные значения выводятся из evidence
   (run-config входы, сводки, run-reports) с cross-check-гейтами; «без ручных
   чисел» теперь фактически истинно; код-own — только классифицированные
   release-метаданные.
3. Детерминизм: манифест генерируется builder-ом детерминированно
   (замороженный штамп) и входит в byte-for-byte `--check`.
4. A @ `9cbde33` фиксируется как SUPERSEDED интегрированным отремонтированным
   кандидатом B (стратегия Repair Map); отдельный ре-accept A не проводится,
   если harness не требует обратного.
