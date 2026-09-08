# NL0-002 — REPAIR MAP R1

Исполнение: `EX-NL0-002-R1-REPAIR1`. Вход: Fresh Independent Verifier R1, verdict **FAIL / FIX_REQUIRED** (`docs/evidence/NL0-002/FRESH_VERIFIER_R1.md` на `origin/control/nl0-002-fresh-verifier-r1`, commit `48d6d0c0089d985118e629ac459c7aa9d85e85eb`; verified head `495b03391e7eff72bbfbb5c5912e35ef9035b868`).

Правило применения: `FIX_REQUIRED` исправляется точечными исправлениями с новым evidence (этот документ), без повторного прогона E1/E2 audit и без изменения подтверждённых verifier'ом фактов.

## Блокирующие findings → исправления

### FIX 1 — audit evidence для не-E1/E2 зависимостей не зафиксирован (Verifier §3)

| Verifier finding | Исправление | Evidence |
|---|---|---|
| Колонка «Exact source/version» содержит только имена репозиториев/пакетов без immutable identity лицензии — отчёт невоспроизводим при изменении upstream | Для каждой из 7 зависимостей (scadnano, oxView, PyMBAR, AiiDA, aiida-shell, Ax, BoTorch) зафиксирован проверенный license subject: canonical repository (+ GitHub repo id), checked commit 2026-09-08, license path, Git blob SHA-1, SHA-256 содержимого, SPDX/licence result; целостность подтверждена локальным git-style blob hashing (byte-exact, 7/7) | `docs/evidence/NL0-002/LICENSE_EVIDENCE_PINS_R1.md` (полная таблица + метод); обновлённые строки матрицы: `docs/research/DEPENDENCY_LICENSE_MATRIX.md` §1 |
| BoTorch source должен указывать на canonical `meta-pytorch/botorch`; `pytorch/botorch` — исторический alias | Строка BoTorch в матрице переписана: canonical `meta-pytorch/botorch` (repo id 142940093, checked commit `d4b9fc655034f6c6186f1cdc73398b47d3d55b7f`), `pytorch/botorch` → server-side redirect на тот же repo id (live-проверка 2026-09-08); license blob `b93be90515ccd0b9daedaa589e42bf5929693f1f` = MIT | `LICENSE_EVIDENCE_PINS_R1.md` §«BoTorch — canonical source и исторический alias» |
| Runtime package versions может остаться NL1-001 | Оставлено как есть: пины фиксируют license subject, а не runtime-версии; оговорка вынесена в матрицу (текст под §1) и в пины | `DEPENDENCY_LICENSE_MATRIX.md` (примечание под таблицей); `LICENSE_EVIDENCE_PINS_R1.md` (абзац «Метод проверки») |

### FIX 2 — формулировка GPL aggregate/compatibility категорична (Verifier §4)

| Verifier finding | Исправление | Evidence |
|---|---|---|
| Аудит говорил, что вендоринг GPLv3-fixtures рядом с пермиссивным кодом NanoLab «создаст смешанное произведение и конфликт с Option A/B» — слишком категорично: GPLv3 различает aggregate и combined covered work | Формулировка заменена: наличие GPL-файла рядом с MIT/Apache-кодом само по себе не создаёт конфликта; независимые MIT/Apache-2.0 файлы могут сосуществовать с GPLv3-материалом при корректной структуре распространения; обязанности combined covered work зависят от фактической интеграции и conveyance | `RIGHTS_AND_REDISTRIBUTION_AUDIT.md` §1 «Анализ» (первые два пункта, переписаны) |
| Требуется различать `aggregate / separate executable / same-process binding or linking / modified GPL code` | Введена явная рабочая классификация четырёх ситуаций и границы упаковки | `DEPENDENCY_LICENSE_MATRIX.md` §2 (блок AGGREGATE / SEPARATE_EXECUTABLE / SAME_PROCESS_BINDING / MODIFIED_GPL_CODE); `RIGHTS_AND_REDISTRIBUTION_AUDIT.md` §1 новый подраздел «Границы для будущих packaging-решений» |
| Матрица в обратную сторону говорила, что copyleft «не распространяется автоматически» без различения executable vs binding — тоже слишком сильно | Заменено: `oxDNA executable` и `oxpy binding` — не одна и та же packaging situation; будущая same-process `oxpy` integration перед release-архитектурой помечена `REQUIRES_OWNER_DECISION` + `REQUIRES_LEGAL_REVIEW` | `DEPENDENCY_LICENSE_MATRIX.md` §2 (пункты о packaging situation и блок REQUIRES_*) |
| Консервативную политику `DOWNLOAD_ON_SETUP` / no-vendor сохранить | Сохранена и зафиксирована явно как безопасная политика до решений владельца: `DOWNLOAD_ON_SETUP` + `NO_VENDORING_YET`; `VENDOR_NOT_RECOMMENDED` переформулирован как проектная политика, а не юридическое утверждение | `DEPENDENCY_LICENSE_MATRIX.md` §2; `RIGHTS_AND_REDISTRIBUTION_AUDIT.md` §1 «Границы…», «Рекомендация» |
| Документ не должен выдавать себя за юридическое заключение | В обоих документах явные оговорки «не юридическое заключение» (заголовок §2 матрицы, подраздел границ аудита, пины) | `DEPENDENCY_LICENSE_MATRIX.md` §2; `RIGHTS_AND_REDISTRIBUTION_AUDIT.md` §1; `LICENSE_EVIDENCE_PINS_R1.md` (заключительная строка) |

### FIX 3 — свёртка GPLv3 obligations в «+NOTICE» некорректна (Verifier §5)

| Verifier finding | Исправление | Evidence |
|---|---|---|
| `allowed under GPLv3 (+NOTICE)` в матрице — неверная свёртка обязательств | Заменено на точную нейтральную формулировку: under GPLv3 terms; preserve applicable copyright/license/no-warranty notices; provide a copy of GPLv3 when conveying covered source; corresponding-source obligations apply where relevant | `DEPENDENCY_LICENSE_MATRIX.md` §1 (строки oxDNA/oxpy и E1 fixtures); §4.1 |
| «Говорит о будущем NOTICE-файле» как GPL-обязанности | Раздел: standalone NOTICE-файл не является определяющей обязанностью GPLv3; вопрос NOTICE связан с выбором собственной лицензии NanoLab (Apache-2.0 имеет собственные NOTICE-требования) и практикой атрибуции | `DEPENDENCY_LICENSE_MATRIX.md` §4.1 (последний абзац); упоминание «с NOTICE» удалено из `RIGHTS_AND_REDISTRIBUTION_AUDIT.md` §1 «Рекомендация» |
| Scientific citation policy держать отдельно от license obligations | §4 матрицы переименован и разделён: «4. Citation policy (научная атрибуция; отдельно от license obligations)» и «4.1 License obligations (GPLv3, нейтральная сводка)»; ссылка в аудите обновлена | `DEPENDENCY_LICENSE_MATRIX.md` §4/§4.1; `RIGHTS_AND_REDISTRIBUTION_AUDIT.md` §1 «Анализ» |

## Non-blocking замечания (Verifier §6, пп. 1–2)

| Замечание | Исправление | Evidence |
|---|---|---|
| 1. `summary.md` должен содержать literal HEAD/TREE, а не косвенные ссылки | `summary.md` repair execution содержит literal `BASE_HEAD = 495b03391e7eff72bbfbb5c5912e35ef9035b868`, `REPAIRED_CANDIDATE_HEAD`, `REPAIRED_CANDIDATE_TREE` (точные SHA) | `docs/work/executions/EX-NL0-002-R1-REPAIR1/summary.md` |
| 2. Уточнить подсчёт `9 CLEAR`: отделить «9 software dependencies CLEAR» от «E1 fixture CLEAR» | В матрице §2 блок `DEPENDENCIES_CLEAR = 9 software dependencies …` + `NOTE` о том, что E1 fixture — отдельная строка CLEAR вне девятки; то же разделение зафиксировано в `summary.md` repair execution | `DEPENDENCY_LICENSE_MATRIX.md` §2; `summary.md` (раздел «Результаты») |

Замечание §6 п.3 (пересмотр packaging при выборе лицензии владельцем) — не требовал действия в этом repair: он уже отражён как `REQUIRES_OWNER_DECISION` / owner decisions (матрица §2–3, аудит §1 «Границы…», §7).

## Неподвижные утверждения (проверены verifier'ом, изменению не подлежали и не изменены)

```text
E1 = GPL-3.0, mode DOWNLOAD_ON_SETUP            — не изменено
E2 rights = UNKNOWN, mode REFERENCE_ONLY        — не изменено
NANOBASE = UNKNOWN per-record                   — не изменено
S08 = RESTRICTED / reference-only               — не изменено
NanoLab LICENSE не назначен                     — не изменено
project/state.json, project/plan.json           — не изменены
EX-NL0-002-R1/events/**                         — не изменены (terminal 0005 остаётся последним)
Сторонние scientific файлы не копировались      — NONE
Симуляции не запускались                        — NONE
NL0 не закрывался, PR #17 не merged             — не изменено
```

## Ограничения repair

- Пины зафиксированы на 2026-09-08; дальнейшее движение upstream не отслеживалось (повторная сверка — по blob SHA/SHA-256 из таблицы).
- Repair не повторял независимую проверку E1/E2 — они PASS в Fresh Verifier R1 §2.
- Документы остаются implementer recommendation, не юридическим заключением; fresh exact-head Verifier — следующий actor.
