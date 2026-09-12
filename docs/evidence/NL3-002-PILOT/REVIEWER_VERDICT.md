# REVIEWER verdict — EX-NL3-002-PILOT-R1

- **Execution**: EX-NL3-002-PILOT-R1 (WO NL3-002-PILOT, child of NL3-002)
- **Reviewed at**: exact HEAD `4d72ce06e142083a1a7adb255628a821f28b9a66` of `work/nl3-002-pilot-r1` (verified `git rev-parse HEAD` == `4d72ce0` in dedicated worktree `review/nl3-002-pilot-r1`)
- **Base**: `760901c` (origin/main, Director checkpoint) — confirmed by `git log 760901c..4d72ce0`: `eba4758` START → `82770d2` feat → `4d72ce0` records
- **Date**: 2026-09-12
- **Independence caveat**: review выполнен в FRESH-сессии (новый агентный контекст, отдельный worktree, никакие артефакты исполнителя не переиспользовались), однако на том же физическом хосте и тем же оператором, что и исполнение; WSL-артефакты ранов проверены по месту.

## Таблица проверок

| # | Проверка | Команда | Результат |
|---|----------|---------|-----------|
| 1 | Пререгистрация-дисциплина | `git show 760901c:docs/work/WO-NL3-002-PILOT.md` | **PASS** — WO существует в base (до START eba4758); seeds 101001/102002/103003 и steps 24000 в s00*_run_report/deviations соответствуют WO; все отклонения от pro_CPU.in зафиксированы в s00*_deviations.json (10 позиций: seed, steps, topology/conf 74b→0b, имена outputs, print-интервалы, добавлен lastconf_file) |
| 2 | Scope | `git diff --stat 760901c..4d72ce0` | **PASS** — 33 файла, 2131 insertions / 0 deletions; только SESSION_LOG, executions/EX-NL3-002-PILOT-R1/**, scripts/e2/observables.py (new func), tests/test_e2_pilot.py; `project/**` не менялись; `docs/experiments/**` не трогались |
| 3 | Тесты | `PYTHONPATH=scripts; python -m unittest discover -s tests -t .` | **PASS** — Ran 231 tests, OK (skipped=1); отдельно `tests.test_e2_pilot` — 4/4 OK (equivalence naive vs bucketed, включая wrapped/minimum-image fixture) |
| 4 | Аддитивность observables | `git diff 760901c..4d72ce0 -- scripts/e2/observables.py` | **PASS** — diff содержит только новую функцию `reference_pairs_bucketed` (+79 строк, 0 удалений/изменений); константы PAIR_D_MIN/PAIR_D_MAX/BOND_D_MAX/EIG_INVALID/ISOTROPYICS не тронуты; `docs/research/E2_OBSERVABLES_R1.md` — пустой diff (frozen v1 untouched) |
| 5 | Digest-гейт и артефакты | evidence/source-download-verification.json; `wsl sha256sum` | **PASS** — 3/3 digest_gate PASS (size+blob_sha1+sha256), значения точно совпадают с scripts/hinge_family/source_pins.json (0b.top cd046127…, 0b.conf 506c41fc…/2294162 B, pro_CPU.in bd6cd418…). Повторный hash рана: `0b.top` → cd046127…, `s001_traj.dat` → b8ca210a… — оба совпали с s001-artifacts.manifest.json |
| 6 | Байты источника в Git | `git ls-tree -r --name-only HEAD \| grep -E '0b.\|pro_CPU'` | **PASS** — пусто; в evidence только дайджесты/числа/пути |
| 7 | Научная стерильность | summary/events/analysis JSON | **PASS** — везде `scientific_outcome = NOT_EVALUATED`; `class: non-confirmatory`; steps 24000 во всех манифестах (2e7 не запускались); DRAFT-угол помечен `DRAFT proxy, non-confirmatory, not the E2-PROTO manifest` в каждом analysis-файле; lbf≈0.054 (frame 0) и pairs 26–29 поданы как «Открытые наблюдения — вход в E2-PROTO-R1, не выводы» |
| 8 | Бюджет | cost-summary.json | **PASS** — wall реплик 1441.16 / 1447.95 / 1449.27 s ≤ 1500 s target; общий calendar ~50 мин ≤ 3 ч; per-step: rate ≤0.0519 (single, upper bound) vs 0.0600–0.0604 (3 параллельных) — расхождение объяснено и зафиксировано как contention factor ~1.16× |
| 9 | Валидаторы | `python -m harness.work_cli validate …`; `python -m harness.cli check-consistency` | **PASS** — validate: `ok: true`, terminal HANDOFF_COMPLETED, has_summary; check-consistency: `ok: true`, errors/warnings пусты |
| 10 | U4 | events/manifests | **PASS** — события 0001/0002/0005 фиксируют download во временный каталог вне Git, durable_cache: false, удаление временных исходников после execution; артефакты ранов в WSL вне Git с location+SHA-256+size в манифестах — соответствует G1=B |

## Findings

| ID | Severity | Finding |
|----|----------|---------|
| F-1 | **LOW** (прозрачность vs процедурный finding) | Манифесты ранов содержат honest error entry для `pro_CPU.in` (`sha256sum: pro_CPU.in: No such file or directory`) — референсный input не копировался в run-dir, поэтому его digest в манифесте рана подтверждается только через source-download-verification.json (по которому pro_CPU.in прошёл гейт до сборки input.in). Оценка: прозрачная запись ошибки лучше молчания; процедурная шероховатость — в E2-PROTO стоит копировать все digest-gated входы в run-dir и хэшировать единым проходом. |
| F-2 | **LOW** | В s00*_deviations.json отклонения `topology 74b.top→0b.top` / `conf_file 74b.conf→0b.conf` имеют reason «bounded pilot / per-run naming», хотя это смена subject по WO, а не naming. Семантика верно раскрыта в event 0002; неточна только reason-строка в deviations JSON. |
| F-3 | **INFO** | Rate-run использовал seed 101001 (тот же, что S001). WO не требует отдельного seed для калибровочной пробы; влияние на результат (измерение стоимости) ничтожно. |

Ни один finding не блокирует: все три не влияют на целостность данных, пререгистрацию или права.

## Claim ceiling

Вердикт ограничивает допустимые интерпретации: пилот — **C0_SOFTWARE_ONLY / non-confirmatory calibration**. Допустимо опираться на: (a) измеренную стоимость (~0.052 s/step single upper bound, ~0.060 s/step при 3 параллельных; 2e7×3 ≈ 1e6 s engine wall — budgeting only); (b) инженерную совместимость engine 00dc7fb9 с 2017-input; (c) процедурную воспроизводимость (digest-гейт, manifests, tests). НЕ допустимо: любые выводы о шарнире (угол, integrity, pairs) как научные результаты — lbf≈0.054 в frame 0, reference pairs 26–29 и DRAFT-углы ~178.6° суть кандидаты-наблюдения для E2-PROTO-R1 freeze, не результаты.

## VERDICT: **PASS**

Процедурная дисциплина выдержана: пререгистрация до запуска, bounded объёмы, digest-гейт, additive-only observables с equivalence-тестами, никаких научных claim'ов, байты источника вне Git, бюджет соблюдён, валидаторы зелёные. Рекомендация: Director ACCEPT → merge (Human Gate), findings F-1/F-2 учесть при drafting E2-PROTO-R1.

— REVIEWER, fresh-сессия, 2026-09-12
