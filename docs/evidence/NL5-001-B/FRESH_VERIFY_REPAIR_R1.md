# NL5-001-B — Fresh exact-head Verifier (repair R1, clean integration)

**VERIFY_VERDICT: PASS**

**Роль:** независимый VERIFIER (fresh-сессия, не автор / не reviewer subject, не наследует чужие PASS).
**Точная дата верификации:** 2026-09-16, сессия `verify-nl5-repair-r1`.

---

## 1. Verdict

**PASS.** Exact-head subject `a9950dc87760986a2987a7b61131a417243a8c2b` (tree `8b2e96339e7a91feb67683d33caefa0d5c8598b2`) независимо верифицирован: все 5 проверок hosted-CI эквивалента локально зелёные, repair-специфичные проверки (детерминированный R1.2 rebuild, card_lint, frozen reproduction rule) зелёные, три negative control подтверждают fail-closed поведение, числовые инварианты карточек сходятся с опубликованным evidence. Расхождений не найдено.

## 2. Exact subjects и live-наблюдения

| Объект | Значение |
|---|---|
| HEAD (verify worktree, detached) | `a9950dc87760986a2987a7b61131a417243a8c2b` |
| HEAD^{tree} | `8b2e96339e7a91feb67683d33caefa0d5c8598b2` |
| base (`origin/main`) | `9de094c8d423574568e62832854664b577e9f282` |
| `origin/work/nl5-001-clean-integration-r1` (наблюдение 1, 2026-09-16T11:52:08Z) | `a9950dc87760986a2987a7b61131a417243a8c2b` |
| `origin/work/nl5-001-clean-integration-r1` (наблюдение 2, 2026-09-16T12:04:23Z) | `a9950dc87760986a2987a7b61131a417243a8c2b` — не двинулся |
| PR #41 via API (наблюдение 1, ≈2026-09-16T11:52:2xZ) | `state=open`, `draft=true`, `head.sha=a9950dc…`, `base=main@9de094c…`, `mergeable_state=clean` |
| PR #41 via API (наблюдение 2, 2026-09-16T12:05:08Z) | `state=open`, `draft=true`, `head.sha=a9950dc…`, `base=main@9de094c…` — head не двинулся |
| Ancestry | `git merge-base --is-ancestor 9de094c a9950dc` → exit 0 |
| Tree diff vs `origin/work/nl5-001-clean-integration-r1` | пусто (`git diff --stat` без вывода, exit 0) |
| `git status --porcelain` в verify worktree до работ | пусто (0 строк) |

Коммит-цепочка `9de094c..a9950dc` — 41 коммит; tip: `a9950dc control(nl5-001-b): clean integration rebuild R1 record - stack de-liquefaction on 9de094c`.

## 3. Checks — полный локальный эквивалент hosted CI (5/5)

Все команды выполнены в fresh detached worktree на exact head; приведены реальные exit codes.

| # | Check | Команда (эквивалент workflow) | Результат | Exit |
|---|---|---|---|---|
| 1 | JSON syntax sweep | цикл из `.github/workflows/hosted-ci.yml`: `git ls-files -z '*.json'` + `python3 -m json.tool` для каждого файла; 4 pinned non-JSON fixtures — сверка sha256 | 1035 tracked JSON: 1031 parsed OK, 4 pinned digest-match (`e3b0c442…` ×3, `1de18ae4…` ×1) | 0 |
| 2 | Harness consistency | `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | consistency ok (stages 9, tasks 19, experiments 7) | 0 |
| 3 | Execution passports | `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-*` для всех каталогов | 36/36 EX-* каталогов валидны | 0 |
| 4 | Workflow NC lint | `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | 1 workflow, violations=0, blocking=0 | 0 |
| 5 | Unit tests | `python3 -m unittest discover -s tests -t .` | **Ran 360 tests … OK** | 0 |

## 4. Repair-специфичные проверки

| Check | Команда | Результат | Exit |
|---|---|---|---|
| R1.2 deterministic check | `PYTHONPATH=scripts python3 -m release.build_library_r12 check` | `ok=true`, `problems=[]` (два независимых полных build byte-identical, включая manifest) | 0 |
| Полный rebuild → нулевой дрейф | disposable-копия всего дерева (вне проверяемого worktree): baseline-commit всей копии → `PYTHONPATH=scripts python3 -m release.build_library_r12 build` → `git status --porcelain` | rebuild пересобрал 21 файл пакета; `git status --porcelain` пуст (0 строк) — committed bytes == rebuilt bytes | 0 |
| card_lint package | `PYTHONPATH=scripts python3 -m release.card_lint package releases/nanolab-components-v0.1` | `ok=true`, `errors=[]`, ровно **1 ожидаемый warning**: D2 `UNDECIDED_PENDING_OWNER_DECISION` (RIGHTS.json, package draft-only) | 0 |
| Frozen reproduction rule | `PYTHONPATH=scripts python3 -m unittest tests.test_release_repair_r12` + прямой прогон `reproduction_rule.classify` на 4 контрольных случаях из тестов | 9/9 tests OK; контрольные случаи: `[65.50,65.90,66.40]→MATCH` (вне старого pooled CI — корректно), `[68.0,68.2,68.4]→MISMATCH`, `[65.8,66.0]→INCONCLUSIVE`, `technical_ok=False→INCONCLUSIVE`; rule `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` | 0 |
| Reproduction helper (positive) | `reproduce.py verify` на нетронутом пакете | ok=true | 0 |

## 5. Negative controls (все — в disposable-копии, не в проверяемом дереве, без push)

| NC | Assertion-команда (ожидаемый отказ) | Ожидание | Факт | Assert exit |
|---|---|---|---|---|
| (a) | изменить 1 байт в `releases/nanolab-components-v0.1/families/dna_hinge/cards/11b.card.json` (`74.218071238`→`74.218071239`, первая позиция reference median) → `python3 -m unittest tests.test_release_manifest_candidate` обязан упасть; после — восстановление байт | baseline exit 0; tampered exit ≠ 0 | baseline=0, tampered=1 (`AssertionError` на manifest exactness) | 0 (PASS) |
| (b) | дубликат пути в тестовом RELEASE_MANIFEST через валидатор `scripts/release` (`build_library_r12.build(tmp)` → `manifest_create` → `files.append(deepcopy(files[0]))` → `manifest_verify`); дополнительно CLI `card_lint manifest verify` | `report.ok=False` c ошибкой `duplicate path`; CLI exit ≠ 0 | `ok=False`, error `duplicate path entry 'CITATION.cff'`; CLI exit=3 — fail-closed подтверждён | 0 (PASS) |
| (c) | удалить один файл пакета (`protocols/README.md`) → `reproduce.py verify` обязан вернуть exit 3; после — восстановление | exit 3 | baseline=0, после удаления exit=3, `missing file: protocols/README.md` | 0 (PASS) |

Каждый NC оформлен как assertion-команда: возвращает 0 только при наблюдении ожидаемого отказа. Все три вернули 0.

## 6. Числовые инварианты (карточки vs опубликованный evidence)

Сверка `measured_observables`/`reproduction.expected` карточек с `docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/parametric-summary.json` (и для 0b confirmatory — с `docs/work/executions/EX-NL3-002-R1/evidence/confirmatory-summary.json`); всего 26 сравнений, все OK:

| Карточка | Spot-значение (1 на карточку) | Card | Evidence | OK |
|---|---|---|---|---|
| 0b (confirmatory 200k, primary) | `E2-R1-C001` median_deg | `65.095434789` | `65.095434789` (confirmatory-summary) | ✓ |
| 0b (150k reslice, secondary pooled-only by note) | estimate | `65.870460546` | pooled median `65.870460546` (parametric-summary) | ✓ |
| 11b | `PARAM-11B-S001` median_deg | `74.218071238` | `74.218071238` | ✓ |
| 32b | `PARAM-32B-S001` median_deg | `79.877463339` | `79.877463339` | ✓ |
| 53b | `PARAM-53B-S001` median_deg | `132.343978104` | `132.343978104` | ✓ |
| 74b | measurement_status | `NOT_MEASURED`, observables пусты, `known_gaps` описывает arm-manifest отказ как known gap; fabricated numbers отсутствуют | — | ✓ |

Дополнительно по каждой MEASURED-карточке (11b/32b/53b) сверены все 3 per-replica medians, campaign estimate == pooled median, bootstrap ci95 == pooled bootstrap, reproduction envelope == [min,max] replica medians, reproduction campaign statistic == median(replica medians); для 0b — reproduction medians == confirmatory replicas. Полное совпадение байт-в-байт по числам.

## 7. Corroboration — hosted CI

- Run **35090409941** (`hosted-ci`), API: `head_sha=a9950dc…` (exact subject), `head_branch=work/nl5-001-clean-integration-r1`, `event=pull_request`, `status=completed`, **`conclusion=success`** (наблюдение 2026-09-16 ≈12:04Z). Один job `RC0 hosted validation (H0)` — 5/5 шагов, что согласуется с моими локальными 5/5.
- Fresh Reviewer PASS: ветка `review/nl5-001-b-repair-r1` @ `8e83486c7f276147a65192e2e52e912597318ae8`, отчёт `docs/evidence/NL5-001-B/FRESH_REVIEW_REPAIR_R1.md` (присутствует на review-ветке; на subject-ветке каталога `docs/evidence/NL5-001-B/` нет — это ожидаемо, review-отчёт публикуется отдельной веткой).

## 8. Independence caveat

Верификация выполнена fresh-агентом в изолированной сессии: собственный detached worktree от exact `a9950dc`, команды воспроизведены из `.github/workflows/hosted-ci.yml` независимо, disposable-копия для rebuild/negative controls создана вне проверяемого дерева. Ограничения: (1) локальная среда (Linux, python 3.10) может отличаться от hosted runner — полного совпадения окружения гарантировать нельзя, однако все проверки stdlib-only; (2) результаты hosted CI приняты по API как corroboration, а не воспроизведены побитово; (3) научная корректность измеренных значений (углы, окна, статистика) не пере-выводилась из raw frames — сверялись опубликованные evidence-файлы против карточек (verifier проверяет exactness/provenance, не повторяет кампанию); (4) GitHub API доступ — read-only токен.

## 9. Remains before merge (Human Gate inputs)

- Merge PR #41 в `main` — Human Gate (по PROJECT_CONTROL.md).
- D2 license decision (`UNDECIDED_PENDING_OWNER_DECISION`) — блокирует public release пакета (единственный card_lint warning, ожидаемый).

---

**VERIFY_VERDICT = PASS**
