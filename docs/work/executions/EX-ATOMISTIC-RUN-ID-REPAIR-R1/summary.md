# Mission-wide run ID repair — handoff

Published base `61790c05a738d43a9be276b08d7be00d0758ea04`. Repair code/source **58173bdd70c42263b96dff30d849446cdb79f2fd**, TREE **560fcf5ed89b08fd2776c84cac9f0847e0f909c6**. Branch `repair/atomistic-mission-run-id-r1`. [Repair map](repair-map.md) описывает confirmed finding и canonical fix.

`api.run` передаёт explicit run_id в shared `budget.reserve`. Проверка duplicate выполняется под тем же flock до active/count checks, до добавления row и до subprocess. FAILED, CANCELLED, COMPLETED и RUNNING IDs заняты в пределах mission независимо от output_root. Новая запись сохраняет run_id; старая запись без этого поля читается через basename run_dir без миграции. Rejected повтор не резервирует слот и не меняет сохранённый расход. Blocked manifest остаётся для диагностики.

Команда `PYTHONPATH=scripts python3 -m unittest tests.test_atomistic_backend tests.test_atomistic_web -v`: **27 PASS + 1 explicit real MD SKIP**, 28 tests, 6.662 s, exit0. [Validation receipt](validation.json) фиксирует результаты. Три добавленных regression tests: FAILED ID в двух output roots с assert_not_called для второго Popen и byte-for-byte неизменным ledger; legacy row без run_id; concurrent duplicate reserve с единственным slot/budget. Все tests используют временный ledger и mock worker; **0 actual simulations**, production ledger не затронут.

Scope source: только `scripts/atomistic/{api,budget}.py`, backend tests. Physics worker, source model, thresholds и historical pilot raw не изменены. Исторический pilot сохраняет свой exact source/protocol claim; новый source требует review/verification, а прошлый run не объявляется выполненным новым кодом. Scientific outcome **NOT_EVALUATED**; P0/E6 не принимаются.

Один следующий шаг: интегратору объединить repair с UI export/friction fixes, опубликовать immutable candidate и вернуть его независимым Reviewer/Verifier для affected checks. Implementer не выносит acceptance verdict.
