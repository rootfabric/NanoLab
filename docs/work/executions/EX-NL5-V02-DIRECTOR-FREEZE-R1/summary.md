# EX-NL5-V02-DIRECTOR-FREEZE-R1 — summary

Status: **HANDOFF_READY — FROZEN PACKAGE F CREATED + Director FREEZE RECORDED (zero science)**.

Canonical base:

```text
main = 549b687a9171ea3636dbb00078d7018f619cebd3
tree = 5bfb2411d6283420e9067850807c6650725d838b
HG-B = APPROVED
```

Result:

```text
F_HEAD =
cb91ade761f6802fc40c500761d3e35022408822

F_TREE =
ad21ce39b42681f581da996b2805a5b2fb49111f
```

F — immutable FROZEN PACKAGE COMMIT, опубликован non-force push
(`9eec5d5..cb91ade`); amend/rewrite запрещены. Exact Git blobs of F (вычислены
из Git object database):

```text
protocol      = docs/research/NANOLAB_REPRO_V0_2_FROZEN_R1.md
                blob 197cc717bae0b0906ac7816d11f28f93676558c2
                sha256 7fafbf9ace099594a16182523432ca38fe5c31f30d2d8969d7281b8852f45962
contract      = docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/
                repro-v0-2-freeze-contract-FROZEN_R1.json
                blob 5f788c45842db695abbd3fc8706828bc74173d5e
                sha256 c556b3f24a112f460cf34070e6a5ce99eb826e05663c589583af4dbe02f6ee4f
seed record   = docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/
                repro-v0-2-seed-record-FROZEN_R1.json
                blob 0164e0e3f5dda6dbf63174df3730b1bd921d2c76
                sha256 8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28
                (байт-в-байт копия принятой R4 PRE-DATA seed record)
```

Director FREEZE record (строгий потомок F):

```text
commit        = 4236e0c7cfb19de2687a8f0d3be3641cc1b000d4
paths         = docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R1.{md,json}
record json   = blob 423fdab372cc98fb902544df4b43da27a2231790
                sha256 87ae3a9e23db2f90331889dd0cc83414b6eecf525a10987a8d2f26aa04afcdb8
pins          = subject_head/subject_tree = F; protocol/contract/seed-record
                exact digests; HG-B binding (549b687a…, blob 61d14912…,
                HG_B_OWNER_APPROVAL / HUMAN_GATE_OWNER / APPROVED)
```

Gate на frozen байтах: `PASS / PREFREEZE_VALIDATION_PASS / freeze_status
FROZEN / DISPATCH_BLOCKED / dispatch_ready=false`
(`evidence/frozen-gate-PASS-R1.json`). Дельта frozen contract от R4 — только
allowlisted subject binding, 307/310 листьев неизменны
(`evidence/frozen-package-delta-check-R1.json`).

Validation:

```text
unittest discover      = Ran 593 tests, OK
check-consistency      = ok:true, errors [], warnings []
workflow_lint          = workflows 1, violations 0, blocking 0
work_cli all EX-*      = 50/50 ok
```

Commits этой execution:

```text
9eec5d5 preparation (expected prep HEAD)
cb91ade FROZEN PACKAGE COMMIT F
4236e0c Director FREEZE record + event 0002
<this>  bookkeeping handoff (event 0003 + summary + passport + WORK_QUEUE)
```

Ceilings (не изменены):

```text
SCIENTIFIC_RUNS = 0
AUTHOR_U1 = NOT_ASSIGNED
R2 = WAITING_HOST / NOT_ACTIVE
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED
machine_launch_authorized = false
```

Dispatch = BLOCKED до: fresh Reviewer(F) PASS + fresh Verifier(F) VERIFIED +
R2 ACTIVE + AUTHOR_U1 assigned + authority record A (lifecycle
`S -> F -> D/R/V -> A`).

Next action: fresh SCIENTIFIC REVIEWER(F), затем fresh independent
VERIFIER(F) — оба пинуют exact F (НЕ record/bookkeeping коммиты). Не начинать
science.
