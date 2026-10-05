# HG_B_OWNER_DECISION_R1 — Human Gate B owner decision record (immutable, append-only)

```text
DECISION_ID         = NL5-ACCEPTANCE-POLICY/HG-B/R1
OWNER_DECISION      = APPROVED
DECISION_CLASS      = HUMAN_GATE_B

CANONICAL_MAIN_HEAD = 3b0dd01e17e374c011007c6b0cdbbb5703bf2360
CANONICAL_MAIN_TREE = 10ba8bbffcae06ae7fad7135b2493494b0d4f9b1

R4_3_PRODUCT_SUBJECT = 39cc9809ad4b9ad61b2effd6dbcb8c9067848da0
R4_3_PRODUCT_TREE    = 10ba8bbffcae06ae7fad7135b2493494b0d4f9b1

RECORDED_AT_UTC     = 2026-10-05T02:15:00Z (machine stamp момента записи;
                      само решение владельца дано в HG-B closure mission)
RECORDING_ROLE      = CONTROL / IMPLEMENTER session (durable Git record);
                      authority решения = HUMAN_GATE_OWNER (владелец)
MACHINE_RECORD      = docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.json
```

Этот файл — **durable Git-запись уже состоявшегося owner-решения**, а не новый
proposal и не новое обсуждение. История proposal (§1–§9 с addenda R4/R4.1)
сохранена без изменений; фиксация решения добавлена append-only разделом §10 в
`docs/control/NL5_ACCEPTANCE_PRINCIPLE_HG_B_PROPOSAL_R1.md`.

## 1. Решение

```text
HG-B: APPROVED
```

Утверждённый принцип (verbatim из proposal §2):

```text
NL5 acceptance requires successful fresh external reproduction
under preregistered v0.2 distribution-based rule.
```

## 2. Утверждённый protocol basis (pre-data, exact parameters)

```text
rule_id              = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL
candidate revision   = R4 / post-R4.3 hardened pre-freeze basis
                       (научные параметры R4; control-plane repairs R4.1–R4.3;
                        confirmed fresh Reviewer PASS + Verifier VERIFIED +
                        PR #50 merge; committed PRE-DATA package digests
                        неизменны с R4.2)

delta                = 0.5
design               = paired (fresh paired identities, paired per-seed
                       differences, standard TOST equivalence semantics)
integer policy       = ceil-nmin-floor-replacement-pairs-v1

N                    = 0b 64 | 32b 64 | 11b 10 | 53b 10
N_min                = 0b 52 | 32b 52 | 11b 8 | 53b 8
replacement quotas   = 0b 12 | 32b 12 | 11b 2 | 53b 2 (pairs)
confirmatory runs    = 296
replacement runs cap = 56
max_runs             = 352
wall hours/platform  = 560
```

## 3. Утверждённые защитные свойства (часть basis, не опции)

```text
- paired TOST                        = CI90 медианного парного сдвига целиком
                                       внутри pre-declared equivalence interval
                                       ±δ·s_eff; standard TOST H0/H1
- fresh deterministic identities     = sha256-цепочка от protocol anchor;
                                       исторические seeds в frozen exclusion
                                       list (34); никакой reuse
- replacement ТОЛЬКО FAILED_TECHNICAL = scientific outcome никогда не является
                                       основанием замены; one-shot pair-level
                                       ledger; attempt id уникальны
- frozen replacement streams         = pools 12/12/2/2 пар от pinned cursor
                                       75/76/21/21 (никогда raw N+1)
- collision-skip proof required      = machine-bound scan manifest на pinned
                                       immutable tree a9d7d07; каждый recorded
                                       skip доказуемо повторяем; fabricated
                                       skip => FREEZE_GATE_FAIL
- 74b excluded                       = 74b исключён из v0.2 reproduction rule;
                                       остаётся NOT_MEASURED / KNOWN_GAP
- mandatory feasibility gate         = FAIL => BLOCKED; обход «accept risk»
                                       запрещён
- machine preconditions dispatch     = HG-B = APPROVED (эта запись) является
                                       одним из обязательных machine-readable
                                       preconditions nanolab_v02_dispatch_
                                       authority schema v3 (lifecycle
                                       S -> F -> R/V -> A)
```

## 4. Границы решения (что HG-B НЕ делает)

```text
DOES NOT FREEZE PROTOCOL                    — freeze = отдельная Director-запись
DOES NOT ACTIVATE R2                        — HG-A отдельно (gates U1-U5 + NC-U1..U5)
DOES NOT ASSIGN AUTHOR_U1                   — реальный host не выделен
DOES NOT AUTHORIZE SCIENTIFIC RUNS          — runs = 0; launch = HUMAN_PROTECTED_WRITER
DOES NOT ACCEPT NL5                         — NL5 = IN_PROGRESS до frozen criterion
                                              выполнен + review/verify + HG-C
DOES NOT CHANGE NL5-002 v0.1 terminal MISMATCH — historical terminal immutable
DOES NOT CHANGE PLATFORM_INSENSITIVE finding — frozen R1 study immutable
DOES NOT UNLOCK NL6                         — NL6-001 = LOCKED
```

## 5. Decision basis (canonical state, проверен fresh fetch 2026-10-05)

```text
PR #50                 = MERGED; merge_commit = 3b0dd01e17e374c011007c6b0cdbbb5703bf2360
                         (product subject 39cc9809ad4b9ad61b2effd6dbcb8c9067848da0,
                          product tree 10ba8bbffcae06ae7fad7135b2493494b0d4f9b1)
fresh Reviewer         = PASS — REVIEWER_VERDICT_R4 (branch
                         review/nl5-v02-prefreeze-hardening-r4-3-r4,
                         evidence tip f564aa7ab4654043a3bbd0711a893427f5a0f2f2)
                         на exact R4.3 HEAD 39cc9809 / TREE 10ba8bbf
fresh Verifier         = VERIFIED — verify/nl5-v02-prefreeze-hardening-r4-3-r1
                         @ 4d14b34f8b91312a6c8d393840cb107974d0de10
Director readiness     = READY_FOR_HUMAN_GATE — DIRECTOR_READINESS_R1 (branch
                         control/nl5-v02-prefreeze-hardening-r4-3-director-
                         readiness-r1; verdict refs, не merged в main)
TR-PR hosted CI        = run 37242371055 attempt 2 = SUCCESS (head 39cc9809)
post-merge main CI     = run 37252078697 = SUCCESS (head 3b0dd01e)
decision delta         = HG-B proposal §8 (R4) + §9 (R4.1 dispatch authority);
                         научные параметры §2 этой записи им соответствуют
```

## 6. Состояние на момент решения (без завышения)

```text
scientific_runs_at_decision      = 0
candidate_status_at_decision     = PRE-DATA / NOT FROZEN
r2_status_at_decision            = WAITING_HOST / NOT_ACTIVE
nl5_status_at_decision           = IN_PROGRESS
external_reproductions_at_decision = 0
nl6_001_status_at_decision       = LOCKED
author_u1_at_decision            = NOT_ASSIGNED
pre-freeze gate                  = PREFREEZE_VALIDATION_PASS / DISPATCH_BLOCKED
                                   (committed package остаётся dispatch-blocked —
                                   обязательный negative control; проверено при
                                   записи, см. execution event EX-NL5-ACCEPTANCE-
                                   POLICY-R2 event 0008)
```

## 7. Binding этой записи при freeze (не self-declared)

Поля `source_commit` / `git_blob_sha1` / `canonical_sha256` для ЭТОЙ записи, как
и `FROZEN_PACKAGE_HEAD` / `reviewed_head` / `verified_head`, **сознательно не
присутствуют** в этой записи: они не могут быть честно известны до фактического
commit/freeze lifecycle. Binding создаётся позже отдельными authority-записями по schema v3
(`nanolab_v02_dispatch_authority`): Director freeze record свяжет эту запись как
exact immutable Git blob (source_commit/path/git_blob_sha1/canonical_sha256/
record_kind/issuer_class). HG-B-запись легально предшествует FROZEN PACKAGE
COMMIT F (binding-only, lifecycle S -> F -> R/V -> A).

## 8. Dormant branch note — repair/nl5-acceptance-policy-r4-power-gate-r1

Историческая dormant-ветка (tip `01d191402029bd628ed3cb27c5f4fa02b129af38`,
merge-base с main `290cba6e`) содержит только административные записи
(WO + passport + START) предложения **pre-data decision-power gate**
(дополнительный power-gate: P(EQUIVALENT | ideal equivalence planning model)
≥ 0.90 per primary / ≥ 0.80 WO-level при выборе N). Она НЕ merged и НЕ
cherry-picked. Статус идеи относительно этой записи:

```text
DORMANT_POWER_GATE_BRANCH = INSPECTED / NOT_MERGED / SUPERSEDED (для HG-B)
```

Обоснование: (а) implementation на ветке отсутствует — только WO/START;
(б) озабоченность power-gate (риск INCONCLUSIVE при N=64, reviewer Monte-Carlo
оценка P(REPRODUCED | идеальная эквивалентность) ≈ 6% WO-level) уже durably
задокументирована в canonical main (EX-NL5-ACCEPTANCE-POLICY-R2 summary §7
NOTE для владельца) и была осознанным tradeoff headroom-дизайна при выборе N=64;
(в) владелец утвердил exact параметры N=64/64/10/10 с этим знанием — введение
power-gate теперь изменило бы утверждённые pre-data параметры и потребовало бы
НОВОГО owner decision package, а не тихой интеграции; (г) power-gate не является
обязательной integrity-защитой: без него INCONCLUSIVE — честный, механически
обрабатываемый исход frozen rule (rule не подгоняется; готовится следующая
научно обоснованная revision). Путь остаётся доступным: ЛЮБЫЕ изменения
кандидата ДО freeze бесплатны для integrity, но после этой записи требуют новой
pre-data revision + повторного owner approval, т.к. параметры зафиксированы HG-B.
Обязательной отсутствующей защиты не обнаружено — STOP не требуется.

## 9. Что разблокировано и цепочка далее

```text
HG-B APPROVED (эта запись)
      ↓
Director Freeze preparation (отдельный bounded WO)
      ↓
F = immutable FROZEN PACKAGE COMMIT (protocol + contract + seed record +
    analyzer pin; без self-reference к собственному SHA)
      ↓
fresh Reviewer(F) → fresh Verifier(F)
      ↓ (параллельный infrastructure track)
native Ubuntu AUTHOR_U1 → U1-U5 + NC-U1..NC-U5 → review/verify → HG-A → R2 ACTIVE
      ↓
Science открывается ТОЛЬКО при одновременно: HG-B APPROVED (есть) +
FROZEN package accepted + R2 ACTIVE + AUTHOR_U1 assigned
```
