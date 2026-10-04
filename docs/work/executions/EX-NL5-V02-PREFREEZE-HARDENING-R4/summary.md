# EX-NL5-V02-PREFREEZE-HARDENING-R4 — summary

## Result

```text
VERDICT = READY_FOR_REVIEW
CLAIM_CLASS = C0_SOFTWARE_ONLY
SCIENTIFIC_RUNS = 0
CANDIDATE = PRE-DATA / NOT FROZEN
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED
HG-B = WAITING_OWNER (addendum §8 добавлен в proposal)
MERGE = WAITING_HUMAN
HOSTED_CI_RUN = NOT_RUN (gh не аутентифицирован; draft PR — следующий актор)
```

F1–F4 из focused audit 2026-10-03 исправлены на exact R3 subject с полным
сохранением истории; confirmatory identities R3 сохранены бит-в-бит.

## Base / product subject

```text
BASE_MAIN  = 87298b36431045474d3784adf5cee8c9a64d0fc9
BASE_TREE  = db19f9dd265873f99c995aa279ae5e0c5b21c330
BRANCH     = work/nl5-v02-prefreeze-hardening-r4
HANDOFF_HEAD = <см. event 0004 / финальный отчёт — exact SHA перед handoff>
```

История ветки (append-only, без force/squash):
START `c205f14` → merge handoff `1077bdf` → merge R3 subject (PR #48 @
`ce13f0e`) `9826f27` → implementation `962cc24` → CONTINUATION `834b57c` →
(финальные control-коммиты до этого summary).

## Findings → repairs (детали в REPAIR_MAP_R1.md)

```text
F1 freeze contract   = FIXED — authoritative machine contract (revision r4),
                       fail-closed, dispatch-bypass невозможен (negative tests)
F2 collision scan    = FIXED — pinned immutable tree a9d7d07, exit 0/1/иное
                       (SCAN_ERROR), exact path allowlist; 176 fresh = CLEAN
F3 replacement stream= FIXED — frozen pools 12/12/2/2 от cursor 75/76/21/21
                       (никогда raw N+1); ledger: attempt id уникальны,
                       FAILED_TECHNICAL-only, quota exhaustion без расширения
F4 integer policy    = FIXED — ceil-nmin-floor-replacement-pairs-v1:
                       N_min 52/8, cap 56 runs, max_runs 352; wording
                       смягчён; HG-B proposal addendum §8 (owner delta)
```

R3→R4 candidate delta — явная таблица изменений в
`docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md` (revision R4, PRE-DATA);
научные параметры (δ=0.5, N, grid, paired scheme, wall 560h) не менялись;
`max_runs` ужесточён 356→352 (производная одной политики, не расширение).

## Validation (реальная поверхность)

```text
python3 -m unittest discover -s tests -t .        → Ran 513 tests OK
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root . → ok
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .         → blocking 0
PYTHONPATH=scripts python3 -m harness.work_cli validate (все EX-*)   → ok
```

## Track B — native Ubuntu R2 (отдельный трек, не смешан с R4)

```text
HOSTNAME = outenemy
HOST_ELIGIBLE_U1 = NO (hostname в forbidden_hostnames; outenemy = EXTERNAL_U2_ONLY)
AUTHOR_U1 = NOT_ASSIGNED
R2_STATUS = WAITING_HOST / NOT_ACTIVE; R2_ACTIVATED = NO
U1..U5 = WAITING_HOST; NC-U1..NC-U5 = WAITING_HOST (guard не обходился)
FINGERPRINT_SHA256 = см. track-b-r2-host/host-check-NOT_ELIGIBLE_R1.json
```

Хост иначе native-класса (bare-metal kernel signature, virt=none, ext4,
systemd degraded) — ineligible ИСКЛЮЧИТЕЛЬНО по hostname role rule.
Environment quirk (глобальный pip-пакет `scripts` затеняет repository
namespace package; рабочая инвокация `PYTHONPATH=scripts python3 -m r2.cli …`)
задокументирован без системных изменений.

## Связанная работа (не дубль, требует секвенирования)

`origin/repair/nl5-acceptance-policy-r4-power-gate-r1` — другой «R4»:
decision-power gate repair по WO-NL5-ACCEPTANCE-POLICY-R4-POWER-GATE-R1
(START 2026-10-01, только административные коммиты, dormant). Обе ветки
меняют `scripts/nl5/**` и candidate doc — при integration потребуется
явный merge/rebase с Repair Map. Эта задача его не дублирует и не отменяет.

## R4.1 — fresh Reviewer R1 FIX_REQUIRED → repair (2026-10-04, append-only)

Fresh independent Reviewer R1 (`REVIEWER_VERDICT_R1`, branch
`review/nl5-v02-prefreeze-hardening-r4-r1` head `2729b9c`) подтвердила факты R4 и
вынесла FIX_REQUIRED: M-1..M-4 blocking + m-1 minor. Repair R4.1 выполнен на ветке
`repair/nl5-v02-prefreeze-hardening-r4-r1` (от tip `1964bb5`, reviewer branch
интегрирована `--no-ff`, merge `61aa6eb`); детали — `REPAIR_MAP_R1_1.md`, START
marker — event `0004`. Итог:

```text
M-1 dispatch authority   = FIXED — PREFREEZE_VALIDATION_PASS отделён от DISPATCH_READY;
                           committed PRE-DATA package = DISPATCH_BLOCKED (evidence
                           r4-1-dispatch-blocked-PRE_DATA_R4_1.json); positive fixture
                           только SYNTHETIC TEST FIXTURE ONLY
M-2 replacement replay   = FIXED — bit-exact replay + replacement_pool_sha256 /
                           record_r4_sha256; R3 digest eb4ab3f8… = provenance
M-3 collision skip proof = FIXED — machine-bound scan manifest (41/41 skips proven,
                           148+28 accepted CLEAN) + rerun pinned scan: fabricated
                           skip => FREEZE_GATE_FAIL
M-4 pair ledger          = FIXED — pair-level one-shot replacement, both legs scheduled
m-1 equivalence wording  = FIXED — equivalence interval (±δ·s_eff), standard TOST H0/H1
Валидация                = 557 tests OK (было 513); check-consistency ok; workflow_lint
                           blocking 0; work_cli все EX-* ok; hosted CI = NOT_RUN
```

Статусы НЕ меняются: CANDIDATE = PRE-DATA / NOT FROZEN; SCIENTIFIC RUNS = 0;
HG-B = WAITING_OWNER; R2 = WAITING_HOST / NOT_ACTIVE; AUTHOR_U1 = NOT_ASSIGNED;
NL5 = IN_PROGRESS; external_reproductions = 0; NL6-001 = LOCKED.

## R4.2 — fresh Reviewer R2 FIX_REQUIRED → narrow repair (2026-10-04, append-only)

Fresh independent Reviewer R2 (`REVIEWER_VERDICT_R2`, branch
`review/nl5-v02-prefreeze-hardening-r4-1-r2` head `2be5c8f`) подтвердила закрытие
R1 M-2/M-3/m-1 (= PASS) и вынесла FIX_REQUIRED по двум blocking + одному minor
дефекту новой machinery: M-5 (Git/provenance binding dispatch authority),
M-6 (атомарность pair replacement), m-2 (snapshot safety `open_pair`). Narrow
repair R4.2 выполнен на ветке `repair/nl5-v02-prefreeze-hardening-r4-r2`
(от tip R4.1 `7406b5a` = reviewed subject; reviewer branch интегрирована
`--no-ff`, merge `5ea37a4`); детали — `REPAIR_MAP_R2.md`, START marker — event
`0006`. Итог:

```text
M-5 Git/provenance       = FIXED — schema_version 2: subject_head обязан быть реальным
                           Git commit, rev-parse <head>^{tree} == subject_tree; каждый
                           authority record несёт source_commit/path/git_blob_sha1/
                           canonical_sha256/record_kind/issuer_class и привязан к одному
                           freeze-evidence commit; байты читаются из Git object database,
                           НЕ из mutable worktree; frozen_subject_binding связывает
                           contract/protocol/seed-record как exact Git blobs, байт-в-байт
                           с валидируемыми входами; trust ceiling: DISPATCH_PRECONDITIONS_
                           RECORDED + machine_launch_authorized=false + launch_gate=
                           HUMAN_PROTECTED_WRITER (DISPATCH_AUTHORIZED не существует);
                           fixture — test-only на реальном временном synthetic Git repo
M-6 atomic replacement   = FIXED — двухфазная транзакция: PHASE 1 валидирует все будущие
                           записи без мутаций (pair state, quota/cursor, replacement pair
                           id свободен, seed не owned, формат+глобальная уникальность
                           обоих attempt id, различие ног), PHASE 2 коммитит под rollback
                           guard (snapshot/restore всех структур); после любого rejection
                           state структурно идентичен (новый state_snapshot() helper)
m-2 snapshot safety      = FIXED — open_pair возвращает независимый snapshot (legs
                           копируется); ledger/pair getters тоже независимы
Валидация                = 580 tests OK (было 557; +23 net: DispatchAuthorityGitBindingTest
                           11, PairReplacementAtomicityTest 13, минус переработанные);
                           check-consistency ok; workflow_lint blocking 0; work_cli все
                           49 EX-* ok; prefreeze committed package = PREFREEZE_VALIDATION_
                           PASS / DISPATCH_BLOCKED (evidence r4-2-prefreeze-validation-
                           PASS-R4_2.json, package digests unchanged); hosted CI = NOT_RUN
```

Принятые поверхности R4/R4.1 не переделывались: M-2 replacement replay, M-3 collision
proof, equivalence/TOST wording = PASS у Reviewer R2; код этих поверхностей не менялся;
committed package (contract/record/manifest) байт-в-байт тот же. Параметры дизайна без
изменений: N = 64/64/10/10; N_min = 52/52/8/8; replacement quotas = 12/12/2/2;
replacement cap = 56; max_runs = 352; δ = 0.5; paired design; R3 confirmatory identities.

Статусы НЕ меняются: CANDIDATE = PRE-DATA / NOT FROZEN; SCIENTIFIC RUNS = 0;
HG-B = WAITING_OWNER; AUTHOR_U1 = NOT_ASSIGNED; R2 = WAITING_HOST / NOT_ACTIVE;
NL5 = IN_PROGRESS; external_reproductions = 0; NL6-001 = LOCKED.

## Next action

```text
NEXT_ACTOR = fresh independent SCIENTIFIC/PROTOCOL REVIEWER
NEXT_ACTION = review exact R4.2 HEAD/TREE (см. event 0007 / REPAIR_MAP_R2.md) на
              предмет M-5 + M-6 + m-2 и сохранения границ R4/R4.1; затем — только
              при PASS — fresh exact-head Verifier, draft PR (TR-PR hosted CI),
              Director readiness record; merge = Human Gate. R2: ждать реального
              owner-provided U1 (не outenemy). Verifier до Reviewer PASS не запускать.
```
