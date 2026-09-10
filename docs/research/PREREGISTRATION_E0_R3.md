# E0-PROTO-R3 — Пререгистрация E0 (superseding R2 только в части идентичности кампании; третья попытка)

Идентификатор протокола: `E0-PROTO-R3`. Статус: **PREREGISTERED, НЕ ВЫПОЛНЕН**. Supersedes: `E0-PROTO-R2` **исключительно** в части идентичности кампании (campaign_id `E0-R3`, run ID `E0-R3-*`) и ремонта исполнительного инструмента. Все случаи, ожидания, критерии, tolerances и семантика исходов наследуются из `E0-PROTO-R1` дословно (машинный биндинг: [protocol.json](../experiments/evidence/E0/E0-R3/protocol.json), поле `supersedes`). Work Order: `NL2-001`. Исполнение: `EX-NL2-001-R1`. Дата фиксации: 2026-09-09.

## 1. Основание

Попытка `E0-R2` дала 17/18 `RUN_FAILED_TECHNICAL`: runner передавал в `git cat-file` кампания-относительные пути фикстур (exit 128 — материализация входов не удалась), а публикуемые события несли зашитый устаревший campaign_id (несогласованность с манифестами). NOT_SUPPORTED у POS в R2 — артефакт того же отказа (валидация директорий с несогласованными событиями), а не контрактный сигнал. Отказы сохранены в [E0-R2/runs](../experiments/evidence/E0/E0-R2/runs/) с причинами; ремонт: `87bf408` (полная параметризация контекста кампании в runner: campaign/experiment id, fixture-base, tools-dir), `f2fa411` (публикация R2-отказов). Run ID не переиспользуются → кампания `E0-R3`.

## 2. Что менялось / что НЕ менялось

Не менялось: 18 случаев; ожидания и критерии; tolerances (5e-7 / 1e-12); семантика исходов; single-execution; budget; stop conditions; запрет post-hoc исключений. Ни одного наблюдения случая не существует — ожидания не пересматривались.

Изменено: campaign_id/run ID → `E0-R3-*`; протокол → `E0-PROTO-R3`; runner полностью параметризован. Фикстуры/инструменты/схемы/валидаторы — те же замороженные поверхности (reuse по дайджестам; fixture-base = `experiments/evidence/E0/E0-R1`).

## 3. Правила версии

Как §0 `E0-PROTO-R1`. Subject = pre-execution коммит данной кампании (пререгистрация + protocol + campaign.md + input_digests; фикстуры/инструменты — замороженные поверхности R1 по дайджестам). Campaign-level scientific_outcome = `NOT_EVALUATED`; приёмка — независимый review + Director.

## 4. Связи

[E0-PROTO-R1](PREREGISTRATION_E0_R1.md) · [E0-PROTO-R2](PREREGISTRATION_E0_R2.md) · [protocol.json R3](../experiments/evidence/E0/E0-R3/protocol.json) · [WO-NL2-001](../work/WO-NL2-001.md).
