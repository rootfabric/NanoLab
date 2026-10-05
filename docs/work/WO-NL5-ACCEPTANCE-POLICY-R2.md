# Work Order WO-NL5-ACCEPTANCE-POLICY-R2 — Candidate reproduction rule v0.2 + HG-B package

Статус: **IN_PROGRESS** (execution `EX-NL5-ACCEPTANCE-POLICY-R2`, ветка
`control/nl5-acceptance-policy-r2`, base `8205781def7179d6bdfa6eb7ab2a84d46776649c`).
Track: `NL5` control (open owner decision `NL5-ACCEPTANCE-POLICY`). Risk: **HIGH**
(acceptance-policy surface: затрагивает будущий scientific acceptance, но в этой
R1 **никакой protocol не freeze'ится и никаких данных не производится** —
подготовка proposal-пакета). Claim ceiling: **C0_SOFTWARE_ONLY** (документы +
deterministic seed-generation tooling; научных утверждений и прогонов нет).

Дата открытия: 2026-09-30. Trigger: central-agent mission 2026-09-30 (§19–§28):
owner-решение `NL5-ACCEPTANCE-POLICY` (открыто 2026-09-20,
`docs/evidence/NL5-002/DIRECTOR_DECISION_R1.md`) требует полностью готового
proposal, а не вопроса.

## 1. Границы scientific facts (НЕ меняются)

```text
NL5-001 = ACCEPTED (package 0.1.0; v0.1.1 bounded repair, science byte-identical)
NL5-002 = WAITING_HUMAN — terminal verified MISMATCH / NOT accepted (canonical 2026-09-20)
NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE = immutable (FROZEN before NL5-001-C data)
PLATFORM-SENSITIVITY-R1 = PLATFORM_INSENSITIVE, FULLY VERIFIED (frozen R1 study)
NL5 = IN_PROGRESS; external_reproductions = 0; NL6-001 = LOCKED
```

Запрещено этим WO: пересматривать/расширять v0.1 envelopes, двигать thresholds,
переклассифицировать old MISMATCH, объявлять NL5 ACCEPTED, открывать NL6-001,
запускать любые simulations, менять `project/state.json`.

## 2. Цель

Подготовить **pre-data** candidate-пакет для HG-B (owner decision):

1. `docs/control/NL5_ACCEPTANCE_PRINCIPLE_HG_B_PROPOSAL_R1.md` — полное
   предложение владельцу: принцип «NL5 acceptance requires successful fresh
   external reproduction under preregistered v0.2 distribution-based rule»,
   alternatives, что approval разрешает/не разрешает.
2. `docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md` — candidate protocol
   v0.2 (status **CANDIDATE / PRE-DATA / NOT FROZEN**): scientific question,
   hypotheses, platform definitions, variants, fresh seeds (deterministic
   generation, frozen exclusion list), N, observables, distribution metrics,
   decision rule с frozen vocabulary, technical failure policy, budget,
   stop conditions; явное разделение technical / numerical / distributional
   reproducibility / scientific consistency; historical R1 data используются
   ТОЛЬКО для power/budget planning (appendix), не как thresholds.
3. `scripts/nl5/repro_v02_seeds.py` — deterministic seed-generation tool:
   sha256-цепочка от protocol anchor, positive int32, uniqueness, frozen
   exclusion list (все известные R1 confirmatory seeds), record JSON с
   digest; tool НЕ генерирует «удобные» seeds — алгоритм зафиксирован и
   тестируется на детерминизм.
4. `tests/test_nl5_repro_v02_seeds.py` — тесты детерминизма/уникальности/
   exclusions.

## 3. Freeze chain (ЧЕСТНО: в этом WO не выполняется)

```text
candidate (этот WO)
  → HG-B: owner утверждает принцип (и, при желании, candidate как basis)
  → Director freeze record (protocol + seeds + analyzer pin, отдельный WO/commit)
  → fresh scientific Reviewer + fresh Verifier FROZEN protocol
  → и только потом: R2 ACTIVE (отдельная точка) → author leg EX-NL5-REPRO-V0-2-U1-R1
```

Никакой элемент freeze-цепочки не исполняется этой R1. Candidate может быть
изменён владельцем/Reviewer ДО freeze без нарушения protocol integrity —
после freeze изменения только через новую revision.

## 4. Decision-rule принципы (проверяются Reviewer особо)

- Equivalence margin фиксируется **a priori** по стандартной конвенции
  (стандартизованный эффект 0.5 pooled within-platform SD, граница «medium
  effect» в equivalence-практике), а НЕ подбором под observed R1 shifts.
- Historical values (P1/P2 shifts, envelopes, medians) — только в appendix
  power/budget planning.
- Frozen vocabulary исходов: `REPRODUCED | REPRODUCED_WITH_DEVIATION |
  INCONCLUSIVE | FAILED_TECHNICAL | MISMATCH`.
- Technical failure ≠ scientific mismatch; budget abort ≠ mismatch.

## 5. Allowed paths

```text
docs/work/WO-NL5-ACCEPTANCE-POLICY-R2.md
docs/work/executions/EX-NL5-ACCEPTANCE-POLICY-R2/**
docs/control/NL5_ACCEPTANCE_PRINCIPLE_HG_B_PROPOSAL_R1.md
docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
scripts/nl5/**
tests/test_nl5_repro_v02_seeds.py
docs/work/WORK_QUEUE.md   (только sync-предложение в NL5-002 строке)
```

## 6. Required outputs и приёмка

Passport + events (START → CONTINUATION → VALIDATION → HANDOFF) + summary;
валидации: pytest (полный набор), check-consistency, workflow lint, work_cli
validate; fresh Reviewer + fresh Verifier на exact HEAD; merge = Human Gate
(сам HG-B — отдельное owner-решение вне Git-мержа).

## 7. Owner decision closure — HG-B R1 (append-only, 2026-10-05)

Append-only дополнение: §1–§6 выше не изменяются. Цель этого WO — candidate
acceptance-policy preparation + HG-B owner decision — **исполнена и закрыта**:

```text
HG-B CLOSED = APPROVED
next work is a NEW freeze execution

DECISION_ID     = NL5-ACCEPTANCE-POLICY/HG-B/R1
decision record = docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.{md,json}
decision basis  = canonical main после PR #50 (3b0dd01e; R4.3 product subject
                  39cc9809ad4b9ad61b2effd6dbcb8c9067848da0)
execution event = EX-NL5-ACCEPTANCE-POLICY-R2 event
                  0008-continuation-hg-b-owner-decision
```

Статусная механика: существующая harness schema не содержит отдельного
terminal-статуса «COMPLETED / ACCEPTED_CONTROL_DECISION», новый status enum не
изобретался — execution остаётся в допустимом состоянии HANDOFF_READY с
append-only post-terminal correction event 0008 (CONTINUATION_CHECKPOINT), а
эта секция + decision record + WORK_QUEUE являются canonical truth о закрытии.
Reproduction НЕ исполнялся этим WO: freeze chain (Director freeze → fresh
review/verify FROZEN → R2 ACTIVE → author/external legs) — отдельные новые
work orders. Границы неизменны: NL5 = IN_PROGRESS, external_reproductions = 0,
NL6-001 = LOCKED, научных прогонов 0.
