# Журнал передачи работы

Записи добавляются, а не переписываются в пользу последнего успеха. Каждая запись содержит subject, scope, реальные действия/проверки, ограничения и следующий шаг. Самореферентный SHA текущего файла не требуется: ссылаться на проверенный предшествующий subject или отдельный отчёт публикации.

## FOUNDATION-R1 — Инициализация плана

Основание: запрос владельца сохранить обсуждённые цели и планы в новом rootfabric/NanoLab. Репозиторий прочитан через подключённый GitHub: исходно пустой, веток не было. Создан bootstrap commit `1eb156bc83e3b86afaeebd2e6ea8444e5d85f697`.

Подготовлены миссия, архитектура, NL0–NL8, паспорта E0–E6, очередь работ, правила агентов, контракты и реестр источников. Научный runtime не написан; физические симуляции, AI-кампании и внешнее воспроизведение не выполнялись.

Следующее действие: **NL0-001 — выбрать фактически воспроизводимый эталон**, затем аудит прав и пререгистрация.

## HARNESS-R1 — Development + Experiment Harness

Основание: запрос владельца использовать действующий harness `rootfabric/distributed-world-simulator` как базу для NanoLab и обязать агентов фиксировать начало, продолжение и конец задач/экспериментов в Git.

Base canonical main: `3714ae7d7dacb7ba90eedea4c1d6539c9d80225b`. Создана ветка `control/nanolab-harness-r1`. Из DWS перенесены control principles: main-owned state, bounded Work Orders, durable Git memory, risk routing, independent evidence review и preauthorized routine Git. DWS-specific Godot scheduler не переносился.

NanoLab extension: `Experiment Run` как отдельная scientific execution unit; preregistration; frozen subject; START/CONTINUATION/END; technical/scientific outcomes; claim ladder C0–C5; artifact manifest с SHA-256/provenance. Проверенный machine subject: `253b44262001bf36779a2c4ea2cd5bff9bfbe5b2`, tree `94b46bfb76ab5a3eb63af5d5cfeaf877a2427bfd`.

Harness setup не изменил scientific frontier: `NL0`, next `NL0-001`, E0–E6 `NOT_RUN`.

## EX-NL0-001-R1 — первый Work Order через Harness

Canonical base: `9d8ea394c6c037b0560908689e2ce932bf0c511c`. Branch: `work/nl0-001-reference-selection-r1`. Durable START commit: `3c94662340f1885d4aa6fe4360d4f4676bfe9bb8`; source-inspection checkpoint: `73997369d7f83ef7d60585223c1128eef729204c`; implementer research commit: `dd5cef3c8bd7212c64da4c80fedb5ca03169eac9`.

Проверены три E1-кандидата из pinned official oxDNA upstream. Выбран DSDNA8/MD: 16 nucleotides, два strands, CPU input на 1e6 steps и существующий upstream `quick_compare`. Для его topology/config/input/oracle записаны SHA-256 и Git blob identities.

Первоначальный S08 hinge source проверен повторно: ACS SI даёт definitions/results PDF и movies, но bounded inspection не обнаружил отдельного machine-readable caDNAno/oxDNA input pack. Это сохранено как `INPUT_PACK_NOT_LOCATED`.

Найден более сильный executable E2 source: Shi–Castro–Arya DOI `10.1021/acsnano.7b00242` и авторский `gauravarya77/DNA-hinge-simulations@23fd1ff7731e9017bd776f49206dc42d70d9fe91`. Подтверждены пять caDNAno designs, пять `.top/.conf` пар, preparation scripts и CPU/GPU inputs. Repository не содержит отдельного LICENSE в inspected tree — rights остаются для NL0-002.

Ни один physics run не запускался; E0–E6 остаются `NOT_RUN`. Work Order передаётся независимому Reviewer/Verifier как HIGH-risk candidate selection; implementer не выставляет ACCEPTED.

Следующее действие после review: NL0-002 license/redistribution audit и NL0-003 preregistration E1/E2 protocols. NL0 целиком не закрыт.

## NL0-001-DIRECTOR-R1 — каноническая приёмка

Exact Implementer candidate: `f738bff77f2406552b4383c05989ffc6e56a3bd5`.

Fresh Reviewer evidence: `e0303aa05bbcc3f6839c3af31d7a28ecbd66a932`, verdict `PASS`, epoch drift `CONTINUE`.

Fresh Verifier evidence: `1a9bf9ca2288021b0371b858c77bd648dac2faaf`, verdict `PASS`, exact candidate/review binding `YES`, E1 hash/E2 tree/Harness close/state safety checks `PASS`.

PR #11 merged с expected-head guard в `142ed2df0a971763567d6cc672a218d04ee85201`; текущий INFRA drift не изменил scientific contracts NL0-001.

Director decision: `NL0-001 = ACCEPTED`. Канонически приняты E1 reference DSDNA8/MD и E2 Shi–Castro–Arya hinge family как входы для следующих protocol/runtime работ. Это не означает, что E1/E2 выполнены: E0–E6 остаются `NOT_RUN`, `physics_runs=0`.

State transition: `NL0` остаётся `IN_PROGRESS`; `NL0-002` и `NL0-003` становятся `READY`; scheduler priority — `NL0-002`. Полный acceptance record: `docs/evidence/NL0-001/DIRECTOR_ACCEPTANCE_R1.md`.

Следующее действие: выполнить `NL0-002` license/redistribution audit; `NL0-003` может готовиться параллельно отдельным Work Order при отсутствии file/scope conflict.

## EX-NL0-002-R1 — аудит прав и лицензий

Canonical base: `95b1319600bcc64572d84c0456acb927802ab806`. Branch: `work/nl0-002-license-rights-audit-r1`. Durable START commit: `6a35586` (pushed до substantive work). Core rights checkpoint: `57fea06`.

Независимая live-проверка через GitHub API на pinned commits. E1: root LICENSE репозитория oxDNA — полный GPL-3.0 текст (blob `94a9ed0`), fixtures покрыты root license, citation-обязанности в README; `E1_RIGHTS = CLEAR`, режим `DOWNLOAD_ON_SETUP`. E2: полный tree `DNA-hinge-simulations@23fd1ff` не содержит LICENSE нигде, GitHub license detection пустая, README без правовых statements; `REDISTRIBUTION_RIGHTS = UNKNOWN`, режим `REFERENCE_ONLY` + user-side download by exact commit, решение за владельцем (контакт авторов). S08 — `RESTRICTED` (cite-only). NANOBASE — per-record UNKNOWN. MVP-зависимости: MIT (scadnano, PyMBAR, AiiDA, aiida-shell, Ax, BoTorch) и GPL-3.0 (oxDNA stack, oxView); всё CLEAR как отдельно устанавливаемые зависимости. Варианты лицензии NanoLab (Apache-2.0/MIT/GPL-3.0-or-later + CC BY/CC BY-SA для документации) подготовлены, лицензия не назначена.

Incident (environment, не scientific): внешняя реструктуризация workspace в середине исполнения заменила одиночный checkout на клоны main/nl0-002; два несоммиченных research-файла потеряны из working tree и восстановлены дословно из сессионного содержимого; remote branch и все push-коммиты не пострадали.

Ни один physics run не запускался; E0–E6 остаются `NOT_RUN`; сторонние научные файлы в NanoLab не копировались. Implementer не выставляет ACCEPTED; результат передаётся независимому Verifier (LOW risk) с явными owner decisions.

Следующее действие: independent Verifier проверяет матрицу/audit по exact HEAD; владелец решает лицензию NanoLab и судьбу E2-запроса авторам.

## EX-NL0-002-R1-REPAIR1 — bounded repair по Fresh Verifier R1

Вход: FRESH_VERIFIER_R1 verdict FAIL / FIX_REQUIRED (evidence `48d6d0c`, ветка `control/nl0-002-fresh-verifier-r1`), verified head `495b0339`. База repair подтверждена live: PR #17 OPEN/MERGEABLE на `495b0339`, ff-only pull без изменений.

Закрыты ровно три verifier fix: FIX 1 — immutable license pins для 7 software dependencies (canonical repo + checked commit 2026-09-08 + license path + Git blob SHA-1 + SHA-256 + SPDX; git-style blob verify 7/7 byte-exact; BoTorch canonical `meta-pytorch/botorch`, `pytorch/botorch` → redirect, тот же repo id) в `LICENSE_EVIDENCE_PINS_R1.md` + матрице; FIX 2 — GPL boundary wording (AGGREGATE / SEPARATE_EXECUTABLE / SAME_PROCESS_BINDING / MODIFIED_GPL_CODE; MIT/Apache-файлы могут сосуществовать с GPLv3-материалом; обязанности combined work зависят от интеграции и conveyance; oxDNA executable ≠ oxpy binding; будущая same-process oxpy integration → REQUIRES_OWNER_DECISION + REQUIRES_LEGAL_REVIEW; политика DOWNLOAD_ON_SETUP / NO_VENDORING_YET сохранена); FIX 3 — «GPLv3 (+NOTICE)» заменено на точную нейтральную формулировку obligations, citation policy отделена от license obligations (§4/§4.1). Non-blocking: literal BASE_HEAD/REPAIRED_CANDIDATE_HEAD/REPAIRED_CANDIDATE_TREE в summary; раздельный подсчёт «9 software dependencies CLEAR» vs «E1 fixture CLEAR».

Связка repair: BASE_HEAD `495b0339`, REPAIRED_CANDIDATE_HEAD `cd55320441c2c904f8e406870c902fbff587c602` (tree `131a54fe787294dbf43c45279270521326d4f939`, terminal event 0005 subject). Коммиты: `ba38958` start → `2e551d3` pins → `9e48125` GPL wording → `cd55320` validation → handoff. Замороженные факты (E1 GPL-3.0/DOWNLOAD_ON_SETUP; E2 UNKNOWN/REFERENCE_ONLY; NANOBASE per-record UNKNOWN; S08 RESTRICTED) и все EX-NL0-002-R1 events не изменялись. Симуляции не запускались; сторонние файлы не копировались; state.json не изменён; NL0 не закрыт; PR #17 не merged; PASS/ACCEPTED не выставлен.

Следующее действие: fresh exact-head Verifier по repaired candidate; merge PR #17 — Human Gate.

## EX-NL0-003-R1 — пререгистрация протокола E1 и постановка E2

Canonical base: `81e299f1924e50bcff1bc5c893bccd934ef2883d` (origin/main совпал live). Branch: `work/nl0-003-preregister-reference-protocol-r1` (отдельный worktree). Durable START commit: `9372b79e1406ffd2d0853bcd3c8f2232062f737c` (pushed до substantive work). Source checkpoint: `53379e4973158e38531e346461d625b421f93cdf`. Substantive HEAD: `3450866925ce49fc81ee658806d3ec81b2e1bc81` (tree `a18762b9bc577a92eb10b923801b974f42fd4273`).

Issue #4 восстановлен через GitHub API дословно, acceptance criteria не расширены. Входы E1 повторно верифицированы на pinned upstream commit `00dc7fb9…`: 4/4 SHA-256 MATCH против пинов INPUT_AVAILABILITY (один transient raw-404, устранён повтором; файлы во временный каталог ОС, в репозиторий не копировались).

Опубликован `E1-PROTO-R1` (`PREREGISTRATION_E1_R1.md`): subject/SHA-256, verbatim условия из `quick_input` (CPU, 1e6 steps, john, T 20C, dt 0.005 и т.д.), observable = среднее колонки 2 `energy.dat` с upstream-оракулом `ColumnAverage::energy.dat::2::-1.37970256144::0.15` из `quick_compare` (критерий не подгоняется), схема T1 (upstream-equivalent) + T2 (robustness), пилот-процедура и freeze для `R_confirm`, разделение статистической/физической/модельной неопределённостей, семантика SUPPORTED / NOT_SUPPORTED / FAILED_TECHNICAL / INCONCLUSIVE / BLOCKED_ENVIRONMENT. Не выдуманы и помечены UNKNOWN: effective interaction_type/salt/thermostat-delta (defaults engine), семантика колонки 2, R_confirm, engine pin (NL1-001), measured budget.

Опубликован `E2-SETUP-R1` (`E2_SETUP_R1.md`): первый шарнир `0b`, требования к определению угла/целостности (числа — только из спиненного SI перед E2-PROTO), decision rule 298 K vs 300 K (reproduction arm = авторские inputs verbatim по exact commit; расхождение документируется, не замалчивается), family = пять опубликованных вариантов, hard dependencies: права `DNA-hinge-simulations` (owner decision с NL0-002), методология E0/E1 (NL2), engine pin (NL1-001). E2-файлы не скачивались (REFERENCE_ONLY).

Validation: json.tool 6/6 OK; CONTROL_DEVELOPMENT -CheckConsistency ok=true exit 0; CONTROL_WORK validate ok=true. Симуляции не запускались (`E0–E6 NOT_RUN`, `physics_runs=0`); state.json/plan.json не изменялись; ACCEPTED не выставлен. Риск HIGH → независимый REVIEWER, затем VERIFIER, затем Director checkpoint; merge — Human Gate.

Следующее действие: независимый review/verify по exact substantive HEAD; после PASS — checkpoint proposal владельцу (merge).

## NL0-003-DIRECTOR-R1 — каноническая приёмка

Exact subjects: base `81e299f…`, START `9372b79e`, substantive `9404a422` (tree `b8b1bd99`), PR head `6e30aee7`.

Fresh Reviewer R1: **PASS** (0 blocking / 2 minor), evidence `36c68e15` (ветка `review/nl0-003-preregistration-r1`): критерии зафиксированы до кампании (verbatim upstream-оракул), пилот-дисциплина freeze корректна, семантика исходов различена, 298 K vs 300 K решён decision rule без замалчивания, числа не выдуманы, overclaim'ов нет.

Fresh Verifier R1: **PASS**, evidence `ecc5dabf` (ветка `verify/nl0-003-preregistration-r1`): независимо 4/4 SHA-256 и 4/4 git blob upstream входов, verbatim `quick_input`/`quick_compare`, binding `9404a422`/tree `b8b1bd99`, diff в allowed_paths, state/plan/policies не тронуты, JSON по схемам, контролы exit 0, числа без трассировки не найдены.

Checkpoint proposal: `ebafd1e4` (ветка `control/nl0-003-director-checkpoint-r1`). Владелец явно разрешил публикацию в сессии; PR #21 merged с race-guard `expectedHeadOid=6e30aee7` (origin/main оставался на base до merge), merge commit `678be065`. MINOR findings сохранены с dispositions: §6.1 маркировка ASSUMED → `E1-PROTO-R2`; label SUBSTANTIVE_HEAD в evidence → авторитетен terminal binding `9404a422`.

Director decision: `NL0-003 = ACCEPTED`; `NL0 = ACCEPTED` (checkpoint-catalog: references ✓, access/rights ✓, preregistered E1 scope + E2 постановка ✓); frontier → `NL1`; `NL1-001 = READY`, scheduler priority. `E0–E6` остаются `NOT_RUN`, `physics_runs = 0`. Полный acceptance record: `docs/evidence/NL0-003/DIRECTOR_ACCEPTANCE_R1.md`.

Следующее действие: `NL1-001 — pin environment and upstream smoke`; владельцу: права `DNA-hinge-simulations` (контакт авторов) и лицензия NanoLab остаются открытыми owner decisions.

## 2026-09-09 — NL1-001 (EX-NL1-001-R1) — environment pin + upstream smoke, IMPLEMENTER handoff

Mission владельца: «выполняй NL1» (главный агент сессии DSH harness). Base = 57c1e63733ea3b10f991c0f9609c426dc75b17a5 (fresh origin/main), ветка work/nl1-001-env-pin-smoke-r1, START dd4692d.

Опубликован environment pin ENGINE_ENVIRONMENT_R1: WSL2 Ubuntu 24.04.2 (gcc 13.3.0, cmake 3.31.6 user-local с проверкой SHA-256 против Kitware, без sudo и без глобальных изменений системы); oxDNA собран из pinned upstream commit 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591 (CPU Release, DOUBLE=ON, CUDA/MPI=OFF; build 14.1 s; SHA-256 бинарей записаны). Fixture DSDNA8 верифицирован 4/4 SHA-256 против пинов E1-PROTO-R1 §2.2 через сырые blob'ы. Негативная находка сохранена: Windows working-tree checkout с core.autocrlf=true искажает fixture-байты (4/4 mismatch; PowerShell-пайплайн тоже) — канонический путь для всех будущих прогонов: git cat-file blob + bash redirect в Linux.

Upstream smoke EX-NL1-001-SMOKE-001 (вход с сокращённым steps=1e4, не E1-прогон): COMPLETED, exit 0, wall 0.13 s, max RSS 6424 KB, 0.0100 ms/step, NaN/Inf=0, «everything went OK». Effective defaults закрыты из лога/исходников pinned commit: interaction_type=dna (default, average-режим, seq-файл не загружен), john = alias BrownianThermostat (pt=0.019929118, pr=0.006687465), T 20C → 0.097717, salt NOT_APPLICABLE, seed случайный; колонка 2 energy.dat = потенциальная энергия на нуклеотид (PotentialEnergy.cpp: energy /= N) — ASSUMED §5.1 → OBSERVED-in-source. Verbatim 1e6-step прогон НЕ выполнялся (запрет E1-PROTO-R1 §7). Claim C0, научные утверждения отсутствуют. Planning-оценка бюджета E1: ~10–15 c/прогон на ядро.

Handoff: независимый REVIEWER → независимый VERIFIER → Director checkpoint → PR (merge — Human Gate).

Director decision (2026-09-09): NL1-001 = ACCEPTED. Основание: EX-NL1-001-R1 (environment pin ENGINE_ENVIRONMENT_R1: oxDNA 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591, WSL2 Ubuntu 24.04.2, gcc 13.3.0, cmake 3.31.6 user-local; fixture 4/4 SHA-256; smoke EX-NL1-001-SMOKE-001 COMPLETED exit 0, 0.13 s / 6424 KB, NaN/Inf=0) + независимые REVIEWER PASS (737b3eb) и VERIFIER PASS (ea486e2) на exact subject 39b3448. Findings MINOR исправлены (d81bf63: байт-починка SESSION_LOG после PowerShell-escaping и erratum формулировки smoke-отклонений; 462050f: passport HANDOFF_READY). Claim C0_SOFTWARE_ONLY; E0-E6 остаются NOT_RUN, physics_runs = 0. UNKNOWN E1-PROTO-R1 SS11.1-3 закрыты (effective defaults; колонка 2 = U/N). Verbatim-прогоны E1 разблокированы. Полный acceptance record: docs/evidence/NL1-001/DIRECTOR_ACCEPTANCE_R1.md.

Следующее действие: NL1-002 - первый вертикальный E1 путь (T1 verbatim + 3 PILOT + анализ + архив + freeze R_confirm в E1-PROTO-R2); merge - Human Gate (авторизация владельца запрашивается отдельно после review NL1-002).

## 2026-09-09 — INFRA0-001 (EX-INFRA0-001-R1) — compute trust and execution baseline, DIRECTOR acceptance

Mission владельца: закрыть INFRA0-001 по процедуре NL1-001 director acceptance (DIRECTOR INFRA-линии; явная авторизация владельца на приёмку и merge в main). Implementation: `infra/infra0-execution-baseline-r1` @ `9427ff1` (base canonical main `71535d0`; база исполнения `57c1e63`). Опубликован baseline `EXECUTION-BASELINE-R1` (docs/infra/EXECUTION_BASELINE_R1.md) + machine-readable `config/infra/execution-baseline.v1.json`: 7 trigger routes (TR-PR/TR-PUSH-MAIN hosted-only; TR-DISPATCH protected RESERVED_NOT_ACTIVE; TR-PRT/TR-WFRUN FORBIDDEN_R1), классы H0/C0/G0/H1 с reserved labels, токен-политика read-only, RC0–RC3 (paid compute запрещён), artifact policy, NC-1..NC-7, threat matrix, 11 non-goals. Runners/workflows/secrets — NONE; научный трек не затронут.

Независимые вердикты: REVIEWER PASS (`41c1382`; MINOR-1..4, NOTE-1..3), VERIFIER PASS (`40d6c4a`; FINDING-1..3, 36/36 doc↔config сверок, jsonschema events 4/4, secret-скан 0). Оба влиты в `control/infra0-director-checkpoint-r1` merge-коммитами. Corrections (event 0005, actor DIRECTOR): erratum `42db4cc` — MINOR-2 (§8 формулировка + удаление U+00AD), MINOR-3 (§4 TR-DISPATCH синхронизирован с конфигом, G0 только после INFRA5-001). MINOR-1 принят с условием: механический NC-1-тест — блокирующий критерий приёмки INFRA1-002. MINOR-4/NOTE-1..3 приняты к сведению.

Director decision (2026-09-09): INFRA0-001 = ACCEPTED; checkpoint INFRA0 = ACCEPTED (frontier INFRA0 закрыт). Claim C0_SOFTWARE_ONLY; capabilities.* все false (ни CI, ни runner не установлены — принят контракт, не инфраструктура). Baseline doc + config переведены PROPOSED → ACCEPTED этим решением. State: `project/infra-state.json` frontier → INFRA1, next_work_order → INFRA1-001 (READY), INFRA1 → IN_PROGRESS. Полный acceptance record: docs/infra/evidence/INFRA0-001/DIRECTOR_ACCEPTANCE_R1.md.

Следующее действие: INFRA1-001 «Add hosted harness CI» — первый hosted workflow по baseline §4–§6 (TR-PR/TR-PUSH-MAIN только на H0, минимальные permissions, pinned actions); далее INFRA1-002 с блокирующим механическим NC-1-тестом.
