# WO-INTEGRATION-NL5-C0-R1 — один C0 candidate для верифицированных материалов NL5-CLOSE-R1

START: 2026-11-23T14:33Z. Owner request (сессия 2026-11-24): «проверь состояние проекта; продолжи». Operational card `project/operations/INTEGRATION-R1.json` (READY, actor DIRECTOR); функция интегратора по `docs/control/FLOW_THROUGHPUT_R1.md` §6; карта `docs/control/NL5_C0_INTEGRATION_MAP_R1.md` (Director record 2026-10-26).

Base: `main@ddf8a25cdd95a1598338816f6a585ffdde1e0f2a`, tree `80b4668d9d289f7696d06d39ed9d21d44c4f0acf`.
Branch: `integration/nl5-c0-r1`. Risk MEDIUM: docs-only C0 records + одна карточка очереди; код, протоколы, harness не меняются. Claim C0_SOFTWARE_ONLY.

Scope: собрать в одном candidate уже проверенные exact subjects в порядке карты — F01 `c7c5be6edbcdb5a304705ff6d53863fa735d7d0c`, F02 `9b24f93092e917cb6064d5c7723e5b4d1f05d67d`, F03 `1831585fa70169c4e473acfe38e9603e45cfe22c`, F05 `4c9d8fd30300a2f48504d1b914693f0a66bb3555`, batch review `906d55dffebb606570bb6ff6b3cd17778d314202`, batch verify `9be1964b7860853931fa69d70c8f42a7f053b536`, integration map `8585c063a82971f9c9ce788bc1dfd173528631e5`; проверить целостность (каждый добавленный путь blob-идентичен своему subject), зависимости и действующее разрешение; прогнать интеграционные CI gates; опубликовать одну merge-рекомендацию (PR). Разрешение конфликтов — только `docs/work/WORK_QUEUE.md` (см. карту), прочие конфликты = STOP.

Allowed paths: `docs/work/WO-INTEGRATION-NL5-C0-R1.md`, `docs/control/NL5_C0_INTEGRATION_RECORD_R1.md`, `project/operations/INTEGRATION-R1.json`, `docs/work/executions/EX-INTEGRATION-NL5-C0-R1/**` + пути, добавляемые merges. Запрещено: правка исторических events/evidence subjects, frozen F2, `project/state.json`, код/тесты/harness, force push, direct push main.

Budget: локальные C0 gates (JSON, consistency, executions, workflow lint, unittest differential против fresh main) и до 4 H0 CI jobs <=15 минут. Scientific runs=0, paid compute=0. Ни один subject не меняется; новый Reviewer/Verifier для неизменных subject не требуется (FLOW-R1 §3/§6), интеграция получает полный интеграционный CI.

Stop conditions: pin mismatch любой ветки; конфликт вне `WORK_QUEUE.md`; любая blob-расходимость; новые failing tests относительно fresh main; G1–G4 не PASS. Merge в main — Human Gate владельца; этот WO не выдаёт launch/merge authority и не меняет NL5 acceptance, AUTHOR_U1, R2 или authority A.
