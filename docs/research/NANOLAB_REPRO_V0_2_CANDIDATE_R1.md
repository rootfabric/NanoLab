# NANOLAB_REPRO_V0_2_CANDIDATE_R1 — Candidate distribution-based reproduction rule

Статус: **CANDIDATE / PRE-DATA / NOT FROZEN**.

```text
rule_id (candidate) = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL
подготовлен          = WO-NL5-ACCEPTANCE-POLICY-R2 (EX-NL5-ACCEPTANCE-POLICY-R2)
базовый main         = 8205781def7179d6bdfa6eb7ab2a84d46776649c
date                 = 2026-09-30
freeze status        = NOT FROZEN — freeze отдельной Director-записью ТОЛЬКО после
                       HG-B (owner approval принципа), до любых confirmatory data
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
ограничения: (а) envelope из 3 реплик — крайне узкая эмпирическая полоса,
высокочувствительная к единичным отклонениям; (б) правило не различает
«платформенный сдвиг меньше собственной вариативности» от «совпадение точка-в-
точку»; (в) INCONCLUSIVE-область велика. Platform-sensitivity study
(WO-NL5-002-E-R1, PLATFORM_INSENSITIVE, frozen R1) подтвердил: paired shifts
между платформами малы относительно разброса, но точечные envelope-правила это
выражают плохо. v0.2 — **distribution-based** правило: equivalence платформенных
распределений, а не совпадение точечных статистик.

## 2. Разделение видов reproducibility (не смешивать)

```text
technical reproducibility      — тот же package/engine на той же платформе:
                                 exit=0, integrity gates, digest-совпадение входов,
                                 завершённые траектории (ЕСЛИ оно сломано — это
                                 FAILED_TECHNICAL, не MISMATCH)
numerical reproducibility      — побитовая/около-побитовая повторяемость траекторий
                                 на идентичной среде (изучалось NL2-002/NL5-002-E
                                 raw replay; здесь НЕ является критерием)
distributional reproducibility — ЭТОТ протокол: equivalence распределений
                                 наблюдаемых между author- и external-платформами
                                 при fresh seeds
scientific consistency         — согласие с ранее принятыми качественными выводами
                                 карточек (order-of-magnitude, направление эффектов);
                                 отдельная поверхность acceptance, здесь не гейтится
```

Package может быть технически воспроизводимым при статистической вариативности —
v0.2 оценивает именно distributional слой.

## 3. Scientific question

> Воспроизводится ли распределение per-replica median hinge angle опубликованных
> вариантов dna_hinge (0b, 32b primary; 11b, 53b controls) на независимой
> external-платформе (U2) относительно author-платформы (U1) эквивалентно —
> то есть так, что межплатформенный сдвиг мал относительно собственной
> внутриплатформенной вариативности свежих реплик?

## 4. Hypotheses (для каждого primary варианта v ∈ {0b, 32b})

```text
H0(v): |Δ_v| < δ·s_v , где Δ_v = median_external(v) − median_author(v),
       s_v = pooled within-platform SD(n−1) fresh replica medians,
       δ = 0.5 (fixed a priori; см. §9 — выбор конвенциональный, не под R1 data)
H1(v): |Δ_v| ≥ δ·s_v
```

Статистическое решение — TOST-эквивалентность (§9): H0 эквивалентности
принимается, если 90% CI(Δ_v) целиком внутри (−δ·s_v, +δ·s_v).

## 5. Platform definitions

```text
P-A (author)    = AUTHOR_U1, native Ubuntu R2, fingerprint frozen в
                  ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md §10 до кампании
P-B (external)  = U2 outenemy, независимая external сессия из release package +
                  frozen WO + pinned source acquisition; workspace НЕ копируется
                  из author; свежий fingerprint фиксируется отдельно (§mission 33)
исключено       = Windows/WSL2 (WINDOWS_ALLOWED_FOR_NEW_SCIENCE = NO)
требование      = P-A ≠ P-B физически; у P-B своя build-цепочка по контракту R2 §5
```

Экзотические расхождения toolchain (gcc line, cmake version) НЕ являются
automatic failure: их допускает сам принцип distribution-based equivalence
(это и проверяется). Fingerprint'ы обеих платформ входят в evidence.

## 6. Variants

```text
primary = 0b, 32b   (гейтовые варианты; как в frozen WO-NL5-002-E-R1)
controls = 11b, 53b (репортятся той же статистикой; НЕ гейтят verdict §10)
74b     = NOT_MEASURED / KNOWN_GAP — исключён до отдельного arm-manifest-v2
          repair WO; значения 74b запрещены
```

Budget-приоритет при ограничениях: primaries всегда; controls могут быть
исключены только ДО freeze (в этом candidate они включены).

## 7. Fresh seeds (никакого повторного использования R1 confirmatory seeds)

Generation (deterministic, до данных):

```text
anchor   = "NANOLAB-REPRO-V0.2-R1" (фиксируется Director freeze record'ом)
seed(v, i) = int.from_bytes(sha256(f"{anchor}|{v}|replica-{i:04d}").digest()[:4], "big")
             & 0x7FFFFFFF  → positive int32
i ∈ {1..10} на (variant, platform); пары seed-множество ИДЕНТИЧНО на обеих
платформах (paired design, как в frozen WO-NL5-002-E-R1);
bootstrap seeds = аналогично с label "bootstrap-{v}" (10 000 resamples)
```

Frozen exclusion list (генератор ОТКАЗЫВАЕТСЯ выдавать запись с коллизией;
тестами): все известные R1 confirmatory seeds — E1 {-200619630, 319832093};
E2 reference {201004, 202008, 203012}; E3-reval {204016, 205020, 206024};
platform study S001–S010 {1259289227, 1358106528, 1524307444, 601855227,
274288237, 972234272, 1934775205, 1747973984, 880427736, 744386736}; bootstrap
902107. На момент Director freeze — повтор whole-tree literal search (каждый
fresh seed не встречается в evidence-дереве; прецедент: verifier platform study).

## 8. N и replicas

```text
N = 10 fresh replicas на (variant, platform) для всех 4 вариантов
    (= парный дизайн platform study: n=10 × 2 variants × 2 platforms исполнен
    на CPU; 4 варианта удваивают объём — budget §12 учитывает это честно)
N_min = 8 валидных replica medians на ячейку, иначе ячейка INCONCLUSIVE
replacement allowance = 20% на ячейку, ТОЛЬКО для FAILED_TECHNICAL
    (новые attempt id, старые попытки сохраняются, логи обязательны)
```

## 9. Observables, metrics, decision rule

Observable — без изменений frozen convention: per-replica `median_deg`
валидных кадров в тех же measurement windows (0b = 200k шагов, 11b/32b/53b =
150k шагов; те же frame-validity gates), считанный **упакованной конвенцией**
`analyze_hinge.py` из release package. Convention НЕ заменяется и не
параметризуется заново.

Metrics (по каждому variant):

```text
Δ̂        = median_B − median_A               (median по replica medians платформы)
s        = pooled within-platform SD(n−1)     (primary scale; MAD как robustness-check)
d        = Δ̂ / s                              (standardized effect)
CI90(Δ)  = percentile bootstrap, 10 000 resamples, frozen bootstrap seed
overlap  = overlap coefficient эмпирических распределений (descriptive)
```

Decision rule (mechanical, frozen до данных):

```text
equivalence margin = ±δ·s, δ = 0.5
эквивалентность v     : CI90(Δ_v) ⊂ (−δ·s_v, +δ·s_v)      (TOST, alpha=0.05)
не-эквивалентность v  : |d_v| ≥ δ И CI90(Δ_v) не накрывает −δ·s_v..+δ·s_v полностью
                        снаружи (значимо вне полосы)
```

WO-level verdict (frozen vocabulary):

```text
REPRODUCED                  = обе primaries эквивалентны; controls без gross failure
REPRODUCED_WITH_DEVIATION   = то же, но с задокументированными non-scientific
                              deviations исполнения (build/tooling/environment),
                              не меняющими observable/convention/seeds
MISMATCH                    = хотя бы одна primary значимо не-эквивалентна
INCONCLUSIVE                = ни эквивалентность, ни не-эквивалентность не показаны
                              (или < N_min валидных реплик в любой primary ячейке)
FAILED_TECHNICAL            = кампания не завершена технически (бюджет/среда/engine);
                              НЕ является MISMATCH
```

Controls: statistics репортятся; gross control failure (|d| ≥ 1.0 на control)
требует investigation-note в analysis, но НЕ меняет verdict (пре-объявлено,
чтобы не возникало соблазна post-hoc расширения). 74b не производится.

## 10. Запреты (protocol integrity)

- Не подбирать δ, окна, seeds, N, статистику после просмотра данных (любое
  изменение = новая revision + новый freeze + новая кампания).
- Не использовать v0.1 envelopes/medians как acceptance thresholds (исторические
  значения — только appendix power/budget planning).
- Не считать exit 0 научным PASS; не превращать FAILED_TECHNICAL в MISMATCH.
- Не переписывать NL5-002 terminal MISMATCH и PLATFORM_INSENSITIVE (frozen R1).
- Не производить 74b.

## 11. Technical failure policy

Replica FAILED_TECHNICAL: engine exit ≠ 0, неполная траектория, невалидные
кадры сверх frozen gates, digest mismatch входов. Retry — новый attempt id
(`-R1`, `-R2`, …), append-only ledger; replacement в пределах 20% allowance.
Ячейка с систематическими technical failures (≥ 3 подряд FAILED_TECHNICAL)
останавливается → честная классификация, не «подгонка» (прецедент
WO-NL5-002-E-R1 budget discipline).

## 12. Budget и stop conditions (pre-declared)

```text
runs              = 4 variants × 10 replicas × 2 platforms = 80 confirmatory
                    + ≤ 16 replacements (20%) = ≤ 96 total
compute           = CPU-only, paid compute FORBIDDEN (без отдельной owner-
                    авторизации; mission §49)
calibration       = из R1 операционных данных: 0b 200k ≈ 10–14 ч single-thread,
                    32b 150k аналогично (WO-NL5-002-E-R1); intra-node parallelism
                    как в platform study
wall budget       = ≤ 168 ч на платформу (7 суток); превышение → STOP /
                    BUDGET_EXCEEDED, не расширять автоматически
stop conditions   = environment недоступна → BLOCKED_ENVIRONMENT; ≥ 3 подряд
                    FAILED_TECHNICAL в ячейке → ячейка остановлена; любое
                    требование изменить protocol после data → STOP + новый WO;
                    R2 NOT ACTIVE на момент старта author leg → кампания не
                    стартует (HARD_BLOCKED)
```

## 13. Freeze chain (после HG-B, отдельными записями)

```text
HG-B APPROVED (owner)
  → Director FREEZE record: protocol text (этот документ с любыми owner-
    поправками), seed record (сгенерирован tools/nl5, digest), analyzer pin
    (package version + convention digest), N, budget
  → fresh scientific Reviewer + fresh exact-head Verifier FROZEN protocol
  → prerequisite: R2 ACTIVE (gates U1–U5, NC-U1..U5, review/verify, Human Gate)
  → author leg  = EX-NL5-REPRO-V0-2-U1-R1 (на U1 через native executor)
  → external leg = EX-NL5-REPRO-V0-2-U2-R1 (на U2 из release package)
  → independent analysis + Scientific Reviewer + Verifier → NL5 decision
```

## Appendix A — Historical data used ONLY for power/budget planning

Не thresholds. Из frozen R1: platform study 0b shift +0.685° CI95
[−0.550, +1.199], 32b shift −1.207° CI95 [−2.090, +2.149]; n=10/ячейка
исполнимо в wall ≤ 72 ч на платформу для 2×2 дизайна; E2 confirmatory 0b
pooled median 65.98° [65.67, 66.32] (SD межрепличный ~0.017° в E1
масштабах/до °1.5 в E2 масштабах — межрепличный разброс E2 значителен, что и
мотивирует distribution-based правило). Ожидаемая power: при n=10 и
внутриплатформенной SD порядка наблюдавшейся в platform study, CI90 ширины
~1.2·s позволяют разрешать d ≥ ~0.5 — margin согласован с budget, но
переоценивается на пилоте E5-B-класса при необходимости (до freeze — не после).

## Appendix B — Отличия от v0.1 (для Reviewer)

| аспект | v0.1 (immutable) | v0.2 (candidate) |
|---|---|---|
| единица | 3 replica medians, envelope [min,max] | 10 fresh replicas/платформа, парные seed-множества |
| статистика | point-in-envelope + directional separation | TOST equivalence на Δ с margin δ·s + bootstrap CI90 |
| margin | нет (эмпирический envelope) | δ = 0.5 pooled SD, a priori, конвенциональный |
| платформы | любая external | P-A = U1 (R2 ACTIVE), P-B = U2; Windows исключён |
| outcomes | MATCH/MISMATCH/INCONCLUSIVE | + REPRODUCED / REPRODUCED_WITH_DEVIATION / FAILED_TECHNICAL |
| technical failure | отдельно от scientific | явно: FAILED_TECHNICAL ≠ MISMATCH, replacement policy |
| 74b | NOT_MEASURED | NOT_MEASURED (без изменений) |
