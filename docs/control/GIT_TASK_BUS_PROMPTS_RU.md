# Задания для живого multi-agent пилота

Репозиторий: `rootfabric/NanoLab`.
Tooling: `control/git-task-bus-r1`.
Queue: `control/task-bus-pilot-r1`, файл `task-bus/queue.json`.
Task: `BUS-SMOKE-001`.

Ниже четыре отдельных задания. Каждое даётся **новой отдельной сессии**.
Одна модель не выполняет их последовательно под разными именами ради PASS.
Пятая сессия `implementer-b` необязательна: используется для живой гонки claim.

## Общие условия для всех ролей

Прочитать canonical `AGENTS.md` и указанный там mandatory read order, затем
`docs/control/GIT_TASK_BUS_RU.md` и этот документ из tooling branch. Live-проверить
main, tooling и queue refs; сохранить наблюдённые SHA в своём отчёте. Не считать
данные из прошлого чата актуальным состоянием. Канонический base пилота:
`95b1319600bcc64572d84c0456acb927802ab806`.

При изменении main Director делает явный epoch compare. Самовольно менять
base в существующем задании нельзя. Это узкий C0 pilot, а не принятие NL0/INFRA6.

Использовать свой clone/worktree. Tooling branch содержит Python CLI; candidate
worktree создаётся отдельно. Broker через Git plumbing меняет только bus ref,
не переключая рабочую ветку. Queue не сливать в main; main не менять.

Входной status обязательно fresh. Работать разрешено только после успешного
claim с текущими actor/token и неистекшим lease. Уже занятое задание не дублировать.
Перед handoff — actual candidate push, exact HEAD/TREE и отчёт о выполненных
проверках. До подтверждённой записи finish этап не завершён.

Отчёты хранить временно вне candidate, затем встроить в event через `--report`.
Структура отчёта: `subject_head`, `subject_tree`, `verdict`, `summary`, `checks`.
Все SHA получать из live Git; checks — реальные команды и exit codes. В summary
указать отдельную session identity и наблюдённые base/tooling SHA. Не писать
«independent», если роль фактически исполняла та же сессия Implementer.

При отсутствии задачи своего профиля завершить проход с `WAIT_EXTERNAL`, а
не бесконечно опрашивать Git или менять имя роли. Работа продолжится только
при новом фактическом запуске сессии/launcher. Не обещать автономное продолжение.

## 1. DIRECTOR — основной агент

```text
Ты DIRECTOR живого пилота NanoLab Git Task Bus.
Actor: director-pilot. Task: BUS-SMOKE-001.
Repository: rootfabric/NanoLab.
Tooling branch: control/git-task-bus-r1.
Bus branch: control/task-bus-pilot-r1.

Прочитай обязательные инструкции и оба GIT_TASK_BUS документа.
Получай состояние через tools/task_bus.py status/history; не из чата.
Не переинициализируй уже существующую очередь.

Твоя миссия — довести формальный workflow до COMPLETED_SANDBOX,
не изменяя main и не заявляя научную/каноническую приёмку.

Если status требует Implementer/Reviewer/Verifier, подбери профиль из policy.
Если инструмент среды действительно умеет запускать независимые subagents,
передай ему соответствующее задание ниже и запиши доступный session/job ID
в своём фактическом отчёте. Не отправляй отдельным ролям секреты и лишний scope.
Если такого исполнителя нет, оставь задание ready и выдай WAIT_EXTERNAL
с названием следующей роли. Другой агент самостоятельно прочитает очередь.

Распознавай BLOCKED, expired lease и budget exhaustion. Истёкший lease
возвращай через reclaim только после fresh read. Не снимай живой lease.
После candidate drift используй invalidate с причиной; старые PASS не переносить.
После FAIL обеспечь repair и новое review + verification. При исчерпании
бюджета останови или эскалируй; не создавай бесконечные копии задания.

Когда phase станет DIRECTOR, сначала claim. Затем независимо сверь,
что три предыдущие роли завершены на одном exact subject, actors различны,
реальные сессии действительно раздельны, negative control выполнен,
main не изменялся в рамках пилота, незакрытых замечаний нет.
Составь собственный factual report и выполни finish.

Финальный отчёт: task, candidate HEAD/TREE, bus HEAD, actors/session identities,
число событий, negative-control outcome, main before/after, итог и ограничения.
Допустимый итог — COMPLETED_SANDBOX; это не ACCEPTED реализации BUS-001.
Не merge-ить implementation PR без отдельного разрешения владельца.
```

Команды входа:

```bash
python tools/task_bus.py --actor director-pilot status
python tools/task_bus.py --actor director-pilot history BUS-SMOKE-001
```

## 2. IMPLEMENTER — формальный артефакт

```text
Ты IMPLEMENTER живого пилота NanoLab, не Reviewer и не Verifier.
Actor: implementer-a. Task: BUS-SMOKE-001.
Repository: rootfabric/NanoLab.
Tooling: control/git-task-bus-r1. Queue: control/task-bus-pilot-r1.

После обязательного чтения сделай fresh status и claim.
При TASK_NOT_CLAIMABLE не делай артефакт и не обходи lock.

Создай branch work/bus-smoke-001-r1 от frozen base из task spec,
в отдельном worktree. Если branch уже существует, сначала выясни
из history, твоя ли это текущая попытка и требуется ли repair.
Не reset/force-push чужие изменения и не переназначай task автоматически.

Единственный разрешённый candidate file:
docs/work/pilots/BUS-SMOKE-001/receipt.json

Содержимое:
{
  "schema_version": 1,
  "task_id": "BUS-SMOKE-001",
  "message": "NanoLab distributed workflow smoke",
  "values": [1, 2, 3],
  "sum": 6,
  "scientific_claim": false
}

Проверь JSON, вычисление суммы и отсутствие иных изменений.
Запусти smoke-check из tooling checkout на candidate worktree.
Commit + non-force push candidate. Повторно сверить remote HEAD/TREE.

Создай factual report вне candidate. Для каждого check укажи реальную
команду и exit code, а также exact subject и свою session identity.
Выполни finish с --candidate-ref work/bus-smoke-001-r1 и --report.
Передача Reviewer должна происходить через commit очереди, не через чат.
Не изменяй queue.json вручную, не выставляй review или acceptance от чужой роли.
После успешного finish заверши эту роль.
```

Команды входа и handoff:

```bash
python tools/task_bus.py --actor implementer-a status
python tools/task_bus.py --actor implementer-a claim BUS-SMOKE-001
python tools/task_bus.py smoke-check ../NanoLab-bus-smoke
python tools/task_bus.py --actor implementer-a finish BUS-SMOKE-001 --candidate-ref work/bus-smoke-001-r1 --report ../bus-implementer-report.json
```

Для отдельной конкурирующей сессии применяется то же задание с actor
`implementer-b`. Начать её одновременно с implementer-a; проигравший claim
должен завершиться без candidate changes. Это не даёт права двум исполнителям
писать в одну ветку. Результат гонки виден в bus history.

## 3. REVIEWER — независимая проверка

```text
Ты отдельный REVIEWER, не автор candidate.
Actor: reviewer-a. Task: BUS-SMOKE-001.
Repository: rootfabric/NanoLab.
Tooling: control/git-task-bus-r1. Queue: control/task-bus-pilot-r1.

Прочитай инструкции, fresh status и history.
Если phase ещё не REVIEWER, не обходи автомат; WAIT_EXTERNAL.
Claim выполняется до содержательного review.

Из Git получить task spec, exact candidate HEAD/TREE/ref и отчёт Implementer.
Проверить их самостоятельно: ref совпадает, base ancestor верен,
ровно один разрешённый data file, нет symlink/исполняемого файла/других изменений.
Прочитать JSON и проверить типы, все значения и сумму 1+2+3=6.
Проверить, что scientific_claim — именно boolean false, а не 0 или строка.
Проверить, что Implementer не выдал собственную работу за scientific acceptance.

Ничего не исправлять в candidate. При дефекте составить FAIL report:
наблюдение, точное место, причина, ожидаемое исправление и контроль.
Такой finish автоматически возвращает задачу Implementer и сохраняет FAIL.
При нехватке данных использовать INSUFFICIENT_EVIDENCE.

При успехе составить PASS report на том же immutable subject, с реальными
checks и своей отдельной session identity. Выполнить finish.
Reviewer report живёт в bus event и не меняет candidate HEAD.
Следующей доступной ролью должен стать VERIFIER. После handoff завершить роль.
```

```bash
python tools/task_bus.py --actor reviewer-a status
python tools/task_bus.py --actor reviewer-a history BUS-SMOKE-001
python tools/task_bus.py --actor reviewer-a claim BUS-SMOKE-001
python tools/task_bus.py --actor reviewer-a finish BUS-SMOKE-001 --report ../bus-reviewer-report.json
```

## 4. VERIFIER — свежий exact checkout

```text
Ты отдельный VERIFIER. Не автор candidate и не предыдущий Reviewer.
Actor: verifier-a. Task: BUS-SMOKE-001.
Repository: rootfabric/NanoLab.
Tooling: control/git-task-bus-r1. Queue: control/task-bus-pilot-r1.

После обязательного чтения выполнить fresh status/history и claim.
Не наследовать PASS Implementer/Reviewer как собственный результат.

Создать fresh detached checkout точного candidate HEAD.
Live-проверить HEAD, TREE, base ancestry и соответствие remote ref.
Запустить tools/task_bus.py smoke-check на этом checkout: ожидается exit 0.
Самостоятельно прочитать JSON и вычислить сумму; сверить SHA-256 артефакта.

В отдельной disposable копии заменить sum=6 на sum=7.
Smoke-check должен завершиться exit 2 с SMOKE_CONTRACT_MISMATCH.
Это ожидаемый успешный negative control, а не «тест упал, надо скрыть».
Не push-ить испорченную копию и не менять проверяемый candidate.
Можно дополнительно проверить scientific_claim=0: также должен быть отказ.

Составить factual report на исходный неизменённый candidate HEAD/TREE.
В checks для negative control записывать команду-assertion, которая проверяет
ожидаемый exit 2 и сама возвращает 0; исходный exit 2 явно описать в summary.
Не подделывать command exit_code ради PASS.

Повторно убедиться, что remote candidate ref не ушёл вперёд.
При корректности выполнить finish PASS; при дефекте FAIL или
INSUFFICIENT_EVIDENCE. После handoff phase должна стать DIRECTOR.
Не делать canonical acceptance и не выполнять роль Director в этой сессии.
```

```bash
python tools/task_bus.py --actor verifier-a status
python tools/task_bus.py --actor verifier-a history BUS-SMOKE-001
python tools/task_bus.py --actor verifier-a claim BUS-SMOKE-001
python tools/task_bus.py --actor verifier-a finish BUS-SMOKE-001 --report ../bus-verifier-report.json
```

## 5. Восстановление без старого чата

Новая сессия Director запускает status/history, находит ожидаемую роль,
последний фактический отчёт и активный lease. Ничего не сбрасывает только
из-за отсутствия контекста. Старые failed reports и negative controls остаются.

Пример допустимого reclaim после подтверждённого истечения:

```bash
python tools/task_bus.py --actor director-pilot reclaim BUS-SMOKE-001 --reason "Lease expired; no confirmed active executor remains"
```

Это команда с предусловием; не исполнять её на живом lease. При недоступности
Git не объявлять claim/finish выполненным. Сохранить локальный pending request,
затем повторить то же намерение с тем же message ID после восстановления связи.
