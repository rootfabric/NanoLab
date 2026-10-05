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

## 5. Errata / repair R1 (post review FAIL f07fe39)

Fresh scientific review вернул **FAIL** (3 MAJOR + 4 MINOR) — candidate-протокол
не был готов к freeze. Candidate переведён в **revision R2** (текст переписан,
R1 сохранён в git history @ 3171564; по-прежнему PRE-DATA / NOT FROZEN):

1. M-1: exclusion list 19 → **34** (B-R1 + B-R2 seeds добавлены, верифицированы
   по evidence); seed-потоки не изменились (digest прежний).
2. M-2: primary statistic — **paired per-seed differences**; bootstrap pinned
   (PAIRED, B=10 000, RNG mechanical); N primaries **40**/cell (MC review на
   реальных R1 данных: n=10 при δ=0.5 давало гарантированный INCONCLUSIVE);
   budget 200+40=240 runs; **mandatory feasibility gate** до dispatch.
3. M-3: decision rule полностью механический (§9.2/§9.3, приоритеты; controls
   противоречие устранено; s_floor 0.01°; замкнутый список deviation classes).
4. m-1..m-4: окна разведены, регенерация вписана в протокол, R2-gate обеих ног
   явный, тесты doc-consistency обновлены.

Тесты: 14 seed-tool / 388 full, зелёные. Reviewer refresh + fresh Verifier —
следующие шаги; событие 0005 (CONTINUATION_CHECKPOINT, post-terminal
corrections class).

## 6. Errata / repair R3 (central closure mission)

Candidate переведён в **revision R3** (control/nl5-acceptance-policy-r3,
substantive head bc83af2):

1. **N-contract**: generator выдаёт ровно протокольные cardinalities —
   после declared N-grid search SELECTED_N = 64: streams 0b 64 / 32b 64 /
   11b 10 / 53b 10 = **148 fresh identities** (R1/R2 дефект «10 при
   требуемых 40/64» устранён machine-контрактом PRIMARY_REPLICAS/
   CONTROL_REPLICAS/VARIANT_REPLICAS + consistency gate).
2. **Declared N-grid**: {40,48,64,80,96,128}, headroom 0.80, правило
   зафиксировано ДО вычислений; SELECTED_N = 64 (полный grid — evidence).
3. **Mandatory gate FAIL ⇒ BLOCKED**; «accept risk» обход запрещён.
4. **Whole-tree collision scan**: deterministic continuation rule,
   skips recorded; freeze-time scan excludes seed-record/protocol paths.
5. **Consistency gate**: protocol N == record N == budget N == N_min
   (scripts/nl5/repro_v02_freeze_gate.py + тесты PASS/FAIL).
6. Budget: 296 + 60 = max 356 runs; wall ≤ 560 ч/платформа.

Тесты: 25 seed-tool / 399 full. Seed record R3: digest
eb4ab3f891e17dd2b456a3870ed73b19e39d67bf51109b6cb47ca64524ce476b.

## 7. Errata / repair R3.1 (post review R3 PASS 846a5a2)

MINOR-1: литералы «100 fresh» → «148 fresh» (§7 cardinality, Appendix B).
MINOR-3: добавлены mission-обязательные тесты (N-grid constant + deterministic,
selected-N deterministic 64, headroom 0.80 boundary semantics) — 29 seed-tool /
403 full зелёные. MINOR-2 (bootstrap literals R1/R2-эры) — принят как
задокументированный (буква контракта цела; влияние pre-data нулевое). NOTE
для владельца: reviewer MC на N=64 — P(REPRODUCED | идеальная эквивалентность)
≈ 6% WO-level (INCONCLUSIVE — вероятный исход; осознанный tradeoff headroom-
дизайна; ревизии headroom/N — через owner до freeze).

## 8. HG-B owner decision closure (2026-10-05, append-only post-terminal)

Владелец вынес решение **HG-B = APPROVED** (Human Gate B, event 0008). Это —
закрытие owner-decision цели этого execution (candidate acceptance-policy
preparation + HG-B owner decision); подготовка freeze — НОВЫЙ execution/WO.

```text
HG-B CLOSED = APPROVED
next work is a NEW freeze execution

DECISION_ID        = NL5-ACCEPTANCE-POLICY/HG-B/R1
decision record    = docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.{md,json}
decision basis     = canonical main после PR #50 (merge 3b0dd01e, tree 10ba8bbf;
                     R4.3 product subject 39cc9809ad4b9ad61b2effd6dbcb8c9067848da0)
approved principle = NL5 acceptance requires successful fresh external
                     reproduction under preregistered v0.2 distribution-based rule
approved rule      = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL (R4 / post-R4.3 basis)
approved params    = δ=0.5; N 64/64/10/10; N_min 52/52/8/8; replacement quota
                     pairs 12/12/2/2; confirmatory 296; replacement cap 56;
                     max_runs 352; paired TOST; integer policy
                     ceil-nmin-floor-replacement-pairs-v1; wall 560 ч/платформа
```

Границы (не завышены): freeze НЕ выполнялся; SCIENTIFIC_RUNS = 0; candidate =
PRE-DATA / NOT FROZEN; committed package по-прежнему
PREFREEZE_VALIDATION_PASS / DISPATCH_BLOCKED (negative control перепроверен
2026-10-05, evidence `r4-3-prefreeze-validation-PASS-R4_3.json` digests
неизменны); AUTHOR_U1 = NOT_ASSIGNED; R2 = WAITING_HOST / NOT_ACTIVE; NL5 =
IN_PROGRESS; external_reproductions = 0; NL6-001 = LOCKED. Passport
allowed_paths расширен на `docs/evidence/NL5-ACCEPTANCE-POLICY/**` (placement
owner decision record по owner mission; статус паспорта не менялся —
HANDOFF_READY остаётся валидным terminal-handoff состоянием; новый status enum
не изобретался). Dormant-ветка `repair/nl5-acceptance-policy-r4-power-gate-r1`
= INSPECTED / NOT_MERGED / SUPERSEDED для HG-B (обоснование — §8 decision
record: admin-only, concern уже задокументирован в §7 выше, изменение
утверждённых параметров требует нового owner package). NEXT: Director Freeze
preparation (отдельный WO) → FROZEN PACKAGE COMMIT F → fresh review/verify F;
параллельно R2 activation (HG-A). Не путать: HG-B approval НЕ означает NL5
ACCEPTED.
