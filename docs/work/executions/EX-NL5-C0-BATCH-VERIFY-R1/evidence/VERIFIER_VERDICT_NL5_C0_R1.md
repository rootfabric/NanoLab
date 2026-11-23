# VERIFIER VERDICT — NL5-C0-R1 (exact-head batch verify: F02 + F03 + F05-prep)

```text
RECORD_KIND      = VERIFIER_VERDICT
EXECUTION        = EX-NL5-C0-BATCH-VERIFY-R1
WORK_ORDER       = WO-NL5-C0-BATCH-VERIFY-R1
PROGRAM          = NL5-CLOSE-R1 (issue #81); subjects: #83 (F02) / #84 (F03) / #86 (F05-prep)
ROLE             = VERIFIER (fresh independent DSH session bd0c45d7-6bfd-40c4-8aea-879c9afd546c;
                   not REVIEWER, not any IMPLEMENTER; no reviewer/implementer context)
VERIFY BRANCH    = verify/nl5-c0-batch-f02-f03-f05-r1
BASE             = 3b567ae33f247b182b2ae451d2cc4598a9e76019 (= origin/main at fresh fetch)
SCIENTIFIC RUNS  = 0 (offline documentary verification only)
CLAIM CLASS      = C0_SOFTWARE_ONLY
BATCH VERDICT    = VERIFIED (F02 VERIFIED; F03 VERIFIED; F05-prep VERIFIED;
                   review verdict consistent; negative control PASSED)
```

## 0. Freshness / pinning (метод: fresh checkout без git-истории)

```bash
git fetch origin
git rev-parse origin/main                                  # = 3b567ae33f247b182b2ae451d2cc4598a9e76019 = BASE (не двигался)
git rev-parse origin/work/nl5-f02-u1-host-r1               # = c38ad687d87bfa0c33d69bfee4fe40020d34ba45 == заявленному HEAD
git rev-parse origin/work/nl5-f02-u1-host-r1^{tree}        # = 8dbfeb02311d659c1a961434d3eb0a55502de569 == заявленному TREE
git rev-parse origin/work/nl5-f03-u2-readiness-r1          # = 1831585fa70169c4e473acfe38e9603e45cfe22c == HEAD
git rev-parse origin/work/nl5-f03-u2-readiness-r1^{tree}   # = 8a89d2a446e4f05fcec7a6daade6572ff5a75212 == TREE
git rev-parse origin/work/nl5-f05-dispatch-prep-r1         # = 4c9d8fd30300a2f48504d1b914693f0a66bb3555 == HEAD
git rev-parse origin/work/nl5-f05-dispatch-prep-r1^{tree}  # = 17e2a7141295c9f6e5bf6fc302bc8d977b210a4d == TREE
git rev-parse origin/review/nl5-c0-batch-f02-f03-f05-r1    # = 906d55dffebb606570bb6ff6b3cd17778d314202 == review PASS tip
```

Ни один subject не сдвинулся после REVIEWER PASS → NOT_VERIFIED-инвалидация не требуется.

Fresh-распаковки (аналог fresh clone, БЕЗ git-истории):

```bash
git archive c38ad687… | tar -x -C /tmp/verify-f02
git archive 1831585f… | tar -x -C /tmp/verify-f03
git archive 4c9d8fd3… | tar -x -C /tmp/verify-f05
```

## 1. Harness-валидаторы на свежих деревьях (3/3 PASS)

```bash
cd /tmp/verify-<wo> && PYTHONPATH=<tree>/scripts python3 -m harness.work_cli validate docs/work/executions/EX-…
```

```text
F02 EX-NL5-F02-U1-HOST-R1:        ok=true, errors=[], status=BLOCKED_OWNER_U1, terminal handoff + summary есть
F03 EX-NL5-F03-U2-READINESS-R1:   ok=true, errors=[], status=HANDOFF_READY, post-terminal corrections (event 0004) корректно распознан
F05 EX-NL5-F05-DISPATCH-PREP-R1:  ok=true, errors=[], status=HANDOFF_READY
```

`passport_sha256` от валидатора сверён с `sha256sum` паспортов в свежих деревьях — 3/3 MATCH:

```text
F02: 1477b5bd2ecbf2c3b504e19dfec27223a23fcf126de48dc229db385a7f4267dd
F03: 7c91b2b385ad45b13b20ad25a8cd981a085c89253745d95e714110b14856b5ea
F05: 081f584d471aad78565d2c452119947c1803667e74d0897730f246682c4ca61a
```

## 2. Scope compliance (3/3 PASS)

```bash
git diff --name-only 3b567ae..<subject>
```

```text
F02 : 10 файлов  = docs/work/WO-NL5-F02-U1-HOST-R1.md + docs/work/WORK_QUEUE.md + EX-NL5-F02-U1-HOST-R1/**  → только allowed paths
F03 : 13 файлов  = docs/work/WO-NL5-F03-U2-READINESS-R1.md + docs/work/WORK_QUEUE.md + EX-NL5-F03-U2-READINESS-R1/** → только allowed paths
F05 : 11 файлов  = docs/work/WO-NL5-F05-DISPATCH-PREP-R1.md + docs/work/WORK_QUEUE.md + EX-NL5-F05-DISPATCH-PREP-R1/** → только allowed paths
project/*.json, scripts/**, tests/**, frozen-пути — не затронуты ни в одном subject.
```

WORK_QUEUE (numstat): F02 `1 0`; F03 `2 0` (1 запись + 1 пустой separator); F05 `1 0`. Существующие строки не менялись (0 deletions везде).

## 3. Frozen integrity (PASS)

```bash
F2 = 60da9a846511265a8ac7564da088c3d74cb073f0; git rev-parse F2^{tree} = e565c8a6cee9e829fac14008ebc9c2ea1609931d
git diff --name-only F2 <subject> -- <protocol> <contract> <seed>   # ПУСТО для всех 3 subjects и для origin/main
git show <subject>:<path> | sha256sum                                # canonical SHA-256
git rev-parse <subject>:<path>                                       # git blob SHA-1
```

| Артефакт | canonical SHA-256 (= DIRECTOR_FREEZE_R2.json) | blob SHA-1 | F02 | F03 | F05 |
|---|---|---|---|---|---|
| protocol `docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md` | `2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d` | `4835719622bae49a8e8b480536a482b4b222d408` | MATCH | MATCH | MATCH |
| contract `…/repro-v0-2-freeze-contract-FROZEN_R2.json` | `7e6476544e82af73d5d7e0672666ece99bf4d499a0da30645b02886bcdc45b3a` | `d6a9ccde4d1dadf42d1a8cd9b88faa02646cf70b` | MATCH | MATCH | MATCH |
| seed `…/repro-v0-2-seed-record-FROZEN_R2.json` | `8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28` | `0164e0e3f5dda6dbf63174df3730b1bd921d2c76` | MATCH | MATCH | MATCH |

Итого 9/9 canonical SHA-256 + 9/9 blob SHA-1 == `docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R2.json` (subject_head 60da9a8… / subject_tree e565c8a6… в нём совпадают с моим `rev-parse`). Diff frozen-путей F2→каждый subject и F2→origin/main пуст.

## 4. SHA-256 контроль ключевых evidence-файлов (CHECKOUT_SHA256)

Заявленных self-значений SHA-256 для этих 9 файлов ни в passports/summaries subjects, ни в review-вердикте нет (проверено grep'ом 64-hex по всем EX-деревьям и review-ветке) — external claim отсутствует, поэтому зафиксирован baseline: `CHECKOUT_SHA256` байтов свежих деревьев, каждый сверен с SHA-256 Git-объекта (`git show <subject>:<path> | sha256sum`) — 9/9 MATCH (свежее дерево байт-в-байт == закоммиченные байты):

| Subject | Файл | CHECKOUT_SHA256 == GIT_OBJECT_SHA256 |
|---|---|---|
| F02 | evidence/U1_HOST_ELIGIBILITY_R1.json | `cc34ae99245678be48fcc492aca67483b9e9faa9b4c58a0a75923e60a04709e7` |
| F02 | evidence/U1_HOST_ELIGIBILITY_R1.md | `f42b1b144beb443dea351afab6ed24ff22d75b183e33b30bb969e17646f0f315` |
| F03 | evidence/U2_READINESS_R1.json | `3440e116595c3b20782f354b52bcf026dc35e300773f2040957319023447a241` |
| F03 | evidence/U2_READINESS_R1.md | `4b4d9e362972bf5c0a68fb98532880c00133d3e6ccb09de937f24225e6f0e5c0` |
| F03 | evidence/U2_LIVE_HOST_OBSERVATION_R1.json | `2c27a99bfb36742dd93f09bd899a905c3b359e4879abd6dd7fa0971b41ca03d1` |
| F03 | evidence/U2_LIVE_HOST_OBSERVATION_R1.md | `1660b254fe2031c1498d1d7c9447d358f5fa6474e61fb2e979317c8f1e6f6b50` |
| F05 | evidence/DISPATCH_READINESS_R1.json | `3c799cb8cbd222575af498a98fc63a227b5fb1f107774bf9d72e532415e56301` |
| F05 | evidence/DISPATCH_READINESS_R1.md | `a2ccc3f718fb323610ce81332416281a558eedb8ceea89b5d47444149ebf1c1c` |
| F05 | evidence/budget-ledger-R1.json | `4e7cfbc079db9897decdc37fa7d0c58bce1a84d6cbf1d35c3d787aedd1c3464b` |

Проверяемые заявленные хеши из evidence/summary — все сходятся:

```text
HG_B_OWNER_DECISION_R1.json @ origin/main: git blob  61d1491233aeb2537f9800d6183def5b8fb0c8e0 == claim F05/батч-ревью
                                           sha256   b68dd341a5671d6314da3fcf6d32fae54f88b385b7b5a631edb07b0f6f49d2c9 == claim
F03 L-04 engine binary (read-only host check):
  sha256sum ~/nanolab/cache/oxdna-build-r2-u2/bin/oxDNA = 6effd00a09628895fac48b8b4c60c4dc82557d05910da6bebe276b8355126b78 == claim; size 3380728 == claim
```

## 5. Claims-vs-evidence пересчёты (независимо, для consistency с review)

```text
F2 commit меняет ровно 8 файлов; 8/8 blob SHA-1 SAME F2 vs origin/main           # базис F03-claim «9/9» (см. F03-NF-2)
seed recount из frozen seed record: seeds 64/64/10/10=148 (== fresh_seed_total),
  bootstrap 4, pools 12/12/2/2=28, skips 10/11/10/10=41, всего 180 distinct,
  все уникальны, пересечений seed↔pool 0                                          # == claims F03/F05
budget arithmetic: 296 = 148×2; 56 = 28×2; max 352; per-platform 176;            # == budget-ledger-R1.json
  HG_B approved_parameters.wall_hours_per_platform = 560, confirmatory 296,
  replacement cap 56, max_runs 352, quotas 12/12/2/2, decision=APPROVED           # == claims F05/review
checks_log (DISPATCH_READINESS_R1.json /seed_identity_replay): ровно 85 записей, все ok:true, checks_failed=[]  # == «85/85»
launch gates: machine_launch_authorized=false (F03 ×3, F05 ×8 упоминаний), AUTHOR_U1=NOT_ASSIGNED,
  R2=WAITING_HOST / NOT_ACTIVE, scientific_runs=0 (F02 evidence verdict-поля подтверждены)       # == review launch_gates_preserved
F05-F-1 компенсация существует: scripts/nl5/repro_v02_freeze_contract.py L1900
  `hashlib.sha256(raw).hexdigest() != art_digest` (+ L1928/L1935 on-disk binding)  # == review claim ~L1893-1905
```

## 6. Review-вердикт consistency (origin/review/nl5-c0-batch-f02-f03-f05-r1 @ 906d55d)

`BATCH_REVIEWER_VERDICT_NL5_C0_R1.{md,json}` прочитаны на review-ветке. Сверка его claims с моими независимыми результатами:

```text
HEAD/TREE 3 subjects          : 3/3 совпадают (review == мои rev-parse == passport)
Вердикты F02/F03/F05 = PASS   : подтверждаю (мои статусы: BLOCKED_OWNER_U1 / HANDOFF_READY / HANDOFF_READY == review passport_status_at_subject)
work_cli validate ok:true ×3  : воспроизведено
scope 3/3 allowed paths       : воспроизведено
frozen integrity 9/9          : воспроизведено
WORK_QUEUE +1/+2/+1, 0 del    : воспроизведено (numstat)
Findings список ПОЛОН         : F02-NF-1, F03-NF-1, F03-NF-2, F03-NF-3, F03-NF-4, F05-NF-1 — все 6 независимо подтверждены:
  F02-NF-1: dispatch proof 0000 (строка 9) действительно содержит «F01 HANDOFF = ACCEPTED (documentary)»
  F03-NF-1: git show 39e9aec -- events/0001,0002 -> единственное изменение «actor_role: EXTERNAL-PREFLIGHT-IMPLEMENTER → IMPLEMENTER» (оба файла; больше никаких правок)
  F03-NF-2: F2 меняет 8 файлов (не 9); 8/8 SAME vs main; 9-я запись — DIRECTOR_FREEZE_R2.json, добавлен потомком F2
  F03-NF-3: WORK_QUEUE F03 numstat 2 0 (запись + пустой separator)
  F03-NF-4: actor_id «nl5-f03-u2-preflight-r1» во всех 4 events (≠ «u2-readiness» naming)
  F05-NF-1: все 3 event-файла закоммичены единственным коммитом 4c9d8fd (git log -- <event> = 1 commit каждый)
Расхождения с review-вердиктом: НЕ ОБНАРУЖЕНЫ.
```

## 7. NEGATIVE CONTROL (обязательный tamper-тест) — PASSED

```bash
cp /tmp/verify-f05/…/evidence/DISPATCH_READINESS_R1.json /tmp/nc_f05_DISPATCH_READINESS_R1.json
baseline: sha256 = 3c799cb8cbd222575af498a98fc63a227b5fb1f107774bf9d72e532415e56301
tamper:   1 байт — "scientific_runs": 0 -> 1 (offset 352)
after:    sha256 = 764b722a97f75a83090804ac11e9230c56a9480ac1150150d28c072929c34fc0
verdict:  diff vs expected != 0 -> TAMPER DETECTED
```

Метод hash-сверки чувствителен к одиночной байтовой правке — negative control сработал. (Тест выполнен только на /tmp-копии; subject-деревья и worktree не изменялись.)

## 8. Вердикты

```text
F02  (origin/work/nl5-f02-u1-host-r1        @ c38ad687d87bfa0c33d69bfee4fe40020d34ba45 / tree 8dbfeb02311d659c1a961434d3eb0a55502de569) = VERIFIED
F03  (origin/work/nl5-f03-u2-readiness-r1   @ 1831585fa70169c4e473acfe38e9603e45cfe22c / tree 8a89d2a446e4f05fcec7a6daade6572ff5a75212) = VERIFIED
F05  (origin/work/nl5-f05-dispatch-prep-r1  @ 4c9d8fd30300a2f48504d1b914693f0a66bb3555 / tree 17e2a7141295c9f6e5bf6fc302bc8d977b210a4d) = VERIFIED
BATCH = VERIFIED (3/3 VERIFIED; review verdict консистентен; negative control PASSED; расхождений с review нет)
```

Границы: это exact-head verification документальных C0 handoff'ов. VERIFIED ≠ научный accept и ≠ R2 activation:
`machine_launch_authorized=false`, AUTHOR_U1=NOT_ASSIGNED, R2=WAITING_HOST/NOT_ACTIVE, merge в main = Human Gate.
Любой новый коммит на subject-ветках инвалидирует этот вердикт для нового HEAD.
