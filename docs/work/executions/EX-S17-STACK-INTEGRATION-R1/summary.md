# EX-S17-STACK-INTEGRATION-R1 — S17 R3+repair+CLI integration candidate

Accepted base main fb3148b (includes merged R2 #59, source R4 #69, INFRA3/U1 dry-run #70). This branch imports **55 exact source blobs** from original R3+Repair+CLI (PR #71), plus final exact repair verification event from #67 and append-only Work Queue; provenances are in evidence/source-blob-map.json. Never merge original faulty R3 #60 alone.

Erratum child `EX-PREP-S17-R3-OVERHANG-ERRATUM-R1`: seven follower 21nt declarations corrected to source-pinned 20nt segments. RED CI #39523456603 had 930 tests/7 FAIL; GREEN CI #39524159028 had 930 tests **OK**, F01–F04 retained. No scientific run, real original follower NOT_RECONSTRUCTED, no NL5/6/7 status changed.

**Fresh standalone R3 Reviewer and final integration exact-head Verifier still WAIT_EXTERNAL.** Do not claim independent acceptance or merge without these gates; original #60/#67/#71 remain as durable sources until integrated candidate accepted.

## Timestamp correction (pre-acceptance, explicit exception)

Hosted CI #39524871712 rejected identical timestamps across events 0002–0004. Original Git blobs 0002=00ba2a3c239a3e70577bcf0d1090f942ecacb17b, 0003=10303b5b4abb7829995402d357da1424ac779696, 0004=f6e3bffca2a52a93f5ce84425241a08e7d746ee4 remain addressable in history at 4db05c2dd9663c08244cefaf440b6a49c0703c72. In a new non-force commit only event 0003/0004 timestamps were normalized (+1/+2ms). This is a **documented exception to strict append-only event-file immutability** before acceptance, not an altered scientific result. Event 0005 records the correction; fresh Reviewer must review this exception.
