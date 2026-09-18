# FRESH_REVIEW_R1 — NL5-001-D (независимое fresh review)

Review id: `NL5-001-D/FRESH_REVIEW_R1`
Дата review (UTC): 2026-09-18
Reviewer: fresh independent Reviewer (отдельная сессия, без доступа к чатам Implementer/Director)
Subject: PR #42, ветка `control/nl5-001-d-license-r1`

```
REVIEW_VERDICT = PASS
REVIEWED_HEAD = 216c01c1597ee49bbf946e391f09db4360ebb8cd
REVIEWED_TREE = c9390dfd28297056d8d524ddabaca7020b59037d
BASE = bc9ad8c5a10e482ea380a03b6fe30aed2cac451e
```

Live branch head (`git fetch origin && git rev-parse origin/control/nl5-001-d-license-r1`) =
`216c01c1597ee49bbf946e391f09db4360ebb8cd` — совпадает с REVIEWED_HEAD. Subject не STALE.

## 1. Independence statement

- Reviewer — fresh-сессия: implementation не выполнял, verify не выполнял, к чатам/сессиям Implementer и Director доступа не имеет.
- Все факты ниже получены самостоятельно из живого Git в чистом worktree `review-nl5-001-d-r1` (ветка `review/nl5-001-d-r1`, exact HEAD `216c01c…`).
- Заявленные в `docs/work/executions/EX-NL5-001-D-R1/summary.md` результаты (в т.ч. hosted CI `35336208105`) НЕ наследовались и НЕ принимались на веру: все команды валидации переисполнены локально на exact HEAD (см. раздел 3).

## 2. Проверка идентичности subject

| Проверка | Результат | Exit code |
|---|---|---|
| `git rev-parse HEAD` | `216c01c1597ee49bbf946e391f09db4360ebb8cd` | 0 |
| `git rev-parse HEAD^{tree}` | `c9390dfd28297056d8d524ddabaca7020b59037d` | 0 |
| `git status --porcelain` | пусто (чистый worktree) | 0 |
| `git merge-base --is-ancestor bc9ad8c5… HEAD` | ancestor подтверждён | 0 |
| `git rev-parse origin/control/nl5-001-d-license-r1` | `216c01c1597ee49bbf946e391f09db4360ebb8cd` (совпадение) | 0 |

## 3. Выполненные команды и результаты (локально на exact HEAD)

| Команда | Результат | Exit code |
|---|---|---|
| `python3 -m unittest discover -s tests -t .` | `Ran 360 tests in 11.389s` / `OK` | 0 |
| `PYTHONPATH=scripts python3 -m release.build_library_r12 check` | `ok=true`, `problems=[]` | 0 |
| `PYTHONPATH=scripts python3 -m release.card_lint package releases/nanolab-components-v0.1` | `ok=true`, `errors=[]`, `warnings=[]` | 0 |
| `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | `ok=true`, head/tree совпадают с exact subject | 0 |
| `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-001-D-R1` | `ok=true`, `HANDOFF_READY`, terminal handoff есть, `has_post_terminal_corrections=false` | 0 |
| Свежая сборка `release.build_library_r12.build()` во временный каталог; `diff -r` против committed package | byte-identical (`BUILDER_VS_COMMITTED: IDENTICAL`) | 0 |
| Независимый пересчёт sha256+size всех записей `RELEASE_MANIFEST.json` | 20/20 записей совпали | 0 |

## 4. Scope diff base..HEAD против allowed_paths

- `git diff --name-only bc9ad8c5…..216c01c…` → ровно 16 файлов, все входят в `allowed_paths` из `WO-NL5-001-D-R1.md` / `passport.json`; формальная программная сверка: **out-of-scope: NONE**.
- Изменённые поверхности: `LICENSE`, `LICENSE-DOCS-DATA.md`, `LICENSE_POLICY.md`, `docs/control/NL5_001_D_LICENSE_DECISION_R1.md`, `docs/research/DEPENDENCY_LICENSE_MATRIX.md`, `scripts/release/build_library_r12.py`, 4 файла release-пакета (`RIGHTS.json`, `CITATION.cff`, `VERSION`, `RELEASE_MANIFEST.json`), `docs/work/WO-NL5-001-D-R1.md`, `docs/work/executions/EX-NL5-001-D-R1/**`.
- Расширение scope (добавление `scripts/release/build_library_r12.py` в WO и passport) выполнено durably ДО изменения builder'а: WO — commit `fdfb510`, passport — commit `c959923`. Корректно.

## 5. Лицензии — согласованность owner decision D2

Вывод: **D2 согласован на всех поверхностях; сторонние материалы не перелицензированы.**

- `LICENSE` — декларация Apache-2.0 (SPDX-License-Identifier: Apache-2.0) с явным исключением third-party/upstream материалов.
- `LICENSE-DOCS-DATA.md` — декларация CC-BY-4.0 для документации и NanoLab-owned derived data/results, тоже с upstream-исключением.
- `LICENSE_POLICY.md` — зафиксирован `OWNER_DECISION D2 принят 2026-09-18`; режимы E1 (GPL-3.0, DOWNLOAD_ON_SETUP), E2 (UNKNOWN rights → REFERENCE_ONLY + user-side download by exact commit), S08 (RESTRICTED), NANOBASE (per-record REFERENCE_ONLY) сохранены; UNKNOWN не является разрешением.
- `docs/control/NL5_001_D_LICENSE_DECISION_R1.md` — durable owner record: код Apache-2.0, docs/derived data CC-BY-4.0, граница прав: `gauravarya77/DNA-hinge-simulations @ 23fd1ff7731e9017bd776f49206dc42d70d9fe91` остаётся REFERENCE_ONLY/download-on-run, oxDNA — upstream GPL, restricted/UNKNOWN — свои права.
- `docs/research/DEPENDENCY_LICENSE_MATRIX.md` — раздел вариантов помечен историческим, добавлена запись `OWNER_DECISION D2 (2026-09-18)` с явным «не меняет лицензии и rights mode сторонних/upstream материалов».
- `releases/nanolab-components-v0.1/RIGHTS.json`: `own_code_license: Apache-2.0`, `own_docs_data_license: CC-BY-4.0`, `package_version: 0.1.0`; provenance/** — `METADATA_ONLY` / `REFERENCE_ONLY` с тем же pinned commit; policy `download_on_run: true`, `durable_cache: FORBIDDEN` сохранены.

Межфайловых расхождений D2 не найдено.

## 6. Release package (0.1.0-rc0 → 0.1.0)

- `VERSION` = `0.1.0`.
- `CITATION.cff` = `version: "0.1.0"`, `date-released: 2026-09-18`, `license: Apache-2.0`; draft-комментарии rc0 удалены.
- `RELEASE_MANIFEST.json` = `package_version: 0.1.0`, `generated_by: release.build_library_r12 deterministic-r1.2`; дайджесты CITATION/RIGHTS/VERSION обновлены, дайджесты всех научных файлов (cards, rules, reports, provenance, schema) — без изменений относительно rc0, т.е. байты научных файлов не менялись на всей ветке.
- Divergence builder ↔ committed package отсутствует: свежая сборка в чистый временный каталог byte-identical с committed package (проверено независимо `diff -r`); дополнительно тест `test_real_release_manifest_exact` пересчитывает манифест из committed байтов — в составе 360 пройденных тестов.
- Независимый пересчёт всех 20 записей манифеста (sha256 + size_bytes) — 0 расхождений.

## 7. Builder `scripts/release/build_library_r12.py`

- Финализация D2 (`_finalize_release_metadata`) применяется после `_postprocess` и ДО `card_lint.manifest_create`, поэтому манифест покрывает уже финализированные RIGHTS/VERSION/CITATION. Корректный порядок.
- Детерминизм: `check` выполняет две независимые полные сборки и требует byte-identичность, включая манифест (`ok=true, problems=[]`); дополнительно моя собственная сборка совпала с committed package байт-в-байт.
- Builder меняет только release-метаданные (package_version, лицензии, notes, VERSION, CITATION.cff); научный контент карточек не трогает.

## 8. Execution records (иммутабельность)

- `events/0001-work-order-started.json` — создан одним commit `8e15a6a`, далее не редактировался (`git log --follow`).
- `events/0002-validation-recorded.json` — создан одним commit `53d0a9c`, далее не редактировался.
- `events/0003-handoff-completed.json` — создан одним commit `216c01c` (HEAD).
- `passport.json` редактировался (`f98efdd` → `c959923` → `6b0f023`) — это не event; оба изменения — документированные durable scope/status-обновления до и в процессе работы.
- `harness.work_cli validate` — ok, `has_post_terminal_corrections=false`.
- События 0002/0003 ссылаются на substantive subject `50aee777…`; diff `50aee77..HEAD` содержит только файлы `EX-NL5-001-D-R1/**` (контрольные записи), научных/кодовых изменений после 50aee77 нет.

## 9. Scientific non-regression (подтверждён)

Сверка по diff `bc9ad8c5…..216c01c…` (base==head по перечисленным поверхностям, diff пуст):

- Карточки `families/dna_hinge/cards/0b|11b|32b|53b|74b.card.json` и `family.json` — не изменены.
- `docs/release/REPRODUCTION_RULE_V0_1.md` и `scripts/release/reproduction_rule.py` — не изменены.
- `docs/work/executions/EX-NL5-001-A-R1/**`, `EX-NL5-001-B-R1/**`, `EX-NL5-001-B-REPAIR-R1/**`, `EX-NL5-001-C-R1/**` — не изменены.
- Единственные изменившиеся записи `RELEASE_MANIFEST.json` — CITATION.cff / RIGHTS.json / VERSION / package_version; дайджесты карточек, reproduction-правил и отчётов идентичны rc0 → байты научных поверхностей не менялись.
- Обязательные факты на HEAD сохранены как есть: **0b = MATCH**, **11b = INCONCLUSIVE** (не превращён в PASS/MATCH; явно сохранён как durable honest outcome), **32b = MATCH**, **53b = MATCH**, **74b = NOT_MEASURED / KNOWN_GAP** (`docs/work/executions/EX-NL5-001-C-R1/summary.md`; `variant_status` family.json; RELEASE_CONTRACT R1.2 без изменений). Научные thresholds, observables и reference replica medians не затронуты (соответствующие файлы вне diff).

## 10. Отсутствие upstream E2 bytes в release package

- В пакете `provenance/` содержит только `source-digests.json` (digest-метаданные: blob_sha1/sha256/size, pinned commit `23fd1ff7…`, `rights_mode: REFERENCE_ONLY`, download-on-run). Сами upstream-файлы не включены.
- Наибольший файл пакета — `reports/evidence/parametric-summary.json` (29 408 байт, NanoLab-derived). Бинарных/upstream-артефактов в пакете нет. Вендоринга E2/GPL нет.

## 11. Minor observations (не блокируют PASS)

1. `LICENSE` — декларация Apache-2.0 (SPDX + ссылка на канонический текст), полный текст лицензии в файл не встроен. Это соответствует формулировке owner record («Apache-2.0 declaration»), но при распространении дистрибутива рекомендуется поставлять полный текст Apache-2.0 (appendix) в составе артефакта. Вопрос к Verifier/Human Gate, не к этой ветке.
2. `project/state.json` по-прежнему содержит `open_decisions`: лицензионный выбор. `state.json` вне allowed_paths и принадлежит `main` (MAIN DECLARES PROJECT STATE) — переход состояния NL5-001 корректно выполнять после Human Gate merge силами Director, а не в этой ветке.
3. `RELEASE_MANIFEST.json` содержит 20 записей на 21 файл пакета (манифест исключает сам себя) — ожидаемое поведение `card_lint.manifest_create`.

## 12. Remaining risks

- Научная валидность самих фактов MATCH/INCONCLUSIVE не переадjudицируется этим review: подтверждена только non-regression (факты идентичны base). Содержательный разбор 11b INCONCLUSIVE относится к NL5-001-C evidence и Human Gate.
- Full-text Apache-2.0 в финальном дистрибутиве — см. minor observation 1.
- Hosted CI-заявки из summary.md не проверялись (нет необходимости: все проверки переисполнены локально); fresh Verifier по-прежнему требуется перед merge согласно handoff.

## 13. Вердикт

```
REVIEW_VERDICT = PASS
```

Основания: subject exact и fresh (live head совпадает); diff строго в allowed_paths; D2 согласован на всех лицензионных поверхностях без перелицензирования третьих сторон; release-пакет финализирован 0.1.0 и байт-идентичен детерминированной сборке builder'а; execution records валидны и иммутабельны; scientific non-regression подтверждён покомпонентно; upstream REFERENCE_ONLY bytes в пакет не включены. Merge в `main` остаётся Human Gate; далее — отдельный fresh exact-head Verifier.
