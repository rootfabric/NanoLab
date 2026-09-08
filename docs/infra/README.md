# NanoLab Infrastructure Track

`INFRA` — отдельная параллельная линия развития вычислительной инфраструктуры NanoLab.

Её задача — дать научной линии надёжные исполнители, CI, хранилище артефактов, CPU/GPU compute и позднее масштабирование, **не становясь источником научной истины**.

Каноническая карта INFRA хранится в `main`. Каждая стадия выполняется отдельной bounded веткой и Work Order; длинная вечная `infra`-ветка не используется.

```text
SCIENCE: NL0 → NL1 → NL2 → NL3 → NL4 → ...
              ↘   ↘   ↘   ↘
INFRA:      INFRA0 → INFRA1 → INFRA2 → INFRA3 → INFRA4 → INFRA5 → INFRA6 → INFRA7
```

По умолчанию INFRA — capability provider, а не hard gate научной дорожной карты. Если конкретный scientific Work Order требует определённую capability (например GPU exact execution), зависимость объявляется явно в этом Work Order.

Начать с [ROADMAP](ROADMAP.md), затем [SECURITY_MODEL](SECURITY_MODEL.md) и [EXECUTION_BACKENDS](EXECUTION_BACKENDS.md). Машиночитаемые план и состояние: `project/infra-plan.json` и `project/infra-state.json`.
