# NL2-001 — REPAIR MAP F1 (исправление по REVIEWER VERDICT FIX_REQUIRED, findings F1–F7)

- Repair execution: `EX-NL2-001-R1` (та же ветка `work/nl2-001-contracts-e0-r1`; EX-журнал событий остаётся терминально закрытым — corrections публикуются новыми evidence-документами и campaign-событиями, по прецеденту «corrections — новым event»).
- Основание: `docs/evidence/NL2-001/REVIEWER_VERDICT.md` (ветка `review/nl2-001-contracts-e0-r1` @ `2c3b485f5cd993f75336d966285958b25e97e08c`), вердикт `FIX_REQUIRED`, научное/контрольное содержание подтверждено — ремонт касается только пакета доказательств.
- Ремонтируемый subject: `2cee872179bbcccff93c1b9458c6b25ea491a999` (проверенный reviewer'ом HEAD).
- Run ID не переиспользовались; **новых прогонов нет** (исходы не меняются — подтверждено reviewer'ом и настоящим ремонтом).

## 1. F1 — Root cause

`tools/e0_runner.py::emit_run` сериализовал `artifacts.manifest.json` **до** финальной перезаписи `artifacts/case_record.json`, добавляющей ключ `schema_validation["artifacts.manifest.json"]`. Следствие: запись `case_record.json` в манифесте содержала sha256/size **pre-image** (версии без финального ключа); в Git опубликованы байты с финальным ключом — систематически **+35 байт**. Манифест не описывал опубликованные байты → нарушение provenance-контракта (`RAW ARTIFACT REUSE REQUIRES DIGEST + PROVENANCE`), не задокументированное имплементёром.

## 2. Pre-image воспроизведение (механически, до ремонта)

| Проверка | Результат |
|---|---|
| Run-каталогов проверено (R1+R2+R3+R4) | 73 |
| `case_record.json`: recorded digest ≠ фактические байты | **73/73** |
| Pre-image (удаление финального ключа `schema_validation["artifacts.manifest.json"]` + каноничная сериализация) восстанавливает recorded sha256+size | **73/73** |
| Размерный дельта (фактические байты − pre-image) | всегда **+35** байт |
| Прочие записи манифестов (stdout/stderr/extras) vs байты | 0 расхождений |

## 3. Метод ремонта (по прецеденту NL1-002 R2/F-1)

В каждом из 73 run-каталогов:

1. исходный `artifacts.manifest.json` сохранён **byte-equal** как `artifacts.manifest.v1-superseded.json`;
2. канонический `artifacts.manifest.json` переписан с **пересчитанными** `sha256`/`size_bytes` из фактических байтов `artifacts/*` (все прочие поля — name/producer_run_id/subject_sha/storage_location/media_type/producer_command — без изменений);
3. исправлена ровно одна запись на каталог — `case_record.json` (18+18+19+18 = 73); прочие записи уже совпадали;
4. campaign-level erratum-событие `experiments/evidence/E0/<campaign>/events/0001-erratum-f1-manifest-digests.json` (4 шт., по одному на кампанию; schema-valid по `experiment-event.schema.v1.json`).

Post-repair byte-compare: **225/225 записей** (R1 55, R2 55, R3 59, R4 56) — 0 расхождений. CLI: R1 18/18 ok, R3+R4 37/37 ok; R2 — сохранённое задокументированное отклонение попытки (events несли stale campaign_id, см. REPAIR события и R2-erratum event) — к digest-ремонту отношения не имеет, поверхность superseded кампанией E0-R4.

## 4. Гарантии (что не затронуто)

- **Байты `case_record.json` не менялись** (git diff: изменены только `artifacts.manifest.json`, добавлены `*.v1-superseded.json` и campaign-события).
- События прогонов (0001/0002/0003), summary.md, evidence значения (observed/scientific_outcome) — без изменений; научные исходы не затронуты (подтверждено reviewer'ом: значения `schema_validation` всюду пусты).
- `subject_sha`/`producer_run_id`/`storage_location` записей манифестов не менялись.
- Старые события не редактировались; история не переписывалась; новых прогонов не было.

## 5. Отложенный фикс + задокументированные gap'ы (кандидаты NL2-003)

1. **emit_run порядок** (финальная запись `case_record.json` до построения манифеста): по инструкции dispatch код инструмента в этом ремонте не меняется (инструмент заморожен; новых прогонов нет). Фикс ОБЯЗАТЕЛЕН для любых будущих кампаний E0-tooling.
2. **Gap «валидаторы не сверяют digest-vs-blob»**: ни один валидатор (work_cli/experiment_cli/jsonschema-слой) не проверяет соответствие sha256 манифеста фактическим байтам — F1 существовал во всех 73 каталогах и не ловился POS001 (тот же класс «структура без семантики», что и S003). Кандидат NL2-003 **вместе с S003** (разделение технического/научного статусов).
3. R2-CLI-отклонение (stale campaign_id в events неудавшейся попытки) — сохранено как есть, поверхность superseded E0-R4.

## 6. Коммиты ремонта (ветка `work/nl2-001-contracts-e0-r1`, поверх 2cee872)

```text
0d9df16  experiment(E0): erratum F1 - corrected artifact manifests for E0-R1 (18 run dirs)
<после R2> fix(E0): correct R2 erratum event (byte-compare 55/55; CLI R2 - сохранённый дефект попытки)
<после R2> fix(E0): R2 erratum event summary restored to a single string
24dac2d  fix(E0): campaign erratum events use schema-valid fields (command, artifact_refs)
549c310  experiment(E0): erratum F1 - corrected artifact manifests for E0-R3 (19 run dirs)
d350f78  experiment(E0): erratum F1 - corrected artifact manifests for E0-R4 (18 run dirs)
(этот коммит)  docs(NL2-001): repair map F1 + erratum F2-F5 + evidence updates
(финальный)  work(NL2-001): F6 scope deviation documented, repair event
```

## 7. Next action

Независимый VERIFIER: проверить repair-поверхности (byte-equal superseded-оригиналы; пересчитанные дайджесты 225/225; неизменность case_record/событий/исходов) на exact HEAD; merge — Human Gate.
