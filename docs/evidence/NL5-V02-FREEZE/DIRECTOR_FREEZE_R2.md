# DIRECTOR_FREEZE_R2 — Director FREEZE decision for the corrected v0.2 package F2

```text
record_kind        = DIRECTOR_FREEZE_RECORD
issuer_class       = DIRECTOR
director           = DIRECTOR
decision           = FREEZE
decision_id        = NL5-V02-FREEZE/DIRECTOR/R2
rule_id            = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL
candidate_revision = R4 (post-R4.3 hardened basis)
frozen_revision    = FROZEN_R2
recorded_at_utc    = 2026-10-05T16:02:14Z
```

## Disposition of FROZEN_R1 / Director FREEZE R1 (historical, immutable)

```text
FROZEN_R1 (F1)         = cb91ade761f6802fc40c500761d3e35022408822
FROZEN_R1 tree         = ad21ce39b42681f581da996b2805a5b2fb49111f
Director FREEZE R1     = commit 4236e0c7cfb19de2687a8f0d3be3641cc1b000d4
Scientific review R1   = FAIL / FIX_REQUIRED
                         (docs/evidence/NL5-V02-FREEZE/FRESH_SCIENTIFIC_REVIEW_R1.{md,json};
                         blocking finding M-1 — frozen protocol §6 collision-scan
                         exact allowlist contradicted the authoritative contract
                         allowlist of the pinned historical tree)
```

FROZEN_R1 and Director FREEZE R1 are **historical immutable attempt** evidence:
they are preserved byte-for-byte, never amended or rewritten, and are
**superseded for dispatch by FROZEN_R2** after this corrected package passed
the repaired fail-closed gate. No Verifier(FROZEN_R1) acceptance applies.

## Frozen subject (immutable corrected FROZEN PACKAGE COMMIT F2)

```text
subject_head (F2_HEAD) =
60da9a846511265a8ac7564da088c3d74cb073f0

subject_tree (F2_TREE) =
e565c8a6cee9e829fac14008ebc9c2ea1609931d

git cat-file -t F2_HEAD            = commit
git rev-parse F2_HEAD^{tree}       = F2_TREE (proven)
```

F2 — dedicated immutable commit, содержащий frozen артефакты как exact Git blobs
этого commit (значения вычислены из Git object database, не из mutable worktree;
машинная перепроверка всех pins записи выполнена перед публикацией):

```text
protocol =
  path              = docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md
  git_blob_sha1     = 4835719622bae49a8e8b480536a482b4b222d408
  canonical_sha256  = 2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d

contract =
  path              = docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/
                      repro-v0-2-freeze-contract-FROZEN_R2.json
  git_blob_sha1     = d6a9ccde4d1dadf42d1a8cd9b88faa02646cf70b
  canonical_sha256  = 7e6476544e82af73d5d7e0672666ece99bf4d499a0da30645b02886bcdc45b3a

seed record =
  path              = docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/
                      repro-v0-2-seed-record-FROZEN_R2.json
  git_blob_sha1     = 0164e0e3f5dda6dbf63174df3730b1bd921d2c76
  canonical_sha256  = 8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28
```

Seed record — байт-в-байт копия принятой R4 PRE-DATA seed record и FROZEN_R1
seed record (один и тот же Git blob `0164e0e3…`; `cmp` чистый; SHA-256
`8e844bff…` = contract `seed_record_file_sha256`). Ни одна научная идентичность
(seeds, cursors, pools, skips, bootstrap, exclusion list, digests) не изменилась.

Frozen contract выведен из `repro-v0-2-freeze-contract-PRE_DATA_R4.json`
исключительно allowlisted заменой scientific-subject binding:
`candidate_doc_path` → FROZEN_R2 protocol path; `seed_record_path` → FROZEN_R2
seed record path; `freeze_status` → `FROZEN`; `frozen_subject_head`/
`frozen_subject_tree` = `null` (non-authoritative compatibility fields, R4.3
M-7). 307 из 310 листьев JSON идентичны источнику; машинная проверка дельты:
`frozen-package-delta-check-R2.json` (result PASS). Замороженные научные
инварианты идентичны FROZEN_R1: rule `NANOLAB_REPRO_V0_2_DISTRIBUTIONAL`,
R4 basis, N = 64/64/10/10, N_min = 52/52/8/8, replacement quotas 12/12/2/2 пар,
confirmatory 296, replacement cap 56, max_runs 352, wall 560 ч/платформа,
δ = 0.5, paired TOST, bootstrap 10000 PAIRED, integer policy
`ceil-nmin-floor-replacement-pairs-v1`, 74b excluded / NOT_MEASURED /
KNOWN_GAP, replacement = FAILED_TECHNICAL only, pinned collision-scan manifest.

## M-1 correction (the only substantive delta vs FROZEN_R1)

```text
scan tree =
a9d7d07fa264e9907b67ca244b00ba2da3430b0f

scan_allowlist_paths_exact (authoritative contract; FROZEN_R2 protocol
scan-allowlist-v1 block, ordered exact) =
docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/
  repro-v0-2-seed-record-PRE_DATA_R4.json
```

Allowlist определён в pinned историческом дереве скана `a9d7d07…`: это
существующие в нём approved R4 пути (candidate document + PRE_DATA_R4 seed
record). Пути артефактов FROZEN_R2 пакета — более поздние Git-объекты и НЕ
являются записями allowlist этого исторического скана. Регрессия gate:
fail-closed FROZEN-only binding `scan-allowlist-v1` ↔
`contract.seed_generation.scan_allowlist_paths_exact`
(`scripts/nl5/repro_v02_freeze_contract.py`, `ScanAllowlistBindingTest`,
12 тестов); FROZEN_R1-style frozen-package paths и сырой FROZEN_R1 протокол
дают `FREEZE_GATE_FAIL` / exit 3 (`m1-negative-control-R2.json`).

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
evidence          = docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/
                    frozen-gate-PASS-R2.json
```

`PREFREEZE_VALIDATION_PASS` — имя internal-consistency стадии валидатора;
authoritative факт freeze — настоящий F2 + настоящая запись (D2), а не gate.
Full validation на подготовительных поверхностях: 605 tests OK;
check-consistency ok (0/0); workflow_lint blocking 0; work_cli 51/51 EX-* ok
(финальная перепроверка — на handoff commit).

## State ceiling (unchanged)

```text
SCIENTIFIC_RUNS            = 0
NL5                        = IN_PROGRESS
NL6-001                    = LOCKED
AUTHOR_U1                  = NOT_ASSIGNED
R2                         = WAITING_HOST / NOT_ACTIVE
external_reproductions     = 0
machine_launch_authorized  = false
launch_gate                = HUMAN_PROTECTED_WRITER
```

Dispatch остаётся ЗАБЛОКИРОВАННЫМ до: fresh Reviewer(**F2**) PASS + fresh
independent Verifier(**F2**) VERIFIED + R2 ACTIVE + AUTHOR_U1 assigned +
authority record A (schema v3, lifecycle S → F → D/R/V → A). Review/verify
обязаны пиновать exact F2_HEAD/F2_TREE и exact artifact blobs выше — не F1 и
не служебные коммиты.
