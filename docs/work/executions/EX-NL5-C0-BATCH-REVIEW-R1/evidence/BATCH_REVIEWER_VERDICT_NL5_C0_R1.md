# BATCH REVIEWER VERDICT — NL5-C0-R1 (F02 + F03 + F05-prep)

```text
RECORD_KIND      = BATCH_REVIEWER_VERDICT
EXECUTION        = EX-NL5-C0-BATCH-REVIEW-R1
WORK_ORDER       = WO-NL5-C0-BATCH-REVIEW-R1
PROGRAM          = NL5-CLOSE-R1 (issue #81); scope issues #83 / #84 / #86
ROLE             = REVIEWER (fresh independent session; no implementer context)
SESSION REF      = DSH subagent b8eca5d9-8ad0-419d-8092-58da4d471487 (Director dispatch proof 0000)
REVIEW BRANCH    = review/nl5-c0-batch-f02-f03-f05-r1
REVIEW BASE      = 3b567ae33f247b182b2ae451d2cc4598a9e76019 (same as program BASE)
REVIEW START HEAD= a70057000d97ad64979207391bf980ee7e240fae (tree f49af7ba7588e62e4d9a486958a732254285c2f2)
SCIENTIFIC RUNS  = 0 (documentary review only; no protocol/contract/seed edits; no subject-branch writes)
CLAIM CLASS      = C0_SOFTWARE_ONLY
BATCH VERDICT    = PASS (F02 PASS; F03 PASS; F05-prep PASS; all findings non-blocking)
```

## 0. Subject pinning (проверено независимо через `git fetch origin --prune`)

```text
git rev-parse origin/work/nl5-f02-u1-host-r1       = c38ad687d87bfa0c33d69bfee4fe40020d34ba45 (tree 8dbfeb02311d659c1a961434d3eb0a55502de569)
git rev-parse origin/work/nl5-f03-u2-readiness-r1  = 1831585fa70169c4e473acfe38e9603e45cfe22c (tree 8a89d2a446e4f05fcec7a6daade6572ff5a75212)
git rev-parse origin/work/nl5-f05-dispatch-prep-r1 = 4c9d8fd30300a2f48504d1b914693f0a66bb3555 (tree 17e2a7141295c9f6e5bf6fc302bc8d977b210a4d)
```

Все три exact HEAD/TREE совпадают с паспорт-обязательствами reviewer-паспорта; branch tips не двигались
между dispatch и review. `origin/main` = 3b567ae33f247b182b2ae451d2cc4598a9e76019 = BASE (не двигался).

## 1. F02 (U1 host eligibility) — VERDICT: PASS

### 1.1 Scope compliance — PASS

```text
git diff --name-only 3b567ae..c38ad68 ->
  docs/work/WO-NL5-F02-U1-HOST-R1.md
  docs/work/WORK_QUEUE.md                        (1 added line, 0 deleted)
  docs/work/executions/EX-NL5-F02-U1-HOST-R1/**  (dispatch, events 0001-0003, evidence, passport, summary)
```
Только allowed paths (WO + execution dir + 1 append). Запрещённые поверхности (project/*.json,
docs/evidence/NL5-V02-FREEZE/**, scripts/, tests/, frozen protocol/contract/seed) не затронуты.

### 1.2 Frozen integrity — PASS

```text
git diff --name-only 60da9a846511265a8ac7564da088c3d74cb073f0 c38ad68.. -- <protocol> <contract> <seed>   -> ПУСТО
git diff --name-only 60da9a846511265a8ac7564da088c3d74cb073f0 origin/main  -- <protocol> <contract> <seed> -> ПУСТО
git show <subject>:<protocol> | sha256sum = 2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d  == DIRECTOR_FREEZE_R2.json
git show <subject>:<contract> | sha256sum = 7e6476544e82af73d5d7e0672666ece99bf4d499a0da30645b02886bcdc45b3a  == DIRECTOR_FREEZE_R2.json
git show <subject>:<seed>     | sha256sum = 8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28  == DIRECTOR_FREEZE_R2.json
git rev-parse <subject>:<3 paths> = 48357196… / d6a9ccde… / 0164e0e3… == manifest blob SHA-1 (3/3)
```
Примечание: сам файл `DIRECTOR_FREEZE_R2.json` добавлен потомком F2 (commit-пин D2 по его собственной
lifecycle-нотации «S -> F -> D/R/V -> A»; record_source_note); это НЕ правка frozen-артефактов — байты
protocol/contract/seed при F2 совпадают байт-в-байт.

### 1.3 Events chain — PASS

```text
0001-work-order-started        2026-10-25T17:19:04Z  WORK_ORDER_STARTED        subject 59b59be
0002-continuation-…fingerprint 2026-10-25T17:21:35Z  CONTINUATION_CHECKPOINT   subject 59b59be
0003-handoff-completed         2026-10-25T17:23:20Z  HANDOFF_COMPLETED         subject 436be08
```
Таймстемпы parseable, монотонные, без batch-copy дублей; каждый event-файл создан одним коммитом и
не редактировался (`git log -- <event>` = ровно один commit на файл). Append-only соблюдён.

### 1.4 Claims vs evidence — PASS (все ключевые факты пересчитаны независимо)

- `hostname` (моя команда) = `outenemy`; `config/infra/r2-activation.v1.json`: `forbidden_hostnames: ["outenemy"]`,
  `outenemy_role: EXTERNAL_U2_ONLY` → FORBIDDEN_AS_U1 подтверждён.
- Owner-allocation каналы пусты (проверено мной): `test -f ~/.ssh/config` → ABSENT; `env | grep -iE 'u1|author_ubuntu'`
  → пусто; `origin/main` = BASE без движения; F01 handoff @ c7c5be6 подтверждает NOT_ASSIGNED. Итог 0/5 каналов.
- Evidence `U1_HOST_ELIGIBILITY_R1.json`: `verdict.status=BLOCKED_OWNER_U1`, `candidate_marking=CANDIDATE_NOT_ALLOCATED`,
  `author_u1=NOT_ASSIGNED`, `r2_status=WAITING_HOST / NOT_ACTIVE`, `scientific_runs=0`.
- Passport status = `BLOCKED_OWNER_U1`; self-accept отсутствует (grep по ACCEPTED/R2_ACTIVE/machine_launch_authorized=true
  по execution dir — единственное упоминание ACCEPTED это Director-описание F01 handoff в dispatch proof 0000,
  авторство Director, не self-accept имплементёра).
- Вердикт BLOCKED_OWNER_U1 корректен: выделения U1 нет, единственный доступный хост запрещён deny-list как U2.

### 1.5 Harness validators (read-only, на git archive дерева subject)

```text
cd /tmp/subj_f02 && PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-F02-U1-HOST-R1
  -> ok: True, errors: [], status BLOCKED_OWNER_U1
```

### 1.6 Findings F02

- F02-NF-1 (non-blocking, наблюдение): в dispatch proof 0000 (автор — Director, commit edd7952) F01 handoff
  охарактеризован как «ACCEPTED (documentary)». Это описательный статус документальной передачи F01,
  а не научная авторизация и не self-accept имплементёра F02; на вердикт F02 не влияет. Фиксируется для
  терминологической гигиены (COMPLETED_SANDBOX/HANDOFF != ACCEPTED).

## 2. F03 (U2 readiness + addendum) — VERDICT: PASS

### 2.1 Scope compliance — PASS

```text
git diff --name-only 3b567ae..1831585 ->
  docs/work/WO-NL5-F03-U2-READINESS-R1.md
  docs/work/WORK_QUEUE.md                        (+2 строки: 1 запись + 1 пустой separator; 0 удалений)
  docs/work/executions/EX-NL5-F03-U2-READINESS-R1/**  (dispatch, events 0001-0004, evidence x4, passport, summary)
```
Только allowed paths; запрещённые поверхности не затронуты.

### 2.2 Frozen integrity — PASS

Те же команды, что в §1.2 против subject 1831585: diff по frozen путям пуст; canonical SHA-256
protocol/contract/seed = 3/3 MATCH с DIRECTOR_FREEZE_R2.json (2658ee3e… / 7e647654… / 8e844bff…).

### 2.3 Events chain — PASS с finding (append-only нарушен по букве, не по существу)

```text
0001-work-order-started                    2026-10-25T17:20:41Z WORK_ORDER_STARTED       subject 7e1e0bc
0002-continuation-stale-audit-…            2026-10-25T17:26:20Z CONTINUATION_CHECKPOINT  subject cc3430e
0003-handoff-completed                     2026-10-25T17:27:35Z HANDOFF_COMPLETED        subject 52798b7
0004-continuation-addendum-live-u2-host-…  2026-10-25T17:36:29Z CONTINUATION_CHECKPOINT  subject 39e9aec (post-terminal, corrections-класс — допустимо)
```
Таймстемпы монотонные. Post-terminal addendum 0004 — корректный corrections-class (не редактировал
предыдущие файлы: `git log` по evidence 0001-0003 не показывает правок в 1831585).

### 2.4 Claims vs evidence — PASS (ключевые claims пересчитаны независимо)

- **Engine binary sha256**: путь из evidence `~/nanolab/cache/oxdna-build-r2-u2/bin/oxDNA`. Мои команды:
  `sha256sum` = `6effd00a09628895fac48b8b4c60c4dc82557d05910da6bebe276b8355126b78`, `stat -c %s` = 3380728 bytes —
  ТОЧНОЕ совпадение с claim (L-04 live PASS подтверждён независимо).
- **«9/9 F2-блобов SAME на main»**: мой пересчёт `git rev-parse F2:<path>` vs `git rev-parse origin/main:<path>`
  для всех файлов, изменённых коммитом F2 → 8/8 SAME. Девятая запись композиции F03 — `DIRECTOR_FREEZE_R2.json`
  (добавлен потомком F2), помечен SAME_DIR. Существу claim соответствует (целостность F2 подтверждена),
  формулировка «9 files changed by F2» неточна — см. F03-NF-2.
- **L-03 диски**: мой `df -h /` = 96% used, 19G available (nvme0n1p2, 458G) — совпадает с измерением addendum
  0004; addendum честно фиксирует `L-03 = MEASURED_FAIL_ON_THRESHOLD` (порог 80% превышен на всех томах;
  pass-condition ≥2×15GB=30GB free сейчас не выполняется) и требует remediation/accept-risk до F07. F03 НЕ
  заявлял disk-pass — расхождений claim vs evidence нет; моё измерение подтверждает их измерение.

### 2.5 Self-accept/статусы — PASS

Passport = `HANDOFF_READY`; verdict = `READY_FOR_DISPATCH_PREP` + `BLOCKED_NO_U2_ACCESS_FROM_SESSION`;
grep `R2_ACTIVE=true|machine_launch_authorized=true|status=ACCEPTED` по execution dir и WO — 0 совпадений.
Constraints явно фиксируют: U2-ready != R2_ACTIVE != scientific authorization.

### 2.6 Harness validators (read-only, на git archive дерева subject)

```text
cd /tmp/subj_f03 && PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-F03-U2-READINESS-R1
  -> ok: True, errors: [], status HANDOFF_READY (has_post_terminal_corrections: true — event 0004 распознан как corrections-класс)
```

### 2.7 Findings F03

- **F03-NF-1 (non-blocking)**: пре-терминальные events 0001 и 0002 были отредактированы в handoff-коммите
  39e9aec: `actor_role: EXTERNAL-PREFLIGHT-IMPLEMENTER -> IMPLEMENTER` (единственное изменение в обоих
  файлах, подтверждено diff; timestamps/subject_sha/summary не менялись). По AGENTS.md («events не
  редактировать; corrections — новым event») это нарушение append-only по букве. Митигируется: (а) правка
  открыто заявлена в commit message («canonical actor_role»); (б) не меняет ни одного факта, результате или
  таймстемпа; (в) оригинал сохранён в git-истории; (г) роль и до, и после — implementer-класс. Правильный
  паттерн — corrections event. На вердикты/факты не влияет → non-blocking.
- **F03-NF-2 (non-blocking)**: формулировка «9/9 files changed by F2 SAME» неточна: коммит F2 меняет 8 файлов
  (все 8 SAME — проверено мной), 9-я запись композиции — DIRECTOR_FREEZE_R2.json (SAME_DIR, добавлен
  потомком F2). Существу утверждения (целостность F2) это не противоречит.
- **F03-NF-3 (non-blocking, formatting)**: WORK_QUEUE append = 1 строка-запись + 1 пустая строка-separator
  (0 удалений); существующие строки не менялись.
- **F03-NF-4 (non-blocking, наблюдение)**: `actor_id` в events = `nl5-f03-u2-preflight-r1` при
  execution/WO-именовании `…u2-readiness…` — legacy-нейминг ранней фазы; dsh_session_id консистентен.

## 3. F05-prep (dispatch readiness C0) — VERDICT: PASS

### 3.1 Scope compliance — PASS

```text
git diff --name-only 3b567ae..4c9d8fd ->
  docs/work/WO-NL5-F05-DISPATCH-PREP-R1.md
  docs/work/WORK_QUEUE.md                        (1 added line, 0 deleted)
  docs/work/executions/EX-NL5-F05-DISPATCH-PREP-R1/**  (dispatch, events 0001-0003, evidence x3, passport, summary)
```
Только allowed paths; scripts/** и запрещённые поверхности не тронуты.

### 3.2 Frozen integrity — PASS

Те же команды, что в §1.2 против subject 4c9d8fd: diff по frozen путям пуст; canonical SHA-256 3/3 MATCH.

### 3.3 Events chain — PASS

```text
0001-work-order-started                        2026-10-25T17:15:00Z WORK_ORDER_STARTED       subject 9da777b
0002-continuation-frozen-dispatch-verification 2026-10-25T17:37:09Z CONTINUATION_CHECKPOINT  subject cfaea0a
0003-handoff-completed                         2026-10-25T17:37:44Z HANDOFF_COMPLETED        subject cfaea0a
```
Таймстемпы монотонные; каждый event-файл создан одним коммитом (4c9d8fd) и не редактировался.

### 3.4 Claims vs evidence — PASS (пересчитано независимо)

**Seed replay 148 identities / 85 checks:**
- Мой пересчёт по самому frozen seed record (`repro-v0-2-seed-record-FROZEN_R2.json` @ subject):
  `seeds`: 0b=64, 32b=64, 11b=10, 53b=10 → **148** (= declared `fresh_seed_total` 148);
  `bootstrap_seeds`: 4; `replacement_pools`: 12/12/2/2 → **28**; `skipped_identities`: 10/11/10/10 → **41**;
  всего различных идентичностей 148+4+28 = **180**, все уникальны (проверка set-ом), пересечений
  seed↔pool по литералам нет. Всё совпадает с claims F05.
- `checks_log` в DISPATCH_READINESS_R1.json: ровно **85** записей, все `ok: true`, `checks_failed: []`,
  verdict PASS — «85/85» подтверждено подсчётом.

**Budget ledger арифметика:**
- 296 = 148 × 2 (author leg + external leg) ✓; 56 = 28 × 2 ✓; 296 + 56 = **352** = max_runs ✓;
  max_runs_per_platform = **176** = 352/2 ✓.
- wall_hours_per_platform = **560**: пересчитано из первоисточника —
  `git show origin/main:docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.json`:
  `approved_parameters.wall_hours_per_platform = 560`, confirmatory_runs=296, replacement_runs_cap=56,
  max_runs=352, quotas 12/12/2/2 — всё совпадает; `sha256sum` файла =
  `b68dd341a5671d6314da3fcf6d32fae54f88b385b7b5a631edb07b0f6f49d2c9` == binding в ledger;
  `git rev-parse` blob = `61d1491233aeb2537f9800d6183def5b8fb0c8e0` == binding.
- Storage: базис пересчитан из `run_output_digests_p1.json` (n=20 final runs; агрегация size_bytes по run):
  mean = **105.9 MB**, max = **119.8 MB** — точное совпадение с ledger. Тогда 176 × 119.8 MB = 21 084.8 MB ≈
  **21.08 GB ≤ 21.2 GB** claimed ceiling ✓; 176 × 105.9 MB = 18.6 GB (expected) ✓; 2×21.2 = 42.4 GB total ✓;
  retry reserve 1.5× → ≥ 32 GB/platform ✓.

**Adversarial 7/8:**
- В evidence 8 негативных тестов: ADV-1/2/4/5/6/7/8 = REJECTED (exit 3), ADV-3 = NOT_REJECTED_AT_GATE_SCOPE
  → 7/8, логично и честно (единственный незакрытый кейс задокументирован как finding F05-F-1).
- **Независимое воспроизведение** (read-only; копии в /tmp, `--repo-root` на review worktree, скрипт из
  дерева subject):
  - T1 pristine protocol+contract+record → `gate: PASS, exit 0`;
  - T2 воспроизведение ADV-3: sed-правка строки 263 `N = 64 -> N = 65` (prose) → `gate: PASS, exit 0`
    → **F05-F-1 подтверждён как реальный**: prose-правка вне machine-блоков gate не ловит;
  - T3 негатив-контроль: правка machine-блока `n_0b = 64 -> 63` → `gate: FREEZE_GATE_FAIL, exit 3`
    («protocol machine block n_0b = '63' != contract '64'»).

**F05-F-1 компенсация (canonical_sha256 binding) — существует, проверено кодом и хэшами:**
- `scripts/nl5/repro_v02_freeze_contract.py` (прочитан read-only из дерева subject, 2931 строка):
  authority/plan-стадия для каждого `frozen_subject_binding.{protocol,contract,seed_record}` читает Git-объект
  `art_commit:path` и проверяет `hashlib.sha256(raw).hexdigest() != art_digest` (строки ~1893–1905), плюс
  git blob SHA-1 match (строки ~1880–1892) и `source_commit == frozen_head` (строки ~1872–1878). Любая байтовая
  правка протокола (включая prose) меняет sha256 → authority-стадия fail-closed.
- T4: sha256 tampered prose copy = `23666bf6…` != канонический `2658ee3e…` — дрифт детектируем биндингом.

### 3.5 Self-accept/статусы — PASS

`state_ceiling` в evidence: `SCIENTIFIC_RUNS=0`, `AUTHOR_U1=NOT_ASSIGNED`, `R2=WAITING_HOST / NOT_ACTIVE`,
`R2_ACTIVE=false`, `machine_launch_authorized=false`, `launch_gate=HUMAN_PROTECTED_WRITER`,
`authority_A_created_in_this_wo=false`. Passport = `HANDOFF_READY`; honest_result_class =
`READY_WITH_OPEN_GATES`; pre-launch gate GATE-F04-R2-ACTIVE = OPEN. Никакой научной авторизации,
R2 activation или ACCEPTED не объявлено.

### 3.6 Harness validators (read-only, на git archive дерева subject)

```text
cd /tmp/subj_f05 && PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-F05-DISPATCH-PREP-R1
  -> ok: True, errors: [], status HANDOFF_READY
```

### 3.7 Findings F05

- **F05-NF-1 (non-blocking, process)**: все три event-файла (включая WORK_ORDER_STARTED с timestamp
  17:15:00Z) закоммичены одним финальным коммитом 4c9d8fd, т.е. durable START record не публиковался
  до substantive work (AGENTS.md work protocol п.3). Для C0-documentary WO с offline-валидаторами риск
  минимален: timestamps монотонные и правдоподобные, evidence полный и append-only. Отмечено для
  процессной гигиены следующих WO.
- Позит: явное `script_location_note` (verification script в /tmp, не в scripts/**) — корректное уважение
  read-only scope scripts/**.

## 4. WORK_QUEUE

```text
F02: git diff BASE..c38ad68 -- docs/work/WORK_QUEUE.md -> +1 строка, -0
F03: git diff BASE..1831585 -- docs/work/WORK_QUEUE.md -> +2 строки (1 запись + 1 separator), -0
F05: git diff BASE..4c9d8fd -- docs/work/WORK_QUEUE.md -> +1 строка, -0
```
Ровно одна запись на subject; существующие строки не менялись ни в одном subject (0 deletions везде).

## 5. Независимые пересчёты reviewer (сводка команд)

```text
git fetch origin --prune; git rev-parse <3 subject refs> и <ref>^{tree}   -> exact HEAD/TREE 3/3 match
git diff --name-only 3b567ae..<subject>                                    -> scope 3/3 (allowed paths only)
git diff --name-only 60da9a8..<subject> -- <frozen paths>                  -> пусто 3/3; то же для origin/main
git show <subject>:<protocol|contract|seed> | sha256sum                    -> 3/3 canonical match
git rev-parse <subject>:<3 paths>                                          -> 3/3 blob SHA-1 match
hostname; test -f ~/.ssh/config; env | grep -iE 'u1|author_ubuntu'         -> outenemy; ABSENT; пусто
grep -A6 forbidden_hostnames config/infra/r2-activation.v1.json            -> ["outenemy"], EXTERNAL_U2_ONLY
git rev-parse origin/main                                                  -> 3b567ae (= BASE, не двигался)
git diff --name-only 60da9a8^ 60da9a8 (+ per-file rev-parse F2 vs main)    -> 8/8 SAME (базис «9/9» F03)
sha256sum ~/nanolab/cache/oxdna-build-r2-u2/bin/oxDNA; stat -c %s          -> 6effd00a…5126b78; 3380728 (exact match)
df -h /                                                                    -> 96% used, 19G avail (совпало с F03 addendum)
python3 (recount seeds/pools/skips/uniqueness из frozen seed record)       -> 148/4/28/41/180 unique, 0 overlap
python3 (len(checks_log), all ok)                                          -> 85/85 ok
python3 (budget arithmetic + HG_B json/sha256/blob)                        -> 296/56/352/176/560h/storage 21.08GB<=21.2; b68dd341…, 61d14912…
python3 (aggregate run_output_digests_p1.json per-run size_bytes)          -> mean 105.9 MB, max 119.8 MB (n=20)
gate T1 pristine / T2 prose-tamper / T3 machine-tamper (копии в /tmp)      -> PASS exit0 / PASS exit0 / FAIL exit3
sha256sum pristine vs prose-tampered protocol                              -> 2658ee3e… vs 23666bf6… (дрифт детектируем)
read scripts/nl5/repro_v02_freeze_contract.py (строки ~1840-1950)          -> canonical_sha256 recomputed from Git object bytes
work_cli validate на git-archive деревьях всех трёх subjects               -> ok:True, errors:[] x3
```

## 6. Вердикты

```text
F02  (work/nl5-f02-u1-host-r1        @ c38ad687d87bfa0c33d69bfee4fe40020d34ba45) = PASS
F03  (work/nl5-f03-u2-readiness-r1   @ 1831585fa70169c4e473acfe38e9603e45cfe22c) = PASS
F05  (work/nl5-f05-dispatch-prep-r1  @ 4c9d8fd30300a2f48504d1b914693f0a66bb3555) = PASS
BATCH VERDICT = PASS (все три PASS; blocking findings: 0)
```

## 7. Remaining risks / next action

- Все находки non-blocking (F02-NF-1, F03-NF-1..NF-4, F05-NF-1); научных/бюджетных/authority-рисков не
  обнаружено; launch gates сохранены на всех трёх subjects.
- Напоминание ceiling: PASS здесь — это documentary C0 review конкретных HEAD; это НЕ R2 activation,
  НЕ научная авторизация и НЕ ACCEPTED. F04 остаётся заблокирован до реального выделения U1 (owner actions
  A1–A6); L-03 storage threshold на U2 сейчас fail (96%/19G) — требуется remediation или accept-risk до F07.
- NEXT_ACTION (единственный): Director передаёт batch PASS свежему Verifier (отдельный dispatch, exact
  HEAD/TREE всех трёх subjects), затем Human Gate.

## 8. Divergence note (enum mapping)

Директива называет события «0001 (REVIEW_STARTED) → 0002 (REVIEW_PASS)»; canonical enum harness
(`scripts/harness/work_cli.py` ALLOWED_EVENTS) не содержит типов REVIEW_STARTED/REVIEW_PASS. Использованы
enum-валидные типы с семантикой в event_id: `0001-review-started` = WORK_ORDER_STARTED,
`0002-review-verdict-pass` = HANDOFF_COMPLETED (terminal). Это документированное соответствие, не отступление.
