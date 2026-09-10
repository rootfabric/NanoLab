# Run E0-R3-N002 — E0-R3 control case

- Family: NEG (SYNTHETIC software control, no physics content)
- Subject: `6c366e0df4822d39572362356bc65279f5a762d1`
- Expected (frozen in protocol.json before execution): `{"exit_code": "nonzero", "stdout_must_not_contain": ["\"ok\": true"]}`
- Observed: see `artifacts/case_record.json` (exit code 1, checks in `0003-analysis-completed`)
- Execution outcome: RUN_COMPLETED
- Scientific outcome (per-case, mechanical): **SUPPORTED**
- Schema validation of this run's machine files: all clean

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
