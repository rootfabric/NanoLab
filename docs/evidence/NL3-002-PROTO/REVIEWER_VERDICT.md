# REVIEWER VERDICT — EX-NL3-002-PROTO-R1

- **Execution**: EX-NL3-002-PROTO-R1 (WO-NL3-002-PROTO, подготовка freeze E2-PROTO-R1)
- **Exact HEAD**: `9b3e1c5d2f21f9e677848905eb96fcb01cb6b3d0` (ветка `work/nl3-002-proto-r1`; стэковая база 4d72ce0 = пилотный tip) — подтверждён `rev-parse` в fresh worktree
- **Дата review**: 2026-09-12 (fresh-сессия REVIEWER)
- **Independence caveat**: fresh-сессия, независимый контекст; тот же физический хост и тот же исполнитель-оператор (человек/инфраструктура) — независимость контекстная, не инфраструктурная.
- **Вердикт**: **PASS**

## Таблица проверок 1–11

| # | Проверка | Команда | Результат |
|---|---|---|---|
| 1 | Преререгистрация WO | `git log --diff-filter=A -- docs/work/WO-NL3-002-PROTO.md` | **PASS** — добавлен в `a80c1f0` (первый коммит ветки), до substantive `d38e248` |
| 2 | Scope | `git diff --stat 4d72ce0..9b3e1c5` | **PASS** — только allowed paths (WO, executions/EX-NL3-002-PROTO-R1/**, SESSION_LOG, E2_OBSERVABLES_R2.md new, scripts/e2/**, tests/**); diff `project/` пуст; diff `E2_OBSERVABLES_R1.md` **пуст** (frozen v1 не тронут) |
| 3 | Тесты | `PYTHONPATH=scripts; python -m unittest discover -s tests -t .` | **PASS** — 242 теста, OK (1 skip); `tests/test_e2_proto.py` — ровно 11 новых (unittest -v: Ran 11 tests, OK) |
| 4 | v1 нетронут | `git diff 4d72ce0..9b3e1c5 -- scripts/e2/observables.py` | **PASS** — единственная удалённая строка: CLI-диспетчеризация (`report = analyse(...)` → ветвление v1/v2; путь v1 `analyse()` сохранён). Функции `reference_pairs`/`reference_pairs_bucketed`/`pairs_fraction`/`hinge_angle` и константы `PAIR_D_MIN/MAX=0.05/0.55`, `BOND_D_MAX`, `EIG_INVALID`, `ISOTROPY_EPS`, `ORIENTATION_EPS` без изменений; v2 — только добавления (`reference_pairs_v2`, `pairs_fraction_v2`, `analyse_v2`, `PAIR_D_*_V2`); `analyse_v2` → `schema_version: 2`, v1 → `schema_version: 1` |
| 5 | R2-документ | чтение `docs/research/E2_OBSERVABLES_R2.md` | **PASS** — мотивация (v1: 26–29 пар при ~4000 ожидаемых), определение v2 (окно (0.05, 1.3], антипараллельность a1·a1 ≤ −0.3, mutual-nearest + greedy-вариант), константы, статус PRE-CONFIRMATORY / DIRECTOR FREEZE PENDING, таблица отличий от R1 |
| 6 | Манифест-воспроизводимость | независимая перезапись: download-on-run (digest-гейт PASS) + `derive_manifest` + `canonical_json`, сравнение с git-блобом | **PASS** — свежая деривация **байт-идентична** blob `9b3e1c5:...evidence/arm-manifest-0b.json`; wall-clock в манифесте отсутствует; временные файлы удалены (проверено). Примечание: см. finding F2 (CRLF) и F1 (2/2 vs «3/3») |
| 7 | Манифест-санити | разбор `arm-manifest-0b.json` | **PASS** — arm_a ∩ arm_b = ∅ (overlap 0); \|arm_a\|=4006, \|arm_b\|=3942; покрытие 94.87% топологии (0.948675101) / 99.97% парных (0.999748428); hinge_angle frame 0 = **66.89°** записан как факт (`validation.hinge_angle_frame0.status=OK`) с честной пометкой в summary §п.5 и open question 5: беззнаковая конвенция v1 не различает θ и 180°−θ; «ожидание малого угла не подтвердилось» зафиксировано явно (summary п.1) |
| 8 | v2 frame-0 числа | `evidence/v2-frame0.json` + R2 + proposals | **PASS** — mutual 3300 / greedy 3975; согласованы в R2 (§1, §3), summary (п.2) и proto-proposals (`pairs_v2_frame0`) |
| 9 | Sterility/U4/G1 | ls-tree всех 4 коммитов ветки, скан evidence/events, temp-каталоги | **PASS** — прогонов физики нет (в events/passport только derivation + тесты); 2e7 не запускался (упоминается только как длина авторского прогона и DRAFT-опция); proposals помечены DRAFT (статусы в каждом блоке); digest-гейт по фактически использованным входам PASS; байтов источника в Git нет (0 hits по `\.(top|conf)$`, `pro_(CPU|GPU)\.in`, `Design_Hinges` во всех коммитах ветки); временные каталоги источника отсутствуют |
| 10 | Валидаторы | `python -m harness.work_cli validate docs/work/executions/EX-NL3-002-PROTO-R1`; `python -m harness.cli check-consistency` | **PASS** — оба `ok: true`, exit 0; validate: HANDOFF_READY, 5 корректных событий; check-consistency: frontier NL3, head 9b3e1c5 |
| 11 | Proposals-санити | чтение `proto-proposals.json` | **PASS** — длины {2e5, 1e6, 2e7} × R_confirm=3; wall-прогнозы точно согласованы с 0.052 s/step single / 0.060 parallel: 10 400 с = 2.89 ч / 52 000 с = 14.4 ч / 1 040 000 с = 288.9 ч на реплику (0.14 / 0.69 / 13.9 календарных дней для 3 реплик parallel); seeds 201004/202008/203012 (отдельны от авторского 7777 и пилотных 101001/102002/103003); статистика: квантили q05–q95 + bootstrap-CI медианы (детерминированный seed), no optional stopping, все реплики публикуются; весь файл DRAFT («final freeze is the Director's decision») |

## Findings

| ID | Severity | Finding |
|---|---|---|
| F1 | INFO | Digest-гейт данного execution покрыл 2/2 фактически использованных входов (0b.top cd046127…/120204, 0b.conf 506c41fc…/2294162). `MD_Hinges/pro_CPU.in` (bd6cd418…/933) остаётся pinned в `scripts/hinge_family/source_pins.json` (значения совпадают с пинами), но в этом execution не скачивался и не верифицировался — корректно, т.к. физика не запускалась и pro_CPU.in не потреблялся. Ожидание «3/3» из review-brief описывает pin-реестр, а не evidence этого прогона; docs-заявлений «3/3» в репо нет — несоответствия нет. |
| F2 | INFO | Рабочая копия `arm-manifest-0b.json` в worktree показывает CRLF — артефакт checkout при `core.autocrlf=true`; закоммиченный blob — LF и байт-идентичен свежей деривации. Контентных расхождений нет. |
| F3 | INFO | `v2-frame0.json` / `proto-proposals.json` используют `schema_version: 1` со собственными kind (`e2_proto_v2_frame0`, `e2_proto_proposals`) и v2-префиксами полей. Требование «v2-выходы помечены schema 2» выполнено там, где оно определено: trace-выход `analyse_v2` → `schema_version: 2`; для evidence-отчётов калибровки отдельная схема допустима. |
| F4 | LOW | `evidence/run_arm_manifest.py` содержит абсолютный путь `REPO = r"C:\NanoLab\nl3-002-proto"` (worktree исполнительницы) — скрипт-свидетель не переносим без правки пути. Воспроизводимость при этом подтверждена: деривация воспроизведена независимым скриптом с относительным путём и дала байт-идентичный результат. Рекомендация: в будущих WO использовать путь относительно `__file__`. |

## Claim ceiling

- **C0_SOFTWARE_ONLY / pre-confirmatory preparation.** Никаких научных утверждений о реальном шарнире: манифест рук, детектор v2 и числа frame 0 — измеренные факты авторской init-конфигурации и калибровка ПО; E2 campaign = NOT_EVALUATED, физика = NOT_RUN (2e7 не запускался).
- Все θ-критерии, длины {2e5/1e6/2e7}, seeds и статистика — **DRAFT**; freeze — только Director в E2-PROTO-R1.
- Открытые пункты для Director корректно перечислены (режим v2 mutual vs greedy; выбор θ-вариантов; длина confirmatory; принятие arm-manifest-0b.json как замороженного манифеста; интерпретация угла 66.89° при конвенции v1).

## Вывод

**PASS.** Execution соответствует WO, пререгистрация соблюдена, v1-frozen артефакты не тронуты, деривация манифеста байт-воспроизводима на exact HEAD, стерильность (G1=B, U4=NO, отсутствие физики и байтов источника в Git) подтверждена. Findings — только INFO/LOW, ни одно не блокирует Director-freeze.
