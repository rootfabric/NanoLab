# EX-NL0-001-R1 — Handoff summary

## Scope

Work Order `NL0-001`: выбрать воспроизводимый E1 и исполняемый E2 candidate family. Никакие simulations/E0–E6 не выполнялись.

## Result

- E1 recommendation: official oxDNA `DSDNA8/MD` quick regression fixture pinned at upstream `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`.
- E2 recommendation: Shi–Castro–Arya five-hinge family from DOI `10.1021/acsnano.7b00242`, data repo pinned at `23fd1ff7731e9017bd776f49206dc42d70d9fe91`.
- S08 (`7b06470`): retained as scientific reference; machine input pack not located in bounded inspection.
- Rich future reference: leaf-spring structure 196 / Zenodo 8248808 / `sulcgroup/hinges`.

## Durable evidence

- `docs/research/REFERENCE_SELECTION.md`
- `docs/research/INPUT_AVAILABILITY.md`
- `docs/research/SOURCES.md`
- `docs/evidence/NL0-001/IMPLEMENTER_EVIDENCE.md`
- execution events in this directory

## Validation performed

- exact upstream commits/trees read through GitHub;
- selected DSDNA8 files fetched and SHA-256 recorded;
- `quick_input` and `quick_compare` inspected rather than inferred;
- complete recursive tree of selected E2 data repository inspected;
- article/repository descriptions cross-checked;
- negative evidence (missing S08 machine pack, missing E2 repository LICENSE) retained explicitly.

## Limits

No oxDNA build/run, no experimental validation, no independent Reviewer/Verifier verdict. This handoff is `C0_SOFTWARE_ONLY` source-selection evidence and does not change E1/E2 from `NOT_RUN`.

## Next actor

`REVIEWER`, then `VERIFIER` because risk class is HIGH. If PASS, Director may accept **NL0-001 only** and activate NL0-002 / NL0-003 according to dependencies.
