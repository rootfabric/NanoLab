# Run E0-R3-S003-RETRY1 — E0-R3 control case

- Family: STATUS (SYNTHETIC software control, no physics content)
- Subject: `6c366e0df4822d39572362356bc65279f5a762d1`
- Expected (frozen in protocol.json before execution): `{"separation_probe": true}`
- Observed: see `artifacts/case_record.json` (exit code 3, checks in `0003-analysis-completed`)
- Execution outcome: RUN_COMPLETED
- Scientific outcome (per-case, mechanical): **NOT_SUPPORTED**
- Schema validation of this run's machine files: all clean

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
