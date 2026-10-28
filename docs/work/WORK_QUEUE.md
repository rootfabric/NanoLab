# NanoLab — Work Queue

Оперативный view: [CURRENT_QUEUE](CURRENT_QUEUE.md), источник — `project/operations/*.json`. Научная приёмка и зависимости остаются в `project/state.json` и `project/plan.json`.

```bash
PYTHONPATH=scripts python3 -m harness.cli drive --root .
PYTHONPATH=scripts python3 -m harness.operations --format markdown
```

Не дописывать все handoffs в один общий файл: новая task card — отдельный JSON, execution history — соответствующий `EX-*/events/`. Это устраняет конфликты независимых веток на общей таблице.

## Сохранённая история

[WORK_QUEUE_HISTORY_PRE_FLOW_R1.md](WORK_QUEUE_HISTORY_PRE_FLOW_R1.md) — побайтовая копия всей предыдущей очереди из `main@3b567ae33f247b182b2ae451d2cc4598a9e76019`. Старые evidence, failed/inconclusive результаты и ссылки не удалены. Старые NEXT_ACTION/IN_PROGRESS не интерпретировать как текущий dispatch.

FLOW-R1 не меняет scientific acceptance. Команды записи новых C0 events: [FLOW_R1_COMMANDS](FLOW_R1_COMMANDS.md). Политика: [FLOW-THROUGHPUT-R1](../control/FLOW_THROUGHPUT_R1.md).
