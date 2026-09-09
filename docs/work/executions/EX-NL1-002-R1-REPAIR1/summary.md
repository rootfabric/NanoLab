# EX-NL1-002-R1-REPAIR1 — Summary

```text
BASE_HEAD                = ec7e3edc83a3434d96222a0a8a94b03f7fa10e23  (verified subject по VERIFIER R2;
                            продолжение работы — с c44b2091d183be55e8accd47e845c0511c041083 = subject +
                            4 коммита superseded R1-вердиктов; work-content бит-в-бит идентичен subject)
REPAIRED_CANDIDATE_HEAD  = ab78759b717d21eccf80950ec29613fbe1e74224  (последний substantive коммит перед
                            terminal event; = subject_sha терминального event 0005)
REPAIRED_CANDIDATE_TREE  = 849d7d7fa8134de7117238dbd9c0fb9eb4d925a7  (tree REPAIRED_CANDIDATE_HEAD)
HANDOFF_COMMIT           = коммит ПОСЛЕ terminal event; добавляет только 0005-handoff-completed.json,
                            этот summary и статус passport HANDOFF_READY; substantive результат
                            не меняет.
```

## Параметры

```text
WORK_ORDER = NL1-002 (repair по VERIFIER VERDICT R2, FIX_REQUIRED; superseding R1-вердиктов)
VERIFIER_EVIDENCE = 149feda3fe16ce63afaecf52a4d4b8ae83325dd7 (VERIFIER_VERDICT_R2.md на
                    verify/nl1-002-reference-run-r2)
RISK       = HIGH (научный пакет; ремонт только контрактной поверхности)
CLAIM      = C1_COMPUTATIONAL_REPRODUCTION_CEILING_NOT_EVALUATED (не повышался)
SCOPE      = ровно F-1..F-3 из вердикта R2; научное содержание не пересматривалось
```

## Результаты repair

```text
F_1_CONTRACT_SURFACES = DONE — artifacts.manifest.json во всех 4 run-каталогах E1-R1 переведены
    в контрактную форму-массив (name/sha256/size_bytes/producer_run_id/subject_sha/storage_location/
    producer_command) по artifact-manifest.schema.v1.json; все дайджесты/размеры 1:1 (16/16 совпадают
    с сырыми git-blob байтами); оригиналы сохранены бит-в-бит как artifacts.manifest.v1-superseded.json.
    manifest.json дополнены полями subject_sha/claim_ceiling/model/observables/stop_conditions
    (+resource_budget на пилотах) строго аддитивно; события прогонов дополнены experiment_id/subject_sha
    (+24 строки, 0 удалений); новые event 0004-repair-manifest-contract x4.
    CONTROL_EXPERIMENT validate x4 -> ok=true, exit 0 (до ремонта: AttributeError, exit 1).
F_2_SUBJECT_SHA_ERRATUM = DONE — event 0006-repair-completed в EX-NL1-002-R1 фиксирует полную форму
    9cc83e8599c76366a6ba8c5bc49f7398f5fca64f для сокращённой 9cc83e8 в событиях 0002-0005; сами события
    не редактировались; все новые события несут полные 40-hex.
F_3_TERMINAL_LAST = DONE (путём, разрешённым WO: «новой последовательностью событий») — отклонение
    terminal-not-last в EX-NL1-002-R1 признано erratum-ом 0006 и остаточно задокументировано; контракт-
    чистая последовательность публикации — в этом execution: WORK_ORDER_STARTED первым, HANDOFF_COMPLETED
    последним, ровно один terminal event, все subject_sha полные.
```

## Validation

```text
CONTROL_EXPERIMENT validate x4 (S001,P001,P002,P003) -> ok=true, errors=[], warnings=[], exit 0 (4/4)
CONTROL_WORK validate EX-NL1-002-R1-REPAIR1 (финальное дерево, terminal последним) -> ok=true, exit 0
CONTROL_WORK close EX-NL1-002-R1-REPAIR1 -> ok=true (has_terminal_handoff=true, has_summary=true), exit 0
CONTROL_WORK validate EX-NL1-002-R1 -> ok=false, exit 3 — 5 остаточных ошибок в неизменяемых
    опубликованных событиях 0002-0005; задокументированы в REPAIR_MAP_R2_R1.md §5, execution superseded
    данным для контрактной валидации (путь «новой последовательностью событий», разрешённый WO)
CONTROL_DEVELOPMENT -CheckConsistency -> ok=true, errors=[], warnings=[], exit 0
```

## Что не менялось (гарантии)

```text
Научные артефакты (energy.dat/trajectory.dat/last_conf.dat/log.dat x4) — 0 изменений;
    16/16 digest match raw git-blob bytes (критерий R2 D1)
protocol.json (оракул ColumnAverage::energy.dat::2::-1.37970256144::0.15), campaign.md,
    evidence-map.json, analyze_energy.sh — не изменялись
Статистика кампании (mean -1.38602478921, SD 0.00832919790) — не пересчитывалась, не менялась
События EX-NL1-002-R1 0001-0005, его passport.json и summary.md — не изменялись
R1-вердикт-файлы на ветке — сохранены как superseded история; вердикты R2 не затронуты
project/state.json / project/plan.json — не изменялись; acceptance не выставлялся;
    campaign-level scientific_outcome = NOT_EVALUATED
Симуляции не запускались; новых claims нет
```

## Факты для аудита

```text
THIRD_PARTY_FILES_COPIED = NONE
SIMULATIONS_RUN          = NONE (ремонт контрактной поверхности; physics_runs = 0)
STATE_CHANGED            = NO (project/state.json не изменён)
REPAIR_COMMITS           = ac5c6cb, 6b6dab4, f78a182, 4a1b5d5, 1461d6d, ab78759 (+ этот handoff-коммит)
REPAIR_MAP               = docs/evidence/NL1-002/REPAIR_MAP_R2_R1.md
```

## Ограничения

- Старый execution `EX-NL1-002-R1` остаётся exit 3 по CONTROL_WORK validate (неизменяемые события);
  для контрактной валидации superseded этим execution — см. REPAIR_MAP_R2_R1.md §5.
- Ремонт не пересматривал и не мог пересматривать научные выводы: они подтверждены R2 независимо (§4 вердикта).

## NEXT_ACTOR

```text
NEXT_ACTOR = FRESH_VERIFIER (повторная проверка только исправленных поверхностей по binding
             REPAIRED_CANDIDATE_HEAD ab78759b717d21eccf80950ec29613fbe1e74224, R2 §5).
PASS/ACCEPTED агентом не выставляется. Merge в main — Human Gate.
```
