# Atomistic product + FLOW — независимый integration Reviewer R2

Технический вердикт: **PASS** на exact subject ниже. **P-REV-01, P-REV-02, P-REV-03 CLOSED**. Это совокупный результат substantive source review `61790c0` и bounded delta recheck финального repair; исходный FAIL сохранён. Material/scientific conclusion остаётся **NOT_EVALUATED / NOT_SCIENTIFICALLY_VALIDATED**, P0 **OPEN**. Финальные actual UI/Verifier checks выполняются отдельно; этот отчёт их не подменяет и не разрешает merge.

## Exact subject и независимость

- Финальный reviewed HEAD: **`71bc62102cc36bf49b04d40d81d3070d87cccad6`**.
- Финальный reviewed TREE: **`f86af90728797541594396ac0bef0964d9f8dd28`**.
- Предыдущий integration subject: `61790c05a738d43a9be276b08d7be00d0758ea04`, tree `5414a12b970b40238eea0a702103df838af30df9`.
- Canonical comparison base: `3b567ae33f247b182b2ae451d2cc4598a9e76019`.
- Reviewed FLOW repair: `ff35e283985f1eed1bacda9a3b3be191782e3700`; `scripts/harness/review_impact.py` после него не менялся. Исходный FLOW-REV-01 уже CLOSED отдельным независимым recheck.
- Reviewer: **`/root/flow_review`**, отдельная REVIEWER session, не автор исходного product или repairs. Worktree `/workspace/scratch/48cb7a65c9c0/NanoLab-product-review`, detached exact HEAD.
- Shared host/container `8988315495f9`, Python `3.12.14`. Отдельный физический host/external reproduction не заявляются.
- Product files Reviewer не менял; после проверок `git status --porcelain` пусто.

Preserved baseline evidence, SHA-256:

| Файл | SHA-256 |
|---|---|
| `product-review-report.md` | `61323a6f53e4489a6989cf9fc2edc8fc01ea5d9f3c035077f2758d11b7eb7354` |
| `product-review-adversarial.py` | `5836965498055f95f49e555cd6cb1825ebbb9cb48d81d34abccd2664424bf21b` |
| `product-review-adversarial.log` | `1756803b8eb57f0537c3f0ed140f2304ea8b91d3d182f9077137c9fc7f1a6b41` |

## Закрытие findings

**P-REV-01 CLOSED.** `LocalApp.export` читает исходные байты из server-generated run directory; проверяет совпадение пути/run ID/manifest с активным результатом, exact allowlist всех десяти artifacts, symlinks, размеры и SHA-256. ZIP включает эти десять файлов и исходный manifest без JSON reserialization. Независимый тест использовал **копию опубликованного actual Cu run**: все **11** файлов побайтово совпали, каждая manifest SHA-256/size совпала, export → extract → `api.verify_run` PASS. Tamper, symlink, unknown entry и подмена run_dir отвергнуты. Ни исходный real artifact, ни его manifest не переписаны.

**P-REV-02 CLOSED.** `budget.reserve(run_dir, run_id, ...)` проверяет соответствие basename ID и mission-wide уникальность **под тем же flock**, до резервирования слота/worker. Existing rows без `run_id` читаются через basename сохранённого run_dir; миграция и удаление history отсутствуют. Независимый cross-root failed-ID test получил один mocked launch; второй вызов заблокирован, ledger bytes неизменны. Копия настоящей legacy row отвергает повтор без её изменения. В race восьми writers с одним ID получено **1 reservation / 7 duplicate rejections**, одна ledger row. Production mission grant не использован.

**P-REV-03 CLOSED.** Friction step исправлен на `0.0001`. Независимая exact-rational проверка всех **12** default numeric HTML inputs подтверждает min/max и отсутствие stepMismatch. Это source/static recheck; фактическую native browser/actual UI проверку проводит отдельный executor.

Других blocking findings в reviewed integration/repair нет. Authority/roadmap/material claims не повышены ремонтом. Сохраняются explicit engineering limits, раздельные P0/P1 software/material statuses и historical NL/FLOW/Task Bus gates.

## Команды и результаты

| Команда / проверка | Результат |
|---|---|
| `git checkout --detach 71bc62102cc36bf49b04d40d81d3070d87cccad6` и `git rev-parse HEAD HEAD^{tree}` | exit 0, совпадают с subject выше |
| `git diff 61790c05a738d43a9be276b08d7be00d0758ea04..HEAD -- scripts/atomistic tests/test_atomistic* docs/atomistic/UI.md` | exit 0; просмотрен весь bounded delta |
| `NANOLAB_REAL_ATOMISTIC_TEST=0 PYTHONPATH=scripts python3 -m unittest tests.test_atomistic_backend tests.test_atomistic_web -v` | **exit 0; 31 tests: 30 PASS, 1 explicit real-MD SKIP**, 8.136 s |
| `PYTHONPATH=scripts python3 /workspace/scratch/48cb7a65c9c0/product-review-repair-adversarial.py` | **exit 0; 6 independent checks PASS**, 0.044 s |
| `git diff --quiet ff35e283985f1eed1bacda9a3b3be191782e3700..HEAD -- scripts/harness/review_impact.py` | exit 0, ранее проверенный FLOW repair неизменен |
| `sha256sum` baseline report/script/log | совпадают с preserved hashes выше |
| `git status --porcelain` | пусто |

Независимый код: `/workspace/scratch/48cb7a65c9c0/product-review-repair-adversarial.py`. Логи: `/workspace/scratch/48cb7a65c9c0/product-review-repair-adversarial.log`, `/workspace/scratch/48cb7a65c9c0/product-review-repair-tests.log`.

Полный repository suite здесь не повторялся: его выполняет отдельный Verifier. Substantive review baseline уже проверил plan/authority, validation/security, worker limits/cancel, ledger/restart и происхождение 32Cu/51metrics/11frames sample от pinned source `599ba8d1f089d74dc5f67a33011cba020f6df57a`. Sample остаётся историческим evidence исходного producer subject; accounting/export repairs не превращают его в actual run нового exact HEAD. Финальный fresh actual run и UI receipt должны указывать собственный producer subject и общий ledger.

## Неблокирующее замечание

В `docs/atomistic/UI.md` указан CLI `python -m atomistic.cli verify-run <directory>`, тогда как существующая команда — **`verify`**. Это LOW documentation typo; исправить при ближайшей публикации evidence/docs, без изменения source/physics. Технический PASS не зависит от опечатки команды в тексте.

Reviewer actual MD runs=0, production ledger mutations=0, paid compute=0, product edits=0, merge=0. Claim ceiling — **SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED**. Independent Verifier, Director и действующий Human merge gate сохраняются.

**Одно next action:** Director объединяет этот technical PASS с отдельными final exact-subject Verifier/actual UI receipts и публикует candidate evidence/status; material acceptance не объявляется.
