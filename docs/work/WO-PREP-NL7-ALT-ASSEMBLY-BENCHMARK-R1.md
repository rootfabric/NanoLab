# WO-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1 — альтернативный опубликованный DNA benchmark из двух компонентов

**Status:** STARTED / scoped preparatory C0 work; issue #75. Parent track: NL7 preparation, **NOT** NL7-001 scientific acceptance.

**Canonical base:** `main@fb3148b46a9638167168a46cb170902a4ad9e8d2`, tree `fb3148b46a9638167168a46cb170902a4ad9e8d2`; branch `work/prep-nl7-alt-assembly-benchmark-r1`.
**Risk:** MEDIUM; **claim** C0_SOFTWARE_ONLY; `scientific_runs=0`; `paid_compute=0`.
**Executor:** GitHub-hosted H0 for offline tests, public source audit; U1/U2 scientific hosts not used.

## Intent and boundary

Find a published, independently traceable two-component DNA assembly with actual source topology/configuration and hybridization interfaces. Candidate A: Huang et al. Narcissus+Echo (Nemesis), DOI `10.1038/s41565-024-01738-7`, structure IDs 256/257 **R4_REPORTED_NOT_BYTE_VERIFIED**. Candidate B: Weck & Heuer-Jungemann moDON, DOI `10.1038/s41467-025-56846-2`, Nanobase 263 mentioned in author's Data Availability; special connection types XY rerouted scaffold and Z three-strand handles. The alternative is **not S17 follower**.

No design file may be marked pin-verified without exact legal source bytes and SHA-256. OxView JSON / caDNAno is not the same as a relaxed oxDNA `.top/.dat` pair. Reuse KnowledgePack v1 when source files are actually recovered; do not add fictional molecular connections.

## Allowed paths

- `docs/work/WO-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1.md`
- `docs/work/WORK_QUEUE.md` (append-only)
- `docs/work/executions/EX-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1/**`
- `docs/research/ALT_DNA_TWO_PART_SOURCE_AUDIT_R1.md`
- `docs/research/ALT_DNA_TWO_PART_SOURCE_PACK_R1.json`
- `scripts/knowledge_pack/alt_pair_source_gate.py`
- `tests/test_alt_pair_source_gate.py`

## Forbidden

`project/state.json`, `project/plan.json`, `project/infra-state.json`, frozen NL5 artifacts, R2/R3 source code, `scripts/r2/**`, `scripts/nl5/**`, all new oxDNA MD/relax/pull-release/E5, unapproved paid resources, outward emails, direct main push, force-push, self-review or merge. No vendored third-party raw CAD unless explicit rights and scoped approval.

## Work phases and deliverables

A. Targeted primary-source inventory & rights: two candidate DOIs, Nanobase structures, publisher source statements, exact discovered file listing and provenance. `SOURCE_REPORTED` vs `CONTENT_VERIFIED` strictly separate. If a source endpoint is blocked, preserve `SOURCE_ACCESS_BLOCKED` with tested URI and tool limitation.

B. A source-only machine manifest and strict offline source-ready gate. `READY_FOR_STATIC_PREP` only when **two** part files (topology and configuration each), their SHA-256 and rights, interface mapping, true source bytes and file size/containment are verified; otherwise report precise `BLOCKED_SOURCE` reasons. This does NOT simulate or certify hybridization, energy or motion.

C. Synthetic-only positive/negative tests; no S17 model replacement. Data + docs + summary/passport/event chain + draft PR. Fresh independent Reviewer/Verifier requested as a separate actual executor; until then `WAIT_EXTERNAL`.

Budget: ≤256 MiB network, ≤2 GiB scratch, 0 science/paid compute. If no original file bytes can be retrieved, output honest `BLOCKED_SOURCE` and do not claim new imports. This C0 task may finish with gaps.
