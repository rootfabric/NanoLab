# EX-INTEGRATION-NL5-C0-R1 — summary

Work Order: [WO-INTEGRATION-NL5-C0-R1](../../WO-INTEGRATION-NL5-C0-R1.md). Director record: [NL5_C0_INTEGRATION_RECORD_R1](../../../control/NL5_C0_INTEGRATION_RECORD_R1.md). Program: NL5-CLOSE-R1 (#81). Risk MEDIUM, claim C0_SOFTWARE_ONLY, scientific runs = 0.

## Что сделано

На fresh `main@ddf8a25cdd95a1598338816f6a585ffdde1e0f2a` (tree `80b4668d9d289f7696d06d39ed9d21d44c4f0acf`) собран один C0 candidate `integration/nl5-c0-r1` из семи exact subjects в порядке карты `NL5_C0_INTEGRATION_MAP_R1.md`: F01 `c7c5be6`, F02 `9b24f93`, F03 `1831585`, F05 `4c9d8fd`, batch review `906d55d`, batch verify `9be1964`, integration map `8585c06` (merge-only head `7096923`, tree `0f6d13a7`). 58 добавленных путей blob-идентичны subjects; 0 удалений и 0 изменений существующих путей. Единственный конфликт `docs/work/WORK_QUEUE.md` разрешён в форме FLOW-R1 (побайтово = main); факты шести append-строк сохранены в `summary.md` включённых execution directories и в history subject-веток.

## Проверки

| Gate | main | candidate |
|---|---|---|
| JSON syntax | 1591 ok | 1626 ok |
| consistency | ok | ok |
| executions | 72 ok | 79 ok, errors 0 |
| workflow lint | 0 | 0 |
| unittest (Windows, не авторитетно) | 1054 ran, 73 failing methods (env) | 1054 ran, то же множество, **0 новых** |

Authoritative gate — hosted CI H0 на PR #98 (5 checks) на финальном HEAD. Локальные логи: `scratch/lead-2026-11-24/` (вне Git).

## Exact subject / commands

- Branch `integration/nl5-c0-r1`, PR https://github.com/rootfabric/NanoLab/pull/98.
- Commands: `git merge --no-ff <subject-sha>` ×7; `git diff --name-only --diff-filter=U` (только `docs/work/WORK_QUEUE.md`); `git checkout --ours -- docs/work/WORK_QUEUE.md`; `python -m harness.batch_validate json|executions --root .`; `python -m harness.cli check-consistency|drive --root .`; `python -m harness.operations --root . --format json|markdown`; `python -m harness.workflow_lint --root .`; `python -m unittest discover -s tests -t .`.
- Card `project/operations/INTEGRATION-R1.json`: READY/DIRECTOR → WAITING_HUMAN/HUMAN, blocker `NL5_C0_INTEGRATION_MERGE_PENDING`.

## Границы и открытые риски

Merge в main — Human Gate владельца (один на 7 subjects). Научная приёмка NL5, frozen F2, AUTHOR_U1 (NOT_ASSIGNED), R2 (WAITING_HOST), authority A и launch gates не меняются; новые Reviewer/Verifier для неизменных subjects не требуются (FLOW-R1 §3/§6), интеграция получает полный интеграционный CI. Открытый PR #97 уже исправляет stale cards PR #96 — здесь не дублировалось, чтобы не конфликтовать; порядок merge #97/#98 выбирает владелец. Внутри merge commits author name локальной машины (`YGlamazdin`), email тот же, что в истории main; содержимое subjects от этого не зависит.

## Next action (одно)

Владелец принимает merge-решение по PR #98; после merge — `drive`/`operations` на fresh main и перевод `INTEGRATION-R1` в `DONE` следующим C0 package.
