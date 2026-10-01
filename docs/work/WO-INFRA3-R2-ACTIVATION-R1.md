# Work Order WO-INFRA3-R2-ACTIVATION-R1 — R2 activation tooling (готовность к mechanical activation)

Статус: **IN_PROGRESS** (execution `EX-INFRA3-NATIVE-UBUNTU-R2-R1`, ветка
`infra/infra3-native-ubuntu-r2-activation-r1`, base `8205781def7179d6bdfa6eb7ab2a84d46776649c`).
Родительский WO: `WO-NATIVE-UBUNTU-EXECUTOR-R1` (INFRA3-003). Track: `INFRA`.
Risk: **MEDIUM**. Claim ceiling: **C0_SOFTWARE_ONLY**. Это **не научный WO**:
никаких scientific runs, никаких PASS по gates U1–U5 / NC-U1..U5, никакой
активации R2.

Дата открытия: 2026-09-30. Trigger: central-agent mission 2026-09-30 (§3–§5, §11–§15)
— машина U1 по-прежнему не выделена (`AUTHOR_U1 = NOT_ASSIGNED`,
`R2_STATUS = WAITING_HOST / NOT_ACTIVE`); до её появления разрешена и требуется
подготовка activation tooling, чтобы последующая активация R2 после выделения U1
была механической и не требовала импровизации на живом хосте.

## 1. Проблема

Контракт среды R2 и policy зафиксированы (`ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md`,
`NATIVE_UBUNTU_EXECUTION_POLICY_R1.md`), но вся процедура активации (fingerprint →
build → gates U1–U5 → NC-U1..U5 → raw manifest → activation decision) существует
только как текст. Исполнять её вручную на freshly-provisioned хосте — источник
ошибок класса того самого инцидента, который миграция исключает (ручные
SSH-сессии, CI-зависимые jobs, retry-штормы). Нужен исполняемый, тестируемый
tooling, который на U1 прогоняет процедуру как есть, а вне U1 честно отказывается.

## 2. Цель

Реализовать в репозитории bounded, детерминированный R2 activation tooling:

```text
scripts/r2/*            — fingerprint + native-eligibility, run contract,
                          executor (direct/systemd launcher), supervisor
                          (transient units + survival checks), gates
                          U1–U5, negative controls NC-U1..U5, activation
                          decision machine
config/infra/r2-activation.v1.json — machine-readable pins/policy (engine pin,
                          flags, canonical paths, honest statuses)
tests/test_r2_activation_tooling.py — unit-тесты всей логики (без systemd,
                          без сети, без сборки oxDNA — fake runners/tmp dirs)
```

Ключевые machine-инварианты, которые tooling обязан enforcing'ить (не доверять
оператору на память):

1. **Host gate**: fingerprint-валидатор признаёт хост U1-eligible только при
   native Linux (virt=none, без Microsoft-kernel маркера), native ФС
   (ext4/xfs/btrfs), доступном systemd и `hostname` НЕ из списка запрещённых
   (`outenemy` — EXTERNAL_U2_ONLY, никогда author). Все исполняющие subcommands
   (`build-engine`, `gate`, `nc`, scientific-run paths) отказывают на
   не-eligible хосте (exit 2, `BLOCKED_HOST`), без silent fallback.
2. **Run contract**: execution_id / run_base / attempt; attempt id = `<run_base>`
   либо `<run_base>-R<n>`; append-only ledger с защитой от переиспользования
   attempt id (включая после FAILED_TECHNICAL); technical outcome
   (`COMPLETED | FAILED_TECHNICAL | ABORTED | BLOCKED_ENVIRONMENT`) отделён от
   scientific outcome (`NOT_EVALUATED` в этом tooling всегда).
3. **Raw evidence**: каждый run получает `~/nanolab/raw/<execution-id>/<attempt-id>/`
   (stdout/stderr/exit) + artifact manifest (path, sha256, size, producer,
   retention) + digest манифеста в ledger. Git хранит только compact evidence.
4. **Gates**: U1–U5 и NC-U1..U5 — машина состояний `WAITING_HOST → PASS | FAIL`;
   `PASS` записывается только при непустом evidence-ref на существующий файл.
5. **Activation decision**: `R2_ACTIVATED = YES` вычислим ТОЛЬКО при
   (все gates PASS) ∧ (все NC PASS) ∧ (frozen native-eligible fingerprint) ∧
   (fresh review PASS) ∧ (fresh verify VERIFIED) ∧ (human_gate_approved = true);
   иначе — `WAITING_HOST / NOT_ACTIVE` со списком причин. Policy-инвариант
   зашит кодом, а не соглашением.

## 3. Вне scope (запрещено этим WO)

- Любые scientific runs; любые запуски oxDNA; any physics.
- Фактическое исполнение gates U1–U5 / NC-U1..U5 (машина U1 не выделена —
  статусы остаются `WAITING_HOST`).
- Регистрация self-hosted runner (INFRA2-001); secrets; платный compute.
- Изменения `project/state.json`, `project/infra-state.json`, scientific
  history, `ENGINE_ENVIRONMENT_R1.md`, существующих execution-каталогов.
- Объявление `R2_STATUS` ≠ `WAITING_HOST / NOT_ACTIVE` в любых canonical
  surfaces; назначение AUTHOR_U1; изменение роли outenemy.

## 4. Allowed paths

```text
docs/work/WO-INFRA3-R2-ACTIVATION-R1.md
docs/work/executions/EX-INFRA3-NATIVE-UBUNTU-R2-R1/**
scripts/r2/**
tests/test_r2_activation_tooling.py
config/infra/r2-activation.v1.json
docs/work/WORK_QUEUE.md            (только строка INFRA3-003 — surface sync)
project/infra-plan.json            (только note задачи INFRA3-003)
docs/infra/ROADMAP.md              (только уточнение статуса INFRA3-003, если нужно)
```

## 5. Required outputs

1. Tooling + config + tests (см. §2) с зелёным прогоном на dev-хосте
   (outenemy, как C0 dev environment — разрешено: это НЕ scientific execution).
2. Execution `EX-INFRA3-NATIVE-UBUNTU-R2-R1`: passport, events
   (START → CONTINUATION → VALIDATION → HANDOFF), branch-passport, summary —
   честные статусы, exact HEAD/TREE.
3. Surface sync WORK_QUEUE/infra-plan (одна строка/примечание, без смены
   статусов границ).
4. Fresh Reviewer + fresh Verifier на exact HEAD; merge = Human Gate.

## 6. Validation plan (этого WO, на dev-хосте)

- `python3 -m pytest tests/ -q` — полный набор зелёный (включая новые тесты).
- `PYTHONPATH=scripts python3 -m harness.cli check-consistency` → ok.
- `PYTHONPATH=scripts python3 -m harness.workflow_lint` → blocking=0.
- `PYTHONPATH=scripts python3 scripts/harness/work_cli.py validate
  docs/work/executions/EX-INFRA3-NATIVE-UBUNTU-R2-R1` → ok.
- Демонстрация отказа: `check-host` на dev-хосте (outenemy) возвращает
  not-eligible по hostname-правилу; исполняющие subcommands возвращают
  `BLOCKED_HOST` (негативные контролы самого tooling).

## 7. Честные границы результата

Результат — готовность: «выделить U1 → запустить tooling → получить
fingerprint/build/gates/NC evidence → activation decision с Human Gate».
Никакая часть фактической активации этим WO не выполняется и не может быть
выполнена без машины U1 и отдельного Human Gate. `NEW_SCIENCE` без R2 остаётся
`HARD_BLOCKED`.

## 8. Errata (repair R1, 2026-09-30 — после fresh review PASS @ 89fdbb0)

Уточнение §2 (инвариант 1): host-guard покрывает исполняющие subcommands
`build-engine`, `run`, `gate`, `nc-verify` (exit 2 `BLOCKED_HOST` вне
native-eligible U1); `fingerprint`, `check-host`, `nc-plan` — безопасны
на любом хосте; `report`, `activation-check` — read-only/аналитика (решение
об активации всё равно требует fingerprint + review + verify + Human Gate).
Gate PASS привязывает sha256/size evidence-файла; hostname deny-list
сравнивает full- и short-name; build provenance содержит верифицированный
commit. Детали — event 0005 и errata в execution summary.
