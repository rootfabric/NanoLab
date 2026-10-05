# DIRECTOR_FREEZE_R1 — Director FREEZE decision for v0.2 package F

```text
record_kind        = DIRECTOR_FREEZE_RECORD
issuer_class       = DIRECTOR
director           = DIRECTOR
decision           = FREEZE
decision_id        = NL5-V02-FREEZE/DIRECTOR/R1
rule_id            = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL
candidate_revision = R4 (post-R4.3 hardened basis)
frozen_revision    = FROZEN_R1
recorded_at_utc    = 2026-10-05T08:57:46Z
```

## Frozen subject (immutable FROZEN PACKAGE COMMIT F)

```text
subject_head (F_HEAD) =
cb91ade761f6802fc40c500761d3e35022408822

subject_tree (F_TREE) =
ad21ce39b42681f581da996b2805a5b2fb49111f

git cat-file -t F_HEAD            = commit
git rev-parse F_HEAD^{tree}       = F_TREE (proven)
```

F — dedicated immutable commit, содержащий ровно три frozen артефакта как exact
Git blobs этого commit (значения вычислены из Git object database, не из
mutable worktree):

```text
protocol =
  path              = docs/research/NANOLAB_REPRO_V0_2_FROZEN_R1.md
  git_blob_sha1     = 197cc717bae0b0906ac7816d11f28f93676558c2
  canonical_sha256  = 7fafbf9ace099594a16182523432ca38fe5c31f30d2d8969d7281b8852f45962

contract =
  path              = docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/
                      repro-v0-2-freeze-contract-FROZEN_R1.json
  git_blob_sha1     = 5f788c45842db695abbd3fc8706828bc74173d5e
  canonical_sha256  = c556b3f24a112f460cf34070e6a5ce99eb826e05663c589583af4dbe02f6ee4f

seed record =
  path              = docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/
                      repro-v0-2-seed-record-FROZEN_R1.json
  git_blob_sha1     = 0164e0e3f5dda6dbf63174df3730b1bd921d2c76
  canonical_sha256  = 8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28
```

Seed record — байт-в-байт копия принятой R4 PRE-DATA seed record
(`cmp` чистый; `sha256sum` источника и копии совпадают и равны контрактовому
`seed_record_file_sha256`). Ни одна научная идентичность (seeds, cursors,
pools, skips, bootstrap, exclusion list, digests) не изменилась.

Frozen contract выведен из `repro-v0-2-freeze-contract-PRE_DATA_R4.json`
исключительно allowlisted заменой scientific-subject binding:
`candidate_doc_path` → frozen protocol path; `seed_record_path` → frozen seed
record path; `freeze_status` → `FROZEN`; `frozen_subject_head`/`frozen_subject_tree`
= `null` (non-authoritative compatibility fields, R4.3 M-7 — точные pins F
находятся в настоящей записи). 307 из 310 листьев JSON идентичны источнику;
машинная проверка дельты: `frozen-package-delta-check-R1.json` (result PASS).
Замороженные научные инварианты: rule `NANOLAB_REPRO_V0_2_DISTRIBUTIONAL`,
R4 basis, N = 64/64/10/10, N_min = 52/52/8/8, replacement quotas 12/12/2/2
пар, confirmatory 296, replacement cap 56, max_runs 352, wall 560 ч/платформа,
δ = 0.5, paired TOST, bootstrap 10000 PAIRED, integer policy
`ceil-nmin-floor-replacement-pairs-v1`, 74b excluded / NOT_MEASURED /
KNOWN_GAP, replacement = FAILED_TECHNICAL only, pinned collision-scan
manifest. Fresh Reviewer R4 PASS + fresh Verifier VERIFIED R4.3 basis
(39cc9809… / 10ba8bbf…) — зафиксированы в §0 frozen protocol.

## Owner basis

```text
HG-B = APPROVED
  decision_id       = NL5-ACCEPTANCE-POLICY/HG-B/R1 (2026-10-05)
  record binding (exact immutable Git blob):
    source_commit   = 549b687a9171ea3636dbb00078d7018f619cebd3 (canonical main)
    path            = docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.json
    git_blob_sha1   = 61d1491233aeb2537f9800d6183def5b8fb0c8e0
    canonical_sha256= b68dd341a5671d6314da3fcf6d32fae54f88b385b7b5a631edb07b0f6f49d2c9
    record_kind     = HG_B_OWNER_APPROVAL
    issuer_class    = HUMAN_GATE_OWNER
```

## Gate at freeze

```text
gate              = PASS
validation_stage  = PREFREEZE_VALIDATION_PASS
freeze_status     = FROZEN
dispatch          = DISPATCH_BLOCKED
dispatch_ready    = false
evidence          = docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/
                    frozen-gate-PASS-R1.json
```

`PREFREEZE_VALIDATION_PASS` — имя internal-consistency стадии валидатора;
authoritative факт freeze — настоящий F + настоящая запись (D), а не gate.

## State ceiling at freeze (zero science)

```text
SCIENTIFIC_RUNS                    = 0
external_reproductions             = 0
candidate status at freeze         = PRE-DATA (zero confirmatory data at freeze)
NL5                                = IN_PROGRESS
NL6-001                            = LOCKED
AUTHOR_U1                          = NOT_ASSIGNED
R2                                 = WAITING_HOST / NOT_ACTIVE
machine_launch_authorized          = false
launch_gate                        = HUMAN_PROTECTED_WRITER
```

## Lifecycle and dispatch ceiling

```text
lifecycle = S -> F -> D/R/V -> A
S = PRE-FREEZE state, HG-B APPROVED (canonical main 549b687a…)
F = cb91ade761f6802fc40c500761d3e35022408822 (этот subject; никогда не
    amend/rewrite после публикации)
D = настоящая запись (отдельный commit, строгий потомок F)
R = fresh SCIENTIFIC REVIEWER(F) — отсутствует
V = fresh independent VERIFIER(F) — отсутствует
A = authority/readiness record (schema v3) — отсутствует

dispatch = BLOCKED; blockers:
  - fresh Reviewer(F) = missing
  - fresh Verifier(F) = missing
  - R2 ACTIVE = false
  - AUTHOR_U1 = NOT_ASSIGNED
```

Post-freeze edit policy: любое изменение научного содержания frozen protocol /
contract / seed record — только новая revision (v0.3+) через новый Work Order
и новый freeze; правка frozen текста запрещена.

Record source note: собственные commit SHA / blob identity этой записи
намеренно отсутствуют внутри её же байтов (самореференс невозможен); они
фиксируются append-only event 0003 исполнения `EX-NL5-V02-DIRECTOR-FREEZE-R1`
в более позднем commit. Следующие акторы: fresh SCIENTIFIC REVIEWER(F), затем
fresh independent VERIFIER(F) — оба обязаны пиновать exact F, а не этот
record commit. SCIENCE НЕ НАЧИНАТЬ.
