# EX-INFRA3-NL5-READINESS-R1 — Summary (handoff)

Work Order: `WO-INFRA3-NL5-READINESS-R1` (GitHub issue #65, parent program #63)
Branch: `infra/infra3-nl5-readiness-r1` (worktree `/home/rdpuser/NanoLab/infra3-nl5-readiness`)
Track: INFRA (INFRA3-003 line). Risk MEDIUM. Claim ceiling: **C0_SOFTWARE_ONLY**.
Execution class: **DRY-RUN ONLY** — 0 scientific runs за всю execution.

## 1. Exact subjects

```text
base (canonical main, PR #57 merge)  = 513c4fa86470d939e9f9b7829e9c67c489c15a57
base tree                            = 6d3a2132ae6ecdfed6269fe39697e8ac9bab152a
implementation subject HEAD          = d8842c2f51870cbf3adf5eae28078ff9d996aa31
implementation subject tree          = 2b49d54ff8c122ef5112442a75afe57dd56ca7e2
terminal packaging commit            = добавляет events/0002..0004, evidence-map.json,
                                       summary.md поверх implementation subject
                                       (sha этого commit невозможно включить в
                                       него сам; см. git log ветки после push)
START commit                         = b5356044fd1c2656888d2fece99dfa2ad128569d
```

События 0002–0004 ссылаются на implementation subject `d8842c2f…` (прецедент
`EX-INFRA3-NATIVE-UBUNTU-R2-R1`: события ссылаются на implementation-состояние,
терминальный packaging-commit добавляет сам execution-пакет).

## 2. Deliverables (все — documentation/tooling, C0)

| Path | sha256 |
|---|---|
| `docs/work/WO-INFRA3-NL5-READINESS-R1.md` | `888a5db39013023145b14f802c7629a85c84b99f01cc8fff2704344e6b5e550d` |
| `docs/infra/U1_PROVISIONING_CHECKLIST_R1.md` | `c86deb681cac9a7fca71a07c265e0f47a0da4d4362c178983d0b867c7b51c2bc` |
| `docs/infra/NL5_V02_DRYRUN_MANIFEST_R1.json` | `4b4f1d0d249964be33f9c917d97e04efb7fb261feb931361da551a18efc2353d` |
| `docs/infra/INFRA3_NL5_READINESS_REPORT_R1.md` | `a45804b1d2a4f45d516e4328787a0043d0cfe7054d11d70e4f6008cac7a1f1cf` |
| `tests/test_infra3_nl5_readiness.py` | `826584ac602e69bec68a22255af6be078b2f03e74e39baffdaa31feacc431096` |

## 3. Команды и результаты (dev-хост, offline; 0 scientific runs)

```text
$ python3 -m unittest discover -s tests -t .
Ran 709 tests in 58.376s
OK                                  # включает 30 новых тестов tests/test_infra3_nl5_readiness.py

$ PYTHONPATH=scripts python3 -m harness.cli check-consistency
ok: no warnings; frontier NL5; next_work_order NL5-002;
head d8842c2f51870cbf3adf5eae28078ff9d996aa31;
tree 2b49d54ff8c122ef5112442a75afe57dd56ca7e2

$ PYTHONPATH=scripts python3 -m harness.workflow_lint
workflows 1; violations 0; blocking 0

$ PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-INFRA3-NL5-READINESS-R1
ok=true; errors=[]; profile=standard_work_order;
event_types=[WORK_ORDER_STARTED, CONTINUATION_CHECKPOINT, VALIDATION_RECORDED, HANDOFF_COMPLETED];
has_terminal_handoff=true; has_post_terminal_corrections=false
(passport_sha256 на момент прогона: 054fa889d565a61ff4841e1bb835c4d0292896b61b5fc9e61a99f6b1625da859)
```

## 4. Ключевые факты (verified, не заявленные)

- **Frozen-кампания NL5 v0.2**: числа взяты из канонического frozen-протокола
  `docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md` — sha256 на диске
  `2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d`,
  совпадает с пинами Director FREEZE R2 (`DIRECTOR_FREEZE_R2.json`:
  subject_head `60da9a846511265a8ac7564da088c3d74cb073f0`, subject_tree
  `e565c8a6cee9e829fac14008ebc9c2ea1609931d`, protocol/contract/seed-record
  sha256 пины). Подтверждённые числа: **confirmatory 296** = 2·(64+64+10+10),
  **replacement cap 56**, **max 352**, wall ≤ 560 ч/платформу, N_min 52/8,
  SELECTED_N = 64, 74b запрещён. Числа из mission-текста не принимались на
  веру — сверены (§7/§10/§11 протокола).
- **Reconciliation**: все infra-ветки линии (PR #45/#46/#47/#52/#53/#55/#56) —
  merged предки canonical main на этом base (`git merge-base --is-ancestor`);
  «review-verified, но не merged» infra-фактов не осталось. Чего не существует
  нигде: U1, PASS любого gate, R2 ACTIVE, Reviewer(F)/Verifier(F)/authority(A).
- **HOST_NOT_ASSIGNED**: канонический факт `u1-host-search-R1.json` (PR #53)
  + отсутствие любого allocation record; outenemy = EXTERNAL_U2_ONLY
  (`config/infra/r2-activation.v1.json` forbidden_hostnames) — как author
  executor никогда не предлагается.

## 5. Evidence paths

```text
docs/work/executions/EX-INFRA3-NL5-READINESS-R1/passport.json
docs/work/executions/EX-INFRA3-NL5-READINESS-R1/events/0001..0004
docs/work/executions/EX-INFRA3-NL5-READINESS-R1/evidence-map.json
docs/infra/U1_PROVISIONING_CHECKLIST_R1.md
docs/infra/NL5_V02_DRYRUN_MANIFEST_R1.json
docs/infra/INFRA3_NL5_READINESS_REPORT_R1.md
tests/test_infra3_nl5_readiness.py
docs/work/WORK_QUEUE.md  (одна append-only строка WO-INFRA3-NL5-READINESS-R1)
```

## 6. Границы (не изменены)

Frozen NL5 v0.2 артефакты не тронуты (диджесты перепроверены тестами);
`project/state.json`, `project/infra-state.json`, `project/plan.json` не
менялись; runners/credentials/secrets не создавались; платный compute = 0;
научных запусков = 0; Windows/WSL2 не использовался. Статусы: `NL5 =
IN_PROGRESS`, `NL6-001 = LOCKED`, `external_reproductions = 0`, `R2 =
WAITING_HOST / NOT_ACTIVE`, `AUTHOR_U1 = NOT_ASSIGNED`, `NEW_SCIENCE =
HARD_BLOCKED`, `dispatch = BLOCKED`, `machine_launch_authorized = false`.

## 7. Open risks

1. U1 не выделена — единственный hard blocker; пакет честно класса
   READY_FOR_HOST, не READY_FOR_EXECUTION.
2. Hardware floor чек-листа (§1) выведен из U2 raw-capacity прецедента
   (~15 ГБ/нога) и подлежит перепроверке по фактическому fingerprint U1.

## 8. Next action (один)

Fresh independent Reviewer + fresh exact-head Verifier этой ветки на exact
HEAD/TREE, затем Human Gate (merge). После merge следующая INFRA-стадия
стартует от свежего canonical main.
