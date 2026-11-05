# Текущая очередь

Операционные задачи: `project/operations/*.json`; historical DNA scientific status — `project/state.json`; независимые atomistic P0–P6 — `project/product-plan.json` и `project/product-state.json`. Старый WORK_QUEUE.md хранит историю, его NEXT_ACTION не является dispatch.

```bash
PYTHONPATH=scripts python3 -m harness.cli drive --root .
PYTHONPATH=scripts python3 -m harness.operations --root . --format markdown
```

На Windows: `$env:PYTHONPATH="scripts"; python -m harness.cli drive --root .`.

Ближайший product slice: ATOMISTIC-ADAPTER-PREP и ATOMISTIC-APP-PREP, параллельно ATOMISTIC-REFERENCE-PREP для P0. Каждая карточка задаёт consumer/demo/budget/stop. Показанное READY — доступная подготовка; IN_PROGRESS — назначенная работа, не доказанный actual run или acceptance. WIP ≤3; waiting tasks сохраняют actor/resume condition, повторный аудит неизменного blocker не нужен.

Operations schema остаётся C0-only. Карточки не разрешают physics. Только [WO-ATOMISTIC-PRODUCT-R1](WO-ATOMISTIC-PRODUCT-R1.md) разрешает narrow engineering validation нового adapter: actual calculations, один material/model, disposable Linux, ≤4096 atoms/2000 MD steps per run, ≤8 actual pilot runs/20 минут/2 GiB суммарно, последовательно. Machine profile/stops — product-plan. Без этого WO либо для future science нужен собственный launch profile; никакого NL5/E5 dispatch. P0 OPEN, принятых P-стадий нет.

Исторические RESOURCE-R1/U1/U2/INTEGRATION-R1 и DNA real-source/offline slice сохраняются; их ожидание не блокирует atomistic software path. NL6-TESTRIG-PREP может идти параллельно по прежнему C0 scope. Scientific DNA launch gates неизменны. Политика: [FLOW-R1](../control/FLOW_THROUGHPUT_R1.md), [roadmap](../ROADMAP.md).
