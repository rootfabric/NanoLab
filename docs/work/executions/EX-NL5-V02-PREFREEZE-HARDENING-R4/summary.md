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

## Next action

```text
NEXT_ACTOR = fresh independent SCIENTIFIC/PROTOCOL REVIEWER
NEXT_ACTION = review exact HEAD (см. HANDOFF event) на предмет F1–F4 + scope
              scientific claims; затем fresh exact-head Verifier; затем draft
              PR (TR-PR hosted CI) и Director readiness record; merge =
              Human Gate. R2: ждать реального owner-provided U1 (не outenemy).
```
