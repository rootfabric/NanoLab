# EX-NATIVE-UBUNTU-EXECUTOR-R1 — Summary

```text
execution_id = EX-NATIVE-UBUNTU-EXECUTOR-R1
work_order   = WO-NATIVE-UBUNTU-EXECUTOR-R1
branch       = control/native-ubuntu-executor-r1
base         = d07e75e68c20599e4b942aefb20b4b3922985219 (origin/main)
substantive_head = 4dac9dc3f7c71e72de9622fe56cbbefcf402739d
substantive_tree = 013b55754a79124d66c2728e73d0b521031cd81f
status       = HANDOFF_READY (fresh Reviewer + fresh Verifier -> Human Gate)
risk/claim   = MEDIUM / C0_SOFTWARE_ONLY (control/infrastructure; НЕ научный WO)
```

## 1. Что сделано

1. `docs/work/WO-NATIVE-UBUNTU-EXECUTOR-R1.md` — WO: целевая архитектура
   (GitHub → U1 native Ubuntu AUTHOR/DEV/PRIMARY EXECUTOR; U2 = outenemy external
   REPRO/VERIFY; Windows = UI/historical evidence only), требования native
   (запрет WSL/VM//mnt/c), canonical paths, software policy, fresh oxDNA build R2
   (`00dc7fb9`, CPU/DOUBLE=ON/CUDA=OFF/MPI=OFF), migration gate без binary-sha
   equality с WSL, validation gates U1–U5, negative controls NC-U1..U5, raw
   evidence policy.
2. `docs/research/ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` — контракт среды R2,
   статус **WAITING_HOST**, процедура заморозки fingerprint по факту выделения U1.
3. `docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md` —
   `WINDOWS_WSL_EXECUTOR = HISTORICAL_ONLY` + `WINDOWS_ALLOWED_FOR_NEW_SCIENCE = NO`
   (EFFECTIVE 2026-09-27, owner decree); `DEFAULT_AUTHOR_EXECUTOR =
   NATIVE_UBUNTU_R2` PROPOSED с явными условиями активации; до активации научные
   execution-запросы = честный HARD_BLOCKED (resume: выделить U1), тихий fallback
   на Windows запрещён; process isolation (systemd units, CI ≠ lifecycle owner
   scientific jobs).
4. Поверхности: `AGENTS.md` (Executor environment policy), `AGENT_START.md`
   (Ubuntu-first), `HARNESS_AUTONOMOUS_EXECUTION_RU.md` (scientific execution вне
   Windows fallback-списка), `scheduler-policy.v1.json` (revision
   NL-N5-2026-09-27-R2 + executor_environment_policy), `docs/ROADMAP.md` (§4),
   `docs/work/WORK_QUEUE.md` (INFRA3-003), `docs/infra/ROADMAP.md` (INFRA3 =
   native Ubuntu reproducible scientific executor), `project/infra-plan.json`
   (INFRA3-003).

## 2. Чего НЕ сделано (честно)

- Машина U1 не выделена (owner, 2026-09-27). Все gates U1–U5 и NC-U1..U5 —
  **WAITING_HOST**; ни один PASS не декларируется. Fingerprint R2 не снимался.
- Никаких научных прогонов; научная история (включая `ENGINE_ENVIRONMENT_R1.md`,
  результаты NL5-002-E) не изменялась; NL5/NL6 границы не тронуты.
- Self-hosted runner не регистрировался (INFRA2-001 вне scope); secrets нет.

## 3. Валидация этой ветки

- `check-consistency` → ok:true; `workflow_lint` → blocking=0.
- `unittest`: 3 FAIL в `test_release_contract` — **pre-existing** на base
  `d07e75e` (воспроизведены на чистом worktree base): Windows CRLF-артефакт
  чекаута (autocrlf=true), на hosted CI ubuntu зелёные; вне diff этой ветки.
  Сам этот CRLF-класс проблем де-факто закрывается миграцией (autocrlf false на R2).
- `work_cli validate` EX-NATIVE-UBUNTU-EXECUTOR-R1 → без нарушений (checkpoint
  `INFRA3` против `^NL[0-8]$` — известный documented deviation class NOTE-1).

## 4. Открытые риски

- До выделения U1 научная execution-вертикаль не имеет canonical executor:
  любые новые scientific WO блокируются на «выделить U1» (честный HARD_BLOCKED).
- Policy-обновления поверхностей вступают в силу только после merge (Human Gate).

## 5. Errata / repair после review R1 (MINOR-1..MINOR-5, verdict PASS 7f25e8d)

- **MINOR-1**: поле `notes` удалено из `passport.json` (schema
  `additionalProperties: false`); содержимое перенесено в branch-passport §2.
- **MINOR-2**: устаревшая запись об отклонении checkpoint-паттерна исправлена:
  паттерн уже `^(NL[0-8]|INFRA[0-7])$` (расширен `EX-CTRL-LINTSCHEMA-R1`),
  отклонения не существует (branch-passport §2, авторитетная коррекция; event 0001
  не редактируется — append-only).
- **MINOR-3**: подтверждено, что `timestamp_utc` событий 0002–0004 — декларативные
  метки записи, смещённые относительно фактических commit-времён; события
  неизменяемы, факт фиксируется этой строкой (прецедент errata-via-summary).
- **MINOR-4**: уточнение записи event 0003: на машине reviewer'а test-suite даёт
  **6** base-идентичных FAIL (класс Windows-CRLF чекаута; включая
  test_release_manifest_candidate ×2, test_release_planning_refs ×1), а не 3;
  все воспроизводятся на чистом base `d07e75e` — вклад ветки 0.
- **MINOR-5**: `passport.status` переключён `IN_PROGRESS` → `HANDOFF_READY`.
- **NOTE-1/2/3** (символы U1/U2 машины vs gates; события 0002/0003 биндят START
  commit; пустой depends_on INFRA3-003) — приняты к сведению, исправления не
  требуют; символика машин уточнена: машина автора = U1 AUTHOR_UBUNTU, внешняя
  машина = U2 (outenemy), gates именуются U1–U5 по документу R2.

## 6. Next action (одно)

Выделить U1 (native Ubuntu, не WSL/VM), затем: freeze fingerprint
(`ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` §9) → gates U1–U5 → NC-U1..U5 →
fresh Reviewer/Verifier миграции → Human Gate → `DEFAULT_AUTHOR_EXECUTOR` ACTIVE.
