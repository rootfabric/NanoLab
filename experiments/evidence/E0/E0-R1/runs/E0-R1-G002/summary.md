# Run E0-R1-G002 — E0-R1 control case

- Family: GEO (SYNTHETIC software control, no physics content)
- Subject: `5a151f751f7d60c1902e43fa503efd9a6037b236`
- Expected (frozen in protocol.json before execution): `{"queries": {"q1_distance_AB": {"op": "eq", "value": 0.0, "atol": 1e-12}, "q2_angle_at_B": {"op": "undefined"}}}`
- Observed: see `artifacts/case_record.json` (exit code None, checks in `0003-analysis-completed`)
- Execution outcome: RUN_FAILED_TECHNICAL
- Scientific outcome (per-case, mechanical): **NOT_EVALUATED**
- Schema validation of this run's machine files: all clean

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
