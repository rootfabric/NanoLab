# EX-NL0-002-R1-REPAIR1 — Summary

```text
BASE_HEAD                = 495b03391e7eff72bbfbb5c5912e35ef9035b868  (original verified candidate;
                            верифицирован live перед repair: fetch --all --prune, pull --ff-only,
                            rev-parse HEAD = 495b0339…, PR #17 OPEN/MERGEABLE на этом head)
REPAIRED_CANDIDATE_HEAD  = cd55320441c2c904f8e406870c902fbff587c602  (последний substantive коммит перед
                            terminal event; = subject_sha терминального event 0005)
REPAIRED_CANDIDATE_TREE  = 131a54fe787294dbf43c45279270521326d4f939  (tree REPAIRED_CANDIDATE_HEAD)
HANDOFF_COMMIT           = коммит ПОСЛЕ terminal event; добавляет только 0005-handoff-completed.json,
                            этот summary и статусы passport/branch-passport; substantive результат
                            не меняет. Exact SHA финального PR head фиксируется в PR #17.
```

## Параметры

```text
WORK_ORDER = NL0-002 (repair по FRESH_VERIFIER_R1, verdict FAIL / FIX_REQUIRED)
VERIFIER_EVIDENCE = 48d6d0c0089d985118e629ac459c7aa9d85e85eb (docs/evidence/NL0-002/FRESH_VERIFIER_R1.md
                    на origin/control/nl0-002-fresh-verifier-r1)
RISK       = LOW (documentation / metadata / license evidence pinning)
CLAIM      = C0_SOFTWARE_ONLY
SCOPE      = ровно три verifier fix + два non-blocking уточнения; E1/E2 audit заново не повторялся
```

## Результаты repair

```text
FIX_1_IMMUTABLE_LICENSE_EVIDENCE = DONE — для scadnano, oxView, PyMBAR, AiiDA (aiida-core),
    aiida-shell, Ax, BoTorch зафиксированы: canonical repository (+ repo id), checked commit
    2026-09-08, license path, Git blob SHA-1, SHA-256, SPDX/licence result; целостность подтверждена
    git-style blob hashing 7/7 byte-exact. BoTorch canonical = meta-pytorch/botorch (repo id
    142940093); pytorch/botorch = исторический alias -> server-side redirect, тот же repo id.
    Runtime-версии — NL1-001; license audit воспроизводим по immutable subject.
FIX_2_GPL_BOUNDARY = DONE — введена классификация AGGREGATE / SEPARATE_EXECUTABLE /
    SAME_PROCESS_BINDING / MODIFIED_GPL_CODE; категоричное «создаст конфликт с Option A/B» удалено;
    зафиксировано: независимые MIT/Apache-2.0 файлы могут сосуществовать с GPLv3-материалом при
    корректной структуре распространения; обязанности combined covered work зависят от фактической
    интеграции и conveyance; oxDNA executable и oxpy binding — разные packaging situations;
    будущая same-process oxpy integration = REQUIRES_OWNER_DECISION + REQUIRES_LEGAL_REVIEW до
    фиксации release-архитектуры; безопасная политика DOWNLOAD_ON_SETUP + NO_VENDORING_YET сохранена.
FIX_3_GPL_OBLIGATIONS = DONE — «allowed under GPLv3 (+NOTICE)» удалено; заменено на: under GPLv3
    terms; preserve applicable copyright/license/no-warranty notices; provide a copy of GPLv3 when
    conveying covered source; corresponding-source obligations apply where relevant. Standalone
    NOTICE-файл явно не назван определяющей GPLv3-обязанностью. Citation policy отделена от license
    obligations (матрица §4 / §4.1).
NON_BLOCKING_1 = DONE — literal BASE_HEAD / REPAIRED_CANDIDATE_HEAD / REPAIRED_CANDIDATE_TREE в этом summary.
NON_BLOCKING_2 = DONE — раздельный подсчёт: «9 software dependencies CLEAR» (oxDNA/oxpy, oxDNA
    analysis tools, scadnano, oxView, PyMBAR, AiiDA, aiida-shell, Ax, BoTorch) и отдельно
    «E1 fixture CLEAR» (DSDNA8 — научный вход, отдельная строка матрицы, в девятку не входит).
```

## Подсчёт CLEAR (устранение двусмысленности)

```text
9 software dependencies CLEAR  = oxDNA/oxpy, oxDNA analysis tools, scadnano, oxView, PyMBAR,
                                 AiiDA, aiida-shell, Ax, BoTorch
E1 fixture CLEAR               = oxDNA DSDNA8 (4 файла test/DNA/DSDNA8) — научный вход под GPL-3.0,
                                 mode DOWNLOAD_ON_SETUP; отдельная строка матрицы, НЕ входит в «9»
Итого строк CLEAR в матрице    = 10 (9 программных зависимостей + 1 fixture), считаются раздельно
```

## Что не менялось (заморожено verifier'ом)

```text
E1 = GPL-3.0, mode DOWNLOAD_ON_SETUP            — не изменено
E2 rights = UNKNOWN, mode REFERENCE_ONLY        — не изменено
NANOBASE = UNKNOWN per-record                   — не изменено
S08 = RESTRICTED / reference-only project policy — не изменено
NanoLab LICENSE не назначен                     — не изменено
EX-NL0-002-R1/events/** (terminal 0005 последним) — не изменено
project/state.json / project/plan.json          — не изменены
NL0 не закрыт; PR #17 не merged                 — не изменено
```

## Validation

```text
python -m json.tool (passport + events 0001-0004 на момент прогона) -> OK
CONTROL_DEVELOPMENT.ps1 -CheckConsistency                           -> ok=true, errors=[], exit 0
CONTROL_WORK.ps1 validate (pre-terminal)                            -> ok=true, exit 0
CONTROL_WORK.ps1 close (после terminal)                             -> точный output зафиксирован
                                                                       в комментарии PR #17
```

## Ограничения

- Пины лицензий зафиксированы на 2026-09-08; дальнейшее движение upstream не отслеживалось (сверка — по blob SHA/SHA-256).
- Repair не является юридическим заключением; правовые интерпретации (aggregate/combined, binding) помечены как требующие owner decision / legal review, не решённые агентом.
- Runtime-пины PyPI-версий и сборки oxDNA — NL1-001; Ax/BoTorch — planned E3.

## Факты для аудита

```text
THIRD_PARTY_FILES_COPIED = NONE (только refs/hashes/metadata license evidence)
SIMULATIONS_RUN          = NONE (E0–E6 NOT_RUN, physics_runs = 0)
STATE_CHANGED            = NO (project/state.json не изменён)
```

## NEXT_ACTOR

```text
NEXT_ACTOR = FRESH_VERIFIER (fresh exact-head проверка repaired candidate по binding
             REPAIRED_CANDIDATE_HEAD cd55320441c2c904f8e406870c902fbff587c602).
PASS/ACCEPTED агентом не выставляется. Merge PR #17 — Human Gate.
```
