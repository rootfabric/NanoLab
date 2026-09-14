# Fresh Reviewer R1 — NL5-001-A / Release Contract

## Verdict

**FIX_REQUIRED**

Роль: Fresh Reviewer. Эта сессия не выполняла implementation `WO-NL5-001-A-R1`. Independence caveat: fresh role/session, но тот же GitHub installation/account; actor identity не является доказательством независимого executor identity.

## Exact subjects

- stacked base: `control/post-mvp-route-r1 @ e05793cc8ff03b3b1af2d81b38e39d82cd7527d6`
- substantive subject по handoff: `2efbed379fce9d448ec24052724576a974ba2e05`
- exact branch head reviewed: `9cbde33b854eeeb00abde84346c17fe3080bbe50`
- branch: `work/nl5-001-a-release-contract-r1`

Stack check: A is ahead-only from exact PR #37 head; no rebase/drift was observed during review.

## Blocking findings

### F-A1 — digest contract overstates SHA-256 proof level

**Severity: MEDIUM / BLOCKING**

Exact A schema requires every `source_provenance.digest_gates` entry to contain all three fields:

- `size_bytes`
- `blob_sha1`
- `sha256`

But later library assembly established from existing evidence that for 11b/32b/53b/74b the registry proof is `blob_sha1`; SHA-256 was computed at download and is not independently registry-verified. Treating `sha256` as an unconditional normative digest gate collapses `CONTENT_VERIFIED` and `COMPUTED_NOT_VERIFIED` into one apparent proof level.

This is not hypothetical: B had to introduce amendment R1.1 (`sha256` optional + paired `sha256_status`) specifically to repair A's contract.

**Required repair:** A cannot be accepted at `9cbde33`. Either:

1. backport R1.1 into A and re-review a new A exact head, then rebase B; or
2. explicitly supersede A by an integrated repaired B candidate and do not declare the old A subject ACCEPTED.

### F-A2 — declared planning provenance references a missing document

**Severity: LOW/MEDIUM / BLOCKING FOR DURABLE RECOVERY**

`WO-NL5-001-A-R1.md` and `docs/release/RELEASE_CONTRACT_V0_1.md` reference:

`docs/control/POST_MVP_EXECUTION_PROGRAM_R1.md`

at the exact A head, but this path is absent. The Work Order says its `NL5-001-A` decomposition comes from that program, so a fresh session cannot follow the declared durable planning source from Git.

The existing `docs/control/POST_MVP_DEVELOPMENT_ROUTE_R1.md` already contains the A..D planning decomposition and can serve as the actual durable source.

**Required repair:** either add the intended execution-program document as a real reviewed artifact, or replace the nonexistent references with the existing canonical route/document section.

## Checks that passed

- Scope is bounded to release contract/tooling; no physics or canonical project state change.
- License choice remains an owner decision; draft package is not treated as publicly releasable.
- `74b` is represented as `NOT_MEASURED / KNOWN_GAP`, not fabricated as a measured result.
- Fail-closed schema executor / linter architecture is reasonable for the stated stdlib-only constraint.
- Human Gate remains explicit.

## Reviewer conclusion

The A design is useful, but exact head `9cbde33...` contains a known normative digest-contract defect plus a broken durable planning reference. It must not be independently marked PASS/ACCEPTED.

**REVIEW_VERDICT = FIX_REQUIRED**

## Recommended integration route

Because B already carries the R1.1 digest repair, the least wasteful path is to repair B as the integrated superseding candidate, make the A supersession explicit, and avoid merging/accepting a known-defective A subject separately. If strict staged acceptance is required by policy, backport R1.1 + planning-reference repair into A first and then rebase B.
