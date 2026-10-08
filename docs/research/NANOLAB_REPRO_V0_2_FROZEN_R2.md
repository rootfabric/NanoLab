# NANOLAB_REPRO_V0_2_FROZEN — Frozen distribution-based reproduction rule (v0.2)

Статус: **FROZEN / PRE-DATA** — научное содержание правила v0.2 заморожено до
любых confirmatory данных.

Этот документ — authoritative frozen protocol правила
`NANOLAB_REPRO_V0_2_DISTRIBUTIONAL`, corrected immutable revision
**FROZEN_R2**. Он выведен из approved R4 candidate
(`docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md`, revision R4, post-R4.3
hardened basis) без изменения какого-либо научного параметра и без единого
confirmatory наблюдения. История candidate-ревизий R1 → R2 → R3 → R4 → R4.1 —
git history документа-предшественника и evidence
`docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/`; она не копируется
сюда дословно, а фиксируется ссылками на immutable commits/paths.

Предыдущая frozen-ревизия FROZEN_R1 (immutable FROZEN PACKAGE COMMIT F1 =
cb91ade761f6802fc40c500761d3e35022408822, tree
ad21ce39b42681f581da996b2805a5b2fb49111f, protocol
`docs/research/NANOLAB_REPRO_V0_2_FROZEN_R1.md`) — сохранённая историческая
неудачная попытка freeze: fresh Scientific Reviewer R1 дал вердикт
FAIL / FIX_REQUIRED (находка M-1: §6 протокола FROZEN_R1 объявляла exact path
allowlist collision-скана как пути frozen-артефактов самого пакета, тогда как
authoritative contract корректно сохранял approved R4 allowlist pinned-дерева;
review evidence `docs/evidence/NL5-V02-FREEZE/FRESH_SCIENTIFIC_REVIEW_R1.{md,
json}`). FROZEN_R1 и Director FREEZE R1 record не изменены и не удалены — это
immutable historical attempt, superseded для dispatch настоящей ревизией
FROZEN_R2. Единственное содержательное исправление FROZEN_R2 относительно
FROZEN_R1 — корректная фиксация exact allowlist collision-скана (§6, machine
block `scan-allowlist-v1`) и revision/provenance-метаданные; научное
содержание (§3–§11) идентично approved R4 / FROZEN_R1 по всем параметрам.

## 0. Замораживающие объявления (authoritative)

```text
rule_id                   = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL
candidate basis revision  = R4 (параметры утверждены HG-B; см. ниже)
frozen revision           = FROZEN_R2 (этот документ; corrected revision после
                            fresh Scientific Review R1 = FIX_REQUIRED на
                            FROZEN_R1, находка M-1 — противоречие declaration
                            collision-scan exact allowlist; см. §6)
freeze decision           = FREEZE, issuer_class = DIRECTOR — Director FREEZE
                            record: docs/evidence/NL5-V02-FREEZE/
                            DIRECTOR_FREEZE_R2.{md,json}; record commit —
                            строгий потомок frozen package commit F
owner basis               = HG-B APPROVED, decision_id
                            NL5-ACCEPTANCE-POLICY/HG-B/R1 (2026-10-05):
                            docs/evidence/NL5-ACCEPTANCE-POLICY/
                            HG_B_OWNER_DECISION_R1.{md,json}
scientific basis subject  = R4 product subject
                            39cc9809ad4b9ad61b2effd6dbcb8c9067848da0
                            (tree 10ba8bbffcae06ae7fad7135b2493494b0d4f9b1);
                            fresh Reviewer R4 = PASS (f564aa7ab4654043a3bbd0711a
                            893427f5a0f2f2); fresh Verifier = VERIFIED
                            (4d14b34f8b91312a6c8d393840cb107974d0de10)
authoritative contract    = docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/
                            evidence/repro-v0-2-freeze-contract-FROZEN_R2.json
                            (revision r4, freeze_status = FROZEN; выведен из
                            PRE_DATA_R4 заменой только allowlisted
                            scientific_subject leaves — как в FROZEN_R1)
seed record               = docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/
                            evidence/repro-v0-2-seed-record-FROZEN_R2.json
                            (байт-в-байт копия принятой R4 PRE-DATA seed record;
                            идентична FROZEN_R1 seed record)
claim ceiling             = C1_COMPUTATIONAL_REPRODUCTION (у будущей кампании)
execution WO              = WO-NL5-V02-DIRECTOR-FREEZE-R2
                            (EX-NL5-V02-DIRECTOR-FREEZE-R2)
```

1. **Zero confirmatory data at freeze.** На момент freeze не существует ни
   одного confirmatory запуска v0.2: SCIENTIFIC_RUNS = 0,
   external_reproductions = 0. Freeze выполнен строго до данных; это
   обязательное свойство lifecycle S → F → R/V → A.
2. **Post-freeze edit policy.** Любое изменение научного содержания этого
   протокола (параметры, seeds, статистика, decision rule, критерии) после
   freeze — только новая revision (v0.3+) через новый Work Order, новый freeze
   и новую кампанию. Правка frozen текста запрещена; технические
   (ненаучные) исправления требуют отдельного явного решения с новой
   фиксированной версией документа.
3. **Authoritative declarations.** Ровно один machine block `machine-contract-v1`
   (§11), ровно одна cardinality-строка (§6) и ровно один machine block
   `scan-allowlist-v1` (§6) являются авторитетными декларациями документа;
   они машинно сверяются contract gate'ом с authoritative contract JSON
   (allowlist block — ordered exact сравнение с
   `seed_generation.scan_allowlist_paths_exact`; repair M-1 review R1).
   Любое противоречие/дублирование =
   FREEZE_GATE_FAIL (fail-closed). Литеральная устаревшая декларация
   незамороженности в FROZEN-протоколе запрещена валидатором.
4. Этот документ не содержит и не может содержать SHA собственного frozen
   package commit: pins F_HEAD/F_TREE публикуются внешним Director FREEZE
   record и последующими review/verify записями (exact-subject = F).

## 1. Мотив (сжатая фиксация; полный текст — candidate basis)

`NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` (immutable, применён к NL5-001-C/NL5-002)
дал механический вердикт NL5-002, но имеет заранее видимые ограничения:
envelope из 3 реплик — узкая эмпирическая полоса; правило не различает
«сдвиг меньше собственной вариативности» от «совпадение точка-в-точку»;
INCONCLUSIVE-область велика. v0.2 — distribution-based правило: equivalence
платформенных распределений при fresh paired seeds. Terminal MISMATCH NL5-002
и finding PLATFORM_INSENSITIVE не пересматриваются этим протоколом.

## 2. Разделение видов reproducibility (не смешивать)

```text
technical reproducibility      — тот же package/engine на той же платформе:
                                exit=0, integrity gates, digest-совпадение входов,
                                завершённые траектории (сломано => FAILED_TECHNICAL,
                                не MISMATCH)
numerical reproducibility      — побитовая повторяемость траекторий на идентичной
                                среде (здесь НЕ критерий)
distributional reproducibility — ЭТОТ протокол: equivalence распределений
                                наблюдаемых между author- и external-платформами
                                при fresh paired seeds
scientific consistency         — согласие с ранее принятыми качественными выводами
                                карточек; отдельная поверхность, здесь не гейтится
```

## 3. Scientific question

> Воспроизводится ли распределение per-replica median hinge angle вариантов
> dna_hinge (0b, 32b primary; 11b, 53b controls) на независимой
> external-платформе (U2) относительно author-платформы (U1) эквивалентно —
> то есть так, что межплатформенный сдвиг МЕДИАН мал относительно собственной
> внутриплатформенной вариативности свежих реплик?

Scope-ограничение (explicit, R4, сохранено): правило проверяет эквивалентность
**медианного парного сдвига** относительно внутриплатформенной вариативности
(TOST-логика на CI90 медианы d_i). Оно НЕ проверяет равенство прочих свойств
распределений (дисперсии, хвосты, форма, высшие моменты) и не утверждает
«платформы одинаковы во всём». PASS (EQUIVALENT) означает только, что CI90
медианного парного сдвига целиком лежит внутри заранее определённого
equivalence interval (−δ·s_eff, +δ·s_eff) (R4.1 wording, reviewer correction
m-1). Equivalence — НЕ statistical non-significance относительно нуля: сдвиг
может быть статистически отличим от нуля и при этом практически эквивалентен,
если весь его CI внутри pre-declared полосы; незамкнутый/широкий CI даёт
INCONCLUSIVE даже при точечном сдвиге, неотличимом от нуля.

## 4. Hypotheses (для каждого primary варианта v ∈ {0b, 32b})

Standard TOST semantics (R4.1, m-1; механическое decision rule §8.2 остаётся
authoritative и ему одного достаточно для вердикта):

```text
H0(v): не-эквивалентность — CI90(Δ_v) НЕ лежит целиком внутри полосы
       (−δ·s_v, +δ·s_v)                                (non-equivalence)
H1(v): эквивалентность — CI90(Δ_v) целиком внутри (−δ·s_v, +δ·s_v)
                                                     (equivalence, §8.2)
иначе  : INCONCLUSIVE для v
где Δ_v = median(d_v), d_i = median_B,i − median_A,i (paired по seed i),
    s_v = pooled within-platform SD(n−1) тех же парных образцов
          (s_eff = max(s_v, 0.01°), §8.1),
    δ  = 0.5 (fixed a priori; конвенция «medium effect»; НЕ выводится из R1 data)
Отвержение H0 (CI целиком внутри полосы) = EQUIVALENT(v) — mechanical rule
§8.2; H0/H1 labels — standard TOST convention, а не отдельный тест.
```

## 5. Platform definitions

```text
P-A (author)    = AUTHOR_U1, native Ubuntu R2, fingerprint frozen в
                  ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md §10 до кампании
P-B (external)  = U2 outenemy, независимая external сессия из release package +
                  frozen WO + pinned source acquisition; workspace НЕ копируется
                  из author; свежий fingerprint фиксируется отдельно
исключено       = Windows/WSL2 (WINDOWS_ALLOWED_FOR_NEW_SCIENCE = NO;
                  HISTORICAL_ONLY)
требование      = P-A ≠ P-B физически; у P-B своя build-цепочка по контракту R2 §5;
                  ОБЕ ноги гейтятся на R2 ACTIVE до dispatch (§12)
```

Расхождения toolchain (gcc line, cmake version) НЕ automatic failure: их
допускает сам принцип distribution-based equivalence. Fingerprint'ы обеих
платформ входят в evidence. На момент freeze AUTHOR_U1 = NOT_ASSIGNED,
R2 = WAITING_HOST / NOT_ACTIVE — это статусные границы, а не научные параметры.

## 6. Variants, fresh paired seeds, cursors (frozen identities)

```text
primary = 0b, 32b   (гейтовые варианты)
controls = 11b, 53b (репортятся; влияют только на downgrade §8.3)
74b     = NOT_MEASURED / KNOWN_GAP — исключён до отдельного arm-manifest-v2
          repair WO; значения 74b запрещены
run lengths (frozen convention B-R2 / platform study, без изменений):
  0b = 200k шагов; 11b, 32b, 53b = 150k шагов;
  analysis window / frame-validity gates — та же frozen convention
```

Generation (deterministic, зафиксировано до данных):

```text
anchor   = "NANOLAB-REPRO-V0.2-R1"
seed(v, i) = int.from_bytes(sha256(f"{anchor}|{v}|replica-{i:04d}").digest()[:4], "big")
             & 0x7FFFFFFF  → positive int32
bootstrap seeds = аналогично с label "bootstrap-{v}" (retry -01, -02, … при коллизии)
generation_revision = r4-pools-on-a9d7d07 (confirmatory identities = R3,
                      bit-exact replay)
```

Экземпляр ОБЯЗАН быть идентичным на обеих платформах (paired design: seed i на
P-A и P-B образует пару i) — это часть протокола, не опция.

Frozen exclusion list — 34 документированных R1 confirmatory seeds (генератор
ОТКАЗЫВАЕТСЯ выдавать seed record с коллизией; полный список — в seed record
и authoritative contract, `historical_exclusions.list_size = 34`).

Обязательство регенерации (часть протокола): seed record frozen из anchor,
сверен с exclusion list (34), literal tree scan по **pinned immutable tree**
`a9d7d07fa264e9907b67ca244b00ba2da3430b0f` — каждый fresh replica identity
(confirmatory + replacement pool; НЕ bootstrap) не встречается нигде в
зафиксированном дереве КРОМЕ exact path allowlist, зафиксированного ниже
machine block'ом `scan-allowlist-v1` и в authoritative contract
(`seed_generation.scan_allowlist_paths_exact`): это approved R4 пути,
существующие в pinned историческом дереве `a9d7d07…` — candidate document +
PRE_DATA_R4 seed record (repair M-1 review FROZEN_R1: allowlist принадлежит
pinned scan-дереву `a9d7d07…`; пути артефактов данного frozen-пакета — более
поздние Git-объекты и НЕ являются записями allowlist этого исторического
скана); prefix-исключения запрещены (F2). Scan
исполняется `git grep` по зафиксированному tree/commit, семантика fail-closed:
0 = найдено, 1 = чисто, иной код / недоступный object / не-git = SCAN_ERROR →
BLOCKED. Детерминистическое tree-collision правило: identity потребляются в
index-порядке; identity с литеральной формой в pinned дереве (SEED_COLLISION)
ПРОПУСКАЕТСЯ, потребляется следующий index, skip записывается в record; replay
записанных skips обязан воспроизводить опубликованные identities бит-в-бит
(машинно проверяется contract gate + machine-bound collision-scan manifest с
re-run каждого recorded skip). Изменение exclusion tree = новая generation
revision, не скрытый дрейф.

Machine-readable declaration exact allowlist (authoritative; ровно один такой
block в документе; машинно сверяется ordered exact сравнением с
`seed_generation.scan_allowlist_paths_exact` authoritative contract;
FROZEN-only синтаксис, исторический PRE-DATA R4 документ его не содержит;
repair M-1 review FROZEN_R1):

```text
# scan-allowlist-v1 (authoritative collision-scan exact allowlist; pinned scan tree a9d7d07fa264e9907b67ca244b00ba2da3430b0f; пути артефактов FROZEN_R2 пакета НЕ являются записями allowlist этого исторического скана)
path_1 = docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
path_2 = docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/repro-v0-2-seed-record-PRE_DATA_R4.json
```

Cardinality contract (revision R4, machine-enforced через authoritative
freeze contract) — единственная декларация кардинальностей в этом документе:

```text
0b = 64, 32b = 64, 11b = 10, 53b = 10  → fresh_seed_total = 148
(generation-time scan на pinned tree a9d7d07: 0b 10 skips, 32b 11, 11b 10,
 53b 10; indices_consumed = 74/75/20/20; next_candidate_index = 75/76/21/21)
bootstrap seeds = 4 (по одному на variant; индексы записаны в record)
148 fresh globally unique; bootstrap unique;
bootstrap ∩ fresh = ∅; fresh ∩ historical = ∅; bootstrap ∩ historical = ∅
protocol N == seed-record N == budget N == N_min-базис == authoritative contract
    (любое расхождение = FREEZE_GATE_FAIL, dispatch без PASS gate невозможен — F1)
replacement pool = заранее сгенерирован и frozen ДО данных от
    next_candidate_index (F3; §7)
```

Confirmatory seeds, bootstrap seeds, replacement pools, курсоры и все digests
фиксируются ТОЛЬКО authoritative contract JSON + seed record JSON этого
пакета (single source of truth); их полный состав в протокол не дублируется.

## 7. N, replicas, integer policy

```text
primaries (0b, 32b) : N = 64 fresh paired replicas на (variant, platform)
controls (11b, 53b) : N = 10 (non-gating, статистика та же)
обоснование N       = declared N-grid search (§10.1), зафиксированный ДО
                      вычислений: минимальный grid N с ratio_decision ≤ 0.80
                      по ОБОИМ primaries (safety headroom); механическое
                      исполнение на committed R1 paired данных дало
                      SELECTED_N = 64; R1 значения — ТОЛЬКО planning-оценка,
                      не thresholds
integer policy (F4) = ceil-nmin-floor-replacement-pairs-v1 (единая для всех
                      поверхностей):
  N_min             = ceil(0.80·N) валидных пар на ячейку:
                      primary ceil(0.80·64) = 52 (literal «не менее 80%»);
                      control ceil(0.80·10) = 8
  replacement quota = floor(0.20·N) ПАР на variant-ячейку, ТОЛЬКО для
                      FAILED_TECHNICAL: primary 12 пар, control 2 пары
                      (12/64 = 18.75% ≤ 20%; 2/10 = 20% ≤ 20% literal)
  replacement runs  = 2 runs на пару (paired legs) → cap =
                      2·(12+12+2+2) = 56 runs ≤ 20% от 296 literal
  max_runs          = 296 + 56 = 352
replacement mechanics = заранее сгенерированный frozen replacement pool на
                      variant, продолжающий deterministic поток С ИНДЕКСА
                      next_candidate_index (после последнего потреблённого
                      candidate index, включая skips; raw «N+1» ЗАПРЕЩЕН —
                      audit F3). Курсор (indices_consumed,
                      next_candidate_index) хранится per variant в record.
                      Новые attempt id (`<run_base>` / `<run_base>-R<n>`,
                      reuse запрещён, append-only ledger); замена —
                      pair-level one-shot (R4.1 M-4): pair_id unique, одна
                      frozen seed_identity на пару, замена ТОЛЬКО для
                      terminal PAIR_FAILED_TECHNICAL, максимум ОДНА замена
                      на failed pair, замена потребляет СЛЕДУЮЩУЮ identity
                      пула в порядке и планирует ОБЕ ноги новой пары;
                      outcome-driven выбор seeds запрещён. Исчерпание квоты
                      = честная классификация ячейки, без расширения
```

## 8. Observables, metrics, decision rule (полностью механические)

Observable — frozen convention без изменений: per-replica `median_deg`
валидных кадров, считанный упакованной конвенцией `analyze_hinge.py`
(nanolab-components 0.1.0). Convention НЕ заменяется и не параметризуется заново.

### 8.1 Статистика (pinned полностью)

```text
пары          = seed i на P-A и P-B (идентичный seed-set, §6);
                пара валидна, если обе стороны COMPLETED и прошли
                frame-validity; failed-пары не участвуют (замена §7)
d_i           = median_B,i − median_A,i                     (paired difference)
Δ̂            = median(d_i)                                  (primary statistic)
s             = pooled within-platform SD(n−1) обоих платформенных
                наборов тех же валидных пар; s_eff = max(s, 0.01°)
                (s_floor = 0.01° pre-declared: вырожденный s=0 не обнуляет
                margin и не допускает деления на ноль)
margin        = ±δ·s_eff, δ = 0.5
CI90(Δ̂)      = percentile bootstrap, PAIRED scheme: ресемплирование ПАР
                (индексы i) с возвращением; B = 10 000; RNG =
                python random.Random(bootstrap_seed_v); quantile =
                линейная интерполяция между порядковыми статистиками
                (numpy.quantile default 'linear')
overlap       = overlap coefficient эмпирических распределений (descriptive)
```

Выбор PAIRED схемы — часть дизайна (frozen identical seed-set), сделан
a priori, не по данным.

### 8.2 Классификация варианта (механическая, приоритет сверху вниз)

```text
1. если n_valid < N_min            → INCONCLUSIVE(v)
   (controls: n_valid < 8 → control-статистика помечается
   INCONCLUSIVE-CONTROLS и ИСКЛЮЧАЕТСЯ из downgrade-логики §8.3;
   verdict определяется primaries; направление ошибки консервативное)
2. если CI90(Δ̂) ⊂ (−margin, +margin)          → EQUIVALENT(v)
3. elif CI90(Δ̂) целиком выше +margin ИЛИ
         целиком ниже −margin                       → NOT_EQUIVALENT(v)
4. иначе                            → INCONCLUSIVE(v)
```

### 8.3 WO-level verdict (механический, приоритет сверху вниз)

```text
1. любая primary FAILED_TECHNICAL-класса кампании (бюджет/среда/движок,
   технический abort)              → FAILED_TECHNICAL
2. n_valid < N_min хотя бы одной primary → INCONCLUSIVE
3. обе primary EQUIVALENT(2) И ни одного gross control failure И
   ни одного задокументированного deviation ИЗ §8.4
                                   → REPRODUCED
4. обе primary EQUIVALENT(2) И (gross control failure ИЛИ deviations §8.4)
                                   → REPRODUCED_WITH_DEVIATION
5. хотя бы одна primary NOT_EQUIVALENT(3) → MISMATCH
6. иначе                          → INCONCLUSIVE
```

Gross control failure = |d̂_control| ≥ 1.0·s_eff (control) — pre-declared
threshold; он НЕ создаёт MISMATCH (controls не гейтят), но ПОНИЖАЕТ
REPRODUCED до REPRODUCED_WITH_DEVIATION и требует investigation-note в analysis.

### 8.4 Классы отклонений (pre-declared, замкнутый список)

```text
DEV-BUILD      : отличия toolchain/флагов сборки от зафиксированных fingerprints
DEV-ENV        : отличия ОС/окружения, не покрытые fingerprint-эквивалентностью
DEV-TOOLING    : отличия версий analyzer/packaging-инструментов при
                 byte-identical научных значениях
DEV-OPS        : scheduling/ресурсные события, повлиявшие на исполнение
```

Любое отклонение вне списка = protocol deviation → STOP + новая revision.
Каждое отклонение фиксируется в analysis с классом и признаком «менял ли
model / observable / seeds / статистику» (такие изменения запрещены §9).

## 9. Запреты (protocol integrity)

- Не подбирать δ, окна, seeds, N, статистику после просмотра данных (любое
  изменение = новая revision + новый freeze + новая кампания).
- Не использовать v0.1 envelopes/medians как acceptance thresholds (исторические
  значения — только feasibility planning).
- Не считать exit 0 научным PASS; не превращать FAILED_TECHNICAL в MISMATCH.
- Не переписывать NL5-002 terminal MISMATCH и PLATFORM_INSENSITIVE (frozen R1).
- Не производить 74b.

## 10. Budget, declared N-grid, feasibility gate, stop conditions (pre-declared)

### 10.1 Declared N-grid search (зафиксировано ДО вычислений)

```text
grid            = {40, 48, 64, 80, 96, 128}   (candidate R3 constant)
headroom        = ratio_decision <= 0.80 по ОБОИМ primaries
                  (safety headroom: проектировать НЕ на границе 1.0)
selection rule  = минимальный grid N, проходящий headroom по обеим primaries
δ / статистика  = БЕЗ ИЗМЕНЕНИЙ (0.5, paired) — grid меняет ТОЛЬКО N
planning data   = committed R1 paired platform-study medians (power/budget
                  planning; НЕ thresholds)
```

Механическое исполнение (pinned `run_n_grid`,
scripts/nl5/repro_v02_feasibility_gate.py; полный grid сохранён в evidence
`repro-v0-2-n-grid-R3.json`, digest закреплён в authoritative contract):

```text
N= 40: 0b 0.124 / 32b 1.298  → FAIL
N= 48: 0b 0.124 / 32b 1.298  → FAIL
N= 64: 0b 0.071 / 32b 0.736  → PASS  ← SELECTED_N = 64
N= 80: 0b 0.019 / 32b 0.173  → PASS
N= 96: 0b 0.019 / 32b 0.173  → PASS
N=128: 0b 0.019 / 32b 0.173  → PASS
```

### 10.2 Budget (derivation от SELECTED_N = 64, machine-consistent, F4 policy)

```text
confirmatory runs = 296 = 2·(64 + 64 + 10 + 10)
replacement cap   = Σ по ячейкам 2 × floor(0.20·N) = 2·(12+12+2+2) = 56 runs
                    (per-cell literal ≤ 20%: 12/64 = 18.75%, 2/10 = 20%;
                    сумма 56/296 = 18.92% ≤ 20%)
MAX runs          = 296 + 56 = 352
compute           = CPU-only, paid compute FORBIDDEN без отдельной owner-
                    авторизации
wall budget       = ≤ 560 ч на платформу; превышение → STOP / BUDGET_EXCEEDED,
                    не расширять автоматически
```

### 10.3 Mandatory feasibility gate (dispatch-инвариант)

```text
gate FAIL ⇒ execution = BLOCKED. Путь «owner accepts risk → execute despite
failed mandatory gate» ЗАПРЕЩЁН. Execution становится разрешён ТОЛЬКО новой
preregistered revision, которая САМА проходит gate.
```

Gate confirmation на dispatch: SELECTED_N = 64 и committed grid-строка N=64
(0b 0.071 / 32b 0.736 ≤ 0.80) — кампания проектируется в области, которая
была feasible на committed planning-данных R1 (planning-оценка, НЕ гарантия
исхода будущих данных/среды). Если к моменту dispatch planning-данные
изменились, grid пересчитывается той же pinned реализацией до dispatch, и
любое ухудшение за пределы headroom = BLOCKED (новая revision).

### 10.4 Consistency gate = authoritative freeze contract gate (F1)

```text
authoritative source = machine-readable freeze contract JSON этого пакета
  (revision r4, freeze_status = FROZEN): единственный authoritative
  declaration для freeze/dispatch; дублирующие/противоречащие декларации =
  FREEZE_GATE_FAIL
dispatch       = entrypoint обязан вызвать полный contract gate; PLAN не
  строится без PASS (обход невозможен по построению; negative tests
  фиксируют отказ)
проверки       = malformed/missing/extra/unknown revision/read error →
  fail-closed; фактические массивы: длины, int32-range, без bool,
  глобальная уникальность, disjoint fresh/bootstrap/replacement/historical
  множества, digest, bit-exact регенерация replay, per-cell quotas,
  total cap, wall cap, cardinalities
```

### 10.5 Stop conditions

```text
stop conditions   = environment недоступна → BLOCKED_ENVIRONMENT; ≥ 3 подряд
                    FAILED_TECHNICAL в ячейке → ячейка остановлена; любое
                    требование изменить protocol после data → STOP + новый WO;
                    ОБЕ ноги (author U1 и external U2) требуют R2 ACTIVE /
                    разрешённый executor до dispatch (HARD_BLOCKED иначе);
                    feasibility gate FAIL → BLOCKED (§10.3, без accept-risk
                    обхода); dispatch дополнительно гейтится fresh
                    Reviewer(F) PASS + fresh Verifier(F) VERIFIED + authority
                    record (lifecycle S → F → R/V → A)
```

## 11. Authoritative machine block (machine-contract-v1)

Единственный machine block документа; сверяется gate'ом с authoritative
contract JSON этого пакета:

```text
# machine-contract-v1 (authoritative; verified against repro-v0-2-freeze-contract-FROZEN_R2.json)
rule_id = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL
candidate_revision = R4
anchor = NANOLAB-REPRO-V0.2-R1
n_0b = 64
n_32b = 64
n_11b = 10
n_53b = 10
n_min_primary = 52
n_min_control = 8
replacement_quota_pairs_primary = 12
replacement_quota_pairs_control = 2
confirmatory_runs = 296
replacement_runs_cap = 56
max_runs = 352
wall_hours_per_platform = 560
selected_n = 64
headroom_ratio = 0.8
bootstrap_resamples = 10000
exclusion_list_size = 34
exclusion_tree_pin = a9d7d07fa264e9907b67ca244b00ba2da3430b0f
integer_policy_name = ceil-nmin-floor-replacement-pairs-v1
```

## 12. Freeze chain status и dispatch ceiling

```text
S  = PRE-FREEZE state, HG-B APPROVED (canonical main 549b687a9171ea3636dbb000
     78d7018f619cebd3, tree 5bfb2411d6283420e9067850807c6650725d838b)
F  = immutable FROZEN PACKAGE COMMIT — ЭТОТ документ + authoritative contract
     + seed record как exact Git blobs одного dedicated commit
D  = Director FREEZE record (отдельный commit, строгий потомок F),
     docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R2.{md,json}, пинует
     F_HEAD/F_TREE и exact Git-object digests трёх артефактов
     (исторические FROZEN_R1 = cb91ade761f6802fc40c500761d3e35022408822 и
     Director FREEZE R1 = 4236e0c7cfb19de2687a8f0d3be3641cc1b000d4 —
     immutable attempt, review FIX_REQUIRED, для dispatch superseded)
R  = fresh SCIENTIFIC REVIEWER(F) — ещё НЕ существует
V  = fresh independent VERIFIER(F) — ещё НЕ существует
A  = authority/readiness record (schema v3) — ещё НЕ существует
```

Даже после F и D научный dispatch остаётся ЗАБЛОКИРОВАННЫМ до появления R
(PASS), V (VERIFIED), R2 ACTIVE (gates U1–U5, NC-U1..U5, review/verify,
Human Gate) и назначенного AUTHOR_U1; launch gate = HUMAN_PROTECTED_WRITER,
machine_launch_authorized = false. Будущие ноги кампании:
`EX-NL5-REPRO-V0-2-U1-R1` (author, U1) и `EX-NL5-REPRO-V0-2-U2-R1`
(external, U2 из release package) — только после полного chain.

## Appendix A — Provenance references (immutable anchors)

```text
HG-B owner decision        = docs/evidence/NL5-ACCEPTANCE-POLICY/
                             HG_B_OWNER_DECISION_R1.{md,json}
                             (canonical main 549b687a9171ea3636dbb00078d7018f
                             619cebd3; canonical_sha256/blob — в Director
                             FREEZE record)
candidate basis            = docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
                             (revision R4; R4.3 product subject 39cc9809ad4b9ad
                             61b2effd6dbcb8c9067848da0, tree 10ba8bbffcae06ae7f
                             ad7135b2493494b0d4f9b1)
R4 hardening evidence      = docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/
source seed record (R4)    = docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/
                             evidence/repro-v0-2-seed-record-PRE_DATA_R4.json
collision-scan manifest    = docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/
                             evidence/r4-1-collision-scan-manifest-R4.json
                             (path + SHA-256 закреплены в authoritative contract)
feasibility evidence       = docs/work/executions/EX-NL5-ACCEPTANCE-POLICY-R2/
                             evidence/repro-v0-2-n-grid-R3.json
prior frozen attempt R1    = docs/research/NANOLAB_REPRO_V0_2_FROZEN_R1.md
                             (immutable F1 cb91ade761f6802fc40c500761d3e35022408822,
                             tree ad21ce39b42681f581da996b2805a5b2fb49111f;
                             Director FREEZE R1 = commit 4236e0c7cfb19de2687a8
                             f0d3be3641cc1b000d4; fresh Scientific Review R1 =
                             FIX_REQUIRED — docs/evidence/NL5-V02-FREEZE/
                             FRESH_SCIENTIFIC_REVIEW_R1.{md,json}, находка M-1;
                             historical, не изменяется, для dispatch superseded
                             настоящей ревизией)
freeze execution           = docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/
WO                         = docs/work/WO-NL5-V02-DIRECTOR-FREEZE-R2.md
```

Этот appendix — ссылки, а не научные декларации; научное содержание правила
зафиксировано §3–§11 и authoritative contract JSON.
