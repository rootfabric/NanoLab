# Карта документации

Начать с [README](../README.md), затем читать [VISION](VISION.md), [ROADMAP](ROADMAP.md) и [MVP](MVP.md).

## Control / Harness

- [Project Control](../PROJECT_CONTROL.md) — canonical `main`, единицы управления и условия приёмки.
- [Harness Control](../HARNESS_CONTROL.md) — короткий router для control surface.
- [Development Harness](control/DEVELOPMENT_HARNESS_RU.md) — Work Orders, recovery, repair и handoff.
- [Review & Evidence](control/HARNESS_REVIEW_AND_EVIDENCE_RU.md) — risk routing, claim ladder и Evidence Map.
- [Autonomous Execution](control/HARNESS_AUTONOMOUS_EXECUTION_RU.md) — границы автономии и executor fallback.
- [Experiment Harness](control/EXPERIMENT_HARNESS_RU.md) — preregistration и durable START/CONTINUATION/END.
- [Branching & Git](control/BRANCHING_AND_GIT_RU.md) — ветки, commits и PR.
- [Источник harness](control/HARNESS_SOURCE_NOTE.md) — какие части DWS использованы как база.

## Система

- [Архитектура](ARCHITECTURE.md), [контракты данных](DATA_CONTRACTS.md), [ИИ и управление исследованиями](AI_ORCHESTRATION.md).
- [Научная методология](SCIENTIFIC_METHOD.md), [среда и вычислительные ресурсы](OPERATIONS.md), [принятые исходные решения](DECISIONS.md).

## Исследования

- [Программа E0–E6](experiments/README.md) и [шаблон experiment campaign](experiments/EXPERIMENT_RUN_TEMPLATE.md).
- [Инструменты и варианты интеграции](research/TOOL_LANDSCAPE.md).
- [Источники и границы проверки](research/SOURCES.md).
- [Открытые вопросы](research/OPEN_QUESTIONS.md).
- [Дальние направления и сохранённые идеи](RESEARCH_PORTFOLIO.md).

## Работа и доказательства

- [Очередь работ](work/WORK_QUEUE.md), [первое задание](work/WO-NL0-001.md), [старт агента](work/AGENT_START.md).
- [Шаблон Work Order](work/templates/WORK_ORDER_TEMPLATE.md), [Branch Passport](work/templates/BRANCH_PASSPORT_TEMPLATE.md).
- [GitHub Issues и связь с планом](work/GITHUB_TRACKING.md).
- [Машиночитаемый план](../project/plan.json), [текущее состояние](../project/state.json), [журнал передачи работы](work/SESSION_LOG.md).
- [Требования к evidence](evidence/README.md), [Evidence Map template](evidence/EVIDENCE_MAP_TEMPLATE.md), [Scientific Review template](review/SCIENTIFIC_REVIEW_TEMPLATE.md).
- [Участие](../CONTRIBUTING.md), [лицензирование](../LICENSE_POLICY.md).

Machine contracts находятся в `config/control/harness/`, исполняемый lightweight controller — в `scripts/harness/`.

Документы задают замысел и критерии. `project/state.json` задаёт текущую стадию. `project/plan.json` задаёт идентификаторы и зависимости работ. GitHub Issues служат рабочими обсуждениями, но не подменяют научные доказательства.
