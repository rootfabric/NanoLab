# OWNER_DECISION D2 — NanoLab own materials license

Date (UTC): 2026-09-18
Recorded by: agent under explicit owner instruction
Parent: NL5-001 / NL5-001-D
Supersedes: `UNDECIDED_PENDING_OWNER_DECISION` for NanoLab-owned release materials

## Decision

- **NanoLab code:** Apache-2.0
- **NanoLab documentation and NanoLab-owned derived data/results:** CC-BY-4.0

The owner explicitly requested freely redistributable licensing.

## Rationale

The project should remain freely reusable for research, modification, redistribution and commercial/industrial integration. Apache-2.0 provides a permissive software license with an explicit patent grant. CC BY 4.0 keeps scientific documentation and NanoLab-owned derived results freely reusable while preserving attribution.

## Rights boundary

This decision applies only to material owned by NanoLab.

It does **not** relicense third-party or upstream material. In particular:

- `gauravarya77/DNA-hinge-simulations @ 23fd1ff7731e9017bd776f49206dc42d70d9fe91` remains `REFERENCE_ONLY`, download-on-run, no durable cache, no vendoring in the release;
- oxDNA and covered fixtures keep their upstream GPL terms;
- restricted publications/SI and per-record external data keep their own rights.

NanoLab-derived measurements/results already authorized for publication by the G1 decision may be distributed under CC-BY-4.0; the underlying upstream bytes are not included.

## Applies from

- NanoLab repository releases after this decision;
- `nanolab-components` package version `0.1.0`;
- release metadata finalized by `NL5-001-D-R1`.

## Implementation surfaces

- root `LICENSE` → Apache-2.0 declaration;
- root `LICENSE-DOCS-DATA.md` → CC-BY-4.0 declaration;
- `LICENSE_POLICY.md`;
- `releases/nanolab-components-v0.1/RIGHTS.json`;
- `releases/nanolab-components-v0.1/CITATION.cff`;
- `releases/nanolab-components-v0.1/VERSION`;
- deterministic release manifest and builder.

This is a project licensing decision, not a legal opinion about third-party rights.
