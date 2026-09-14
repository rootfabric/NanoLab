# Fresh Reviewer R1 — NL5-001-B / Component Library Assembly

## Verdict

**FIX_REQUIRED**

Роль: Fresh Reviewer. Эта сессия не выполняла implementation `WO-NL5-001-B-R1`. Independence caveat: fresh role/session, но тот же GitHub installation/account; actor identity не является доказательством независимого executor identity.

## Exact subjects

- stacked base: `work/nl5-001-a-release-contract-r1 @ 9cbde33b854eeeb00abde84346c17fe3080bbe50`
- substantive subject по handoff: `be73c5408bee54bc66105f0dee3e3262905eb2ad`
- exact branch head reviewed: `628526594784ded8bb2067976cefbe53c4ac0e48`
- branch: `work/nl5-001-b-library-assembly-r1`

Stack check: B is ahead-only from exact A head. Final delta `be73c54... -> 6285265...` contains execution terminal records/evidence/summary only.

## What passed

- R1.1 direction is correct: `blob_sha1 + size_bytes` remain the registry-level mandatory pins; optional `sha256` is paired with `sha256_status`; S5 enforces pair consistency.
- Measured medians/CI fields inspected for 0b/11b/32b/53b trace to published E2 summaries.
- `74b` remains honest `NOT_MEASURED`, zero observables, runs `NOT_RUN`, explicit `KNOWN_GAP`, `blocking_release=false`.
- Draft license state is explicit and publication remains blocked pending owner decision D2.
- No new physics runs or canonical state changes were introduced.

## Blocking findings

### F-B1 — builder provenance claim is stronger than implementation

**Severity: MEDIUM / BLOCKING**

The Work Order, summary and evidence map state that the builder is a pure evidence→package function with **zero hand-entered numbers**. Static review of `scripts/release/build_library.py` shows scientific/protocol values embedded as source constants/literals rather than read from the declared evidence, including examples such as:

- `WINDOW_STEPS = 150000`;
- 0b `steps = 200000`;
- 0b seeds `[201004, 202008, 203012]`;
- parameter-card `temperature = 300 K`;
- `salt_concentration_M = 0.5`;
- `print_conf_interval = 4000`;
- `print_energy_every = 100`;
- analysis/reproduction text embeds `150000`, `10000` bootstrap resamples and seed `424242`;
- pinned upstream commit is also transcribed in `_rights()`.

These values do exist in published evidence/protocol artifacts, so this is repairable, but the present provenance statement is false as written and tests currently verify mainly measured outputs, not that protocol pins are evidence-derived.

**Required repair:** derive scientific/protocol pins from frozen evidence/config artifacts (or explicitly define a narrow set of contract-owned metadata constants and stop claiming zero manual scientific values). Add tests comparing generated protocol pins, seeds, windows and relevant rights pins against their source evidence.

### F-B2 — full-package byte reproducibility is overclaimed

**Severity: MEDIUM / BLOCKING**

`build_library.py` intentionally does not emit `RELEASE_MANIFEST.json`; `build_library.check()` excludes that file from byte comparison. Separately, `card_lint.manifest_create()` writes `generated_at_utc = now()`, so regenerating the manifest changes its bytes.

Therefore `build_library check` proves byte identity only for builder-owned payload files, **not the complete committed release package**, while the Work Order/summary/evidence wording presents whole-package deterministic byte reproducibility.

**Required repair — choose one:**

1. make the manifest deterministic from frozen release metadata/subject and include it in the byte-identical check; or
2. narrow all normative/handoff claims to say that builder payload is deterministic while the manifest is integrity-verifiable but not byte-reproducible on regeneration.

Tests/evidence-map/summary must match the chosen semantics.

### F-B3 — reproduction acceptance misuses original bootstrap CI as a replication tolerance

**Severity: HIGH METHODOLOGICAL / BLOCKING BEFORE NL5-001-C**

Cards currently instruct that a new pooled median must fall inside the original card's bootstrap CI95, otherwise `REPRODUCTION_MISMATCH`.

A bootstrap confidence interval for the original pooled median estimates uncertainty of that original statistic; it is not a prediction/tolerance interval for a new independent campaign. Existing 0b evidence itself shows per-replica medians (about 65.10, 65.71, 67.24 deg) spanning far beyond the narrow pooled CI95 (~65.67–66.32 deg), demonstrating that between-run variability is materially wider than this rule.

Using the pooled CI as the clean-room/external reproduction pass band risks false mismatch and would make NL5-002 scientifically brittle.

**Required repair:** preregister a reproduction comparison rule appropriate to independent repetitions before C runs. It may reuse a protocol-level criterion, explicit equivalence/tolerance bound justified from replicate variability, or another reviewed statistical comparison. Do not choose the threshold after observing C. Preserve `INCONCLUSIVE` as an allowed outcome where power/replicates are insufficient.

### F-B4 — R1.1 normative text is internally inconsistent

**Severity: MEDIUM / BLOCKING**

The Revision history correctly says R1.1 makes `sha256` optional and pairs it with `sha256_status`, and code/schema enforce S5. But the body of `RELEASE_CONTRACT_V0_1.md` still states that each digest gate contains `size_bytes`, `blob_sha1`, `sha256`, and the semantic-rules table still lists only S1–S4.

**Required repair:** update the normative field policy and semantic-rules table to match R1.1/S5 exactly. The contract, schema and executable linter must agree.

### F-B5 — inherited broken planning reference

**Severity: LOW/MEDIUM / BLOCKING FOR DURABLE RECOVERY**

The inherited release contract still references nonexistent `docs/control/POST_MVP_EXECUTION_PROGRAM_R1.md`. Repair/supersede this reference as described in A finding F-A2.

### F-B6 — manifest duplicate paths are not rejected fail-closed

**Severity: MEDIUM / BLOCKING FOR RELEASE-CONTRACT HARDENING**

`manifest_verify()` constructs a dictionary keyed by `entry["path"]`. Duplicate paths in `manifest["files"]` therefore collapse silently; the schema does not enforce `uniqueItems` and the mini-schema executor intentionally does not support it. A malicious or malformed manifest can contain duplicate path records while only the last survives verification logic.

**Required repair:** add explicit semantic duplicate-path rejection before dictionary conversion, plus a negative test. Also apply the documented relative-path semantic check directly to manifest entry paths.

## Test-gap findings

Current tests are useful for measured medians, CI copying, digest statuses, 74b gap, linting and tamper detection, but they do not prove F-B1 provenance purity, do not test a deterministic complete manifest, do not challenge the statistical reproduction criterion, and do not reject duplicate manifest paths.

## Reviewer conclusion

The assembled library is a strong candidate and the measured-value handling/74b honesty are good, but the release/reproduction contract is not ready for clean-room C. The main risks are **provenance overclaim**, **overstated determinism**, and especially an **invalid replication tolerance rule** that could turn a valid independent reproduction into a false mismatch.

**REVIEW_VERDICT = FIX_REQUIRED**

## Required repair sequence

1. Repair F-B3 first and freeze the reproduction criterion before any NL5-001-C data.
2. Repair F-B1/F-B2/F-B4/F-B5/F-B6 and add negative/provenance tests.
3. Re-run full tests, builder checks and package lint on a new exact B head.
4. Fresh Reviewer re-review the repaired exact head.
5. Only after Reviewer PASS hand to a separate exact-head Verifier, then proceed to C/environment gate.

Do not run NL5-001-C against the current tolerance contract; that would expose the next campaign to a post hoc criterion repair.
