# FRESH_REVIEW_R1 — independent adversarial review of work/prep-s17-r1

- **Reviewed head:** `d9b7efd6737652adffbe71026b29fa1dc052a067` (SUBJECT_HEAD — matches remote tip)
- **Reviewed tree:** `0abed1da7b5ee035d27d9f111189b636c12aa148` (SUBJECT_TREE — matches)
- **Reviewer:** fresh independent agent, no prior involvement; judged only from Git evidence and own re-execution.
- **Method:** fresh clone to /tmp/prep-s17-review; all pins re-derived; full diff inspected; every web claim re-fetched live (2026-10-15); validator attacked with 49 custom adversarial mutations; import validation re-run on freshly downloaded bytes; all machine gates re-executed at the exact SUBJECT_HEAD.
- **Verdict: FAIL** (1 blocking finding — handoff evidence records claim gates that the committed tree does not reproduce). The engineering substance is sound and all substantive source claims were independently confirmed; the blocking defect is record accuracy and is repairable via the project's corrections-event process.

---

## R1 — Pins: PASS

| Check | Result |
|---|---|
| `git rev-parse HEAD` | `d9b7efd6737652adffbe71026b29fa1dc052a067` == SUBJECT_HEAD ✓ |
| `git rev-parse HEAD^{tree}` | `0abed1da7b5ee035d27d9f111189b636c12aa148` == SUBJECT_TREE ✓ |
| `git ls-remote origin refs/heads/work/prep-s17-r1` | `d9b7efd6…` == SUBJECT_HEAD ✓ |
| merge-base(origin/main, HEAD) | `32d3c6840341ad3954d5001235a3cc35b8ca0e01` == BASE ✓ (origin/main tree `474249da8fee669c85aa763274e33a16d4293f40` ✓) |
| History shape | 5 commits, single-parent linear chain from base, no merges/rewrites ✓ |

## R2 — Scope discipline: PASS

- `git diff origin/main HEAD --stat`: exactly 17 files, all within allowed surfaces (WO doc, `EX-PREP-S17-R1/**`, `docs/research/S17_*`, `scripts/knowledge_pack/**`, `tests/test_knowledge_pack.py`, WORK_QUEUE.md). No other paths touched.
- `project/state.json`: blob `b819755783119ecc56be50cab1bc736c09c85b24` identical on both refs; diff empty ✓
- Frozen artifacts: all 15 case-insensitive `frozen` matches in `git ls-tree -r origin/main` plus `docs/research/NANOLAB_REPRO_V0_2_*` plus `scripts/{e2,nl4,nl5,r2,hinge_family}/` byte-identical (blob-level comparison, 0 changes) ✓
- WORK_QUEUE.md: exactly one appended WO-PREP-S17-R1 row ✓

## R3 — Source claims audit (live web, this review's own downloads): PASS with 1 minor

| Claim | Independent result |
|---|---|
| Nanobase structure 196 = 12-file manifest | `GET /api/v1/structure/structure-files?id=196` → 12 files, 1:1 match with pack entries ✓ |
| NE.top sha256 `5074d559…` / 215903 B | reproduced exactly ✓ |
| NE.dat sha256 `c73aeb86…` / 3955400 B | reproduced exactly ✓ |
| remaining 10 Nanobase files (beyond required spot-check) | all 12/12 SHA-256 reproduced exactly ✓ |
| Zenodo 8248808 MD5s (4 zips) | all 4 reproduced exactly ✓ |
| Zenodo sizes | 3/4 match; **`pull_release23.zip` pack says 20 669 125 082 B, Zenodo says 20 691 250 829 B (transposed digits, Δ=22 125 747 B)** — MINOR-1 |
| Zenodo README.md sha256 `7ea24d81…` / 1478 B | downloaded and reproduced exactly ✓ |
| hinges @ `7c8b04a6` get_k.py / hinge_bonds.py / extract_data.py / README.md | all 4 SHA-256 + byte sizes reproduced exactly ✓ |
| hinges license | GitHub API `license: None`; full non-truncated tree (83 paths) contains no LICENSE/COPYING/LEGAL ⇒ REFERENCE_ONLY justified ✓ (tree pin `d730871c…` and push date 2023-03-09 also confirmed) |
| Nature article open access CC BY 4.0 | HTTP 200; JSON-LD `"license":"http://creativecommons.org/licenses/by/4.0/"`; title + pages 226–236 + online 2023-10-19 all match ✓ |
| T7_force.txt trap constants (8694/7374/0.3290/8.8), `input_pull` → `external_forces_file=polymerase_positioning.txt` (absent from 12-file set), `topology=linked.top`/`conf_file=first_conf.dat` (recipe absent), DNA2/salt 2.0/NVT john/dt 0.003 | all verified from freshly downloaded bytes ✓ |

## R4 — Contract validator correctness: PASS (2 minor robustness holes)

- Committed `S17_KNOWLEDGEPACK.json`: `validate_pack` → `[]`, `load_pack` clean ✓
- 49 adversarial probes written by this reviewer (scratch file, never committed): forbidden claim levels (incl. case/whitespace variants), duplicate paths, wrong provenance combos, vendoring under RESTRICTED/FORBIDDEN/UNKNOWN redistribution, VENDORED mode + FORBIDDEN, empty observables + empty missing_inputs, null/empty scalars, bad DOI/sha256/size/role/availability/provenance enums, unknown fields at every level, bad upstream_checksum shapes, bad provenance sha, schema/kind violations. **48/48 rejected as expected.**
- Pack NE/NE_NB/nNE topology/configuration digests match the evidence file `s17-import-validation-R1.json` ✓ (and my own re-downloads).
- MINOR-3: `schema_version: true` (JSON bool) validates as `1` (Python bool/int equality leak).
- MINOR-4: `verify_manifest` has no root containment — a `../`-prefixed ON_DISK_VERIFIED entry verifies a file outside the declared root (demonstrated).

## R5 — Import validation re-execution: PASS

Re-downloaded all pairs to /tmp (never committed) and ran `knowledge_pack.import_validation.import_paired` myself:

| Pair | Counts (nt/strands/particles) | Chain integrity | Deterministic re-import | Structural digest vs evidence |
|---|---|---|---|---|
| NE | 14343 / 161 / 14343 ✓ | 160 linear + 1 circular ✓ | ✓ | `2722f75f…` matches ✓ |
| NE_NB | 14011 / 163 / 14011 ✓ | 162 + 1 ✓ | ✓ | `c34da652…` matches ✓ |
| nNE | 14343 / 163 / 14343 ✓ | 162 + 1 ✓ | ✓ | `93787ca9…` matches ✓ |

Negative controls (my own corruptions): non-UTF-8 byte flip → hard fail; UTF-8-safe digit flip → `ok=False` via chain-integrity error (`n5 link inconsistency at nucleotide 50`) — fail-closed ✓. Observations (MINOR-5, MINOR-6): non-UTF-8 corruption raises an uncaught `UnicodeDecodeError` (still fail-closed, but unstructured), and `canonical_structural_digest` is insensitive to n3/n5 linkage corruption (my linkage-corrupted digest was unchanged; the chain-integrity check is what catches it — the digest name overstates its coverage).

## R6 — Machine gates at exact SUBJECT_HEAD: 3 of 4 PASS, 1 FAILED vs claim

| Gate | Claimed | Observed | Result |
|---|---|---|---|
| `python3 -m unittest discover -s tests -t .` | 675 OK | **668 tests OK, exit 0** (static `def test_` count also 668; base main = 638, so branch adds **30**, not 37) | **CLAIM NOT REPRODUCED** (part of BLOCKING-1) |
| `harness.cli check-consistency` | ok, tasks 19 | `ok:true`, tasks 19, stages 9, experiments 7, exit 0 | PASS |
| `harness.workflow_lint` | blocking 0 | blocking 0, exit 0 | PASS |
| `work_cli validate` all `EX-*/` | 0 FAIL | 56/56 `ok:true` (exit 0 failures); EX-PREP-S17-R1: `ok:true`, status HANDOFF_READY, terminal HANDOFF_COMPLETED present | PASS |

## R7 — Claim ceiling: PASS

All added diff lines scanned: `MODEL_REPRODUCED` / `COMPONENT_CHARACTERIZED` / `ASSEMBLY_VALIDATED` appear only as forbidden-list entries or explicit negations; E5/NL6-001 only as "not started / draft boundary, НЕ dispatch"; U1 "not performed / NOT_ASSIGNED"; R2 "NOT_ACTIVE"; scientific runs = 0 everywhere; NL5-002 left WAITING_HUMAN; PR #54 treated as proposed only. UNKNOWN/UNVERIFIED discipline is genuine: ports UNVERIFIED/UNKNOWN, index mapping UNVERIFIED, linked.top recipe missing, oxDNA pin UNKNOWN, Zenodo sha256 UNKNOWN+NOT_VERIFIED with MD5, Nanobase entry metadata UNKNOWN, smFRET 403/UNKNOWN. No unsupported property is asserted.

## R8 — Process: PASS with 1 minor

- Event types: 0001 WORK_ORDER_STARTED → 0002/0003 CONTINUATION_CHECKPOINT → 0004 HANDOFF_COMPLETED (terminal, last); passport status HANDOFF_READY; `work_cli validate` ok ✓
- Conventional commits ✓; linear single-parent history, no force-push (remote tip == reviewed HEAD) ✓
- MINOR-2: event timestamps are non-monotonic — 0002 stamped `18:05:00.000Z`, AFTER 0003 (`17:39:12.028Z`) and terminal 0004 (`17:45:00.000Z`), although 0002 precedes them in sequence, subject_sha and commit order. `work_cli` enforces monotonicity only for corrections-tail events, so this passes machine gates, but it defeats the git-chronology cross-check the harness comments describe.

---

## Findings

### BLOCKING

**BLOCKING-1 — Handoff evidence records claim gates that the committed tree does not reproduce.**
The tree delivers **30** new tests in a single file `tests/test_knowledge_pack.py` (suite total **668**, all passing), but the handoff records state **37** new tests, a total of **675**, and cite a second file `tests/test_knowledge_pack_import.py` that does not exist at HEAD and never existed anywhere in the branch history (`git log --all` empty). The false/phantom references appear in:
1. `docs/work/WORK_QUEUE.md` WO row: "37 новых тестов …; ветка: 675 tests OK";
2. `docs/work/executions/EX-PREP-S17-R1/summary.md` (deliverables list: the phantom file + "37 тестов"; validation section: "675 tests OK (base 638 + 37 новых)");
3. `docs/work/executions/EX-PREP-S17-R1/evidence-map.json`: `changed_surfaces` lists `tests/test_knowledge_pack_import.py` (also outside the passport `allowed_paths`), `unit_tests` = "675 OK (638 base + 37 new …)";
4. terminal event `events/0004-handoff-completed.json` and `events/0003-…json` `command_refs`: "python3 -m unittest discover … # 675 OK";
5. `docs/research/S17_PREP_AUDIT_R1.md` §8: `python3 -m unittest tests.test_knowledge_pack tests.test_knowledge_pack_import` (second module nonexistent).

Consequence beyond arithmetic: because the claimed import tests live in the phantom file, **`scripts/knowledge_pack/import_validation.py` ships with zero committed test coverage** while the summary advertises "37 тестов (контракт+импорт … count mismatch)". (Its behaviour was independently reproduced by this review — see R5 — so the evidence JSON itself is trustworthy; the *test-coverage claim* is not.) In this project's own discipline (exact pinned evidence, immutable published events, corrections as new events), a HANDOFF_COMPLETED record whose gate line cannot be reproduced at the pinned head must be corrected (corrections events / errata + corrected counts, or actually committing the missing tests) before the Human Gate. The Verifier stage would fail on the same evidence.

### MINOR

- **MINOR-1:** `S17_KNOWLEDGEPACK.json` records `pull_release23.zip` `size_bytes` = 20 669 125 082; Zenodo reports 20 691 250 829 (digit transposition; MD5 correct; the WO row's "46.17 GB" total matches the true sizes, confirming a transcription slip in the pack field). Fix in a pack revision.
- **MINOR-2:** non-monotonic event timestamps (0002 after 0003/0004) — see R8.
- **MINOR-3:** `contract.py` accepts `schema_version: true` as `1` (bool/int equality leak).
- **MINOR-4:** `verify_manifest` lacks root containment (`../` path escape demonstrated).
- **MINOR-5:** `import_paired` raises uncaught `UnicodeDecodeError` on non-UTF-8 corruption (fail-closed, but inconsistent with the structured-errors design).
- **MINOR-6:** `canonical_structural_digest` does not cover n3/n5 linkage columns; linkage corruption can leave the digest unchanged (caught instead by chain integrity). Naming overstates coverage.

## Verdict

**FAIL** — one blocking finding (BLOCKING-1). All substantive engineering claims verified true (sources, digests, import validation, scope, ceiling, gates except the test count); the blocker is confined to evidence-record accuracy in the handoff layer and is repairable with a small corrections pass (correct counts to 668/30 or commit the missing tests; fix evidence-map changed_surfaces/unit_tests; fix summary.md §Deliverables/§Validation and S17_PREP_AUDIT_R1.md §8; WORK_QUEUE row counts; corrections event for the timestamp erratum).

*Review artifacts: `FRESH_REVIEW_R1.md` + `FRESH_REVIEW_R1.json` (this directory), branch `review/prep-s17-r1`.*
