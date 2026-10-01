# NL5-ACCEPTANCE-POLICY/REVIEWER_VERDICT — Fresh independent scientific review of EX-NL5-ACCEPTANCE-POLICY-R2 candidate package

```text
REVIEW_ID          = NL5-ACCEPTANCE-POLICY/REVIEWER_VERDICT
REVIEW_VERDICT     = FAIL
REVIEW_DATE        = 2026-09-30 (review executed 2026-09-30T15:43Z UTC)
REVIEWED_BRANCH    = control/nl5-acceptance-policy-r2
REVIEWED_HEAD      = 51ca09a23addf0563e488505b1845daf8c438326 (handoff)
SUBSTANTIVE_HEAD   = ee40984a9a6a08c4d3c6182b5ba400a365bf59e5
                   (tree 69ecb1bf495f063b7d80894c7481e69b8e36e327 — сверен git cat-file)
BASE               = 8205781def7179d6bdfa6eb7ab2a84d46776649c (= origin/main, свежий
                     `git fetch --all --prune`; branch-remote: отсутствует на origin до review)
CLAIM CEILING      = C0_SOFTWARE_ONLY — этот вердикт не создаёт научных утверждений,
                     не freeze'ит протокол и не поднимает claim; NL5-002 terminal
                     MISMATCH / NOT accepted остаётся каноническим
ROLE               = REVIEWER (fresh independent session; scientific/protocol review
                     пакета HG-B; implementation-сессия не наследовалась)
```

## 0. Заявление о независимости и метод

Я — свежая reviewer-сессия, не видевшая контекст имплементёра. Каждый факт ниже
проверен механически из git-объектов exact HEAD `51ca09a` в изолированном worktree
`review/nl5-acceptance-policy-r2` (user CONTROL, `core.autocrlf false`,
`core.safecrlf true`), либо независимо воспроизведён (тесты, seed-генерация,
статистический анализ на закоммиченных данных R1). Full diff `8205781..51ca09a`
прочитан целиком (15 файлов, +1031/−1). Ничего из брифа не принято на веру.

Verdict `FAIL` **scoped**: он относится к candidate-протоколу
`NANOLAB_REPRO_V0_2_DISTRIBUTIONAL` как к тексту, который **нельзя freeze'ить и
нельзя одобрять через HG-B как basis для freeze в текущей параметризации и
формулировках** (findings M-1..M-3). Честность пакета, scope-дисциплина,
machine-корректность, детерминизм tooling и неприкосновенность научных фактов —
проверены и **подтверждены** (разделы 2–4). Все дефекты исправимы бесплатно до
freeze — именно это и есть назначение данного review.

## 1. Предмет и binding-факты

Пакет: candidate-протокол `docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md`
(NANOLAB_REPRO_V0_2_DISTRIBUTIONAL, CANDIDATE / PRE-DATA / NOT FROZEN), HG-B
proposal `docs/control/NL5_ACCEPTANCE_PRINCIPLE_HG_B_PROPOSAL_R1.md`, WO
`docs/work/WO-NL5-ACCEPTANCE-POLICY-R2.md`, seed tooling
`scripts/nl5/repro_v02_seeds.py` + 13 тестов, pre-data seed record
(`record_sha256 5c95664485e00069379e962f44b3ba247f00030e02a7375a27d3b4ab441f5a9c`),
passport/events/summary, WORK_QUEUE sync. Binding (сверено):

```text
base 8205781def7179d6bdfa6eb7ab2a84d46776649c = origin/main   — VERIFIED
substantive ee40984a…, tree 69ecb1bf495f063b7d80894c7481e69b8e36e327 — VERIFIED
handoff 51ca09a (4 commits: 793459d → 3171564 → ee40984 → 51ca09a)   — VERIFIED
ветка НЕ существовала на origin до review (ls-remote пуст)            — VERIFIED
```

## 2. Таблица проверок

| # | Проверка | Результат | Факты |
|---|---|---|---|
| 1 | Binding SHA/trees | OK | см. §1; tree `69ecb1b…` совпадает с заявленным |
| 2 | Full diff прочитан | OK | 15 файлов; единственная модификация существующего — WORK_QUEUE NL5-002 строка, append-only (прежний текст сохранён байт-в-байт) |
| 3 | Тесты tooling | OK | `pytest tests/test_nl5_repro_v02_seeds.py -q` → **13 passed**; `pytest tests/ -q` → **387 passed** |
| 4 | Seed record | OK | регенерация через tool → **byte-identical** committed JSON, sha256 `5c956644…` совпал; независимая ре-деривация raw `hashlib` (вне tool) 3 значений (0b/0001, 53b/0010, bootstrap-32b) — совпадение; negative-control refusal срабатывает; fresh∩historical = ∅; 44/44 уникальны |
| 5 | Machine-проверки | OK | check-consistency `ok:true, errors=[]`; workflow_lint `blocking=0`; work_cli validate `ok:true, HANDOFF_READY`, события START→CONTINUATION→VALIDATION→HANDOFF schema-valid; паспорт без notes, `HANDOFF_READY` |
| 6 | Scope vs allowed_paths | OK | 15/15 изменённых файлов внутри allowed_paths паспорта (exact / `EX-…/**` / `scripts/nl5/**`) |
| 7 | Секреты / commits | OK | секрет-скан diff чист; 4/4 commits conventional (`control(nl5): …`); timestamps событий монотонны 14:56:00Z→15:05:37Z, согласованы с git-эпохой |
| 8 | Научные факты не тронуты | OK | `project/state.json` не в diff; NL5-002 terminal MISMATCH/NOT ACCEPTED, v0.1 envelope immutable, PLATFORM_INSENSITIVE FULLY VERIFIED, `external_reproductions = 0`, NL6-001 LOCKED — подтверждены в WO §1, summary §2, WORK_QUEUE (текст сохранён); candidate нигде не объявляет NL5 ACCEPTED (единственное упоминание — условное, HG-B proposal §2.5); `REPRODUCTION_RULE_V0_1.md` не изменён |
| 9 | Nothing frozen | OK | protocol `CANDIDATE / PRE-DATA / NOT FROZEN` (§статус); freeze chain §13 полна: HG-B → Director FREEZE record (protocol+seed record+analyzer pin+N+budget) → fresh Reviewer + fresh Verifier FROZEN → prerequisite R2 ACTIVE → legs; whole-tree literal search предписан (§7); обходных путей не найдено |
| 10 | Convention сохранена | OK (c m-1) | per-replica `median_deg`, packaged `analyze_hinge.py`, окна 0b=200k / 11b-32b-53b=150k соответствуют исполненной конвенции (B-R2 analysis `window_steps`; E-study `--window 200000/150000`); replacement/деградации конвенции нет |
| 11 | Виды reproducibility | OK | §2: technical/numerical/distributional/scientific-consistency раздельно; FAILED_TECHNICAL ≠ MISMATCH согласовано в §9/§10/§11, v0.1 rule («не превращается в scientific mismatch»), HG-B, WO |
| 12 | HG-B scope | OK | APPROVES/DOES NOT корректны: R2 activation = HG-A (отдельно), scientific runs не разрешены, NL5 merge = HG-C, платный compute запрещён, NL6-001 не открывается |
| 13 | δ=0.5 a priori | OK по замыслу (см. M-2, N-1) | margin объявлен конвенциональным (§4/§9, Appendix B); исторические shifts только в Appendix A как power/budget context; из observed чисел margin НЕ выведен; observed R1 \|d\| = 0.25s / 0.38s — внутри ±0.5s, признаков reverse-tuning нет; НО feasibility-арифметика Appendix A ошибочна → M-2 |
| 14 | Fresh seeds / exclusions | **DEFECT** | список 19 покрывает S001–S010 (сверены с PREREGISTRATION_FREEZE_R1 1:1), bootstrap 902107, reference, E3-reval, E1; НО пропущены 15 документированных confirmatory seeds NL5-002 B-R1/B-R2 → **M-1** |
| 15 | Decision rule механичен | **DEFECT** | противоречие controls, двусмысленная формулировка не-эквивалентности, незапиненный bootstrap-план, вырожденный s=0, REPRODUCED_WITH_DEVIATION без классов → **M-3** |
| 16 | Статистическая достижимость | **DEFECT** | TOST-ветвь недостижима при n=10, δ=0.5, budget §12 → **M-2** |

## 3. Научные findings

### M-1 (MAJOR) — Exclusion list непон относительно собственных заявлений «все известные R1 confirmatory seeds»

Протокол §7 и docstring tool'а утверждают полноту («все известные R1 confirmatory
seeds» / «every known R1 confirmatory seed»). Факт: в evidence-дереве задокументированы
и отсутствуют в списке из 19:

```text
B-R1 (EX-NL5-002-B-R1/evidence/frozen_seeds.json): 510101, 520202, 530303
B-R2 (EX-NL5-002-B-R2/evidence/seeds_frozen.json): 410273, 520931, 638257,
    741953, 852607, 963541, 174329, 285637, 396421, 507283, 618457, 729613
```

B-R1/B-R2 — confirmatory external-кампании NL5-002 (B-R2 дал terminal MISMATCH).
Собственная freeze-запись platform study (`PREREGISTRATION_FREEZE_R1.md`) фиксирует
«полное объединение 33 значений», включающее B-R1/B-R2 — т.е. сам репозиторий считает
их известными seed-наборами. Существенный дисбаланс: reference seeds авторской
кампании (201004/202008/203012) в списке ЕСТЬ, а seeds обеих внешних кампаний — НЕТ.

Митигации (зафиксировать честно): вероятность коллизии ≈ 44·15/2³¹ ≈ 3·10⁻⁷ —
пренебрежима; freeze-time whole-tree literal search (§7) поймает коллизию — литералы
B-R2 seeds присутствуют в дереве. Но (а) текстовое claim полноты — ложно и попало бы
в frozen текст; (б) автоматическая гарантия (generator refusal) эти значения не
покрывает; (в) тест `test_exclusion_list_contains_all_documented_r1_seeds`
само-референтен (сравнивает множество с его же hard-coded копией) и доказательства
полноты не даёт.

**Рекомендация (до freeze, бесплатно):** добавить 15 значений в
`HISTORICAL_SEEDS_V1`; переписать тест так, чтобы он собирал seeds из evidence-файлов
(seeds_frozen.json / frozen_seeds.json / PREREGISTRATION_FREEZE_R1) и сверял с
tool-списком; скорректировать формулировку «все известные» либо сделать её истинной.

### M-2 (MAJOR) — Equivalence-ветвь решения недостижима при заявленных n=10 и budget: кампания спроектирована давать INCONCLUSIVE

Независимый количественный анализ на закоммиченных per-seed данных platform study
(`EX-NL5-002-E-R1/evidence/paired/paired_platform_sensitivity.json`, n=10/платформа,
реальные P1/P2 medians; numpy MC, seed фиксирован; bootstrap CI90 10k resamples,
percentile; правило применено буквально):

```text
s_pooled(SD n−1):  0b = 1.557°, 32b = 1.878°  → margin ±0.5s = ±0.778° / ±0.939°
v0.2-правило на РЕАЛЬНЫХ данных R1:
  0b : d = −0.25s, CI90 half-width 1.13s (indep) / 0.78s (paired) → INCONCLUSIVE
  32b: d = +0.38s, CI90 half-width 0.88s (indep) / 0.84s (paired) → INCONCLUSIVE
MC, истинная платформенная эквивалентность (Δ = 0), σ = observed pooled SD, n=10:
  P(REPRODUCED) ≈ 0.000–0.003 на вариант (оба bootstrap-плана);
  WO-level (обе primaries) ≈ 0.000–0.001%; P(INCONCLUSIVE) ≈ 98.6–99.0%
MC, сдвиг уровня R1 (0.25s / 0.38s): REPRODUCED ≈ 0; INCONCLUSIVE 84–98%
Достижимость: CI90 half-width / margin при Δ=0: n=10 → ≈1.85; n=20 → ≈1.32;
  n=40 → ≈0.93 (т.е. equivalence достижима только с ~n≈40/ячейку — конфликт
  с frozen budget §12: ≤ 96 runs на 8 ячеек).
```

Ключевые точки: (а) даже собственная оценка Appendix A «CI90 ширины ~1.2·s» шире
полосы эквивалентности 2δ·s = 1.0·s — т.е. при Δ̂=0 TOST-условие
`CI ⊂ (−0.5s, +0.5s)` невыполнимо; реализованная ширина ещё больше (~1.6–1.9·s).
Утверждение «margin согласован с budget» арифметически противоречит самому себе.
(б) Это НЕ подбор margin под данные в сторону REPRODUCED или MISMATCH — наоборот:
observed R1 эффекты (|d| = 0.25s/0.38s) лежат глубоко внутри ±0.5s. Дефект — в
произведении margin × n × ширины CI, а не в положении δ. (в) Практическое следствие:
кампания из 80 confirmatory runs почти гарантированно вернёт INCONCLUSIVE — honest,
но нулевой информационный исход за полный бюджет; NL5 останется нерешённой, что
воспроизводит ситуацию v0.1 в новой форме. (г) Пилот-механизм Appendix A (последний
абзац, «переоценивается на пилоте E5-B-класса при необходимости (до freeze)») —
правильная идея, но он optional и опирается на неверную предпосылку о ширине CI —
поэтому недостаточен.

**Рекомендация (до freeze):** сделать power/feasibility-pilot ОБЯЗАТЕЛЬным шагом
freeze-цепочки с квантифицированным критерием прохождения (например: пилот должен
продемонстрировать CI90 half-width ≤ 0.5·s при плановом n и заявленном bootstrap-плане;
иначе — ревизия дизайна до freeze). Варианты ревизии (владельцу на выбор, HG-B
«APPROVED WITH CHANGES»): paired-difference статистика с явным учётом корреляции
(эмпирическая кросс-платформенная ρ на R1 данных всего 0.22–0.32 — одной парностью
дефицит не закрыть), увеличение n (конфликтует с budget §12 → требует явного
owner-решения о расширении бюджета либо сокращения вариантов), увеличение δ (тогда δ
перестаёт быть «конвенциональным 0.5» и требует независимого обоснования — это законно
только как явное owner-решение до freeze), либо честное признание в протоколе, что
дизайн рассчитан на INCONCLUSIVE-чувствительность и какие последствия этого для NL5.

### M-3 (MAJOR) — Decision rule не полностью механичен: противоречие по controls, двусмысленности и незапиненные детали анализа

Frozen rule обязан применяться механически; каждая из перечисленных дыр оставляет
аналитику post-hoc свободу ровно там, где она запрещена:

1. **Controls-противоречие (жёсткое).** §9 vocabulary: «REPRODUCED = обе primaries
   эквивалентны; **controls без gross failure**». §9 Controls: «gross control failure
   (|d| ≥ 1.0 на control) требует investigation-note, **но НЕ меняет verdict**». При
   контроле с |d| ≥ 1.0 vocabulary исключает REPRODUCED, но ни MISMATCH (требует
   primary), ни INCONCLUSIVE («ни эквивалентность, ни не-эквивалентность не показаны»
   — а primaries показаны) его тоже не покрывают → исход не определяется текстом.
   Выбрать, что именно означает «controls без gross failure» в vocabulary (условие
   REPRODUCED или орфографический остаток), должен owner ДО freeze.
2. **Формулировка не-эквивалентности двусмысленна.** «CI90(Δ_v) не накрывает
   −δ·s..+δ·s полностью снаружи (значимо вне полосы)»: восстанавливаемый intend —
   «CI целиком вне полосы», но буквальное прочтение («CI не накрывает полосу
   полностью») пересекается с equivalence-условием (CI внутри полосы тоже «не
   накрывает её полностью») без правила приоритета исходов. Для frozen mechanical
   rule недопустимо: переписать однозначно, напр. «CI90(Δ_v) целиком вне
   (−δ·s_v, +δ·s_v)», и явно задать порядок проверки исходов.
3. **Bootstrap-план запинен не полностью.** Зафиксированы seed (per variant) и 10 000
   resamples; НЕ зафиксированы: схема ресемплинга (paired по seed-парам vs независимая
   по платформам), RNG implementation, percentile-конвенция/интерполяция. На R1 данных
   один только выбор схемы меняет CI90 0b half-width с 1.13s до 0.78s (−45%) —
   достаточно для flip'а пограничных вердиктов. Прецедент в проекте есть: R1 passport
   пинул «bootstrap RNG implementation» пре-дата; v0.2 обязан повторить.
4. **Вырожденный s=0 не определён.** При (почти) детерминированных репликах margin → 0,
   d = Δ/0 не определён; R1 этот случай пинул в паспорте («within_v = 0 degenerate
   case»), v0.2 — нет.
5. **REPRODUCED_WITH_DEVIATION без пре-объявленных классов.** «задокументированные
   non-scientific deviations (build/tooling/environment)» — классификация отклонения
   как scientific/non-scientific отдана анаитику post-hoc. Пре-объявить закрытый
   перечень классов отклонений, допустимых для этого вердикта.

Что проверено и НЕ является дырой: N < N_min → INCONCLUSIVE (§8+§9 согласованы);
asymmetric cells (8 vs 10) — pooled SD(n−1) и Δ̂ определены; замена ≤20% только
FAILED_TECHNICAL с append-only attempt id — пре-объявлена; ≥3 подряд
FAILED_TECHNICAL → остановка ячейки — пре-объявлена; WO-агрегация
(одна primary MISMATCH → MISMATCH; одна primary INCONCLUSIVE при второй
REPRODUCED → INCONCLUSIVE) — полна и непротиворечива вне controls-кейса.

### MINOR findings

- **m-1 (окна/формулировка).** «0b = 200k, 11b/32b/53b = 150k шагов» соответствует
  исполненной analysis-конвенции (B-R2 `window_steps`, E-study `--window`), но
  NL5-002-A формулирует иначе: run 11b = 200000 шагов при общем analysis window
  t ≤ 150000. Candidate смешивает run-length и measurement window. На сравнимость
  observable не влияет (медиана по кадрам t ≤ 150k), но freeze-запись обязана запинить
  явно: run length И analysis window И frame counts по вариантам (0b: 50 кадров;
  32b: 37 — из B-R2/E артефактов).
- **m-2 (regeneration-обязательство не в протоколе).** «Seed record регенерируется при
  freeze и сверяется digest'ом» заявлено в summary.md, но в тексте протокола §13 стоит
  только «seed record (сгенерирован tools/nl5, digest)». Перенести в протокол как
  binding-шаг freeze (включая сравнение с `5c956644…` или явную замену anchor'а с
  перегенерацией).
- **m-3 (external leg gate).** §12 гейтит на R2 ACTIVE только author leg; то же
  требование для external leg есть в summary/WORK_QUEUE, но не в протоколе. Внести в
  §12/§13: ни одна нога не стартует до R2 ACTIVE + frozen protocol.
- **m-4 (self-referential тест).** См. M-1(в): тест полноты exclusion list сравнивает
  множество с его копией; заменить на чтение из evidence.

### NOTE (для владельца — ответы на ключевые методологические вопросы)

- **N-1: δ=0.5 подобран a priori, не под данные.** Формулировки §4/§9/Appendix B
  последовательно объявляют конвенцию (граница «medium effect»), historical shifts
  (0b +0.685°, 32b −1.207°) присутствуют ТОЛЬКО в Appendix A как power/budget
  контекст; нигде margin не выведен из наблюдённых чисел; observed |d| = 0.25s/0.38s
  лежат внутри ±0.5s (никакого «гарантированного MISMATCH» margin не создаёт).
  Запрет §10 «не подбирать δ после просмотра данных» присутствует. Проблема не в
  under/over-tuning, а в M-2: согласованность margin с n и бюджетом не
  продемонстрирована и по арифметике Appendix A не достигается.
- **N-2: paired seed-множество не скрывает platform-specific подбор.** Seeds
  детерминированы sha256-цепочкой от anchor (человеческий выбор исключён), refusal
  при коллизии тестируется, множества идентичны на обеих платформах (симметрия);
  эмпирическая кросс-платформенная корреляция per-seed medians на R1 данных
  ρ ≈ 0.22–0.32 — pairing статистически почти не помогает (см. M-2), но и смещения
  не создаёт.
- **N-3 (наблюдение для анализа).** Δ̂ v0.2 = разность маргинальных медиан — на R1
  данных знакопротивоположен R1 paired shift (0b: −0.388° vs +0.685°; 32b: +0.710° vs
  −1.207°). Оценка пре-пинута (это хорошо), но расхождение стоит задокументировать в
  аналитическом плане, чтобы знак Δ не интерпретировали как «платформа сменила
  направление эффекта».

## 4. Явные утверждения ревьюера

1. Binding-факты пакета (base/substantive/tree/handoff, состав коммитов, состав
   файлов) соответствуют заявленным; ветка до review на origin отсутствовала.
2. Ни один scientific факт канона не изменён: diff аддитивен; WORK_QUEUE — append к
   одной строке; `project/state.json`, `REPRODUCTION_RULE_V0_1.md`, NL5-002 evidence —
   не тронуты; NL5-002 остаётся terminal MISMATCH / NOT accepted; candidate не
   объявляет acceptance и не «чинит» MISMATCH; NL6-001 остаётся LOCKED.
3. Nothing frozen: protocol NOT FROZEN; freeze chain полна и в данной R1 не
   исполнялась; freeze до данных обеспечен структурой (HG-B → Director freeze → fresh
   review/verify FROZEN → data), обходных путей в тексте нет.
4. Tooling детерминирован и воспроизводим: 13/13 и 387/387 тестов зелёные; committed
   seed record воспроизводится байт-в-байт с тем же `record_sha256 5c956644…`;
   независимая (вне-tool) ре-деривация значений совпадает; refusal-путь работает.
5. Machine-инварианты зелёные: check-consistency ok:true; workflow_lint blocking=0;
   work_cli validate ok:true (HANDOFF_READY, схема событий/passport); scope diff
   15/15 внутри allowed_paths; секрет-скан чист; conventional commits соблюдены;
   timestamps машинно согласованы; паспорт без notes.
6. НЕСМОТРЯ на пункты 1–5, candidate-протокол в текущей редакции **не готов к
   freeze**: правило решения содержит внутреннее противоречие и двусмысленности
   (M-3), exclusion-claim ложен (M-1), а параметризация δ×n×budget делает
   успешный исход кампании практически недостижимым (M-2). Это устранимо бесплатно
   до freeze — что и требуется сделать до/при HG-B.

## 5. Независимые валидации, выполненные этой сессией

1. `git fetch --all --prune`; ls-remote проверка отсутствия ветки; rev-parse всех SHA;
   `git cat-file -p ee40984…` → tree `69ecb1b…`; полный `git diff 8205781..51ca09a`.
2. `PYTHONPATH=scripts python3 -m pytest tests/test_nl5_repro_v02_seeds.py -q` → 13 passed;
   `python3 -m pytest tests/ -q` → 387 passed.
3. Регенерация seed record tool'ом → byte-identical → sha256 `5c956644…` (совпадение);
   независимая ре-деривация raw hashlib трёх значений; brute-check fresh∩historical = ∅;
   negative-control refusal.
4. `CONTROL_DEVELOPMENT.sh --check-consistency` → ok:true; `workflow_lint` → blocking=0;
   `work_cli validate docs/work/executions/EX-NL5-ACCEPTANCE-POLICY-R2` → ok:true,
   HANDOFF_READY; паспорт/события сверены (schema через validator; timestamps; notes).
5. Scope-анализ diff vs passport allowed_paths (поубережно); секрет-скан; commit-формат.
6. Сверка exclusion list с `PREREGISTRATION_FREEZE_R1.md` (S001–S010 попарно) и с
   `EX-NL5-002-B-R1/evidence/frozen_seeds.json`, `EX-NL5-002-B-R2/evidence/seeds_frozen.json`
   (обнаружены 15 отсутствующих значений → M-1).
7. Сверка convention: `REPRODUCTION_RULE_V0_1.md`, `WO-NL5-002-C2-R1.md`,
   `WO-NL5-002-E-R1.md`, `WO-NL5-002-A-R1.md`, B-R2/E артефакты окон → m-1.
8. Статистический анализ (numpy, фиксированный seed, скрипт scratch, в review не
   закоммичен; числа выше воспроизводимы из указанных данных): применение правила v0.2
   к реальным paired-данным R1; MC 2000–3000 реплик на сценарий (Δ=0; сдвиг уровня R1);
   соотношения half-width/margin по n ∈ {10,20,30,40}; ρ по пер-seed парам; оба
   bootstrap-плана (independent/paired).

## 6. Вердикт

```text
REVIEW_VERDICT = FAIL
```

Обоснование в одну строку: пакет процессно и машинно чист, ничего не freeze'ит и
фактов не трогает (всё подтверждено), но candidate-протокол содержит ложный claim
полноты exclusion list (M-1), внутренне противоречивое и неполное mechanical decision
rule (M-3) и параметризацию, при которой собственный success-исход (REPRODUCED)
недостижим в рамках собственного бюджета (M-2), — freeze такого текста или одобрение
его владельцем как basis для freeze без правок недопустимы.

Обязательные правки до freeze (все — бесплатны сейчас): M-1 (+15 seeds, тест из
evidence, коррекция claim); M-2 (обязательный power-pilot с количественным критерием;
ревизия n/δ/статистики по выбору владельца); M-3 (устранить controls-противоречие;
однозначная формулировка не-эквивалентности + порядок исходов; пины bootstrap-плана;
s=0; классы отклонений для REPRODUCED_WITH_DEVIATION); желательно m-1..m-4.

ЭТО РЕВЬЮ: не создаёт научных утверждений; не freeze'ит и не размораживает протокол;
не меняет NL5-002 terminal MISMATCH / NOT accepted, v0.1 envelope,
PLATFORM-SENSITIVITY-R1, external_reproductions = 0, NL6-001 LOCKED; claim ceiling
рассматриваемого пакета остаётся C0_SOFTWARE_ONLY. FAIL относится к готовности
candidate-протокола к freeze, а не к честности исполнения WO: все заявленные
software/process-факты пакета подтверждены (§2, §4).

— Fresh independent Scientific Reviewer (CONTROL), 2026-09-30

---

## Review refresh R1 (candidate R2) @ 6e5287b

```text
REFRESH_ID        = NL5-ACCEPTANCE-POLICY/REVIEWER_VERDICT (refresh R1)
REFRESH_VERDICT   = PASS
REFRESH_DATE      = 2026-09-30 (executed 2026-09-30T16:16Z UTC)
REFRESHED_HEAD    = 6e5287bb3b831396908d0e431e06200f0e42006c
                    (repair commit поверх 51ca09a; один коммит; conventional;
                     f07fe39 — отдельная review-ветка, предком не является и не должен быть)
SCOPE OF CHANGE   = 7 файлов: candidate doc переписан в R2, tool (+15 seeds),
                    tests (+1 тест = 14), HG-B proposal (review cycle + gate в
                    freeze-механике), evidence repro-v0-2-seed-record-PRE_DATA_R2.json,
                    summary errata §5, event 0005 (CONTINUATION_CHECKPOINT,
                    post-terminal corrections class — work_cli принимает, ok:true)
PASS MEANING      = candidate R2 готов к вынесению на HG-B / freeze-цепочку с
                    позиций этого review; НЕ freeze и не научное утверждение;
                    claim ceiling по-прежнему C0_SOFTWARE_ONLY у пакета
```

### Таблица finding → fix → измерение → статус

| Finding | Fix в R2 | Независимое измерение этой сессии | Статус |
|---|---|---|---|
| **M-1** exclusion 19, ложный claim «все известные» | +15 B-R1/B-R2 seeds → 34; тест хардкодит 34 с per-source комментариями + `len==34` | Независимая экстракция seed'ов из evidence-файлов (B-R1 frozen_seeds.json: 3; B-R2 seeds_frozen.json: 12; PREREGISTRATION_FREEZE_R1 S001–S010: 10; reference 3; E3-reval 3; E1 2; bootstrap 1) → **34, EQUAL с tool-множеством, missing/extra = ∅**; seed-потоки НЕ изменились: регенерация byte-identical R2-записи, `record_sha256 5c956644…` == R1 == R2 (digest не покрывает exclusion — корректно); fresh∩historical = ∅ | **CLOSED** |
| **M-2** TOST недостижим при n=10; пилот optional; budget 96 | primary statistic = paired per-seed differences; bootstrap pinned (PAIRED, B=10 000, `random.Random(bootstrap_seed_v)`, quantile linear); N=40 primaries / N_min=32; budget 200+40=240; **MANDATORY FEASIBILITY GATE §12** (ratio ≤ 1.0 по обеим primaries до dispatch, FAIL → INFEASIBLE → owner, без подгонки) | (а) Структурно: MC pinned-статистики, n=10 → P(EQUIVALENT\|Δ=0) ≈ 3%/вариант; **n=40 → 22–44%/вариант (ρ=0–0.32), WO-level ≈ 5–19%** — недостижимость устранена, но успех не гарантирован. (б) Gate воспроизведён ПОСВОВНО (pinned RNG `random.Random(bootstrap_seed_v)`, B=10 000, subsample n=40) на committed R1 данных: **0b ratio 0.124 (PASS), 32b ratio 1.298 (FAIL > 1.0)**; numpy-репликация другим RNG даёт те же ratios (робастно). (в) Параметрическая оценка для реальных n=40 свежих пар: 0b ≈ 0.81, 32b ≈ 0.76 (borderline-feasible) — gate-оценка на 10-точечной эмпирической поддержке granularity-смещена в ОБЕ стороны (0b 0.124 — нереалистично оптимистична; 32b 1.298 — пессимистична) | **PARTIAL** — структурная невозможность устранена; gate добавлен, механичен и failsafe; НО по букве протокола на committed данных gate сейчас FAIL для 32b → ожидаемый исход freeze-цепочки: INFEASIBLE → owner (честный, но владелец должен видеть это ДО HG-B); см. риски R-1..R-3 |
| **M-3** rule не механичен (controls-противоречие; двусмысленность; незапиненный bootstrap; s=0; deviation-классы) | §9.2 приоритетная классификация (n<N_min → INCONCLUSIVE; CI⊂полоса → EQUIVALENT; elif CI целиком вне → NOT_EQUIVALENT; else INCONCLUSIVE); §9.3 WO-level с приоритетами, controls gross failure (≥1.0·s_eff(control)) → downgrade до REPRODUCED_WITH_DEVIATION, не MISMATCH; s_eff = max(s, 0.01°); §9.4 замкнутый список DEV-* , вне списка → STOP + новая revision | Перечитано целиком: приоритеты взаимоисключающие и полные (6 веток покрывают всё пространство); NOT_EQUIVALENT сформулирован точно; противоречие R1 устранено явно (текст §9.3 называет и снимает его); bootstrap-план запинен полностью и воспроизводимо (мой gate — прямая реализация текста); FAILED_TECHNICAL ≠ MISMATCH сохранён во всех поверхностях | **CLOSED** (остаток: NOTE R-4 — control-ячейка с n_valid < 8 не отображена в §9.3) |
| **m-1** окна смешивали run-length и window | §6: run lengths запинены как исполненная конвенция (0b=200k; 11b/32b/53b=150k), analysis window/gates — frozen convention без изменений | Сверено с B-R2 `window_steps` и E-study `--window` — соответствует исполненному; считаем закрывающим | **CLOSED** |
| **m-2** регенерация только в summary | §7 «Обязательство регенерации (часть протокола…)»: регенерация + сверка 34 exclusions + whole-tree literal search; несовпадение digest = freeze невозможен | Текст присутствует в протоколе; механика проверена регенерацией | **CLOSED** |
| **m-3** external leg не загейчен на R2 ACTIVE | §5 «ОБЕ ноги гейтятся на R2 ACTIVE до dispatch»; §12 stop conditions «ОБЕ ноги … HARD_BLOCKED» | Текст в двух местах; согласован с summary | **CLOSED** |
| **m-4** само-референциальный тест полноты | Тест хардкодит полные 34 значения с указанием источников + count-pin | Хардкод сверен с evidence-файлами независимо (EQUAL, см. M-1); runtime-чтение evidence было бы сильнее, но зафиксированный полный набор корректен на этом дереве | **CLOSED** |
| **NEW-1** (этот refresh) WORK_QUEUE staleness | — (в repair-коммите WORK_QUEUE.md НЕ менялся, хотя repair-брифф ожидал sync N=40/10) | Строка NL5-002 в WORK_QUEUE всё ещё описывает пакет как «N=10/ячейка» (текст R1-эпохи) — расходится с R2 (N=40 primaries / 10 controls, budget 240) | **NOT_CLOSED** (minor, канонический факт не искажает; исправить синком при следующем touch поверхности) |

### Регрессия и machine-проверки @ 6e5287b (все зелёные)

```text
pytest tests/ -q                 → 388 passed (387 + 1 новый doc-pin тест; seed-tool 14)
check-consistency                → ok:true, errors=[]
workflow_lint                    → blocking=0
work_cli validate EX-…-R2        → ok:true, HANDOFF_READY,
                                   has_post_terminal_corrections=true (event 0005 —
                                   валидный post-terminal corrections класс)
scope diff 51ca09a..6e5287b      → 7/7 файлов в allowed_paths паспорта
секрет-скан / conventional commit / timestamps → чисто; 0005 (15:52:42Z) > 0004
```

### Оставшиеся риски (не блокируют HG-B, должны быть видимы владельцу)

- **R-1 (главный).** По буквальному воспроизведению §12 gate на committed R1 данных
  **32b FAIL (ratio 1.298)** → freeze-цепочка по этому протоколу, скорее всего,
  завершится INFEASIBLE → owner, а не dispatch. Параметрическая оценка говорит, что
  реальные n=40 погранично проходимы (ratios ≈ 0.76–0.81) — т.е. это артефакт выбора
  gate-оценки, а не смерть дизайна. РЕКОМЕНДАЦИЯ: вычислить и опубликовать §12 gate
  evidence УЖЕ сейчас (все входы committed, вычисление pre-data) и приложить к HG-B,
  чтобы владелец одобрял принцип, зная текущий исход gate'а; при желании — owner-решение
  по параметрам (n, gate-оценка) до freeze.
- **R-2.** Gate-оценка на 10-точечной эмпирической поддержке granularity-смещена
  двунаправленно (0b: 0.124 против параметрических ~0.81; 32b: 1.298 против ~0.76).
  Запинить в freeze-записи точную реализацию и интерпретацию (или заменить на
  параметрическую + empirical-две оценки с обоими числами в evidence).
- **R-3.** Даже при идеальной эквивалентности платформ P(WO-level REPRODUCED) при
  n=40 ≈ 5–19% (ρ-зависимо; margin остаётся в шкале within-platform SD, а SD парных
  разностей ≈ 1.25–1.41·s при ρ≈0–0.3). Дизайн честный, но INCONCLUSIVE остаётся
  частым исходом; это осознанный tradeoff, теперь управляемый gate'ом.
- **R-4 (NOTE).** §9.3 не определяет исход при control-ячейке с n_valid < 8
  (gross-failure порог тогда считается на неустойчивой выборке). Направление ошибки
  консервативно (downgrade, не завышение); рекомендуется пре-пинуть (например:
  control n<N_min → трактовать как deviation-class note / REPRODUCED_WITH_DEVIATION).
- **R-5 (NEW-1).** WORK_QUEUE NL5-002 строка устарела (N=10/ячейка) — синхронизировать.

### Refresh-verdict

```text
REFRESH_VERDICT = PASS
```

Обоснование в одну строку: все три MAJOR и все четыре MINOR R1-ревизии закрыты
(измеримо; M-2 — структурно, с обязательным failsafe-гейтом) либо сведены к
задокументированным рискам с владельческим путём решения; новых дефектов
целостности не найдено; пакет честно остаётся PRE-DATA / NOT FROZEN и готов к
вынесению на HG-B с раскрытием R-1..R-5. Этот refresh не создаёт научных
утверждений, не freeze'ит протокол и не меняет NL5-002 terminal MISMATCH /
NOT accepted, v0.1 envelope, PLATFORM-SENSITIVITY-R1, external_reproductions = 0,
NL6-001 LOCKED.

— Fresh independent Scientific Reviewer (CONTROL), refresh R1, 2026-09-30

---

## Review refresh R2 @ a9d7d07

```text
REFRESH_ID        = NL5-ACCEPTANCE-POLICY/REVIEWER_VERDICT (refresh R2)
REFRESH_VERDICT   = PASS
REFRESH_DATE      = 2026-09-30 (executed 2026-09-30T16:29Z UTC)
REFRESHED_HEAD    = a9d7d07fa264e9907b67ca244b00ba2da3430b0f
                    (один repair-коммит поверх 6e5287b — линейная история; subject
                     sha event 0006 = c25bcd6, т.е. мой refresh R1 — корректный lineage)
SCOPE OF CHANGE   = 7 файлов: gate-скрипт (pinned), gate evidence JSON, протокол
                    §12 two-estimate + §9.2 control-оговорка, HG-B §4.1,
                    WORK_QUEUE sync, тесты +4, event 0006
```

### R-1..R-5 → фикс → измерение → статус

| Risk | Фикс @ a9d7d07 | Независимое измерение этой сессии | Статус |
|---|---|---|---|
| **R-1** gate на committed данных: 32b FAIL → INFEASIBLE→owner, число не видно владельцу до HG-B | §4.1 HG-B proposal: числа 0b 0.124/0.207, 32b 1.298/0.907 опубликованы; 32b = FEASIBILITY-UNCERTAIN как owner-решение ДО HG-B с тремя опциями (принять риск / R3 сузить primary до 0b / R3 расширить budget); пороги не трогаются | §4.1 присутствует, числа совпадают с моим MC и committed evidence; опции сформулированы как owner-решение, не имплементатора | **CLOSED** (INFEASIBLE-путь для 32b — теперь задокументированный owner-пункт, не дефект имплементации) |
| **R-2** gate-оценка granularity-смещена, реализация не запинена | `scripts/nl5/repro_v02_feasibility_gate.py` (pinned, 162 строки): DECISION = subsample n=40 (protocol letter), ADVISORY = √n-экстраполяция из полного n=10-bootstrap; §12 дополнен two-estimate схемой и вычисленными числами; evidence committed с `source_sha256` | source digest `2b0df07d…` совпадает с sha256 committed paired JSON; повторный прогон `evaluate_variant` **bit-exact** воспроизводит committed evidence JSON (все float-поля ≤1e-12, gate_pass-флаги совпадают); числа = мои независимые MC: 0b 0.124 PASS / 32b 1.298 FAIL / advisory √n 32b 0.907 | **CLOSED** |
| **R-3** P(успеха\|Δ=0) ≈ 5–19% — INCONCLUSIVE частый исход | Не «фиксится» кодом — осознанный tradeoff: теперь виден владельцу через §4.1 (числа + опции R3) и управляется failsafe-gate | Подтверждён моим MC (без изменений); protocol letter не искажён | **CLOSED** (как задокументированный tradeoff с владельческим путём; наука не подгонялась) |
| **R-4** control n_valid < 8 не отображён в §9.3 | §9.2: control n_valid < 8 → INCONCLUSIVE-CONTROLS, исключается из downgrade-логики §9.3; verdict определяется primaries | Текст в §9.2 в нужном приоритет-блоке; §9.3 когерентен (downgrade применяется только к оцениваемым controls) | **CLOSED** |
| **R-5 / NEW-1** WORK_QUEUE staleness (N=10/ячейка) | WORK_QUEUE строка NL5-002 → «N=40 primaries/10 controls» | Diff точечный: заменён только фрагмент параметров, весь остальной текст строки байт-в-байт сохранён (terminal MISMATCH/NOT ACCEPTED и вся цепочка гейтов нетронуты) | **CLOSED** |

### Регрессия и machine-проверки @ a9d7d07 (все зелёные)

```text
pytest tests/test_nl5_repro_v02_seeds.py -q → 18 passed (14 + 4 gate-теста:
  quantile_linear, pooled_sd known values, half-width shrinks with n,
  evaluate_variant gate fields — осмысленные unit-проверки машинерии)
pytest tests/ -q                            → 392 passed
check-consistency → ok:true; workflow_lint → blocking=0;
work_cli validate EX-…-R2 → ok:true, HANDOFF_READY
event 0006 = CONTINUATION_CHECKPOINT 16:25:00Z, subject_sha = c25bcd6 (мой refresh R1)
scope 6e5287b..a9d7d07 → 7/7 в allowed_paths; секрет-скан 0; conventional commit
```

### Оценка блокирующих дефектов

Блокирующих для freeze-цепочки дефектов НЕ осталось. Неопределённость 32b
(subsample 1.298 vs advisory 0.907 vs параметрика 0.76–0.81) теперь: (а) честно
зафиксирована в evidence и протоколе two-estimate схемой; (б) вынесена владельцу
до HG-B с тремя опциями без касания порогов/статистики; (в) покрыта failsafe
поведением gate (FAIL ⇒ INFEASIBLE ⇒ owner, без подгонки). Это правильная
конструкция pre-data честности: неопределённость превращена в механическую
процедуру + владельческое решение, а не в post-hoc свободу.

### Refresh-verdict

```text
REFRESH_VERDICT = PASS
```

Candidate R2 + pinned feasibility gate готов к вынесению на HG-B с моих позиций.
Этот refresh не создаёт научных утверждений, не freeze'ит протокол и не меняет
NL5-002 terminal MISMATCH / NOT accepted, v0.1 envelope, PLATFORM-SENSITIVITY-R1,
external_reproductions = 0, NL6-001 LOCKED; claim ceiling пакета — по-прежнему
C0_SOFTWARE_ONLY.

— Fresh independent Scientific Reviewer (CONTROL), refresh R2, 2026-09-30

## Review R3 (candidate R3) @ 2c3171e

```text
REVIEW_ID          = NL5-ACCEPTANCE-POLICY/REVIEWER_VERDICT (review R3)
REVIEW_VERDICT     = PASS
REVIEW_DATE        = 2026-10-01
REVIEWED_BRANCH    = control/nl5-acceptance-policy-r3
REVIEWED_HEAD      = 2c3171eac9e4e347968f2c266e7a4f8fc2d63c72
SUBSTANTIVE_HEAD   = bc83af2ff3b5951544491dd1760907662ff0e39a
                     (tree 64a861c3a6c4d7009162d957c51863e0d98b7ed6 — сверен
                      git rev-parse bc83af2^{tree}; заявленное совпадает)
BASE-ЦЕПОЧКА       = a9d7d07 (refresh R2 head, точный родитель bc83af2) →
                     bc83af2 (repair R3) → 2c3171e (event 0007, append-only
                     post-terminal correction) — сверено git log --format='%h %p'
ANCESTRY           = 61d8c67 (мой refresh R2 PASS @ a9d7d07) — голова repair R3
                     сидит точно на проверенной базе; review-коммиты живут на
                     review-ветках, вне candidate-цепочки (корректно)
BRANCH НА ORIGIN   = отсутствовала до review (git ls-remote --heads origin
                     review/nl5-acceptance-policy-r3 — пусто); worktree
                     review/nl5-acceptance-policy-r3 @ 2c3171e, user CONTROL,
                     autocrlf false, safecrlf true
CLAIM CEILING      = C0_SOFTWARE_ONLY для этого вердикта: не создаёт научных
                     утверждений, НЕ freeze'ит протокол, НЕ объявляет NL5
                     acceptance; NL5-002 terminal MISMATCH / NOT ACCEPTED,
                     v0.1 envelope, PLATFORM-SENSITIVITY-R1,
                     external_reproductions = 0, NL6-001 LOCKED — не тронуты
ROLE               = REVIEWER (свежая независимая сессия; доверяю только
                     git-фактам и собственным измерениям)
```

Предмет: candidate `NANOLAB_REPRO_V0_2_CANDIDATE_R1.md` revision R3 (PRE-DATA,
NOT FROZEN), seed tool `scripts/nl5/repro_v02_seeds.py` (N-contract),
`scripts/nl5/repro_v02_feasibility_gate.py` (declared N-grid),
`scripts/nl5/repro_v02_freeze_gate.py` (consistency gate), HG-B proposal R3,
evidence: `repro-v0-2-seed-record-PRE_DATA_R3.json` (record_sha256
eb4ab3f891e17dd2b456a3870ed73b19e39d67bf51109b6cb47ca64524ce476b),
`repro-v0-2-n-grid-R3.json`; старые R1/R2 evidence — не переписаны (0-diff).
Full diff `a9d7d07..2c3171e` прочитан (11 файлов, +1136/−143). R3 закрывает
M-2 PARTIAL (мой refresh R1) и миссионерские требования closure: N-contract,
declared grid, no-accept-risk, consistency gate, tree-collision scan.

## R3.1 Инвариант-согласованность N (machine-проверено, все числа рядом)

| Поверхность | Значение | Источник/проверка |
|---|---|---|
| protocol §7 cardinality contract | 0b = 64, 32b = 64, 11b = 10, 53b = 10 → fresh_seed_total = 148 | текст, строка контракта R3; единственное вхождение паттерна для парсера gate |
| protocol §8 N | primaries N = 64 paired / controls N = 10; N_min = 51 (80%·64) / 8 | текст; согласовано с §12.4 |
| protocol §12.1 declared grid | grid {40, 48, 64, 80, 96,128}, headroom ratio ≤ 0.80, правило «минимальный проходящий N» | текст-константа ДО результатов; SELECTED_N = 64 — вывод, не константа |
| protocol §12.1 исполнение | N=40 FAIL (0.124/1.298) → N=48 FAIL → N=64 PASS (0b 0.071 / 32b 0.736) → SELECTED_N = 64 | мой прогон `run_n_grid` воспроизвёл committed evidence bit-exact (см. R3.3) |
| protocol §12.2 budget | 2×64×2 + 2×10×2 = 256 + 40 = 296; replacements ceil(296·0.20)=60; MAX 356; wall ≤ 560 ч | литералы в тексте; `derive_budget(2,2)` = 296+60=356 — совпадает; 148/20=7.4× калибровка 72 ч → 532.8 ≤ 560 ч |
| seed record variant_counts | {0b:64, 32b:64, 11b:10, 53b:10}; primary_replicas=64; control_replicas=10; fresh_seed_total=148; длины потоков 64/64/10/10 | committed JSON; сверено программно |
| seeds.py | PRIMARY_REPLICAS=64, CONTROL_REPLICAS=10, VARIANT_REPLICAS 64/64/10/10, FRESH_SEED_TOTAL=148 | machine constants; тест `test_seed_count_contract` |
| freeze_gate.py | PRIMARY_N=64, CONTROL_N=10, N_MIN_PRIMARY=51, N_MIN_CONTROL=8, REPLACEMENT_FRACTION=0.20, WALL=560 | machine constants; gate PASS на пакете (R3.4) |

**ВСЕ поверхности согласованы: 64/64/10/10 = 148 везде; 296+60=356 везде;
N_min 51/8 = 80%-базис 64/10. Расхождений не найдено.**

## R3.2 Seed record — независимое воспроизведение

- Регенерация `seed_record(tree_collision_scan=…)` со сканом **a9d7d07-tree**
  (временный worktree, удалён после проверки) → **byte-identical** committed
  JSON; `record_sha256 = eb4ab3f8…` совпал с committed evidence.
- Fresh_total = 148; глобальная уникальность 148/148; 34 exclusions ∩ fresh = ∅;
  bootstrap 4 уникальных, ∩ fresh = ∅, ∩ historical = ∅.
- Skips записаны и подтверждены сканом: 0b 10 / 32b 11 / 11b 10 / 53b 10
  (indices 1–10 всех вариантов + 32b index 25). **Каждый** из 41 skip-seed
  литерально встречается в a9d7d07-tree; **ни один** из 148 emitted seeds
  не встречается. Источники коллизий: старые seed records R1/R2
  (`…PRE_DATA.json`/`…_R2.json` — тот же anchor, тот же поток → правило
  continuation механически отработало) и траекторные артефакты (32b idx 25).
- Tree-collision правило pre-declared (§7: index-порядок, skip+record),
  тест `test_tree_collision_continuation_rule` (mock) +
  `test_literal_tree_scan_hits_needle` (реальный git grep -F).
- Freeze-time scan: 148 fresh seeds при исключении seed-record/protocol путей
  (задокументировано в §7) → **0 коллизий** в текущем дереве.

## R3.3 Declared N-grid — воспроизведение bit-exact

Мой прогон `run_n_grid` (PYTHONPATH=scripts, committed R1 paired JSON
`EX-NL5-002-E-R1/evidence/paired/paired_platform_sensitivity.json`,
source_sha256 `2b0df07d…` совпал) на bootstrap seeds из committed R3 record →
**полное побитовое совпадение** с `repro-v0-2-n-grid-R3.json` по всем float-полям,
selected_n=64, design_infeasible_at_grid=false (единственное поле-различие —
строка `source`: абсолютный путь окружения имплементатора vs мой относительный;
не числовое). Строки N=40/48 честно FAIL и сохранены; плато 80/96/128 —
ожиданная квантизация 10-точечной поддержки subsample-bootstrap (известный
R-2 granularity-артефакт), полный grid сохранён. Правило — constant (grid +
headroom 0.80 + «минимальный проходящий»), SELECTED_N — вывод. Независимая
проверка feasibility двумя оценками на N=64: pinned subsample 0b 0.0714 / 32b
0.7357; мой пересчёт ADVISORY √n-схемы (R-2) на N=64: 0b 0.164 / 32b 0.717 —
**обе оценки ≤ 0.80 на выбранном N** (расхождение оценок R2-эры на n=40 снято
выбором N=64).

## R3.4 No-accept-risk + consistency gate + machine-проверки

- §12.3: «gate FAIL ⇒ execution = BLOCKED; путь "owner accepts risk → execute
  despite failed mandatory gate" ЗАПРЕЩЁН; разрешение ТОЛЬКО новой
  preregistered revision, которая САМА проходит gate». §12.5 дублирует в
  stop conditions. HG-B proposal §4.1: accept-risk опция УДАЛЕНА (сравнил с
  R2-версией: была опция «принять риск» — теперь absent; риск 32b снят
  grid-выбором N=64). Найден ровно один контекст «accept» в пакете —
  запретительный. **No-accept-risk: подтверждено.**
- `freeze_consistency_gate(protocol_text, committed_record)` → **PASS**
  (failures=[]); негативные направления проверены мной: record
  variant_counts 0b→10 → FREEZE_GATE_FAIL; protocol literal 40 →
  FREEZE_GATE_FAIL; budget drift (3 primaries) → FREEZE_GATE_FAIL. Тесты
  покрывают PASS (`test_pass_on_consistent_package`) и оба FAIL-направления
  (`test_fail_on_record_mismatch` — класс дефекта R1/R2;
  `test_fail_on_protocol_mismatch` — grid-минимум 40). Бюджет-drift направление
  тестом не покрыто (покрыто моим прогоном) — см. MINOR-3.
- `python3 -m pytest tests/ -q` → **399 passed**; `PYTHONPATH=scripts
  python3 -m pytest tests/test_nl5_repro_v02_seeds.py -q` → **25 passed**
  (список тестов сверен поимённо).
- check-consistency → `ok:true, errors=[], warnings=0`; workflow_lint →
  `violations=0, blocking=0`; `work_cli validate
  docs/work/executions/EX-NL5-ACCEPTANCE-POLICY-R2` → `ok:true,
  HANDOFF_READY`; события 0005–0007 = CONTINUATION post-terminal corrections —
  валидный класс (терминальный HANDOFF 0004 не редактировался; tail
  corrections append-only), timestamps монотонны 14:56:00Z→01:21:10Z,
  subjects 0005/0006/0007 = f07fe39/c25bcd6/bc83af2 — lineage корректен.
- jsonschema: passport VALID (`execution-passport.schema.v1.json`); 7/7 events
  VALID (`work-event.schema.v1.json`) — мой прогон jsonschema Draft7.
- Scope: `git diff --name-only a9d7d07..2c3171e` = 11 файлов, все ⊂
  allowed_paths паспорта (exact + `EX-…/**` + `scripts/nl5/**`).
- Protected paths 0-diff: `project/state.json`, `project/infra-state.json`,
  `docs/evidence/**`, `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE.md`,
  `REPRODUCTION_RULE_V0_1.md`, `ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md`,
  `experiments/evidence`, EX-NL5-002-{E,B-R1,B-R2} — не тронуты; R1/R2
  seed records byte-identical (record_sha256 5c956644… сохранён).
- Секрет-скан full diff: чист. Commits conventional (`repair(nl5):`).

## R3.5 Non-post-hoc nature — явные ответы (обязательная секция)

Единственное «данное», существующее на момент R3 — committed HISTORICAL R1
platform-study paired medians; confirmatory data кампании v0.2 НЕ СУЩЕСТВУЮТ
(PRE-DATA). Вопрос «использовались ли future confirmatory data» вырождается
в «использовались ли R1 planning-данные за пределами разрешённой роли» —
mission §26 разрешает planning-использование исторических данных.

1. **δ — НЕТ.** δ = 0.5 объявлен конвенцией «medium effect» в candidate R1
   (3171564) и не менялся ни в одной ревизии (§4: «fixed a priori… НЕ выводится
   из R1 data»); секция §9 R2→R3 **byte-identical** (проверено побайтовым
   сравнением секций). Исторические сдвиги присутствуют только в Appendix A
   как power/budget контекст. Reverse-tuning отсутствует: observed R1 |d| =
   0.25s/0.38s лежат внутри ±0.5s.
2. **N — НЕТ** (в разрешённом смысле). N выведен declared-grid процедурой:
   grid {40,48,64,80,96,128}, headroom 0.80 и правило «минимальный проходящий»
   сформулированы как константы §12.1 ДО результатов; SELECTED_N = 64 —
   механический вывод pinned `run_n_grid` на committed R1 **planning**-данных
   (разрешено mission §26; Appendix A: «Не thresholds»). Я воспроизвёл grid
   bit-exact. Направление выбора консервативно: N увеличен 40→64 (budget
   240→356 runs), т.е. имплементатор выбрал дороже-и-надёжнее, а не дешевле;
   правило не имеет свободных параметров. Честная оговорка: текст правила и
   grid-результаты попали в один commit bc83af2, поэтому git-порядок
   «текст-до-вычислений» внутри коммита недоказуем; компенсируется
   механичностью правила, отсутствием подтверждённых данных (подгонять
   нечего, кроме planning-бюджета), совпадением с моими независимыми
   оценками (advisory 0.907@n=40 → 0.717@N=64) и тем, что пересчёт grid при
   dispatch (§12.3) и fail-safe поведение gate закрывают путь злоупотребления.
3. **seeds — НЕТ.** Детерминированный sha256-поток от фиксированного anchor;
   continuation-правило pre-declared (§7); skips записаны и независимо
   воспроизведены (R3.2); регенерация byte-identical; ручной выбор невозможен
   по конструкции (refusal на historical, skip+record на tree-collision).
4. **variants — НЕТ.** 0b/32b primary + 11b/53b control объявлены в candidate
   R1 и не менялись; 74b по-прежнему NOT_MEASURED/запрещён. Никаких будущих
   данных не существует.
5. **decision thresholds — НЕТ.** §9 (margin ±δ·s_eff, N_min=80%, приоритетная
   классификация §9.2/9.3, downgrade-правило, s_floor, классы §9.4) —
   byte-identical R2→R3. Изменены ТОЛЬКО §7 (N-contract), §8 (N=64+N_min=51),
   §12 (grid/budget/gates) и Appendix B (история ревизий) — все изменения
   смещают дизайн в сторону большей доказательной силы, не в сторону
   желаемого вердикта.

**ИТОГ: ни δ, ни N, ни seeds, ни variants, ни thresholds не выбраны по future
confirmatory data — таких данных не существует; все выбора a priori либо
механический вывод pre-declared правила на разрешённых planning-данных.**

## R3.6 Findings

**MAJOR: нет.**

- **MINOR-1 (текст, застарелый литерал — исправить ДО freeze).** В новом
  §7 cardinality-блоке: «**100** fresh globally unique» (строка 157) и в
  Appendix B: «N-contract generator (**100** fresh seeds)» (строка 398).
  Фактическое значение 148 (64+64+10+10); 100 — застарелый литерал R2-эры
  (40+40+10+10). Machine-контракты (record, тесты, gate) принуждают 148,
  аналитической свободы не создают, но текст, идущий в freeze, обязан быть
  однозначным. Рекомендация: заменить на «148 fresh globally unique (100%)»
  и «148 fresh seeds» — бесплатно до данных.
- **MINOR-2 (bootstrap seeds унаследованы от R1/R2-эры).** R3 bootstrap =
  {323707441, 1702258603, 404063983, 627625019} — **byte-identical** R1/R2-era
  bootstrap (тот же anchor + labels «bootstrap-{v}»); мой whole-tree scan
  нашёл ровно эти 4 литерала в старых records вне разрешённых путей (fresh
  148 — 0 коллизий). Контракт §7 нарушен не буквой (scan покрывает только
  fresh; bootstrap-требования — уникальность и дизъюнктность — выполнены),
  но «свежесть» bootstrap условна, и freeze-time whole-tree scan, расширенный
  на bootstrap, провалился бы. Влияние pre-data нулевое (bootstrap — только
  RNG ресемплинга CI; физики не касается; в R1/R2 использовался на
  planning-данных). Рекомендация: распространить continuation-правило на
  bootstrap-метки ЛИБО явно задокументировать намеренное переиспользование.
- **MINOR-3 (event 0007 завышает test-coverage).** Summary события заявляет
  тесты «N-grid deterministic, selected-N deterministic, headroom 0.80» —
  таких тестов НЕТ (поимённая сверка 25 тестов; grep по run_n_grid/HEADROOM/
  selected_n в tests/ пуст). Реально покрыты: budget 296/356 и N_min (внутри
  freeze-gate PASS-теста), FAIL-направления record/protocol; grid-selection
  я проверил независимым bit-exact прогоном (R3.3). Отчётная неточность в
  record; рекомендация: добавить тест run_n_grid (детерминизм + selected_n +
  HEADROOM_RATIO constant) и budget-drift FAIL-направление до freeze.

**NOTE:**

- Commit bc83af2: «25/402 tests green» — фактический счёт 25 seed / **399**
  full; задокументировано самим пакетом (event 0007 + summary §6 errata) как
  cosmetic. Подтверждаю: 399/399.
- R-3 (частота INCONCLUSIVE) количественно сохраняется и на N=64: мой MC
  (numpy, committed R1 σ, семантика pinned-правила, Δ=0, 400 trials×B=1000):
  P(EQUIVALENT) 0b ≈ 0.21, 32b ≈ 0.28–0.30 (ρ=0/0.3), WO-level ≈ 0.06 —
  однократная кампания и при идеальной эквивалентности платформ чаще вернёт
  честный INCONCLUSIVE, чем REPRODUCED. Это тот же задокументированный
  tradeoff, что был закрыт в refresh R1/R2 (owner-visible, failsafe gate);
  направление ошибки консервативное (spurious MISMATCH при Δ=0 редок).
  Владельцу видеть до HG-B.
- Two-estimate disclosure (ADVISORY √n) из R2 §12 в R3-протоколе больше не
  публикуется (заменена grid-механикой); R2 evidence сохранена и
  ссылается §12.3. Мой пересчёт advisory на N=64 (0.164/0.717 ≤ 0.80) —
  скрытой неопределённости на выбранном N нет.
- WORK_QUEUE NL5-002: замена точечная («40» → «64 primaries/10 controls
  (declared grid)»), но результат содержит дубль фрагмента «…(declared grid)
  primaries/10 controls» — cosmetic; terminal MISMATCH/NOT ACCEPTED и вся
  цепочка гейтов сохранены байт-в-байт.
- Тестовый файл: `if __name__ == "__main__": unittest.main()` стоит ПЕРЕД
  последними двумя классами (FeasibilityGateTest, FreezeConsistencyGateTest) —
  прямой запуск файла как скрипта тихо пропустил бы 7 тестов; pytest
  собирает все 25. Cosmetic. Аналогично `derive_budget(None)`-ветка — dead
  code. Cosmetic.
- Wall-budget: 148 runs ≈ 7.4× калибровки (20 runs/72 ч) = 532.8 ч ≤ 560 ч —
  арифметика сходится.

## R3.7 Явные утверждения ревьюера

1. Binding-факты соответствуют заявленным: head 2c3171e, substantive bc83af2
   (tree 64a861c3…), base a9d7d07 = точный родитель; ветка отсутствовала на
   origin до review; R1/R2 evidence-records не переписаны.
2. N-инвариант ПОЛНОСТЬЮ согласован на всех восьми поверхностях (R3.1):
   64/64/10/10=148, 296+60=356, N_min 51/8, headroom 0.80, SELECTED_N=64.
3. Seed record R3 детерминированно воспроизводится byte-identical со сканом
   a9d7d07-tree; skips/уникальность/дизъюнктность подтверждены независимо.
4. N-grid воспроизведён bit-exact; неудобные строки сохранены; SELECTED_N
   выведен, не назначен.
5. No-accept-risk подтверждён (§12.3/§12.5 + HG-B §4.1, опция удалена).
6. Consistency gate: PASS на пакете, FAIL на всех трёх негативных классах.
7. Non-post-hoc: НЕТ по всем пяти пунктам (R3.5) — с честной оговоркой о
   недоказуемости внутрикоммитного порядка «правило-до-вычислений» и её
   компенсациях.
8. Nothing frozen: candidate NOT FROZEN / PRE-DATA; freeze chain §13 не
   исполнялась; этот вердикт ничего не freeze'ит и не объявляет NL5
   acceptance; merge = HG-C, HG-B = owner.
9. Несмотря на MINOR-1..3 — все три устранимы бесплатно до freeze и не создают
   post-hoc свободы в правиле решения; блокирующих дефектов нет.

## R3.8 Вердикт

```text
REVIEW_VERDICT = PASS
```

Candidate R3 готов к вынесению на HG-B с моих позиций — при условии
раскрытия владельцу MINOR-1..3 + NOTE (R-3-квантификация на N=64) и
рекомендации исправить MINOR-1 (застарелые «100 fresh») до Director freeze.
Этот вердикт не создаёт научных утверждений, не freeze'ит протокол, не
меняет NL5-002 terminal MISMATCH / NOT accepted, v0.1 envelope,
PLATFORM-SENSITIVITY-R1 FULLY VERIFIED, external_reproductions = 0,
NL6-001 LOCKED; claim ceiling — C0_SOFTWARE_ONLY.

— Fresh independent Scientific Reviewer (CONTROL), review R3, 2026-10-01
