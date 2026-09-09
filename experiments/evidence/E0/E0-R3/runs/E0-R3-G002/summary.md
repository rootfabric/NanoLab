# Run E0-R3-G002 — E0-R3 control case

- Family: GEO (SYNTHETIC software control, no physics content)
- Subject: `6c366e0df4822d39572362356bc65279f5a762d1`
- Expected (frozen in protocol.json before execution): `{"queries": {"q1_distance_AB": {"op": "eq", "value": 0.0, "atol": 1e-12}, "q2_angle_at_B": {"op": "undefined"}}}`
- Observed: see `artifacts/case_record.json` (exit code 0, checks in `0003-analysis-completed`)
- Execution outcome: RUN_COMPLETED
- Scientific outcome (per-case, mechanical): **SUPPORTED**
- Schema validation of this run's machine files: all clean

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
