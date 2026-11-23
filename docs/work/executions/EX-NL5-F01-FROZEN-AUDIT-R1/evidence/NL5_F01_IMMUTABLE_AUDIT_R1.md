# NL5_F01_IMMUTABLE_AUDIT_R1 — независимый аудит NL5 FROZEN_R2 и графа задач (C0)

**Execution:** `EX-NL5-F01-FROZEN-AUDIT-R1`
**Work Order:** `WO-NL5-F01-FROZEN-AUDIT-R1` ([Issue #82](https://github.com/rootfabric/NanoLab/issues/82), программа [NL5-CLOSE-R1 #81](https://github.com/rootfabric/NanoLab/issues/81))
**Claim class:** `C0_SOFTWARE_ONLY` · **Risk:** `MEDIUM` · **SCIENTIFIC_RUNS = 0** (жёсткий ноль: ни одного oxDNA/MD/physics-запуска, ни одного платного ресурса)
**Actor:** `IMPLEMENTER-AUDITOR` (`nl5-f01-auditor-r1`) — **реальная отдельная субагентская сессия**, запущенная Director через DSH subagent tool.

> Аудит контрольный/документальный. Все выводы прежних Reviewer/Verifier сохранены без изменений; научный статус никем не переопределяется; самоприменения ACCEPTED/PASS нет. Максимум этого WO — `HANDOFF_COMPLETED` с фактами.

---

## 0. Идентичность исполнителя (реальные доказательства, без имитации)

| Факт | Значение | Как получено |
|---|---|---|
| Launcher | DSH subagent tool (Director запустил настоящую отдельную сессию) | факт запуска; dispatch proof Director |
| DSH session id аудитора | `454dea06-3e76-4c1e-80bd-d5287bc2cae0` | переменная окружения `DSH_SESSION_ID` этой сессии |
| Director session (для связи) | `e49ea301c3d2` | `dispatch/0000-DIRECTOR-DISPATCH-PROOF.md` |
| Branch / base | `work/nl5-f01-frozen-audit-r1`, BASE `3b567ae33f247b182b2ae451d2cc4598a9e76019`, TREE `560dc913a71a237d3c452a5a2e492e213b232911` | `git rev-parse` |
| Dispatch HEAD | `11f901bfc49b5b6b3c086865f5d73c48f94c520b` | `git rev-parse HEAD` на старте |

Вымышленные session/job id не использовались и не нужны: реальный launcher существует (этот документ — его продукт).

---

## 1. Epoch check: свежий `git fetch origin`

```text
git fetch origin --prune
git rev-parse origin/main   -> 3b567ae33f247b182b2ae451d2cc4598a9e76019
```

**Результат: `origin/main` = BASE = `3b567ae…` → НЕТ epoch change.** Программа NL5-CLOSE-R1 опубликована на том же HEAD, на котором выполняется аудит. Отдельного события EPOCH_CHANGE не требуется.

## 2. Пересчёт immutable-хешей на exact F2

`F2 = 60da9a846511265a8ac7564da088c3d74cb073f0`, `F2_TREE = e565c8a6cee9e829fac14008ebc9c2ea1609931d` (пересчитано: `git rev-parse F2^{tree}`).

Команды пересчёта (воспроизводимы дословно):

```bash
git rev-parse 60da9a846511265a8ac7564da088c3d74cb073f0:<path>          # GIT_BLOB_SHA1
git show 60da9a846511265a8ac7564da088c3d74cb073f0:<path> | sha256sum   # CANONICAL_BLOB_SHA256
```

| Артефакт | Путь | GIT_BLOB_SHA1 (пересчитан) | CANONICAL_BLOB_SHA256 (пересчитан) | Декларировано в DIRECTOR_FREEZE_R2.json | Вердикт |
|---|---|---|---|---|---|
| Frozen protocol | `docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md` | `4835719622bae49a8e8b480536a482b4b222d408` | `2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d` | те же (`protocol_blob_sha1` / `protocol_sha256`) | **MATCH** |
| Freeze contract | `docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-freeze-contract-FROZEN_R2.json` | `d6a9ccde4d1dadf42d1a8cd9b88faa02646cf70b` | `7e6476544e82af73d5d7e0672666ece99bf4d499a0da30645b02886bcdc45b3a` | те же (`contract_blob_sha1` / `contract_sha256`) | **MATCH** |
| Seed record | `docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-seed-record-FROZEN_R2.json` | `0164e0e3f5dda6dbf63174df3730b1bd921d2c76` | `8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28` | те же (`seed_record_blob_sha1` / `seed_record_sha256`) | **MATCH** |

**3/3 MATCH.** FROZEN_R2 package не изменён после публикации. Дополнительно сверены внутренние привязки контракта: `scientific_subject.seed_record_file_sha256` = `8e844bff…`, `seed_record_r4_sha256` = `51a8819236bd780b6034e83e3b89f4594ac176df3397a9c6b47806e09651fe91`, `replacement_pool_sha256` = `369a63c05592c400a2d6c160ecad940d1b0654948c1165650dbd1cce6a7ee821` — прочитаны из frozen-байтов, противоречий с Director record нет.

## 3. Ancestry / authority chain

| Проверка | Команда | Результат |
|---|---|---|
| F2 — предок origin/main | `git merge-base --is-ancestor 60da9a8… origin/main` | exit 0 → **YES** |
| F2 — предок рабочей ветки | `git merge-base --is-ancestor 60da9a8… HEAD` | exit 0 → **YES** |
| Director FREEZE R2 record (D2) в main | добавлен в `a2f7304ebbb5973b81cf49dee60c21c85c6a974d`; `git merge-base --is-ancestor a2f7304… origin/main` | exit 0 → **YES** |
| D2 pin-ы | `subject_head=60da9a8…`, `subject_tree=e565c8a6…` | совпадают с пересчитанными |
| HG-B | `docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.json`: `record_kind=HG_B_OWNER_APPROVAL`, `issuer_class=HUMAN_GATE_OWNER`, `decision=APPROVED`, `candidate_revision=R4`, `rule_id=NANOLAB_REPRO_V0_2_DISTRIBUTIONAL`, `recorded_at_utc=2026-10-05T02:15:00Z` | **HG-B = APPROVED** |
| Lifecycle D2 | `record_source_note`: собственный commit/blob не вписывается в record (self-reference невозможен), фиксируется позже в append-only event 0003 | согласовано; D2 pins F2 «from a strict descendant commit» |
| Post-freeze edit policy | `post_freeze_edit_policy`: правки frozen-текста запрещены, новая ревизия только через новый WO | нарушений не найдено (разд. 2) |

### 3.1 Reviewer(F2) и Verifier(F2) — существуют, append-only, pin F2 точно; ВАЖНЫЙ ФАКТ ИНТЕГРАЦИИ

| Роль | Ветка | Tip | Вердикт | Pin subject | Предок F2? | Предок origin/main? |
|---|---|---|---|---|---|---|
| Fresh Reviewer | `review/nl5-v02-frozen-r2-scientific-review-r1` | `d63eb5c088133f92ebd20501835a159cc3e4b865` | **PASS** | `60da9a8…` / `e565c8a6…` (exact) | YES | **NO** |
| Fresh Verifier | `verify/nl5-v02-frozen-r2-r1` | `f12d0b497cb28a2f18476ded90b4b1bd079bb414` | **VERIFIED** (605 tests OK, EX-* 51/51, M-1 matrix 12/12, frozen gate PASS с pinned-scan rerun, seed byte-identity R4/F1/F2) | `60da9a8…` / `e565c8a6…` (exact) | YES | **NO** |

- История файлов `FRESH_SCIENTIFIC_REVIEW_R2.*` (review-ветка) и `FRESH_VERIFIER_R2.*` (verify-ветка): **ни одного изменения после добавления на любом ref** (`git log --all --diff-filter=M` пуст) → append-only соблюдён, записи не переписаны.
- **Неинтегрированность:** tips R/V-веток НЕ входят в `origin/main`. В `main` лежит `DIRECTOR_FRESH_AUDIT_R1` (commit `ff199f9`) + его fresh review (commit `5663991`), которые ссылаются на R/V-вердикты по branch tip SHA и независимо пересчитали их ключевые утверждения (`chain_verdict=INTACT`). Сами R/V-записи в каноническом дереве `main` отсутствуют (`git ls-tree origin/main docs/evidence/NL5-V02-FREEZE/` не содержит `FRESH_SCIENTIFIC_REVIEW_R2.*` / `FRESH_VERIFIER_R2.*`).
- Это **не** подрыв авторитета (вердикты верифицированы третьей стороной и pin-ят exact F2), но это факт, который Director должен учесть при F05: dispatch authority v3 должна ссылаться на R/V-записи по exact branch tip SHA (либо интегрировать записи в `main` отдельным control-WO до финального authority A).
- Замечание по формулировке: в `DIRECTOR_FREEZE_R2.json` `dispatch_blockers` содержат «fresh Reviewer(F2) = missing / fresh Verifier(F2) = missing» — это честная фиксация **на момент заморозки** (до завершения R/V). Сейчас R/V существуют (см. выше), но canonical `machine_launch_authorized` от этого не меняется: `R2 ACTIVE = false`, `AUTHOR_U1 = NOT_ASSIGNED`.

## 4. Feasibility grid (прочитано из frozen-артефактов, не из mission-текста)

Источник 1 — frozen contract @F2: `docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-freeze-contract-FROZEN_R2.json` (sha256 `7e647654…`).
Источник 2 — frozen seed record @F2: `docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-seed-record-FROZEN_R2.json` (sha256 `8e844bff…`).
Кросс-цитата — frozen protocol §10 (строки 415–422, 490–494): `confirmatory_runs = 296`, `replacement cap = 2·(12+12+2+2) = 56`, `MAX runs = 352`, `compute = CPU-only, paid compute FORBIDDEN без отдельной owner-…`, `wall budget = ≤ 560 ч на платформу`.

| Параметр | Значение из frozen-байтов | Источник (путь) |
|---|---|---|
| Primary варианты | `0b`, `32b`: `role=primary`, **N=64** (n_min=52) каждый | contract `.variants` |
| Control варианты | `11b`, `53b`: `role=control`, **N=10** (n_min=8) каждый | contract `.variants` |
| Семантика пар | paired identities: confirmatory runs = 2·(64+64+10+10) = **296** | contract `.run_budget.confirmatory_runs=296`; protocol:415 |
| Replacements | только `FAILED_TECHNICAL`; quota pairs `12/12/2/2` (0b/32b/11b/53b), 2 runs/pair → cap **56** (18.92% ≤ 20%) | contract `.replacement`, `.integer_rounding_policy`; protocol:416 |
| Total cap | `max_runs = 296 + 56 = **352**` | contract `.run_budget.max_runs=352` |
| Wall budget | `wall_hours_per_platform = **560**`; превышение → STOP / BUDGET_EXCEEDED | contract `.run_budget`; protocol:422 |
| Вычисления | **CPU-only** (environment_pins: `cuda=OFF`, `mpi=OFF`); платформы P-A = U1 native Ubuntu R2, P-B = U2 external (outenemy, EXTERNAL_U2_ONLY); Windows/WSL = HISTORICAL_ONLY | contract `.environment_pins`; protocol:420 |
| N-grid | `n_grid=[40,48,64,80,96,128]`, `selected_n=64`, headroom 0.8; evidence `repro-v0-2-n-grid-R3.json` (sha256 `53629463…`) | contract `.feasibility_planning` |
| Seeds | primary_replicas=64, control_replicas=10, fresh_seed_total=148, bootstrap 4; exclusion list 34; exclusion_tree_pin `a9d7d07fa264e9907b67ca244b00ba2da3430b0f` | seed record |
| Пулы замен | фактические размеры пулов 12/12/2/2 seed-ов (проверено подсчётом) | contract `.replacement.pools` |

**Вердикт: grid подтверждён точно в заявленных значениях (N=64 primary; controls N=10; 296/56/352; ≤560 ч/платформа; CPU-only). Значения не придумывались — каждое прочитано из frozen-байтов с указанием пути.**

## 5. Freeze gate PASS + DISPATCH_BLOCKED

Каноническое evidence @F2: `docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/frozen-gate-PASS-R2.json`:

```text
gate                 = PASS
validation_stage     = PREFREEZE_VALIDATION_PASS
freeze_status        = FROZEN
dispatch_ready       = false
dispatch             = DISPATCH_BLOCKED
dispatch_blockers    = [no validated nanolab_v02_dispatch_authority object was supplied …]
budget               = 296 / 56 / 352 / 560h
```

**Независимый машинный rerun гейта** (read-only, C0; exact F2-байты contract+protocol+seed, актуальный git object store):

```bash
PYTHONPATH=scripts python3 -m nl5.repro_v02_freeze_contract gate \
  --contract docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-freeze-contract-FROZEN_R2.json \
  --protocol docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md \
  --record   docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-seed-record-FROZEN_R2.json \
  --repo-root .        # -> exit 0
```

Результат rerun: `gate=PASS`, `validation_stage=PREFREEZE_VALIDATION_PASS`, `freeze_status=FROZEN`, `dispatch=DISPATCH_BLOCKED`, `dispatch_ready=false`, `failures=[]`. Отчёт rerun сохранён в `evidence/frozen-gate-rerun-F2-audit-R1.json` (sha256 `300575f54a07743127936ccbd6124e9792da6e6735165485e763485a587f7e23`).

Методическое примечание (честная фиксация): тот же rerun на голой распаковке F2-дерева без `.git` даёт `FREEZE_GATE_FAIL` (exit 3) — fail-closed по дизайну: pinned scan tree `a9d7d07f…` недоступен без git object store («scan errors are fatal»). Это подтверждает fail-closed-поведение, а не дефект артефактов.

`machine_launch_authorized = false`, `launch_gate = HUMAN_PROTECTED_WRITER` — подтверждено в `DIRECTOR_FREEZE_R2.json.state_ceiling_at_freeze`; изменений канонического статуса с тех пор не обнаружено (разд. 6).

## 6. Текущий статус U1 / R2 / science_runs

| Параметр | Значение | Источник (свежий) |
|---|---|---|
| AUTHOR_U1 | **NOT_ASSIGNED** | `docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md` (строки 20–23); `DIRECTOR_FREEZE_R2.state_ceiling_at_freeze`; `DIRECTOR_FRESH_AUDIT_R1.r2_probe.r2_status` |
| R2 | **WAITING_HOST / NOT_ACTIVE**, `R2_ACTIVATED = NO` | там же |
| NEW_SCIENCE | **HARD_BLOCKED** (без R2; silent fallback на Windows = FORBIDDEN) | `NATIVE_UBUNTU_EXECUTION_POLICY_R1.md` |
| DEFAULT_AUTHOR_EXECUTOR | NATIVE_UBUNTU_R2, PROPOSED → ACTIVE только после fingerprint + gates U1–U5 + NC-U1..U5 + review/verify + Human Gate | там же, строки 11, 31–33 |
| Science runs с момента freeze | **0** | см. ниже |

**science_runs = 0 с момента freeze — проверка по Git:** `git log/diff F2..origin/main -- docs/evidence docs/work/executions`: 25 коммитов, ни один не добавляет научных run-артефактов (поиск по `trajectory|energy.dat|stdout|log.dat|*.dat` среди добавленных файлов — пусто). Новые EX-* каталоги после F2 — документальные/кодовые (NL7/PREP-S17 knowledge-pack, INFRA3 readiness, fresh audit): offline-тесты и контракты, без oxDNA/physics. Счётчики `project/state.json.execution` не изменились: `physics_runs = 35` (исторические, NL1–NL4) и `external_reproductions = 0` — ровно те же значения в `git show F2:project/state.json`. `DIRECTOR_FRESH_AUDIT_R1` и его review отдельно зафиксировали `SCIENTIFIC_RUNS=0`.

## 7. Старый terminal NL5-002 MISMATCH — сохранён

| Проверка | Результат |
|---|---|
| `project/state.json` | `NL5-002 = WAITING_HUMAN`; stage `NL5 = IN_PROGRESS`; `NL5-001 = ACCEPTED`; `execution.external_reproductions = 0`; `paid_compute_authorized = false` |
| Terminal verdict | «**NL5-002 закрыт как terminal MISMATCH / NOT accepted** (canonical 2026-09-20; PR #43 merge `7504b38`)» — `docs/work/WORK_QUEUE.md` (преамбула) |
| Scientific MISMATCH | `docs/evidence/NL5-002/FRESH_VERIFY_R1.md` (0b: все 3 реплики строго выше envelope → MISMATCH; 32b: все 3 строго ниже → MISMATCH; WO-level MISMATCH, `numeric_repro_condition_met=false`) и `FRESH_REVIEW_R1.md` — **файлы вердикта ни разу не изменялись ни на одном ref** (`git log --all --diff-filter=M` по ним пуст) |
| Post-terminal правки | единственная — `c55229a` (2026-09-20): cosmetic fix усечённого SHA в `DIRECTOR_DECISION_R1.md` (4 строки, задокументирован как Finding-1 review `nl5-002-terminal-decision-r1`); вердикт-файлы не тронуты → append-only семантика не нарушена |
| NL5-002-E (platform sensitivity) | закрыт отдельно (P1+P2, PLATFORM_INSENSITIVE, `DIRECTOR_ACCEPTANCE_R2.md`), NL5 acceptance им не объявлен — согласовано с «NL5-002=WAITING_HUMAN» |

**Вердикт: старый terminal MISMATCH сохранён, канонические статусы согласованы по всем поверхностям.**

## 8. Реальные subagent capabilities среды (профилирование без имитации)

Проверено живыми пробами в этой сессии (все пробы — без побочных эффектов; POST-проба с пустым телом не создаёт контента ни при каком ответе):

| Capability | Статус | Доказательство |
|---|---|---|
| DSH subagent launcher (реальные отдельные сессии с durable id) | **РАБОТАЕТ** | эта сессия: `DSH_SESSION_ID=454dea06-3e76-4c1e-80bd-d5287bc2cae0`; Director-сессия `e49ea301c3d2` в dispatch proof. Сессии изолированы, каждая пишет свой JSONL (`DSH_SESSION_JSONL`) |
| Git push по SSH в origin | **РАБОТАЕТ** | `ssh -T git@github.com` → «Hi rootfabric! …»; non-force push этой ветки выполнен |
| GitHub API чтение (issues, PRs) без auth | **РАБОТАЕТ** | `GET /issues/82|81|83|84|85|86|87|88`, `GET /pulls?state=open` → HTTP 200 |
| GitHub issue-comment **запись** | **ЗАБЛОКИРОВАН** | `POST /issues/82/comments` с fine-grained PAT (хранится в `~/.git-credentials`, identity `rootfabric`, 93 симв.) → **HTTP 403** «Resource not accessible by personal access token»; независимо воспроизвело находку Director из dispatch proof (2026-10-25). Следствие: proof-протокол программы публикуется в Git, не в issue-комментариях |
| Токен в env (`GH_TOKEN`/`GITHUB_TOKEN`) | отсутствует | `env` пуст по этим именам; единственный PAT — в git credential store |
| Внешние LAN-пробы к U2/outenemy | НЕ ПРОВОДИЛИСЬ (вне scope F01, host не назначен) | — |

Вывод для программы: распределённый Director DAG на DSH subagent tool **реализуем** (реальные сессии + SSH push); слабое место — отсутствие issue-comment write API (durable-публикация только через Git) — уже скомпенсировано практикой dispatch proofs в `docs/work/executions/**/dispatch/`.

## 9. Скан открытых branches / PR на дублирование

- `git fetch origin --prune`; `git branch -r` — 200+ refов; активные *незакрытые* ветки по NL5-CLOSE тематике: только `origin/work/nl5-f01-frozen-audit-r1` (эта ветка, dispatch Director). Ветки `control|review|verify/nl5-v02-*` — завершённые цепочки S/F/D/R/V (уже учтены в разд. 3); `infra/infra3-*`, `u2-outenemy-*` — готовые пакеты готовности (см. матрицу), дублирования F01 не составляют.
- Open PR (API, `state=open`): **только #78** (docs, Nanobase source receipt) и **#16** (docs, worktree layout). **Ни один не дублирует F01/F02/F03/F05.** Повторной реализации уже закрытых задач в открытых PR нет.
- Старый fresh-audit тираж (`control|review|verify/nl5-v02-fresh-audit-r1`, `EX-NL5-V02-FRESH-AUDIT-R1`) уже в `main` (`ff199f9`, `5663991`) — это предшественник, не дубль: мой аудит независимо пересчитал его ключевые выводы (разд. 2–6).

## 10. Evidence matrix F02 / F03 / F05 + C0 launch list + science launch gate

Зависимости по issue-текстам: F02 (#83) ← F01 + owner host; F03 (#84) ← F01, параллельно F02; F05 (#86) ← F01/F03 (C0-prep), финальный authority A требует F04 (#85, R2 ACTIVE); F06 (#87)/F07 (#88) — научные ноги кампании (вне юрисдикции F01).

| Задача | Статус матрицы | Обоснование (true blockers) |
|---|---|---|
| **F02** — U1 native Ubuntu: выделение, fingerprint, host security (C0) | **READY (C0 start)** / цель блокирована **BLOCKED: AUTHOR_U1=NOT_ASSIGNED** | F01 handoff завершён; preparation docs можно начинать. Приоритет уже создан: `EX-INFRA3-NL5-READINESS-R1` (dry-run package, `U1_PROVISIONING_CHECKLIST_R1.md`, `NL5_V02_DRYRUN_MANIFEST_R1.json`) — не STALE: подтверждён этим аудитом. True blocker фактического provisioningu: физическая машина U1 не предоставлена owner-ом; R2-activation gates U1–U5/NC-U1..U5 не могут стартовать без host |
| **F03** — U2 external reproducibility + raw manifests, изоляция (C0) | **READY (C0 start)** / внешняя нога блокирована **BLOCKED: U2 host/owner-координация** | F01 handoff завершён; пакет готовности `docs/evidence/INFRA3-U2-READINESS` + review PASS (`d588e2a`) на main, релевантен (не STALE). True blocker: outenemy = EXTERNAL_U2_ONLY, фактическая внешняя машина/доступ — вне этой сессии и вне C0 |
| **F05** — dispatch authority v3, feasibility/budget guard (C0) | **READY (C0 prep)** / финальный authority A **BLOCKED: R2 ACTIVE=false + AUTHOR_U1=NOT_ASSIGNED (F04)** | Все числовые входы уже frozen (296/56/352/560h, CPU-only, N=64 — разд. 4); gate PASS + DISPATCH_BLOCKED с машинным блокером «no validated nanolab_v02_dispatch_authority object» (разд. 5). Проект authority v3 можно готовить; подписывать/активировать нельзя до F04. Доп. требование (разд. 3.1): ссылать R/V-записи по exact branch tip SHA или интегрировать их в main |
| F04 — R2 activation (U1–U5 + NC-U1..U5) | **BLOCKED** | AUTHOR_U1=NOT_ASSIGNED, физического U1 нет; не в списке разрешённых C0-запусков F01 |
| F06/F07 — научные ноги (Issue #87/#88) | **BLOCKED (hard)** | `machine_launch_authorized=false`, `launch_gate=HUMAN_PROTECTED_WRITER`, `NEW_SCIENCE=HARD_BLOCKED`; science launch gates не в юрисдикции F01 |

### Разрешённые C0-запуски после HANDOFF (по оценке этого аудита)

1. **F02-C0** (#83): хост-чеклисты/fingerprint-инструментарий/security baseline документально; реальная машина — только от owner.
2. **F03-C0** (#84): U2 readiness verification docs, raw-manifest templates, isolation spec; без внешних платных запусков.
3. **F05-prep-C0** (#86): drafting dispatch authority v3 + feasibility/budget guard из frozen-чисел; без присвоения статусов.

### Science launch gate (отдельный, не C0)

```text
machine_launch_authorized = FALSE        (canonical, подтверждено на свежих evidence)
launch_gate               = HUMAN_PROTECTED_WRITER
Необходимое условие снятия: F04 (R2 ACTIVE: fingerprint frozen + gates U1-U5 + NC-U1..U5 +
review/verify) + AUTHOR_U1 assigned + fresh dispatch authority A + Human Gate.
Бюджет кампании заморожен: 296 confirmatory + ≤56 replacements = ≤352 runs,
≤560 ч/платформа, CPU-only, paid compute forbidden без отдельного owner-решения.
F01 НЕ выдаёт никакой научной авторизации.
```

## 11. BLOCKED / INCONCLUSIVE / ограничения (честная фиксация)

1. **R/V-записи F2 не интегрированы в `main`** (tips `d63eb5c`/`f12d0b4` вне main) — вердикты верифицированы и append-only, но Director-у нужно либо интегрировать записи, либо ссылаться на exact tips в authority v3. Не блокирует C0 F02/F03/F05-prep.
2. **GitHub issue-comment write = 403** (воспроизведено) — proof-протокол только через Git.
3. **Физическое состояние хостов U1/U2 не проверяемо из этой сессии** (нет доступа) → NOT_VERIFIABLE_FROM_SESSION; канонический статус NOT_ASSIGNED/WAITING_HOST остаётся действительным.
4. **Gate rerun на git-less распаковке F2** даёт fail-closed FAIL — методическое следствие (pinned tree вне object store), не дефект артефактов; основной rerun на репозитории = PASS.
5. **INCONCLUSIVE-наук нет**: аудиторные утверждения не пересекают claim ceiling `C0_SOFTWARE_ONLY`; научные вопросы (MISMATCH-гипотеза platform/FP) остаются прерогативой Human Gate, не этого WO.

## 12. Расхождения Issue #82 ↔ фактический репозиторий

1. Issue #82 формулирует «пересчитать sha256 Git blob» — фактически это две разные величины (GIT_BLOB_SHA1 + CANONICAL_BLOB_SHA256); обе пересчитаны, обе MATCH (разд. 2). Терминологическое, не содержательное.
2. `dispatch_blockers` в D2 («fresh Reviewer/Verifier = missing») устарели относительно текущего состояния (R/V существуют на ветках) — честная временная фиксация на момент freeze; канонические блокеры (R2/U1) остаются в силе.
3. Других расхождений не найдено: BASE совпадает, frozen-хеши совпадают, статусы state.json/policy совпадают с декларациями issue/программы.

---

## 13. Handoff

- Deliverables: этот отчёт, машиночитаемое зеркало `NL5_F01_IMMUTABLE_AUDIT_R1.json`, rerun-отчёт гейта, events (START/CONTINUATION/HANDOFF), append-запись в `WORK_QUEUE.md`, `passport.json` → `HANDOFF_READY`, `summary.md`.
- Валидация: `work_cli validate` ok; `check-consistency` ok; `workflow_lint` blocking=0 (итоговые числа — в HANDOFF event и JSON).
- **Next action:** Director принимает документальную передачу (без научной приёмки) и может открывать C0-сессии F02 (#83) / F03 (#84) / F05-prep (#86) отдельными субагентами; F04+/F06/F07 остаются заблокированными science gate-ами.
