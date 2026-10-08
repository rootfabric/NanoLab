# NL5 v0.2 FROZEN_R1 — Fresh Scientific Reviewer R1

```text
REVIEW_ID =
NL5-V02-FROZEN-R1/SCIENTIFIC_REVIEW_R1

VERDICT =
FAIL / FIX_REQUIRED

REVIEWED_SUBJECT_HEAD =
cb91ade761f6802fc40c500761d3e35022408822

REVIEWED_SUBJECT_TREE =
ad21ce39b42681f581da996b2805a5b2fb49111f

REVIEWED_PROTOCOL_BLOB =
197cc717bae0b0906ac7816d11f28f93676558c2

REVIEWED_CONTRACT_BLOB =
5f788c45842db695abbd3fc8706828bc74173d5e

REVIEWED_SEED_RECORD_BLOB =
0164e0e3f5dda6dbf63174df3730b1bd921d2c76

BASE_MAIN =
549b687a9171ea3636dbb00078d7018f619cebd3

SCIENTIFIC_RUNS =
0
```

## 1. Scope and independence

Fresh scientific/protocol review of the immutable FROZEN PACKAGE COMMIT F only.

The reviewed scientific subject is **F itself**:

```text
F_HEAD = cb91ade761f6802fc40c500761d3e35022408822
F_TREE = ad21ce39b42681f581da996b2805a5b2fb49111f
```

The later Director record / execution handoff commits are control evidence only and are not substituted for the scientific subject.

This review independently inspected the remote Git objects, the frozen protocol, frozen contract, seed record, delta-check evidence, frozen-gate evidence, the approved R4 candidate text, HG-B basis and the later Director record binding.

The implementer-reported `593 tests OK` / harness results are execution evidence; this reviewer does not claim an independent local rerun.

## 2. Confirmed PASS surfaces

The following are correct and should be preserved in the next revision.

### 2.1 Immutable subject / freeze sequencing

PASS.

- F is a real Git commit.
- F tree is exactly `ad21ce39...`.
- protocol / contract / seed record are Git blobs of F.
- F does not embed its own commit SHA.
- the Director FREEZE record is in a strict descendant commit `4236e0c...`.
- the Director record pins F HEAD/TREE and exact artifact blob/digest identities.

This is consistent with the required `S -> F -> D/R/V -> A` lifecycle.

### 2.2 Scientific contract leaves

PASS.

The frozen contract delta evidence reports exactly three changed leaves relative to the approved PRE-DATA R4 contract:

```text
scientific_subject.candidate_doc_path
scientific_subject.freeze_status
scientific_subject.seed_record_path
```

The other 307 leaves remain unchanged.

Approved scientific parameters are preserved:

```text
N = 64 / 64 / 10 / 10
N_min = 52 / 52 / 8 / 8
replacement quotas = 12 / 12 / 2 / 2 pairs
confirmatory runs = 296
replacement cap = 56
max_runs = 352
delta = 0.5
paired TOST
bootstrap = 10,000
integer policy = ceil-nmin-floor-replacement-pairs-v1
74b excluded
replacement only for FAILED_TECHNICAL
```

### 2.3 Seed identity preservation

PASS.

The frozen seed record SHA-256 is:

```text
8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28
```

and is recorded as byte-identical to the accepted R4 PRE-DATA seed record.

Confirmatory identities, bootstrap seeds, replacement streams, consumed cursors, exclusions and integrity digests are preserved.

### 2.4 Decision rule / scientific interpretation

PASS.

The frozen protocol preserves the intended scientific scope:

- primary observable = per-replica median hinge angle;
- paired differences use identical seed identities across U1/U2;
- primary statistic = median paired shift;
- equivalence = CI90 entirely inside the predeclared `±0.5 * s_eff` interval;
- statistical non-significance from zero is not treated as equivalence;
- controls downgrade reproduced outcomes but do not independently create MISMATCH;
- technical failure remains distinct from scientific mismatch;
- frozen outcome vocabulary remains honest;
- no v0.1 threshold tuning or retrospective reclassification is introduced.

### 2.5 State ceiling

PASS.

At freeze:

```text
SCIENTIFIC_RUNS = 0
AUTHOR_U1 = NOT_ASSIGNED
R2 = WAITING_HOST / NOT_ACTIVE
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED
dispatch = BLOCKED
```

No scientific campaign was started.

## 3. Blocking finding

### M-1 — Frozen protocol changes the collision-scan exact allowlist while the authoritative contract preserves the approved R4 allowlist

Severity: **MAJOR / SCIENTIFIC-PROTOCOL-INTEGRITY BLOCKING**

The approved R4 candidate says that the seed collision scan is performed against the pinned immutable tree and allows seed literals only at:

```text
seed record path + candidate document path
```

The authoritative approved R4 contract makes those paths exact:

```text
docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md

docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/
repro-v0-2-seed-record-PRE_DATA_R4.json
```

The FROZEN_R1 contract correctly preserves those exact paths in:

`seed_generation.scan_allowlist_paths_exact`.

However FROZEN_R1 protocol §6 now states:

```text
exact path allowlist =
{seed record path, frozen protocol path данного пакета}
```

That is a different allowlist.

This is not merely a filename formatting issue. The exact allowlist is part of the F2 collision-integrity protection: it defines which occurrences in the pinned tree may be ignored when proving that confirmatory/replacement identities are fresh.

The package therefore contains two contradictory declarations:

```text
authoritative contract:
candidate R1 path + PRE_DATA_R4 seed record path

frozen protocol §6:
FROZEN_R1 protocol path + FROZEN_R1 seed record path
```

The current contract gate passes because the protocol cross-check does not machine-bind `scan_allowlist_paths_exact`; therefore this contradiction is precisely a class the current frozen gate fails to detect.

Because the collision tree is pinned to `a9d7d07fa264e9907b67ca244b00ba2da3430b0f`, the correct allowlist remains the paths that exist in **that pinned tree**. The later frozen-package paths are not replacements for the approved allowlist.

## 4. Why this blocks PASS

FROZEN_R1 itself states that:

- the collision obligation is part of the protocol, not a summary;
- exact-path allowlisting is fail-closed;
- contradictory authoritative declarations must fail the freeze gate;
- post-freeze text is immutable.

Therefore the reviewer cannot reinterpret §6 after the fact or silently prefer the JSON contract over the frozen protocol.

The scientific seed arrays themselves do not need to change, but the frozen protocol package is internally inconsistent on a protection that determines seed-freshness proof semantics.

**FROZEN_R1 must remain immutable and preserved as a failed reviewed freeze revision. It must not be amended.**

## 5. Required repair — new frozen revision only

Create a new immutable package revision, recommended:

```text
FROZEN_R2
```

Do not rewrite or amend FROZEN_R1.

The new frozen protocol must state the exact approved R4 allowlist, e.g.:

```text
scan tree =
a9d7d07fa264e9907b67ca244b00ba2da3430b0f

scan_allowlist_paths_exact =
docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/
  repro-v0-2-seed-record-PRE_DATA_R4.json
```

It should explicitly explain why: the collision proof is a search of the pinned historical tree `a9d7d07...`; those are the allowlisted locations in that tree. FROZEN_R2 artifact paths are later Git objects and are not substitutions for the historical scan allowlist.

### 5.1 Scientific delta ceiling

No scientific/statistical values may change.

The R2 seed record should remain byte-identical to R4/R1 frozen seed record.

The R2 contract should remain scientifically identical to approved R4, with only freeze-package metadata/path changes.

### 5.2 Required regression hardening

The mismatch escaped because `_validate_protocol()` does not currently cross-check the exact collision-scan allowlist declaration.

Add a fail-closed regression so a FROZEN protocol declaring an allowlist different from:

`contract.seed_generation.scan_allowlist_paths_exact`

cannot pass the frozen gate.

A minimal implementation may add a FROZEN-only machine declaration / canonical digest or another deterministic parseable declaration. PRE-DATA R4 historical documents do not need to be rewritten.

Required negative test:

```text
contract allowlist = approved R4 exact paths
frozen protocol allowlist = frozen-package paths
=> FREEZE_GATE_FAIL
```

Required positive test:

```text
frozen protocol exact allowlist == contract exact allowlist
=> gate may PASS
```

## 6. Director record disposition

The existing Director FREEZE R1 record correctly pins FROZEN_R1 and should be preserved as historical evidence.

It must not be reused as the Director record for FROZEN_R2.

After a corrected FROZEN_R2 package commit exists, create a new later Director FREEZE R2 record pinning the new F2 HEAD/TREE and artifact blobs.

## 7. Review conclusion

```text
immutable F sequencing           = PASS
scientific numeric parameters    = PASS
seed identity preservation       = PASS
decision rule                    = PASS
state ceiling / zero science     = PASS
collision allowlist consistency  = FIX_REQUIRED (M-1)

OVERALL =
FAIL / FIX_REQUIRED
```

No Verifier(FROZEN_R1) should run as an acceptance gate.

```text
NEXT_ACTOR =
IMPLEMENTER / DIRECTOR FREEZE R2

NEXT_ACTION =
create immutable FROZEN_R2 package with corrected exact collision allowlist
and a regression gate; then create a new Director FREEZE R2 record; publish
new F2 HEAD/TREE for a fresh Scientific Reviewer.

DO NOT START SCIENCE.
```
