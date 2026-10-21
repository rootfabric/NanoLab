# WO-S17-STACK-INTEGRATION-R1 — canonical safe integration R3 + RED→GREEN Repair + Assembly CLI

Status: STARTED / integration gate. Owner mission 2026-10-21: close validated NanoLab stack and continue; explicit merge Human Gate, **but do not bypass independent review/verification**.

- Repository: rootfabric/NanoLab
- Base main: `fb3148b46a9638167168a46cb170902a4ad9e8d2` (after R2 #59, R4 #69, U1/NL5 readiness #70 merged)
- Source lineage: R3 PR #60 @ `2cf8297f10ab5ec98b8c8023ff76b39d92ef398b`; R3 repair PR #67 @ `a4b4cf3a1072b9139720bb4420e3bc53154cff6a`; CLI PR #71 @ `ca6eabd84c0712af87d8ab571b1e3caf549bfb16`.
- Repair verified code: `0b9311c380a2d228be0bdb35701287a2b9e9339a`, CLI verified code: `5231b1d4650bd37ad39a63cbe1d18c451bb889a8`.
- Worktree branch: `integration/s17-r3-repair-assembly-cli-r1`. Risk MEDIUM; claim C0_SOFTWARE_ONLY; scientific runs 0; paid compute 0.

## Plan

1. Record durable START before substantive work. Build a clean additive tree from the new current main, preserving only 55 R3+repair+CLI changed paths relative to exact R2 ancestor `26c4cd51151167634815c531b9c49dcc54ba6243`; preserve all original blob SHAs. Add missing immutable `EX-PREP-S17-R3-REPAIR-R1/events/0007-exact-head-verified.json` from PR #67. Do not backport old R2 or overwrite accepted source/infra docs. Merge only new Work Queue rows append-only.
2. Run hosted CI on a new PR into main with exact HEAD and full tests; compare source-tree SHA/diffs before deciding merge. Repair any incompatibility in explicit narrow commits, no force push.
3. Examine erratum: seven follower ports declare 21 nt overhang segments versus pinned R3 sequence-level exact 20 nt pairs. Separate narrow erratum correction may be added only with provenance, tests, own durable receipt, no claim promotion. Original real D–F must remain NOT_RECONSTRUCTED.
4. Fresh independent R3-specific code Review and separate exact-head Verifier are mandatory before final integration. GitHub-hosted CI is independent execution but NOT a substitute for independent reviewer. If reviewer unavailable, WAIT_EXTERNAL and leave PR draft, do not self-accept.
5. After Human Gate + verification, mark source stacked PRs #60/#67/#71 as superseded, never merge invalid interim R3 code alone.

## Allowlist

- Originally scoped R3, R3-Repair, Assembly CLI docs/code/tests under `docs/research/S17_R3_*`, `docs/examples/s17_static_assembly_example/**`, `scripts/knowledge_pack/{assembly_spec,mechanical_component_spec,assembly_cli}.py`, `tests/test_s17_r3_*.py`, `tests/test_s17_static_assembly_cli.py`, and `docs/work/executions/EX-PREP-S17-R3*/**`, `docs/work/executions/EX-S17-STATIC-ASSEMBLY-HARDENING-R1/**`.
- `docs/work/WORK_QUEUE.md` append-only. This integration Work Order and `docs/work/executions/EX-S17-STACK-INTEGRATION-R1/**`.

## Forbidden

`project/state.json`, `project/plan.json`, `project/infra-state.json`, frozen NL5/evidence, R2 source/protocols, other unchanged main files; no MD/oxDNA science, no U1 activation, no self-review, no main direct push, no force-push, no fabricated source follower, no author emails.

## Acceptance

Exact clean integration branch with byte-preserved source blobs except documented scoped repair; all 4 F01–F04 fail-closed, deterministic CLI, full H0 gates PASS, no regression or science inflation, explicit independent Reviewer/Verifier and Human Gate before merge. If any gate absent, report READY_FOR_REVIEW / WAIT_EXTERNAL rather than accepted.
