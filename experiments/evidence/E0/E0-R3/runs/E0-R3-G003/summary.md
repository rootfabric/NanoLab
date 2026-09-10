# Run E0-R3-G003 — E0-R3 control case

- Family: GEO (SYNTHETIC software control, no physics content)
- Subject: `6c366e0df4822d39572362356bc65279f5a762d1`
- Expected (frozen in protocol.json before execution): `{"queries": {"q1_angle_P_O_Q": {"op": "eq", "value": 60.0, "atol": 1e-12}, "q2_angle_P_R_Q": {"op": "eq", "value": 120.0, "atol": 1e-12}}}`
- Observed: see `artifacts/case_record.json` (exit code 0, checks in `0003-analysis-completed`)
- Execution outcome: RUN_COMPLETED
- Scientific outcome (per-case, mechanical): **SUPPORTED**
- Schema validation of this run's machine files: all clean

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
