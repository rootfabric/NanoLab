# NanoLab — Agent Router

Канонический репозиторий `rootfabric/NanoLab`; scientific truth и принятая policy — свежий `main`. Рабочие ветки публикуют execution facts, не self-acceptance.

## Начало обычной задачи

Прочитать `PROJECT_CONTROL.md`, `HARNESS_CONTROL.md`, `project/state.json`, `project/plan.json`, текущий Work Order и ближайшие scoped инструкции. Для risk routing и исправлений применять `docs/control/FLOW_THROUGHPUT_R1.md` (после её canonical merge она имеет приоритет над старым общим требованием повторять все роли после каждого коммита). Команда:

```bash
PYTHONPATH=scripts python3 -m harness.cli drive --root .
```

`project/operations/*.json` и `docs/work/CURRENT_QUEUE.md` — актуальные C0 задачи. Исторические roadmap/WORK_QUEUE сохранены отдельно и не являются dispatch. WAITING_HUMAN/BLOCKED нельзя трактовать как разрешение запуска; доступные C0 PREP работы показаны параллельно.

Назначен центральным агентом / Director / интегратором — дополнительно читать `DIRECTOR.md`. Не имитировать независимые роли одной сессией. Task Bus применяется только к явно назначенной bus-работе; до его P1.1–P1.4 gates production P2 запрещён. COMPLETED_SANDBOX не ACCEPTED, actor_id не доказательство отдельного executor.

## Дополнительное чтение по риску

Scientific protocol/run/model/analysis/inputs/claim: `docs/SCIENTIFIC_METHOD.md`, `docs/control/EXPERIMENT_HARNESS_RU.md`, `HARNESS_REVIEW_AND_EVIDENCE_RU.md`, паспорт эксперимента, frozen protocol/authority и source provenance. Scientific gates не сокращаются административной policy.

CI/runner/storage/compute: `docs/infra/SECURITY_MODEL.md`, `EXECUTION_BACKENDS.md`, `ROADMAP.md`, `project/infra-plan.json`, `project/infra-state.json`. INFRA предоставляет capability, не scientific truth.

Полный development/branching протокол: `docs/control/DEVELOPMENT_HARNESS_RU.md`, `HARNESS_AUTONOMOUS_EXECUTION_RU.md`, `BRANCHING_AND_GIT_RU.md`. Machine contracts: `config/control/harness/`.

## Work protocol

1. Проверить fresh main и exact base, создать scoped branch/worktree.
2. До substantive change сохранить Work Order, execution passport и WORK_ORDER_STARTED; commit + non-force push.
3. Работать только в scope/budget. После содержательного этапа, blocker или handoff — durable checkpoint, не commit на каждую строку.
4. Для новых C0 records использовать `harness.work_cli start|record|finish|correct` (примеры `docs/work/FLOW_R1_COMMANDS.md`). Sequence-v1 допускает одинаковые реальные UTC timestamps; искусственные миллисекунды не нужны. Старые/научные records не мигрировать.
5. LOW administrative-only — автоматическая проверка + существующий Human merge gate. Ordinary MEDIUM tooling — один независимый Reviewer, включающий механическую проверку, + CI. HIGH protocol/inputs/topology/analysis/claim/authority/security — отдельные Reviewer и Verifier + Director. CRITICAL — дополнительно Human/domain gate. C0 и Markdown не означают низкий риск.
6. Чужой repair может проверить тот же независимый Reviewer/Verifier. Publication-only commit требует доказанной неизменности product/input subject и delta review текста, а не нового полного цикла. Неясное влияние — полный/affected путь. Этот FLOW-R1 пакет сам проходит HIGH review, не self-accepts.
7. Перед handoff: exact subject HEAD/TREE, команды/результаты, evidence, оставшиеся риски и одно next action. Отрицательные/failed/inconclusive результаты сохранять. Исторические events не редактировать; corrections добавляются.
8. Merge main остаётся Human Gate, если явное scoped разрешение уже не выдано; его условия должны фактически выполниться. Разрешение на implementation не является независимым acceptance.

## Неизменные scientific правила

Exit code 0 не scientific PASS. Claim не выше evidence. До кампании freeze protocol/code/model/inputs/digests, observables/statistics/exclusions/budget/stop conditions. Run ID уникален; failed ID не использовать заново. Raw reuse требует digest и provenance; raw вне Git допустим с manifest sha256/size/producer/subject/location. Не менять threshold/N/seeds после просмотра результата без новой protocol revision. Технический outcome и научный conclusion разделяются. Никаких фиктивных source models или SOURCE_VERIFIED из библиографии.

## Исполнители и безопасность

WINDOWS_WSL_EXECUTOR=HISTORICAL_ONLY (owner decree 2026-09-27); Windows/WSL не для новых scientific runs, кроме explicit bounded environment-comparison WO. Author — отдельный native Ubuntu U1; outenemy — независимый EXTERNAL_U2, не author/dev host. До frozen fingerprint + U1–U5/NC-U1..U5 + review/verify/Human Gate R2 science остаётся WAITING_HOST. См. `docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md`, `docs/research/ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md`, `docs/work/WO-NATIVE-UBUNTU-EXECUTOR-R1.md`. Новые owner minima U1 не отменяются.

Public PR выполняется только на ephemeral hosted route, никогда автоматически на trusted self-hosted scientific node. Никаких секретов, глобальных установок/изменений узлов или paid compute сверх разрешённого scope/budget. Wet-lab/hardware — CRITICAL с отдельным human/domain gate. READY карточка не запускает worker.

## Git и язык

Внутри Work Order разрешены scoped branch/worktree, stage, commit, non-force push, draft PR, evidence publication и review request. Запрещены direct push main, force/history rewrite, destructive remote deletion и неразрешённое расширение полномочий. Git — durable memory, не чат. Документы/отчёты — русский, identifiers/schemas/events и Conventional Commit types — английский.
