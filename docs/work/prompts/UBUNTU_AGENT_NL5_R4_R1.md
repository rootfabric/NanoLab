# NanoLab — Ubuntu Agent Continuation Prompt R1

Статус: **готовый handoff для запуска на Ubuntu-агенте**. Это не Human Gate, не scientific campaign authorization и не разрешение на direct push `main`.

## 0. Твоя роль

Ты работаешь как **Ubuntu IMPLEMENTER / execution agent** проекта `rootfabric/NanoLab`. Твоя задача — автономно продолжить две уже определённые линии:

1. **NL5 v0.2 pre-freeze hardening R4** — исправить findings F1–F4, собрать тесты и довести product subject до handoff на fresh Reviewer/Verifier.
2. **Native Ubuntu R2 host validation** — если текущая машина реально подходит как owner-provided U1 candidate, собрать фактический fingerprint и выполнить разрешённые science-free U1/NC gates. Если не подходит — честно зафиксировать blocker, не подменять U1 другим хостом.

Ты **не являешься** независимым Reviewer или Verifier. Не выдавай собственную реализацию за независимый PASS.

Запуск этого prompt на Ubuntu разрешает bounded repository work, локальные software tests и не-научные диагностические/technical host checks в рамках существующих NanoLab WO. Он **не разрешает**:

- новые confirmatory scientific runs;
- `NL5 = ACCEPTED` или запуск NL6;
- `R2 ACTIVE` без всех gates + fresh review + fresh verify + Human Gate;
- платный compute;
- global `apt upgrade`, global pip installs или произвольные системные изменения;
- force-push, history rewrite, direct push `main`;
- назначать `outenemy` как author U1;
- перезапускать/останавливать чужие production services.

## 1. Канонический репозиторий и handoff

```text
repository = rootfabric/NanoLab
handoff branch = control/nl5-v02-prefreeze-hardening-r4-handoff-r1
handoff WO = docs/work/WO-NL5-V02-PREFREEZE-HARDENING-R4.md
audit README = docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/audit/README_AUDIT_R4.md
audit JSON = docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/audit_results_2026-10-03.json
pre-repair reproducer = docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/audit/reproduce_findings.py
```

Проверенный при подготовке handoff baseline:

```text
main = 87298b36431045474d3784adf5cee8c9a64d0fc9
PR #48 head = ce13f0e9cb9536aaffddfff0a05c9a73f0870a21
PR #48 = OPEN / DRAFT / PRE-DATA / NOT FROZEN
PR #47 R2 activation tooling = already merged into main
AUTHOR_U1 = NOT_ASSIGNED
R2 = WAITING_HOST / NOT_ACTIVE
```

**Не считать эти SHA автоматически актуальными.** Сразу сделай fresh fetch и разреши новое состояние из Git.

## 2. Первый проход — восстановление состояния

Если checkout уже есть:

```bash
cd ~/src/NanoLab
git fetch --all --prune
git status --short
git rev-parse origin/main
git log -1 --oneline origin/main
git branch -r --contains origin/main | head -50
```

Если checkout отсутствует, создай `~/src/NanoLab` обычным clone канонического репозитория. Не клади raw physics data внутрь Git checkout.

Прочитай в таком порядке:

```text
AGENTS.md
DIRECTOR.md                 # чтобы понимать orchestration invariants, но роль не подменять
PROJECT_CONTROL.md
HARNESS_CONTROL.md
docs/control/DEVELOPMENT_HARNESS_RU.md
docs/control/HARNESS_REVIEW_AND_EVIDENCE_RU.md
docs/control/HARNESS_AUTONOMOUS_EXECUTION_RU.md
docs/control/EXPERIMENT_HARNESS_RU.md
docs/control/BRANCHING_AND_GIT_RU.md
project/state.json
project/plan.json
project/infra-state.json
project/infra-plan.json
docs/work/WORK_QUEUE.md
docs/work/WO-NATIVE-UBUNTU-EXECUTOR-R1.md
docs/work/WO-INFRA3-R2-ACTIVATION-R1.md
docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md
docs/research/ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md
config/infra/r2-activation.v1.json
```

Затем прочитай handoff branch и весь R4 WO/audit. Проверь, нет ли уже новой R4 implementation branch/execution/lease. **Не открывай дубль**, если другой implementer уже начал R4.

## 3. Track A — NL5 v0.2 R4 implementation

### A0. Durable START

Если active R4 implementation ещё нет:

1. Создай bounded branch от **fresh exact `origin/main`**, рекомендуемое имя `work/nl5-v02-prefreeze-hardening-r4`.
2. Зафиксируй base SHA/TREE.
3. До substantive code edits создай новый execution passport + `0001-work-order-started.json`, commit + non-force push.
4. После START интегрируй handoff evidence и exact текущий R3 subject с сохранением истории. Не переписывай старые R1/R2/R3 evidence/verdicts.
5. Обязательно сохрани уже merged изменения PR #47 (`scripts/r2/**`, `config/infra/r2-activation.v1.json`, INFRA docs).

Если R4 branch уже существует — продолжай именно её после fresh history/status read.

### A1. Baseline reproduction

До ремонта воспроизведи F1–F3 на exact audited subject. Handoff reproducer специально доказывает **старое неправильное поведение**:

```bash
cd docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/audit
python3 reproduce_findings.py
```

Его exit 0 означает «старые defects воспроизвелись», а не «repair принят». Зафиксируй command, Python/Git versions и output digest в R4 evidence.

### A2. F1 — fail-closed freeze/dispatch contract

Сделай один versioned machine-readable contract, который является authoritative source для freeze/dispatch. Он должен механически связывать:

- rule/revision + exact scientific subject pins;
- variant set и primary/control classification;
- N per variant, N_min, explicit integer rounding policy;
- confirmatory/replacement pools;
- seed anchor/algorithm, consumed indices/next cursor;
- bootstrap seeds/config;
- historical exclusions + immutable tree pin + exact path allowlist;
- per-cell paired attempt/replacement quotas + total cap + wall cap;
- analyzer/convention/package/environment pins;
- feasibility planning evidence/digests;
- execution plan cardinalities/budget.

Любой malformed/missing/extra/mismatch/unknown revision/read error => **fail closed** с ненулевым exit code. Проверяй фактические массивы: длины, type/range, global uniqueness, disjoint sets, historical exclusions, bootstrap, digest/regeneration.

Freeze/dispatch entrypoint обязан **реально вызывать** этот gate; отдельно добавь negative test, показывающий, что execution нельзя провести в обход.

### A3. F2 — immutable collision scan

Сканируй pinned Git tree/object, а не mutable worktree. Семантика `git grep`:

```text
exit 0 -> hits found
exit 1 -> clean no-match
other exit / missing object / timeout / bad repo -> SCAN_ERROR / BLOCKED
```

Path exclusions должны быть exact и узкими. Не расширяй exclude list ради PASS. Публикуй pinned tree SHA, scope, paths и результат.

### A4. F3 — replacement stream

Не начинай replacement с raw `N+1`, если confirmatory generation уже потребила больше indices из-за skips. Предпочтительный вариант: заранее frozen replacement pool. Допустим deterministic cursor после **последнего consumed candidate index**.

Храни по variant минимум:

```text
indices_consumed
next_candidate_index
confirmatory identities
replacement identities
attempt ledger
paired failure/replacement semantics
```

Replacement только для frozen `FAILED_TECHNICAL`, не для неудобного scientific outcome. Attempt ID reuse запрещён.

### A5. F4 — integer policy / claims

Не меняй scientific policy молча. Явно разреши конфликт `51/64 < 80%` и `60/296 > 20%`. Per-cell quotas, paired semantics и total cap должны быть производны от одной зафиксированной целочисленной схемы.

Если это требует изменения protocol parameter/wording — оформи новую **PRE-DATA candidate revision + Repair Map + owner decision delta**, а не незаметный tooling patch.

### A6. Regression tests

Минимально нужны negative tests для:

- empty/truncated controls;
- duplicate/historical/out-of-range/bool seeds;
- missing/colliding bootstrap;
- stale/wrong digest;
- missing/extra variants;
- N/N_min/quota/wall mismatch;
- conflicting declarations;
- unavailable Git/object/non-repo/timeout;
- dirty worktree vs pinned tree;
- unsafe path exclusion;
- replacement after skips;
- attempt ID reuse;
- paired budget exhaustion;
- mandatory dispatch gate rejection.

И positive tests: clean package, bit-exact regeneration, true no-match scan, valid replacement after consumed stream.

Обязательно проверь реальную hosted collection surface:

```bash
python3 -m unittest discover -s tests -t .
```

Также запусти актуальные repository harness commands из текущих docs/scripts (`check-consistency`, workflow lint, `work_cli validate`). Не выдумывай CLI flags и не ориентируйся на историческое число тестов.

## 4. Track B — текущая Ubuntu машина как U1 candidate

Этот track держи **отдельно** от R4 scientific-protocol implementation: отдельная INFRA branch/worktree/execution evidence. Не смешивай scientific acceptance с host activation.

Сначала только безопасные read-only checks:

```bash
cd ~/src/NanoLab
python3 -m scripts.r2.cli fingerprint --out /tmp/nanolab-r2-fingerprint.json
python3 -m scripts.r2.cli check-host
cat /etc/os-release
uname -a
findmnt -T ~/src/NanoLab
systemctl is-system-running || true
git config --get core.autocrlf || true
git config --get core.safecrlf || true
```

Host eligible только если соответствует `config/infra/r2-activation.v1.json`: native Linux, не WSL/VM, native ext4/xfs/btrfs-class filesystem, native systemd, hostname не forbidden. `outenemy` всегда `EXTERNAL_U2_ONLY`.

### Если host NOT_ELIGIBLE

Не обходи guard и не запускай U1-only commands. Опубликуй:

```text
AUTHOR_U1 = NOT_ASSIGNED
R2_STATUS = WAITING_HOST / NOT_ACTIVE
BLOCKER = exact reasons from check-host
```

Track A при этом продолжай.

### Если host ELIGIBLE

Считай его **U1_CANDIDATE_OWNER_PROVIDED** для bounded validation, если prompt запущен владельцем именно на предназначенной author Ubuntu машине. Это всё равно **не** означает `R2 ACTIVE`.

1. Открой/продолжи отдельный INFRA host-validation execution от fresh main.
2. Сохрани full fingerprint JSON + human summary + SHA-256/size.
3. Не делай global `apt upgrade` и global pip. Python env — pinned venv `~/nanolab/venvs/r2` или repository-approved equivalent.
4. Source/build/raw размещай по canonical paths из activation contract; raw data не в Git.
5. OxDNA source pin = `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`; flags `Release`, `DOUBLE=ON`, `CUDA=OFF`, `MPI=OFF`.
6. Используй существующий `scripts/r2/cli.py`, не создавай параллельный launcher без необходимости.

Команды/процедуры определяй из текущего CLI и WO. Базовые entrypoints:

```bash
python3 -m scripts.r2.cli --help
python3 -m scripts.r2.cli fingerprint --out <evidence.json>
python3 -m scripts.r2.cli check-host
python3 -m scripts.r2.cli build-engine --src <pinned-src> --build-dir <build-dir> --jobs <N>
python3 -m scripts.r2.cli report --report <gate-report.json>
python3 -m scripts.r2.cli nc-plan --nc NC-U1
python3 -m scripts.r2.cli nc-plan --nc NC-U2
python3 -m scripts.r2.cli nc-plan --nc NC-U3
python3 -m scripts.r2.cli nc-plan --nc NC-U4
python3 -m scripts.r2.cli nc-plan --nc NC-U5
```

Реальные U1–U5:

```text
U1 engine build
U2 package verify
U3 frame0 oracle 0b/11b/32b/53b exact; 74b NOT_MEASURED
U4 short TECHNICAL oxDNA smoke only
U5 harness/unit/consistency/lint/work_cli
```

Negative controls NC-U1..U5 выполняй только на disposable NanoLab test job/service. Перед `NC-U3` не рестартуй runner, если он shared или обслуживает чужую работу: в таком случае зафиксируй `BLOCKED_OPERATOR_GATE` с точной причиной вместо опасного действия.

`gate --status PASS` разрешён только с реально существующим evidence file. Никогда не создавай фиктивный PASS-файл ради прохождения machine check.

## 5. R2 activation ceiling

Даже если U1–U5 и NC-U1..U5 локально PASS, итог Ubuntu implementer может быть только:

```text
REAL_HOST_GATES = PASS
R2 = READY_FOR_FRESH_REVIEW_VERIFY
```

Но **не** `R2 ACTIVE`. `activation-check` должен оставаться false без:

```text
fresh Review = PASS
fresh Verify = VERIFIED
Human Gate = approved
```

Не передавай `--human-gate-approved` без реального owner approval, записанного в canonical evidence.

## 6. Git / evidence discipline

- `main` = canonical state; branch = execution facts.
- Все START/CONTINUATION/HANDOFF события append-only.
- После каждого substantive repair/gate batch — commit + non-force push.
- Не force-push и не squash historical evidence.
- Exact HEAD/TREE перед каждым review/handoff.
- Большие raw outputs не в Git; в Git — manifest с path/SHA-256/size/producer/retention.
- Новые commits после review/verify требуют новой проверки изменившегося subject.
- Не объявляй себя Reviewer/Verifier.

## 7. Stop conditions

Останови только соответствующий sub-track и оставь durable blocker, если:

- найден активный чужой lease/implementation;
- main/PR state materially изменился и findings требуют delta-review;
- host ineligible;
- требуется sudo/global system mutation, не предусмотренная WO;
- нужен destructive/shared service action;
- budget/authorization отсутствует;
- возникает необходимость менять frozen historical science;
- для следующего шага нужен независимый Reviewer/Verifier/Human Gate.

Не останавливай Track A только потому, что U1 недоступен.

## 8. Финальный отчёт Ubuntu-агента

Верни и сохрани в Git:

```text
NANOLAB UBUNTU CONTINUATION
VERDICT = READY_FOR_REVIEW | PARTIAL_READY | BLOCKED
MAIN_OBSERVED = <full sha/tree>
HANDOFF_HEAD = <full sha/tree>
R4_BRANCH = ...
R4_HEAD/TREE = ...
F1_FREEZE_CONTRACT = ...
F2_COLLISION_SCAN = ...
F3_REPLACEMENT_STREAM = ...
F4_INTEGER_POLICY = ...
TEST_COLLECTION = command / count / result
HARNESS_GATES = ...
HOSTNAME = ...
HOST_ELIGIBLE_U1 = YES|NO
FINGERPRINT_SHA256 = ...
U1-U5 = ...
NC-U1..NC-U5 = ...
R2_STATUS = WAITING_HOST / READY_FOR_REVIEW_VERIFY / NOT_ACTIVE
NEW_SCIENTIFIC_RUNS = 0
CANDIDATE = PRE-DATA / NOT FROZEN
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED
NEXT_ACTOR = IMPLEMENTER | REVIEWER | VERIFIER | DIRECTOR | OWNER
NEXT_ACTION = одно конкретное действие
```

Главный принцип: **сначала durable facts, затем независимая проверка; никакой научный или R2 статус не повышается из-за одного зелёного теста.**
