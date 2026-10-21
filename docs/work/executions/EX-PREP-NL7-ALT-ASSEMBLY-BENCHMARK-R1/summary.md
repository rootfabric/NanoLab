# EX-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1 — implementation handoff (C0 only)

**Outcome: IMPLEMENTED_WITH_SOURCE_GAP / BLOCKED_SOURCE**. Priority S23 Narcissus+Echo (published two different DNA-origami halves); secondary S22 moDON (reusable monomer with xy/z modular interfaces). Nanobase structures 256/257 names are inherited from accepted S17 R4 reporting and not byte-verified in this execution; structure 263 caDNAno is cited in moDON article's Data Availability but original bytes/rights are still UNKNOWN.

Delivered a provisional BIBLIOGRAPHIC source manifest, comparative audit and fail-closed offline structural/rights/source-integrity gate. **0 external CAD/oxDNA raw bytes downloaded, 0 scientific runs, 0 new true two-part assembly**. No new source pins or scientific claims.

CI history is preserved: #39530605362 initially failed on two new test expectations; corrected. #39530778687 attempt 1 failed on two inherited U2 temp-directory Git cleanup races (`Directory not empty: objects`). Attempt 2 on unchanged code subject 06569eaf9360ba363695c508ac2b9ff4c02cef3b passed **828 tests OK**, hosted consistency, work-cli, security lint and JSON checks. These are software checks only, not a scientific reproduction.

Independent fresh Reviewer and separate exact-head Verifier = WAIT_EXTERNAL. Merge = Human Gate. Next actor with legitimate Nanobase access should retrieve actual 256/257 origami source files, review each file's rights, pin SHA-256, and validate original topology/config/anchor-map; until then source remains BLOCKED_SOURCE.

## Adversarial hardening R1.1 — 2026-10-21

New RED CI [#39538287299](https://github.com/rootfabric/NanoLab/actions/runs/39538287299): 830 tests / **2 expected falsifier FAIL** (numeric nonterminal strand anchor; fake exposed segments not in verified topology). New GREEN CI [#39538562254](https://github.com/rootfabric/NanoLab/actions/runs/39538562254) on exact implementation subject `3d0b55b948c6d1decb5863d8f1bf528c1abf9c10`: **832 tests OK**. Source validator now binds declared ssDNA overhangs to terminal n3/n5 indices and bases in 5′→3′ convention; still cannot prove an overhang is unpaired/exposed or experimentally hybridizes — independent original CAD/model evidence and review needed. Original R1.0 CI evidence remains preserved. Initial passport incorrectly identified base commit `fb3148b46a9638167168a46cb170902a4ad9e8d2` as `base_tree_sha`; changed to exact canonical tree `1275a3faba16b6e9528651b12deec83b4337d6f0` in a new commit with this explicit audit note and event (prior blob remains in history).


## Adversarial hardening R1.2 — 2026-10-21

Three independent new negative controls found further false-positive outcomes in the offline source gate. [RED H0 #39547500409](https://github.com/rootfabric/NanoLab/actions/runs/39547500409), test-only HEAD b0945180cda58cab3a8a8d3edfbf67ff50603376: **835 tests / 3 expected FAIL** (A/B-swapped duplicate DNA terminal, zero-norm particle orientation, NaN configuration box). All three previously incorrectly yielded TEST_FIXTURE_STATIC_INPUTS_OK.

The narrow repair reserves every topology nucleotide for at most one declared interface bond, including opposite-terminal segment overlap; checks positive finite box dimensions and calls the existing strict configuration orientation validator. Unwrapped oxDNA PBC positions are intentionally not prohibited. Synthetic controls also distinguish two nonoverlapping 6nt opposite-end ports (PASS) from two overlapping 8nt opposite-end ports (BLOCKED). [GREEN H0 #39547978810](https://github.com/rootfabric/NanoLab/actions/runs/39547978810) on exact code/test HEAD a8b3512a64d3efc2948a6aa820aa7731151a7f4d: **837 tests OK / hosted checks 5 of 5 PASS**.

This remains C0 input-file preflight, NOT evidence of exposed ssDNA, binding chemistry, stability or function. Source state BIBLIOGRAPHIC / BLOCKED_SOURCE; 0 external CAD/oxDNA raw bytes observed, 0 scientific runs; independent Reviewer and separate exact-head Verifier remain WAIT_EXTERNAL. A final documentation-only commit requires its own subsequent H0 verification.
