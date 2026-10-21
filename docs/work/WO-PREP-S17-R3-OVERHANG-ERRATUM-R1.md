# WO-PREP-S17-R3-OVERHANG-ERRATUM-R1 — resolve seven 21-nt follower overhang declarations to pinned 20-nt pair recipe

Owner work continuation: 2026-10-21; scope C0_SOFTWARE_ONLY; 0 scientific runs; no paid compute. Follows R3-repair `ERRATUM-1` recorded in PR #67 and the original pinned R3 recipe (`s17-r3-df-interface-recipe.json`, SHA-256 `5f485b0ac8d1e822a424a73f065ede7df36245ee4cd8a8e27cbe93681f1b61b6`).

Work base: integration/s17-r3-repair-assembly-cli-r1 @ `7236461353293ca1bb542b0404e385cccb681e82`. Original R3 follower component spec holds seven overhang-segment values 21 nt long (DFC-02,03,04,05,07,08,09). All ten published pairs have explicit 20-nt reciprocal reverse complements; driver side 10/10 matches. These 7 adjacent extra nucleotides in the follower declarations are not part of the published paired segment. Do NOT change pinned full ODN sequence, metadata, recipe or science. Fix only seven `chemistry.overhang_segment` values from pinned `follower_segment`, respecting the `follower_odn` join. Assert exact offsets/substrings, complementarity and uniqueness in offline regression tests.

Allowed: `docs/research/S17_R3_COMPONENT_FOLLOWER.json`; new `tests/test_s17_r3_overhang_erratum.py` plus a narrow update to `tests/test_s17_r3_assembly.py` (existing historical negative assertion becomes corrected-case positive assertion plus deliberately reintroduced 21nt tamper refusal); `docs/work/WO-PREP-S17-R3-OVERHANG-ERRATUM-R1.md`; `docs/work/executions/EX-PREP-S17-R3-OVERHANG-ERRATUM-R1/**` and one append-only WORK_QUEUE line if needed. Forbidden: R2, NL5 frozen artifacts, project state/plan, physics code, original recipe, DOI/source pins, topology/config replacements, direct main/force-push, artificial anchors. Claim ceiling PINNED_IMPORT_VERIFIED (sequence-level source only); true S17 follower topology/config still UNKNOWN and original assembly NOT_RECONSTRUCTED.

Required: durable START, RED→GREEN negative tests (or clearly identified existing RED), exact git diff seven values only, full offline suite & Harness CI, independent Reviewer/Verifier on final integration subject before merge. No self-accept.

## 2026-10-21: execution handoff

Seven exact 20nt corrections, RED hosted #39523456603 → GREEN #39524159028 (930 tests OK). Full ODN sequences and source pins untouched; reviewer/verifier WAIT_EXTERNAL.
