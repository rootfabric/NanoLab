# Work Order WO-INFRA3-NL5-READINESS-R1 — Readiness package for native Ubuntu host U1 + frozen NL5 v0.2 campaign (DRY-RUN ONLY)

Статус: **IN_PROGRESS** (execution `EX-INFRA3-NL5-READINESS-R1`, ветка
`infra/infra3-nl5-readiness-r1`, base `513c4fa86470d939e9f9b7829e9c67c489c15a57`,
base tree `6d3a2132ae6ecdfed6269fe39697e8ac9bab152a`).
Родительский WO: `WO-NATIVE-UBUNTU-EXECUTOR-R1` / `WO-INFRA3-R2-ACTIVATION-R1`
(INFRA3-003). Track: `INFRA`. GitHub issue: #65 (родительская программа #63).
Risk: **MEDIUM**. Claim ceiling: **C0_SOFTWARE_ONLY**.

Это **не научный WO**: ни одного scientific run, ни одного запуска oxDNA, ни
одного исполнения gates U1–U5 / NC-U1..U5, ни одного инстанцирования runners,
никакой активации R2, никакого изменения frozen NL5 v0.2 acceptance criteria.
Результат — **machine-checkable DRY-RUN ONLY readiness package**.

## 1. Проблема

Канонический frozen пакет NL5 v0.2 (FROZEN_R2, F2 = `60da9a846511265a8ac7564da088c3d74cb073f0`)
и R2 activation tooling (`scripts/r2/*`, `config/infra/r2-activation.v1.json`)
опубликованы на `main` (PR #52, PR #47), U2-плечо технически готово (PR #55),
но машина U1 (AUTHOR_UBUNTU) **не выделена** — канонический факт
`docs/work/executions/EX-NL5-V02-FRESH-AUDIT-R1/evidence/u1-host-search-R1.json`
(AUTHOR_U1 = NOT_ASSIGNED; R2 = WAITING_HOST / NOT_ACTIVE). Между «пакет
заморожен» и «кампания может стартовать» лежит слой подготовки, который пока
существует только разрозненным текстом: требования к физической машине U1,
процедура заморозки fingerprint, машинные определения gates, ожидаемая
структура dispatch-кампании. Этот слой нужно зафиксировать как готовый,
проверяемый пакет **до** появления железа, чтобы активация после выделения U1
была механической (runbook `DIRECTOR_FRESH_AUDIT_R1.md` §6), а не импровизацией.

## 2. Цель

Произвести DRY-RUN ONLY readiness package:

```text
docs/infra/U1_PROVISIONING_CHECKLIST_R1.md      — проверяемые требования к
                                                  отдельной физической Ubuntu-машине
                                                  U1 (AUTHOR_UBUNTU): железо,
                                                  OS-пины, disk layout, сетевая
                                                  изоляция, процедура fingerprint
                                                  (точные команды), oxDNA build
                                                  provenance, зависимости,
                                                  SSH/CI-изоляция, systemd
                                                  survival, доказательство
                                                  U1 != U2 != Windows/WSL2
docs/infra/NL5_V02_DRYRUN_MANIFEST_R1.json      — machine-readable DRY-RUN
                                                  манифест-скелет frozen-кампании
                                                  NL5 v0.2: campaign id, frozen
                                                  protocol ref (path + sha256),
                                                  схема id расчётов, engine pin,
                                                  placeholders входных digests,
                                                  attempt/stop-семантика, сплит
                                                  U1/U2, бюджеты, gates U1–U5 и
                                                  NC-U1..U5 как machine-checkable
                                                  записи (id, описание, команда/
                                                  артефакт, pass-условие,
                                                  честный статус)
docs/infra/INFRA3_NL5_READINESS_REPORT_R1.md    — компактный отчёт готовности:
                                                  состояние по каждому gate,
                                                  декларация HOST_NOT_ASSIGNED,
                                                  точный список человеческих
                                                  действий для активации U1,
                                                  что остаётся запрещённым до
                                                  Human Gate
tests/test_infra3_nl5_readiness.py              — offline unittest: JSON парсится,
                                                  id уникальны, записи gates
                                                  полны, числа кампании = каноническим
                                                  frozen-числам (296/56/352),
                                                  ни один scientific run не
                                                  триггерится, статусы честные
```

Канонические числа кампании подтверждаются из frozen-протокола
`docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md` (sha256
`2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d`, §7/§10.2/§11):
`confirmatory_runs = 296 = 2·(64+64+10+10)`, replacement cap `56`, `max_runs = 352`,
`wall_hours_per_platform = 560`. Числа из mission-текста не принимались на веру —
сверены с каноническим протоколом и authoritative contract JSON.

## 3. Вне scope (запрещено этим WO)

- Любые scientific runs; любые запуски oxDNA/MD/E5; any physics; инстанцирование
  runners; научное исполнение gates U1–U5 / NC-U1..U5.
- Изменение frozen NL5 v0.2 acceptance criteria или protocol files
  (`docs/research/NANOLAB_REPRO_V0_2_FROZEN_R*.md`, authoritative contract,
  seed record, `docs/evidence/NL5-V02-FREEZE/**`, `releases/**`).
- Изменение `project/state.json`, `project/infra-state.json`, `project/plan.json`.
- Регистрация runners/credentials; платный compute; новый LAN-скан
  (U1 host search уже опубликован fresh audit'ом).
- Назначение U1; предложение outenemy как author-исполнителя (outenemy =
  EXTERNAL_U2_ONLY, никогда U1); новые scientific runs на Windows/WSL2
  (запрещены owner decree 2026-09-27).
- Прямой push в `main`, force-push, правка чужих worktree/веток.

## 4. Allowed paths

```text
docs/work/WO-INFRA3-NL5-READINESS-R1.md
docs/infra/U1_PROVISIONING_CHECKLIST_R1.md
docs/infra/NL5_V02_DRYRUN_MANIFEST_R1.json
docs/infra/INFRA3_NL5_READINESS_REPORT_R1.md
tests/test_infra3_nl5_readiness.py
docs/work/executions/EX-INFRA3-NL5-READINESS-R1/**
docs/work/WORK_QUEUE.md            (только одна append-строка этого WO)
```

Чтение/импорт `scripts/r2/*`, `scripts/nl5/*`, frozen-артефактов разрешён и
необходим (reconciliation + диджесты); их **модификация** запрещена.

## 5. Required outputs

1. Deliverables §2 с честными статусами (`HOST_NOT_ASSIGNED` / `NOT_MET` — без
   единого PASS, машина U1 не существует).
2. Execution `EX-INFRA3-NL5-READINESS-R1`: passport, append-only events
   (START → CONTINUATION → VALIDATION → HANDOFF), evidence-map, summary
   с exact HEAD/TREE и выводами команд.
3. Surface sync: одна строка в `docs/work/WORK_QUEUE.md`.
4. Валидация: `python3 -m unittest discover -s tests -t .`;
   `PYTHONPATH=scripts python3 -m harness.cli check-consistency`;
   `PYTHONPATH=scripts python3 -m harness.workflow_lint`;
   `PYTHONPATH=scripts python3 -m harness.work_cli validate
   docs/work/executions/EX-INFRA3-NL5-READINESS-R1` — всё зелёное.
5. Fresh Reviewer + fresh Verifier на exact HEAD; merge = Human Gate.

## 6. Budget

Локальный CPU (документы, JSON, unittest) на dev-хосте; 0 scientific runs;
0 платных сервисов; сеть только `git push origin` ветки. Ограничение claim:
пакет доказывает **готовность** (READY_FOR_HOST), не готовность исполнителя.

## 7. Честные границы результата

Ожидаемый класс исхода — **READY_FOR_HOST**: пакет полный, но машина U1 не
выделена, все gates/NC остаются неисполненными (`HOST_NOT_ASSIGNED`), R2 =
WAITING_HOST / NOT_ACTIVE, `NEW_SCIENCE` = HARD_BLOCKED, dispatch кампании NL5
v0.2 = BLOCKED (frozen chain требует R/V/A + Human Gate). Ничто в этом пакете
не повышает scientific claim и не приближает `NL*` checkpoint.
