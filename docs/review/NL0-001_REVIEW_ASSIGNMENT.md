# NL0-001 — Independent Review Assignment

Subject under review: `f738bff77f2406552b4383c05989ffc6e56a3bd5`  
Implementer branch: `work/nl0-001-reference-selection-r1`  
Review branch initialized from exact subject: `review/nl0-001-reference-selection-r1`  
Risk: `HIGH`

This file assigns work; it is **not** a review verdict.

## Reviewer attacks

1. Confirm the selected E1 DSDNA8/MD fixture is a suitable first reproducible physical-model reference and that its upstream oracle is read correctly.
2. Confirm selected E2 DOI `10.1021/acsnano.7b00242` is linked to the pinned `gauravarya77/DNA-hinge-simulations` repository and that the five-hinge family/inputs described by the implementer actually exist.
3. Challenge the mapping from spring-length variants to future hinge-angle observable.
4. Check REPORTED vs OBSERVED vs UNKNOWN boundaries, especially 298 K article vs 300 K repository input.
5. Verify rights statements are conservative: public accessibility must not be treated as redistribution permission.
6. Confirm no E0/E1/E2 scientific run or acceptance is implied.

Allowed verdicts: `PASS`, `FAIL`, `INSUFFICIENT_EVIDENCE`.

A fresh reviewer should publish its own evidence and verdict without modifying the implementer subject. Verifier follows if review passes or if the risk policy requires independent evidence confirmation.
