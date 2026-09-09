# Run E0-R2-G001 — E0-R1 control case

- Family: GEO (SYNTHETIC software control, no physics content)
- Subject: `3a2d72bcd613289321608fb42b6b668d8224b5f0`
- Expected (frozen in protocol.json before execution): `{"queries": {"q1_distance_AC": {"op": "eq", "value": 1.4142135623730951, "atol": 1e-12}, "q2_angle_at_B": {"op": "eq", "value": 90.0, "atol": 1e-12}}}`
- Observed: see `artifacts/case_record.json` (exit code None, checks in `0003-analysis-completed`)
- Execution outcome: RUN_FAILED_TECHNICAL
- Scientific outcome (per-case, mechanical): **NOT_EVALUATED**
- Schema validation of this run's machine files: all clean

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
