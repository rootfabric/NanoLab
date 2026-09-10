# Run E0-R4-G001 — E0-R4 control case

- Family: GEO (SYNTHETIC software control, no physics content)
- Subject: `ce477aad1e4a125c9e881fd9f6a741ec6d2fa876`
- Expected (frozen in protocol.json before execution): `{"queries": {"q1_distance_AC": {"op": "eq", "value": 1.4142135623730951, "atol": 1e-12}, "q2_angle_at_B": {"op": "eq", "value": 90.0, "atol": 1e-12}}}`
- Observed: see `artifacts/case_record.json` (exit code 0, checks in `0003-analysis-completed`)
- Execution outcome: RUN_COMPLETED
- Scientific outcome (per-case, mechanical): **SUPPORTED**
- Schema validation of this run's machine files: all clean

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
