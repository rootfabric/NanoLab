# Repair map — mission-wide run_id

Основание: independent integration review выявил MEDIUM defect, подтверждённый интегратором. Published base: `61790c05a738d43a9be276b08d7be00d0758ea04`. Existing owner mission `WO-ATOMISTIC-PRODUCT-R1`; новых simulations для исправления не требуется.

Failure: exclusive mkdir защищал только `output_root/run_id`; другой output_root позволял повторно использовать FAILED ID внутри того же mission. Ledger хранил run_dir и reservation_id, но не проверял run_id.

Root cause: идентификатор исполнения проверялся в файловом namespace каталога результата, а budget authority уже была общей для mission. Каноническое место исправления — `scripts/atomistic/budget.py:reserve`, внутри существующего flock. Не требуется новый scheduler.

Implementation: `api.run` передаёт явный run_id в `budget.reserve`; reserve проверяет соответствие basename каталога, затем все сохранённые ledger rows независимо от terminal status, до добавления reservation и до worker launch. Новые rows содержат run_id. Для legacy rows без run_id используется `Path(run_dir).name`; миграция старых записей не выполняется. Duplicate отказ сохраняется стандартным blocked manifest без новой reservation/списания budget.

Entry points и sibling paths: CLI → api.run → budget.reserve; web → api.run → тот же shared ledger. Прямые unit-test calls `reserve` обновлены к явному параметру. Physics worker, numerical thresholds, model, historical pilot protocol и raw bytes не изменяются.

Validation: mock-only FAILED reuse в двух output roots с отсутствующим вторым Popen и byte-for-byte неизменным ledger; legacy fallback без миграции; два одновременных запроса того же ID резервируют ровно один slot и один полный budget. Existing backend/web suites должны оставаться зелёными; real integration explicit skip. Scientific impact — отсутствует для исторического pilot, но новый source требует independent affected review/verification на объединённом immutable subject.

Remaining risk: аварийная RUNNING reservation по прежнему fail-closed до операторского аудита; это отдельный предусмотренный stop condition, не причина сбрасывать IDs. Run ID uniqueness ограничена текущим mission ledger: смена operator-selected nonGit mission root не создаёт новой grant.
