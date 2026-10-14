# FRESH_REVIEW_R2 — independent re-review of work/prep-s17-r1 after Repair R2

- **Reviewed head:** `527f588207f96371ff664b830eedcc575746f194` (matches remote tip — verified via `git ls-remote`)
- **Reviewed tree:** `2428f4ccfb3ad331b160a9a9613ef4f09009ef5f` (matches)
- **Re-review of:** FRESH_REVIEW_R1 (verdict FAIL, 1 blocking + 6 minor) at `d9b7efd6737652adffbe71026b29fa1dc052a067`; repair pushed as 3 commits on top of the R1 subject (`3e405ab` substance → `aacdeb9` 0005 subject pin + accidental 0006 → `527f588` 0006 dropped). `d9b7efd` verified as ancestor (no rewrites, non-force).
- **Method:** fresh clone to /tmp/prep-s17-review-r2; pins re-derived; repair diff inspected file-by-file (incl. word-level diff of the WORK_QUEUE row); all machine gates re-executed at the exact new head; my 49-probe adversarial suite re-run against the hardened validator; import validation re-run on the same freshly-downloaded source bytes (cached from R1 review) against the new R2 evidence digests; both corruption negative controls re-executed.
- **Verdict: PASS** (blocking resolved; all six R1 minors addressed and independently re-verified; 1 new minor found, non-blocking).

---

## R2.1 — Pins and history: PASS

| Check | Result |
|---|---|
| remote tip / HEAD | `527f588207f96371ff664b830eedcc575746f194` == pin ✓ |
| `HEAD^{tree}` | `2428f4ccfb3ad331b160a9a9613ef4f09009ef5f` == pin ✓ |
| merge-base(origin/main, HEAD) | `32d3c6840341ad3954d5001235a3cc35b8ca0e01` ✓ |
| R1 subject ancestry | `git merge-base --is-ancestor d9b7efd HEAD` → ancestor (no rewrite) ✓ |
| repair commits | 3e405ab (repair substance), aacdeb9 (0005 subject pin + accidental 0006 terminal), 527f588 (0006 dropped) — linear, conventional prefixes ✓ |

## R2.2 — BLOCKING-1 resolution: RESOLVED

- `tests/test_knowledge_pack_import.py` now exists in the tree (127 lines, 9 tests: 7 original + 2 hardening); statically counted `def test_`: `test_knowledge_pack.py` = 32, `test_knowledge_pack_import.py` = 9 → 41 new; full suite at the exact head: **`Ran 679 tests in 50.350s / OK`, exit 0** — the advertised "679 (638 base + 41)" is now true.
- The R1 arithmetic is now recorded truthfully everywhere checked: summary.md КОРРЕКЦИЯ section ("R1 668 = 638+30; repair head 679 = 638+41: 32 + 9"), WORK_QUEUE КОРРЕКЦИЯ R2 block (same numbers), evidence-map.json `unit_tests` corrected, `corrections_r1` block added, event 0005 records the correction with `subject_sha` pinned to `3e405ab`. R1 text in summary.md / S17_PREP_AUDIT_R1.md / WORK_QUEUE row was NOT mass-retro-edited: corrections are appended blocks (verified by prefix/word-level diff); events 0001–0004 and passport.json are byte-identical to the R1 head (the allowed_paths omission is recorded as an erratum instead of an edit).
- `import_validation.py` now has committed test coverage (positive import, whitespace stability, content sensitivity, invalid base, broken neighbour link, truncated conf, count mismatch, non-UTF-8, linkage sensitivity).

## R2.3 — R1 minors: all addressed and re-verified

| ID | Fix claimed | My independent re-execution |
|---|---|---|
| m-1 | pack size 20669125082 → 20691250829 | pack diff = exactly that one line; value matches the Zenodo API size I fetched in R1 (`20691250829`) ✓; pack still validates clean |
| m-2 | timestamp errata recorded | event 0005 + summary.md КОРРЕКЦИЯ record the 0002-vs-0003 erratum; events untouched ✓ |
| m-3 | schema_version bool guard | `isinstance(bool)` guard added; my probe `schema_version=true` now REJECTED ("boolean is not an integer") + unit test ✓ |
| m-4 | verify_manifest root containment | `resolve()` + `is_relative_to()` guard; my outside-root `../outside.txt` scenario now returns "path escapes the verification root" (previously verified a file OUTSIDE root) + unit test ✓ |
| m-5 | non-UTF-8 → ImportValidationError | my byte-flip corruption now raises `ImportValidationError("topology is not valid UTF-8…")` instead of raw UnicodeDecodeError + unit test ✓ |
| m-6 | linkage-sensitive structural digest | digest now includes `topology_linkage_sha256` over full `sid:base:n3:n5` rows; my linkage-corrupted NE.top now yields a **different** digest AND still fails via chain integrity; all three pair digests regenerated and match evidence R2 ✓ |

New R2 evidence (`s17-import-validation-R2.json`, schema_version 2, explicit `supersedes` of R1; R1 file kept as historical) — reproduced on my fresh downloads:
- NE: 14343/161, chain 160+1, digest `c227e0b585983820…` ✓ match
- NE_NB: 14011/163, chain 162+1, digest `5e7610a84bed1881…` ✓ match
- nNE: 14343/163, chain 162+1, digest `20c3912671280b71…` ✓ match
- SHA-256 of all six topology/configuration files still match the pack pins ✓

My full 49-probe adversarial suite (claim inflation, duplicates, provenance combos, vendoring gates, empty/null discipline, enum violations, unknown fields, traversal, bool leak): **49/49 behave as expected** against the hardened validator; committed pack still validates clean via `validate_pack` and `load_pack`.

## R2.4 — Gates at exact new head: PASS

| Gate | Claimed | Observed |
|---|---|---|
| unittest | 679 OK | **679 tests OK, exit 0** ✓ |
| check-consistency | ok, tasks 19 | ok:true, tasks 19/stages 9/experiments 7, head/tree == pins, exit 0 ✓ |
| workflow_lint | blocking 0 | blocking 0, exit 0 ✓ |
| work_cli all EX-* | 0 FAIL | 56/56 `ok:true`; EX-PREP-S17-R1 ok:true, HANDOFF_READY, single terminal HANDOFF_COMPLETED, `has_post_terminal_corrections: true` (0005 = sanctioned corrections-tail CONTINUATION, timestamp 18:25Z ≥ terminal 17:45Z, valid 40-hex subject) ✓ |

## R2.5 — Scope and boundaries of the repair: PASS

- Repair diff (d9b7efd..HEAD) touches only: `docs/research/S17_*`, `docs/work/WORK_QUEUE.md`, `EX-PREP-S17-R1/**` (event 0005, evidence R2, evidence-map, summary), `scripts/knowledge_pack/*`, `tests/test_knowledge_pack*.py` — all within the WO's allowed surfaces (the import-test file itself is the subject of the recorded allowed_paths erratum, disclosed rather than hidden).
- `project/state.json` blob identical to main; all frozen artifacts + `NANOLAB_REPRO_V0_2_*` + `scripts/{e2,nl4,nl5,r2,hinge_family}` byte-identical (re-verified at new head) ✓.
- Events 0001–0004 and passport.json untouched since R1 head ✓. Claim ceiling unchanged: 0 scientific runs, no status promotions, PINNED_IMPORT_VERIFIED wording preserved ✓.

## Findings (this re-review)

### MINOR
- **MINOR-R2-1:** In the WORK_QUEUE WO row, the R1 Acceptance cell was edited by exactly one word — "fresh review PASS" → "fresh **re-**review PASS" — without being declared inside the appended КОРРЕКЦИЯ R2 block, while that block states the R1 records were preserved "без ретро-редакции". Semantically accurate and git-visible, but it is a literal (if tiny) retro-edit of R1 text that the block disclaims. Cosmetic; correctable by declaring it in the corrections text or reverting the word.

### Observations (not findings)
- The repair history contains transient pre-merge states: 0005 was first committed with `"__REPAIR_COMMIT__"` placeholder subject_sha (3e405ab) and pinned in the next commit; a duplicate terminal 0006 was added (aacdeb9) and dropped at the tip. The reviewed head conforms (single terminal, valid 40-hex, work_cli ok); gates are claimed and verified only at the reviewed head, and these iterations never reached canonical main.
- evidence-map.json `changed_surfaces` retains `tests/test_knowledge_pack_import.py` — accurate as of this head (the file now exists), with the R1 omission documented in `corrections_r1.errata`.

## Verdict

**PASS** — the blocking finding is resolved (real tests committed; all advertised counts now match reality: 679 = 638 + 41, verified by execution at the exact pinned head), all six R1 minors are fixed and were independently re-verified by re-execution, repairs stayed in scope, and the corrections-tail event structure conforms to work_cli rules. One new cosmetic minor (MINOR-R2-1) can be folded into the next corrections pass or accepted as-is; it does not affect any substantive claim.

*Review artifacts: `FRESH_REVIEW_R2.md` + `FRESH_REVIEW_R2.json` (this directory), branch `review/prep-s17-r1` (commit on top of the R1 review `3370be06`).*
