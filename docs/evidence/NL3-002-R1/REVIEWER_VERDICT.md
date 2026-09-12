# REVIEWER VERDICT — EX-NL3-002-R1

- **Execution**: EX-NL3-002-R1 (confirmatory-кампания E2-R1, Work Order NL3-002)
- **Exact HEAD**: `c9ff9a187eaa2f944e6f0405ac234dcb1efd7287` (branch `work/nl3-002-confirm-r1`)
- **Дата review**: 2026-09-12
- **Reviewer**: FRESH-сессия, ветка `review/nl3-002-confirm-r1` (worktree `C:\NanoLab\review-nl3-002-confirm`)
- **Independence caveat**: REVIEWER выполнялся в fresh-сессии на отдельной ветке от exact HEAD; независимый пересчёт статистики выполнен собственным скриптом Reviewer'а из raw-артефактов (WSL) на подвыборке кадров. При этом сам analysis-код (`scripts/e2/observables.py`) не переписывался, а переиспользовался как frozen-субъект — это осознанное ограничение: он верифицирован тестами (242 OK) и покомпонентно сверён на общих кадрах, но полная независимая реимплементация детектора v2 не выполнялась. Wall-времена ранов не воспроизводимы (крэш обёртки, см. finding F-3), приняты по ФС-реконструкции с кросс-чеком.

## Таблица проверок 1–10

| # | Проверка | Команда | Результат | Статус |
|---|---|---|---|---|
| 1 | Freeze-до-данных | `git log --follow -- docs/research/E2_PROTO_R1.md`; `Select-String c00*_input.in / c00*_deviations.json` | Протокол появился в `280104c` (единственный коммит по файлу), кампания (66428e3→c9ff9a1) после. seeds 201004/202008/203012, steps=200000, print_conf_interval=4000, print_energy_every=100 — идентично в `c00X_input.in` и `c00X_deviations.json`. 2e7 не запускался (steps_requested=200000 ×3; energy rows 2001 = 200000/100+1) | PASS |
| 2 | Scope | `git diff --stat 280104c..c9ff9a1`; `git diff --name-only -- project/ scripts/ tests/` | Только `docs/work/executions/EX-NL3-002-R1/**` + `docs/work/SESSION_LOG.md` (32 файла, +3719). `project/**` не менялись; `E2_PROTO_R1.md`/`E2_OBSERVABLES_*.md` — пустой diff (0 строк) | PASS |
| 3 | Тесты | `PYTHONPATH=scripts; python -m unittest discover -s tests -t .` | Ran 242 tests: **OK (skipped=1)** | PASS |
| 4 | Digest-гейт | чтение `evidence/source-download-verification.json`; WSL `sha256sum`; `Test-Path %TEMP%\nl3-002-confirm-src` | 3/3 PASS: `0b.top` cd046127…, `0b.conf` 506c41fc…, `pro_CPU.in` bd6cd418… (size+blob_sha1+sha256). Входы скопированы в run-dir и byte-verified (манифесты; sha256 top/conf в WSL совпадает лично проверен). U4: temp-каталог удалён (не существует) | PASS |
| 5 | Независимый пересчёт | собственный скрипт Reviewer'а: `scripts/e2/observables.py` (v2 mutual + frozen arm-manifest-0b + гейты) на raw `c001_traj.dat`/`0b.top`, каждый 5-й кадр из 50 | 10/10 общих кадров: max |Δangle| = **4.5e-10 °** (порог 0.01°), pf2/lbf/disp совпадают до ~5e-10, validity совпадает; reference_pairs_v2 = 3292 = манифесту. sha256 `c001_traj.dat` = `1ad63c38…` = манифесту рана | PASS |
| 6 | Арифметика пула | программная сверка `confirmatory-summary.json` ↔ `c00X-analysis.json` | 150 кадров = 3×50, 0 invalid; pool median **65.9769** ∈ [65.9, 66.1]; CI95 **[65.675, 66.318]** ∈ [65.6, 66.4]; независимо пересчитанная медиана из per-replica frames = 65.976921401 — совпадает | PASS |
| 7 | Гейты | чтение `c00X-analysis.json` | lbf max 0.05559/0.05595/0.05547 < 0.1078; pf_v2 min 0.9818/0.9846/0.9809 ≥ 0.50; disp max 7.43/7.91/8.40 ≤ 20.0 — всё в артефактах, подтверждено пересчётом (C001) | PASS |
| 8 | Стерильность | `git grep` интерпретационных паттернов; `git ls-tree -r c9ff9a1`; `git diff -- project/state.json` | scientific_outcome = MEASURED; заявлений о «работающем шарнире»/соответствии статье не найдено; угол подан в конвенции [0,180] (erratum R1 §2.5); байтов источника (0b.top/0b.conf/pro_CPU.in/traj/MD_Hinges) в Git нет; state.json не менялся | PASS |
| 9 | Отклонение обёртки | event 0002, `run-reports.json.wall_measurement`, WSL `cat exit_code.txt` | Крэш обёртки (`del` на set) задокументирован прозрачно: движки — осиротевшие, но завершились штатно; `EXIT:0` ×3 проверен Reviewer'ом лично по `exit_code.txt`. Wall восстановлен по ФС (birth energy-файла → mtime exit_code.txt) с кросс-чеком C002: in-process 10710.2 s vs 10885 s реконструировано, дельта объяснена (WSL startup + загрузка конфига). Бюджет: 11146/10885/11134 s ≤ 12600 s | PASS |
| 10 | Валидаторы | `python scripts/harness/work_cli.py validate/close …EX-NL3-002-R1`; `python -m harness.cli check-consistency` | validate ok (HANDOFF_READY, terminal handoff, no post-terminal corrections); close ok; check-consistency ok (frontier NL3, next NL3-002, head c9ff9a1) | PASS |

## Findings

- **F-1 (INFO, positive)** — Урок F-1 пилота закрыт: все digest-gated входы физически скопированы в каталог каждого рана и byte-verified (манифесты `c00X-artifacts.manifest.json`); sha256 входов и trajectory в WSL совпадают с манифестами при независимой проверке.
- **F-2 (INFO)** — `confirm_analysis.py` содержит hardcoded-путь `REPO = C:\NanoLab\nl3-002-confirm` (worktree исполнителя). На воспроизводимость в рамках данного review не влияет (Reviewер использовал собственный скрипт), но для future-proofing заслуживает параметризации.
- **F-3 (INFO)** — Wall-времена ранов — ФС-реконструкция, а не прямой процессный учёт (следствие крэша обёртки). Запись честная: метод реконструкции и кросс-чек (Δ ≈ 175 s на C002, ≈1.6%) раскрыты; вывод «в бюджете» устойчив к этой погрешности.
- **F-4 (COSMETIC)** — В `summary.md` колонка q5–q95 для per-replica строк заполнена «—», хотя данные есть в `c00X-analysis.json`. Информации не искажает.

Отклонений от frozen-протокола не обнаружено. Протокольные отклонения от `pro_CPU.in` (steps/seed/имена outputs/print_conf_interval/print_energy_every/lastconf_file + предмет 74b→0b) полностью перечислены в `c00X_deviations.json` и соответствуют разрешённым протоколом.

## Вердикт

**PASS** — все 10 обязательных проверок выполнены; независимый пересчёт из raw-артефактов воспроизводит заявленную статистику с точностью ~5e-10° (порог 0.01°).

## Claim ceiling

**C0_SOFTWARE_ONLY / measured-only**: подтверждено только то, что в рамках frozen E2_PROTO_R1 (3 реплики × 2e5 steps, detector v2 mutual, frozen arm-manifest-0b) измерено распределение угла с пул-медианой 65.98° [CI95 bootstrap: 65.67–66.32] на 150/150 валидных кадрах при ненарушенных гейтах целостности. Никакого утверждения о «функциональном шарнире», соответствии статье или научной приемлемости результата данный review не делает; acceptance NL3-002 и повышение claim — прерогатива Director/Human Gate.
