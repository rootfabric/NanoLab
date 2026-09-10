# Run E0-R2-POS001 — E0-R1 control case

- Family: POS (SYNTHETIC software control, no physics content)
- Subject: `3a2d72bcd613289321608fb42b6b668d8224b5f0`
- Expected (frozen in protocol.json before execution): `{"all_run_dirs_ok": true, "check_consistency_ok": true}`
- Observed: see `artifacts/case_record.json` (exit code 3, checks in `0003-analysis-completed`)
- Execution outcome: RUN_COMPLETED
- Scientific outcome (per-case, mechanical): **NOT_SUPPORTED**
- Schema validation of this run's machine files: all clean

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
