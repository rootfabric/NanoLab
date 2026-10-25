# [REVIEWER-76] Независимое review PR #76 (R1.1+R1.2) @ HEAD 2e199d6 — VERDICT: PASS

**Review gate:** GATE-NL7-ALT-SOURCE-R1 (Issue #77) · **PR:** #76 (`work/prep-nl7-alt-assembly-benchmark-r1`) · **Дата review:** 2026-10-21 UTC
**Роль:** независимый fresh Reviewer (отдельная сессия, не Implementer/Director этой ветки). Review выполнялся read-only в изолированном checkout `/home/rdpuser/NanoLab/review-pr76-r1`; собственные артефакты — только в `review-evidence/` и `/tmp`. 0 scientific runs, 0 MD/relax, 0 скачиваний внешних CAD/oxDNA байтов. Веб-активность ограничена библиографической проверкой DOI (метаданные публикаций, не исходники).

## 0. Точный предмет review

| Величина | Ожидание (Issue #77) | Факт (`git rev-parse`) | Совпадение |
|---|---|---|---|
| HEAD | `2e199d68af3119aaeb4194b2d622c365da8f6bfe` | `2e199d68af3119aaeb4194b2d622c365da8f6bfe` | ✅ |
| TREE | `9e8cd2c7a2ddbf5616b38e6922a14f458cac1e8b` | `9e8cd2c7a2ddbf5616b38e6922a14f458cac1e8b` | ✅ |
| Base main | `fb3148b46a9638167168a46cb170902a4ad9e8d2` | merge-base = `fb3148b…`, `origin/main` = `fb3148b…` | ✅ |

Рабочее дерево чистое (`git status --porcelain` пуст). Ветка впереди main на 16 коммитов; все 15 изменённых файлов лежат внутри `allowed_paths` паспорта (проверено `git diff --name-only fb3148b..HEAD` против списка разрешений — вне scope файлов нет). Секретных строк в diff нет.

## 1. Обязательные команды (все выводы сохранены в review-evidence/)

| # | Команда | Exit | Наблюдение | Вывод |
|---|---|---|---|---|
| 1 | `python3 -m unittest discover -s tests -t .` | **0** | `Ran 837 tests in 58.536s` / `OK` (`cmd1_unittest.out`) | Регрессия 837/837 OK |
| 2 | `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | **0** | `errors: []`; `"head": "2e199d6…"`, `"tree": "9e8cd2c…"` — совпадают с предметом | Consistency OK |
| 3 | `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | **0** | `violations: 0, blocking: 0` (`cmd3_workflow_lint.out`) | Lint OK |
| 4 | `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1` | **0** | `ok: true`, `HANDOFF_READY`, terminal handoff + summary есть; **честно подсвечен** `has_post_terminal_corrections: true` (CONTINUATION 0005/0006 после handoff) | Evidence-пакет валиден |
| 5 | `PYTHONPATH=scripts python3 -m knowledge_pack.alt_pair_source_gate docs/research/ALT_DNA_TWO_PART_SOURCE_PACK_R1.json --candidate S23_NARCISSUS_ECHO --root .` | **2** | `outcome: BLOCKED_SOURCE`, 5× `SOURCE_BYTES_NOT_OBSERVED` (`cmd5_gate_real_pack.out`) | **Корректный fail-closed на реальном pack'е (ожидаемое поведение, не дефект)** |

Хостед-CI сверена независимо через GitHub API (read-only): run `39548593361` = SUCCESS на **точном HEAD `2e199d6`**; GREEN `39547978810` = SUCCESS на `a8b3512`; RED `39547500409` = failure на test-only `b094518`; R1.1: RED `39538287299` failure / GREEN `39538562254` success на `3d0b55b`. Все head-SHA и conclusions совпадают с заявленными в evidence-map и событиях. (Логи RED-прогонов уже не извлекаются — истёк срок хранения; поэтому RED-поведение я воспроизвёл локально, см. §3.4.)

## 2. Область 1 — направление цепи oxDNA (n3/n5, 3′/5′, порядок оснований)

Независимый вывод из `scripts/hinge_family/oxdna_topology.py` (не менялся в ветке: `git diff fb3148b..HEAD -- scripts/hinge_family/` пуст): строка формата `<strand> <base> <n3> <n5>`, нуклеотиды стрэнда перечисляются от 3′-терминуса к 5′-терминусу; у 3′-терминального нуклеотида `n3 == -1`, у 5′-терминального `n5 == -1`; `n3` указывает на соседа в сторону 3′-конца, `n5` — в сторону 5′-конца; файловый порядок строк идёт 3′→5′, поэтому conventional 5′→3′ представление — реверс файлового порядка.

Проверено моими собственными пробами (`review-evidence/probe_adhoc.py`, класс `P1`, 15/15 OK):

- **(a) внутренний индекс не терминален:** `_verified_terminal_segment` (alt_pair_source_gate.py:203–231) требует `n3 == -1` для «3p» и `n5 == -1` для «5p»; проба подтвердила отказ для внутренних индексов (сообщение `internal anchor`), для too-long сегмента (`invalid segment length`) и для circular-стрэнда (нет терминалов; в цикле дополнительно срабатывает `visited`-защита «circular/ambiguous»). Юнит-тесты: `test_falsifier_numeric_in_bounds_but_nonterminal_anchor_must_block`, `test_reverse_complements_do_not_prove_exposed_single_strand_by_themselves` (индексы 2 и 3 внутри 12nt стрэнда → `BLOCKED_SOURCE`).
- **Полярность правильная:** моя проба `P2_Polarity` подала сегмент, равный «сырому» файловому порядку (3′→5′) вместо 5′→3′ — гейт отклонил (`topology sequence mismatch`). Обратный обход для «3p» идёт по `n5` с финальным `reversed()`, для «5p» — по `n3` без реверса (alt_pair_source_gate.py:229–231); проход `occupied` (строки 287–291) использует ту же ориентацию (`rows[cursor][3]` = n5 для «3p», `[2]` = n3 для «5p»).
- **(b) комплементарность ≠ доказательство открытого оверхэнга:** гейт требует, чтобы объявленный сегмент **байт-в-байт присутствовал** на номинированном терминале digest-verified топологии (`_validate_anchor_map`, строки 274–283: `declared overhang segment is not present at source topology … terminal`), а docstring (строки 197–201) и claim receipt прямо фиксируют: наличие последовательности на терминале не доказывает, что она unpaired/доступна/гибридизована; итоговый положительный исход называется `…PREFLIGHT_OK_REVIEW_REQUIRED`, а манифест обязан держать `source_verdict = BLOCKED_SOURCE` (строка 88). Никакого «доказанного соединения» из реверс-комплементарности не выводится — только структурная provenance-проверка + требование независимого review.

## 3. Области 2–3 — негативные тесты R1.1/R1.2 и false-positive контроль

### 3.1 R1.1 (есть в `tests/test_alt_pair_source_gate.py`, реально fail-closed)
- Порт с нетерминальным индексом → `BLOCKED_SOURCE`: `test_falsifier_numeric_in_bounds_but_nonterminal_anchor_must_block`, `test_reverse_complements_do_not_prove_exposed_single_strand_by_themselves`.
- Комплементарная строка, отсутствующая в исходной топологии → отказ: `test_falsifier_complementary_oligos_absent_from_topology_must_block` (`CCCCCC`/`GGGGGG` → `topology sequence mismatch`).
- Дополнительно: неверная полярность (`test_correct_sequence_wrong_polarity_terminal_fails`), неверный индекс (`test_bad_anchor_index_fails`), circular/backbone-нарушения (`test_modified_backbone_fails_strict_preflight`), короткий стрэнд и unknown базы отсекаются `_verified_terminal_segment` (проба P1).

### 3.2 R1.2 (отклоняются — подтверждено тестами и моим независимым RED-репро)
- **A/B-swapped повторное использование порта:** `test_falsifier_reversed_duplicate_port_pair_must_block` — физический нуклеотид учитывается через `used_nucleotides: set[(part, index)]` (строки 245–247, 287–294), порядок A/B не имеет значения.
- **Пересечение занятых нуклеотидов:** `test_distinct_terminal_bonds_with_overlapping_nucleotides_blocked` (8nt на противоположных терминалах одного стрэнда → `nucleotide already assigned`).
- **Нулевая ориентация в .dat:** `test_falsifier_nonunit_particle_orientation_must_block` — `check_orientation()` отбраковывает `|‖o‖−1|>1e-6` и не-ортогональность; zero-вектор даёт девиацию 1.0.
- **NaN в box:** `test_falsifier_nonfinite_box_must_block` — `Configuration.parse` пропускает `nan` (сравнение `nan <= 0` ложно), но гейт требует `math.isfinite(v) and v > 0` (alt_pair_source_gate.py:334); моя проба P5 подтвердила отказ и для `inf`.

### 3.3 Обратное (false-positive) — валидное не отклоняется
- `test_distinct_terminal_bonds_with_nonoverlapping_nucleotides_allowed`: два непересекающихся 6nt порта на противоположных терминалах → `TEST_FIXTURE_STATIC_INPUTS_OK`.
- Моя проба `P3_NoFalsePositives`: **unwrapped PBC-координаты вне box** (x≈40–61 при box 30) + повёрнутый ортонормированный базис → принято. Гейт сознательно не вызывает `check_positions_in_box` (строки 336–339), требуя только `len(conf.particles) == top.nucleotides` — периодические unwrapped координаты не ложно отклоняются.

### 3.4 Независимое RED→GREEN воспроизведение (сверх хостед-CI)
Скриптом `review-evidence/probe_redgreen.py` я запустил HEAD-тест-модуль против **старого R1.1-блоба гейта `1064c879`** (head `3d0b55b`, извлечён `git cat-file`, репозиторий не изменялся): 4 failures — все три заявленных R1.2-фальсификатора (A/B-swap, zero-norm orientation, NaN box) плюс overlap-регрессия. Тот же модуль против HEAD-блоба `c2fdf3a1`: 42/42 OK. Т.е. fix `a5f9f4d`+`a8b3512` действительно устраняет реальные false-positive, а тесты не «подогнаны».

## 4. Область 4 — контроль файлов/путей и провенанс

- **Path traversal / symlink / размер / SHA-256:** `test_relative_parent_escape_rejected`, `test_absolute_path_rejected`, `test_symlink_rejected`, `test_missing_file_rejected`, `test_bad_declared_size_rejected`, `test_size_cap_validation`, `test_tampered_*_digest_rejected`. Мои пробы: вложенный `sub/../../escape.top` → отказ; **symlink-родительский каталог** (`linkdir/…` → symlink на корень) → отказ (проверяется каждый компонент пути, строки 174–179); cap 16 MiB; дайджест 64-hex обязателен для `CONTENT_VERIFIED`.
- **Повторяющиеся JSON-ключи:** `parse_json_no_duplicate_keys` применяется и к манифесту, и к anchor map; тесты `test_duplicate_json_keys_fail_closed`, `test_cli_bad_manifest_double_key_fails`; моя проба с дубликатом `"pairs"` в anchor map → отказ.
- **rights=ALLOWED — не самодекларация, а дисциплина UNKNOWN:** гейт читает файлы только при `rights == "ALLOWED"` (строка 169), но в реальном pack'е все входы `UNKNOWN`, и `validate_manifest` запрещает `UNKNOWN`-входам нести конкретные path/sha/size/url (строки 148–153) и запрещает права на неизвестных входах. `ALLOWED` в enum — user-asserted значение: это честно отражено в audit-доке («лицензия публикации не переносится на неаудированные исходники», «article CC BY 4.0 не устанавливает file-level redistribution») и не подменяется криптографическим доказательством; реальный pack остаётся полностью UNKNOWN.
- **`source_verdict` не повышается из метаданных:** `validate_manifest` жёстко требует `BLOCKED_SOURCE` для всех кандидатов (строка 88) — даже полностью верифицированный вход даёт максимум `C0_SOURCE_FILE_PREFLIGHT_OK_REVIEW_REQUIRED`, т.е. продвижение вердикта вне гейта невозможно.
- **git log -S base_tree_sha:** исходное значение в passport.json (коммит `3a7acbb`) ошибочно копировало commit SHA (`fb3148b…`) в `base_tree_sha`; исправлено в `5e5712e` на `1275a3faba16b6e9528651b12deec83b4337d6f0`. Я проверил: `git rev-parse fb3148b^{tree}` = `1275a3fa…` — **исправленное значение верно**. Оригинальный blob сохранён в ancestry (`3a7acbb`), исправление явно задокументировано в event 0005, `summary.md` (раздел R1.1) и `evidence-map.json → amendments[R1.1].meta_correction`. Диспозиция: **приемлемая документированная pre-acceptance метаданная коррекция** (не тихая правка событий: все 6 event-файлов создавались одним коммитом каждый и после создания не менялись — проверено `git log --follow` по каждому). Инструмент `work_cli` при этом честно рапортует `has_post_terminal_corrections: true`.

## 5. Область 5 — claim ceiling и соответствие claim ↔ evidence

- Pack: `claim_ceiling: BIBLIOGRAPHIC`, `scientific_runs: 0`, `network_bytes_downloaded: 0`, все CAD-входы `UNKNOWN`, `source_verdict: BLOCKED_SOURCE` у обоих кандидатов; имена файлов 256/257 честно помечены `R4_REPORTED_NOT_BYTE_VERIFIED`, 263 — `PAPER_REPORTS_FILE_NOT_FETCHED`. В дереве ветки **нет ни одного сфабрикованного `.top`/`.dat`** (`git diff --name-only | grep -E '\.(top|dat)$'` пуст).
- Receipt гейта: `C0_INPUT_FILE_PREFLIGHT_ONLY; NO SIMULATION; NO ASSEMBLY_VALIDATED`.
- Audit/summary/evidence-map: явные формулы `IMPLEMENTED_WITH_SOURCE_GAP / BLOCKED_SOURCE`, «0 external CAD/oxDNA raw bytes», «это software checks, не scientific reproduction», Reviewer/Verifier = WAIT_EXTERNAL, merge = Human Gate. Grep на инфляцию claims (assembly validated / scientifically proven / relaxed structure / functional connection и т.п.) по всем subject-документам — пусто.
- Библиографическая идентичность подтверждена независимо (метаданные публикаций): DOI `10.1038/s41565-024-01738-7` = «A modular DNA origami nanocompartment…» (Nature Nanotechnology, 2024), DOI `10.1038/s41467-025-56846-2` = «Fully addressable designer superstructures assembled from one single modular DNA origami» (Nature Communications) — совпадают с audit-доком ([MPG Pure / Nature](https://pure.mpg.de/view/item_3604899), [Nature Communications](https://www.nature.com/articles/s41467-025-56846-2)).
- Тесты `PublishedAudit` дополнительно закрепляют потолок: `test_claim_inflation_rejected`, `test_unobserved_files_cannot_gain_concrete_sha`, `test_reported_files_are_not_fabricated_digest_pins`, `test_no_fake_topology_or_follower_ready_claim`, `test_file_roles_are_reports_not_oxdna_inputs`.

## 6. Blockers

**Не найдено.** Ключевые риски, проверенные адверсариально (внутренний индекс как порт; комплементарность без топологии; неверная полярность; A/B-swap; пересечение occupation; zero-norm orientation; NaN/Inf box; traversal/symlink; дубликаты JSON-ключей; самоповышение verdict/claim) — все закрываются fail-closed, подтверждено тестами и моими независимыми пробами.

## 7. Minors (все non-blocking)

- **N1. Robustness CLI (fail-closed сохранён):** манифест-корень не-dict (`[]`, `"str"`, `null`) падает с необработанным `AttributeError` в `evaluate()` (alt_pair_source_gate.py:301; `main` ловит только `OSError`/`ValueError`, строка 373) → traceback и **exit 1** вместо чистого `BLOCKED_INVALID_MANIFEST` с exit 2. Exit никогда не 0 — fail-open нет, но диагностика грязная. Рекомендация: проверять `isinstance(pack, dict)` в `main`/начале `evaluate`. Evidence: `probe_edgecases.out` E1/E2.
- **N2. Stale top-level пины в evidence-map:** `artifacts` и `new_tests: 33` отражают R1.0; на HEAD audit-doc blob = `5199d97e…` (пин `04b785fe…`), гейт = `c2fdf3a1…` (пин `b455b109…`), тесты = `136a957f…` (пин `6ffbabd1…`), тестов в модуле 42 (33 было на R1.0 — сходится по истории 33→37→42). Пины в `amendments` R1.1/R1.2 точны. Топ-уровень нельзя читать как пины HEAD; рекомендуется явная пометка «artifacts = R1.0 snapshot» при следующем append.
- **N3. WORK_QUEUE не содержит R1.2-строки:** R1.2 задокументирован в event 0006, evidence-map и summary — косметический doc-sync.
- **N4. Nuance path-проверки:** `Path("./x")` нормализует `.` (проверка `part in (".", "..")` не срабатывает для `./x`), но эскейпа нет и digest-пин связывает содержимое; безопасности не вредит. Отмечено для точности формулировок (`probe_adhoc.py` P7).
- **N5. Недоступность логов RED-прогонов** (истёк срок GitHub Actions): счётчики «830/2» и «835/3» опираются на implementer-записи; существование прогонов, head-SHA и conclusions проверены мной через API, а RED-поведение независимо воспроизведено локально (§3.4).

## 8. Вердикт

### VERDICT: PASS

**Область действия PASS (строго ограничена):** C0 offline source-readiness гейт, его негативные/позитивные контроли, evidence-пакет и claim-дисциплина на точном HEAD `2e199d6` / TREE `9e8cd2c7a2ddbf5616b38e6922a14f458cac1e8b`. PASS **не означает**: научную приемку, наличие/права исходных CAD-файлов, доказанную сборку, гибридизацию, геометрию или стабильность. Source state остаётся **BIBLIOGRAPHIC / BLOCKED_SOURCE**; 0 научных запусков; никакие статусы этим review не повышены. Отдельный fresh exact-head Verifier (по Issue #77) и Human Gate для merge — по-прежнему обязательны.

**Артефакты review:** `review-evidence/cmd1_unittest.out`, `cmd2_check_consistency.out`, `cmd3_workflow_lint.out`, `cmd4_work_cli.out`, `cmd5_gate_real_pack.out` (+ `*.meta.txt` с exit-кодами), `probe_adhoc.py`/`.out` (15 проб), `probe_redgreen.py`/`.out` (независимое RED→GREEN), `probe_edgecases.out`.

— REVIEWER-76, независимая сессия
