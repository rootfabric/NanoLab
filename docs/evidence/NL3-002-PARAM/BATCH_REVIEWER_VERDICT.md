# Batch REVIEWER Verdict — серия NL3-002-PARAM

- **Ревьюер**: независимый fresh-Reviewer (fresh-сессия, без контекста исполнения)
- **Дата**: 2026-09-13 (UTC)
- **Exact HEAD**: `24a21aad0ae8c752fd3236324005f70a4b56760c` (ветка `work/nl3-002-summary-r1`), verified `git rev-parse HEAD`
- **Review worktree**: `C:\NanoLab\review-nl3-002-param-batch` (branch `review/nl3-002-param-batch-r1`)
- **Серия**: EX-NL3-002-PARAM-11B-R1, EX-NL3-002-PARAM-32B-R1, EX-NL3-002-PARAM-53B-R1, EX-NL3-002-PARAM-74B-R1, EX-NL3-002-SUMMARY-R1
- **Протоколы**: `docs/research/E2_PROTO_R1.md` (FROZEN + addendum §8), `E2_OBSERVABLES_R2.md`, `docs/work/WO-NL3-002-PARAM.md`
- **Independence caveat**: fresh-сессия ревью, но тот же физический хост и тот же исполнитель-человек, что и исполнение серии; raw-артефакты (траектории WSL) не перечитывались — ревью опирается на Git-committed evidence, published JSON-ы и воспроизводимые пересчёты из них.

## Вердикт: **PASS**

Claim ceiling: `C0_SOFTWARE_ONLY` / measured-only. Cross-variant тренд-интерпретации (в т.ч. по последовательности 65.87 → 73.93 → 78.09 → 132.36) — **вне** claim ceiling и вне scope исполнения; в артефактах серии они отсутствуют (проверка 9).

## Таблица проверок 1–11

| # | Проверка | Команда/метод | Результат |
|---|---|---|---|
| 1 | Scope/пререгистрация | `git merge-base --is-ancestor 5940c8a <merge>` → 0 (все 4); `bdbebfd` ancestor 32b/53b/74b merges → 0; `git log --follow` WO/PROTO; per-seed JSON + input.in | **PASS**. WO (5940c8a) и addendum §8 (bdbebfd) предшествуют соответствующим веткам. Seeds 201004/202008/203012 и steps подтверждены: 11b steps_requested=200000, SIGTERM на 12600 s (wall 12401–12472 s, 46/50 кадров, t_last=184000); 32b/53b steps=150000, exit 0 3/3. Диффы веток — только own execution dirs + SESSION_LOG (out-of-scope файлов нет). |
| 2 | Тесты | `PYTHONPATH=scripts; python -m unittest discover -s tests -t .` | **PASS** — `Ran 242 tests ... OK (skipped=1)`. |
| 3 | Manifest-деривации до данных | чтение `arm-manifest-{11b,32b,53b}-report.json`, 74b failure JSON; порядок коммитов (manifest в чекпоинте 0002 до END_EXECUTION 0003) | **PASS**. Все 3 отчёта: `determinism.byte_identical=true`, sha256 run1==run2 (4078f285…/2e542a61…/8e58eb89…); 74b: `deterministic_identical_error=true`, 2 attempts, runs NOT_RUN — run-каталогов/манифестов траекторий 74b в evidence нет. |
| 4 | Digest-гейты | чтение `source-download-verification.json` ×4 | **PASS**. digest_gate_all=PASS везде; top+conf+pro_CPU.in size_match+blob_sha1_match=true 3/3; sha256-пины 11b–74b `COMPUTED_NOT_VERIFIED` + `sha256_computed_at_first_download` записаны (соответствует owner-decision G1=B, не нарушение); pro_CPU.in полный пин PASS. |
| 5 | Байт-детерминизм | повторный двойной прогон `param_summary_build.py`; `git hash-object` + `git cat-file blob` byte-compare | **PASS**. run1==run2 (SHA-256 58260815A684A290…); регенерированный файл байт-идентичен HEAD-blob (29408 B, 0 bytediffs). Примечание: свежий checkout файла smudged в CRLF — исходное хэш-расхождение артефакт checkout, не контента. |
| 6 | Common-window пересчёт (ключевая) | независимый Python-скрипт ревьюера: фильтр published frames `time<=150000`, valid, median/IQR (linear quantile) | **PASS**. 0b: n=111, median=65.8705 (≈65.87 ✓), IQR [64.978, 66.578]; 11b: n=111, median=73.9287 (≈73.93 ✓), IQR [73.055, 74.555] — совпадение с `parametric-summary.json` до 1e-6 (< 0.05°). 32b/53b: recomputed == published == window (78.091846 / 132.357788, точно). |
| 7 | Карточка компонента 0b | сверка `component-card-0b.json/md` против `confirmatory-summary.json`, per-frame JSON, `arm-manifest-0b.json` | **PASS**. pooled median 65.976921 (65.98 ✓), CI95 [65.675, 66.318] ([65.67, 66.32] ✓), pf_v2 min 0.980874 (≥0.9809 ✓), arm 4006/3942 ✓, pinned 23fd1ff ✓, digest-гейты 3/3 ✓, 112 стрендов/8378 нт ✓; ограничения (конвенция [0,180], U-obs-1 first-principles, coarse-grained, lbf baseline, 300 K decision) — честные; reproduction command полон (5 шагов). |
| 8 | 74b честность | events 0002-blocker/0003-work-order-blocked, passport BLOCKED, validate ok | **PASS**. scientific_outcome=NOT_MEASURED; никакой статистики 74b нет (angle_stats: null); в series-summary 74b — honest gap с полным failure-report (size tables по всем порогам, second/third < 3.0). |
| 9 | Стерильность серии | grep trend/тренд/monoton/корреляц по series artifacts; `git log -- state.json`; `git ls-files` на source-байты | **PASS**. Все упоминания трендов — только как «вне scope/Director»; MEASURED/NOT_MEASURED корректны; `project/state.json` не менялся с 174bdaa (до серии); .top/.conf/траекторий серии в Git нет. |
| 10 | Валидаторы | `work_cli.py validate/close` ×5; `python -m harness.cli check-consistency` | **PASS**. 11b/32b/53b/74B/SUMMARY validate+close ok=true, exit 0 (74b status=BLOCKED корректно); check-consistency exit 0 (stages 9, tasks 18, experiments 7, head 24a21aa). |
| 11 | Процедурные отклонения | чтение summaries/run-reports | **PASS**. 11b budget-interrupt §5 документирован (SIGTERM @12600 s, 46/50, wall восстановлен по ФС + кросс-чек log time 12562–12570 s); инциденты обёрток (timeout harness-джоба; pkill → exit_code.txt не записан, exit_code=null с причиной) раскрыты; 74b honest gap документирован; findings ниже. |

## Per-execution статусы

| Execution | Статус REVIEWER | Примечание |
|---|---|---|
| EX-NL3-002-PARAM-11B-R1 | **PASS** (с отклонением, задокументированным) | MEASURED на 46/50 кадров; бюджетное прерывание §5; окно 150k покрыто (t_last=184000). |
| EX-NL3-002-PARAM-32B-R1 | **PASS** | 3/3 exit 0, 150000 steps, wall 2.25 h ≤ 3.5 ч; recomputed==published. |
| EX-NL3-002-PARAM-53B-R1 | **PASS** | 3/3 exit 0, 150000 steps; recomputed==published. |
| EX-NL3-002-PARAM-74B-R1 | **PASS** (как честный BLOCKED) | NOT_MEASURED, runs NOT_RUN, детерминированный отказ деривации. |
| EX-NL3-002-SUMMARY-R1 | **PASS** | 0 прогонов; байт-детерминизм билдера воспроизведён; карточка 0b сверена. |

## Findings

1. **[INFO] 11b: exit_code=null во всех 3 репликах** — следствие инцидента обёртки (pkill родительского bash); причина и wall-time реконструкция задокументированы в `run-reports.json` (`exit_condition`, `log_time_passed_s_crosscheck`). Данные движка не затронуты. Принимается.
2. **[INFO] 11b: 46/50 кадров (93%)** — калибровочный факт по §5, использован для планирования 32b/53b (steps 150000, уложились в бюджет). Окно сравнения покрыто.
3. **[INFO] 37 кадров vs traj_frames_expected_full_run=38 у 32b/53b** — не truncation: 150000 не делится на print_conf_interval 4000 (последний кадр 148000), объяснено в summary. Не отклонение.
4. **[INFO] sha256-пины вариантов NOT_VERIFIED** — соответствует owner-decision (G1=B); sha256 вычислены при первой загрузке и записаны для future re-use. Не нарушение.
5. **[LOW] 74b: семантика отказа** — отказ манифест-деривации означает лишь, что frozen arm-manifest-v1 не выделяет два блока в геометрии frame 0 74b; это инструментальный факт в рамках замороженной деривации (не физический вывод о 74b). В артефактах подано корректно (варианты revision — только новая пререгистрация, Director).

Блокирующих findings нет.

## Claim ceiling

`C0_SOFTWARE_ONLY` / measured-only: серия даёт измеренные распределения угла (median/IQR/CI95 bootstrap) и манифесты рук per variant в общем окне t ≤ 150000. Тренд-интерпретации и любые выводы о параметр→угол зависимости — вне ceiling, вне исполнения и вне этого ревью; их делает Director на отдельных условиях.
