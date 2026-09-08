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
```

`close` проверяет наличие terminal execution event, analysis и review. Он не заменяет independent scientific verdict.

Runtime намеренно мал. DWS-specific event reducer/scheduler не переносился без необходимости; расширять controller следует только вместе с machine contracts и tests.
