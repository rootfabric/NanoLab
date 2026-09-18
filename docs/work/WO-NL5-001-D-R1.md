# WO-NL5-001-D-R1 — Finalize NanoLab open licenses and release metadata

- Base: `main @ bc9ad8c5a10e482ea380a03b6fe30aed2cac451e`
- Branch: `control/nl5-001-d-license-r1`
- Parent: `NL5-001`
- Risk: MEDIUM (public release rights/metadata; no scientific computation)
- Claim ceiling: C0_SOFTWARE_ONLY

## Owner decision D2

Explicit owner instruction, 2026-09-18:

- NanoLab code: **Apache-2.0**
- NanoLab documentation + own derived data/results: **CC-BY-4.0**
- third-party/upstream materials keep their own rights; E2 upstream inputs remain REFERENCE_ONLY / download-on-run and are not relicensed or vendored.

## Goal

Remove the D2 publication blocker and finalize the v0.1 release metadata without changing scientific results.

## Allowed paths

- `LICENSE`
- `LICENSE-DOCS-DATA.md`
- `LICENSE_POLICY.md`
- `docs/control/NL5_001_D_LICENSE_DECISION_R1.md`
- `docs/research/DEPENDENCY_LICENSE_MATRIX.md`
- `scripts/release/build_library_r12.py`
- `releases/nanolab-components-v0.1/RIGHTS.json`
- `releases/nanolab-components-v0.1/CITATION.cff`
- `releases/nanolab-components-v0.1/VERSION`
- `releases/nanolab-components-v0.1/RELEASE_MANIFEST.json`
- `docs/work/WO-NL5-001-D-R1.md`
- `docs/work/executions/EX-NL5-001-D-R1/**`

## Required outputs

1. Durable owner-decision record.
2. Apache-2.0 license for NanoLab code.
3. CC BY 4.0 notice for NanoLab docs/own derived data.
4. RIGHTS/CITATION/VERSION synchronized with the decision.
5. Normative R1.2 builder emits the finalized metadata deterministically.
6. Deterministic release manifest refreshed after metadata changes.
7. Validation evidence and handoff for Fresh Reviewer + Verifier.
8. No change to 0b/11b/32b/53b/74b scientific facts or NL5-001-C evidence.

## Validation

- repository tests
- release package lint
- deterministic package rebuild/check
- manifest verification
- control consistency / work-event validation
- diff scope check

## Human gate

No direct push to `main`. Merge remains Human Gate.
