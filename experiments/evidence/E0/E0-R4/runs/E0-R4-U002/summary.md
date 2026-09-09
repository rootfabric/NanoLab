# Run E0-R4-U002 — E0-R4 control case

- Family: UNIT (SYNTHETIC software control, no physics content)
- Subject: `ce477aad1e4a125c9e881fd9f6a741ec6d2fa876`
- Expected (frozen in protocol.json before execution): `{"verdicts": {"u002_wrong_20.json": "REJECTED", "u002_wrong_293_15.json": "REJECTED", "u002_wrong_0_29315.json": "REJECTED", "u002_wrong_0_0978.json": "REJECTED"}}`
- Observed: see `artifacts/case_record.json` (exit code 0, checks in `0003-analysis-completed`)
- Execution outcome: RUN_COMPLETED
- Scientific outcome (per-case, mechanical): **SUPPORTED**
- Schema validation of this run's machine files: all clean

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
