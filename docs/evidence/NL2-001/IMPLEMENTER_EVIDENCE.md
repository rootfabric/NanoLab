# NL2-001 — Implementer Evidence Map

Исполнение: `EX-NL2-001-R1`. Дата: 2026-09-09. Роль: IMPLEMENTER (независимость review/verify — fresh-сессии).

## Intent и классы

- Work Order: `NL2-001` — реализовать схемы, manifest и E0 ([WO-NL2-001](../../work/WO-NL2-001.md)).
- Risk: `MEDIUM`. Claim: `C0_SOFTWARE_ONLY` (execution facts). Campaign-level scientific_outcome E0-R4 = **NOT_EVALUATED** (приёмка E0 — независимый review + Director).

## Exact subject

- Base SHA: `15a2c9b1b5c095e24e2e1c24afd77feef5361102`; branch `work/nl2-001-contracts-e0-r1`; START `609d4a3`.
- Subject кампании E0-R4: `ce477aad1e4a125c9e881fd9f6a741ec6d2fa876` (pre-execution commit; дайджесты 57 поверхностей — `input_digests.json`).
- Инструмент: schemas + `scripts/harness/**` бит-в-бит на base (не менялись); фикстуры/инструменты кампании — frozen поверхность `experiments/evidence/E0/E0-R1/{fixtures,tools}`.

## Что реализовано (недостающие контракты)

1. **Пререгистрация E0** — `E0-PROTO-R1` ([PREREGISTRATION_E0_R1](../../research/PREREGISTRATION_E0_R1.md)): 18 контрольных случаев с ожиданиями/критериями ДО прогонов; tolerances выведены из точности печати engine (5e-7) и запаса float64 (1e-12), не подогнаны. Новые схемы не создавались — только существующие v1-схемы; gap'ы документированы.
2. **Контрактный формат evidence** — по ремонту NL1-002 R2: манифесты-массивы (`name/sha256/size_bytes/producer_run_id/subject_sha/storage_location/producer_command`), полные машинные поля `manifest.json` (subject_sha/claim_ceiling/model/observables/stop_conditions/resource_budget), события с `experiment_id` и полным 40-hex `subject_sha`, `event_id` = имя файла, терминал последним.
3. **E0 исполнен** (кампания E0-R4): 18 случаев, 5 семей — NEG/UNIT/GEO/STATUS/POS (таблица ниже).

## Прогоны E0-R4 (subject `ce477aa`; каждый исполнен ровно один раз)

| Run | Семья | Execution | Scientific | Факт |
|---|---|---|---|---|
| N001 | NEG | COMPLETED | SUPPORTED | пустой passport → fail-closed (exit 1, нет ok:true) |
| N002 | NEG | COMPLETED | SUPPORTED | обрезанный JSON → fail-closed |
| N003 | NEG | COMPLETED | SUPPORTED | `{}` → exit 3, ok:false, errors непуст |
| N004 | NEG | COMPLETED | SUPPORTED | filename ≠ event_id → exit 3 |
| N005 | NEG | COMPLETED | SUPPORTED | первое событие ≠ WORK_ORDER_STARTED → exit 3 |
| N006 | NEG | COMPLETED | SUPPORTED | битый provenance артефакта → exit 3 |
| N007 | NEG | COMPLETED | SUPPORTED | legacy объектный манифест → fail-closed (crash exit 1; graceful-качество — заметка) |
| N008 | NEG | COMPLETED | SUPPORTED | терминал не последним → exit 3 |
| N009 | NEG | COMPLETED | SUPPORTED | контракт exit-кода: exit 3 + программный ok:false |
| U001 | UNIT | COMPLETED | SUPPORTED | T=20C→0.097717 ACCEPTED (полоса 5e-7); tier-2: конверсия найдена в pinned-исходниках `src/Utilities/Utils.cpp:333` (негейтящий артефакт) |
| U002 | UNIT | COMPLETED | SUPPORTED | кандидаты 20/293.15/0.29315/0.0978 → все REJECTED |
| G001 | GEO | COMPLETED | SUPPORTED | √2 и 90° точно (1e-12) |
| G002 | GEO | COMPLETED | SUPPORTED | нулевое плечо → ANGLE_UNDEFINED; 0.0 без NaN |
| G003 | GEO | COMPLETED | SUPPORTED | 60°/120° при смене ориентации, без перескока ветви |
| S001 | STATUS | COMPLETED | SUPPORTED | ANALYSIS_COMPLETED без scientific_outcome → exit 3 |
| S002 | STATUS | COMPLETED | SUPPORTED | scientific_outcome «PASS» → exit 3 (словарь закрыт) |
| **S003** | STATUS | COMPLETED | **NOT_SUPPORTED** | **GAP подтверждён**: технический RUN_COMPLETED с scientific_outcome=SUPPORTED принимается тихо (exit 0, ok:true) — разделение не enforced механически; сохранён как задокументированный gap (кандидат на validator hardening — NL2-003), инструмент не патчился посреди кампании |
| POS001 | POS | COMPLETED | SUPPORTED | 19/19: все 17 run-каталогов + EX + check-consistency чисты |

Campaign-level scientific_outcome: **NOT_EVALUATED**. Failed/excluded: 0 в R4.

## Дисциплина попыток (отрицательные результаты сохранены)

| Попытка | Итог | Причина | Судьба |
|---|---|---|---|
| E0-R1 | 18× RUN_FAILED_TECHNICAL | emit repo-root off-by-one; научной оценки не было | сохранена (`E0-R1/runs/*`), retry по §8 → R2 |
| E0-R2 | 17× RUN_FAILED_TECHNICAL + POS-артефакт | materialize передавал кампания-относительные пути; зашитый campaign_id в событиях | сохранена, retry → R3 |
| E0-R3 | COMPLETED с erratum | 8 каталогов-фикстур материализовались неполными (тестировалась не та поверхность); S003 KeyError; S003-RETRY1 — артефакт | сохранена как есть, superseded → R4 |
| **E0-R4** | 17 SUPPORTED + S003 NOT_SUPPORTED | — | каноническая попытка; вычитка через `python -m harness.experiment_cli validate` — ok |

Run ID ни разу не переиспользовался; ожидания не менялись с `E0-PROTO-R1` (замены только идентификаторов кампаний, каждая — отдельный superseding документ R2/R3/R4).

## Команды / доказательства

- Пререгистрации: `docs/research/PREREGISTRATION_E0_R1..R4.md`; машинные биндинги `experiments/evidence/E0/E0-R*/protocol.json` (+`supersedes`).
- Прогоны: `python tools/e0_runner.py --subject ce477aa --protocol .../E0-R4/protocol.json --digests .../input_digests.json --runs-dir .../E0-R4/runs`; фикс. поверхности извлекались subject-блобами (`git cat-file blob`) с дайджест-контролем.
- Валидация каждой published JSON — jsonschema Draft 2020-12 + FormatChecker (отчёт в `artifacts/case_record.json` каждого прогона).
- Позитивный контроль: `E0-R4-POS001` (19/19 checks).

## Приёмка (самопроверка implementer'а, не acceptance)

- [x] Пререгистрация до прогонов; tolerances не подгонялись; ожидания не менялись после просмотра результатов.
- [x] Уникальные run ID; технический/научный исходы разделены; отрицательные и INCONCLUSIVE-заметки сохранены.
- [x] Машинные timestamps; jsonschema-валидация всех контрактных JSON; манифесты-массивы по контракту NL1-002.
- [x] `project/state.json`, `project/plan.json`, `config/**`, `scripts/harness/**` не менялись; E1/E2 поверхности не тронуты; E1-прогоны не выполнялись.
- [x] Campaign-level NOT_EVALUATED; ACCEPTED не выставляется.

## Оставшиеся риски

См. `evidence-map.json` remaining_risks: gap S003 (разделение статусов не enforced — кандидат NL2-003); crash-валидаторы fail-closed, но некрасиво; одна ОС/инструментальная цепочка; engine-coupled случаи E0 — после runtime.

## Next action (один)

Независимый REVIEWER: проверить evidence-пакет E0 на exact HEAD (замороженные ожидания R1-линии, дисциплина четырёх попыток, сохранённый gap S003) → `docs/evidence/NL2-001/REVIEWER_VERDICT.md`; затем VERIFIER; merge — Human Gate.
