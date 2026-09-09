# NL1-002 — VERIFIER VERDICT R2 (независимая верификация исполнением)

**Вердикт: `FIX_REQUIRED`**

- Verifier: fresh session R2 (независимая, не переиспользует контекст исполнителя/reviewer'а). Дата: 2026-09-09.
- Verified subject: `work/nl1-002-reference-run-r1` @ **`ec7e3edc83a3434d96222a0a8a94b03f7fa10e23`** (base `71535d00a2e729349eea2337217a2c591ed9317d`).
- Verifier branch: `verify/nl1-002-reference-run-r2` (этот HEAD фиксируется последним коммитом ветки; merge НЕ выполнялся).
- Метод: **verification исполнением** — воспроизведение пересборки engine, собственного smoke-прогона, дайджестов, анализа и статистики. Чужим вердиктам верификатор не доверял; R1-вердикты не использовались как входные данные.

## 0. Преамбула: superseding R1

Настоящий вердикт **superseding `b405a7e`** (verifier verdict R1, ветка `verify/nl1-002-reference-run-r1`). Основание аннулирования R1: **role-mixing** — R1-верификация была написана той же оркестрирующей сессией, что и reviewer-вердикт (`7b12012`), что нарушает требование независимости VERIFIER от REVIEWER (`HARNESS_REVIEW_AND_EVIDENCE_RU` §Роли, `WO-NL1-002` маршрут). Вердикты R1 не рассматривались как достоверные и не воспроизводились; все проверки ниже выполнены заново этой сессией.

## 1. Exact subject

| проверка | результат |
|---|---|
| `ec7e3ed…` резолвится; ветка верификатора создана от exact subject | OK |
| `merge-base --is-ancestor 71535d0 ec7e3ed` → exit 0 | OK — subject строго потомок base |
| `ls-remote origin main` = `71535d0` | OK — base = канонический main |
| `ls-remote origin work/nl1-002-reference-run-r1` = `c44b209` | OK с оговоркой: remote-ветка ушла вперёд subject на 4 коммита R1-вердиктов (`7b12012`, `b405a7e`, 2 merge); `git diff --stat ec7e3ed c44b209` = только 2 вердикт-файла (+163 строки), work-content идентичен бит-в-бит; `ec7e3ed` — ancestor `c44b209` |
| свежий worktree от exact subject, чистый `status` | OK |

## 2. Воспроизведение исполнением — все проверки прошли

Подробные протоколы: `VERIFIER_PROGRESS_R2.md`, `verify-r2/ENGINE_REBUILD_AND_SMOKE_R2.md`.

| # | проверка | результат |
|---|---|---|
| D0 | Engine acquisition: probe-repo, `fetch --depth 1 origin 00dc7fb9…`, `rev-parse HEAD` | **MATCH** точный пин |
| D0a | cmake 3.31.6 re-acquired; SHA-256 = пин `5a1133ff…` (§2) | **MATCH** (первая попытка скачивания оборвана прокси и забракована по SHA — задокументирована) |
| D6 | Пересборка §3 в WSL (Ubuntu 24.04.2, gcc 13.3.0, 20 ядер): `CMAKE_EXIT=0`, **`BUILD_EXIT=0`** | **OK** |
| D6a | Бинари: oxDNA 3375976 B, DNAnalysis 2957400 B, confGenerator 2201664 B; флаги Release/`-O3 -DNDEBUG`/DOUBLE=ON/CUDA=OFF/MPI=OFF/NATIVE=ON/JSON=ON/`-D_FORCE_INLINES`, `GIT_COMMIT="00dc7fb"` | **1:1** с §4 и campaign-пином; SHA бинаря `a4810960…` ≠ `ffc80b1a…` — ожидаемо (встроенный `BUILD_TIME`), критерий protocol.json соблюдён |
| D7 | Собственный smoke `EX-VERIFY-NL1-002-R2-SMOKE-001` (новый ID, steps=1e4): RUN_EXIT=0, 11 строк, NaN/Inf=0, 1 конфигурация, RELEASE v3.7, GIT COMMIT 00dc7fb, N=16/2, seed −588845438; avg_col2 **−1.36689954545** → IN_BAND | **OK** |
| D7a | Сравнение с NL1-001 опубликованным smoke (тот же `analyze_energy.sh`): avg_col2 **−1.36018000000** → IN_BAND; расхождение 0.0067 ≪ 0.15 | **полоса совместима** (compatibility-факт, не scientific claim) |
| D1 | SHA-256/size всех артефактов по сырым git-blob байтам vs `artifacts.manifest.json` (4 прогона × 4 файла) | **16/16 MATCH**; кросс-check `events/0002.artifacts_sha256` = манифестам 16/16; дайджесты 44+10 файлов обоих деревьев посчитаны |
| D2 | Воспроизведение опубликованного `analyze_energy.sh` на опубликованных `energy.dat` S001/P001–P003 | **11/11 знаков** по всем прогонам: −1.39393635864 / −1.37730121179 / −1.39389370430 / −1.38687945155; rows=1001, 10 конфигураций, NaN/Inf=0, «END OF THE SIMULATION…» 4/4 |
| D3 | Независимый пересчёт статистики (python3, не awk): mean **−1.38602478921**, SD **0.00832919790**, размах **0.01659249251**, SD/полоса **0.0555**; delta_from_oracle 4/4 до 11 знаков | **бит-в-бит** с evidence-map и `E1-PROTO-R2` §1 |
| D2a | Оракул verbatim из upstream pinned tree (`quick_compare`): `ColumnAverage::energy.dat::2::-1.37970256144::0.15`, SHA-256 `86a8b6ac…` = пин protocol.json | **MATCH** — полоса/значение не подбирались |
| D2b | Лог-факты 4 прогонов: RELEASE v3.7, GIT COMMIT 00dc7fb, seed из лога = опубликованному (−200619630/−473348953/−547126645/−1610133928), T 0.097717, N:16/molecules:2 | **4/4 MATCH** |
| D8 | Опубликованные `run-resources/*/time.log` vs заявленные ресурсы: 13.13/6304, 11.08/6328, 11.74/6700, 12.56/6520; суммарно ~48.5 c ≪ 1 core-hour | **MATCH** |
| D5 | Нет ACCEPTED/self-acceptance: `state.json`/`plan.json`/`config/`/`docs/control/`/`scripts/` — diff vs base ПУСТ; `NL1-002=READY`; паспорт EX `IN_PROGRESS`; E1 = `RUN`/NOT_EVALUATED; вердикт-файлов в пакете нет; handoff маршрутизирует REVIEWER→VERIFIER→Director, merge = Human Gate | **OK** |
| D5a | Дисциплина claims: campaign scientific_outcome NOT_EVALUATED во всех событий/картах; T1-факт публикуется как execution fact; pilot не засчитан в evidence | **OK** |
| D5b | Frozen-before-run: freeze `5c8774f` → repair `9cc83e8` (S001 started-event, пропуск задокументирован в самом event) → прогоны `ec67752` | **OK** |

## 3. Находки (требуют исправления)

**F-1 (MAJOR, контрактная): `CONTROL_EXPERIMENT validate` не работает на пакете.**
Штатный машинный контракт `scripts/harness/experiment_cli.py` (бит-в-бит идентичен base — действовал во время исполнения) на всех 4 run-каталогах падает (`AttributeError: 'str' object has no attribute 'get'`, exit 1): `artifacts.manifest.json` использует форму `{"artifacts": {имя: …}}` вместо контрактного массива `[ {sha256, size_bytes, producer_run_id, subject_sha, storage_location} ]`. Кроме того, по тому же контракту в `manifest.json` отсутствуют `subject_sha` (40-hex), `claim_ceiling`, `model`, `observables`, `stop_conditions`, а в каждом experiment-event — `experiment_id` и `subject_sha`. Содержательно provenance присутствует и верифицирован (D1), прозаический контракт `EXPERIMENT_HARNESS_RU` соблюдён — но контрольная поверхность репозитория (`HARNESS_CONTROL.md`: «Machine contracts…», `CONTROL_EXPERIMENT validate`) на пакете не выполняется механически. Для HIGH-risk scientific WO это должно быть либо устранено, либо закрыто явной control-ревизией контракта.

**F-2 (MINOR, контрактная): сокращённый `subject_sha` в work-событиях.**
`CONTROL_WORK validate docs/work/executions/EX-NL1-002-R1` → **ok=false, exit 3**: в событиях `0002`–`0005` указан `subject_sha: "9cc83e8"` (7 знаков) вместо 40 lowercase hex. Значение осмысленно (freeze-commit), но контракт нарушен.

**F-3 (MINOR, контрактная): событие после терминального handoff.**
Тот же `CONTROL_WORK validate`: ошибка `terminal/handoff event must be last` — после `0004-handoff-completed` опубликован `0005-resource-evidence-committed` (CONTINUATION_CHECKPOINT). Семантически это задокументированный post-handoff checkpoint (допустимый паттерн «corrections — новым event»), но текущий контракт это отклоняет.

**Требуемое исправление (основа Repair Map):**
1. Привести пакет к машинным контрактам БЕЗ переписывания истории: новые события/записи с полными 40-hex `subject_sha`, корректная форма `artifacts.manifest.json` для последующих кампаний; для уже опубликованных событий — erratum/annotation новым event (старые не редактировать).
2. Либо (альтернативативный путь для F-1) — явная control-ревизия контракта (`experiment_cli.py`/doc) на main, легализующая фактическую форму, с recorded decision; work-ветка не имеет полномочий менять foundation.
3. Повторный прогон обоих валидаторов с exit 0 до Director checkpoint.

## 4. Что НЕ скомпрометировано находками

Все исполнительные и числовые факты пакета подтверждены независимым воспроизведением: exact subject, пересборка engine (exit 0, размеры/флаги/commit-строка), 16/16 артефакт-дайджестов, анализ до последнего знака на 4 прогонах, статистика бит-в-бит, оракул из pinned upstream, целостность §5.2 (1001 строка, 10 конфигураций, NaN/Inf=0), seed-политика и лог-факты, ресурсы, дисциплина NOT_EVALUATED, отсутствие self-acceptance. Собственный smoke-прогон верификатора на собственной пересборке — IN_BAND, полоса совместима с NL1-001. Научных подгонок, post-hoc исключений, скрытых retries и превышения claim'ов не обнаружено.

## 5. Итог

**`FIX_REQUIRED`** — научная/исполнительная суть NL1-002 верифицирована и воспроизводится полностью; пакет не может быть принят в текущей форме из-за формальных отклонений от машинных контрактов контроля (F-1–F-3), ломающих штатную валидацию репозитория. После Repair Map (новые evidence, без переписывания истории) и повторного `CONTROL_WORK`/`CONTROL_EXPERIMENT validate` = exit 0 — subject готов к Director checkpoint без повторной научной верификации по существу (повторная проверка — только исправленных поверхностей).

- Verifier evidence: `docs/evidence/NL1-002/VERIFIER_PROGRESS_R2.md`, `docs/evidence/NL1-002/verify-r2/**` (включая артефакты smoke `EX-VERIFY-NL1-002-R2-SMOKE-001`).
- Scratch верификатора (вне Git, disposable): `C:\NanoLab\scratch\nl1-002-verify-r2\` (probe-repo, пересборка, скрипты проверок, отчёты JSON).
- Next action: implementer — Repair Map по F-1…F-3 в новой repair-ветке от exact subject; повторная верификация исправленных поверхностей; merge — Human Gate.
