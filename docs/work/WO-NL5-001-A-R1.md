# WO-NL5-001-A-R1 — Release contract: schema v0.1 + права + интерфейс воспроизведения

## Паспорт

- Work Order: `WO-NL5-001-A-R1` (canonical Work ID `NL5-001-A`; маршрут и декомпозиция A..D — [POST_MVP_DEVELOPMENT_ROUTE_R1](../control/POST_MVP_DEVELOPMENT_ROUTE_R1.md) Phase B).
  **Коррекция (repair R1, F-B5/F-A2):** исходная ссылка на несуществующий
  `docs/control/POST_MVP_EXECUTION_PROGRAM_R1.md` удалена; durable источник
  планирования — POST_MVP_DEVELOPMENT_ROUTE_R1 (Phase B, декомпозиция A..D).
- Checkpoint: `NL5 / NL5-001-A`
- Base: `control/post-mvp-route-r1 @ e05793cc8ff03b3b1af2d81b38e39d82cd7527d6` (PR #37 head; DOC/CODE-подготовка до Gate 0 разрешена программой §2 — merge-конфликтов с PR #37 нет, только новые файлы)
- Branch: `work/nl5-001-a-release-contract-r1`
- Risk: `MEDIUM` — создаёт нормативный контракт будущего release; без физики, без canonical state
- Claim: `C0_SOFTWARE_ONLY`

## Цель

Заморозить контракт component library v0.1 ДО сборки библиотеки (NL5-001-B):

1. Component card schema v0.1 (нормативный JSON Schema-документ + stdlib-executor + lint CLI).
2. Layout release-пакета, policy версионирования и неизменяемости карточек.
3. Форматы `RIGHTS.json`, `CITATION.cff`, `RELEASE_MANIFEST.json`, `VERSION`.
4. Reproduction interface (контракт `reproduce` из пакета без внутренних знаний репозитория).
5. License options memo для owner-решения D2 (решение НЕ принимается агентом).

## Allowed paths

```text
docs/work/WO-NL5-001-A-R1.md
docs/work/executions/EX-NL5-001-A-R1/**
docs/release/RELEASE_CONTRACT_V0_1.md
docs/control/OWN_LICENSE_OPTIONS_MEMO_R1.md
schemas/**
scripts/release/**
examples/release/**
tests/test_release_contract.py
```

## Forbidden scope

- `project/state.json`, `project/plan.json`, `docs/ROADMAP.md`, `docs/work/WORK_QUEUE.md`, checkpoint catalog (territory PR #37 / control change);
- physics/runtime/analysis code; любые прогоны oxDNA; E5/E3-R2 активация;
- сборка реальной библиотеки (это NL5-001-B);
- выбор лицензии владельцем вместо владельца (только memo);
- изменения CI workflow (линт запускается в unittest-гейте);
- merge/direct push в `main` и в `control/post-mvp-route-r1`.

## Требуемые изменения (Definition of Done для A)

1. Схема карточки — машинно-читаемый нормативный артефакт; lint исполняет схему + семантические правила; fail-closed на неподдерживаемых конструкциях.
2. UNKNOWN-политика: неизвестное значение — явный `UNKNOWN`; отсутствие проверки не кодируется как PASS (совместимо с `docs/DATA_CONTRACTS.md`).
3. Digest-политика: sha256/git-blob-sha1/size с паттернами; `RELEASE_MANIFEST` верифицируется перерасчётом дайджестов.
4. Семейство публикуется как одно семейство с вариантами; правило честного гэпа `74b` (KNOWN_GAP/NOT_MEASURED) выражено в схеме и в примере.
5. Права: `REFERENCE_ONLY`/`DOWNLOAD_ON_RUN` требуют `upstream_repo` + `pinned_commit` + `durable_cache=FORBIDDEN` (совместимо с G1 decision и LICENSE_POLICY.md).
6. Memo D2: опции кода и docs/data с tradeoffs, release-специфичные соображения, шаблон решения; БЕЗ выбора.
7. Тесты: валидный пример проходит; негативные фикстуры отвергаются; полный unittest-гейт зелёный.

## Validation

- `PYTHONPATH=scripts python3 -m release.card_lint package examples/release/nanolab-components-v0.1` → ok
- `python3 -m unittest discover -s tests -t .` → OK (все существующие тесты не сломаны)
- `CONTROL_WORK.sh validate/close` на `EX-NL5-001-A-R1` → ok
- `CONTROL_DEVELOPMENT.sh --check-consistency` → ok, canonical state не менялся

## Human gate

Merge — по стандартному Harness (Reviewer для MEDIUM+; Verifier по решению Reviewer), после Gate 0 PR #37. Публичный release по этому контракту — отдельный Human Gate (NL5-001-D).
