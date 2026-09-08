# NL0-001 — Implementer evidence

Verdict: **HANDOFF CANDIDATE; independent review required**.

## Subject

Base main: `9d8ea394c6c037b0560908689e2ce932bf0c511c`  
Execution: `EX-NL0-001-R1`  
Worker branch: `work/nl0-001-reference-selection-r1`

## Checked

- exact NanoLab Work Order and HIGH risk policy;
- current oxDNA upstream commit and exact DSDNA8/SSDNA15/HAIRPIN entries;
- DSDNA8 topology/config/input/oracle content;
- oxDNA repository GPLv3 license;
- S08 ACS article/SI availability;
- Shi–Castro–Arya article and its explicitly linked simulation repository;
- full recursive tree of `DNA-hinge-simulations@23fd1ff7731e9017bd776f49206dc42d70d9fe91`;
- five caDNAno designs, five `.top/.conf` pairs and CPU/GPU MD inputs;
- newer leaf-spring/Nanobase/Zenodo path as a non-MVP fallback.

## Findings

1. DSDNA8/MD is the lowest-risk E1 because it has a tiny exact upstream oracle and complete inputs.
2. S08 is scientifically relevant but its machine-readable input pack was not located in this bounded search.
3. DOI `10.1021/acsnano.7b00242` is a better executable E2 seed: article + author repo provide a parameterized five-hinge family and oxDNA inputs.
4. `DNA-hinge-simulations` has no observed standalone license in its pinned recursive tree; use/redistribution decision is deferred to NL0-002.
5. No NanoLab simulation was run, so E0/E1/E2 statuses remain `NOT_RUN`.

## Required review attacks

Reviewer should attempt to falsify:

- that DSDNA8 quick fixture is sufficiently physical/useful for E1 rather than merely a software smoke;
- that the `7b00242` repository actually corresponds to the cited article and contains enough inputs to support E2;
- that selected parameter family maps cleanly to an observable hinge-angle comparison;
- that any licensing statement overreaches what the repository exposes;
- that 298 K (article) vs 300 K (`pro_CPU.in`) or old-version compatibility creates a blocker that must be resolved earlier.

Implementer cannot mark this Work Order ACCEPTED.
