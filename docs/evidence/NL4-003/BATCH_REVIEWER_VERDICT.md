# BATCH REVIEWER VERDICT — стадия NL4 (предфинальная проверка перед Director acceptance «NL4 = MVP COMPLETE»)

- **Executions (батч)**:
  - `EX-NL4-001-R1` (bounded agent + controller + baselines, mock; REVIEWER PASS `10d5cbe`, merge `3156b7c`)
  - `EX-NL4-002-E3-MECH-R1` + `EX-NL4-002-E3-LLM-R1` (E3 random/grid/LLM, равный бюджет 5×50k, target 90°; batch REVIEWER PASS `3fbc323`, merge `e3f7e5c`, comparison VALID)
  - `EX-NL4-002-E3-REVAL-R1` (winner re-validation: claimed 9.832 аннулирован, финальный 14.891; merge `96d1de6`)
  - `EX-NL4-003-R1` (MVP clean-room: fresh clone → unattended pipeline → 4 рана → verdict NOT_FOUND, revalidated 14.402; merge `a907bf2`)
- **Точка ревью**: worktree `C:\NanoLab\review-nl4-mvp`, ветка `review/nl4-mvp-batch-r1`, exact HEAD `a907bf213c7844fecd2a6f9e11f1f1b358fb487d` (= origin/main).
- **Дата**: 2026-09-14 (fresh REVIEWER-сессия).
- **Independence caveat**: REVIEWER работает в fresh-сессии, не участвовавшей ни в одном implementer-руке стадии; доверие — только файлам Git и воспроизводимым пересчётам (unittest, work_cli, check-consistency, независимый пересчёт median/score/gates из per-run analysis.json, пересчёт candidate-digest). Абсолютная достоверность машинных timestamps — по внутренним консистентным доказательствам (git author/commit times + event-файлы), не по внешнему аудиту часов.

## Таблица обязательных проверок (1–10)

| # | Проверка | Результат | Детали |
|---|----------|-----------|--------|
| 1 | Цепочка стадий | **PASS** | `project/state.json`: NL4-001 = ACCEPTED, NL4-002 = ACCEPTED, NL4-003 = READY (исполнен, HANDOFF_READY), stage NL4 = IN_PROGRESS; physics_runs 13 → 31 (+18 ранов E3: smoke 1 + random 5 + grid 5 + LLM 5 + reval 2 — согласуется с ledgers). `docs/work/WORK_QUEUE.md` и `SESSION_LOG.md` содержат записи Director acceptance NL4-001 (`fdbf74b`) и NL4-002 (`a135ba4`) + все execution-записи. Вердикты `10d5cbe` (merge `3156b7c`) и `3fbc323` (merge `e3f7e5c`) присутствуют в истории main; файл `docs/evidence/NL4-002/BATCH_REVIEWER_VERDICT.md` на месте |
| 2 | Тесты | **PASS** | `python -m unittest discover -s tests -t .` → **Ran 310 tests in 47.4s, OK (skipped=1)** — точно заявленные 310 (1 skip); 18 новых `test_nl4_mvp.py` в комплекте |
| 3 | MVP clean-room воспроизводимость механики | **PASS** | `mvp-report.json` содержит полный provenance: goal (90°/3/50000/1), run IDs E3-MVP-C001..C003 + REV001, input_digests (4), engine commit `00dc7fb9…`, pinned source commit (pro_CPU.in @ 23fd1ff, digest-gated), repo_commit `9e4d720…`, revalidation_seed 206024. Независимый пересчёт из per-run `analysis.json`: C001 78.322645→11.677355; C002 73.279586→16.720414; C003 67.309389→22.690611; REV001 75.598453→14.401547 — все совпадают с отчётом до 1e-6, гейты (lbf≤0.1078, pf_v2≥0.50, disp≤20) зелёные во всех 4 ранах (12/12 кадров валидны). `candidate_digest` пересчитан и совпадает для всех 4 ранов. Verdict-логика корректна: rule «FOUND iff … revalidated < published-best gap»; gap = |78.091846−90| = 11.908154; 14.401547 ≥ 11.908154 → NOT_FOUND, reason `REVALIDATED_SCORE_NOT_BELOW_PUBLISHED_BEST` — воспроизводится точно. Claim-формулировка «ближайший найденный в пространстве 0b/11b/32b/53b при бюджете 3×50000, revalidated score 14.402» — measured-only; limitations явно отрицают физическую валидность («no claim of physical manufacturability») |
| 4 | Изоляция E3 | **PASS** | `llm-decisions.json` (EX-NL4-002-E3-LLM-R1): 0 вхождений GRID/RANDOM/MECH; rationale каждой итерации выведим только из опубликованных E2-медиан + собственных наблюдений LLM-ранов. Батчевый вердикт `3fbc323` (comparison VALID, включая разбор изоляционного инцидента: решения зафиксированы ДО утечки через SESSION_LOG-хвост; детерминизм движка обнуляет возможную пользу) присутствует в `docs/evidence/NL4-002/BATCH_REVIEWER_VERDICT.md` |
| 5 | Анти-bias дисциплина | **PASS** | NL4-002: winner re-validation свежими seeds 204016/205020 (вне frozen-тройки), pooled median 75.109° → claimed 9.832 АННУЛИРОВАН, финальный заявляемый = 14.891 (revalidated, не best-of). NL4-003: REV001 свежий seed 206024 (вне тройки, в deviations.json зафиксирован), финальный claimed = 14.402 = revalidated. В обоих случаях финальный скор = re-validation score, не best-of |
| 6 | Стерильность | **PASS** | `git diff abd79ba..a907bf2 --name-only` — только `docs/work/executions/EX-NL4-003-R1/**`, `SESSION_LOG.md` (append), `scripts/nl4/mvp.py`, `tests/test_nl4_mvp.py`; `project/state.json` менялся только Director-коммитами приёмки (`fdbf74b`, `a135ba4`). Байтов источника (top/conf) в Git не добавлено (`git ls-files *.top/*.conf/*.dat` — только legacy E0/E1-артефакты, существовавшие до NL4). Durable-cache отсутствует (0 cache-файлов в tree; download-on-run по pinned digest, G1-решение соблюдено). U4: temp-исходники удалены (заявлено в summaries, подтверждено в обоих предшествующих ревью) |
| 7 | Валидаторы | **PASS** | `python -m harness.work_cli validate/close` → ok × 5 (EX-NL4-001-R1, E3-MECH, E3-LLM, E3-REVAL, EX-NL4-003-R1; все HANDOFF_READY, errors []). `PYTHONPATH=scripts python -m harness.cli check-consistency --root .` → ok: true, errors: [], frontier NL4, HEAD a907bf2 |
| 8 | MVP-границы | **PASS** | `scripts/nl4/mvp.py` (667 строк, чтение кода): нет сетевых вызовов (urllib/live-execution — только внутри `RealExecutorAdapter` в `real_executor.py`), нет LLM-вызовов (стратегия `mvp-informed-greedy-r1` — scripted `InformedGreedyAgent`, воспроизводящий план verbatim), нет физики вне адаптера (движок — только через `adapter.launch/wait/analyse_run`); `random` используется исключительно как `random.Random(frozen_seed)` для bootstrap CI. Informed-greedy детерминирован: сортировка published-медиан по \|median−target\| (tie-break по имени варианта) + frozen seed-тройка; published-медианы зашиты как DATA с ссылкой на источник |
| 9 | E3-честность | **PASS** | Аннулирование 9.83 подано как **ожидаемое срабатывание anti-bias гейта** (регрессия к среднему; предупреждение зафиксировано в batch-вердикте 3fbc323 ДО reval), не как провал кампании; Director acceptance NL4-002 фиксирует: claimed 9.832 АННУЛИРОВАН, финальный 14.891. Вывод «статистически значимого преимущества LLM-агента перед random не выявлено при данном бюджете и пространстве» сформулирован measured-only: оба best-of-числа явно помечены оптимистичными, family-typical скор 32b ≈ 12.4–13.4 по 6 наблюдениям; сравнение стратегий признано VALID |
| 10 | Готовность MVP | **PASS** | `mvp-report.json` + `mvp-report.md` содержат: reproduction instructions (command + exact clone commit 9e4d720 + goal_json), полный provenance (см. №3), limitations (5 пунктов: дискретное пространство 4 вариантов/74b BLOCKED, coarse-grained модель без manufacturability-claim, angle convention R1 erratum, бюджет 3×50k+1 reval, claimed = re-validation score), CI95 bootstrap (frozen seed 424242, метод E2_PROTO_R1 §6), verdict NOT_FOUND с явным rule и reasons. NOT_FOUND поддержан как исход и в отчёте, и в SESSION_LOG («нормальный исход», согласуется с разбросом 32b@50k из E3-REVAL: 74.59/75.31/75.60), и в WO-NL4-003 |

## Per-execution статусы

| Execution | Статус | Примечания |
|---|---|---|
| EX-NL4-001-R1 | **PASS** (предшествующий вердикт `10d5cbe` подтверждён в истории; validate/close ok сейчас) | bounded agent/controller/allowlist/baselines; mock-уровень, RealExecutorAdapter появился в NL4-002 |
| EX-NL4-002-E3-MECH-R1 | **PASS** (в составе batch `3fbc323`, comparison VALID) | random+grid 5+5 ранов, exit 0, пересчёт median из raw совпадал до 1e-9 |
| EX-NL4-002-E3-LLM-R1 | **PASS** (в составе batch `3fbc323`) | 5 итераций, изоляция решений подтверждена (0 ссылок на mech в decisions) |
| EX-NL4-002-E3-REVAL-R1 | **PASS** | 2 свежих seed, pooled 75.109° → 14.891 финальный; анти-bias гейт сработал штатно |
| EX-NL4-003-R1 | **PASS** | clean-room, 4 рана, все числа отчёта воспроизведены независимо из analysis.json; verdict NOT_FOUND корректен |

## Findings

Не блокирующие наблюдения (для протокола, не требуют исправления до acceptance):

- **F-B1 (minor, документационное)**: поле `input_digests` в mvp-report.json — это `candidate_digest` (sha256 канонического JSON кандидата variant/steps/seed), а не sha256 файла `input.in`; побайтовый sha256 input.in записан отдельно в artifacts-манифесте каждого `analysis.json`. Семантика консистентна во всём отчёте, но имя поля можно прочесть двусмысленно. Рекомендуется уточнить в будущей ревизии схемы (например, `candidate_digests`).
- **F-B2 (minor)**: `provenance.goal_file` указывает на host-путь `C:\NanoLab\mvp-goal.json`; воспроизводимость не страдает, т.к. полный `goal_json` встроен в блок `reproduction`.
- **F-B3 (observation)**: первый clean-room launch упал с ModuleNotFoundError до старта движка; фикс `9e4d720` + повтор из обновлённого clone раскрыт в SESSION_LOG — легитимно (движок не запускался, бюджет не списан), чистый финальный прогон шёл от `9e4d720` (= repo_commit в provenance).

Блокирующих findings нет.

## Вердикт

**PASS.**

Рекомендация Director'у: **NL4 acceptance = MVP COMPLETE готов (PASS)** — при условии стандартного Human Gate merge ветки `work/nl4-003-mvp-r1` (уже в main как `a907bf2`) и публикации настоящего вердикта. Claim ceiling остаётся `C0_SOFTWARE_ONLY` (measured-only); заявленный результат стадии: работающий end-to-end MVP-конвейер (goal → bounded informed-greedy → real oxDNA runs → re-validation → канонический отчёт), честный итог поиска NOT_FOUND (revalidated 14.402 ≥ published-best gap 11.908) и честный итог E3 (значимое преимущество LLM не выявлено; claimed winner-score аннулирован anti-bias гейтом, финальный 14.891). Научные claim'ы не превышают evidence; отрицательные результаты сохранены и поданы как поддерживаемые исходы.
