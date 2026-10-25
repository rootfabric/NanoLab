# EX-NL5-C0-BATCH-VERIFY-R1 — summary

**WO:** WO-NL5-C0-BATCH-VERIFY-R1 (программа NL5-CLOSE-R1, issue #81; subjects #83/#84/#86). **Роль:** VERIFIER, реальная свежая DSH-сессия `bd0c45d7-6bfd-40c4-8aea-879c9afd546c` (не REVIEWER, не имплементёры). **Класс:** C0_SOFTWARE_ONLY, SCIENTIFIC_RUNS = 0.

## Вердикт

```text
BATCH = VERIFIED
F02        VERIFIED  (origin/work/nl5-f02-u1-host-r1        @ c38ad687d87bfa0c33d69bfee4fe40020d34ba45 / tree 8dbfeb02…)
F03        VERIFIED  (origin/work/nl5-f03-u2-readiness-r1   @ 1831585fa70169c4e473acfe38e9603e45cfe22c / tree 8a89d2a4…)
F05-prep   VERIFIED  (origin/work/nl5-f05-dispatch-prep-r1  @ 4c9d8fd30300a2f48504d1b914693f0a66bb3555 / tree 17e2a714…)
REVIEW PASS (origin/review/nl5-c0-batch-f02-f03-f05-r1 @ 906d55d) — консистентен, расхождений нет
NEGATIVE CONTROL — PASSED
```

## Итог (всё воспроизведено независимо на fresh git-archive деревьях без git-истории)

- **Freshness:** `git fetch origin`; `origin/main = BASE 3b567ae…` не двигался; ни один subject не сдвинулся после review; HEAD/TREE 3/3 == заявленным.
- **Валидаторы:** `work_cli validate` ok:true, errors:[] ×3 (статусы BLOCKED_OWNER_U1 / HANDOFF_READY / HANDOFF_READY); passport_sha256 3/3 пересчитаны и совпали.
- **Scope:** `git diff --name-only 3b567ae..<subject>` ×3 — только allowed paths; WORK_QUEUE numstat 1/0, 2/0, 1/0, удалений 0.
- **Frozen integrity:** F2 = `60da9a8…` / tree `e565c8a6…`; diff frozen-путей F2→каждый subject и F2→origin/main пуст; canonical SHA-256 protocol/contract/seed 9/9 == `DIRECTOR_FREEZE_R2.json` (2658ee3e… / 7e647654… / 8e844bff…), blob SHA-1 9/9.
- **SHA-256 контроль:** для 9 ключевых evidence-файлов external self-claims нигде нет (проверено grep) → зафиксированы baseline `CHECKOUT_SHA256`, каждый 9/9 == SHA-256 Git-объекта; все существующие заявленные хеши сошлись: HG_B `61d14912`/`b68dd341`, engine binary `6effd00a…`/3380728 (read-only host check), паспорта.
- **Пересчёты:** F2 меняет 8 файлов (8/8 blob-SAME vs main); seed recount 148+4+28(12/12/2/2)=180 distinct unique, skips 41; budget 296/56/352/176, wall 560h == HG_B; checks_log 85/85 ok; F05-F-1 компенсация существует (repro_v02_freeze_contract.py L1900).
- **Review consistency:** все claims `BATCH_REVIEWER_VERDICT_NL5_C0_R1` воспроизведены; findings полный список, каждый подтверждён first-hand: F02-NF-1 (dispatch proof «ACCEPTED (documentary)»), F03-NF-1 (39e9aec менял в events 0001/0002 только actor_role), F03-NF-2 (8 файлов, не 9), F03-NF-3 (+1 запись +1 separator), F03-NF-4 (legacy actor_id), F05-NF-1 (все events одним коммитом 4c9d8fd). Расхождений нет.
- **Negative control:** 1-байтовый tamper (`scientific_runs` 0→1, offset 352) в /tmp-копии F05 `DISPATCH_READINESS_R1.json`: sha256 `3c799cb8…` → `764b722a…` ≠ expected → TAMPER DETECTED. Метод чувствителен; tamper только в /tmp.

## Границы

VERIFIED ≠ научный accept и ≠ R2 activation: `machine_launch_authorized=false`, AUTHOR_U1=NOT_ASSIGNED, R2=WAITING_HOST/NOT_ACTIVE; merge в main = Human Gate. Любой новый коммит на subject-ветках инвалидирует вердикт для нового HEAD. Читающие операции по subject/review-веткам, main, project/*.json, scripts/**, tests/** — read-only; записи только в своём EX и одна append-only строка WORK_QUEUE.

## Валидация

`work_cli validate` этого EX — ok; `check-consistency` ok; `workflow_lint` blocking=0; `json.tool` strict parse OK для всех новых JSON (финальные прогоны — после публикации).

## Next action

Director: принять VERIFIED по batch F02+F03+F05-prep и вынести merge этих веток в main на Human Gate. F04 остаётся заблокирован до реального выделения U1 (owner actions A1–A6); U2 storage L-03 (96% used, порог 80%) требует remediation или owner accept-risk до F07.
