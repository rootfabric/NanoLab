# Источник и адаптация NanoLab Harness

NanoLab Harness R1 спроектирован на основе действующего harness репозитория `rootfabric/distributed-world-simulator`, прочитанного из его canonical `main` 8 сентября 2026 года.

Использованные идеи и интерфейсы:

- root `AGENTS.md` как router;
- `PROJECT_CONTROL.md`: main-owned state, bounded checkpoint flow;
- `HARNESS_CONTROL.md`: mission/work-order/role separation и Git authority;
- `docs/control/DEVELOPMENT_HARNESS_RU.md`: Git durable memory, Work Orders, append-only execution facts;
- `docs/control/HARNESS_REVIEW_AND_EVIDENCE_RU.md`: risk routing, independent review, Evidence Map;
- `docs/control/HARNESS_AUTONOMOUS_EXECUTION_RU.md`: self-execution и executor fallback;
- `CONTROL_DEVELOPMENT.ps1`: единая machine-readable control surface.

NanoLab **не копирует DWS-specific scheduler/runtime implementation целиком**: он зависит от большого DWS registry, Godot/runtime и собственных checkpoint contracts. Вместо этого сохранена контрольная модель и создан минимальный standard-library Python layer, совместимый с текущим `project/plan.json` / `project/state.json` NanoLab.

Главное расширение NanoLab — Experiment Harness: preregistration, frozen subject, уникальные run IDs, separate execution/scientific outcomes, semantic Git checkpoints и artifact provenance.
