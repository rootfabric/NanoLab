# PREREGISTRATION_FREEZE_R1 — WO-NL5-002-E-R1 (PLATFORM-SENSITIVITY-R1)

Дата freeze (UTC): 2026-09-20 (authoritative `date -u` при записи). Роль: DIRECTOR.
Статус: **PLATFORM_SENSITIVITY_PROTOCOL = FROZEN** (preregistration content frozen;
Review PASS + Verify PASS получены ДО любых данных кампании).

## Exact frozen subject

```text
WO DOCUMENT            = docs/work/WO-NL5-002-E-R1.md
WO HEAD (freeze commit)= 4d6542fda81084dced2578f3e008c8c8e0705a5a
WO TREE                = 7651569ac8d0e93c0cc7614cb692945ad5bd0c98
BRANCH                 = control/nl5-002-terminal-decision-r1 (PR #44)
```

## Gates (до freeze; обе fresh-сессии, обе опубликованы в origin)

```text
FRESH SCIENTIFIC REVIEWER = PASS
  review/nl5-002-e-preregistration-r1 @ 1f8c063e6c620ec6f8caa804954bf861eb76f13d
  (parent = WO HEAD; evidence: docs/evidence/NL5-002-E/FRESH_PREREGISTRATION_REVIEW_R1.md;
   checklist 1–12 PASS; decision-rule partition proof: SENSITIVE ∧ INSENSITIVE = ∅;
   INCONCLUSIVE ⟺ CI excludes 0 ∧ 0.5 ≤ ratio < 1; WO-level aggregation total)

FRESH VERIFIER = PASS (другая fresh-сессия; вердикт review не наследовался)
  verify/nl5-002-e-preregistration-r1 @ bd25baf325987656eddd8a5b2ab36065f0170d5c
  (parent = WO HEAD; evidence: docs/evidence/NL5-002-E/FRESH_PREREGISTRATION_VERIFY_R1.md;
   seeds/protocol/pins/budget/statistics/no-post-data — 9/9 independent recomputations;
   subject binding: REVIEWED vs VERIFIED = match)
```

## Frozen seed list (S001–S010; идентичен на всех платформах — paired design)

```text
S001 = 1259289227   S006 = 972234272
S002 = 1358106528   S007 = 1934775205
S003 = 1524307444   S008 = 1747973984
S004 = 601855227    S009 = 880427736
S005 = 274288237    S010 = 744386736
```

Verifier: 10/10 distinct, positive int32; пересечения с reference {201004, 202008,
203012}, B-R1, B-R2 (12 значений), E3-reval {204016, 205020, 206024} и прочими
найденными в evidence seed-наборами (полное объединение 33 значений) — EMPTY;
whole-tree literal search: каждый seed встречается только в WO-файле.

## Frozen statistical plan (кратко; authoritative текст — WO §«Frozen статистический план»)

```text
primary paired statistic : shift_v = median_i( median[P2, seed_i] − median[P1, seed_i] ), v ∈ {0b, 32b}
CI                       : percentile bootstrap, 10 000 resamples, RNG seed 902107 (frozen)
effect size              : ratio_v = |shift_v| / within_v; within_v = median по платформам
                           (MAD per-seed median внутри платформы)
decision rule (variant)  : PLATFORM_SENSITIVE    — CI excludes 0 AND ratio ≥ 1
                           PLATFORM_INSENSITIVE  — CI contains 0 OR ratio < 0.5
                           иначе INCONCLUSIVE
WO-level                 : 0b и 32b оба SENSITIVE → PLATFORM_SENSITIVE; оба INSENSITIVE →
                           PLATFORM_INSENSITIVE; иначе INCONCLUSIVE
controls                 : 11b/53b — analysis-only, на WO-level вердикт не влияют
pre-data passport pins   : MAD-конвенция (raw vs ×1.4826), bootstrap RNG implementation
                           и within_v = 0 degenerate case фиксируются в паспорте
                           EX-NL5-002-E-R1 на START ДО данных (binding condition Verifier)
```

## Package / protocol pins

```text
package        = nanolab-components 0.1.1 (releases/nanolab-components-v0.1.1/,
                 VERSION = 0.1.1; RELEASE_MANIFEST.json sha256
                 88c1f58061f15fde44225900f0577acbf2634d3f4a75fb96a2cedca24fd1bfef)
                 (0.1.2 — только отдельным bounded owner-решением; science byte-identical)
convention     = convention/analyze_hinge.py (packaged, та же, что R1)
protocol refs  = WO-NL5-002-A-R1 + NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE (не меняются)
windows        = 0b: 200k шагов; 32b: 150k шагов; 74b — ЗАПРЕЩЁН
budget         = 40 primary runs (n=10 × 2 platforms × 2 primary variants); P3 optional +20;
                 CPU-only, no paid compute; wall ≤ 72 ч/платформа
```

## Platform definitions (frozen)

```text
P1 = author/reference environment — WSL2 Ubuntu 24.04.2, kernel microsoft-standard-WSL2,
     i9-13900H, gcc 13.3.0 (ENGINE_ENVIRONMENT_R1)
P2 = external environment — Ubuntu 22.04.5, gcc 11.4.0, Xeon E5-2698 v3 (платформа B-R2;
     host outenemy)
P3 = optional третья независимая Linux/compiler/runtime среда
Environment fingerprint каждой платформы фиксируется до её прогонов.
```

## Dispatch decision (mission §16)

```text
Reviewer PASS                          = да
Verifier PASS                          = да
resource budget within CPU/no-paid     = да (40 runs CPU-only на node 64 threads)
P2 available                           = да (outenemy = точная платформа B-R2)
P1 available                           = НЕТ: авторская среда — WSL2-хост владельца
                                         (i9-13900H laptop), из исполнительной среды
                                         недоступна (нет network route/credentials;
                                         host outenemy ≠ WSL2-хост, uname 5.15.0-190-generic)
P3                                     = отсутствует (optional, не блокирует P1/P2)
```

**STOP условия §16 выполнены частично → DISPATCH = NOT STARTED:**
прогоны кампании не запускаются до доступности P1. Это честная остановка, а не
BLOCKED по науке: preregistration полностью заморожен и готов к paired dispatch.

```text
PLATFORM_EXECUTION = NOT_STARTED / BLOCKED_ON_P1_AVAILABILITY
resume condition   : владелец предоставляет доступ к P1 (WSL2 author environment) —
                     тогда dispatch строго по frozen WO (seeds/statistics/budget
                     без изменений) либо явно новая revision WO
запрещено          : подмена P1 другой средой (научно нечестный pairing),
                     запуск «половинной» кампании только на P2 с paired-интерпретацией
```

## Иммутабельность

R1 (B-R1 INCONCLUSIVE + PORTABILITY_FINDING; B-R2 WO-level MISMATCH) не
пересматривается; NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE не меняется; NL5 acceptance
policy — отдельное owner-решение (open decision NL5-ACCEPTANCE-POLICY); NL6-001/E5
остаются LOCKED. Любое изменение statistical plan/seeds/platforms после данных —
запрещено; правки = новая revision WO (preregistration заново).
