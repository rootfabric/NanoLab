# Repair Map R1 — NL5-001-B after Fresh Reviewer FIX_REQUIRED

Source verdict: `docs/evidence/NL5-001-B/FRESH_REVIEW_R1.md` on review branch `review/nl5-001-b-r1`.
Reviewed exact candidate: `work/nl5-001-b-library-assembly-r1 @ 628526594784ded8bb2067976cefbe53c4ac0e48`.

This document is a reviewer-authored repair map. It does not implement fixes and does not change the reviewed candidate.

## Repair strategy

Prefer an **integrated B repair** over accepting the known-defective A exact subject separately. B already contains A + amendment R1.1. After repair, document that A@9cbde33 is superseded by the repaired integrated candidate. If repository policy requires A acceptance as a separate leaf, backport the contract/link repair to A first and rebase B instead.

## R1 — freeze a valid independent-reproduction criterion before any C data

**Finding:** F-B3.

### Root cause
The current card contract treats the original bootstrap CI95 for a pooled median as a tolerance/prediction band for a future independent reproduction. Those are different statistical objects.

### Canonical repair surfaces
- `docs/release/RELEASE_CONTRACT_V0_1.md`
- a new preregistered reproduction-rule document under `docs/release/` or `docs/research/` (preferred; exact path chosen by Implementer)
- `scripts/release/build_library.py`
- generated cards under `releases/nanolab-components-v0.1/**`
- example cards if they expose the same rule
- tests for release/reproduction contract

### Required design
Before running NL5-001-C, define the independent-reproduction comparison using a reviewed rule appropriate to independent replicas/campaigns. It must specify:
- statistic(s);
- number/structure of replicas;
- allowed outcome set including `MATCH/SUPPORTED`, `MISMATCH/NOT_SUPPORTED` and `INCONCLUSIVE` (exact vocabulary may follow existing harness);
- tolerance/equivalence/comparison rule and its rationale;
- handling of integrity failures and technical failures separately;
- no threshold tuning after C results are observed.

Do not use the original pooled bootstrap CI as a prediction interval unless a separate derivation justifies that use.

### Required tests
- control case that should reproduce under the frozen rule;
- case showing that a new replicate can lie outside the original pooled CI without being automatically classified as a scientific mismatch;
- missing/insufficient replicas -> `INCONCLUSIVE` or explicit non-pass, not implicit PASS.

## R2 — make builder provenance claims true

**Finding:** F-B1.

### Root cause
`build_library.py` transcribes scientific/protocol values as literals while Work Order/evidence claim zero manual scientific numbers and a pure evidence→package function.

### Canonical repair surfaces
- `scripts/release/build_library.py`
- `tests/test_release_library.py`
- `docs/work/WO-NL5-001-B-R1.md` only if semantics are intentionally narrowed
- B summary/evidence-map in the repaired execution record

### Required changes
Read protocol/scientific fields from frozen evidence/config sources rather than literals, including where applicable:
- common window steps;
- requested steps;
- seeds;
- salt;
- print intervals;
- bootstrap resamples/seed;
- upstream pinned commit;
- other numeric protocol pins emitted into cards.

Non-scientific package-format constants such as package version may remain code-owned if explicitly classified as release metadata, not evidence-derived science.

### Required tests
Compare generated `protocol_pins`, relevant analysis pins and rights/source pins directly against source evidence/config files, not against duplicated hardcoded EXPECTED constants only.

## R3 — resolve package determinism semantics

**Finding:** F-B2.

### Root cause
Builder check excludes `RELEASE_MANIFEST.json`; manifest generation contains wall-clock `generated_at_utc`.

### Option A — preferred
Make manifest generation deterministic from frozen release metadata/subject, generate it as part of the deterministic assembly pipeline, and include it in byte-for-byte check.

### Option B
Keep a volatile manifest timestamp but explicitly narrow every claim to:
- deterministic builder payload excluding manifest;
- manifest is integrity-verifiable but regeneration is not byte-identical.

Update Work Order, summary, evidence map and tests consistently. Do not claim whole-package byte reproducibility under Option B.

## R4 — finish R1.1 contract synchronization

**Finding:** F-B4.

### Canonical repair surfaces
- `docs/release/RELEASE_CONTRACT_V0_1.md`

### Required changes
- state `size_bytes + blob_sha1` as mandatory registry-level digest fields;
- describe `sha256` as optional and valid only with `sha256_status`;
- document `sha256_status` meanings;
- add S5 to the semantic-rules table;
- ensure example package/schema snapshot matches repo schema.

## R5 — repair missing planning reference

**Finding:** F-B5 / A F-A2.

Replace references to nonexistent `docs/control/POST_MVP_EXECUTION_PROGRAM_R1.md` with the actual durable planning source (`docs/control/POST_MVP_DEVELOPMENT_ROUTE_R1.md`, including its A..D decomposition), unless the missing program is intentionally introduced as a separately reviewed artifact.

Search the full repaired stack for `POST_MVP_EXECUTION_PROGRAM_R1` and require zero stale references if the replacement strategy is chosen.

## R6 — harden release manifest against duplicate paths

**Finding:** F-B6.

### Canonical repair surfaces
- `scripts/release/card_lint.py`
- `tests/test_release_contract.py`

### Required changes
Before converting manifest entries to a dict:
- reject duplicate `path` values explicitly;
- run the documented relative/POSIX/no-`..` path semantic validation on each manifest entry.

### Required negative tests
- duplicate path with identical metadata -> reject;
- duplicate path with conflicting metadata -> reject;
- leading slash / backslash / `..` path -> reject.

## R7 — repair durable execution claims

After R1–R6 implementation:
- create a new continuation/repair event; never rewrite old events;
- update summary/evidence map to describe actual determinism/provenance semantics;
- preserve old FIX_REQUIRED review as historical evidence;
- exact candidate HEAD/TREE must be frozen before re-review.

## Revalidation gate

Minimum revalidation:

1. full unittest suite;
2. package lint on real release candidate;
3. deterministic check according to selected R3 semantics;
4. manifest negative controls from R6;
5. direct evidence-vs-generated protocol pin tests from R2;
6. reproduction-rule unit tests from R1;
7. consistency/work close checks;
8. scope diff: no physics runs, no canonical state mutation.

Then request **Fresh Reviewer Re-review** on the repaired exact head. Only after PASS may a separate exact-head Verifier run. NL5-001-C must not start before the repaired reproduction criterion is frozen.
