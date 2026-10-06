# NL5 v0.2 FROZEN_R2 — Fresh independent VERIFIER verdict R1

```text
VERIFIER_ID      = NL5-V02-FREEZE/FRESH_VERIFIER_R2
VERDICT          = VERIFIED
VERIFIED_HEAD    = 60da9a846511265a8ac7564da088c3d74cb073f0  (F2_HEAD)
VERIFIED_TREE    = e565c8a6cee9e829fac14008ebc9c2ea1609931d  (F2_TREE)
FROZEN_REVISION  = FROZEN_R2 (candidate basis R4)
DIRECTOR_FREEZE  = a2f7304ebbb5973b81cf49dee60c21c85c6a974d (strict descendant of F2)
REVIEW_BRANCH    = review/nl5-v02-frozen-r2-scientific-review-r1 (tip d63eb5c; F2 + 3 review-record commits)
REVIEW_VERDICT   = PASS (recorded by fresh Reviewer; NOT used as evidence — every fact below reproduced independently)
VERIFIER_BRANCH  = verify/nl5-v02-frozen-r2-r1 (created from exact F2_HEAD; F2 untouched)
SCIENTIFIC_RUNS  = 0
R2               = WAITING_HOST / NOT_ACTIVE
AUTHOR_U1        = NOT_ASSIGNED
external_reproductions = 0
NL5              = IN_PROGRESS
NL6-001          = LOCKED (PLANNED, dependency-locked)
```

- Role: fresh independent **VERIFIER** (no implementer/reviewer conclusion reused as proof)
- Verdict: **VERIFIED**

- Verified subject (exact):
  - `verified_head` = `60da9a846511265a8ac7564da088c3d74cb073f0` (F2_HEAD)
  - `verified_tree` = `e565c8a6cee9e829fac14008ebc9c2ea1609931d` (F2_TREE)
- Verifier branch: `verify/nl5-v02-frozen-r2-r1`, based from **exact F2** (not from Director/handoff/reviewer tips), created after a fresh fetch of `rootfabric/NanoLab`.
- Machine record: `FRESH_VERIFIER_R2.json` (`record_kind = VERIFIER_VERDICT`, `issuer_class = INDEPENDENT_VERIFIER`).
- Raw artifacts: `verify_frozen_r2/` (git identity, contract delta, seed digests, gate report, M-1 matrix, independent scan, repo validation).

All facts below were reproduced independently in a clean worktree checked out at F2.

## 1. Immutable Git identity — PASS

- `git cat-file -t 60da9a8…` → `commit`; `git rev-parse 60da9a8…^{tree}` → `e565c8a6cee9e829fac14008ebc9c2ea1609931d` (exact match to F2_TREE).
- Artifact blobs resolved from the Git object database; SHA-256 recomputed from `git cat-file blob` bytes (and verified byte-identical to worktree files):

| artifact | blob SHA-1 | SHA-256 |
|---|---|---|
| protocol `docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md` | `4835719622bae49a8e8b480536a482b4b222d408` | `2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d` |
| contract `…/repro-v0-2-freeze-contract-FROZEN_R2.json` | `d6a9ccde4d1dadf42d1a8cd9b88faa02646cf70b` | `7e6476544e82af73d5d7e0672666ece99bf4d499a0da30645b02886bcdc45b3a` |
| seed record `…/repro-v0-2-seed-record-FROZEN_R2.json` | `0164e0e3f5dda6dbf63174df3730b1bd921d2c76` | `8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28` |

All six expected values match the binding exactly. Pinned scan object `a9d7d07fa264e9907b67ca244b00ba2da3430b0f` exists (commit; tree `b3b35d566d1a26f970225845a7b4ecf5ce63cb70`).

## 2. Director sequencing — PASS

- `a2f7304ebbb5973b81cf49dee60c21c85c6a974d` (Director FREEZE R2) is a **strict descendant** of F2 (`git merge-base --is-ancestor`: F2 ancestor of D2 = yes; D2 ancestor of F2 = no; D2 parent = F2).
- `DIRECTOR_FREEZE_R2.json` pins exact F2 HEAD/TREE and exact artifact blobs/digests — every pin re-checked against my own computation: all match.
- HG-B binding re-verified from Git bytes: blob `61d1491233aeb2537f9800d6183def5b8fb0c8e0`, sha256 `b68dd341…f49d2c9`, decision `APPROVED`, issuer `HUMAN_GATE_OWNER`, candidate `R4`.
- FROZEN_R1 preserved unamended: F1 head `cb91ade761f6802fc40c500761d3e35022408822` and Director R1 record commit `4236e0c7cfb19de2687a8f0d3be3641cc1b000d4` exist; F1 is an ancestor of F2 (historical FIX_REQUIRED attempt intact).

## 3. Scientific delta vs approved PRE_DATA_R4 — PASS

Independent leaf-level comparison of the F2 contract vs `repro-v0-2-freeze-contract-PRE_DATA_R4.json`:

- 310 leaves on both sides, 310 common.
- Changed leaves: exactly `scientific_subject.candidate_doc_path`, `scientific_subject.freeze_status`, `scientific_subject.seed_record_path`.
- **307 / 310 leaves unchanged**; unexpected scientific delta = **NONE**.

Approved values remain exact in the F2 contract: N = 64/64/10/10; N_min = 52/52/8/8; replacement quotas = 12/12/2/2 pairs; confirmatory runs = 296; replacement cap = 56; max_runs = 352; wall = 560 h/platform; δ = 0.5; bootstrap = 10000; paired design with standard TOST equivalence semantics (protocol §7/§8.2; contract `bootstrap.scheme = PAIRED`); 74b excluded (`NOT_MEASURED / KNOWN_GAP`, «значения 74b запрещены»); replacement only for `FAILED_TECHNICAL`.

## 4. Seed identity — PASS

- F2 seed record is **byte-identical** (`cmp` clean; same blob `0164e0e3…`; same sha256 `8e844bff…`) to both the approved R4 PRE_DATA seed record and the FROZEN_R1 seed record.
- All record digests recomputed from a verifier re-implementation of the digest recipes: logical `record_sha256 = eb4ab3f8…`, full `record_r4_sha256 = 51a88192…` (= `contract.seed_record_r4_sha256`), `replacement_pool_sha256 = 369a63c0…` (= contract binding). All MATCH.
- Seeds (148 confirmatory), bootstrap seeds/indices, replacement pools, skips (41), cursors (`indices_consumed = 74/75/20/20`, `next_candidate_index = 75/76/21/21`), quotas and the 34-seed exclusion list: all MATCH between record and contract.

## 5. M-1 allowlist binding (principal gate) — PASS

- F2 protocol contains **exactly one** `scan-allowlist-v1` machine block; ordered exact paths **equal** `contract.seed_generation.scan_allowlist_paths_exact`:
  1. `docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md`
  2. `docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/repro-v0-2-seed-record-PRE_DATA_R4.json`
- Pinned scan tree `a9d7d07fa264e9907b67ca244b00ba2da3430b0f` — present and used by the real scan.

Negative matrix (all run through the real gate CLI, `--repo-root` = F2 worktree) — **10/10 FREEZE_GATE_FAIL** with the intended failure semantics; CLI wrong frozen allowlist → **exit 3**:

| # | control | observed |
|---|---|---|
| N1 | FROZEN_R1-style frozen-package paths in the block | FAIL, `declaration != contract` |
| N2 | raw FROZEN_R1 protocol | FAIL (incl. `scan-allowlist-v1 block not found`) |
| N3 | missing block | FAIL, `block not found` |
| N4 | duplicate block | FAIL, `exactly one is allowed` |
| N5 | extra exact path | FAIL, `declaration != contract` |
| N6 | order drift | FAIL, `ordered exact comparison` |
| N7 | malformed line | FAIL, `malformed content line` |
| N8 | non-consecutive `path_N` | FAIL, `consecutive 1..K` |
| N9 | frozen-only block in PRE-DATA R4 package | FAIL, `declaration is FROZEN-only` |
| N10 | CLI wrong frozen allowlist | exit 3 |

Positive controls — **2/2 PASS**: P1 F2 exact block == contract → gate PASS (PREFREEZE_VALIDATION_PASS / FROZEN / DISPATCH_BLOCKED / dispatch_ready=false); P2 historical PRE_DATA R4 without the frozen-only block → gate PASS (NOT_FROZEN).

Independent verifier-written pinned-tree scan (own `git grep -I -F -l -e <seed> a9d7d07… --` implementation, not the library's): **176/176** accepted identities clean outside the allowlist; **41/41** recorded skips each have ≥ 1 non-allowlisted literal hit.

Transparency note (non-blocking): the PRE_DATA_R4 seed-record allowlist path postdates the pinned tree and therefore does not exist in it; as an exact-path entry it is inert and cannot mask any hit. The machine binding (protocol block ↔ contract, ordered exact) is exact and fail-closed; all scan invariants hold.

## 6. Real frozen gate with pinned-tree scan rerun — PASS

```
PYTHONPATH=scripts python3 -m nl5.repro_v02_freeze_contract gate \
  --contract …/repro-v0-2-freeze-contract-FROZEN_R2.json \
  --protocol docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md \
  --record …/repro-v0-2-seed-record-FROZEN_R2.json --repo-root .
```

exit 0; `gate = PASS`; `validation_stage = PREFREEZE_VALIDATION_PASS`; `freeze_status = FROZEN`; `dispatch = DISPATCH_BLOCKED`; `dispatch_ready = false`. Scan rerun executed (no `--no-scan-rerun`). `PREFREEZE_VALIDATION_PASS` is understood as internal consistency only — the authoritative freeze fact remains F2 + Director FREEZE R2.

## 7. Full repository validation — PASS (actual counts)

- `python3 -m unittest discover -s tests -t . -v` → **Ran 605 tests … OK**, exit 0 (0 failures / 0 errors / 0 skips).
- `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` → ok=true, 0 errors, 0 warnings (stages 9, tasks 19, experiments 7; head/tree = F2).
- `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` → ok=true, 1 workflow, 0 violations, 0 blocking.
- Every `EX-*` validated with the hosted-CI Check 3/5 loop (`python3 -m harness.work_cli validate`): **51/51 OK**, 0 FAIL.
- Hosted-CI Check 1/5 equivalent JSON sweep: 1325 tracked JSON files, 0 invalid; the 4 pinned non-JSON evidence paths digest-match their CI pins.

## 8. Authority / dispatch ceiling — verified unchanged

- Fresh Verifier(F2) record did **not** exist in F2 before this verdict (`docs/evidence/NL5-V02-FREEZE/` in F2 contains only `DIRECTOR_FREEZE_R1.*` and `FRESH_SCIENTIFIC_REVIEW_R1.*`).
- `r2_activated = false`, `r2_status = WAITING_HOST / NOT_ACTIVE`, `author_u1 = NOT_ASSIGNED`, `new_science_without_r2 = HARD_BLOCKED` (`config/infra/r2-activation.v1.json`).
- `machine_launch_authorized = false`, `launch_gate = HUMAN_PROTECTED_WRITER` (Director FREEZE R2 record; gate report blocker requires Director FREEZE + HG-B + review PASS + verify VERIFIED + R2 ACTIVE before any plan).
- Ceiling: SCIENTIFIC_RUNS (v0.2 campaign) = 0; `external_reproductions = 0`; `NL5 = IN_PROGRESS`; NL6-001 LOCKED (PLANNED, dependency-locked).

## Boundaries respected

No science started. R2 not activated. NL5 not accepted. NL6 not unlocked. This record only adds verifier evidence on top of exact F2; canonical state files are untouched.

## Next (per protocol, for the Director)

`NEXT_ACTOR = DIRECTOR / integration preparation` — integrate F2 tooling + FROZEN_R2 + D2 evidence through PR/hosted CI, preserving exact F2 review/verify bindings; in parallel continue R2 native Ubuntu activation.
