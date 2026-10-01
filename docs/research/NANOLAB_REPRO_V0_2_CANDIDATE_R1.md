# NANOLAB_REPRO_V0_2_CANDIDATE — Candidate distribution-based reproduction rule

Статус: **CANDIDATE / PRE-DATA / NOT FROZEN**.

```text
rule_id (candidate) = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL
candidate revision  = R3 (2026-09-30, repair R2 по fresh review refresh R2 PASS
                      61d8c67 R-1..R-5 + central closure mission: (а) N-contract —
                      генератор выдаёт ровно протокольные cardinalities (было
                      10/вариант при протокольных 40 primaries; R3 grid-search →
                      SELECTED 64); (б) declared N-grid search зафиксирован ДО
                      вычислений; (в) mandatory feasibility gate FAIL ⇒ BLOCKED —
                      «accept risk» обход запрещён; (г) whole-tree seed collision
                      scan с deterministic continuation rule; (д) protocol↔record
                      consistency gate. Полные тексты R1/R2 — git history
                      (3171564 / 6e5287b); изменения ДО freeze бесплатны —
                      confirmatory data нет)
подготовлен          = WO-NL5-ACCEPTANCE-POLICY-R2 (EX-NL5-ACCEPTANCE-POLICY-R2)
базовый main         = 8205781def7179d6bdfa6eb7ab2a84d46776649c
date                 = 2026-09-30
freeze status        = NOT FROZEN — freeze отдельной Director-записью ТОЛЬКО после
                       HG-B (owner approval принципа) и fresh review/verify ЭТОЙ
                       ревизии, до любых confirmatory data
claim ceiling        = C1_COMPUTATIONAL_REPRODUCTION (у будущей кампании)
```

Этот документ — **candidate**. Он не изменяет canonical state, не freeze'ится
этим фактом и не отменяет `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` (тот остаётся
immutable, применённым к NL5-001-C/NL5-002; terminal MISMATCH NL5-002 не
пересматривается). После HG-B и Director freeze любые изменения — только новой
revision (v0.3+), никогда правкой frozen текста.

## 1. Урок v0.1 → мотив v0.2

`NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` классифицирует reproduction по попаданию
median трёх fresh replica medians в empirical envelope `[min, max]` ТРЁХ
reference replica medians. Это дало mechanical, честный вердикт NL5-002
(0b/32b MISMATCH, 11b/53b MATCH), но у правила есть заранее видимые
ограничения: (а) envelope из 3 реплик — крайне узкая эмпирическая полоса;
(б) правило не различает «платформенный сдвиг меньше собственной вариативности»
от «совпадение точка-в-точку»; (в) INCONCLUSIVE-область велика. v0.2 —
**distribution-based** правило: equivalence платформенных распределений.

## 2. Разделение видов reproducibility (не смешивать)

```text
technical reproducibility      — тот же package/engine на той же платформе:
                                 exit=0, integrity gates, digest-совпадение входов,
                                 завершённые траектории (сломано => FAILED_TECHNICAL,
                                 не MISMATCH)
numerical reproducibility      — побитовая/около-побитовая повторяемость траекторий
                                 на идентичной среде (здесь НЕ критерий)
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
> то есть так, что межплатформенный сдвиг мал относительно собственной
> внутриплатформенной вариативности свежих реплик?

## 4. Hypotheses (для каждого primary варианта v ∈ {0b, 32b})

```text
H0(v): CI90(Δ_v) ⊂ (−δ·s_v, +δ·s_v)          (equivalence, TOST-логика, §9)
H1(v): CI90(Δ_v) лежит целиком вне полосы     (не-эквивалентность, §9)
иначе  : INCONCLUSIVE для v
где Δ_v = median(d_v), d_i = median_B,i − median_A,i (paired по seed i),
    s_v = pooled within-platform SD(n−1) тех же парных образцов,
    δ  = 0.5 (fixed a priori; конвенция «medium effect»; НЕ выводится из R1 data)
```

## 5. Platform definitions

```text
P-A (author)    = AUTHOR_U1, native Ubuntu R2, fingerprint frozen в
                  ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md §10 до кампании
P-B (external)  = U2 outenemy, независимая external сессия из release package +
                  frozen WO + pinned source acquisition; workspace НЕ копируется
                  из author; свежий fingerprint фиксируется отдельно
исключено       = Windows/WSL2 (WINDOWS_ALLOWED_FOR_NEW_SCIENCE = NO)
требование      = P-A ≠ P-B физически; у P-B своя build-цепочка по контракту R2 §5;
                  ОБЕ ноги гейтятся на R2 ACTIVE до dispatch (§12/§13)
```

Расхождения toolchain (gcc line, cmake version) НЕ automatic failure: их
допускает сам принцип distribution-based equivalence. Fingerprint'ы обеих
платформ входят в evidence.

## 6. Variants и run parameters

```text
primary = 0b, 32b   (гейтовые варианты)
controls = 11b, 53b (репортятся; влияют только на downgrade §9.3)
74b     = NOT_MEASURED / KNOWN_GAP — исключён до отдельного arm-manifest-v2
          repair WO; значения 74b запрещены
run lengths (как в исполненной конвенции B-R2 / platform study):
  0b = 200k шагов; 11b, 32b, 53b = 150k шагов;
  analysis window / frame-validity gates — те же frozen convention без изменений
```

## 7. Fresh paired seeds (никакого повторного использования R1 confirmatory seeds)

Generation (deterministic, до данных):

```text
anchor   = "NANOLAB-REPRO-V0.2-R1" (фиксируется Director freeze record'ом)
seed(v, i) = int.from_bytes(sha256(f"{anchor}|{v}|replica-{i:04d}").digest()[:4], "big")
             & 0x7FFFFFFF  → positive int32
bootstrap seeds = аналогично с label "bootstrap-{v}"
```

Экземпляр ОБЯЗАН быть идентичным на обеих платформах (paired design: seed i на
P-A и P-B образует пару i) — это часть протокола, не опция.

Frozen exclusion list — 34 документированных R1 confirmatory seeds
(генератор ОТКАЗЫВАЕТСЯ выдавать seed record с коллизией):

```text
E1            : -200619630, 319832093
E2 reference  : 201004, 202008, 203012
E3-reval      : 204016, 205020, 206024
bootstrap R1  : 902107
B-R1          : 510101, 520202, 530303                    (EX-NL5-002-B-R1 evidence/frozen_seeds.json)
B-R2          : 410273, 520931, 638257, 741953, 852607, 963541,
                174329, 285637, 396421, 507283, 618457, 729613
                                                            (EX-NL5-002-B-R2 evidence/seeds_frozen.json)
platform study: 1259289227, 1358106528, 1524307444, 601855227,
                274288237, 972234272, 1934775205, 1747973984,
                880427736, 744386736                        (PREREGISTRATION_FREEZE_R1 S001–S010)
```

Обязательство регенерации (часть протокола, не только summary): при Director
freeze seed record регенерируется из frozen anchor, сверяется с exclusion
list (34), и выполняется whole-tree literal search — каждый fresh seed не
должен встречаться нигде в evidence-дереве КРОМЕ seed record и этого
документа (scan excludes seed-record/protocol paths; прецедент: verifier
platform study). Детерминистическое tree-collision правило генерации
зафиксировано ДО любых вычислений: identity потребляются в index-порядке;
identity, чья литеральная форма уже встречается в дереве (SEED_COLLISION),
ПРОПУСКАЕТСЯ, потребляется следующий index, skip записывается в record
(генерация R3, scan на a9d7d07-tree: skips учтены в record). Несовпадение digest'ов
или collision вне разрешённых мест = freeze невозможен.

Cardinality contract (revision R3, machine-enforced):

```text
0b = 64, 32b = 64, 11b = 10, 53b = 10  → fresh_seed_total = 148
(generation-time scan на a9d7d07-tree: 0b 10 skips, 32b 11, 11b 10, 53b 10)
bootstrap seeds = 4 (по одному на variant)
148 fresh globally unique; bootstrap unique;
bootstrap ∩ fresh = ∅; fresh ∩ historical = ∅; bootstrap ∩ historical = ∅
protocol N == seed-record N == budget N == N_min-базис (consistency gate;
    любое расхождение = FREEZE_GATE_FAIL)
```

## 8. N и replicas

```text
primaries (0b, 32b) : N = 64 fresh paired replicas на (variant, platform)
controls (11b, 53b) : N = 10 (non-gating, статистика та же)
обоснование N       = declared N-grid search (§12), зафиксированный ДО
                      вычислений: grid {40, 48, 64, 80, 96, 128}, правило
                      «минимальный N с ratio_decision ≤ 0.80 по ОБОИМ
                      primaries» (safety headroom, не граница 1.0);
                      механическое исполнение на committed R1 paired данных
                      дало SELECTED_N = 64 (0b 0.071 / 32b 0.736; полный grid
                      — evidence repro-v0-2-n-grid-R3.json); R1 значения —
                      ТОЛЬКО planning-оценка, не thresholds
N_min               = 51 валидных пары на primary ячейку (80% от N=64);
                      8 на control
replacement         = ≤ 20% на ячейку, ТОЛЬКО для FAILED_TECHNICAL
                      (новые attempt id; пара выбрасывается, если любая
                      сторона failed; замена идёт тем же generator-потоком
                      с индексами N+1, N+2, ...)
```

## 9. Observables, metrics, decision rule (полностью механические)

Observable — без изменений frozen convention: per-replica `median_deg`
валидных кадров, считанный упакованной конвенцией `analyze_hinge.py`.
Convention НЕ заменяется и не параметризуется заново.

### 9.1 Статистика (pinned полностью)

```text
пары          = seed i на P-A и P-B (идентичный seed-set, §7);
                пара валидна, если обе стороны COMPLETED и прошли
                frame-validity; failed-пары не участвуют (замена §8)
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

Выбор PAIRED схемы — часть дизайна (frozen identical seed-set, прецедент
frozen statistical plan platform study), сделан a priori, не по данным.

### 9.2 Классификация варианта (механическая, приоритет сверху вниз)

```text
1. если n_valid < N_min            → INCONCLUSIVE(v)
   (controls: n_valid < 8 → control-статистика помечается
   INCONCLUSIVE-CONTROLS и ИСКЛЮЧАЕТСЯ из downgrade-логики §9.3;
   verdict определяется primaries; направление ошибки консервативное)
2. если CI90(Δ̂) ⊂ (−margin, +margin)          → EQUIVALENT(v)
3. elif CI90(Δ̂) целиком выше +margin ИЛИ
        целиком ниже −margin                       → NOT_EQUIVALENT(v)
4. иначе                            → INCONCLUSIVE(v)
```

### 9.3 WO-level verdict (механический, приоритет сверху вниз)

```text
1. любая primary FAILED_TECHNICAL-класса кампании (бюджет/среда/движок,
   технический abort)              → FAILED_TECHNICAL
2. n_valid < N_min хотя бы одной primary → INCONCLUSIVE
3. обе primary EQUIVALENT(2) И ни одного gross control failure И
   ни одного задокументированного deviation ИЗ §9.4
                                   → REPRODUCED
4. обе primary EQUIVALENT(2) И (gross control failure ИЛИ deviations §9.4)
                                   → REPRODUCED_WITH_DEVIATION
5. хотя бы одна primary NOT_EQUIVALENT(3) → MISMATCH
6. иначе                          → INCONCLUSIVE
```

Противоречие R1-ревизии («controls без gross failure» vs «gross failure не
меняет verdict») устранено: gross control failure = |d̂_control| ≥ 1.0·s_eff
(control) — pre-declared threshold; он НЕ создаёт MISMATCH (controls не
гейтят), но ПОНИЖАЕТ REPRODUCED до REPRODUCED_WITH_DEVIATION и требует
investigation-note в analysis.

### 9.4 Классы отклонений (pre-declared, замкнутый список)

```text
DEV-BUILD      : отличия toolchain/флагов сборки от зафиксированных fingerprints
DEV-ENV        : отличия ОС/окружения, не покрытые fingerprint-эквивалентностью
DEV-TOOLING    : отличия версий analyzer/packaging-инструментов при
                 byte-identical научных значениях
DEV-OPS        : scheduling/ресурсные события, повлиявшие на исполнение
```

Любое отклонение вне списка = protocol deviation → STOP + новая revision.
Каждое отклонение фиксируется в analysis с классом и признаком «менял ли
model / observable / seeds / статистику» (такие изменения запрещены §10).

## 10. Запреты (protocol integrity)

- Не подбирать δ, окна, seeds, N, статистику после просмотра данных (любое
  изменение = новая revision + новый freeze + новая кампания).
- Не использовать v0.1 envelopes/medians как acceptance thresholds (исторические
  значения — только §12-feasibility и appendix planning).
- Не считать exit 0 научным PASS; не превращать FAILED_TECHNICAL в MISMATCH.
- Не переписывать NL5-002 terminal MISMATCH и PLATFORM_INSENSITIVE (frozen R1).
- Не производить 74b.

## 11. Technical failure policy

Replica FAILED_TECHNICAL: engine exit ≠ 0, неполная траектория, невалидные
кадры сверх frozen gates, digest mismatch входов. Retry — новый attempt id
(`-R1`, `-R2`, …), append-only ledger; replacement в пределах 20% allowance.
Ячейка с ≥ 3 подряд FAILED_TECHNICAL останавливается → честная классификация.

## 12. Budget, declared N-grid, feasibility gate, stop conditions (pre-declared)

### 12.1 Declared N-grid search (зафиксировано ДО вычислений)

```text
grid            = {40, 48, 64, 80, 96, 128}   (candidate R3 constant)
headroom        = ratio_decision <= 0.80 по ОБОИМ primaries
                  (safety headroom: проектировать НЕ на границе 1.0)
selection rule  = минимальный grid N, проходящий headroom по обеим primaries
δ / статистика  = БЕЗ ИЗМЕНЕНИЙ (0.5, paired) — grid меняет ТОЛЬКО N
planning data   = committed R1 paired platform-study medians (power/budget
                  planning; mission §26; НЕ thresholds)
```

Механическое исполнение (реализация pinned `run_n_grid`,
scripts/nl5/repro_v02_feasibility_gate.py; полный grid сохранён,
evidence `repro-v0-2-n-grid-R3.json`; неудобные строки не выбрасывались):

```text
N= 40: 0b 0.124 / 32b 1.298  → FAIL
N= 48: 0b 0.124 / 32b 1.298  → FAIL
N= 64: 0b 0.071 / 32b 0.736  → PASS  ← SELECTED_N = 64
N= 80: 0b 0.019 / 32b 0.173  → PASS
N= 96: 0b 0.019 / 32b 0.173  → PASS
N=128: 0b 0.019 / 32b 0.173  → PASS
```

### 12.2 Budget (derivation от SELECTED_N = 64, machine-consistent)

```text
confirmatory runs = primaries 2 × 64 × 2 = 256 + controls 2 × 10 × 2 = 40
                    = 296; replacements ≤ 59 → округлено 60 (20%); MAX 356 runs
compute           = CPU-only, paid compute FORBIDDEN без отдельной owner-
                    авторизации
wall budget       = ≤ 560 ч на платформу (~23 суток; калибровка: platform
                    study — 20 runs/platform в ≤ 72 ч при intra-node
                    параллелизме; 148 runs/platform ≈ 7.4×); превышение →
                    STOP / BUDGET_EXCEEDED, не расширять автоматически
```

### 12.3 Mandatory feasibility gate (dispatch-инвариант)

```text
gate FAIL ⇒ execution = BLOCKED. Путь «owner accepts risk → execute despite
failed mandatory gate» ЗАПРЕЩЁН. Execution становится разрешён ТОЛЬКО новой
preregistered revision, которая САМА проходит gate.
```

Gate confirmation на dispatch: SELECTED_N = 64 и committed grid-строка N=64
(0b 0.071 / 32b 0.736 ≤ 0.80) — кампания проектируется в гарантированно
feasible области; если к моменту dispatch planning-данные изменились (новые
committed paired evidence), grid пересчитывается той же pinned реализацией до
dispatch, и любое ухудшение соотношения за пределы headroom = BLOCKED (новая
revision). История R2-эры (0b 0.124 / 32b 1.298 при n=40) сохранена в
evidence `repro-v0-2-feasibility-gate-R2.json` как planning-факт.

### 12.4 Consistency gate (freeze/dispatch machine-check)

```text
protocol §8 N (64/10) == seed-record variant_counts == budget derivation N
== N_min-базис (51/8) == execution plan N. Любое расхождение =
FREEZE_GATE_FAIL — машино-проверяемо (tests + freeze checklist), невозможно
пропустить Reviewer/Verifier.
```

### 12.5 Stop conditions

```text
stop conditions   = environment недоступна → BLOCKED_ENVIRONMENT; ≥ 3 подряд
                    FAILED_TECHNICAL в ячейке → ячейка остановлена; любое
                    требование изменить protocol после data → STOP + новый WO;
                    ОБЕ ноги (author U1 и external U2) требуют R2 ACTIVE /
                    разрешённый executor до dispatch (HARD_BLOCKED иначе);
                    feasibility gate FAIL → BLOCKED (§12.3, без accept-risk
                    обхода)
```

## 13. Freeze chain (после HG-B, отдельными записями)

```text
HG-B APPROVED (owner)
  → Director FREEZE record: protocol text (этот документ с любыми owner-
    поправками), seed record (регенерация + 34 exclusions + literal search,
    digest), analyzer pin (package version + convention digest), N, budget,
    feasibility-gate evidence
  → fresh scientific Reviewer + fresh exact-head Verifier FROZEN protocol
  → prerequisite: R2 ACTIVE (gates U1–U5, NC-U1..U5, review/verify, Human Gate)
  → author leg  = EX-NL5-REPRO-V0-2-U1-R1 (на U1 через native executor)
  → external leg = EX-NL5-REPRO-V0-2-U2-R1 (на U2 из release package)
  → independent analysis + Scientific Reviewer + Verifier → NL5 decision
```

## Appendix A — Historical data used ONLY for power/budget planning

Не thresholds. Reviewer MC (f07fe39, §5) на реальных per-seed данных platform
study: independent-scheme CI90 half-width при n=10 ≈ 1.85×margin → стимул к
paired-схеме и N=40; paired half-width при n=40 ≤ margin (значения — в вердикте
review). E2 confirmatory 0b pooled median 65.98° [65.67, 66.32]. Эти числа
обосновывают N/budget; при freeze feasibility gate (§12) перепроверяется на
committed данных механически.

## Appendix B — Отличия от v0.1 и история candidate-ревизий

| аспект | v0.1 (immutable) | v0.2 candidate |
|---|---|---|
| единица | 3 replica medians, envelope [min,max] | paired seeds, N=64 primaries |
| статистика | point-in-envelope | paired TOST: CI90(Δ) vs ±δ·s_eff |
| margin | эмпирический envelope | δ = 0.5 pooled SD, a priori |
| исходы | MATCH/MISMATCH/INCONCLUSIVE | + REPRODUCED / REPRODUCED_WITH_DEVIATION / FAILED_TECHNICAL |
| 74b | NOT_MEASURED | NOT_MEASURED (без изменений) |

```text
candidate R1 (3171564): initial draft — review FAIL f07fe39 (M-1 exclusion 19→34,
                        M-2 n=10/δ=0.5 недостижим, M-3 rule не механичен)
candidate R2 (6e5287b): paired pinned анализ, N=40 primaries, budget 240,
                        mechanical rule §9.2/9.3, feasibility gate §12,
                        exclusion 34, deviation classes §9.4 — refresh PASS
                        c25bcd6 с M-2 PARTIAL + R-1..R-5
candidate R3 (этот)   : SELECTED_N=64 declared grid, N-contract generator
                        (148 fresh seeds), tree-collision continuation rule,
                        consistency gate, accept-risk обход запрещён
```
