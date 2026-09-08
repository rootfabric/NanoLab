# NanoLab — Development Harness Protocol

**Revision:** `NL-H0-2026-09-08-R1`

Протокол адаптирован из harness Distributed World Simulator под научно-вычислительный проект NanoLab.

## 1. Базовая модель

```text
canonical main
   ├─ vision / roadmap
   ├─ plan / state
   ├─ goals / checkpoints
   ├─ policies / schemas
   └─ accepted evidence
          ↓
       Director
          ↓
  bounded Work Order
          ↓
 worker branch
          ↓
 implementation / experiment
          ↓
 durable events + evidence
          ↓
 Reviewer + Verifier
          ↓
 checkpoint proposal
          ↓
 human merge gate
          ↓
 main declares new state
```

## 2. Git — долговременная память

Новая сессия должна восстановить работу из Git без старого чата: exact base SHA и branch HEAD; checkpoint и Work Order; scope; frozen subject каждого run; последние durable events; артефакты и SHA-256; review findings; blocker и точное следующее действие. Если это невозможно, handoff неполон.

## 3. Main и рабочая ветка

`main` хранит цели, правила, checkpoint catalog и принятую научную/продуктовую картину.

Рабочая ветка хранит исполнение:

```text
docs/work/executions/<execution-id>/
docs/evidence/<work-order>/
experiments/evidence/<experiment>/<run-id>/
implementation / tests / analysis code
```

Большие raw trajectories не коммитятся только ради архива. В Git хранится manifest с размером, URI/путём хранения и SHA-256.

## 4. Bounded Work Order

Перед существенной работой Work Order фиксирует: id, checkpoint, exact base SHA, goal, risk class, claim class, allowed/forbidden paths, dependencies, required outputs, validation/experiment plan, resource budget, stop conditions и human gates.

## 5. Начало работы

До первого substantive change агент обязан:

1. прочитать control state;
2. проверить fresh `main`;
3. создать отдельную ветку от exact main;
4. создать execution passport;
5. записать `WORK_ORDER_STARTED`;
6. commit + non-force push durable start record.

Стартовый commit — recovery point, а не доказательство выполнения.

## 6. Продолжение

После каждого содержательного этапа фиксируется checkpoint, если завершена стадия protocol/setup/implementation/validation/analysis, получена серия runs, меняется actor/role, найден blocker, запущен длинный внешний job или выполнен repair.

Checkpoint содержит exact HEAD, сделанное, команды/результаты, evidence paths, риски и next action. Не нужно коммитить каждую строку лога.

## 7. Завершение

Перед `IMPLEMENTED`/`VERIFIED`/`CHECKPOINT_PROPOSED`: diff в scope, tests/experiments имеют evidence, отрицательные результаты сохранены, нет скрытых retries/skips, exact-head review fresh, handoff содержит одно next action. Implementer не выставляет `ACCEPTED`.

## 8. Repair

`FIX_REQUIRED` для MEDIUM+ требует Repair Map: failure, root-cause hypothesis, owner/module, entry points, sibling paths, tests, scientific impact, canonical fix location и revalidation plan. Повтор одинакового fix без новой информации запрещён.

## 9. Epoch drift

Если `main` изменился после старта, выполнить dependency/control compare и выбрать `CONTINUE` либо `REFRESH_REQUIRED`. Нельзя молча перепривязать старый experiment run к новому HEAD.
