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
