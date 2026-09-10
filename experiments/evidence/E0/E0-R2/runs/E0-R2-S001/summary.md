# Run E0-R2-S001 — E0-R1 control case

- Family: STATUS (SYNTHETIC software control, no physics content)
- Subject: `3a2d72bcd613289321608fb42b6b668d8224b5f0`
- Expected (frozen in protocol.json before execution): `{"exit_code": 3, "stdout_must_contain": ["\"ok\": false"], "ok_field_false": true}`
- Observed: see `artifacts/case_record.json` (exit code None, checks in `0003-analysis-completed`)
- Execution outcome: RUN_FAILED_TECHNICAL
- Scientific outcome (per-case, mechanical): **NOT_EVALUATED**
- Schema validation of this run's machine files: all clean

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
