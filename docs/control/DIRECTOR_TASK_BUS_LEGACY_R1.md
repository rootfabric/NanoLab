# NanoLab — Director / Central Agent Entry Point

Это **первая точка входа для центрального агента**, которому владелец дал задачу уровня «организуй выполнение пункта», «веди дорожную карту», «распредели работу между агентами», «продолжи выполнение через Git» или назначил роль `DIRECTOR`.

Не восстанавливай процесс из старого чата и не придумывай собственную очередь. Истина о проекте находится в Git.

## 0. Сначала определи режим

```text
Обычная одиночная работа по Work Order
    -> стандартный Harness из AGENTS.md

Распределённая работа / несколько ролей / центральный агент
    -> этот DIRECTOR.md
    -> docs/control/GIT_TASK_BUS_POST_PILOT_CORRECTION_R1.md
    -> затем Git Task Bus
```

Если `tools/task_bus.py` и документы Git Task Bus ещё не находятся в текущем `main`, значит механизм ещё проходит pilot/review/merge gate. Не имитируй его вручную. Пока механизм не принят канонически, используй опубликованную implementation branch `control/git-task-bus-r1` и live queue branch `control/task-bus-pilot-r1` только согласно текущему Harness и Human Gate.

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

Затем для распределённого workflow обязательно прочитай:

```text
docs/control/GIT_TASK_BUS_RU.md
docs/control/GIT_TASK_BUS_POST_PILOT_CORRECTION_R1.md
docs/control/GIT_TASK_BUS_PROMPTS_RU.md
```

`GIT_TASK_BUS_POST_PILOT_CORRECTION_R1.md` является обязательной поправкой к pilot revision и имеет приоритет над устаревшими статусами P1/live trial в старых текстах этой ветки.

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

Для `BUS-SMOKE-001` ожидаемый terminal уже достигнут. Не выполнять `init`, `open`, новый `claim` или повтор пилота без нового explicit Work Order.

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

Разные `actor_id` доказывают только protocol role separation. Они не являются доказательством независимой модели/процесса/credential. Production identity proof — отдельный gate.

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
COMPLETED_SANDBOX != ACCEPTED
ACTOR_ID != INDEPENDENT_EXECUTOR_PROOF
NO P2 BEFORE P1.1-P1.4
```

## 8. Текущее состояние BUS-SMOKE-001 / BUS-001

Live pilot уже завершён. Не считать старые `READY_FOR_LIVE_TRIAL`, `NOT_RUN` или `P1 pending` актуальным состоянием.

```text
BUS-SMOKE-001 LIVE PILOT = PASS
BUS-SMOKE-001 TERMINAL   = COMPLETED_SANDBOX
BUS-001 ACCEPTANCE       = NOT YET
```

Frozen pilot subject:

```text
BASE = 95b1319600bcc64572d84c0456acb927802ab806
HEAD = d5bfc55956722e241151e0ef6db5299ee7e55123
TREE = 07dc90857bb40f9bb7e4d991ff782d5ebbc044c3
```

Live queue:

```text
control/task-bus-pilot-r1
```

Последний известный завершивший bus HEAD:

```text
6e95891db110438c3a888aec9af7721ccdb63ceb
```

Перед использованием всё равно сверяй live ref.

Tracking:

```text
Issue #19
Implementation draft PR #20
```

Пилот подтвердил:

```text
DIRECTOR open
  -> IMPLEMENTER
  -> REVIEWER
  -> VERIFIER
  -> DIRECTOR
  -> COMPLETED_SANDBOX
```

Но он не заменяет independent review реализации broker и не закрывает canonical acceptance.

## 9. Обязательный post-pilot маршрут

Текущая последовательность:

```text
P0  Mechanical implementation/tests              DONE
P1  Real BUS-SMOKE-001 multi-agent pilot          PASS
P1.1 State/evidence synchronization               NEXT
P1.2 Fresh BUS-001 implementation Reviewer        REQUIRED
P1.3 Fresh exact-head BUS-001 Verifier             REQUIRED
P1.4 Human Gate / canonical activation             REQUIRED
P2  Production policy + protected writer          LOCKED
P3  Roadmap -> Work Order adapters                 LATER
P4  Bounded launcher + identity proofs + budgets   LATER
P5  Parallel tasks / conflicts / scale campaign    LATER
```

Не начинать P2, пока P1.1-P1.4 не закрыты.

### P1.1 State/evidence synchronization

Привести human-facing state в соответствие authoritative bus:

```text
Issue #19
PR #20
docs/control/GIT_TASK_BUS_RU.md
связанные BUS evidence/status records
```

Старые отрицательные/промежуточные evidence не удалять; stale status supersede новым фактом.

Также применять hash terminology из correction R1:

```text
GIT_BLOB_SHA1
CANONICAL_BLOB_SHA256
CHECKOUT_SHA256
```

Working-tree SHA-256 не объявлять canonical blob hash.

### P1.2 Fresh implementation Reviewer

Reviewer проверяет сам broker/tooling, а не только `receipt.json`:

```text
tools/task_bus.py
tests/task_bus/
config/control/task-bus/
docs/control/GIT_TASK_BUS_RU.md
docs/control/GIT_TASK_BUS_PROMPTS_RU.md
DIRECTOR.md
AGENTS.md integration
```

Перед review: `git fetch`, resolve live tooling HEAD/TREE и PR #20 exact head. Старые SHA и PASS являются только историей.

### P1.3 Fresh exact-head Verifier

Verifier выполняет fresh checkout того же exact subject, rerun tests/positive/negative/concurrency/recovery controls. Любой новый commit после review/verification требует новой проверки для нового HEAD.

### P1.4 Human Gate

Merge eligible только при:

```text
LIVE_PILOT = PASS
HOUSEKEEPING_SYNC = PASS
IMPLEMENTATION_REVIEW = PASS
EXACT_HEAD_VERIFICATION = PASS
PR_HEAD == VERIFIED_HEAD
NO_UNRESOLVED_BLOCKERS
HUMAN_GATE = APPROVED
```

После merge обязательно fresh main + ancestry + canonical regression + проверка `AGENTS.md -> DIRECTOR.md` и доступности tooling из `main`.

## 10. Evidence hash rule

Для exact artifacts хранить отдельно:

```text
GIT_BLOB_SHA1
CANONICAL_BLOB_SHA256
CHECKOUT_SHA256
```

Для `BUS-SMOKE-001/receipt.json` Git blob:

```text
379c597d940fa9ded54ed9549d63a68ad48ead48
```

`2393d4eeea591b3896fa34ee45fa42a6c697cf17b336b4d8188d437ba257c9d6` — Windows checkout hash и должен маркироваться как `CHECKOUT_SHA256`.

## 11. Допустимые итоги до Human Gate

После P1.1-P1.3 Director может объявить только:

```text
BUS-001 = READY_FOR_HUMAN_GATE
BUS-001 = FIX_REQUIRED
BUS-001 = NOT_VERIFIED
```

Не объявлять `BUS-001 = ACCEPTED` до фактического Human Gate, canonical merge и post-merge verification.

## 12. Когда этот файл можно считать устаревшим

Если canonical `AGENTS.md` или более новая revision Task Bus явно указывает новый Director entry point или superseding correction, используй более новую canonical инструкцию. Старые ветки и чаты не имеют приоритета над свежим `main`.
