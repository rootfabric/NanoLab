# NanoLab Component Release Contract v0.1

Статус: **нормативный контракт-кандидат** для `NL5-001` component library / release package.

Канонический маршрут: [POST_MVP_DEVELOPMENT_ROUTE_R1](../control/POST_MVP_DEVELOPMENT_ROUTE_R1.md), Phase B. Durable planning decomposition `NL5-001-A..D` хранится в этом route-документе; ссылки на несуществующий `POST_MVP_EXECUTION_PROGRAM_R1.md` не используются.

Совместимые источники: [DATA_CONTRACTS](../DATA_CONTRACTS.md), [E2_SOURCE_RIGHTS_G1_DECISION_R1](../control/E2_SOURCE_RIGHTS_G1_DECISION_R1.md), [LICENSE_POLICY](../../LICENSE_POLICY.md), `docs/research/E2_PROTO_R1.md`, [REPRODUCTION_RULE_V0_1](REPRODUCTION_RULE_V0_1.md).

Изменение контракта после публикации данных = новая ревизия + новая версия пакета; старый release не переписывается задним числом.

## Revision history

- **R1** — исходный контракт `WO-NL5-001-A-R1`.
- **R1.1** — digest honesty: mandatory registry-level fields = `size_bytes + blob_sha1`; `sha256` optional и допустим только парой с `sha256_status`; добавлено optional `design`.
- **R1.2 / B-Repair-R1** — frozen independent-reproduction rule; full-package deterministic manifest; fail-closed duplicate/unsafe manifest paths; scientific/protocol pins обязаны происходить из evidence/config, а не из duplicated literals; stale planning reference удалён.

## 1. Package layout

```text
nanolab-components-v0.1/
  schema/
  families/<family_id>/
    family.json
    cards/<variant>.card.json
  protocols/
  reports/
  provenance/
  reproduction/
    README.md
    reproduce.py
  RIGHTS.json
  CITATION.cff
  VERSION
  RELEASE_MANIFEST.json
```

Пакет распространяет производные результаты NanoLab; upstream `REFERENCE_ONLY` bytes в release не включаются.

## 2. Component card

Нормативная схема: `schemas/components/component-card.v1.json`; fail-closed executor: `scripts/release/mini_schema.py`; semantic checks: `scripts/release/card_lint.py`.

Обязательные принципы:

- `family + variant`, один family с вариантами, не набор независимых «изобретений»;
- `UNKNOWN` явный; отсутствие проверки никогда не PASS;
- `measurement_status`: `NOT_MEASURED | MEASURED | MEASURED_STATISTICALLY_VALIDATED`;
- `claim_ceiling`: максимум `C1_COMPUTATIONAL_REPRODUCTION` в этой schema line;
- каждое measured observable содержит source path и единицы/convention;
- protocol/scientific pins генерируются из frozen evidence/config sources;
- `74b` остаётся `NOT_MEASURED / KNOWN_GAP` до отдельного arm-manifest-v2.

### Digest semantics R1.1

Для каждого upstream input:

- `size_bytes` — **mandatory**;
- `blob_sha1` — **mandatory registry pin** (Git blob SHA-1);
- `sha256` — optional;
- если присутствует `sha256`, обязательно присутствует `sha256_status`;
- если присутствует `sha256_status`, обязательно присутствует `sha256`.

`sha256_status`:

- `CONTENT_VERIFIED` — SHA-256 проверен против отдельного registry/evidence claim;
- `COMPUTED_NOT_VERIFIED` — SHA-256 вычислен при download, но отдельного registry claim нет;
- `UNKNOWN` — доказанность SHA-256 не установлена.

### Semantic rules

| ID | Rule |
|---|---|
| S1 | `MEASURED*` → observables/source и reproduction expected непусты |
| S2 | `NOT_MEASURED` → known gap обязателен |
| S3 | `REFERENCE_ONLY/DOWNLOAD_ON_RUN/MIXED` → upstream repo + pinned commit + durable cache FORBIDDEN |
| S4 | `C1_COMPUTATIONAL_REPRODUCTION` → measured data |
| S5 | `sha256` ↔ `sha256_status`: поля допускаются только вместе |

Family invariants: I1 — каждый declared variant имеет card; I2 — каждая card объявлена family.

## 3. Reproduction rule

Нормативный документ: `docs/release/REPRODUCTION_RULE_V0_1.md`; machine implementation: `scripts/release/reproduction_rule.py`; rule id: `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`.

**Запрещено** использовать исходный pooled bootstrap CI95 как prediction/tolerance interval независимой reproduction campaign.

Card/release публикует reference per-replica medians/envelope. Independent unit = replica median. При трёх fresh replicas:

- `MATCH`: median fresh replica medians внутри pre-existing reference replica envelope;
- `MISMATCH`: все fresh replica medians полностью и однонаправленно отделены от reference envelope;
- `INCONCLUSIVE`: недостаточно валидных replicas, incomplete integrity/analysis либо промежуточный случай;
- technical failures фиксируются отдельно.

Это operational computational-reproduction classification, не физическая validation claim.

## 4. RIGHTS / citation / version

`RIGHTS.json` допускает `UNDECIDED_PENDING_OWNER_DECISION` только для draft. Публичный release запрещён до owner D2. `REFERENCE_ONLY` не означает redistribution permission. `CITATION.cff` и `VERSION` финализируются в NL5-001-D.

## 5. RELEASE_MANIFEST determinism and hardening

Manifest содержит SHA-256 + size + role каждого package file, кроме самого manifest.

Для release candidate v0.1 manifest **детерминирован**: wall-clock timestamp не является обязательным содержимым и не должен менять bytes повторной сборки. `generated_by` и optional frozen subject описывают происхождение.

Verifier обязан:

- reject duplicate `path` entries до преобразования в mapping;
- reject absolute paths, backslashes и `..`;
- reject missing/unlisted files;
- recompute SHA-256 и size;
- compare package version with `VERSION`.

Full-package deterministic check включает `RELEASE_MANIFEST.json`.

## 6. Builder provenance

Нормативный builder обязан брать machine-readable scientific/protocol numeric fields из published evidence/config:

- window/steps;
- seeds;
- engine/model/environment pins;
- print intervals/salt where emitted;
- bootstrap analysis pins where emitted;
- source/digest pins.

Release metadata (`VERSION`, schema identifiers, labels/prose) может быть code-owned. Human-authored prose не является источником научного numeric claim.

Tests сравнивают generated machine fields непосредственно с evidence/config, а не только с дублированными constants в тестах.

## 7. Acceptance A/B → C

До NL5-001-C:

1. R1.2 contract + reproduction rule должны пройти Fresh Re-review;
2. package lint зелёный;
3. full-package byte-identical rebuild зелёный;
4. manifest duplicate/path negative controls зелёные;
5. evidence-vs-generated protocol pin tests зелёные;
6. `74b` остаётся честным NOT_MEASURED;
7. D2 может оставаться unresolved только как publication blocker, не как причина выдумать license.

A @ `9cbde33` является историческим pre-amendment subject и не принимается отдельно как финальный контракт; repaired integrated B supersedes его для NL5-001 release candidate.
