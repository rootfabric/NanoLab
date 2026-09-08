# GitHub: задачи и связь с планом

Первичная очередь создана вместе с документальным фундаментом. Статусы ниже отражают принятое состояние (см. `project/state.json`); зависимости — в `project/plan.json`.

| Issue | Work ID / стадия | Назначение |
|---|---|---|
| [#1](https://github.com/rootfabric/NanoLab/issues/1) | NL0–NL8 | Общий трекер от эксперимента к наномашинам |
| [#2](https://github.com/rootfabric/NanoLab/issues/2) | NL0-001 | **ACCEPTED** — выбраны DSDNA8/MD (E1) и Shi–Castro–Arya family (E2) |
| [#3](https://github.com/rootfabric/NanoLab/issues/3) | NL0-002 | **ACCEPTED** — E1 CLEAR / E2 UNKNOWN (REFERENCE_ONLY), матрица лицензий, owner decisions |
| [#4](https://github.com/rootfabric/NanoLab/issues/4) | NL0-003 | **ACCEPTED** — `E1-PROTO-R1` + `E2-SETUP-R1`; PR #21 merged |
| [#5](https://github.com/rootfabric/NanoLab/issues/5) | NL1-001/002 | Первый исполняемый путь без ИИ |
| [#6](https://github.com/rootfabric/NanoLab/issues/6) | NL2-001/002/003 | E0/E1, контракты, статистика, provenance и recovery |
| [#7](https://github.com/rootfabric/NanoLab/issues/7) | NL3-001/002 | Параметризованный шарнир и E2 |
| [#8](https://github.com/rootfabric/NanoLab/issues/8) | NL4-001/002/003 | Ограниченный AI-исследователь, E3 и MVP |

Последующие NL5–NL8 уже запланированы в [ROADMAP](../ROADMAP.md) и [WORK_QUEUE](WORK_QUEUE.md), но не разбиты на множество преждевременных Issues. Новые задачи создаются при достижении соответствующей границы.

Номер issue не заменяет Work ID. Групповая задача стадии закрывается только после принятия всех относящихся к ней работ. Merge документации не закрывает перечисленные задачи автоматически.

Для продолжения: [AGENT_START](AGENT_START.md); следующий Work Order — `NL1-001` ([WORK_QUEUE](WORK_QUEUE.md)). В [state.json](../../project/state.json) сохранено машинное отображение Issues.
