# Git Task Bus — распределённый цикл NanoLab

Revision: `NL-BUS-PILOT-R1`, 2026-09-08. Work Order: `BUS-001`.
Статус документа: реализация пилота; не утверждённая замена canonical Harness.
Claim ceiling: `C0_SOFTWARE_ONLY`. Production activation и merge — Human Gate.

## 1. Решение

Git используется как низкочастотная очередь заданий и журнал переходов, а не
как транспорт телеметрии или полноценная замена RabbitMQ/Kafka. Каждый агент
может восстановить задачу из репозитория без предыдущего чата.

```text
main: roadmap, policies, accepted project state
  |
  +-- control/git-task-bus-r1: implementation, tests, instructions, evidence
  |
  +-- control/task-bus-pilot-r1: task-bus/queue.json, execution facts only
  |
  +-- work/bus-smoke-001-r1: candidate JSON artifact, created by Implementer
```

Служебную ветку очереди НЕЛЬЗЯ сливать в main. Она не является второй roadmap.
В main продолжают действовать `project/plan.json`, `project/state.json`,
`project/infra-plan.json` и `project/infra-state.json`. Пилот не меняет ни один
из этих файлов, не закрывает NL0 и не реализует INFRA6 scientific scheduler.

## 2. Что уже существует: исследование первичных источников

Сведения проверены 2026-09-08. Упоминание решения не означает установки или
аудита его безопасности. Код upstream в этот пилот не копировался.

| Решение | Что применимо | Почему не устанавливаем целиком для первого опыта |
|---|---|---|
| Beads [S1] | Граф зависимостей, ready queue, claim, durable task memory | Текущая реализация использует Dolt; JSONL — экспорт, не источник истины. Embedded mode — один writer, server mode требует Dolt server для нескольких writers. Это уже отдельный backend, а не просто файл в main |
| MCP Agent Mail [S2] | Идентичности, inbox/outbox, threads, leases, Git-аудит | Требует MCP-сервис и SQLite. File reservations по умолчанию advisory; наличие записи о reservation само по себе не является эксклюзивным распределённым lock |
| Gas Town [S3] | Главный координатор, независимые workers, восстановление сессий, handoff, merge coordination | Полезный следующий кандидат для запуска CLI-агентов, но внедрение всей системы с её зависимостями и собственной моделью ролей избыточно для одного C0 smoke |
| GitHub Agentic Workflows [S4] | Event-driven запуск, разделение read-only agent и контролируемых write outputs | Возможный будущий launcher. Не переносим автоматически право писать/мерджить или запускать trusted runner |

Заимствованы проверенные архитектурные приёмы: dependency-aware queue,
append-only events, competing consumers, lease + fencing token, idempotent
message handling, reconciliation и explicit role handoff. Собственная часть —
не новый оркестратор LLM, а небольшой транспорт и state machine, связывающий
эти приёмы с exact-head и Human Gate NanoLab.

При масштабировании сначала повторно оценить Beads/Agent Mail/Gas Town, а не
расширять этот пилот в самостоятельную платформу без сравнительного опыта.

## 3. Роли и ответственность

| Роль | Что делает | Что не делает |
|---|---|---|
| HUMAN | Даёт цель, разрешает merge/production/budget gates | Не переносит вручную каждое сообщение между агентами |
| DIRECTOR | Декомпозирует цель, открывает задачи, связывает dependencies, вызывает подходящий executor либо фиксирует ожидание, разбирает сбои, проверяет комплектность | Не выдаёт собственный код за независимый review; не переписывает научную истину |
| IMPLEMENTER | Забирает подходящую задачу, публикует candidate и отчёт | Не принимает собственную работу |
| REVIEWER | Проверяет scope, корректность контракта, риски и evidence, публикует PASS/FAIL/INSUFFICIENT_EVIDENCE | Не правит candidate незаметно; исправление возвращает Implementer |
| VERIFIER | В свежем checkout воспроизводит проверки exact HEAD/TREE и отрицательные контроли | Не наследует чужой PASS |
| EXECUTOR/LAUNCHER | В перспективе запускает CLI/subagent по разрешённому профилю и бюджету | Не определяет scientific verdict; в этом пилоте не установлен |

Один запуск агента — одна роль. `implementer-a` и `implementer-b` — два
конкурирующих исполнителя, а не два названия одной сессии для self-review.
В живом опыте reviewer/verifier должны быть действительно отдельными сессиями.

Профили и capabilities находятся в `pilot-policy.json`; авторитетная копия
после bootstrap находится в самой очереди. Не править её вручную в ходе опыта.
В v1 нет self-registration: добавление новых профилей требует отдельного
пилота/revision через Director, а не произвольной записи из worker.

## 4. Автомат состояний

`phase` в queue — ожидаемая следующая роль, а не canonical Work Order status.
Наличие `lease` означает, что эта роль сейчас выполняется.

```text
DIRECTOR open
  -> IMPLEMENTER (ready -> claim -> work -> finish)
  -> REVIEWER    (ready -> claim -> review -> finish)
  -> VERIFIER    (ready -> claim -> exact re-run -> finish)
  -> DIRECTOR    (ready -> claim -> closure check -> finish)
  -> COMPLETED_SANDBOX
```

`FAIL` от Reviewer или Verifier сохраняет отрицательный отчёт в истории,
сбрасывает approvals/subject и возвращает задачу Implementer. Новый candidate
проходит обе независимые роли заново. `INSUFFICIENT_EVIDENCE` ведёт в BLOCKED;
Director после устранения причины возобновляет ту же роль. Отдельно доступны
`block`, `resume`, `release`, `reclaim`, `invalidate`, `cancel`.

Для пилота `COMPLETED_SANDBOX` означает завершение формального workflow,
**не ACCEPTED в main**. У реальной development-задачи после Director будет
CHECKPOINT_PROPOSED / WAITING_HUMAN, затем разрешённый merge и отдельная
проверка canonical acceptance record. Этот production-маршрут в v1 специально
не включён. Менять scientific state через task bus технически не предусмотрено.

Canonical Harness не переписывается: bus claim соответствует durable START,
finish — handoff/continuation, report — evidence; формальная приёмка основной
реализации BUS-001 всё равно требует Reviewer + Verifier и Human merge gate.

## 5. Протокол записи и гарантии

Авторитетный файл очереди — `task-bus/queue.json` на bus branch. Он содержит
`schema_version`, immutable bootstrap `policy` и последовательность `events`.
Текущий state выводится reducer-ом, отдельной вручную редактируемой копии нет.
Одна запись одновременно завершает этап и делает следующий этап доступным:
нет разрыва «результат записали, reviewer task создать забыли».

Каждое сообщение содержит `id`, `actor`, `op`, `task`, `at` (UTC Unix seconds)
и `data`. Candidate: `{head, tree, ref}`. Report: exact subject, verdict,
summary и checks с командами/exit codes. Report хранится в bus, не меняя
candidate HEAD, поэтому запись review не устаревает от своего собственного commit.

Транзакция:

1. Fetch bus ref в уникальный временный local ref; прочитать и replay весь журнал.
2. Проверить роль, capabilities, dependency, lease, budget, transition и report.
3. Создать один commit с единственным родителем — только что прочитанным HEAD.
4. Non-force push этого commit в bus ref.
5. При конфликте перечитать журнал и ЗАНОВО проверить переход, а не rebase
   старого claim. При потере ответа найти `message_id` в журнале и вернуть
   уже зафиксированный результат. Максимум пять transport attempts.

Git допускает обычное обновление branch только fast-forward [S5]. Два sibling
commit от одного HEAD не могут оба стать непосредственным новым HEAD без
пересчёта. Побеждает одна заявка; другая после fresh read увидит чужой lease.
GitHub API-эквивалент: create tree -> create commit с exact parent -> update
ref с `force=false`; документация ref API описывает этот режим [S6].

Обычные Issue comments/labels/assignees НЕ являются lock. Они могут быть
человекочитаемой проекцией, но не источником истины для claim.

Lease по умолчанию 1800 секунд. Heartbeat только при действительно длинной
работе, до истечения lease; не коммитить холостое ожидание. Просроченный lease
забирает Director через `reclaim`; новый claim получает новый token. Старый
worker может физически продолжить вычисления, но его finish больше не пройдёт.

Все hosts должны синхронизировать UTC. Проверяется грубый clock skew >60 s;
lease expiry — средство восстановления, а не доказательство смерти процесса.
Безопасность от поздних результатов обеспечивает проверка token при записи,
а не абсолютная точность часов.

Гарантии в cooperative model: сериализованные transitions, не более одного
текущего lease, идемпотентное принятие одного message ID, bounded retries,
сохранение отрицательных исходов. **Нет exactly-once исполнения внешней
команды.** Для GPU/CI/external side effects понадобится отдельный job ID,
проверка существующего job и fencing на стороне executor.

## 6. Exact subject, scope и независимость

При каждом `finish` транспорт заново fetch-ит candidate ref и проверяет:
HEAD и TREE, ancestry от frozen base, непустой diff и только разрешённые пути.
Пилот разрешает лишь `docs/work/pilots/<BUS-ID>/...`. Symlink, submodule и
исполняемые файлы не принимаются; data files должны иметь mode 100644.
Новый HEAD без явной invalidation не получает старый PASS.

Перед выполнением тестов Reviewer/Verifier самостоятельно сверяют этот же
subject. Между проверкой candidate ref и записью bus event нет общей
транзакции двух refs; next gate повторяет сверку. Исторический verdict всегда
относится к immutable SHA, не к любому будущему содержимому ветки.

Код broker не исполняет команды из отчётов, текста задачи, PR или комментариев.
Только агент по своей доверенной инструкции запускает разрешённые проверки.

Идентичности акторов в v1 — protocol identities. Один владелец с write-доступом
технически способен представиться разными ролями или вручную изменить журнал.
Проверка разных actor_id НЕ доказывает независимость моделей/людей. Для
production нужны отдельные credentials/attestations, защищённый bus ref и
server-side validation либо единственный доверенный writer. В этом пилоте
такая защита не включалась; доступ рассчитан на доверенных агентов владельца.

## 7. Director: запуск, ожидание и восстановление

Director читает `status` и `history`, а не вспоминает чат. `CLAIM` означает,
что профиль подходит; `DISPATCH_OR_WAIT` — нужен другой профиль; `CONTINUE` —
есть собственный активный lease; `RECLAIM` — lease истёк; `BLOCKED` и
`BUDGET_EXHAUSTED` требуют содержательного решения.

Если в среде действительно доступен запуск независимого subagent, Director
запускает нужную роль с repo/task/bus ref и ограниченным scope. Иначе он
оставляет задачу ready и завершает проход с `WAIT_EXTERNAL`; другой агент
при следующем запуске увидит очередь. Нельзя писать, что subagent запущен,
если не существует подтверждённого executor/job/session ID.

В пилоте используется pull-модель: агенты вызывают `status` при входе и после
handoff. Никакой фоновый процесс этим документом не запускается. Для полностью
автоматической работы отдельно разворачивается scheduler/launcher. Ожидание
должен обслуживать обычный процесс/таймер, а не постоянно рассуждающий LLM.
Webhook допустим как ускоритель пробуждения; обязательна reconciliation по
Git: GitHub не автоматически повторяет все неуспешные webhook deliveries [S7].

Ограничения: 16 claims и 2 repair loops на задачу. После исчерпания не создавать
новый ID ради обхода бюджета: block/cancel и отдельное решение Director/Human.
Пилот не изменяет конфигурацию сервера, не запускает платный compute и не
подключает public PR code к trusted self-hosted runner.

## 8. Установка и команды

Нужны Python >=3.10 и Git с `--no-write-fetch-head`; проверено локально на
Python 3.13.5 и Git 2.47.3 (Linux). Windows этим проходом не проверялся.
У каждого живого агента собственный clone/worktree и уже настроенный Git push
доступ владельца. Токены не вставлять в задания или файлы репозитория.

```bash
git clone https://github.com/rootfabric/NanoLab.git NanoLab-bus-agent
cd NanoLab-bus-agent
git fetch origin
git switch --track origin/control/git-task-bus-r1
python -m unittest discover -s tests/task_bus -v
python tools/task_bus.py --actor director-pilot status
python tools/task_bus.py --actor director-pilot history BUS-SMOKE-001
```

Пути для разных агентов могут отличаться. Все команды CLI принимают `--repo`;
поэтому tooling можно держать на control branch, а candidate — в отдельном
worktree от exact main. Сам broker не checkout-ит ветки, не трогает пользовательский
index и не сбрасывает незакоммиченную работу.

Live очередь подготавливается один раз. **Если она уже опубликована — не
выполнять init/open повторно.** Bootstrap для нового чистого опыта:

```bash
python tools/task_bus.py --actor director-pilot init --policy config/control/task-bus/pilot-policy.json --base 95b1319600bcc64572d84c0456acb927802ab806
python tools/task_bus.py --actor director-pilot open --spec config/control/task-bus/pilot-task.json
```

Основные действия:

```bash
python tools/task_bus.py --actor implementer-a status
python tools/task_bus.py --actor implementer-a claim BUS-SMOKE-001
python tools/task_bus.py --actor implementer-a heartbeat BUS-SMOKE-001
python tools/task_bus.py --actor implementer-a finish BUS-SMOKE-001 --candidate-ref work/bus-smoke-001-r1 --report ../bus-implementer-report.json
python tools/task_bus.py --actor reviewer-a claim BUS-SMOKE-001
python tools/task_bus.py --actor reviewer-a finish BUS-SMOKE-001 --report ../bus-reviewer-report.json
python tools/task_bus.py --actor verifier-a claim BUS-SMOKE-001
python tools/task_bus.py --actor verifier-a finish BUS-SMOKE-001 --report ../bus-verifier-report.json
python tools/task_bus.py --actor director-pilot claim BUS-SMOKE-001
python tools/task_bus.py --actor director-pilot finish BUS-SMOKE-001 --report ../bus-director-report.json
```

Это последовательность разных сессий, не инструкция одной модели выполнить
все роли. Отчёты создаются после реальной работы по контракту раздела 5;
команды нельзя запускать с вымышленными результатами или несуществующими файлами.
Полные задания ролей — [GIT_TASK_BUS_PROMPTS_RU.md](GIT_TASK_BUS_PROMPTS_RU.md).

Receipt token сохраняется в локальном Git metadata каталоге
`task-bus-receipts/<actor>/<task>.json`. Pending request ID сохраняется до
подтверждения; повтор той же CLI-команды после потерянного ответа использует
его снова. `--message-id` позволяет явно закрепить retry ID. Нельзя использовать
один ID для другого содержания. После смены машины можно восстановить свой
активный token из `history` и передать `--token`; не забирать чужую identity.

При API-only доступе использовать те же schema/reducer и exact-parent commit
операции через GitHub connector. Если нет возможности исполнить reducer и
проверить получившийся документ, разрешены чтение/status и handoff executor-у,
но не ручная имитация PASS. API endpoint updates с `force=true` запрещены.

## 9. Формальное испытание

Task: `BUS-SMOKE-001`. Candidate branch: `work/bus-smoke-001-r1`.
Единственный продуктовый файл: `docs/work/pilots/BUS-SMOKE-001/receipt.json`.
Его frozen содержимое (порядок ключей и whitespace несущественны):

```json
{
  "schema_version": 1,
  "task_id": "BUS-SMOKE-001",
  "message": "NanoLab distributed workflow smoke",
  "values": [1, 2, 3],
  "sum": 6,
  "scientific_claim": false
}
```

Проверка из tooling checkout:

```bash
python tools/task_bus.py smoke-check ../NanoLab-bus-smoke
```

Reviewer дополнительно проверяет отсутствие других изменений. Verifier в
fresh exact checkout запускает positive control и отдельно изменяет копию
`sum` на 7: checker обязан вернуть exit 2. Изменённая negative-control копия
не push-ится и не становится candidate.

Критерии живого опыта: один победитель claim; отдельные реальные сессии;
четыре role finish на одном subject; отсутствие передачи контекста через чат;
возобновление Director из Git; main неизменен; terminal COMPLETED_SANDBOX.

Unit/integration tests используют synthetic actors и временные bare remote
репозитории. Их PASS доказывает механические свойства транспорта/автомата,
но не заменяет живой multi-agent pilot и независимое review самой реализации.

## 10. Переход к работе по roadmap

После живого пилота — отдельный Work Order и independent review:

```text
P0  Mechanical tests + ready live pilot                  (this change)
P1  Real independent sessions complete BUS-SMOKE-001      (pending)
P2  Human-reviewed production policy + protected writer (pending)
P3  Roadmap -> Work Order adapters + acceptance observer (pending)
P4  Bounded launcher, identity proofs, cost/job budgets   (pending)
P5  Independent tasks / merge conflicts / scale campaign (pending)
```

Production task должен ссылаться на canonical roadmap task_id и exact base,
объявлять allowed/forbidden scope, dependencies, acceptance, resources,
stop conditions и права merge. Контроллер читает accepted dependency state из
main, а не считает sandbox completion научным acceptance. При main drift —
явное CONTINUE/REFRESH_REQUIRED. Для пересекающихся путей требуется дополнительное
планирование conflicts, для внешних side effects — executor idempotency.

Однофайловый log имеет лимит 2 MB и полное replay. Это осознанный low-volume
pilot. Для множества задач нужны сегментация, snapshots с проверяемой историей,
retention и отдельный performance test; заявлений о масштабировании здесь нет.

## Источники

- S1: Beads, официальный репозиторий: https://github.com/gastownhall/beads
- S2: MCP Agent Mail, официальный репозиторий: https://github.com/Dicklesworthstone/mcp_agent_mail
- S3: Gas Town, официальный репозиторий: https://github.com/gastownhall/gastown
- S4: GitHub Agentic Workflows / Safe Outputs: https://github.github.com/gh-aw/reference/safe-outputs/
- S5: Git push reference: https://git-scm.com/docs/git-push
- S6: GitHub Git References API: https://docs.github.com/en/rest/git/refs
- S7: Failed webhook deliveries: https://docs.github.com/en/webhooks/using-webhooks/handling-failed-webhook-deliveries
