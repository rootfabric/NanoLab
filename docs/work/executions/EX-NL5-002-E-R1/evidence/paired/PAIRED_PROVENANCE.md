# Paired platform-sensitivity analysis — provenance note (EX-NL5-002-E-R1)

Executed: 2026-09-26, SCIENTIFIC_OPERATOR / RECOVERY AGENT (DESKTOP-QNAGSTI),
AFTER the P1-complete evidence commit landed on the live branch
(P1_COMPLETE_HEAD = eb8ccf09789bd2d3feb3e44821968ed6cc6d887f, parent
24f78c324036daf10851bc8fc3c1e0ea6625cd67, canonical base d07e75e68c20599e4b942aefb20b4b3922985219).

## Inputs (Git-published evidence only)

- P1: `evidence/p1/analysis/PLATSENS-P1-*_analysis.json` (20 packaged reports;
  final attempts per slot, highest -R<N> where retries exist: 0B S009-R21,
  0B S010-R14, 32B S001-R14, 32B S002..S006-R13).
- P2: `evidence/p2/analysis/PLATSENS-P2-*_analysis.json` (20 packaged reports).
- Frozen seed identity: `evidence/seeds_runmap_p1.json` and
  `evidence/p2/seeds_runmap_p2.json`.

## Mechanical pairing gate (all PASS)

- 10 complete pairs per variant (0b, 32b); no missing slots on either leg.
- Seeds: P1 seed == P2 seed == frozen WO seed for every S001–S010 (both runmaps
  identical; packaged analyzer may store `seed: null` in the report — accepted
  B-R2 precedent — so the gate uses the committed runmaps, not the report field).
- Variant and steps identical per pair (report `window_steps`: 0b 200000,
  32b 150000 on both legs).
- Package `nanolab-components 0.1.1` (RELEASE_MANIFEST sha256 88c1f580… exact
  match on both legs, `evidence/logs/package_verification.txt` +
  `evidence/p2/logs/package_verification.txt`); single frozen analyzer
  `convention/analyze_hinge.py`; engine commit 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591
  both legs (fresh per-platform builds; P1 binary sha256 363356b9…, P2 size-matched
  B-R2 build convention) — see passports and digest manifests.

## Tooling note (deviation from committed tool, mechanical only)

The committed `paired_tooling/paired_stats_platsens.py` (24f78c3) keys report
slots by `run_id.split("-")[-1]`, which cannot parse final-attempt IDs carrying
retry suffixes beyond its design horizon (-R13/-R14/-R21 here), and its gate
reads the `seed` field that the packaged analyzer leaves null on this file
shape. The statistical core of this directory's implementation
(`paired_analysis.py`) is VERBATIM the frozen plan
(passport.statistics_frozen_pre_data): raw MAD (no 1.4826),
within_v = median(MAD_P1, MAD_P2), ratio degenerate rules, bootstrap
`random.Random(902107)`, 10000 paired-index resamples, percentile CI95 with
linear interpolation, frozen decision rule and WO aggregation.

## Cross-validation

Two independent operator implementations of the frozen plan were run on the
same Git evidence:

1. `evidence/paired/paired_analysis.py` (this directory);
2. an independent implementation (`C:\NanoLab\paired_analysis.py`, session
   tooling, identical spec, independently written loader).

Both produced IDENTICAL statistics for both variants (shift, CI95, MADs,
within, ratio, verdicts). The committed `paired_tooling` self-test
(--self-test, synthetic data only) also PASSes and its documented algorithm
matches line-for-line.

## Result summary (details in paired_platform_sensitivity.json)

```text
0b : shift = +0.684695 deg, CI95 = [-0.550264, +1.199044] (contains 0),
     within = 1.254651, ratio = 0.5457  -> PLATFORM_INSENSITIVE
32b: shift = -1.207386 deg, CI95 = [-2.090433, +2.149149] (contains 0),
     within = 0.915862, ratio = 1.3183  -> PLATFORM_INSENSITIVE
WO : PLATFORM_INSENSITIVE
```

Decision-rule audit: 0b INSENSITIVE because CI contains 0 (ratio in [0.5,1)
would also satisfy the <0.5 branch? NO — ratio 0.5457 ≥ 0.5, so the verdict
rests solely on CI-contains-0). 32b INSENSITIVE because CI contains 0
(ratio 1.3183 ≥ 1 does NOT make it SENSITIVE: the rule requires CI excludes 0
AND ratio ≥ 1).

This is NOT Director acceptance. NL5 remains IN_PROGRESS,
external_reproductions = 0, NL6-001 LOCKED. Fresh Reviewer must explicitly
answer whether the early P2 dispatch and the P1 append-only retry chains
invalidate paired scientific inference (YES/NO), then fresh Verifier and
Director apply.
