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
