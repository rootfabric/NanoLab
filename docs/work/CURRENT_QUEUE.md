# Текущая очередь

Текущие операционные задачи хранятся по одной в `project/operations/*.json`; научные статусы — в `project/state.json`. Не редактировать длинный исторический WORK_QUEUE.md ради каждой новой передачи.

```bash
PYTHONPATH=scripts python3 -m harness.cli drive --root .
PYTHONPATH=scripts python3 -m harness.operations --root . --format markdown
```

На Windows использовать `$env:PYTHONPATH="scripts"; python -m harness.cli drive --root .`.

Порядок: RESOURCE-R1, U1/U2, совместная C0-интеграция, реальные входы, offline slice. NL6-TESTRIG-PREP идёт параллельно; отсутствие follower не запрещает C0 подготовку одиночного driver. Никаких научных запусков из этой очереди. READY означает доступность ограниченной подготовки, не уже работающего агента.

Политика: [FLOW-THROUGHPUT-R1](../control/FLOW_THROUGHPUT_R1.md). История: [WORK_QUEUE](WORK_QUEUE.md).
