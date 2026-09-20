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
integration/nl5-002-r1 @ 4c67e211f0db78c90366d32f643de92089ed190c   (PR #43 head; hosted CI run 35480129676 = success)
review/nl5-002-r1 @ be945f1dbdf97202bc50a91bd0e75744ba9c4fa6   (PASS)
verify/nl5-002-r1 @ 4116468ad570d59c35ff9349020495d4b455c00b   (PASS)
B-R2 terminal evidence: work/nl5-002-b-r2-external-run-r1 @ a8dfe8ce…, отчёт sha256 5aee7934…f421
verify/nl5-002-integration-r1 @ 776bb82fcde8072305ec1365d3bc5698f1f8c418   (tooling/integration PASS, см. Дополнение 2)
```

## Дополнение 2026-09-19 (после Human Gate-подготовки)

- hosted CI на PR #43: run 35478738272 (head 33935ae) = **failure** — Check 3 валидатора
  отвергал external-execution словарь EX-NL5-002-B-R1/B-R2 (finding FR-2 из FRESH_REVIEW_R1).
- Bounded machine-contract revision (schema + work_cli external execution profile,
  9 тестов, fresh review PASS) — commits 616ecea + 932481e, merge 4c67e21 в
  integration-ветку; повторный hosted CI run **35480129676 (head 4c67e21) = success**.
- Дельта — tooling-only; пять scientific веток и их вердикты не затронуты
  (subject-binding review/verify сохраняется). Disclose-комментарий в PR #43
  (issuecomment-5746556599). Merge остаётся Human Gate.

## Дополнение 2 — 2026-09-20: fresh tooling/integration Verifier PASS → PR #43 READY_FOR_HUMAN_GATE

Недостающий gate закрыт. Отдельная fresh Verifier-сессия (не implementer repair'а;
научный вердикт verify/nl5-002-r1 @ 4116468 не наследовался и не пересматривался)
выполнила верификацию exact final integration HEAD:

```text
VERIFY_VERDICT = PASS
VERIFIED_INTEGRATION_HEAD = 4c67e211f0db78c90366d32f643de92089ed190c (== origin/integration/nl5-002-r1; drift NONE)
VERIFIED_TREE             = 641c9cc71545b0bafda039ee0c37c437a638d117
HOSTED_CI                 = 35480129676 SUCCESS (5/5 checks)
UNIT_TESTS                = 369 tests OK
CHECK_CONSISTENCY         = PASS (ok=true, errors=[])
WORKFLOW_LINT             = PASS (blocking=0)
EXTERNAL_PROFILE_POSITIVE = PASS (42/42 EX-* valid; B-R1/B-R2 profile=external_execution,
                            детекция по содержимому events, path-исключений нет)
NEGATIVE_CONTROLS         = PASS (NC-EXT-1..5: 15/15 ожидаемых исходов; NC-STD: PASS)
STANDARD_PROFILE_REGRESSION = PASS (40/40 standard EX-* — вердикты идентичны старому валидатору @33935ae)
```

Evidence: `docs/evidence/NL5-002/FRESH_INTEGRATION_VERIFY_R1.md` на ветке
`verify/nl5-002-integration-r1` @ `776bb82` (опубликована в origin). Честные
оговорки верификатора зафиксированы в документе (§7): механически не детектируется
правка свободного текста `summary` в структурно валидном событии — этот класс
удерживает git-иммутабельность/append-only, не валидатор.

### Director pre-merge (mission §10) — все условия TRUE

```text
PR #43 HEAD == VERIFIED_INTEGRATION_HEAD (4c67e21)          = TRUE
hosted CI exact HEAD = SUCCESS (35480129676, 5/5)           = TRUE
scientific Reviewer PASS (be945f1)                          = TRUE
scientific Verifier PASS (4116468)                          = TRUE
tooling repair Reviewer PASS (commit-message + review, disclosure в PR) = TRUE
integration/tooling Verifier PASS (776bb82)                 = TRUE
no subject drift (все 7 subject-веток — предки 4c67e21; ancestry сверена Director 2026-09-20) = TRUE
```

**PR #43 = READY_FOR_HUMAN_GATE.**

### Disposition

Текущая owner mission НЕ содержит явного разрешения на merge этого evidence PR —
только «довести до Human Gate». Merge НЕ выполняется: **STOP = WAITING_HUMAN**.
Научный факт неизменен: WO-level **MISMATCH** (0b/32b), NL5-002 **NOT accepted**,
`external_reproductions = 0`, NL5 = IN_PROGRESS, NL6-001/E5 заблокирован.

Дополнительно к вопросам Human Gate подготовлен bounded HIGH scientific
Work Order-кандидат **`WO-NL5-002-E-R1` (PLATFORM-SENSITIVITY-R1)** —
`docs/work/WO-NL5-002-E-R1.md` в этой ветке: preregistration DRAFT (платформы
P1/P2[/P3], variants 0b/32b + controls 11b/53b, n=8–10 frozen seeds, paired
bootstrap-план, hypotheses H0/H1, outcomes PLATFORM_INSENSITIVE/PLATFORM_SENSITIVE/
INCONCLUSIVE). Freeze и dispatch — только по решению владельца; v0.1 envelope и
R1 MISMATCH не пересматриваются.
