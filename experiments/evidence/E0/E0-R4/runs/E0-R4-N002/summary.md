# Run E0-R4-N002 — E0-R4 control case

- Family: NEG (SYNTHETIC software control, no physics content)
- Subject: `ce477aad1e4a125c9e881fd9f6a741ec6d2fa876`
- Expected (frozen in protocol.json before execution): `{"exit_code": "nonzero", "stdout_must_not_contain": ["\"ok\": true"]}`
- Observed: see `artifacts/case_record.json` (exit code 1, checks in `0003-analysis-completed`)
- Execution outcome: RUN_COMPLETED
- Scientific outcome (per-case, mechanical): **SUPPORTED**
- Schema validation of this run's machine files: all clean

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
