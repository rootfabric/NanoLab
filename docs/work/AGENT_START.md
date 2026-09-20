# Старт следующего агента

Это готовая инструкция для продолжения одной bounded задачи, а не разрешение выполнить всю дорожную карту за один заход.

> Ты работаешь в `rootfabric/NanoLab`. Цель проекта — открытая проверяемая AI-лаборатория нанокомпонентов; первый MVP — DNA Nanomechanics.
>
> 1. Прочитай `AGENTS.md`, `PROJECT_CONTROL.md`, `HARNESS_CONTROL.md`, `docs/control/*`, `project/state.json`, `project/plan.json`, `docs/ROADMAP.md`, `docs/work/WORK_QUEUE.md` и активный Work Order.
> 2. Проверь live `main`; не считай SHA из старого сообщения актуальным.
> 3. Запусти `CONTROL_DEVELOPMENT` в режимах consistency/overview/drive, если доступен локальный checkout. При connector-only работе выполни эквивалентное чтение machine contracts.
> 4. Создай bounded branch от exact `main`.
> 5. **До substantive work** создай `docs/work/executions/<execution-id>/passport.json`, `events/0001-work-order-started.json`, затем commit + non-force push. Это обязательный START checkpoint.
> 6. После смыслового этапа/batch/blocker/handoff добавляй append-only `CONTINUATION_CHECKPOINT` events и durable commits.
> 7. Если Work Order включает experiment campaign, следуй `docs/control/EXPERIMENT_HARNESS_RU.md`: preregistration и frozen subject должны быть в Git до запуска; каждый run имеет уникальный ID; terminal execution и scientific analysis фиксируются отдельно.
> 8. Перед завершением создай `summary.md` и `HANDOFF_COMPLETED` либо точный `WORK_ORDER_BLOCKED`; проверь `CONTROL_WORK close`. Не объявляй себя независимым Reviewer/Verifier.
> 9. Публикуй PR с evidence, exact HEAD/TREE, выполненными/невыполненными проверками и одним следующим действием.
>
> Если frontier — `NL5`, статус `NL5-002` — **WAITING_HUMAN (terminal verified MISMATCH / NOT accepted, canonical 2026-09-20)**: external reproduction дало 0b/32b MISMATCH, 11b/53b MATCH (Fresh Reviewer `be945f1` + Verifier `4116468`; evidence chain смержена PR #43 `7504b38`). НЕ перезапускать кампанию, не «чинить» пороги, не стартовать NL6-001/E5 (LOCKED до отдельного NL5 acceptance). Активный дочерний WO — `WO-NL5-002-E-R1` platform sensitivity: preregistration FROZEN (Reviewer `1f8c063` + Verifier `bd25baf` PASS, freeze record `PREREGISTRATION_FREEZE_R1`); dispatch = BLOCKED_ON_P1_AVAILABILITY (P1 = авторская WSL2-среда владельца; подмена P1 и P2-only paired run запрещены); 74b не запускать. Открытые owner-вопросы: NL5 acceptance policy после platform study, optional packaging v0.1.2, optional P3 (`docs/evidence/NL5-002/DIRECTOR_DECISION_R1.md`). NL5-001 принят: пакет 0.1.0 опубликован, лицензии закрыты (D2); v0.1.1 — bounded repair (science byte-identical).
>
> Если frontier всё ещё NL0 и NL0-001 не выполнен, выполни `docs/work/WO-NL0-001.md`: выбрать доступный reference E1 и candidate hinge E2, проверить фактические входы, первичные источники и ограничения. Не запускать дорогие simulations и не строить большой orchestrator до выбора входных данных.
>
> Если NL0-001 уже принят, не повторяй его: используй `project/state.json` и dependencies для следующего READY Work ID.

## Локальный старт

Linux/macOS:

```bash
git fetch origin --prune
git status --short
git rev-parse origin/main
./CONTROL_DEVELOPMENT.sh --check-consistency
./CONTROL_DEVELOPMENT.sh --overview
./CONTROL_DEVELOPMENT.sh --drive
```

Windows PowerShell:

```powershell
git fetch origin --prune
git status --short
git rev-parse origin/main
.\CONTROL_DEVELOPMENT.ps1 -CheckConsistency
.\CONTROL_DEVELOPMENT.ps1 -Overview
.\CONTROL_DEVELOPMENT.ps1 -Drive
```

При работе через GitHub connector выполнить эквивалентное чтение. Не выводить credentials и не считать отсутствие локального remote доказательством недоступности подключённого GitHub.
