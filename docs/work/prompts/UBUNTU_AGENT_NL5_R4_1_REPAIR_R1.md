# NanoLab — Ubuntu IMPLEMENTER prompt: NL5 v0.2 R4.1 reviewer corrections

Статус: repair mission после fresh Reviewer R1. Не Human Gate, не freeze, не scientific-run authorization.

## 0. Binding

```text
repository       = rootfabric/NanoLab
product branch   = work/nl5-v02-prefreeze-hardening-r4
reviewed subject = 62f65612f7b2652917396e3acfc5d6d3a605032e
reviewed tree    = a45f8295067ff7bf0b9f0c401f09e0771df7d909
product tip seen = 1964bb51915fb0850f7f34b99d6774c48af5bf60
review branch    = review/nl5-v02-prefreeze-hardening-r4-r1
review verdict   = FIX_REQUIRED
review report    = docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/REVIEWER_VERDICT_R1.md
```

Сначала fresh fetch. Не считать SHA выше автоматически актуальными. Если другая repair-сессия уже опубликовала новый substantive subject, не создавай дубль: сделай delta-read и продолжи существующую работу.

## 1. Start / history

Предпочтительный repair branch:

```text
repair/nl5-v02-prefreeze-hardening-r4-r1
```

Создай его от актуального tip `work/nl5-v02-prefreeze-hardening-r4` (на момент review: `1964bb5…`), затем интегрируй reviewer branch `review/nl5-v02-prefreeze-hardening-r4-r1` с сохранением истории (`--no-ff`, no force, no squash reviewer evidence).

До substantive repair добавь append-only review-correction/continuation event в существующий execution `EX-NL5-V02-PREFREEZE-HARDENING-R4` согласно текущей harness schema. Не редактируй terminal handoff задним числом.

Границы:

```text
SCIENCE RUNS = 0
CANDIDATE = PRE-DATA / NOT FROZEN
HG-B = WAITING_OWNER
R2 = WAITING_HOST / NOT_ACTIVE
NL5 = IN_PROGRESS
NL6-001 = LOCKED
```

## 2. M-1 — separate PRE-FREEZE VALIDATION from DISPATCH READY

Текущий дефект: `build_execution_plan()` выдаёт `nanolab_v02_dispatch_execution_plan` для committed contract с `freeze_status = NOT_FROZEN`; positive tests даже требуют exit 0.

Исправить fail-closed.

### Обязательная модель

Раздели:

```text
PREFREEZE_VALIDATION_PASS
  = internal consistency only

DISPATCH_READY
  = FROZEN + authority prerequisites + full contract validation
```

Текущий committed R4 PRE-DATA package может проходить только pre-freeze validation. Он не должен давать scientific dispatch plan.

Final dispatch authority должна машинно требовать минимум:

- `freeze_status == FROZEN`;
- Director freeze record / exact frozen subject binding;
- HG-B owner approval binding R4 delta;
- required fresh review/verify state for frozen subject;
- R2 ACTIVE / authorized executor condition for both legs, либо отдельный mandatory launcher authority object, который actual dispatch не может обойти.

Практичная реализация: versioned `dispatch_authority` JSON с exact refs/digests + отдельный `validate_dispatch_authority()`. `build_execution_plan()` должен требовать этот объект.

До появления реальных owner/freeze/R2 records actual committed package обязан быть `DISPATCH_BLOCKED`.

Tests:

- NOT_FROZEN + otherwise-clean contract => dispatch rejected;
- missing authority => rejected;
- HG-B not approved => rejected;
- frozen subject mismatch => rejected;
- review/verify mismatch => rejected;
- R2 not active => rejected;
- synthetic fully-authorized fixture => plan generated;
- prefreeze validation current package => PASS without status inflation.

Не создавай fake real-world HG-B/R2 PASS evidence ради positive test: positive dispatch fixture должен быть clearly synthetic test-only.

## 3. M-2 — bit-exact replacement-pool replay

Текущий validator проверяет cursor/length/disjointness, но не доказывает, что pool seeds — deterministic stream.

Добавь independent replay per variant:

```text
anchor
variant
start_index
next_candidate_index
recorded skipped indices
→ derive every candidate
→ skipped entries removed only under validated collision rule
→ accepted identities must equal published replacement pool bit-for-bit
```

Каждый skipped replacement entry должен быть strict object:

```json
{"index": <int>, "seed": <derived-int>, "reason": "SEED_COLLISION_TREE"}
```

No missing/extra keys; wrong seed/reason/index fails.

Добавь full R4 digest or dedicated replacement-pool digest. R3 logical digest можно сохранять как provenance, но он не является R4 integrity digest.

Negative tests:

- mutate one pool seed in both contract + record, recompute file hash => reject;
- fake skip entry => reject;
- wrong skip seed => reject;
- wrong reason => reject;
- wrong next cursor => reject.

## 4. M-3 — prove collision skip legitimacy inside authoritative gate

Сейчас accepted 176 fresh identities scanned clean, но gate доверяет recorded skips.

На freeze/dispatch validation:

1. verify pinned object exists;
2. for every accepted confirmatory/replacement identity:
   - pinned-tree scan;
   - zero non-allowlisted hits required;
3. for every recorded `SEED_COLLISION_TREE` skip:
   - seed must re-derive from anchor/variant/index;
   - pinned-tree scan must have >=1 non-allowlisted hit;
   - exact hit paths recorded/bound;
4. any git error/timeout/missing object => BLOCKED.

Можно rerun scan directly at freeze, либо использовать signed/digested scan manifest, но authority must bind its SHA-256 and exact tree SHA. Простая human-readable evidence рядом недостаточна.

Critical negative test:

```text
mark a clean deterministic candidate index as skipped
→ contract/record otherwise self-consistent
→ gate MUST reject
```

Также negative test: scan manifest digest mismatch / incomplete skipped coverage => reject.

## 5. M-4 — pair-level ReplacementLedger

Текущий ledger — leg-level и позволяет дважды вызвать replacement на одном failed attempt.

Сделай pair-level append-only state machine.

Minimum binding:

```text
pair_id
variant
seed_identity
author_attempt_id + outcome
external_attempt_id + outcome
pair_state
replacement_assigned (0/1)
replacement_identity
replacement_pair_id
```

Rules:

- pair identity unique;
- each attempt id globally unique;
- replacement allowed only when pair terminal technical state contains frozen FAILED_TECHNICAL condition;
- one source pair may receive at most ONE replacement assignment;
- replacement consumes next frozen identity in order;
- replacement schedules BOTH legs;
- repeat request for same failed pair => reject without consuming quota;
- missing/mismatched counterpart => reject;
- quota exhaustion => honest stop, no expansion.

Добавь tests:

- double request same failed pair => rejected and cursor unchanged;
- author failed + external completed => one replacement pair, both new legs scheduled;
- external failed mirror case;
- missing counterpart => rejected;
- wrong seed/pair relationship => rejected;
- second failure must reference the replacement pair, not the original failed pair.

## 6. m-1 — equivalence wording

В candidate §3 заменить “неотличимость медианного сдвига от нуля” на корректную equivalence формулировку:

```text
CI медианного парного сдвига целиком лежит внутри заранее заданного
equivalence interval (−δ·s_eff, +δ·s_eff)
```

Это не означает statistical non-significance относительно нуля.

Желательно привести H0/H1 к standard TOST convention:

```text
H0: non-equivalence (outside / not wholly inside margin)
H1: equivalence (CI wholly inside margin)
```

Если labels оставлены историческими, explicitly state they are non-standard and decision rule is authoritative.

## 7. Preserve R4 good work

Не откатывать без причины:

- N_min 52/8;
- quota 12/12/2/2;
- replacement cap 56 / max 352;
- R3 confirmatory identities/logical digest;
- pinned immutable scanner semantics;
- exact path allowlist;
- next_candidate_index 75/76/21/21;
- PRE-DATA status;
- outenemy EXTERNAL_U2_ONLY / WAITING_HOST;
- no new science.

Power-gate branch `repair/nl5-acceptance-policy-r4-power-gate-r1` не смешивать в этот repair без Director sequencing.

## 8. Validation

Обязательно:

```bash
python3 -m unittest discover -s tests -t . -v
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .
# validate all EX-* exactly as hosted workflow does
```

Добавь reviewer-specific regressions M-1..M-4 before claiming FIXED.

Hosted CI пока не требуй обходным способом. После fresh Reviewer PASS должен быть TR-PR draft and hosted CI on exact PR subject.

## 9. Handoff

Новый substantive repair => новый exact review subject.

Сохрани:

```text
R4.1_HEAD =
R4.1_TREE =
BASE =
REVIEW_R1 = FIX_REQUIRED / branch+SHA
REPAIR_MAP_R1.1 =
M-1 =
M-2 =
M-3 =
M-4 =
m-1 =
TEST_COLLECTION =
HARNESS =
SCIENTIFIC_RUNS = 0
CANDIDATE = PRE-DATA / NOT FROZEN
R2 = WAITING_HOST / NOT_ACTIVE
NEXT_ACTOR = fresh REVIEWER
```

Не запускай Verifier до fresh Reviewer PASS.
