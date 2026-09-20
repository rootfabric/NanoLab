# FRESH_VERIFY_R1 — NL5-002 (независимая fresh exact-head верификация цепочки external reproduction)

Verify id: `NL5-002/FRESH_VERIFY_R1`
Дата verify (UTC): 2026-09-19
Verifier: fresh independent Verifier (отдельная сессия; execution, repair, comparison и review этой цепочки не выполнял, к чатам Implementer/Executor/Orchestrator/Reviewer доступа не имеет, их вердикты не наследовались)

Subjects: пять веток цепочки `work/nl5-002-{a-protocol-freeze, b-external-run, c-compare-repair, b-r2-external-run, c2-compare-r2}-r1` (все от `main @ 48c55b3…`).
Из review-ветки `review/nl5-002-r1` (`docs/evidence/NL5-002/FRESH_REVIEW_R1.md`) взята ТОЛЬКО таблица reviewed subjects (branch → HEAD → TREE); вердикт review не использовался и не влиял.

```
VERIFY_VERDICT = PASS
VERIFIED_BASE  = 48c55b3c4acdd2264527083e3072757be8bd9ada (origin/main; tree 7aca3577e86b21ed8d22fb2742352fd29c3264dd)
SUBJECT DRIFT  = NONE (live HEAD/TREE всех 5 веток == review-таблице, 5/5 match)
```

## 1. Independence statement

- Verifier — fresh-сессия. Все факты ниже получены самостоятельно: живой Git (`git fetch origin --prune` при старте), пересчёты хэшей из git-блобов (`git show`, не рабочая копия), собственные запуски packaged-кода и собственная математика классификации.
- Результаты Executor/Reviewer не принимались на веру: манифесты пересчитаны, анализ перезапущен из raw, классификации пересчитаны моим собственным скриптом (statistics.median по валидным кадрам окна → median-of-3 → включительное envelope-правило), negative controls выполнены в моей tmp-области.
- Репозиторий, main и staging executor'а не изменялись; все записи/подмены — в `/tmp/nl5-002-verify/**`. Доступ к staging `/home/rdpuser/nl5-002-external-r2/workspace/runs/` — чтение, путь provenance raw-траекторий.

## 2. Subject binding (REVIEWED vs VERIFIED, live Git)

| Ветка | REVIEWED HEAD (из FRESH_REVIEW_R1) | VERIFIED HEAD (live origin) | VERIFIED TREE (live origin) | match |
|---|---|---|---|---|
| `work/nl5-002-a-protocol-freeze-r1` | `a41c4502a436b4bc3ee5ecf9e015baf44ef8eea5` | `a41c4502a436b4bc3ee5ecf9e015baf44ef8eea5` | `021f496d3aca2ad9f31a0b544698c35d59a907e2` | **true** |
| `work/nl5-002-b-external-run-r1` | `10b4deb8847794e95c20bc6597ba9d2526f5ee19` | `10b4deb8847794e95c20bc6597ba9d2526f5ee19` | `bb722fb9391cd956cb45d77de5415958006f33e5` | **true** |
| `work/nl5-002-c-compare-repair-r1` | `a1ba5173d7d78fd944da31cc7b5c2c476d423427` | `a1ba5173d7d78fd944da31cc7b5c2c476d423427` | `e474f9e680d96de8414822e7d0f10021dae84d2d` | **true** |
| `work/nl5-002-b-r2-external-run-r1` | `a8dfe8ce220c73131e08f4ab806618a2c0400b16` | `a8dfe8ce220c73131e08f4ab806618a2c0400b16` | `0c940f3e3bd7ec2722be454be56d70033d76f01c` | **true** |
| `work/nl5-002-c2-compare-r2-r1` | `b0aff56845fd67a4b410db9b2b932ee6b50a5eb5` | `b0aff56845fd67a4b410db9b2b932ee6b50a5eb5` | `66523e017f970ab7982e5a36acf8e20757281752` | **true** |

**VERIFIED subjects == REVIEWED subjects: 5/5, drift отсутствует.** `origin/main = 48c55b3c4acdd2264527083e3072757be8bd9ada` == REVIEWED_BASE.

## 3. Package pins v0.1.1 (ветка C, пересчёт из git-контента)

`git archive a1ba5173 releases/nanolab-components-v0.1.1` → независимый пересчёт sha256+size всех 42 записей `RELEASE_MANIFEST.json`:

| Группа записей | Результат |
|---|---|
| non-pyc | **35/35 byte-exact** (sha256 и size совпали, MISMATCHES: NONE) |
| `convention/nlbl_convention/__pycache__/*.pyc` | **7/7 запиненов, файлов НЕТ в git-дереве** (missing: `__init__/canonical/hf_canonical/observables/oxdna_conf/oxdna_topology/reproduction_rule .cpython-310.pyc`) |

- Это ровно задокументированный packaging finding (F-orch1/FR-3): расхождения только на 7 pyc-записях, научные поверхности pinned верно.
- `RELEASE_MANIFEST.json` v0.1.1: мой sha256 = `88c1f58061f15fde44225900f0577acbf2634d3f4a75fb96a2cedca24fd1bfef` (8697 B); `convention/analyze_hinge.py` sha256 = `300ecd58703c50aa9e24976ab92e9aac61f9d60e49f18e68a58b131861f3ae60`.
- Карточки v0.1.1 (мои sha256): 0b `8d4515a7…93d81`, 11b `976f02b1…f0814`, 32b `6a4f55fd…f3663`, 53b `6b22a9f4…347c`, 74b `5894f420…50bb`.

**Сравнение с v0.1.0 (main)**: для карточек 0b/11b/32b/53b `reproduction.expected` **идентично** (канонизированное JSON-сравнение, включая `reference_replica_envelope_deg`): 0b [65.095434789, 67.236579608]; 11b [72.165683993, 74.533109426]; 32b [77.4927314, 79.877463339]; 53b [131.049227687, 135.285186059]. Карточка 74b byte-identical целиком. Leaf-level diff карточек 0b/11b/32b/53b — только packaging-строки (`requires`/`steps` 3–5/`tolerance_policy`/`protocol_pins.notes`); числовые научные поля не тронуты.

## 4. Artifact hashes (ветка B-R2, по git-блобам)

| Проверка | Мой результат |
|---|---|
| `EVIDENCE_SHA256SUMS.txt` (72 файла) vs git-блобы | **72/72 OK** |
| `run_output_digests.json` | `entry_count=84`; **12 прогонов × 7 файлов uniform** (`traj.dat, energy.dat, last_conf.dat, log.dat, run_meta.json, stderr.log, stdout.log`); все записи с sha256+size+run_id+producer; дублей (run_id,path) нет; IDs = ровно 6 базовых + 6 `-R` |
| Сверка digests с ФАКТИЧЕСКИМ staging `/home/rdpuser/nl5-002-external-r2/workspace/runs/<ID>/` | **84/84 OK (sha256+size)** — перекрыл все 12 прогонов (требование было ≥4, включая `-R`); missing=0, mismatch=0 |
| `artifact_manifest.json` | 427 записей, все пути уникальны |
| `EXTERNAL_REPRODUCTION_REPORT.md` sha256 | `5aee793479292eafa6095f91533aca949bfbad596949d19fd7ee8daca910f421` (мой пересчёт блоба) |
| staging-каталог | 12 кампаний + 6 aborted wave-1 (без `-R`) + 2 smoke — согласуется с D1 (aborted ID вне кампании) |

## 5. Reproduction из raw (packaged-анализатор ветки C, моя tmp-область)

Запуск `convention/analyze_hinge.py run` (пакет извлечён из git-ветки C) на staging raw traj/energy/top с теми же окнами/arm-manifests/exit-code-файлами, что у исполнителя, отчёт — в `/tmp/nl5-002-verify/repro/MY_*`:

| Реплика | окно | мой `replica_median_deg` (raw-пересчёт полным float) | ingested `replica_median_deg` | расхождение |
|---|---|---|---|---|
| EXTERNAL-0b-1 | 200000 | 68.3897817955 | 68.389781796 | 0.00e+00 (после canonical-округления) |
| EXTERNAL-11b-1 | 150000 | 72.255209867 | 72.255209867 | 0.00e+00 |
| EXTERNAL-32b-1R | 150000 | 75.180138343 | 75.180138343 | 0.00e+00 |
| EXTERNAL-53b-1R | 150000 | 132.41188514 | 132.41188514 | 0.00e+00 |

- Покоадровное сравнение (time, angle_deg, pairs_fraction_v2, long_bond_fraction, displacement_max, valid, angle_status): **0 несовпадений, max |d| = 0.00e+00** по всем кадрам всех 4 реплик; frames_total/in_window/valid_in_window и engine_exit_code совпали.
- **Campaign на трёх ingested run-jsons (11b)** packaged-кодом в моей tmp: outcome **MATCH**, statistic **73.560609814**, envelope [72.165683993, 74.533109426] — байт-в-байт совпало с ingested `campaign_11b.json`.

## 6. Classification math (мой независимый пересчёт, не packaged-код)

Метод: `frames[]` каждого `EXTERNAL-*_analysis.json` (git-блобы B-R2) → фильтр `valid AND angle_status=="OK" AND time<=window` → per-replica median → median-of-3 → включительное envelope-правило карточки v0.1.1.

| карта | мои per-replica medians (deg) | мой median-of-3 | envelope v0.1.1 | МОЙ исход | executor (campaign JSON) | C2 comparison.json | согласование |
|---|---|---|---|---|---|---|---|
| 0b | 68.3897817955 / 69.6002966125 / 67.5862756410 | **68.3897817955** | [65.095434789, 67.236579608] | **MISMATCH** | MISMATCH (68.389781796) | MISMATCH | ✓ |
| 11b | 72.255209867 / 73.560609814 / 75.35617795 | **73.560609814** | [72.165683993, 74.533109426] | **MATCH** | MATCH (73.560609814) | MATCH | ✓ |
| 32b | 75.180138343 / 74.713050721 / 76.100697787 | **75.180138343** | [77.4927314, 79.877463339] | **MISMATCH** | MISMATCH (75.180138343) | MISMATCH | ✓ |
| 53b | 132.41188514 / 130.244172898 / 136.169087714 | **132.41188514** | [131.049227687, 135.285186059] | **MATCH** | MATCH (132.41188514) | MATCH | ✓ |

- Согласование мой пересчёт == executor == C2: **4/4**, до 1e-9 (у исполнителя округление до 9 знаков).
- Directional separation: **0b** — все 3 fresh строго ВЫШЕ (min fresh 67.5862756410 > hi 67.236579608); **32b** — все 3 строго НИЖЕ (max fresh 76.1006977870 < lo 77.4927314).
- WO-level по frozen mapping WO-A: **MISMATCH** (≥1 карта MISMATCH) — совпадает с C2 `wo_level.verdict = MISMATCH`, `mismatch_cards = [0b, 32b]`, `numeric_repro_condition_met = false`.

## 7. Executor report (первоисточники)

- **13 нумерованных секций** (§1 Executor identity … §13 Findings) + Self-check — все присутствуют; плейсхолдеров **0** (grep `TODO|TBD|PLACEHOLDER|FIXME|XXX|lorem|заполнить|подставить` = 0; шаблонные `<ID>`/`<v>` в описаниях команд — легитимная нотация).
- **Exit codes 12/12**: мой подсчёт `engine_exit_code==0` по всем 12 ingested `_analysis.json` = **12/12**; exit codes наблюдаемые (`exit_code.txt` wrapper'ов), aborted wave-1 (6 ID) вне кампании.
- **frame0 4/4**: `logs/frame0_oracle_summary.json` — computed == card `design.angle_frame0_deg` exact match 4/4 (0b 66.886745865; 11b 74.357957026; 32b 77.477102136; 53b 132.949606811). Дополнительно я САМ запустил packaged `frame0` на staging first-conf (0b и 11b): 66.886745865 OK / 74.357957026 OK — совпадение.
- **Gates**: `logs/upstream_digest_gate.json` — 12 строк (9 уникальных upstream-файлов, pro_CPU.in ×4 варианта): **size_gate PASS 12/12, blob_sha1_gate PASS 12/12**; `published_sha256_status=CONTENT_VERIFIED` 6/12 (0b-тройка + pro_CPU.in) — механика FR-1 (булев `all_pass=false` в C2 comparison.json противоречит фактическому PASS-логу обязательных гейтов; на классификацию не влияет — пересчитано мною независимо, §6).
- **Seeds frozen до запусков**: `seeds_frozen.json` `frozen_at_utc = 2026-09-19T02:08:21Z`; `campaign_start_utc.txt = 02:30:08Z` — frozen раньше стартов. Моя сверка логов запуска (wave-1 12 строк + wave-2 6 строк = **18 уникальных ID**, дублей нет): все 12 кампанных ID присутствуют; **18/18 seed ∈ `seeds_frozen[variant]`**; `-R`-перезапуски — те же frozen seeds; reference seeds 201004/202008/203012 не использованы; steps по вариантам корректны.

## 8. Negative controls (моя tmp-область, репо/staging не изменялись)

| # | Tamper | Наблюдаемый исход | Вывод |
|---|---|---|---|
| NC-1a | Копия пакета; в карточке 11b подменено ПОЛЕ `reference_replica_envelope_deg` ([72.165…, 74.533…] → +10 = [82.165…, 84.533…]); campaign на тех же 3 ingested run-jsons | outcome **НЕ изменился** (MATCH) | Честное наблюдение: packaged `classify()` НЕ читает производное поле envelope — он строит envelope как min/max из `reference_replica_medians_deg`. Поле envelope в карточке — документирующее; машина-правило привязано к медианам. |
| NC-1c | Копия пакета; подменён РЕАЛЬНЫЙ вход правила: минимальный элемент `reference_replica_medians_deg` (72.165683993 → +10); тот же campaign | **MATCH → INCONCLUSIVE** («campaign statistic is outside the reference envelope without complete directional separation», rule envelope стал [74.218071238, 82.165683993]) | **Правило реально читает карточку**: подмена envelope-базиса (reference-медиан) меняет исход. Требование NC-1 выполнено на авторитетном входе правила. |
| NC-2 | В копии ingested `EXTERNAL-11b-2_analysis.json` подменена fresh median (73.560609814 → 80.0); packaged campaign на tampered тройке | **MATCH → INCONCLUSIVE**, statistic пересчитан в 75.35617795 (median [72.255209867, 80.0, 75.35617795]) | **Правило реально считает median-of-3**, а не эхо входа. |
| NC-3 | `python3 reproduction/reproduce.py verify` в СВЕЖЕМ git-checkout пакета v0.1.1 из ветки C (`git archive` в `/tmp/nl5-002-verify/nc3`) | **exit=3, ok=false, ровно 7 ошибок — все «missing file …cpython-310.pyc»**; остальные 35 non-pyc записей верифицированы чисто, иных ошибок 0 | Независимое подтверждение F-orch1/FR-3: fresh-checkout verify падает именно на 7 запиненных pyc, которых нет в git-дереве; научные поверхности pinned корректно. Это packaging-finding, не scientific gate. |

## 9. Scope (diff base→HEAD каждой ветки) и канонический main

| Ветка | Фактический diff `48c55b3..HEAD` | Allowed | Нарушений |
|---|---|---|---|
| A | `docs/work/WO-NL5-002-A-R1.md`, `EX-NL5-002-A-R1/**` (6), `docs/work/templates/EXTERNAL_REPRO_REPORT_TEMPLATE_R1.md` — 8 файлов | WO+executions+templates | 0 |
| B-R1 | `docs/work/executions/EX-NL5-002-B-R1/**` — 12 файлов | EX-NL5-002-B-R1/** | 0 |
| C | `releases/nanolab-components-v0.1.1/**` (36), `docs/work/WO-NL5-002-C-R1.md`, `EX-NL5-002-C-R1/**` (6) — 42 файла | releases+reproduction(packaged)+WO+EX-C-R1 | 0 |
| B-R2 | `docs/work/executions/EX-NL5-002-B-R2/**` — 79 файлов | EX-NL5-002-B-R2/** | 0 |
| C2 | `docs/work/WO-NL5-002-C2-R1.md`, `EX-NL5-002-C2-R1/**` (7) — 8 файлов | WO-C2+EX-C2-R1 | 0 |

- `project/`, `docs/control/`, `docs/work/WORK_QUEUE.md` — **0 файлов** во всех пяти diff (grep по префиксам).
- `project/state.json` на main: `frontier = NL5`, `task_status/NL5-002 = READY`, `execution.external_reproductions = 0` — ветками не менялся (корректно до Human Gate merge).

## 10. Механические проверки (переисполнены мной)

| Команда | Где | Результат |
|---|---|---|
| `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-002-C2-R1` | worktree `nl5-002-c2-compare` @ `b0aff56` (без `git pull`) | **ok=true**, `HANDOFF_READY`, terminal handoff есть, `has_post_terminal_corrections=false`, `passport_sha256=be460d1c…2f6e`, exit 0 |
| `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | main checkout @ `48c55b3` | **ok=true**, 0 errors / 0 warnings, head/tree = 48c55b3…/7aca3577…, exit 0 |
| `python3 -m unittest discover -s tests -t .` | main checkout | **Ran 360 tests — OK** (11.2s) |

## 11. Отклонения (наблюдения Verifier'а, ни одно не является FAIL)

1. **NC-1a nuance (INFO)**: производное поле карточки `reference_replica_envelope_deg` не является входом packaged-правила — классификация привязана к `reference_replica_medians_deg` (min/max = envelope). Подмена производного поля исход не меняет; подмена reference-медиан меняет (NC-1c). Для будущей v0.1.2 можно синхронизировать документацию/валидацию того, какое поле авторитетно. На VERIFIED-цепочку не влияет: campaign JSONs классифицированы ровно по карточным reference-медианам, и card envelope == min/max этих медиан (проверено мной численно на 4 картах).
2. **Packaging findings подтверждены** (7 pyc в манифесте без файлов в git; `RIGHTS.json package_version: 0.1.0` при VERSION 0.1.1) — процессные/упаковочные, научные числа и поверхности не затрагивают; кандидаты в bounded v0.1.2 (вне этого verify).
3. Известные из review процессные факты (future-timestamps errata, D1/D2 перезапуски, FR-1 булев флаг) мной не оспариваются — spot-check первоисточников (seeds/launch logs/gate JSON/frame0/exit codes) дал согласие; их полная re-аудит вне объёма exact-head verify.

## 12. Claim ceiling

Во всех пяти паспортах `claim_class = C1_COMPUTATIONAL_REPRODUCTION`, `risk_class = MEDIUM`. WO-level MISMATCH не повышает claims карточек и frontier: `project/state.json` остаётся `NL5-002 READY`, `external_reproductions = 0` до merge. Научная интерпретация MISMATCH (platform/FP-чувствительность) — гипотеза для отдельного решения Human Gate, не вердикт этого verify.

## 13. Вердикт

Все обязательные проверки зелёные на exact subjects (5/5 HEAD/TREE == review-таблице, drift отсутствует): манифест v0.1.1 35/35 non-pyc byte-exact + ожидаемые 7 pyc-расхождений; 72/72 evidence sha256 по блобам; 84/84 digests == staging raw; мой перезапуск packaged-анализа из raw 4/4 реплик — 0.00e+00 расхождение по всем кадрам; мой независимый пересчёт классификации 4/4 == executor == C2, WO-level MISMATCH [0b, 32b]; все 4 negative control-исхода наблюдаемы и объяснимы (NC-1c/NC-2/NC-3 сработали, NC-1a дал честное наблюдение о неавторитетности производного поля); scope 5/5 веток чист; механика (validate C2 / check-consistency / 360 tests) — ok.

```
VERIFY_VERDICT = PASS
SUBJECT_BINDING = VERIFIED == REVIEWED (5/5)
MERGE TO MAIN  = остаётся Human Gate (этот вердикт его не заменяет)
```

*Verify evidence: этот файл + живой Git; мои расчёты воспроизводимы из блобов `work/nl5-002-b-r2-external-run-r1` (analysis/run_output_digests/EVIDENCE_SHA256SUMS) и `work/nl5-002-c-compare-repair-r1` (releases/nanolab-components-v0.1.1) + staging raw `/home/rdpuser/nl5-002-external-r2/workspace/runs/`.*
