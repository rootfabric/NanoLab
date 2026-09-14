# NanoLab — Independent Reproduction Rule v0.1

Rule id: `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`.

Frozen before NL5-001-C data. Independent unit = replica median, not trajectory frame. The original pooled bootstrap CI95 is descriptive only and MUST NOT be used as a prediction/tolerance interval for an independent campaign.

For a measured variant the reference package publishes three reference replica medians and their empirical envelope `[min,max]`. A fresh reproduction campaign requires three fresh replicas unless its preregistered Work Order says otherwise.

- `MATCH`: fresh campaign median-of-replica-medians is inside the reference replica envelope.
- `MISMATCH`: all fresh replica medians are strictly on the same side of the reference envelope.
- `INCONCLUSIVE`: insufficient valid replicas, incomplete integrity/analysis, or an intermediate case.
- technical failure/digest mismatch is recorded separately and never converted to scientific mismatch.

This is a conservative operational computational-reproduction classification, not proof of physical equivalence. Full rationale and machine implementation: repository `docs/release/REPRODUCTION_RULE_V0_1.md` and `scripts/release/reproduction_rule.py`.
