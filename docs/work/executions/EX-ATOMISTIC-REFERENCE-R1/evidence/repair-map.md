# Reference prep: bounded review repair

Независимый Reviewer /root/reference_review при проверке draft обнаружил:

1. Источник/теоретический DOI и publisher URLs можно было заменить несогласованными значениями с пересчитанным sources digest, а PACKAGE_VALID сохранялся. Причина: лишь общая HTTPS/path validation там, где R1 определяет один конкретный upstream/source. Fix owner reference_protocol: exact R1 locator checks и adversarial tests; без сетевого доступа валидатора и без утверждения о повторной загрузке remote bytes.
2. PROTOCOL.md содержит алгоритм/stop/conclusion details, но отсутствующий файл не препятствовал PACKAGE_VALID. Fix owner reference_protocol: привязать фактический текст к manifest digest/size и проверить его наличие/целостность, отрицательные tests удаления/изменения/unsafe path.

Canonical fix location: scripts/atomistic/reference.py, protocol.json и tests/test_atomistic_reference.py. Sources facts, scientific thresholds и historical science не меняются. Independent Reviewer повторяет affected adversarial checks; Verifier запускает весь CI на опубликованном subject. Physics runs=0. Это первый bounded repair; прошлые отрицательные observations сохраняются данным record и независимым report.

Дополнение той же причины source semantics: изменение source_uncertainty.basis сразу в manifest и factual extract на ошибочное «95%-й доверительный интервал K^T» с обновлёнными хешами не отклонялось. Fix: проверенный fixed-R1 смысл probable error K^S не должен превращаться в uncertainty K^T; отрицательный тест согласованной подмены обоих файлов. Фактические scientific values не изменяются.
