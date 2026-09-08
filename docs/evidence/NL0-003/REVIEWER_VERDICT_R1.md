# NL0-003 — Fresh Reviewer Verdict R1

Роль: `REVIEWER` (независимый, fresh; не implementer, не byte-verifier). Дата: 2026-09-09.

## Reviewed subjects (exact)

```text
BASE_SHA         = 81e299f1924e50bcff1bc5c893bccd934ef2883d   (canonical main)
PR_HEAD          = 6e30aee73252c0cc88545cc675633448dd3aaee5   (ветка review/nl0-003-preregistration-r1, HEAD worktree)
SUBSTANTIVE_HEAD = 9404a422166cb07efd98443a5f208f078a4ab2c4   (tree b8b1bd992f15f9093ea4338255858e94d0bc06ad — перепроверено git rev-parse)
Work Order       = NL0-003 (issue #4), EX-NL0-003-R1, Risk HIGH, claim C0_SOFTWARE_ONLY
```

Объекты review: `docs/research/PREREGISTRATION_E1_R1.md` (E1-PROTO-R1), `docs/research/E2_SETUP_R1.md` (E2-SETUP-R1), execution evidence `docs/work/executions/EX-NL0-003-R1/**` (passport, events 0001–0005, summary), `docs/evidence/NL0-003/IMPLEMENTER_EVIDENCE.md`; основания: REFERENCE_SELECTION.md, INPUT_AVAILABILITY.md, SOURCES.md (S15/S16), DIRECTOR_ACCEPTANCE_R1 NL0-002, PROJECT_CONTROL/HARNESS_CONTROL/docs/control/*, docs/SCIENTIFIC_METHOD.md, project/state.json, risk-policy.v1.json.

## VERDICT: **PASS**

## Findings

### 1. MINOR — интерпретация upstream-полосы подана в рубрике «Что известно (REPORTED/OBSERVED)»

Место: `PREREGISTRATION_E1_R1.md` §6.1: «разброс между прогонами с разными seed **встроен** в смысл upstream-полосы ±0.15».

Обоснование: это утверждение о замысле авторов upstream-теста, не проверяемое из pinned файлов (в `quick_compare` и `quick_input` нет ни слова о калибровке полосы по seed'ам). По логике проекта это ASSUMED-интерпретация, а не REPORTED/OBSERVED факт, и она стоит под заголовком «Что известно (REPORTED/OBSERVED)». Влияния на критерий нет: T1 определён механически verbatim от oracle и от этой интерпретации не зависит; на design-решение «T1 = один прогон» ссылка на upstream-формат теста корректна независимо от неё. Неблокирующая неточность маркировки; рекомендуется в E1-PROTO-R2 перенести формулировку в ASSUMED.

### 2. MINOR — расходится обозначение SUBSTANTIVE_HEAD между IMPLEMENTER_EVIDENCE и terminal event

Место: `IMPLEMENTER_EVIDENCE.md` «Exact subjects»: `SUBSTANTIVE_HEAD = 34508669…` (tree a18762b9…); событие `0005-handoff-completed` и `branch-passport.md`: substantive HEAD = `9404a422166cb07efd98443a5f208f078a4ab2c4` (tree b8b1bd9…).

Обоснование: следствие самоссылочности — evidence-файл коммитится вместе с 9404a42 и физически не мог знать SHA собственного коммита; 34508669 корректен как head на момент валидации (event 0004). Авторитетное разрешение дано явно (summary.md «Binding» + event 0005), поэтому противоречия по существу нет, но в evidence-файле заголовок `SUBSTANTIVE_HEAD` без этой оговорки вводит в заблуждение при чтении файла изолированно. Рекомендация на будущее: в подобных self-referential случаях использовать формулировку «VALIDATION_HEAD» либо дополнять post-commit note. Неблокирующее.

## Оценка по фокусам review

1. **Критерии E1 до кампании / защита от post-hoc.** Значение и полоса — verbatim из upstream `quick_compare` (мной выборочно проверено через GitHub API: содержимое pinned файла = `ColumnAverage::energy.dat::2::-1.37970256144::0.15`, цитата точна), т.е. существуют до любых прогонов NanoLab и не выбраны Implementer'ом. §0/§5.3/§10: изменение любого элемента критерия — только новая ревизия `E1-PROTO-R2` с superseding event; пост-hoc исключения запрещены; failed runs сохраняются. Механизм соответствует EXPERIMENT_HARNESS_RU («Изменение protocol/code») и правилу «DO NOT CHANGE ACCEPTANCE CRITERIA AFTER SEEING RESULTS WITHOUT A NEW PROTOCOL REVISION».
2. **REPORTED / OBSERVED / ASSUMED / UNKNOWN.** Разделение последовательно: defaults engine (interaction_type/salt/thermostat delta/seed) — UNKNOWN до pinning (§2.4, §11); семантика колонки 2 — явно ASSUMED с процедурой подтверждения header'ом первого прогона (§5.1) и корректной реакцией на противоречие (INCONCLUSIVE, не тихая смена критерия); units — ASSUMED/to-confirm. Единственная неточность маркировки — finding 1. Выдачи ASSUMED за факт, влияющего на критерий или исход, не найдено.
3. **Пилот-дисциплина R_confirm.** §6.4 корректен: ровно 3 PILOT-прогона, помечены PILOT, в evidence кампании не засчитываются (соответствует SCIENTIFIC_METHOD: «данные пилота не превращаются незаметно в независимую итоговую проверку»); `R_confirm ≥ 2` фиксируется в новой ревизии до confirmatory кампании; после старта — не уменьшается (увеличение консервативно и допустимо); полоса не меняется никогда без superseding. Пилот не назначает чисел в R1 — требование issue #4 выполнено.
4. **Семантика исходов.** §9 различает Reproduction→SUPPORTED, NOT_SUPPORTED (негативный результат сохраняется, повтор «до успеха» запрещён), FAILED_TECHNICAL (новый run — только с новым ID и причиной, в науку не идёт; соответствует запрету re-use run ID), BLOCKED_ENVIRONMENT, INCONCLUSIVE с явным отличием от NOT_SUPPORTED. Пути тихого ретрая до успеха нет. Exit code 0 ≠ научный PASS — заявлено.
5. **E2-постановка.** Decision rule 298K-vs-300K научен и симметричен требованиям: reproduction arm = авторские inputs verbatim (300K), расхождение с статьёй документируется в каждом отчёте рядом с результатом (не замалчивается — прямое выполнение требования REFERENCE_SELECTION), paper-fidelity arm 298K — только отдельная preregistered ревизия, T-чувствительность — отдельная arm. Определение угла не выдумано: только требования к фиксации из спиненного SI, reconstruct ≠ original, ANGLE_UNDEFINED — отдельный класс (соответствует SCIENTIFIC_METHOD «Наблюдения и статистика»). Права REFERENCE_ONLY не нарушены: файлы E2 не скачивались, только принятые blob/tree-факты NL0-001/002; hard-зависимости (owner decision, NL2, NL1-001) названы структурными. Целевой угол, tolerance, число повторов, ресурсная оценка — не назначены, процедуры freeze зафиксированы.
6. **Согласованность с принятыми фактами и SCIENTIFIC_METHOD.** Разделение статистической ошибки / физической флуктуации / модельных ограничений — §6.3 E1 и §8 E2 (три уровня раздельно). Правила угла, запрет коррелированные кадры считать независимыми, ANGLE_UNDEFINED, подготовка/production-разделение (S03) — отражены. Неоправданных условий сильного вывода не вводится; напротив, claim ceiling E1 = C1, C0 для самого WO, физическая валидность oxDNA — вне scope.
7. **Scope.** `git diff --name-only 81e299f..6e30aee` = 14 файлов, все внутри allowed_paths паспорта (WO, PREREGISTRATION, E2_SETUP, SOURCES, SESSION_LOG, executions/**, evidence/NL0-003/**). `project/state.json`, `project/plan.json`, policies, схемы — не тронуты. Terminal binding перепроверен: 9404a42 → tree b8b1bd99…, совпадает с event 0005 и branch-passport.
8. **Превышение claims.** Нигде не утверждается, что E1/E2 выполнены или что что-то доказано: «PREREGISTERED, НЕ ВЫПОЛНЕН», `E1/E2 = NOT_RUN`, `physics_runs = 0`, ACCEPTED не выставлен, «завершённый протокол не является выполненным E1» повторено в обоих документах и summary.

## Ограничение

Я не выполнял byte-верификацию SHA-256 всех входов, дословность расшифровки `quick_input` по всем строкам и полный аудит Git-объектов — это зона независимого VERIFIER. Выборочная проверка oracle `quick_compare` через GitHub API выполнена только как проверка design-корректности критерия T1. Шаг и точность (dt=0.005, полоса 0.15, steps=1e6) — verbatim из upstream, не выдуманы (подтверждается выборочной проверкой oracle и принятыми фактами NL0-001).

```text
REVIEWER_VERDICT = PASS (2 MINOR findings, BLOCKING = 0)
CLAIM_CEILING    = без изменений: C0_SOFTWARE_ONLY для WO; будущая кампания E1 ≤ C1_COMPUTATIONAL_REPRODUCTION
NEXT_ACTOR       = VERIFIER (HIGH routing), затем Director
```
