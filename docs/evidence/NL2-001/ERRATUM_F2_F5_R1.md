# NL2-001 — ERRATUM F2–F5 (один документ; + фиксация F6/F7)

Основание: `REVIEWER_VERDICT.md` @ `review/nl2-001-contracts-e0-r1` `2c3b485f5cd993f75336d966285958b25e97e08c` (FIX_REQUIRED; F1 — см. [REPAIR_MAP_F1_R1](REPAIR_MAP_F1_R1.md)). Ремонтируемый subject: `2cee872179bbcccff93c1b9458c6b25ea491a999`. Научные исходы E0-R4 (17 SUPPORTED + S003 NOT_SUPPORTED; campaign-level NOT_EVALUATED) не меняются.

## F2 (MODERATE) — атрибуция tier-2 U001

**Было (неверно):** `evidence-map.json` и `IMPLEMENTER_EVIDENCE.md` приписывали R4-U001 «конверсия найдена в pinned-исходниках `src/Utilities/Utils.cpp:333`».

**Факт:** собственный tier-2 артефакт R4 — `experiments/evidence/E0/E0-R4/runs/E0-R4-U001/artifacts/pinned_source_excerpt.txt` — `NOT_OBTAINED`: `TimeoutExpired` после 300 с на `git fetch` pinned-коммита (разрешено §11.4 E0-PROTO-R1 как негейтящая INCONCLUSIVE-заметка). Hit `src/Utilities/Utils.cpp:333` («Converting temperature from Celsius … to simulation units») получен в попытке **R3**: `experiments/evidence/E0/E0-R3/runs/E0-R3-U001/artifacts/pinned_source_excerpt.txt`. Tier-1 (ACCEPTED, полоса 5e-7, reference 0.097717) от tier-2 не зависит — исход U001 корректен в обеих попытках. Оба документа исправлены этим ремонтом; атрибуция: hit — R3-U001; R4 — NOT_OBTAINED.

## F3 (MINOR) — `frozen_at_utc` R2/R3/R4 — placeholder'ы

В protocol.json R2/R3/R4 значения `frozen_at_utc` (14:25:00Z / 15:35:00Z / 17:05:00Z) — круглые числа, не согласующиеся с git-хронологией prereg-коммитов (13:34:22Z / 13:40:40Z / 13:52:47Z). Хронология freeze→run подтверждается цепочкой коммитов и машинными `finished_at_utc` в `case_record.json` (использовано reviewer'ом). Поле дефектно как метаданные; в дальнейшем — только машинная генерация (как все timestamps событий).

## F4 (MINOR) — счётчики попыток в evidence-map

Исправлено в `evidence-map.json` (`failed_prior_attempts_preserved`):

- E0-R2: **17× RUN_FAILED_TECHNICAL + POS001 RUN_COMPLETED/NOT_SUPPORTED** (артефакт отказа; было «runs: 18, FAILED_TECHNICAL»);
- E0-R3: **19 каталогов** — 18 случаев + авторизованный `E0-R3-S003-RETRY1` (было «runs: 18»).

## F5 (MINOR) — «Final HEAD» в summary.md

`EX-NL2-001-R1/summary.md` указывает Final HEAD `24352f9dcc54e77472bdb8db827d2dc1fd0e1a1e` — HEAD на момент написания summary. Фактическая терминальная линия ветки: `24352f9` → `9c0f7ec` (evidence map + implementer evidence) → `edd0ddc` (EX-события 0002–0004 + summary) → **`2cee872`** (R3-поверхности; HEAD, проверенный reviewer'ом). События 0002–0004 несут `subject_sha=24352f9` (HEAD на момент их записи). Run-поверхности R4 после `24352f9` не менялись (проверено). Per verdict — достаточно erratum-заметки; `summary.md` не переписывается (corrections — новым документом); фактический HEAD фиксируется repair-событием и данным документом.

## F6 (MINOR, scope) — процедурное отклонение, зафиксировано

`docs/research/PREREGISTRATION_E0_R2/R3/R4.md` формально находились вне `allowed_paths` паспорта (паспорт разрешал только `PREREGISTRATION_E0_R1.md`), хотя superseding-документы требовались протоколом (§0.1 — новая версия пререгистрации при пересмотре). Исправление: `allowed_paths` паспорта дополнены тремя путями (этим repair-коммитом); отклонение зафиксировано в branch-passport («Documented deviations») и в repair-событии `events/0001-repair-f1-f7.json`.

## F7 (OBSERVATION) — принято к сведению, без правок

(a) R3-поверхности исполнения опубликованы терминальным коммитом `2cee872` (исполнены в 13:41–13:47Z по машинным timestamps) — впредь поверхности попытки публикуются до терминала; (b) `cf9365a` переименовал 18 уже опубликованных R1-событий (добавление `.json`; содержание событий не менялось, изменение задокументировано в коммите). На выводы не влияет.

## Связи

[REPAIR_MAP_F1_R1](REPAIR_MAP_F1_R1.md) · [REVIEWER_VERDICT](https://github.com/rootfabric/NanoLab/blob/review/nl2-001-contracts-e0-r1/docs/evidence/NL2-001/REVIEWER_VERDICT.md) (`2c3b485`) · [events/0001-repair-f1-f7.json](events/0001-repair-f1-f7.json) · [IMPLEMENTER_EVIDENCE](IMPLEMENTER_EVIDENCE.md) · `experiments/evidence/E0/E0-R*/evidence-map.json`
