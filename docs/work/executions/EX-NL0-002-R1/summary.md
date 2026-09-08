# EX-NL0-002-R1 — Summary

```text
BASE_SHA = 95b1319600bcc64572d84c0456acb927802ab806
HEAD     = см. binding ниже
TREE     = фиксируется terminal event 0005 и PR (candidate head)
```

## Binding (hardening: terminal event ↔ final handoff HEAD)

```text
START_COMMIT              = 6a35586642bc9162e5b6f02ab4071a4332a30b45  (harness: start)
CORE_RIGHTS_COMMIT        = 57fea0628df0126ace877c81bdd60b8ad476536f3  (research: core rights checkpoint)
IMPLEMENTATION_COMMIT     = 0b51aa179342ae73c6a81db3a5eaf4c77e92ffe7  (research: evidence package)
EVENT_SHA_BINDING_COMMIT  = 73ac4c1cfcc813d88f61a5e3e5e94c5f1f4ede23  (harness: event sha fix)
SUBSTANTIVE_HEAD          = коммит, непосредственно предшествующий terminal event
                            (содержит все substantive артефакты включая этот summary);
                            exact SHA записан в 0005-handoff-completed.subject_sha
HANDOFF_COMMIT            = единственный коммит ПОСЛЕ terminal event; содержит только
                            0005-handoff-completed.json + статус passport/branch-passport;
                            substantive результат не меняет
```

## Параметры

```text
WORK_ORDER = NL0-002 (docs/work/WO-NL0-002.md, из issue #3)
RISK       = LOW (documentation/metadata/rights audit)
CLAIM      = C0_SOFTWARE_ONLY
```

## Результаты

```text
E1_RIGHTS = CLEAR — GPL-3.0 (root LICENSE blob 94a9ed0, GitHub API на pinned commit 00dc7fb),
            fixtures покрыты root license; режим DOWNLOAD_ON_SETUP; citation obligations
            (JOSS 4693 / JCC 23763 / NAR gkab324) зафиксированы.
E2_RIGHTS = UNKNOWN → REQUIRES_OWNER_DECISION — LICENSE отсутствует во всём pinned tree
            (23fd1ff), GitHub license detection пустая, README без правовых statements;
            режим REFERENCE_ONLY + user-side download by exact commit; копирование/mirror/
            release запрещены до разрешения авторов или решения владельца.
MVP_DEPENDENCY_MATRIX = 9 CLEAR (oxDNA/oxpy, oxDNA analysis tools, scadnano, oxView, PyMBAR,
            AiiDA, aiida-shell, Ax, BoTorch — как отдельно устанавливаемые зависимости),
            1 RESTRICTED (S08 ACS materials, cite-only), 3 UNKNOWN (E2 pack, NANOBASE
            per-record, sulcgroup/hinges deferred).
NANOLAB_LICENSE_OPTIONS = Apache-2.0 / MIT / GPL-3.0-or-later (код);
            CC BY 4.0 / CC BY-SA 4.0 (документация). Лицензия НЕ назначена — решение владельца.
```

## Решения владельца / неизвестное

```text
UNKNOWN_RIGHTS =
  E2 DNA-hinge-simulations (redistribution/modification/release/mirror/durable-cache)
  NANOBASE per-record
  sulcgroup/hinges + Zenodo (deferred, вне MVP)

OWNER_DECISIONS_REQUIRED =
  1. Лицензия NanoLab (код + документация [+ данные отдельно])
  2. Контакт авторов DNA-hinge-simulations за явной лицензией либо замена E2 seed
  3. Политика private durable caching UNKNOWN-файлов
  4. Разрешение вендоринга GPLv3-fixtures (зависит от п.1)
```

## Validation

```text
python -m json.tool state.json/plan.json/events/passport -> OK
CONTROL_DEVELOPMENT.ps1 -CheckConsistency                 -> ok=true, exit 0
CONTROL_WORK.ps1 validate (pre-handoff)                   -> exit 3: только отсутствие
                                                            terminal/summary (ожидаемо);
                                                            структурных errors нет
CONTROL_WORK.ps1 close (после terminal)                   -> см. PR/issue комментарий
```

## Limitations

- Не юридическое заключение; неоднозначные случаи переданы как OWNER_DECISION, не решены агентом.
- NANOBASE недоступен для прямой проверки из сетевого контура исполнения (использована публикация S10).
- Runtime-пин версий PyPI/сборки oxDNA — NL1-001; Ax/BoTorch — planned E3.
- Environment incident: внешняя реструктуризация workspace (checkout → клоны main/nl0-002) в середине
  исполнения; два несоммиченных файла потеряны из working tree и восстановлены дословно; remote/коммиты
  не пострадали (детали: event 0002, IMPLEMENTER_EVIDENCE.md).

## Факты для аудита

```text
THIRD_PARTY_FILES_COPIED = NONE (только refs/hashes/metadata)
SIMULATIONS_RUN          = NONE (E0–E6 NOT_RUN, physics_runs = 0)
project/state.json       = не изменён Implementer'ом
```

## NEXT_ACTOR

```text
NEXT_ACTOR = VERIFIER (LOW-risk routing: docs/metadata требуют независимого Verifier).
Reviewer перед Verifier не обязателен по risk-policy, но желателен по усмотрению владельца:
в аудите есть правовые интерпретации (GPL copyleft/bundling), явно помеченные как не-решения.
```
