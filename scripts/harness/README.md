# NanoLab lightweight harness runtime

Использует только Python standard library.

## Development control

```bash
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .
PYTHONPATH=scripts python3 -m harness.cli overview --root .
PYTHONPATH=scripts python3 -m harness.cli drive --root .
```

Или wrappers в корне: `CONTROL_DEVELOPMENT.sh` / `CONTROL_DEVELOPMENT.ps1`.

## Experiment evidence

```bash
PYTHONPATH=scripts python3 -m harness.experiment_cli validate <run-dir>
PYTHONPATH=scripts python3 -m harness.experiment_cli close <run-dir>
PYTHONPATH=scripts python3 -m harness.experiment_cli verify-digests <run-dir|campaign-dir> [--rev HEAD]
```

`close` проверяет наличие terminal execution event, analysis и review. Он не заменяет independent scientific verdict.

`verify-digests` (NL2-003) сверяет sha256/size каждой записи `artifacts.manifest.json` с фактическими git-блобами (`git cat-file`, не рабочей копией — урок autocrlf, VERIFIER NL2-001 §3 / NL2-002 F-3); exit 0 только при 0 mismatch, пригоден как CI-чек. Путь может быть run-каталогом или родительским каталогом кампании (сканируется поддерево). С NL2-003 `validate` также: отвергает `scientific_outcome=SUPPORTED` вне `ANALYSIS_COMPLETED` без verification-поверхности (S003) и проверяет, что `storage_location` in-Git формата содержит сегменты `campaign_id`/`run_id` манифеста (O1). Контракт provenance/recovery: `docs/research/PROVENANCE_RECOVERY_R1.md`.

Runtime намеренно мал. DWS-specific event reducer/scheduler не переносился без необходимости; расширять controller следует только вместе с machine contracts и tests.
