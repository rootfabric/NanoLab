# DIRECTOR_DECISION_R1 — NL5-002 terminal: MISMATCH (proposal to Human Gate)

Дата: 2026-09-19 (authoritative `date -u` при записи). Роль: DIRECTOR.
Статус: **PROPOSAL — не применён к canonical state; решение за владельцем (Human Gate).**

## Установленный факт (verified цепочкой A→B-R1→C→B-R2→C2 + Fresh Reviewer PASS + Fresh Verifier PASS)

Внешняя кампания NL5-002-B-R2 (nanolab-components 0.1.1, 12/12 валидных реплик,
все integrity gates PASS, packaged-анализ, независимо перепроверено из raw с
расхождением 0.00e+00) дала **WO-level вердикт `MISMATCH`** по frozen mapping
WO-NL5-002-A-R1:

```text
0b  = MISMATCH  (все 3 fresh median строго выше envelope [65.095434789, 67.236579608];
                 statistic 68.389781796)
11b = MATCH     (73.560609814 в [72.165683993, 74.533109426])
32b = MISMATCH  (все 3 строго ниже [77.4927314, 79.877463339]; statistic 75.180138343)
53b = MATCH     (132.41188514 в [131.049227687, 135.285186059])
74b = NOT_MEASURED / KNOWN_GAP (без значений)
```

Портability-repair v0.1.1 свою задачу выполнил (конвенция самодостаточна: frame0
oracle 4/4 EXACT; анализ исполняем вне авторской среды). MISMATCH — не portability
дефект пакета, а научный результат: измеренные распределения 0b/32b на платформе
исполнителя (Ubuntu 22.04 / gcc 11.4 / Xeon E5-2698 v3) вышли за узкие 3-репличные
авторские envelopes. Вероятный класс причины (гипотеза, не вердикт): хаотическая
platform/FP-чувствительность MD-траекторий при n=3 envelope.

## Решение Director (в границах миссии §12)

1. **MISMATCH сохраняется как terminal результат NL5-002.** Не repairить пороги,
   не повторять до MATCH, автоматический R3 не запускать.
2. **NL5 acceptance НЕ объявляется.** Критерий NL5 («release package воспроизведён
   вне авторской среды» по frozen rule) не выполнен; state transition §21
   (`NL5=ACCEPTED`, `external_reproductions=1`, frontier NL6) НЕ применяется.
   `NL6-001 / E5` не стартует (DO NOT START NL6 BEFORE NL5 ACCEPTANCE).
3. **Evidence chain публикуется** (integration/nl5-002-r1: A + B-R1 + C + B-R2 + C2
   + review + verify). Negative results durable.

## Что решает владелец (Human Gate)

| # | вопрос | варианты |
|---|---|---|
| 1 | merge integration в main | merge (рекомендуется: evidence publication, state не меняет) / hold |
| 2 | disposition NL5-002 в state | `WAITING_HUMAN` c terminal MISMATCH (эта ветка) / иная формулировка владельца |
| 3 | следующий научный шаг | (a) исследовательский WO **platform-sensitivity** (мульти-seed × мульти-platform распределения на 0b/32b; publish distributional addendum; возможная НОВАЯ protocol revision v0.2 envelope rule — отдельный preregistration, не tuning); (b) сначала optional bounded packaging repair v0.1.2 (pyc/RIGHTS-metadata findings FR-3/FR-4, вне науки); (c) иное решение владельца |
| 4 | NL6-001/E5 | остаётся заблокированным до NL5 acceptance (не меняется этой веткой) |

## Proposed canonical state sync (эта ветка; применяется только по решению владельца)

```text
task_status.NL5-002: READY -> WAITING_HUMAN (terminal MISMATCH, evidence verified)
open_decisions += NL5-002 disposition (platform-sensitivity WO? packaging v0.1.2? NL5 acceptance policy)
frontier / stage_status.NL5 (IN_PROGRESS) / next_work_order (NL5-002) / external_reproductions (0) — без изменений
WORK_QUEUE / ROADMAP / README / AGENT_START / SESSION_LOG — синхронизированы с фактом terminal MISMATCH
```

## Exact subjects

```text
integration/nl5-002-r1 @ 33935ae813ca476b758192b3252aa6316a2cd5ca (эта ветка от него)
review/nl5-002-r1 @ be945f1dbdf97202bc50a91bd0e75744ba9c4fa6   (PASS)
verify/nl5-002-r1 @ 4116468ad570d59c35ff9349020495d4b455c00b   (PASS)
B-R2 terminal evidence: work/nl5-002-b-r2-external-run-r1 @ a8dfe8ce…, отчёт sha256 5aee7934…f421
```
