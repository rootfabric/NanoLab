# NANOLAB PR76 EXACT-HEAD VERIFICATION — independent VERIFIER-76-INT-R1 (main-integration R1)

**Verifier session:** `VERIFIER-76-INT-R1-17d3b2a1` — отдельная независимая сессия, fresh клон
`~/NanoLab-verify76` на native Ubuntu (git 2.34.1, Python 3.10.12), detached HEAD,
`git status --porcelain` пуст на протяжении всей проверки. Сессия не разделяет identity
ни с Implementer, ни с Director, ни с Reviewer (`REVIEWER-76-INT-R1-cb193b02`, отдельная
машина/сессия). Все доказательства вычислены заново в этой сессии; результаты Reviewer
использовались только для сравнения, не как источник.

Claim ceiling: **C0 SOFTWARE ONLY. SCIENCE_RUNS = 0.**

Evidence: эта директория (`command_log.txt`, `git_blob_evidence.txt`, `unittest_972.log`,
`unittest_main_baseline_930.log`, `probe_negatives_verifier_own.txt`,
`probe_fixtures_generator.py`, `SHA256SUMS`).

---

## 1. Subject identity (SUBJECT_DRIFT = NONE)

Получено независимо через fresh clone + `git fetch --all --prune` + exact checkout:

```text
HEAD     = cf413b053677de17beaf2dcf3ce9b86868361b3e   (= PRODUCT_HEAD, = refs/pull/76/head)
TREE     = 560dc913a71a237d3c452a5a2e492e213b232911   (= PRODUCT_TREE)
PARENT_1 = 9fed48a88bb60d5bdfa4a8280e22366366e42f69
PARENT_2 = 862c7c579cc667c7ed2bae85b4b4fbbb3dfa8fba (= origin/main на момент проверки)
MERGE_BASE(P1,P2) = fb3148b46a9638167168a46cb170902a4ad9e8d2
git status --porcelain = (пусто)
```

Проверено по GitHub API: `main` = `862c7c5…`, `refs/pull/76/head` = `cf413b0…`,
PR #76 `state=open`, `mergeable=true`. Дрейфа subject нет.

**История не переписана.** `git merge-base --is-ancestor`: P1 и P2 (main) — предки HEAD;
все 20 коммитов PR #76, перечисленных GitHub API (`3a7acbb…cf413b0`), — предки
`cf413b0` (20/20). Force-push/rewrite не обнаружены.

## 2. Целостность дерева (blob-level, вычислено независимо)

Полные `git ls-tree -r` всех трёх деревьев + побайтовые сравнения
(`git_blob_evidence.txt`):

- Путей: main = **2501**, parent1 = **2458**, HEAD = **2556**;
  `paths(HEAD) == union(paths(main), paths(parent1))` — множества совпали точно
  (`diff` пуст): **0 посторонних, 0 потерянных путей**.
- Пересечение main∩parent1 = 2403; additions base→p1 = **55**, base→main = **98**,
  множества добавлений дизъюнктны (0 общих путей); удалений (D) нет ни в одном
  направлении (base→p1, base→main, p1→HEAD, main→HEAD — все 0).
- Blob-дрейф main→HEAD: **единственное** изменение — `docs/work/WORK_QUEUE.md`
  (`6d278ea6…` → `f5555fd1…`) — ожидаемое изменение очереди. Все остальные 2500
  путей main сохранены побайтово (0 дрейфа).
- **55/55 новых файлов PR #76 сохранили исходные Git-блобы** parent1 → HEAD
  (проверка `git rev-parse` по каждому из 55 путей — 55 совпадений, 0 mismatch).
- `project/state.json` (`b8197557…`), `project/plan.json` (`89975c1b…`),
  `project/infra-state.json` (`5056b8f5…`), `project/infra-plan.json` (`d400669d…`)
  — blob-идентичны main. Следовательно, frozen NL5/NL6 контент и все принятые
  records не тронуты.

## 3. WORK_QUEUE.md — побайтовая реконсиляция (ДОКАЗАНО)

```text
base fb3148b : 3d511a28… (67,261 B)
main 862c7c5 : 6d278ea6… (80,329 B)   — main_append = 13,068 B
parent1 9fed48a: a95c98f1… (68,156 B) — pr76_append = 895 B
HEAD cf413b0 : f5555fd1… (81,224 B)
```

Побайтово (cat-file + python bytes-сравнение):

- `FINAL == MAIN_WORK_QUEUE + ORIGINAL_PR76_APPEND` → **True** (81,224 = 80,329 + 895);
- `FINAL == BASE + MAIN_APPEND + PR76_APPEND` → **True**;
- `FINAL == P1 + MAIN_APPEND` → False (ожидаемо: порядок принят main-first);
- ORIGINAL_PR76_APPEND (895 B) встречается в финальной очереди **ровно 1 раз**,
  в main-очереди **0 раз**; финал заканчивается append-ом контiguously;
- append = ровно **две NL7-записи** в исходном порядке: `R1.0`
  (496 B, `WO-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1`) и `R1.1`
  (397 B, `…R1.1 (C0 narrow continued)`), каждая встречается в финале ровно 1 раз;
  R1.2-строки в очереди нет (известное N3);
- SHA-256 содержимого финального блоба: `9dfabc8f3f2d0f9b3faf371c220d9613ed9701f05dbc9e75ae2a63f2d5bafd97`.

**`FINAL_WORK_QUEUE = MAIN_WORK_QUEUE + ORIGINAL_PR76_APPEND` — подтверждено побайтово.**

## 4. S17 × NL7 совместимость

- Оба направления используют общие строгие парсеры
  `scripts/hinge_family/oxdna_topology.py` / `oxdna_conf.py`; в
  `knowledge_pack` нет их копий, а `hinge_family` не импортирует `knowledge_pack`
  (циклов/дублирования нет).
- Семантика терминалей перепроверена по коду гейта: 3p ⇔ `n3 == -1`,
  5p ⇔ `n5 == -1`, обход в 5′→3′ с реверсом для 3p; occupancy-учёт ведётся по
  `(part, nucleotide)` — независимо от порядка A/B.
- В `tests/` добавлен только `tests/test_alt_pair_source_gate.py` (42 теста).
- Арифметика регрессии независимо подтверждена: точное дерево main `862c7c5` →
  **Ran 930 tests — OK, exit 0** (отдельный worktree); точное дерево HEAD →
  **Ran 972 tests — OK, exit 0**; 930 + 42 = 972; все прочие тестовые блобы
  идентичны main → регрессий S17/NL5 нет.

## 5. Обязательные проверки (точное дерево cf413b0, эта сессия)

```text
python3 -m unittest discover -s tests -t .                              -> Ran 972 tests — OK, exit 0
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .    -> ok=true, exit 0
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .            -> ok=true, blocking=0, exit 0
PYTHONPATH=scripts python3 -m harness.work_cli validate \
  docs/work/executions/EX-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1            -> HANDOFF_READY, exit 0
PYTHONPATH=scripts python3 -m knowledge_pack.alt_pair_source_gate \
  docs/research/ALT_DNA_TWO_PART_SOURCE_PACK_R1.json \
  --candidate S23_NARCISSUS_ECHO --root .                                -> BLOCKED_SOURCE, exit 2
```

`BLOCKED_SOURCE, exit 2` на реальном пакете — **корректная fail-closed защита**
от неподтверждённых исходников (все пять input-records `UNKNOWN` →
`SOURCE_BYTES_NOT_OBSERVED`; `scientific_runs: 0` в receipt).

## 6. Независимые негативные контролы (собственные, не Reviewer's)

Собственный synthetic-fixtures набор (генератор и полный лог в evidence;
20 сценариев): два 12-nt стренда, 6-nt 3'/5'-overhangs (CATGCA/TGCATG),
CONTENT_VERIFIED + ALLOWED пины, anchor map с реверс-комплементарными сегментами.

**Позитивный контроль (проверка отсутствия ложных отказов):**

```text
P+  валидный fixture с unwrapped-PBC координатами ВНЕ бокса
    -> TEST_FIXTURE_STATIC_INPUTS_OK, exit 0
```

Гейт не требует wrapped-позиций — валидные oxDNA PBC-конфигурации не отклоняются.

**Негативные контролы (все fail-closed):**

```text
N01  NaN в box                          -> BLOCKED_SOURCE exit 2 (nonfinite box)
N02  нулевая ориентация                 -> BLOCKED_SOURCE exit 2 (orientation deviation 1.0)
N03  A/B-swapped повторное использование тех же терминалей
                                        -> "nucleotide already assigned to another interface bond", exit 2
N04  внутренний (нетерминальный) якорь  -> "not a 3p strand terminus (internal anchor)", exit 2
N05  верная последовательность, неверная полярность
                                        -> "not a 5p strand terminus (internal anchor)", exit 2
N06  сегмент длиннее стренда            -> "invalid segment length", exit 2
N07  tamper того же размера             -> "source SHA-256 mismatch", exit 2
N08  rights=RESTRICTED                  -> "RIGHTS_NOT_CLEARED (RESTRICTED)", exit 2
N09  rights=UNKNOWN при CONTENT_VERIFIED -> "RIGHTS_NOT_CLEARED (UNKNOWN)", exit 2
N10  файл > 16 MiB                      -> "file exceeds 16 MiB cap", exit 2
N10B declared<=cap, actual>cap          -> "file exceeds 16 MiB cap", exit 2 (read-time cap)
N11  declared size +1                   -> "file size mismatch", exit 2
N12  абсолютный путь                    -> "path traversal or absolute path", exit 2
N13  "../" traversal                    -> "path traversal or absolute path", exit 2
N14  symlink в пути                     -> "symlink in source path", exit 2
N15  дубликат JSON-ключей               -> BLOCKED_INVALID_MANIFEST, exit 2
N16  claim inflation (не BIBLIOGRAPHIC) -> manifest error, exit 2
N17  не-dict корень манифеста           -> exit 1 (известное N1: fail-closed, но грязная диагностика; 0 не выдаётся никогда)
N18  неизвестный rights-словарь         -> "unknown rights value", exit 2
N19  объявленный, но отсутствующий файл -> "missing or outside-root source file", exit 2
```

Дополнительно проверен N4-обход: путь `./p_plus/alpha.top` проходит проверку `.`
(Python `Path.parts` отбрасывает `.`), но остаётся в пределах root
(`resolve()` + `is_relative_to`), SHA-256/size проверки сохраняются — обход
косметический, root-escape нет. NON-BLOCKING.

## 7. Hosted CI на точном HEAD (независимо по API)

```text
Run 39868768984: workflow hosted-ci.yml, event=pull_request, attempt=1
head_sha = cf413b053677de17beaf2dcf3ce9b86868361b3e  (exact HEAD)
status = completed, conclusion = success
check-run "RC0 hosted validation (H0)": completed / success
  Check 1/5 machine contracts JSON        -> success
  Check 2/5 harness control consistency   -> success
  Check 3/5 passports/work events         -> success
  Check 4/5 workflow negative-control lint-> success
  Check 5/5 validation gate unit tests    -> success
failed steps = 0
```

Локальные 972/972 на идентичном дереве это корроборируют. Локальная регрессия
запускалась на том же HEAD, для которого CI зелёный.

## 8. Carry-over замечания: N1–N5, R-N1, R-N2 (все перепроверены, все NON-BLOCKING)

- **N1** (не-dict корень → `AttributeError`, exit 1 вместо чистого exit 2) —
  воспроизведён независимо (N17 выше): exit 1, никогда 0, fail-closed сохранён.
- **N2** (stale top-level пины evidence-map) — все evidence-map блобы идентичны
  main (дрейф main→HEAD = только WORK_QUEUE.md), оценка Reviewer в силе без изменений.
- **N3** (в очереди нет R1.2-строки) — подтверждено побайтово: append = ровно
  R1.0 + R1.1 дословно; R1.2 задокументирован вне очереди. Требование интеграции
  соблюдено.
- **N4** (`Path("./x")` обходит проверку `.`) — воспроизведён; обход косметический,
  root-escape нет (см. §6).
- **N5** (истёкшие логи RED-прогонов) — существование RED/GREEN прогонов
  подтверждено независимо по API: run `39538287299` completed/**failure** (RED),
  run `39538562254` completed/**success** (GREEN fix). Негативное поведение
  независимо покрыто 42 тестами модуля и пробниками N01–N19.
- **R-N1** (исторический 33-test текст очереди сохранён дословно) — покрыт
  побайтовой реконсиляцией §3: append перенесён без изменений.
- **R-N2** (combined status endpoint pending) — подтверждено: commit status API
  для `cf413b0` возвращает `state=pending`, `total_count=0` при успешном
  check-run H0; успешность подтверждена check-runs API. NON-BLOCKING.

**Новых блокирующих находок не обнаружено.**

## 9. Научные ограничения (сохранены)

```text
SCIENCE_RUNS = 0
S17_FOLLOWER = NOT_RECONSTRUCTED
NL7_SOURCE   = BIBLIOGRAPHIC / BLOCKED_SOURCE
ASSEMBLY_VALIDATED = false
NL5 / NL6 / NL7 = UNCHANGED
```

Все receipts гейта печатают `scientific_runs: 0`; claim-инфляция блокируется
(N16). VERIFIED не повышает научный статус и не является научным PASS — это
подтверждение программной интеграции на exact HEAD.

---

## Итог

```text
NANOLAB PR76 EXACT-HEAD VERIFICATION

PRODUCT_HEAD = cf413b053677de17beaf2dcf3ce9b86868361b3e
PRODUCT_TREE = 560dc913a71a237d3c452a5a2e492e213b232911
MAIN_HEAD = 862c7c579cc667c7ed2bae85b4b4fbbb3dfa8fba
VERIFIER_SESSION = VERIFIER-76-INT-R1-17d3b2a1 (fresh clone, detached HEAD, clean)
REVIEWER_INDEPENDENCE = CONFIRMED (отдельная сессия/identity от Reviewer и Implementer; доказательства вычислены заново, сверка совпадений по всем пунктам)
PARENTS_AND_ANCESTRY = P1=9fed48a8, P2=862c7c57 (=main), merge-base fb3148b4; 20/20 PR-коммитов предки HEAD; main — предок HEAD; rewrite отсутствует
MAIN_BLOB_INTEGRITY = 2501/2501 путей main сохранены; единственный дрейф — docs/work/WORK_QUEUE.md (ожидаемое изменение очереди); 0 потерянных/посторонних путей (2556 = union(2501,2458))
PR76_BLOB_IDENTITY = 55/55 исходных блобов PR #76 сохранены; additions base→p1=55 и base→main=98 дизъюнктны; D=0
WORK_QUEUE_RECONCILIATION = PROVEN byte-exact: FINAL(81,224B) == MAIN(80,329B) + ORIGINAL_PR76_APPEND(895B); append встречается 1 раз, 2 NL7-записи (R1.0+R1.1) по одному разу
S17_NL7_COMPATIBILITY = OK: общие строгие парсеры без циклов/дублирования; 3p⇔n3==-1, 5p⇔n5==-1; occupancy по (part,nucleotide); в tests/ добавлен только tests/test_alt_pair_source_gate.py
UNIT_TESTS = 972/972 OK exit 0 (main baseline 930/930 OK на 862c7c5; 930+42=972)
HARNESS = check-consistency exit 0; workflow_lint exit 0 (blocking 0); work_cli validate exit 0 (HANDOFF_READY); source gate на реальном паке BLOCKED_SOURCE exit 2 (корректный fail-closed)
NEGATIVE_CONTROLS = 19/19 негативных сценариев fail-closed (exit 2; N17 exit 1, известное N1, никогда не 0) + 1/1 позитивный unwrapped-PBC сценарий TEST_FIXTURE_STATIC_INPUTS_OK exit 0
HOSTED_CI = run 39868768984 head_sha=cf413b0… completed/success; H0 check-run success; Check 1/5..5/5 success; 0 failed steps
BLOCKING_FINDINGS = NONE
NONBLOCKING_FINDINGS = N1 (воспроизведён, fail-closed), N2 (блобы evidence-map = main), N3 (подтверждён побайтово), N4 (воспроизведён, косметика, root-escape нет), N5 (RED 39538287299 failure / GREEN 39538562254 success подтверждены по API), R-N1 (покрыт побайтовой реконсиляцией), R-N2 (combined status pending подтверждён)
SCIENTIFIC_CLAIMS = C0 SOFTWARE ONLY; SCIENCE_RUNS=0; S17_FOLLOWER=NOT_RECONSTRUCTED; NL7_SOURCE=BIBLIOGRAPHIC/BLOCKED_SOURCE; ASSEMBLY_VALIDATED=false; NL5/NL6/NL7 UNCHANGED
FINAL_VERDICT = VERIFIED
EVIDENCE_BRANCH = verify/pr76-main-integration-r1
PUBLISHED_COMMENT = PR #76 (issue comment; issue:write недоступен — см. ограничение в комментарии)
NEXT_ACTION = Director: owner-authorized merge PR #76 с expected_head_sha=cf413b053677de17beaf2dcf3ce9b86868361b3e, затем post-merge проверка main и H0; научные ограничения §9 сохраняются
```

**FINAL_VERDICT: VERIFIED** (интеграция PR #76 в main на exact HEAD `cf413b0`
подтверждена независимо; VERIFIED не повышает научный статус).
