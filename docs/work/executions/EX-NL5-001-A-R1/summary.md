# EX-NL5-001-A-R1 — Summary / Handoff

## Result

`IMPLEMENTED / REVIEW_REQUIRED` (MEDIUM risk, контракт + tooling; физика не запускалась).

Substantive subject: `2efbed379fce9d448ec24052724576a974ba2e05` on
`work/nl5-001-a-release-contract-r1`, based exactly on
`control/post-mvp-route-r1 @ e05793cc8ff03b3b1af2d81b38e39d82cd7527d6` (PR #37 head;
DOC/CODE-подготовка до Gate 0 разрешена программой §2, конфликтов с #37 нет — только новые файлы).

## Что сделано

Release contract v0.1 для `nanolab-components` (закрывает planning-scope NL5-001-A из программы §3):

1. **Нормативные схемы** (draft-2020-12 подмножество, исполняемые stdlib-исполнителем):
   `schemas/components/component-card.v1.json` — карточка компонента (family/variant,
   rights, claim_ceiling, measurement_status, protocol_pins, digest-объекты 40/64-hex,
   measured_observables с source-путями, known_gaps, reproduction, provenance);
   `schemas/release/rights.v1.json`; `schemas/release/release-manifest.v1.json`.
2. **Fail-closed executor + линтер**: `scripts/release/mini_schema.py` (неизвестное
   ключевое слово схемы = ошибка; bool/int guard) и `scripts/release/card_lint.py`
   (`card / rights / manifest create|verify / package`; семантики S1–S4; семейные
   инварианты I1/I2; перерасчёт SHA-256 манифеста; exit 3 при ошибке).
3. **Миниатюрный пример-пакет** `examples/release/nanolab-components-v0.1/`:
   `0b` (MEASURED — каждое число verbatim из опубликованного E2 evidence с source-путями),
   `74b` (NOT_MEASURED / KNOWN_GAP / blocking_release=false), family.json, RIGHTS.json
   (UNDECIDED_PENDING_OWNER_DECISION → draft-only), CITATION.cff (draft),
   reproduction/reproduce.py (verify/plan/self-test, без физики), RELEASE_MANIFEST.json
   (создан и верифицирован линтером).
4. **Контракт-документ** `docs/release/RELEASE_CONTRACT_V0_1.md` (layout, политики полей,
   UNKNOWN-политика, версионирование и неизменяемость карточек, reproduction interface,
   acceptance A→B).
5. **Memo D2** `docs/control/OWN_LICENSE_OPTIONS_MEMO_R1.md` — опции кода (MIT /
   Apache-2.0 / GPL-3.0-or-later / BSD-3) и docs+data (CC-BY-4.0 / CC-BY-SA-4.0 / CC0-1.0),
   release-точки применения, шаблон записи решения. Решение НЕ принято.

## Валидации

```text
python3 -m unittest discover -s tests -t .   -> Ran 338 tests, OK (310 + 28 новых)
card_lint package examples/...v0.1           -> ok (1 ожидаемый warning D2 UNDECIDED)
CONTROL_DEVELOPMENT.sh --check-consistency   -> ok (frontier NL5, next NL5-001)
CONTROL_WORK.sh validate/close EX-...-R1     -> ok
```

## Соблюдения harness

Canonical state/plan/roadmap/WORK_QUEUE/catalog не менялись; физика не запускалась;
stdlib-only (гвардеец-тест; совместимость с hosted CI); UNKNOWN — явный, отсутствие
проверки не PASS; G1-права в карточках и RIGHTS; агент лицензию не выбирал.

## Open risks / границы

- контракт — кандидат до review; ревизия при необходимости — только новой ревизией;
- публикация пакета заблокирована до owner-решения D2;
- `reproduce.py` v0.1 не исполняет движок (исполнение — NL5-001-C / NL5-002);
- CI workflow не менялся (линт исполняется unittest-гейтом).

## Next action

REVIEWER: independent review exact head `2efbed3` → merge после Gate 0 PR #37 (Human
Gate). После merge — `NL5-001-B`: сборка реальной библиотеки 0b/11b/32b/53b/74b на этом
контракте (карточки из evidence, все числа verbatim, каждая через линтер).
