# FRESH_VERIFY_R1 — NL5-001-D (независимая fresh exact-head верификация)

Verify id: `NL5-001-D/FRESH_VERIFY_R1`
Дата verify (UTC): 2026-09-18
Verifier: fresh independent Verifier (отдельная сессия; implementation и review этого subject не выполнял, к чатам Implementer/Reviewer/Director доступа не имеет, их вердикты не наследовались)

Subject: PR #42, ветка `control/nl5-001-d-license-r1`, repo `rootfabric/NanoLab`
Worktree верификации: чистый worktree на ветке `verify/nl5-001-d-r1`, exact HEAD (до evidence-commit этого файла).

```
VERIFY_VERDICT = PASS
VERIFIED_HEAD = 216c01c1597ee49bbf946e391f09db4360ebb8cd
VERIFIED_TREE = c9390dfd28297056d8d524ddabaca7020b59037d
Reviewer subject match = TRUE   (REVIEWED_HEAD из review-ветки == VERIFIED_HEAD)
PR live HEAD match = TRUE       (origin/control/nl5-001-d-license-r1 == VERIFIED_HEAD)
```

## 1. Independence statement

- Verifier — fresh-сессия. Все факты ниже получены самостоятельно из живого Git и живых запусков команд на exact HEAD в чистом worktree.
- Результаты Implementer (EX-NL5-001-D-R1) и Reviewer (FRESH_REVIEW_R1) не принимались на веру: все команды валидации, сборка пакета, пересчёт хэшей и все negative controls переисполнены локально. Из review-ветки взято ТОЛЬКО значение поля `REVIEWED_HEAD` для сверки subject'а (не вердикт).
- Все negative controls выполнены в disposable-копиях в `/tmp` (`/tmp/nc1`, `/tmp/nc2_repo`, `/tmp/nc2_out`, `/tmp/nc3`); worktree и remote product-ветки не изменялись. Сборка пакета — в `/tmp/nlv_build_a`, `/tmp/nlv_build_b`, поверх committed-пакета сборка не выполнялась.

## 2. Subject resolution (live Git)

| Проверка | Результат | Exit code |
|---|---|---|
| `git rev-parse HEAD` | `216c01c1597ee49bbf946e391f09db4360ebb8cd` | 0 |
| `git rev-parse HEAD^{tree}` | `c9390dfd28297056d8d524ddabaca7020b59037d` | 0 |
| `git status --porcelain` (до evidence-commit) | пусто (чистый worktree) | 0 |
| `git rev-parse origin/control/nl5-001-d-license-r1` (после `git fetch origin`) | `216c01c1597ee49bbf946e391f09db4360ebb8cd` — совпадает с VERIFIED_HEAD | 0 |
| `git rev-parse origin/main` | `bc9ad8c5a10e482ea380a03b6fe30aed2cac451e` — совпадает с ожидаемым base | 0 |
| `git merge-base --is-ancestor bc9ad8c5… HEAD` | ancestor подтверждён | 0 |
| `git rev-parse origin/review/nl5-001-d-r1` | `11f33b71d06bf2afe90cb02722800d938b1dc50e`; в `docs/evidence/NL5-001-D/FRESH_REVIEW_R1.md` этой ветки `REVIEWED_HEAD = 216c01c1597ee49bbf946e391f09db4360ebb8cd` | 0 |

STALE_SUBJECT: нет. Subject свежий и совпадает с live head PR-ветки.

## 3. Обязательные команды и реальные результаты (полный hosted-CI-equivalent)

| Команда | Результат | Exit code |
|---|---|---|
| `python3 -m unittest discover -s tests -t .` | `Ran 360 tests in 11.851s` / `OK` | 0 |
| `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | `ok=true`, `errors=[]`, `warnings=[]`, `head/tree` = exact VERIFIED_HEAD/VERIFIED_TREE | 0 |
| `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | `ok=true`, `blocking: 0` | 0 |
| `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-001-D-R1` | `ok=true`, `HANDOFF_READY`, terminal handoff есть, `has_post_terminal_corrections=false`, `passport_sha256=2bfeee9c26760951ca923652d3cef905909e661dfb8c0e5a70e0c3ab16208467` | 0 |
| `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-001-C-R1` | `ok=true` | 0 |
| `work_cli validate` всех остальных EX-* (всего 38 каталогов EX-*, каждый переисполнен) | все `ok=true`, exit 0 у каждого | 0 |
| `PYTHONPATH=scripts python3 -m release.build_library_r12 check` | `ok=true`, `problems=[]` | 0 |
| `PYTHONPATH=scripts python3 -m release.card_lint package releases/nanolab-components-v0.1` | `ok=true`, `errors=[]`, `warnings=[]`; `variant_status`: 0b=MEASURED, 11b=MEASURED, 32b=MEASURED, 53b=MEASURED, 74b=NOT_MEASURED | 0 |

## 4. Package byte-for-byte rebuild

Builder: `release.build_library_r12.build(root)` (Python API; CLI `build` пишет в committed-каталог, поэтому использован root-параметр — сборка только в /tmp).

| Проверка | Результат | Exit code |
|---|---|---|
| `build(Path('/tmp/nlv_build_a'))` | 21 файл собран | 0 |
| `diff -r --brief releases/nanolab-components-v0.1 /tmp/nlv_build_a` | ни одного различия — **byte-identical** (RIGHTS.json, CITATION.cff, VERSION, RELEASE_MANIFEST.json, cards, family, protocols, reports, provenance, reproduction, schema) | 0 |
| `build(Path('/tmp/nlv_build_b'))` + `diff -r /tmp/nlv_build_a /tmp/nlv_build_b` | идентично — детерминизм подтверждён независимо | 0 |
| Независимый пересчёт SHA-256 + size каждого файла из `RELEASE_MANIFEST.json` (чистый python, вне project-кода) | **20/20 записей совпали** (sha256 и size_bytes), MISMATCHES: NONE | 0 |

Ключевые хэши committed-пакета:

```text
RIGHTS.json           sha256=5292781ac4448112b3f3ecdaa47aede3f6539f8a68c357808e28dc896fa9bebf size=1511
CITATION.cff          sha256=27046a10719d37f80cf7ceac39f5579b813158ebe496d08567c843d0cfa62433 size=373
VERSION               sha256=e9dd8507f4bf0c6f42458e41aea833ad0bd3f6127272335eee9bf4d58541ed67 size=6
RELEASE_MANIFEST.json sha256=f87134dedf11c279fcdddb47bac2a3cc32ea98f260232ac5457bba1c64a6b7fd (сам manifest в манифест не входит)
VERSION content: "0.1.0"; CITATION.cff: version 0.1.0, license Apache-2.0, date-released 2026-09-18
RIGHTS.json: own_code_license=Apache-2.0, own_docs_data_license=CC-BY-4.0, package_version=0.1.0
```

## 5. Negative controls (все — disposable-копии в /tmp)

| # | Tamper | Детектор | Результат |
|---|---|---|---|
| 1 | `/tmp/nc1`: ровно 1 байт в `RIGHTS.json` (`Apache-2.0` → `apache-2.0`; `cmp -l` = 1 differing byte) | `card_lint manifest verify /tmp/nc1` | **СРАБОТАЛ**: exit 3, `ok=false`, `sha256 mismatch for 'RIGHTS.json'` |
| 2 | `/tmp/nc2_repo` (disposable-копия репо через `git archive HEAD`): в builder-входе `FINAL_CODE_LICENSE` возвращён в `UNDECIDED_PENDING_OWNER_DECISION`; rebuild в `/tmp/nc2_out` (21 файл; `own_code_license` в собранном RIGHTS = UNDECIDED) | `card_lint rights` + `card_lint package` на `/tmp/nc2_out` | **СРАБОТАЛ (как warning-gate)**: exit 0, но явный warning `own license UNDECIDED_PENDING_OWNER_DECISION (owner license decision D2) — package is draft-only; public release blocked until D2`. Gate зафиксирован: по RELEASE_CONTRACT_V0_1 §4 и схеме `rights.v1.json` (описание поля: UNDECIDED keeps the package draft-only, publication blocked) UNDECIDED допускается только для draft; machine-детектор — warning lint'а + forced finalization в нормативном builder'е (`_finalize_release_metadata` жёстко проставляет Apache-2.0/CC-BY-4.0/0.1.0, поэтому UNDECIDED не может пережить rebuild). В committed-пакете warnings=[] — финализация подтверждена. |
| 3 | `/tmp/nc3`: в `RELEASE_MANIFEST.json` подменён digest записи `CITATION.cff` (sha256 → 0×64) | `card_lint manifest verify /tmp/nc3` + независимый recompute | **СРАБОТАЛ**: exit 3, `ok=false`, `sha256 mismatch for 'CITATION.cff'` |
| 4 | Отсутствие upstream E2 bytes в пакете (источник `gauravarya77/DNA-hinge-simulations @ 23fd1ff7731e9017bd776f49206dc42d70d9fe91`) | см. ниже | **ПОДТВЕРЖДЕНО (vendoring отсутствует)** |

Детали NC4: в метаданных пакета найдено 12 upstream `blob_sha1` пинов; `git hash-object` каждого из 21 файлов пакета не совпал ни с одним upstream-пином (NONE) — ни один upstream-файл не вендорен байт-в-байт. Все файлы пакета — NanoLab-derived (cards/family/protocols/reports/provenance/reproduction/schema + RIGHTS/CITATION/VERSION/MANIFEST), файлы >60KB отсутствуют (максимальный — `reports/evidence/parametric-summary.json`, 29408 байт). Упоминания upstream-репозитория — только как digest-метаданные: `provenance/source-digests.json` (`rights_mode: REFERENCE_ONLY`, `pinned_commit: 23fd1ff7…`), поля `RIGHTS.json` (`provenance/**` = REFERENCE_ONLY / METADATA_ONLY) и provenance-поля карточек.

## 6. Scientific immutability относительно base

`git diff --name-only bc9ad8c5a10e482ea380a03b6fe30aed2cac451e..HEAD` = ровно 16 файлов: LICENSE, LICENSE-DOCS-DATA.md, LICENSE_POLICY.md, docs/control/NL5_001_D_LICENSE_DECISION_R1.md, docs/research/DEPENDENCY_LICENSE_MATRIX.md, docs/work/WO-NL5-001-D-R1.md, docs/work/executions/EX-NL5-001-D-R1/** (5 файлов), releases/…/{CITATION.cff, RELEASE_MANIFEST.json, RIGHTS.json, VERSION}, scripts/release/build_library_r12.py. Все — в allowed_paths из WO-NL5-001-D-R1.md.

Пустые diff (без изменений) для обязательных immutability-целей:

- `releases/nanolab-components-v0.1/families/**` (все карточки 0b/11b/32b/53b/74b и family.json) — **не изменены**;
- `docs/release/REPRODUCTION_RULE_V0_1.md` и `scripts/release/reproduction_rule.py` — **не изменены**;
- `docs/work/executions/EX-NL5-001-C-R1/**` (включая evidence/classifications) — **не изменены**.

Live-значения классификаций (прочитаны из committed файлов `EX-NL5-001-C-R1/evidence/classification-*.json` и карточек; rule id во всех — `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`, valid_replicas=3):

| Вариант | Классификация (live) | Хэш classification-файла (sha256) |
|---|---|---|
| 0b | MATCH (66.159296437° внутри envelope [65.095434789, 67.236579608]) | e4bd68cce3c5fa6c78a43a1a9e9531a68897199b6244d85efc3fa83469ab34f2 |
| 11b | INCONCLUSIVE (75.514562357° вне envelope [72.165683993, 74.533109426] без полной направленной сепарации) | 913841e1d159e27d7d7def1cc9c6caf3cfd84f0211ec51bb70b29fddc8bc9c6d |
| 32b | MATCH (78.096569929° внутри envelope [77.4927314, 79.877463339]) | 66b2936a3eafe3b9898041b34d6e69caa2d370f006e26ab1edbef32762d03f0f |
| 53b | MATCH (132.575590442° внутри envelope [131.049227687, 135.285186059]) | fd1b2656b17b52a5a5bd163df2ce0c817bc24aa65be3fe81b2d9d6847649b6e7 |
| 74b | NOT_MEASURED / KNOWN_GAP (`G-74B-ARM-MANIFEST`, `blocking_release=false`, runs NOT_RUN, claim_ceiling C0_SOFTWARE_ONLY); classification-файла нет — корректно | карточка 74b.card.json sha256=5894f420c0ec81621955e7351cb09174b2f7eb4b8358ee63f1bf50a96ce350bb |

Дополнительные хэши immutable-поверхностей: `docs/release/REPRODUCTION_RULE_V0_1.md` sha256=6b70dfc26764c8a21d006824f00e485df9abec8b020e67de5a9709acea793e78; `scripts/release/reproduction_rule.py` sha256=b7b312c054bfbd58e6020b00459f2e568040dac7d2aa4c984d5423bb6665973f; `LICENSE` sha256=592f537c6838503f2471d77494e495a02927ac0226657c431146b6c8aee7ce46; `LICENSE_POLICY.md` sha256=a7bb5616703b3b495561711b1499a6fa8a86c0afbd970adc9a857778e7a9f698; `LICENSE-DOCS-DATA.md` sha256=c3882e70ffa46586e947a168569b6de73994cd5cf7f2aa0152a6775eb4ad68ed.

## 7. Лицензии (owner decision D2)

- `LICENSE` = Apache-2.0 для NanoLab code; `LICENSE-DOCS-DATA.md` = CC-BY-4.0 для docs и own derived data; оба с явным исключением third-party/upstream материалов.
- `LICENSE_POLICY.md` / `docs/control/NL5_001_D_LICENSE_DECISION_R1.md`: owner decision D2 (2026-09-18); сторонние/upstream (включая `gauravarya77/DNA-hinge-simulations @ 23fd1ff7…` REFERENCE_ONLY/download-on-run) не перелицензованы и не вендорены; UNKNOWN не является разрешением.
- `RIGHTS.json`/`CITATION.cff`/`VERSION` синхронизированы (0.1.0, Apache-2.0, CC-BY-4.0);`release.build_library_r12 check` доказывает детерминизм (ok=true, problems=[]).

## 8. Remaining risks

- **NC2 gate — warning, а не hard error**: при `own_code_license=UNDECIDED_PENDING_OWNER_DECISION` lint завершается exit 0 с warning'ом «draft-only; public release blocked until D2». Публикационная блокировка держится на этом warning'е + contract §4 + forced finalization builder'ом, а не на nonzero exit. Для committed-пакета warnings=[] — сейчас блокировки нет, что и требуется.
- `card_lint package` сравнивает packaged schema snapshot с repo schema только через warning — рассинхрон схем не падает с exit 3 (сейчас совпадают).
- Верификация привязана к exact HEAD `216c01c…`; любой новый commit на PR-ветке инвалидирует этот вердикт (нужен re-verify).
- `origin/verify/nl5-001-d-r1` на момент старта верификации не существовала; ветка создана этим evidence-push (non-force).
- Merge в `main` остаётся Human Gate; данный вердикт его не заменяет.

## 9. Verdict

Все обязательные проверки зелёные на exact HEAD `216c01c1597ee49bbf946e391f09db4360ebb8cd` (tree `c9390dfd28297056d8d524ddabaca7020b59037d`): 360/360 tests OK, consistency/workflow-lint/38×EX-validate/build-check exit 0, пакет byte-identical при rebuild, 20/20 manifest-записей подтверждены, все 4 negative controls дали ожидаемый исход, scientific-поверхности неизменны относительно base `bc9ad8c5…`.

`VERIFY_VERDICT = PASS`
