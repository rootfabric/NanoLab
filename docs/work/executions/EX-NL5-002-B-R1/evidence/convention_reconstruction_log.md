# Angle-convention reconstruction log (external executor, BEST_EFFORT evidence)

Goal: implement the package's observable "[0,180] deg, PCA axes, erratum R1
§2.5; detector v2 mutual-nearest + PCA hinge angle, frozen arm manifest" from
package contents only. Validation oracles published in the package:
(a) design.arm_a_nucleotides/arm_b_nucleotides (+ coverage fractions),
(b) design.angle_frame0_deg on the upstream initial conf (frame 0).

## Detector calibration (frame 0)

- Pair geometry measured on upstream confs: WC partners have backbone-site
  (COM) distance ~1.1–1.3, a1·a1 ≈ −0.94 (antiparallel), a3·a3 ≈ −0.93.
  Base site = r + 0.4·a1 (engine model.h POS_BASE; sites along a1).
- v2-style gate detector (COM window [0.9,1.4), a1 < −0.3, mutual-nearest,
  cross-strand) reproduces the published per-frame pair counts:
  my 0b frame t=4000..16000: 3283, 3281, 3317, 3301 vs published
  reference_pairs_v2_count 3292–3301 (E2-R1-C001..C003). MATCH within noise.
- Base-site window [0.1,0.5) mutual-nearest gives 4077–4090 pairs per variant
  (0b: 4077; 11b: 4067; 32b: 4088; 53b: 4081) vs published manifest
  paired-nt counts/2 (0b: 3975; 11b: 3970; 32b: 3998; 53b: 3978): +~100 pairs
  excess that no window/run-length filter removes (extras lie in long
  contiguous duplex runs) -> manifest "paired" set is likely design-based,
  not geometric; design pairing not recoverable from package.
- long_bond proxy (fraction of backbone bonds with length > 1.0, FENE
  divergence limit r0+DR0=0.75+0.25): my 0b t=4000..16000: 0.0546–0.0552 vs
  published replica baselines 0.0554–0.0560 -> definition reproduced.

## Arm-manifest reconstruction attempts (frame-0 angles, deg)

Cards: 0b 66.886745865; 11b 74.357957026; 32b 77.477102136; 53b 132.949606811.

| # | method | 0b | 11b | 32b | 53b |
|---|--------|----|----|-----|-----|
| 1 | helix graph, duplex runs, parallel-threshold grid (10–80 deg) | never two dominant blocks; merges into one ~7200-nt block by thr 50 | same | same | same |
| 2 | coaxial helix merge + contact+parallel grid | fragments (2948+1668+...) | fragments | fragments | fragments |
| 3 | nucleotide parallel blocks on a3 | single block at all thr 0.8–0.95 | same | same | same |
| 4 | nucleotide parallel blocks on helix axis h=a1×a3 | single block ≤0.9 (53b splits at 0.9: 3762/2752) | single | single | splits 0.9 only |
| 5 | 2-line mixture EM (perp distance) | 66.83 | 65.0 | 63.7 | 117.2 |
| 6 | spectral (Fiedler) bisection + PCA axes | 63.62 | 65.00 | 63.72 | 114.88 |
| 7 | #6 + vertex-exclusion R (scan 0–30) | 67.35 @R12 | 70.3 @R20 | 68.4 @R16 | 118.2 @R16 |
| 8 | bisector-plane EM (unbalanced) | 76.1 | 70.6 | 79.9 | 119.6 |
| 9 | size-forced residual ranking (spectral init) | 67.65 | 65.32 | 71.48/77.31* | 117.3/122.7* |
| 10 | #9 + vertex exclusion R=8 (C2) | 67.30 | 75.16 | 79.59 | 119.05 |
| 11 | tip directions (vertex→distal decile) | 66.18 | 69.72 | 71.20 | 118.59 |
| 12 | polyline local direction at vertex | 44.5 | 48.9 | 50.1 | 103.9 |

*two EM outcomes depending on init. No single generic rule reproduces the
published (counts, angle) pairs for all four variants simultaneously; residual
frame-0 angle errors of the best families are ±0.4–2° for 0b/11b/32b and
−14° for 53b, exceeding the reference envelopes' widths (0b 2.14°, 11b 2.37°,
32b 2.38°, 53b 4.24°).

Structural facts established:
- structures are V-shaped; vertex and two arm bands; 53b nearly straight
  (132.9°); arm counts asymmetric in cards (32b 4814/3190) while any spatial
  bisection gives near-symmetric halves (~4248/3928) -> manifest arms are not
  a simple spatial bipartition;
- 74b failure message reveals PARALLEL_GRID threshold keys (e.g. 0.85) and
  block size tables, but the block-construction algorithm is not published.

## Consequence

Frozen observable convention not implementable from the package alone ->
PORTABILITY_FINDING; contract classification per card = INCONCLUSIVE;
BEST_EFFORT_NOT_CONTRACT angle series reported under two documented surrogate
conventions (C1 spectral-split arms; C2 vertex-exclusion + size-forced arms),
frozen at frame 0 per variant, plus frame-0-offset-calibrated diagnostics
(clearly labelled, not for contract use).
