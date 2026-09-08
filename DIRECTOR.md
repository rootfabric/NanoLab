# NanoLab — Director / Central Agent Entry Point

Это **первая точка входа для центрального агента**, которому владелец дал задачу уровня «организуй выполнение пункта», «веди дорожную карту», «распредели работу между агентами», «продолжи выполнение через Git» или назначил роль `DIRECTOR`.

Не восстанавливай процесс из старого чата и не придумывай собственную очередь. Истина о проекте находится в Git.

## 0. Сначала определи режим

```text
Обычная одиночная работа по Work Order
    -> стандартный Harness из AGENTS.md

Распределённая работа / несколько ролей / центральный агент
    -> этот DIRECTOR.md
    -> затем Git Task Bus
```

Если `tools/task_bus.py` и документы Git Task Bus ещё не находятся в текущем `main`, значит механизм ещё проходит пилот/merge gate. Не имитируй его вручную. Для текущего пилота используй опубликованную implementation branch `control/git-task-bus-r1` и live queue branch `control/task-bus-pilot-r1`.

## 1. Обязательное восстановление состояния

Сначала прочитай обычный canonical control plane:

```text
AGENTS.md
PROJECT_CONTROL.md
HARNESS_CONTROL.md
project/state.json
project/plan.json
```

Для инфраструктуры дополнительно:

```text
project/infra-state.json
project/infra-plan.json
```

Затем для распределённого workflow прочитай:

```text
docs/control/GIT_TASK_BUS_RU.md
docs/control/GIT_TASK_BUS_PROMPTS_RU.md
```

Не продолжай задачу на основании текста предыдущего агента, если Git показывает другое состояние.

## 2. Две разные истины

```text
main
  = canonical roadmap / accepted project state

Git Task Bus
  = execution facts / кто сейчас должен действовать / handoff history
```

`COMPLETED_SANDBOX`, `PASS`, зелёный CI или сообщение агента сами по себе не меняют canonical state. Scientific/project acceptance происходит только по действующему Harness и Human Gate.

## 3. Первый запрос Director

В checkout, где доступен `tools/task_bus.py`:

```bash
python tools/task_bus.py --actor director-pilot status
```

Для конкретной задачи:

```bash
python tools/task_bus.py --actor director-pilot history BUS-SMOKE-001
```

Для production-версии actor/task берутся из активной policy/Work Order, а не копируются из пилота.

## 4. Как читать `status`

```text
CLAIM
  -> текущая роль этого actor может забрать задачу

CONTINUE
  -> у этого actor уже есть живой lease; продолжай именно его

DISPATCH_OR_WAIT
  -> задача готова другой роли
  -> если реально доступен независимый executor/subagent: запусти его
  -> иначе зафиксируй WAIT_EXTERNAL и закончи текущий проход

RECLAIM
  -> lease истёк; Director проверяет факты и только затем выполняет reclaim

WAIT_RECLAIM
  -> чужой lease истёк, но этот actor не Director; не захватывать самовольно

BLOCKED
  -> прочитай history/blocker, устрани причину в разрешённом scope или эскалируй

BUDGET_EXHAUSTED
  -> остановись; не создавай новые ID ради обхода лимита

COMPLETED_SANDBOX / CANCELLED
  -> terminal для данного bus workflow; отдельно проверь canonical state
```

## 5. Основная петля Director

```text
fresh main + state
        ↓
fresh bus status/history
        ↓
определить ожидаемую роль
        ↓
есть реальный независимый исполнитель?
    ├─ да -> дать ему role prompt + repo/task/bus ref + bounded scope
    └─ нет -> WAIT_EXTERNAL; Git остаётся durable handoff
        ↓
после следующего Git event снова fresh read
        ↓
FAIL? -> repair loop через Implementer
BLOCKED? -> resolve/escalate
candidate drift? -> invalidate
lease expired? -> reclaim после проверки
        ↓
Reviewer -> Verifier -> Director gate
        ↓
только затем checkpoint proposal / Human Gate по canonical Harness
```

**Director не выполняет роли Reviewer/Verifier под другими именами ради PASS.** Если среда не умеет реально создать отдельную сессию, задача остаётся в Git до прихода другого агента.

## 6. Что передавать запускаемому агенту

Минимальный пакет, без пересказа истории чата:

```text
repository
role / actor_id
work_order_id / task_id
canonical main SHA observed by Director
Git Task Bus branch
implementation/tooling ref if not in main
allowed / forbidden scope
resource budget
stop conditions
instruction: read AGENTS.md + role prompt + fresh status/history
```

Полные role prompts находятся в:

```text
docs/control/GIT_TASK_BUS_PROMPTS_RU.md
```

Не сокращай их до «сделай задачу и скажи PASS», если нужна независимая проверка.

## 7. Инварианты центрального агента

```text
GIT IS DURABLE MEMORY; CHAT IS NOT
MAIN DECLARES PROJECT STATE
TASK BUS REPORTS EXECUTION FACTS
ONE ACTIVE LEASE PER TASK
IMPLEMENTER CANNOT SELF-REVIEW OR SELF-ACCEPT
REVIEW/VERIFY EXACT IMMUTABLE HEAD + TREE
FAILED RESULTS REMAIN DURABLE
NO FORCE PUSH
NO DIRECT MAIN WRITE
NO FAKE SUBAGENT / SESSION ID
NO BACKGROUND PROMISE WITHOUT A REAL EXECUTOR
NO SCIENTIFIC ACCEPTANCE FROM BUS STATUS ALONE
```

## 8. Текущий пилот BUS-SMOKE-001

Пока Git Task Bus не принят в `main`, живое испытание находится здесь:

```text
implementation/tooling:
control/git-task-bus-r1

live queue:
control/task-bus-pilot-r1

task:
BUS-SMOKE-001

tracking:
Issue #19
Implementation draft PR #20
```

Не выполнять `init` или `open` повторно: задача уже создана. Сначала `status/history`.

Ожидаемый живой цикл:

```text
DIRECTOR
  -> IMPLEMENTER
  -> REVIEWER
  -> VERIFIER
  -> DIRECTOR
  -> COMPLETED_SANDBOX
```

Это проверка механизма распределённой разработки. Она **не закрывает NL checkpoint и не является INFRA6 acceptance**.

## 9. Когда этот файл можно считать устаревшим

Если canonical `AGENTS.md` или более новая revision Task Bus явно указывает новый Director entry point, используй более новую canonical инструкцию. Старые ветки и чаты не имеют приоритета над свежим `main`.
