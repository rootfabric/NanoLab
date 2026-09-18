# EX-NL5-001-D-R1 — Summary / Handoff

## Result

`IMPLEMENTED / REVIEW_REQUIRED` (MEDIUM, C0_SOFTWARE_ONLY).

Owner decision D2 has been applied:

- NanoLab code: `Apache-2.0`;
- NanoLab documentation and NanoLab-owned derived data/results: `CC-BY-4.0`;
- upstream/third-party rights unchanged.

## Release result

`nanolab-components` is finalized from `0.1.0-rc0` to `0.1.0`.

Updated release surfaces:

- `RIGHTS.json` — D2 licenses + upstream boundary;
- `CITATION.cff` — version/date/license finalized;
- `VERSION` — `0.1.0`;
- `RELEASE_MANIFEST.json` — deterministic digests refreshed;
- `release.build_library_r12` — emits the same finalized metadata deterministically.

Root licensing surfaces:

- `LICENSE` — Apache-2.0 declaration;
- `LICENSE-DOCS-DATA.md` — CC-BY-4.0 declaration;
- `LICENSE_POLICY.md` and dependency matrix synchronized;
- durable owner record: `docs/control/NL5_001_D_LICENSE_DECISION_R1.md`.

No scientific card, reproduction classification, threshold, raw evidence, or NL5-001-C result was changed.

## Validation

Exact substantive subject:

`50aee77760e73e8399a703566fd3bb0082dc9fbd`

Hosted CI:

`run 35336208105 = SUCCESS`

- Check 1/5 JSON/contracts — PASS
- Check 2/5 consistency — PASS
- Check 3/5 work executions — PASS
- Check 4/5 workflow security lint — PASS
- Check 5/5 unit/package — **360/360 PASS**
- deterministic full package build including manifest — PASS
- committed release manifest exact — PASS
- package lint — PASS

Historical first CI attempt `35336073771` failed only because the implementation commit contained literal newline escape bytes in one Python source line; repaired before the accepted validation subject. No scientific or license decision changed.

## Next action

Fresh independent **Reviewer** reviews the final branch exact head and D2/upstream boundary. After Reviewer PASS, a separate **Verifier** checks exact head, deterministic package, licenses/RIGHTS/CITATION/VERSION/manifest and unchanged scientific surfaces. Merge to `main` remains Human Gate.

After D2 merge, Director can perform `NL5-001` acceptance/state transition and open `NL5-002`.
