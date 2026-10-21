# EX-S17-STACK-INTEGRATION-R1 — S17 R3+repair+CLI integration candidate

Accepted base main fb3148b (includes merged R2 #59, source R4 #69, INFRA3/U1 dry-run #70). This branch imports **55 exact source blobs** from original R3+Repair+CLI (PR #71), plus final exact repair verification event from #67 and append-only Work Queue; provenances are in evidence/source-blob-map.json. Never merge original faulty R3 #60 alone.

Erratum child `EX-PREP-S17-R3-OVERHANG-ERRATUM-R1`: seven follower 21nt declarations corrected to source-pinned 20nt segments. RED CI #39523456603 had 930 tests/7 FAIL; GREEN CI #39524159028 had 930 tests **OK**, F01–F04 retained. No scientific run, real original follower NOT_RECONSTRUCTED, no NL5/6/7 status changed.

**Fresh standalone R3 Reviewer and final integration exact-head Verifier still WAIT_EXTERNAL.** Do not claim independent acceptance or merge without these gates; original #60/#67/#71 remain as durable sources until integrated candidate accepted.
