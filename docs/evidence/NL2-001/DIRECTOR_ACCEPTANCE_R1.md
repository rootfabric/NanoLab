# Director Acceptance — NL2-001 «Implement contracts and E0»

Дата решения: 2026-09-09. Роль: DIRECTOR научной линии NL (fresh-сессия; контекст исполнителя/reviewer/verifier не переиспользовался — только Git-факты и вердиктные документы). Явная авторизация владельца на Director-приёмку и merge в main получена в миссии (Human Gate открыт).

## Решение

```text
NL2-001 = ACCEPTED            # WO-уровень (исполнительская приёмка): E0-инфраструктура и отрицательные контроли
frontier = NL2                # без изменений; stage NL2 = IN_PROGRESS
next_work_order = NL2-002 (READY)
experiment E0 = RUN           # execution fact: первая кампания E0-R4 исполнена и верифицирована
E0 campaign-level scientific_outcome = NOT_EVALUATED   # методическая приёмка E0 не закрыта (engine-coupled случаи — NL2-003+)
Claim ceiling этого WO: C0_SOFTWARE_ONLY — не превышен ни одним вердиктом
```

Принятие NL2-001 — **WO-уровня**: реализованы контрактный формат evidence (по урокам ремонта NL1-002 R2), пререгистрация E0 и исполнительно-верификационный контур E0 с отрицательными и геометрическими контролями. Это **не** научная валидация измерительного тракта в целом: campaign-level `NOT_EVALUATED`, engine-coupled случаи (топология/trajectory oxDNA) остаются открытыми до runtime; статус `E0 = RUN` — констатация исполненного execution fact (та же конвенция, что `E1 = RUN` после NL1-002), а не объявление научного исхода.

## Основание — вердиктная цепочка

1. **Implementation**: `work/nl2-001-contracts-e0-r1`, base `15a2c9b` (canonical main после NL1-002 acceptance correction), START `609d4a3` (push до substantive work), handoff-HEAD `24352f9` (EX-NL2-001-R1, passport HANDOFF_READY). Поставлено: `E0-PROTO-R1..R4` (пререгистрация 18 контрольных случаев ДО прогонов; tolerances 5e-7 units / 1e-12 geometry frozen с R1), контрактные манифесты-массивы с sha256/size/provenance, машинные события, кампания **E0-R4** (frozen subject `ce477aa`): 18/18 COMPLETED — **17 SUPPORTED + S003 NOT_SUPPORTED (preregistered gap-проба сохранена как результат)**; попытки R1/R2 (технические отказы runner) и R3 (erratum) сохранены в evidence с причинами, run ID не переиспользовались, ожидания не менялись. Ремонтная линия поверх проверенного reviewer'ом subject **`2cee872`** → repaired tip **`1d594f3`**.
2. **Independent REVIEWER = FIX_REQUIRED → RE-REVIEW PASS**: `review/nl2-001-contracts-e0-r1` — вердикт `FIX_REQUIRED` @ `2c3b485` (F1 MAJOR — erratum-дайджесты artifact-манифестов; F2 MODERATE — tier-2 атрибуция; F3–F5 MINOR — placeholder frozen_at, счётчики попыток, «Final HEAD» summary; F6 MINOR — недокументированное расширение allowed_paths; F7 OBSERVATION), затем **`RE_REVIEW_R1 = PASS`** @ **`a140b8e`**: F1–F6 закрыты проверяемо — 73/73 superseded-манифестов byte-equal каноническим @ `2cee872`, **225/225 digest-vs-blob (0 mismatch)**, хирургичность (ровно одна запись, только sha256/size), 0 изменений scientific-содержимого (`case_record`/события/фикстуры/tools байт-идентичны), схема-валидность erratum- и repair-событий. Не-блокирующие O1/O2/O3 задокументированы (см. ниже).
3. **Independent VERIFIER = PASS**: `verify/nl2-001-contracts-e0-r1` @ **`b395d10`** (verification ≠ review — воспроизведение на frozen инструменте, прогоны в disposable scratch): **6/6 контрольных E0-прогонов MATCH** published (NEG/UNIT/GEO/STATUS/POS, вкл. подделку 0.0978 и S003 gap); **225/225 digest-vs-blob** против блобов Git @ `1d594f3` (урок autocrlf учтён), 73/73 superseded byte-equal, 73/73 хирургичность; **S003 gap воспроизведён дважды** (runner-кейс + прямой CLI-проб: `RUN_COMPLETED` + `scientific_outcome=SUPPORTED` принимается `ok:true/exit 0`) и **F1-класс gap «валидаторы не сверяют digest-vs-blob»** воспроизведён tamper-пробой; jsonschema **447 файлов / 0 ошибок**; CLI: E0-R1 18/18, E0-R3 19/19, E0-R4 18/18 ok (R2 18× fail — задокументированный stale campaign_id дефект superseded-попытки, не регресс ремонта); пререгистрация monotone freeze→digests→start для всех 4 попыток, tolerances идентичны R1→R4; self-acceptance/E-статусы — нарушений нет. Рекомендация: PASS, путь к Director checkpoint открыт.
4. **Роли независимы**: implementer, reviewer, verifier — разные fresh-сессии (каждый вердикт фиксирует независимость); ACCEPTED до настоящего решения в пакете отсутствовал; merge — Human Gate (разрешён владельцем в этой миссии).

## Checkpoint-ветка и интеграция

`control/nl2-001-director-checkpoint-r1` от repaired tip `1d594f3`; влиты: `review/nl2-001-contracts-e0-r1` @ `a140b8e` и `verify/nl2-001-contracts-e0-r1` @ `b395d10` (merge-коммиты); свежий canonical main `51a479c` (дрейф 15a2c9b→51a479c: INFRA1-002 gates + hosted_ci flip) влит; конфликт только в `docs/work/SESSION_LOG.md` (два параллельных аппенда) — разрешён аддитивно, обе записи сохранены, хронология соблюдена. Коммитные инструменты (`config/**`, `scripts/**`, `.github/**`) на merged-дереве принадлежат main (corrections-aware `work_cli`, NC-линт); локальные прогоны на checkpoint-коммите: `work_cli validate EX-NL2-001-R1` ok=true exit 0, `check-consistency` ok=true exit 0.

## Findings — диспозиция

- F1–F6 (REVIEWER): **закрыты**, подтверждены независимо re-review и verifier. F7 (OBSERVATION): принят к сведению.
- Сохранённые gap'ы и observation'ы — **кандидаты NL2-003 (provenance/workflow hardening)**, фиксируются как результаты, не скрываются:
  1. **Gap S003** — разделение технического/научного статусов не enforced механически (воспроизведён дважды).
  2. **Gap digest-vs-blob** — валидаторы не сверяют sha256/size с фактическими байтами (воспроизведён tamper-пробой); именно поэтому F1 существовал во всех 73 каталогах и не ловился POS001.
  3. **emit_run порядок записи** (корень F1) — REPAIR_MAP_F1_R1 §5.1 фиксирует ОБЯЗАТЕЛЬНЫЙ фикс для будущих кампаний E0-tooling.
  4. O1 — 55 stale `storage_location` в R2-манифестах (сохранённый дефект superseded-попытки, дайджесты корректны); O2 — placeholder-timestamp `18:25:00Z` в repair-событии; O3 — campaign-формат `evidence-map.json` vs `evidence-map.schema.v1.json` (11 ошибок, пре-существующее); F3 — placeholder `frozen_at_utc` в protocol.json R2–R4 (erratum; хронологию авторитетно устанавливают коммиты).
- Превышений claim не обнаружено: `ACCEPTED` в пакете — только словарь механических вердиктов units-check и явное «не выставляется»; campaign `NOT_EVALUATED`; E1/`project/**` на work-ветке не тронуты (подтверждено verifier: tree-хэши `config`/`scripts`/`project` = base).

## Условия, с которыми принято

- Одна инструментальная среда (Windows / Python 3.11.8); независимое окружение — обязанность последующих WO.
- Engine-coupled случаи E0 (oxDNA-топология/trajectory) не покрыты этой кампанией — открыты до runtime (NL2-003); финальная методическая приёмка E0 возможна только после них.
- CLI-отклонение R2-поверхностей — документированный дефект неудавшейся попытки; R2 superseded кампанией E0-R4; очистка (вместе с O1) — NL2-003.
- Статус `E0 = RUN` в `project/state.json` выставлен настоящим checkpoint-коммитом (control-коммит Director, как и предусмотрено handoff-дисциплиной — implementer state.json не менял).

## Изменения состояния проекта (этот checkpoint-коммит)

- `project/state.json`: NL2-001 = ACCEPTED; `completed_tasks` += NL2-001; `next_work_order` = NL2-002; `task_status.NL2-002` = READY; `experiment_status.E0` = NOT_RUN → RUN; frontier NL2 и stage NL2 = IN_PROGRESS — без изменений.
- `config/control/harness/scheduler-policy.v1.json`: next_work_order → NL2-002, notes обновлены.
- `docs/work/WORK_QUEUE.md`: строка NL2-001 → ACCEPTED (сводка исхода), разрешён старт NL2-002.
- `docs/work/SESSION_LOG.md`: настоящая запись (добавлена в конце журнала).

## Следующее действие

`NL2-002` «Validate statistics and E1» (READY, scheduler priority): T2 confirm — 3 реплики по frozen `R_confirm = 3` из `E1-PROTO-R2` (distinct seeds), статистика повторов/чувствительности, затем **научная приёмка E1** (объявление статуса E1 по execution facts). Затем `NL2-003`: provenance/recovery + validator hardening (S003, digest-vs-blob, emit_run, O1–O3).
