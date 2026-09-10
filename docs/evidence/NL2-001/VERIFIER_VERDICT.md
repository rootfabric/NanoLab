# NL2-001 — VERIFIER VERDICT (независимая верификация исполнением)

**Вердикт: `PASS`** — все поверхности чек-листа §1–§5 [RE_REVIEW_R1.md](https://github.com/rootfabric/NanoLab/blob/review/nl2-001-contracts-e0-r1/docs/evidence/NL2-001/RE_REVIEW_R1.md) воспроизведены независимо; научное содержание и заявленные repair-гарантии подтверждаются. Блокирующих находок нет. Merge — Human Gate; campaign-level scientific_outcome остаётся `NOT_EVALUATED`; claim ceiling `C0_SOFTWARE_ONLY`.

- **Проверяемый subject:** `work/nl2-001-contracts-e0-r1` @ `1d594f3cd6f7673307310f53393cb5680deb7696` (base `15a2c9b`; repair-линия поверх проверенного reviewer'ом `2cee872`; review `FIX_REQUIRED` @ `2c3b485`, RE-REVIEW `PASS` @ `a140b8e`).
- **Метод: verification ≠ review — воспроизведение.** Отдельный worktree `verify/nl2-001-contracts-e0-r1`; замороженный инструмент (бит-в-бит base); все контрольные прогоны — ТОЛЬКО в disposable scratch (`C:\NanoLab\scratch\verify-nl2-001\`), published-поверхности не изменялись; собственные скрипты (digest-vs-blob, schema, prereg) — в scratch. Окружение совпадает с environment_binding протокола: Python 3.11.8, jsonschema 4.22.0, git 2.53.0.windows.1. Подробный журнал — [VERIFIER_PROGRESS_R2](VERIFIER_PROGRESS_R2.md).

## 1. Ancestry / scope / instrument freeze — ПОДТВЕРЖДЕНО

- `15a2c9b` — предок `1d594f3` (`merge-base --is-ancestor` → exit 0).
- Diff base→HEAD: 815 файлов — **только** `experiments/evidence/**` (797), `docs/work/**` (9), `docs/evidence/NL2-001/**` (4), `docs/research/**` (4), `docs/experiments/E0_PIPELINE_VALIDATION.md` (1, статусная строка — разрешено WO). Вне evidence-поверхностей — 0 файлов.
- Инструмент бит-в-бит base: tree-хэши `config`, `scripts`, `.github`, `project` идентичны base↔`1d594f3`; `project/state.json`/`plan.json` не тронуты.

## 2. Контрольные прогоны E0 (6 кейсов, 5 семей, замороженным runner'ом) — 6/6 MATCH

Runner `E0-R1/tools/e0_runner.py` (frozen), subject `ce477aad1e4a125c9e881fd9f6a741ec6d2fa876`, протокол/дайджесты E0-R4; фикстуры материализованы из git-блобов subject — дайджест-контроль пройден. Сверка с published `case_record` собственным скриптом (outcome + frozen expected + observed-ядро):

| Кейс | Семья | Моё воспроизведение | Published | |
|---|---|---|---|---|
| E0-R4-U002 | UNIT | 4/4 REJECTED, вкл. подделку **0.0978** | все REJECTED | MATCH |
| E0-R4-N006 | NEG | битый provenance → exit 3, ok:false, errors непуст | то же | MATCH |
| E0-R4-G001 | GEO | √2 и 90° точно (atol 1e-12) | то же | MATCH |
| E0-R4-S003 | STATUS | exit 0, ok:true → **NOT_SUPPORTED (gap)** | NOT_SUPPORTED | MATCH |
| E0-R4-U001 | UNIT | 0.097717 ACCEPTED, delta=0, полоса 5e-7 (tier-2 пропущен: сетевой, негейтящий §11.4) | ACCEPTED | MATCH |
| E0-R4-POS001 | POS | 19/19 checks чисты | 19/19 | MATCH |

Итог кампании подтверждается: **17 SUPPORTED + S003 NOT_SUPPORTED (gap сохранён), campaign-level NOT_EVALUATED**.

## 3. Digest-vs-blob всех 4 кампаний + repair F1 — ПОДТВЕРЖДЕНО

Собственный скрипт против **блобов Git @ `1d594f3`** (не рабочей копии — урок: autocrlf даёт ложные mismatch, зафиксирован в progress V3):

- **225/225 записей** (R1 55, R2 55, R3 59, R4 56): sha256+size каждой записи = фактические блобы `artifacts/*`. **0 mismatches.**
- **73/73** `artifacts.manifest.v1-superseded.json` **byte-equal** каноническим манифестам @ `2cee872` (blob-compare).
- **73/73** хирургичность: ровно одна изменённая запись (`case_record.json`), ровно поля sha256/size_bytes.
- Хирургичность ветки: diff `2cee872→1d594f3` = 77 M (73 манифеста + 4 документа) + 80 A (73 superseded + 4 erratum-события + repair-событие + 2 repair-дока); `case_record`/события прогонов/summary/фикстуры/tools/protocol не тронуты.
- F2-атрибуция подтверждена артефактами (R4-U001 `NOT_OBTAINED`/TimeoutExpired; hit `Utils.cpp:333` — артефакт R3-U001); F4-счётчики верны.

## 4. Gap S003 — ВОСПРОИЗВЕДЁН (двойно)

1. Runner-кейс S003: exit 0, `ok:true`, `separation_enforced=false` → NOT_SUPPORTED (MATCH с published).
2. Прямой CLI-проб без runner'а: фикстура из блобов `1d594f3` → `experiment_cli validate` → **ok:true, exit 0** при `RUN_COMPLETED` + `scientific_outcome="SUPPORTED"`.

Разделение технического/научного статусов не enforced механически — сохранённый gap подтверждён на `1d594f3` (кандидат NL2-003). Дополнительно воспроизведён **F1-класс gap «валидаторы не сверяют digest-vs-blob»**: подмена байта артефакта в scratch-копии — `ok:true`, exit 0 при sha256 ≠ манифесту.

## 5. Схемы и CLI — ПОДТВЕРЖДЕНО

- jsonschema Draft 2020-12 + FormatChecker по v1-схемам (`config/control/harness/**`, бит-в-бит base): **447 файлов, 0 ошибок** — все run-манифесты, все события всех run-каталогов 4 кампаний, все канонические + superseded artifacts-манифесты, 4 campaign erratum-события (subject = subject своей кампании), repair-событие (`work-event`-схема, subject `2cee872`), EX-события 0001–0004.
- CLI: `experiment_cli` — **R1 18/18 ok, R3 19/19 ok, R4 18/18 ok** (exit 0, ok:true, 0 warnings); **R2 18/18 fail** с текстом `«…campaign_id differs from manifest»` на 0002/0003 во всех 18 выходах — задокументированный дефект попытки (stale campaign_id, commit `f2fa411`), ремонт эти файлы не менял, **не регресс**. `work_cli validate EX-NL2-001-R1` → ok:true, HANDOFF_READY; `check-consistency` → ok, exit 0.

## 6. Пререгистрация — ПОДТВЕРЖДЕНА

- Freeze → digests → campaign start монотонно для всех 4 попыток (R1 13:25:27Z→13:26:01Z; R2 13:34:22Z→13:34:44Z; R3 13:40:40Z→13:40:49Z; R4 13:52:47Z→13:52:57Z); результаты — значительно позже. Ожидания frozen до любых прогонов.
- Tolerances/ожидания не менялись R1→R4: 18 кейсов protocol.json идентичны verbatim (модуль run-id префикса, кампания-само-ссылок и документированного placeholder `frozen_at_utc` — erratum F3); `units_reference`/`geometry_tolerance`/`outcome_semantics` идентичны; литералы 5e-7 и 1e-12 во всех ревизиях; `units_check.py ACCEPT_TOLERANCE=5e-7` — frozen.

## 7. Self-acceptance / E-статусы — НАРУШЕНИЙ НЕТ

`ACCEPTED` в документах — только словарь механических вердиктов units-check и явное «ACCEPTED не выставляется»; campaign `NOT_EVALUATED`; `next_action` — независимые REVIEWER→VERIFIER→Director, merge — Human Gate; E1/E2/`project/**` не тронуты; E0-док — только execution fact.

## Findings

**Блокирующих нет.** Подтверждены и остаются задокументированными (не-блокирующие, кандидаты NL2-003 вместе с S003 и digest-gap):

1. **Gap S003** — разделение технического/научного статусов не enforced (воспроизведён, §4).
2. **Gap digest-vs-blob** — валидаторы не сверяют sha256/size с байтами (воспроизведён tamper-пробой, §4); именно поэтому F1 существовал во всех 73 каталогах и не ловился POS001.
3. **emit_run порядок записи** (корень F1) не чинился по инструкции dispatch — зафиксировано REPAIR_MAP §5.1 как ОБЯЗАТЕЛЬНЫЙ фикс для будущих кампаний E0-tooling.
4. **O1** (55 stale `storage_location` в R2 — сохранённый дефект superseded-попытки), **O2** (placeholder-timestamp repair-события 18:25:00Z; рецидив F3-класса в одном поле), **O3** (campaign-формат evidence-map vs harness-схема, 11 ошибок) — воспроизведены дословно, соответствуют RE-REVIEW.
5. **F3** (placeholder `frozen_at_utc` в protocol.json R2–R4) — сохраняется как документированное erratum; хронологию авторитетно устанавливают коммиты (§6).

## Итог

Work Order NL2-001 «Implement contracts and E0» исполнен корректно и проверяемо: контракты соблюдены, E0 воспроизводим, отрицательные результаты и gap'ы сохранены, ремонт F1–F7 хирургичен и подтверждён независимым воспроизведением. **Рекомендация: PASS — путь к Director checkpoint открыт; merge в `main` — Human Gate.**

Next action (одно): Director checkpoint по NL2-001 (затем merge — Human Gate; NL2-003 — hardening: S003 + digest-vs-blob + emit_run + O1–O3).

*Верификация выполнена независимо (fresh-сессия, отдельный worktree `verify/nl2-001-contracts-e0-r1`, прогоны и скрипты — disposable scratch; published-поверхности не изменялись). Старые события не редактировались; VERIFIER_VERDICT публикуется новым документом.*
