# NL5-002-E / FRESH_PREREGISTRATION_VERIFY_R1

- verify id: `NL5-002-E/FRESH_PREREGISTRATION_VERIFY_R1`
- date UTC: 2026-09-20T11:33:06Z (real `date -u` at verification time)
- verifier: fresh independent Verifier session; did NOT author the WO, did NOT
  read or rely on the reviewer's verdict or reasoning. All computations below
  were recomputed from git objects at the exact subject commit.
- `VERIFY_VERDICT = PASS`
- `VERIFIED_WO_COMMIT = 4d6542fda81084dced2578f3e008c8c8e0705a5a`
- `VERIFIED_WO_TREE  = 7651569ac8d0e93c0cc7614cb692945ad5bd0c98`
- `SUBJECT BINDING = review-claimed vs live: match`
  (review evidence branch `origin/review/nl5-002-e-preregistration-r1`, file
  `docs/evidence/NL5-002-E/FRESH_PREREGISTRATION_REVIEW_R1.md`, fields
  `REVIEWED_WO_COMMIT = 4d6542fda81084dced2578f3e008c8c8e0705a5a`,
  `REVIEWED_WO_TREE  = 7651569ac8d0e93c0cc7614cb692945ad5bd0c98`;
  live-resolved: `git rev-parse` of the subject commit and `HEAD^{tree}` in a
  detached worktree — equal. Only these two fields were read; the reviewer's
  verdict was not used.)
- Subject branch check: `4d6542fda81084dced2578f3e008c8c8e0705a5a` is the tip
  of `origin/control/nl5-002-terminal-decision-r1` (live, after
  `git fetch origin --prune`).

Independence statement: this verification was performed in a fresh session in a
dedicated detached worktree (`/tmp/verify-nl5-002-e-prereg`); no existing
worktree was modified; no commits were made outside this verify branch; every
check below is an independent recomputation from the exact tree
`7651569ac8d0e93c0cc7614cb692945ad5bd0c98`.

## Check 1 — Seed uniqueness and int32 validity — PASS

From `docs/work/WO-NL5-002-E-R1.md` (lines 71–80) at the exact commit:
S001=1259289227, S002=1358106528, S003=1524307444, S004=601855227,
S005=274288237, S006=972234272, S007=1934775205, S008=1747973984,
S009=880427736, S010=744386736.

- count = 10; distinct = 10/10 (no duplicates)
- all positive: yes (min 274288237)
- all < 2^31 = 2147483648: yes (max 1934775205); all fit signed int32

## Check 2 — Seed overlap with previous campaign seed sets — PASS (all EMPTY)

New set N = {1259289227, 1358106528, 1524307444, 601855227, 274288237,
972234272, 1934775205, 1747973984, 880427736, 744386736}.

| Previous set (source at subject commit) | Values used | N ∩ set |
|---|---|---|
| reference triple (`frozen_seeds.json` reference_seeds_forbidden, B-R1/B-R2 evidence) | {201004, 202008, 203012} | EMPTY |
| B-R1 `docs/work/executions/EX-NL5-002-B-R1/evidence/frozen_seeds.json` (same 3 seeds for all 4 variants) | {510101, 520202, 530303} | EMPTY |
| B-R2 `docs/work/executions/EX-NL5-002-B-R2/evidence/seeds_frozen.json` (4 variants × 3 seeds) | {410273, 520931, 638257, 741953, 852607, 963541, 174329, 285637, 396421, 507283, 618457, 729613} | EMPTY |
| E3 winner re-validation NL4-002 (`EX-NL4-002-E3-REVAL-R1`, passport/evidence) | {204016, 205020} | EMPTY |
| NL4-003 MVP re-validation seed (`EX-NL4-003-R1`, summary/events) | {206024} | EMPTY |
| Additional run seeds found in NL5-001-C-R1 / NL3-002-PARAM-53B-R1 evidence | {157480, 170085, 175554, 373439, 399746, 456410, 511532, 561483, 592596, 659403, 801667, 979551} | EMPTY |

Full union (33 distinct previous values): N ∩ union = EMPTY.
Stronger exhaustive check: a whole-tree string search at the subject commit for
each of the 10 seed literals returns exactly one file — the WO itself. None of
the 10 values occurs anywhere else in the tree. (Note: seed 424242 found in
NL4-003 evidence is a bootstrap RNG seed of that report, not a run seed;
irrelevant here.)

## Check 3 — Bootstrap RNG seed 902107 is not a run seed — PASS

- 902107 ∉ N (new run seeds); 902107 ∉ any previous run-seed set above.
- Whole-tree search for `902107` at the subject commit: (a) WO line 104
  (bootstrap RNG seed declaration — the intended use); (b) SESSION_LOG.md line
  542 (plan description of the same WO); (c) one coincidental digit-substring
  hit inside a float row of `experiments/evidence/E1/E1-R2/runs/E1-R2-C003/
  artifacts/trajectory.dat` (trajectory data, not a seed assignment). No run
  seed usage anywhere.

## Check 4 — Protocol references resolve to real artifacts — PASS

All verified in the subject tree:

- `docs/work/WO-NL5-002-A-R1.md` exists; it defines the frozen classification
  envelope name `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` (line 94).
- `releases/nanolab-components-v0.1.1/` exists with `RELEASE_MANIFEST.json`
  (structured sha256+size manifest) and `convention/analyze_hinge.py`
  (docstring: frozen convention analyzer, classification by
  `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` — the packaged convention the WO
  pins).
- `releases/nanolab-components-v0.1.1/VERSION` = `0.1.1`.
- The envelope name is also referenced by B-R2 evidence analysis JSONs and
  WO-NL5-002-C-R1/C2-R1 — the mapping is a live, real artifact chain.

## Check 5 — Package/version pins — PASS

- WO pins the tested package: `nanolab-components 0.1.1` (lines 23 and 163).
- Documented bounded allowance: "или 0.1.2, если bounded packaging repair будет
  принят владельцем; научные числа пакетов byte-identical, это фиксируется
  digest'ами" (lines 163–164) — i.e. 0.1.2 only via separate owner acceptance,
  with byte-identical science fixed by digests.
- No unpinned semantics: zero occurrences of "latest" in the WO.

## Check 6 — Budget arithmetic — PASS (internally consistent, bounded)

- Primary runs: n=10 seeds × 2 platforms (P1, P2) × 2 primary variants
  (0b, 32b) = 40 — matches WO "~40 прогонов при n=10 × 2 variants × 2
  platforms".
- P3 optional: +10 seeds × 2 variants = +20 — matches WO "P3 опционально +20".
- Controls 11b/53b: declared optional, analysis-only, do not affect WO-level
  classification — correctly excluded from the primary 40.
- Steps: 0b = 200k, 32b = 150k (R1 windows) — bounded per run; total compute
  bounded (≈ 40 × ≤200k steps, CPU-only).
- Wall: ≤72 h/platform with documented parallel runs within a node; calibrated
  at ~10–14 h/replica single-thread (B campaigns). Feasibility: at ≥7
  concurrent single-thread runs, 40 runs × ≤14 h / 7 ≈ ≤80 h; at 10–16
  concurrent (Xeon E5-2698 v3 class node, 16 cores) ≈ 25–56 h — within 72 h.
  Not impossible, not unbounded.
- Stop conditions present: `BLOCKED_ENVIRONMENT` (env unavailable);
  ≥2 systematic technical failures in one cell → FAILED_TECHNICAL/INCONCLUSIVE
  (no fitting); budget overrun → stop + checkpoint. Nothing unbounded.

## Check 7 — Frozen statistical algorithm — PASS (computable, deterministic, no post-data choices)

Exact restatement from WO lines 101–114:

1. For each variant v ∈ {0b, 32b}: paired per-seed differences
   d_i = median[P2, seed_i] − median[P1, seed_i];
   `shift_v = median_i(d_i)`.
2. Bootstrap 95% CI of the paired difference: percentile method, 10,000
   resamples, bootstrap RNG seed frozen = 902107.
3. `within_v = median across platforms of (per-platform MAD of per-seed
   medians)`; `ratio_v = |shift_v| / within_v`.
4. Decision rule per variant: `PLATFORM_SENSITIVE` iff CI does not contain 0
   AND ratio_v ≥ 1; `PLATFORM_INSENSITIVE` iff CI contains 0 OR ratio_v < 0.5;
   otherwise `INCONCLUSIVE`.
5. WO-level: SENSITIVE iff both 0b and 32b SENSITIVE; INSENSITIVE iff both
   INSENSITIVE; otherwise INCONCLUSIVE.

- Computable as written: all quantities are functions of the per-seed
  per-platform median table; no external inputs.
- Deterministic given data: bootstrap seed fixed (902107), resample count
  fixed (10,000), percentile CI, fixed medians — same data ⇒ same numbers.
- No post-data choices: the decision rule is total — every (CI, ratio) case
  maps to exactly one outcome (verified by case enumeration: CI∋0 ⇒
  INSENSITIVE branch or INCONCLUSIVE resolved by ratio; CI∌0 with ratio ≥ 1 ⇒
  SENSITIVE; CI∌0 with 0.5 ≤ ratio < 1 ⇒ INCONCLUSIVE; ratio < 0.5 ⇒
  INSENSITIVE). Plan change after seeing data is explicitly forbidden (WO
  line 114).

Verified limitation (honest, pre-data deferral): the WO text does NOT pin
(a) the MAD scaling convention (raw MAD vs MAD × 1.4826), (b) the
`within_v = 0` degenerate case (all per-seed medians identical within a
platform ⇒ division by zero in ratio_v), and (c) the bootstrap RNG
implementation (only the seed 902107 is frozen). Confirmed by reading lines
101–113: only "MAD of per-seed medians within a platform" appears, no scaling
constant, no zero-handling. This deferral is acceptable pre-data: all three
affect only the effect-size ratio computation, not data collection, no data
exists yet (Check 8), and the WO's own exit clause requires the
EX-NL5-002-E-R1 passport + START before any runs — so these conventions must
be fixed in the passport at START, before any data are seen, exactly as the
reviewer's recorded limitation states. Recorded here as a binding condition
for that passport.

## Check 8 — No post-data content at the subject commit — PASS

- (a) `docs/work/executions/` contains no `EX-NL5-002-E-*` directory
  (live `ls` at the exact tree; grep for `EX-NL5-002-E-R1` hits only the WO's
  planned-output section, line 154).
- (b) The WO contains no result values, medians, CIs, or campaign dates
  implying runs already happened. All numeric content is either preregistered
  design (seeds, steps, budgets, thresholds) or prior-campaign facts (R1
  MISMATCH classification, B-campaign wall calibration ~10–14 h). Dates
  present: 2026-09-20 (owner permission; seed freeze "до любых прогонов") —
  both pre-data.
- (c) `docs/evidence/NL5-002-E/` does not exist on the control branch at this
  commit (the review evidence file exists only on the side review branch
  `origin/review/nl5-002-e-preregistration-r1`, as allowed). All other
  `NL5-002-E` mentions in the tree (ROADMAP, WORK_QUEUE, SESSION_LOG,
  AGENT_START, DIRECTOR_DECISION_R1, state.json, scheduler-policy notes) are
  plan/status-level references, not campaign data.

## Check 9 — Gates in detached worktree at exact commit — PASS

Executed in `/tmp/verify-nl5-002-e-prereg` at HEAD = 4d6542fda81084dced2578f3e008c8c8e0705a5a:

- `python3 -m unittest discover -s tests -t .` → `Ran 369 tests in 11.514s` /
  `OK` (exit 0) — matches expected 369 OK.
- `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` →
  `"ok": true`, `"errors": []` (exit 0). Benign warning: "git metadata
  unavailable" (does not affect ok status).
- `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` →
  summary: workflows 1, violations 0, **blocking 0** (exit 0).

## Verdict

All nine checks PASS on independent recomputation at the exact subject commit.

`VERIFY_VERDICT = PASS`

Limitations of this verification: (1) the three unpinned statistical
conventions (MAD scaling, within_v=0 handling, bootstrap RNG implementation)
remain open and MUST be fixed pre-data in the EX-NL5-002-E-R1 passport at
START (see Check 7); (2) the wall-budget feasibility of ≤72 h/platform depends
on node parallelism (≥~8 concurrent single-thread runs) and is a design
plausibility check, not a measured guarantee; (3) seed-overlap coverage is
complete with respect to everything findable in this tree at this commit
(whole-tree literal search), which is the strongest claim available to an
exact-head verifier; run environments outside git (WSL/external hosts) are out
of scope by design.
