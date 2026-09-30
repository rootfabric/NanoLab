# EX-NL5-ACCEPTANCE-POLICY-R2 — Summary

```text
execution_id = EX-NL5-ACCEPTANCE-POLICY-R2
work_order   = WO-NL5-ACCEPTANCE-POLICY-R2 (open owner decision NL5-ACCEPTANCE-POLICY)
branch       = control/nl5-acceptance-policy-r2
base         = 8205781def7179d6bdfa6eb7ab2a84d46776649c (origin/main)
substantive_head = ee40984a9a6a08c4d3c6182b5ba400a365bf59e5
risk / claim = HIGH / C0_SOFTWARE_ONLY (proposal package; protocol NOT frozen; no science)
status       = HANDOFF_READY (fresh Reviewer + fresh Verifier -> Human Gate merge;
               HG-B — отдельное owner-решение вне Git)
```

## 1. Что сделано

1. **Candidate protocol** `docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md`
   (`NANOLAB_REPRO_V0_2_DISTRIBUTIONAL`, статус CANDIDATE / PRE-DATA /
   NOT FROZEN): distribution-based equivalence вместо узкого точечного
   envelope v0.1; TOST-эквивалентность Δ median'ов с margin ±0.5 pooled
   within-platform SD (δ a priori по конвенции, не под R1 data); fresh paired
   seeds (deterministic sha256, positive int32, exclusion list 19 исторических
   R1 seeds); N=10/ячейка (N_min 8; replacement 20% FAILED_TECHNICAL only);
   0b/32b primary, 11b/53b controls (74b исключён); observables — frozen
   convention без изменений; frozen vocabulary `REPRODUCED |
   REPRODUCED_WITH_DEVIATION | INCONCLUSIVE | FAILED_TECHNICAL | MISMATCH`;
   явное разделение technical/numerical/distributional/scientific-consistency;
   budget 80+16 runs CPU-only, wall ≤168ч/платформа, STOP/BUDGET_EXCEEDED;
   исторические значения — только appendix power/budget planning.
2. **HG-B proposal** `docs/control/NL5_ACCEPTANCE_PRINCIPLE_HG_B_PROPOSAL_R1.md`
   — принцип «NL5 acceptance requires successful fresh external reproduction
   under preregistered v0.2 distribution-based rule»; что approval разрешает /
   НЕ разрешает; альтернативы; однострочный формат ответа владельца.
3. **Seed tooling** `scripts/nl5/repro_v02_seeds.py` + 13 тестов:
   детерминизм, positive int32, глобальная уникальность, refusal при коллизии
   с историческими seeds, digest stability, doc↔tool consistency.
4. **Pre-data seed record** (evidence):
   `record_sha256 = 5c95664485e00069379e962f44b3ba247f00030e02a7375a27d3b4ab441f5a9c`
   (при freeze регенерируется и сверяется).
5. **Surface sync**: WORK_QUEUE NL5-002 append (package подготовлен; freeze
   только после HG-B; runs по-прежнему HARD_BLOCKED до R2 ACTIVE).

## 2. Чего НЕ сделано (честно)

- Ничего не freeze'ится: freeze = отдельная Director-запись после HG-B, затем
  fresh scientific Reviewer + Verifier FROZEN protocol.
- Никаких simulations/physics; никаких новых scientific runs (HARD_BLOCKED
  до R2 ACTIVE); `project/state.json` не изменён; NL5-002 terminal MISMATCH,
  v0.1 envelope, PLATFORM_INSENSITIVE не тронуты; NL6-001 LOCKED.
- R2 не активирован (машина U1 не выделена) — author leg невозможен независимо
  от HG-B до активации R2.

## 3. Валидация

- `pytest tests/ -q` → 387 passed (374 + 13).
- `check-consistency` → ok:true; `workflow_lint` → blocking=0;
  `work_cli validate` → ok:true.

## 4. NEXT_ACTION

Fresh Reviewer + fresh Verifier на exact HEAD → Human Gate merge этой ветки →
владельцу: **HG-B** (формат ответа — proposal §7). Параллельно HG-A: выделение
U1 → механическая активация R2 tooling'ом EX-INFRA3-NATIVE-UBUNTU-R2-R1.
