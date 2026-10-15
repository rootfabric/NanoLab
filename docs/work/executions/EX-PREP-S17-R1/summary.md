# EX-PREP-S17-R1 — Implementation handoff

## Identity / scope

- Base: `main @ 32d3c6840341ad3954d5001235a3cc35b8ca0e01` (tree `474249da8fee669c85aa763274e33a16d4293f40`).
- Working branch: `work/prep-s17-r1` (isolated worktree `/home/rdpuser/NanoLab/prep-s17`).
- Result: **PREPARATORY WORK IMPLEMENTED / REVIEW REQUIRED**; risk MEDIUM, claim ceiling C0_SOFTWARE_ONLY; достигнутый уровень источника — **`PINNED_IMPORT_VERIFIED`** (структура файлов; НЕ симуляция, НЕ воспроизведение).
- New scientific runs: **0**; U1 activation: **not performed**; E5: **not started**; human scientific gate: **not bypassed**; `project/state.json`: **unchanged**; frozen artifacts: **untouched**.

## Deliverables

- `docs/research/S17_PREP_AUDIT_R1.md` — source registry + rights/provenance report + механизм (B4) + preliminary MechanicalComponentSpec (ports UNVERIFIED/UNKNOWN) + missing inputs + черновая граница будущего HIGH WO NL6-001/E5.
- `docs/research/S17_KNOWLEDGEPACK.json` — machine-readable KnowledgePack v1 instance (20 manifest positions, exact pins/digests, права, observables, UNKNOWN-дисциплина), валиден по контракту.
- `scripts/knowledge_pack/contract.py` — KnowledgePack v1 fail-closed валидатор (claim ceiling, rights gating, explicit-UNKNOWN, manifest integrity).
- `scripts/knowledge_pack/import_validation.py` — детерминированная импорт-валидация oxDNA-пар (строгие парсеры переиспользованы из `hinge_family`).
- `tests/test_knowledge_pack.py` + `tests/test_knowledge_pack_import.py` — 37 тестов: позитивные + negative controls (повреждённые digest/структуры, claim inflation, vendoring без прав, unknown поля, count mismatch).
- `docs/work/executions/EX-PREP-S17-R1/evidence/s17-import-validation-R1.json` — реальная валидация NE/NE_NB/nNE (parse OK, counts match, chain integrity OK, deterministic re-import, negative control однобайтового повреждения → fail-closed).
- `docs/work/executions/EX-PREP-S17-R1/evidence/s17-source-sha256sums-R1.txt` — SHA-256 всех 12+ скачанных source-файлов (метаданные; сами байты в Git НЕ хранятся — REFERENCE_ONLY).
- `docs/work/WO-PREP-S17-R1.md` — bounded Work Order паспорт задачи.

## Ключевые факты аудита (независимая сессия, живые HTTP-проверки)

- Статья: open access CC BY 4.0; driver = транскрипционный (HT–T7RNAP + dsDNA-шаблон), follower = пассивная origami; в MD воздействие задано внешней 16 pN constant-trap силой; химическое топливо НЕ симулируется.
- Nanobase structure 196: все 12 файлов получены и верифицированы; NE.top/NE.dat — готовая минимальная импортируемая пара.
- Zenodo 8248808: 46.17 GB проинвентаризированы (name/size/MD5), не скачивались; trajectory decimation 1/20; GPU-недетерминизм задокументирован источником.
- `sulcgroup/hinges`: лицензии НЕТ ⇒ REFERENCE_ONLY; анализ-скрипты research-grade (hard-coded paths), алгоритмы наблюдаемых задокументированы (SVD-угол, ×0.85 nm, equipartition K).
- UNKNOWN сохранены как UNKNOWN: `polymerase_positioning.txt`, рецепт `linked.top`/`first_conf.dat`, точный пин oxDNA, 23 °C-инпуты, entry-метаданные Nanobase, provenance `driver_*/follower_*`, доступность smFRET-датасета.

## Validation (exact HEAD см. evidence-map)

- `python3 -m unittest discover -s tests -t .` → **675 tests OK** (base 638 + 37 новых).
- `PYTHONPATH=scripts python3 -m harness.cli check-consistency` → ok:true, tasks:19.
- `PYTHONPATH=scripts python3 -m harness.workflow_lint` → blocking:0.
- `work_cli validate` всех `docs/work/executions/EX-*/` → 0 FAIL (включая этот EX).
- Pack instance проходит `knowledge_pack.contract.validate_pack` (тесты закрепляют).

## Known limits / риски

- Валидатор контракта — scoped prototype v1; развитие контракта = новая ревизия, не молчаливое расширение.
- Импорт-валидация подтверждает структуру файлов, не физику; пары не запускались в oxDNA.
- Ports/index-mapping UNVERIFIED: до отдельной верификации нельзя строить assembly поверх этих индексов.
- Route LITERATURE_TO_MECHANISM (PR #54) здесь учитывается как proposed: после его merge возможна лёгкая сверка формулировок (отдельный follow-up, не блокер этого WO).

## Next action

Fresh independent Reviewer + fresh exact-head Verifier ветки `work/prep-s17-r1`, затем Human Gate merge.

## КОРРЕКЦИЯ R2 (2026-10-14, append-only; не ретро-редакция разделов выше)

Fresh independent Reviewer (review `review/prep-s17-r1` @ `3370be06`) = **FAIL / 1 blocking + 6 minor** на exact R1 subject `d9b7efd`/`0abed1d`. Blocking подтверждён исполнителем: реализация-субъект R1 `3cf7818` содержал 668 тестов (638 base + 30), а разделы выше заявляли 675/37 и ссылались на `tests/test_knowledge_pack_import.py`, НЕ добавленный в git (ошибка `git add`; файл существовал на диске и локально проходил). Repair R2:

- Реальный import-test файл добавлен в дерево (+7 тестов); валидатор ужесточён (minor-3 schema_version-bool reject; minor-4 `verify_manifest` root-containment; minor-5 non-UTF-8 → `ImportValidationError`; minor-6 linkage-чувствительный structural digest через `topology_linkage_sha256`).
- Evidence пересоздан как `evidence/s17-import-validation-R2.json` (schema_version 2, supersedes R1; R1 сохранён как historical; структурные digest'ы обновлены — c227e0b585983820… / 5e7610a84bed1881… / 20c3912671280b71…).
- Pack: размер `pull_release23.zip` исправлен 20 669 125 082 → 20 691 250 829 (minor-1, MD5 был верен).
- Errata (minor-2): timestamp события 0002 (18:05:00Z) был проставлен позже фактического порядка работ, чем 0003 (17:39:12Z); события неизменяемы — errata фиксируются здесь и в event 0005.
- Точные числа финального head: **679 tests OK** (638 base + 41: 32 в `test_knowledge_pack.py`, 9 в `test_knowledge_pack_import.py`).
- Passport не ретро-редактируется: omission `tests/test_knowledge_pack_import.py` в `allowed_paths` зафиксирована как erratum R1 здесь и в event 0005.
