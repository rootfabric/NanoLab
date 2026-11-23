# EX-NL5-C0-BATCH-REVIEW-R1 — Summary

## Что это

Независимый batch documentary review трёх C0-handoff программы NL5-CLOSE-R1 (issue #81):
F02 (issue #83), F03 (issue #84), F05-prep (issue #86). Свежая REVIEWER-сессия без контекста
имплементёров (DSH subagent `b8eca5d9-8ad0-419d-8092-58da4d471487`). Научных запусков 0;
код не менялся; subjects не писались.

## Вердикт

```text
F02  work/nl5-f02-u1-host-r1        @ c38ad687d87bfa0c33d69bfee4fe40020d34ba45 = PASS
F03  work/nl5-f03-u2-readiness-r1   @ 1831585fa70169c4e473acfe38e9603e45cfe22c = PASS
F05  work/nl5-f05-dispatch-prep-r1  @ 4c9d8fd30300a2f48504d1b914693f0a66bb3555 = PASS
BATCH = PASS (blocking findings: 0; non-blocking: 6)
```

## Ключевые независимые пересчёты (см. полный список в вердикте)

- Exact HEAD/TREE трёх subjects = 3/3 match паспорт; tips не двигались; `origin/main` = BASE.
- Frozen F2=60da9a8: diff по protocol/contract/seed пуст на всех subjects и на main; canonical
  SHA-256 2658ee3e…/7e647654…/8e844bff… = 9/9 match `DIRECTOR_FREEZE_R2.json`.
- F02 факты: hostname=`outenemy` ∈ `forbidden_hostnames` (EXTERNAL_U2_ONLY); `~/.ssh/config`
  ABSENT; env allocation пуст; → BLOCKED_OWNER_U1 корректен, self-accept нет.
- F03 claims: engine binary `~/nanolab/cache/oxdna-build-r2-u2/bin/oxDNA` sha256
  `6effd00a…5126b78` / 3380728 B — точное совпадение; F2-блобы 8/8 SAME на main; L-03 диски
  (df: 96%, 19G free) — честно зафиксирован MEASURED_FAIL_ON_THRESHOLD.
- F05 claims: seed recount по frozen record 148/4/28/41 = 180 unique (0 overlap); checks_log
  85/85 ok; budget 296=148×2, 56=28×2, ≤352, 176/platform, 560h (HG-B b68dd341… пересчитан),
  storage 21.08 GB ≤ 21.2 GB (P1 basis 105.9/119.8 MB пересчитан); adversarial 7/8 логичен,
  gate-тесты воспроизведены (pristine PASS / prose-tamper PASS → F05-F-1 реален / machine-tamper
  FAIL exit 3); компенсация F05-F-1 существует (canonical_sha256 binding, ~L1893–1905).

## Findings (все non-blocking)

- F02-NF-1: «ACCEPTED (documentary)» про F01 в Director dispatch proof — терминология, не self-accept.
- F03-NF-1: events 0001/0002 `actor_role` отредактирован в 39e9aec (append-only по букве; факты/таймстемпы нет).
- F03-NF-2: «9/9 files changed by F2» = фактически 8 файлов SAME + 1 запись SAME_DIR.
- F03-NF-3: WORK_QUEUE append = запись + blank separator.
- F03-NF-4: actor_id `…u2-preflight…` vs WO-нейминг `…u2-readiness…`.
- F05-NF-1: START event закоммичен финальным коммитом (durable START не публиковался до work).

## Статусы/gates

Ни один subject не объявил ACCEPTED / R2_ACTIVE / научную авторизацию;
`machine_launch_authorized=false` всюду; authority A не создан.

## Next action

Один: Director dispatch свежего Verifier по тем же exact HEAD/TREE, затем Human Gate.
F04 заблокирован до реального U1; U2 storage L-03 требует remediation/accept-risk до F07.

## Файлы

- `evidence/BATCH_REVIEWER_VERDICT_NL5_C0_R1.md` (+ `.json`) — полный отчёт с командами
- `events/0001-review-started.json`, `events/0002-review-verdict-pass.json`
- `docs/work/WORK_QUEUE.md` — одна append-строка
- `passport.json` — status REVIEW_PASS
