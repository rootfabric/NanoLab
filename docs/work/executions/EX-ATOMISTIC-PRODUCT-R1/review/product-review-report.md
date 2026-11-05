# Atomistic product + FLOW — независимый integration Reviewer R1

Вердикт: **FAIL / FIX_REQUIRED** для exact subject ниже. Подтверждены три bounded MEDIUM дефекта первого пользовательского сценария. Scientific conclusion: **NOT_EVALUATED**; material validation **OPEN / NOT_SCIENTIFICALLY_VALIDATED**. Исправления не требуют новых MD-запусков.

## Subject, scope, независимость

- Integration HEAD: **`61790c05a738d43a9be276b08d7be00d0758ea04`**.
- Integration TREE: **`5414a12b970b40238eea0a702103df838af30df9`**.
- Canonical comparison base main: `3b567ae33f247b182b2ae451d2cc4598a9e76019`.
- Reviewed FLOW repair dependency: `ff35e283985f1eed1bacda9a3b3be191782e3700`, tree `9f54fc28c2c954c2e55ff706e6baac9fb8e280af`. Ранее FLOW-REV-01 закрыт независимым bounded recheck, исходный FAIL сохранён; integration delta не меняет исправленный helper.
- Reviewer identity: **`/root/flow_review`**, отдельная REVIEWER session, не автор product, roadmap, UI или repair.
- Worktree: `/workspace/scratch/48cb7a65c9c0/NanoLab-product-review`, detached exact HEAD; после проверок `git status --porcelain` пусто.
- Host/container: `8988315495f9`, Python `3.12.14`; host и filesystem общие с другими исполнителями. Отдельный физический host / external material reproduction не заявляются.

Прочитаны актуальные AGENTS, WO-ATOMISTIC-PRODUCT-R1, product-plan/state, roadmap, authority changes, model card/pilot protocol/adapter/UI docs; просмотрены все новые `scripts/atomistic/` и affected tests. Учитывались ранее прочитанные PROJECT_CONTROL, HARNESS_CONTROL, development/review/security правила. Проверены новые P0–P6 зависимости, разграничение historical NL и engineering demo, API validation, фиксированный worker subprocess/resource limits, request/job handling, budget/restart/cancel/no-overwrite, сохранение/provenance/model pin и lineage опубликованного Cu example. Product files Reviewer не редактировал.

## P-REV-01 — MEDIUM: скачанный ZIP не сохраняет проверяемый результат

**Место:** `scripts/atomistic/web.py:120–129`, в частности повторная сериализация на строках 123–124 и запись четырёх JSON на 127–128.

Экспорт создаёт новые байты config/trajectory/metrics, но вкладывает исходный manifest с хешами исходных файлов. На реальном опубликованном run `cu-emt-demo-r1-001` все три повторно сериализованных JSON имеют **другие SHA-256** (исчезает завершающий newline). Также отсутствуют семь файлов, на которые manifest ссылается: environment, numerical-control, protocol, relaxation.json/log, report.md, worker.log.

Независимый read-only roundtrip: загрузить JSON опубликованного run в LocalApp result, вызвать `export()`, распаковать ZIP во временный каталог и вызвать `api.verify_run`. Получено **`RunError: artifact integrity failure: config.json`**; проверка имён дополнительно находит все семь пропусков. Даже присутствующие данные не соответствуют вложенному receipt. В документации UI сокращённый экспорт оговорён, но core product contract обещает сохранение bundle с provenance; текущий ZIP непригоден для переноса и проверки результата.

**Исправление:** формировать ZIP из исходных точных байтов completed run directory после integrity verification, включая manifest и все перечисленные им файлы. Не пересчитывать JSON и scientific evidence. Добавить тест реального сохранённого bundle: export → extract → `verify_run` PASS, точное соответствие SHA-256/size и полный набор файлов. Invalid/tampered artifact должен явно блокировать export.

## P-REV-02 — MEDIUM: failed run ID можно повторить сменой output_root

**Место:** `scripts/atomistic/api.py:172–176` и `scripts/atomistic/budget.py:55–67`.

No-overwrite проверяется только существованием `output_root/run_id`. Общий mission ledger хранит path/reservation, но не проверяет уникальность run ID. Поэтому после failed attempt `first-output/reused-id` вызов с тем же ID в `second-output/reused-id` получает новую reservation и запускает worker повторно в той же mission. Это противоречит forbidden `reusing failed run ID` в product-plan и README; receipt больше не однозначно определяется run ID.

Независимое воспроизведение **без MD и без использования настоящей квоты**: временный mission ledger, два output roots, одинаковый `reused-id`, `Popen` заменён на `OSError('NO MD: mock launch failure')`. Получено **2 launch attempts и 2 ledger rows** вместо отказа второго запуска до subprocess.

**Исправление:** под общим существующим flock проверять mission-wide run ID до reservation/subprocess и сохранять его в ledger. Существующую 1/8 row поддержать без удаления: вывести её ID из `Path(run_dir).name`. Повтор любого already-used ID, включая FAILED/CANCELLED, должен блокироваться независимо от output_root; новый уникальный ID допускается в прежнем бюджете. Добавить cross-root/restart regression; не сбрасывать старую ledger history.

## P-REV-03 — MEDIUM: исходная форма не принимает собственное значение friction

**Место:** `scripts/atomistic/static/index.html:17`, input `id="friction"`.

У поля `value=0.01`, `min=0.0001`, `step=0.001`. Относительно step base min значение даёт `(0.01−0.0001)/0.001 = 99/10`, не целое число. Поэтому native HTML constraint validation отмечает default как stepMismatch и блокирует обычный submit первого сценария. Browser QA central session сообщил этот failure; Reviewer независимо подтвердил исходные атрибуты и точную рациональную арифметику. Reviewer сам новый browser/MD run не выполнял.

**Исправление:** согласовать step с поддерживаемым backend диапазоном/default (например, 0.0001). Проверить native `checkValidity()` исходной формы и отправку default config до mocked backend; не ограничиваться POST-тестом, обходящим форму.

## Проверки и результаты

| Проверка / команда | Результат |
|---|---|
| `git worktree add --detach ../NanoLab-product-review 61790c05a738d43a9be276b08d7be00d0758ea04` | exit 0, exact checkout |
| `git rev-parse HEAD HEAD^{tree}` | exit 0, SHA/TREE совпадают |
| `NANOLAB_REAL_ATOMISTIC_TEST=0 PYTHONPATH=scripts python3 -m unittest tests.test_atomistic_backend tests.test_atomistic_web -v` | **exit 0; 25 tests: 24 PASS, 1 explicit real-MD skip**, 6.609 s |
| `PYTHONPATH=scripts python3 -m atomistic.cli verify examples/atomistic/runs/cu-emt-demo-r1-001` | exit 0; исходный completed run integrity PASS |
| `PYTHONPATH=scripts python3 /workspace/scratch/48cb7a65c9c0/product-review-adversarial.py` | **exit 1; 4 independent checks: 2 PASS, 1 FAIL, 1 ERROR**, оба отрицательных результата соответствуют P-REV-01/02 |
| `git rev-parse 599ba8d1f089d74dc5f67a33011cba020f6df57a^{tree}` | `d1e1359ba0e06230aeed0197f2b548f6e9b7f1d1`, совпадает с receipt |
| `git diff 599ba8d1f089d74dc5f67a33011cba020f6df57a..HEAD -- scripts/atomistic/api.py scripts/atomistic/budget.py scripts/atomistic/worker.py scripts/atomistic/integration.py scripts/atomistic/cli.py` | пустой delta; physics-producing source сохранён |
| SHA-256/size всех шести `adapter_sources` против source Git blobs и current modules | все совпадают |
| Frozen project/state + goals/catalog против reviewed FLOW repair | побайтово неизменны; historical NL acceptance не расширен |
| Shared production mission ledger, read only | 1 COMPLETED, charged 0.6553803189999599 s; SHA-256 `7116b39382df4c645abf298f0788a7d4463a27a39d5d72db0d65c775f60491ef` |
| `git status --porcelain` | пусто |

Независимый adversarial script: `/workspace/scratch/48cb7a65c9c0/product-review-adversarial.py`; его log: `/workspace/scratch/48cb7a65c9c0/product-review-adversarial.log`. Affected unit log: `/workspace/scratch/48cb7a65c9c0/product-review-tests.log`. Все mutation checks использовали temporary roots и mock Popen; production ledger не изменялся.

## Положительные результаты и границы

Published actual artifact подтверждён: **32 Cu atoms, 51 metric rows, 11 frames, final step 50**, coordinates меняются; relaxation converged и potential energy уменьшилась; заранее заданный same-engine derivative control PASS. Исходный code/protocol checkpoint `599ba8d` закоммичен в 10:46:53 UTC, до started_utc 10:47:27; receipt сохраняет clean tree и точные module/model digests. Это readback существующего расчёта, не независимый новый physics run.

API отклоняет неизвестные поля/материалы/модели/units, NaN/Inf, bool/int mismatches, oversized structures/steps/frames, unsafe paths/IDs и overwrite в одном root. Worker фиксирован, shell/произвольный model path отсутствуют; заданные dependency versions и frozen EMT/config digests сверяются до расчёта. CPU/address-space/file-size limits и single numerical thread заданы. Cancellation/failed evidence/no retry проверены mocks. Постоянный mission ledger сохраняет count и блокирующую active reservation при restart; sequential grant и count exhaustion работают. HTTP loopback/Host/Origin/token/size/path allowlists проходят affected suite. Прямого remote execution interface не найдено.

Roadmap честно разделяет P0 material validation, software delivery и историческую DNA acceptance. EMT не выдаётся за validated EAM/DFT или подтверждение свойств меди; краткая траектория и same-engine derivative check не объявлены доказательством устойчивости/равновесия. P0 остаётся OPEN, future P4–P6 условны. Scoped engineering exception не активирует U1/U2, NL5/E5 либо Task Bus. Product state пока IN_PROGRESS_PENDING_INDEPENDENT_REVIEW — self-acceptance не заявлен.

Других blocking findings после substantive проверки нет. Полный repository suite/CI выполняет отдельный Verifier; ранее проверенный FLOW helper повторно полностью не аудировался. Reviewer actual MD runs=0, paid compute=0, host mutations=0, merge=0, external messages=0.

**Одно next action:** завершить единый bounded repair P-REV-01/02/03 и передать его неизменный exact HEAD/TREE тому же независимому Reviewer для delta recheck, затем отдельному Verifier для финальной проверки интеграции.
