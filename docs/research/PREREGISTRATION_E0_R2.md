# E0-PROTO-R2 — Пререгистрация E0 (superseding R1 только в части идентичности кампании; повтор после технического отказа)

Идентификатор протокола: `E0-PROTO-R2`. Статус: **PREREGISTERED, НЕ ВЫПОЛНЕН**. Supersedes: `E0-PROTO-R1` **исключительно** в части идентичности кампании (campaign_id `E0-R2`, run ID `E0-R2-*`) и ремонта исполнительного инструмента. Все случаи, ожидания (expected), критерии, tolerances и семантика исходов наследуются из [E0-PROTO-R1](PREREGISTRATION_E0_R1.md) **дословно** (механическая замена идентификаторов, без правки содержания; машинный биндинг: [protocol.json](../experiments/evidence/E0/E0-R2/protocol.json), поле `supersedes`). Work Order: `NL2-001`. Исполнение: `EX-NL2-001-R1`. Дата фиксации: 2026-09-09.

## 1. Основание (почему R2)

Первая попытка исполнения `E0-R1` дала **18/18 `RUN_FAILED_TECHNICAL`**: emit-путь runner'а использовал неверный корень репозитория (`parents[2]` вместо `parents[3]`) и падал до записи какого-либо результата случая; научной оценки не производилось. Причина зафиксирована в каждом run-каталоге R1 ([experiments/evidence/E0/E0-R1/runs/](../experiments/evidence/E0/E0-R1/)), ремонт: коммиты `d05da27` (fix repo-root + параметризация поверхностей), `254d467` (публикация R1-отказов), `cf9365a` (фикс расширения analysis-событий). По hard rule «DO NOT REUSE A FAILED RUN ID» повтор выполняется под новыми run ID — кампания `E0-R2`. Это и есть «повтор с записанной причиной» из §8 E0-PROTO-R1, а не повтор «до успеха» научного результата: никакого научного результата в R1 не было.

## 2. Что менялось / что НЕ менялось

**Не менялось (наследуется 1:1):** перечень 18 случаев; ожидания и критерии каждого случая; tolerances (5e-7 units; 1e-12 geometry); семантика исходов; правило единственного исполнения; budget (CPU ≤ 120 c); stop conditions; запрет post-hoc исключений. Ожидания не были скорректированы ни по одному наблюдению (наблюдений не существует — R1 не сохранил ни одного результата случая).

**Изменено (только идентичность/инфраструктура):** campaign_id → `E0-R2`; run ID → `E0-R2-N001..POS001`; протокол → `E0-PROTO-R2`; runner — починен repo-root и параметризованы пути (protocol/digests/runs-dir); run-каталоги — `experiments/evidence/E0/E0-R2/runs/`.

## 3. Замороженные поверхности

- Фикстуры, инструменты (`tools/`), schemas и валидаторы — те же замороженные файлы кампании R1 (`experiments/evidence/E0/E0-R1/{fixtures,tools}/`), дайджесты всех поверхностей — в `input_digests.json` кампании R2 (сырые блобы subject-коммита R2). Дублирование файлов не требуется: reuse по дайджестам с provenance.
- Subject R2 = freeze-коммит кампании E0-R2 (protocol.json + campaign.md кампании R2; содержимое фикстур/инструментов бит-в-бит идентично R1, что подтверждают дайджесты).

## 4. Правила версии

Как §0 E0-PROTO-R1: изменения после просмотра результатов R2 — только новая версия протокола с superseding event. Campaign-level scientific_outcome = `NOT_EVALUATED`; приёмка E0 — независимые REVIEWER + VERIFIER и Director checkpoint.

## 5. Связи

[E0-PROTO-R1](PREREGISTRATION_E0_R1.md) · [protocol.json R2](../experiments/evidence/E0/E0-R2/protocol.json) · [campaign.md R2](../experiments/evidence/E0/E0-R2/campaign.md) · [WO-NL2-001](../work/WO-NL2-001.md).
