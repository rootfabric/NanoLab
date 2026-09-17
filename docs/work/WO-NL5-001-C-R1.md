# WO-NL5-001-C-R1 — Clean release reproduction (nanolab-components-v0.1)

- Base: `main @ 6577f8bb5fcf5f97ad40fadfdbbc34e9f0c970fc`
- Branch: `work/nl5-001-c-clean-reproduction-r1`
- Risk: MEDIUM (computational reproduction; no canonical-state changes; no new physical claims)
- Claim ceiling: C1_COMPUTATIONAL_REPRODUCTION (per-reproduction statement only; does not raise card claims)
- Subject package: `releases/nanolab-components-v0.1` (merged `6577f8b`; frozen HEAD `a9950dc…` lineage, reviewed PR #41)
- Classification rule: `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` (`docs/release/REPRODUCTION_RULE_V0_1.md`, FROZEN BEFORE DATA)

## Scope

Independent (fresh-seed) computational reproduction of the four MEASURED DNA-hinge cards of the frozen release package, with per-card classification `MATCH | MISMATCH | INCONCLUSIVE` by the frozen envelope rule:

| variant | topology_nt | steps | reference seeds (NOT reused) | fresh seeds (FROZEN below) |
|---|---|---|---|---|
| 0b  | 8378 | 200000 | [201004, 202008, 203012] | [170085, 157480, 561483] |
| 11b | 8444 | 200000 | [201004, 202008, 203012] | [373439, 592596, 456410] |
| 32b | 8570 | 150000 | [201004, 202008, 203012] | [399746, 801667, 659403] |
| 53b | 8696 | 150000 | [201004, 202008, 203012] | [511532, 979551, 175554] |

`74b` is `NOT_MEASURED / KNOWN_GAP` — excluded from reproduction; no values may be produced for it.

## Frozen protocol (must not be tuned after any result is seen)

1. Engine: oxDNA CPU build, double precision, commit `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`
   (local provenance: `/home/rdpuser/nl5-001-c-env/BUILD_PROVENANCE.md`; cmake defaults `DOUBLE=ON`, `CUDA=OFF`).
2. Upstream inputs: `gauravarya77/DNA-hinge-simulations @ 23fd1ff7731e9017bd776f49206dc42d70d9fe91`
   (`MD_Hinges/<variant>.conf`, `MD_Hinges/<variant>.top`, `MD_Hinges/pro_CPU.in`), download-on-run into a
   disposable temp dir; mandatory size + `blob_sha1` gates against
   `docs/work/executions/EX-NL3-002-PARAM-<V>-R1/evidence/source-download-verification.json` pins;
   `durable_cache = FORBIDDEN` (REFERENCE_ONLY, G1 decision B); `sha256` recorded as COMPUTED_NOT_VERIFIED.
3. Per-replica input: upstream files verbatim (`E2-SETUP-R1` §5 reproduction-arm rule: temperature/salt/precision
   unchanged), EXCEPT `seed = <frozen fresh seed>` above. Everything else byte-identical to upstream.
4. Execution: 12 independent runs (4 variants × 3 replicas), single-threaded processes, run in parallel on the
   local 64-core host; no GPU.
5. Analysis: frozen observable convention `docs/research/E2_OBSERVABLES_R2.md` + erratum R1 §2.5
   ([0,180] deg, PCA axes, detector v2 mutual-nearest + PCA hinge angle, frozen arm manifest),
   frame-validity gates §4 `docs/research/E2_PROTO_R1.md`, common comparison window `t <= 150000`
   (addendum §8; per-card steps above, longer runs analysed in-window only);
   per-replica median over valid in-window frames; campaign statistic = median of three per-replica medians.
6. Classification: per card, `scripts/release/reproduction_rule.py` semantics —
   `MATCH` if campaign statistic inside inclusive reference envelope `[min(ref_medians), max(ref_medians)]`
   (published per-card in `reproduction.expected`); `MISMATCH` if all three replica medians strictly on one
   side; otherwise `INCONCLUSIVE`. Bootstrap CI95 is descriptive only, never a tolerance.
7. Technical failures (digest gate failure, engine crash, budget abort) are recorded as
   `FAILED_TECHNICAL` / `BLOCKED_ENVIRONMENT` per run and do NOT count as scientific mismatch.

## Budget and stop conditions

- 12 runs, 150k–200k steps each; total wall-clock budget 48 h; per-replica hard kill at 20 h → `FAILED_TECHNICAL`.
- No paid compute; no GPU; no upstream code modifications; no canonical state/plan/roadmap changes.
- Stop immediately and record if any digest gate fails (input integrity), or engine produces invalid output
  (NaN / truncated trajectory) in > 1 run of the same variant.

## Forbidden

- Reuse of reference seeds; threshold/envelope changes; cherry-picking replicas; durable caching of upstream files;
- merge to `main` (Human Gate; pre-approval granted for this mission chain);
- editing immutable historical events; changing acceptance criteria after seeing results.

## Deliverables

Execution records under `docs/work/executions/EX-NL5-001-C-R1/` (passport, events, summary, per-replica evidence
manifests with sha256/size), per-card classification records, honest `MISMATCH/INCONCLUSIVE` preserved if they occur.
