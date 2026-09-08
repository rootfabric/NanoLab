# NL0-002 — Director Acceptance R1

Дата: 2026-09-08. Роль: `DIRECTOR`. Work Order: `NL0-002 — Audit dependencies, rights and licensing options`.

## Exact subjects

```text
BASE_MAIN                  = 95b1319600bcc64572d84c0456acb927802ab806
IMPLEMENTER_INITIAL_HEAD   = 495b03391e7eff72bbfbb5c5912e35ef9035b868
FRESH_VERIFIER_R1_EVIDENCE = 48d6d0c0089d985118e629ac459c7aa9d85e85eb
FRESH_VERIFIER_R1_VERDICT  = FAIL / FIX_REQUIRED
REPAIR_SUBSTANTIVE_HEAD    = cd55320441c2c904f8e406870c902fbff587c602
REPAIRED_PR_HEAD           = 86be310c93aeb0dc92e7992f5492933b08265984
REPAIRED_PR_TREE           = 45be9fe20ceddc6f04e96daa3a457afac9d5004e
EXACT_HEAD_VERIFIER_R2     = dbdd272c28572644a14359a2f0e9ddbe0a0c25f4
EXACT_HEAD_VERDICT         = PASS
MERGE_COMMIT               = 598faa63ab2ff1d1824870973d356a8da4dac1a4
```

Human merge gate был явно разрешён владельцем перед merge. PR #17 объединён с `expected_head_sha=86be310c93aeb0dc92e7992f5492933b08265984`; race между verification и merge не допущен.

## Review history preserved

Первый Fresh Verifier не принял первоначальный candidate и выдал три `FIX_REQUIRED`:

1. immutable license evidence для software dependencies;
2. корректное различение GPL aggregate / separate executable / same-process binding / modified GPL code;
3. удаление неточной свёртки GPL obligations в `(+NOTICE)`.

Эти findings не скрыты успехом. Они были закрыты отдельным `EX-NL0-002-R1-REPAIR1`, после чего Exact-Head Verifier R2 дал PASS на repaired PR head.

## Director decision

```text
RISK_CLASS       = LOW
CLAIM_CLASS      = C0_SOFTWARE_ONLY
VERIFIER_R2      = PASS
EPOCH_DRIFT      = CONTINUE
DIRECTOR_VERDICT = ACCEPTED
```

Reviewer не был обязательным по LOW-risk routing. Правовые неоднозначности не были решены агентом как юридические заключения; они сохранены как owner/legal decisions.

## Канонически принятые результаты

### E1

```text
oxDNA root license = GPL-3.0
E1 project mode    = DOWNLOAD_ON_SETUP
```

Для будущего release/packaging разделяются aggregate, separate executable, same-process binding и modified GPL code. Same-process `oxpy` integration требует owner decision и legal review до фиксации release architecture.

### E2

```text
DNA-hinge-simulations license in pinned tree = NOT LOCATED
REDISTRIBUTION_RIGHTS                         = UNKNOWN
E2 project mode                               = REFERENCE_ONLY
```

Public GitHub visibility не считается разрешением на redistribution. До явной лицензии/permission NanoLab не должен копировать E2 pack в repository/release/mirror.

### Software dependency license evidence

Приняты immutable license-evidence pins для scadnano, oxView, PyMBAR, AiiDA, aiida-shell, Ax и BoTorch: canonical repository, checked commit, license path, Git blob SHA-1, SHA-256 и license result.

BoTorch canonical source: `meta-pytorch/botorch`; `pytorch/botorch` сохранён как historical redirect alias.

### Project license

NanoLab license **не назначена**. Варианты Apache-2.0 / MIT / GPL-3.0-or-later для кода и CC BY / CC BY-SA для документации являются options, а не решением.

## State transition

Каноническое состояние после этого acceptance record:

```text
frontier       = NL0
NL0            = IN_PROGRESS
NL0-001        = ACCEPTED
NL0-002        = ACCEPTED
NL0-003        = READY
next_work_order = NL0-003
E0..E6         = NOT_RUN
physics_runs   = 0
```

`NL0` целиком не закрыт. Оставшаяся работа NL0 — `NL0-003`: preregistration exact E1 protocol и постановки E2.

## Open owner decisions preserved

1. Выбрать лицензию NanoLab для code/docs/data.
2. Получить явную лицензию/permission для `DNA-hinge-simulations` либо заменить E2 seed до NL3.
3. Определить policy durable private caching для UNKNOWN-rights files.
4. Перед release architecture отдельно оценить same-process `oxpy` integration.

## Non-blocking Harness hardening

Verifier R2 сохранил два неблокирующих provenance-наблюдения:

- handoff commit repair также дописал `SESSION_LOG.md`, поэтому описание «только terminal/status/summary» было слегка неполным;
- ручные `timestamp_utc` events не привязаны валидатором к Git commit timestamps.

Это не блокировало NL0-002, но должно быть учтено в будущем hardening Harness.

## Final

```text
NL0-002 = ACCEPTED
NEXT    = NL0-003
```
