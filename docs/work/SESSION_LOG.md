# Журнал передачи работы

Записи добавляются, а не переписываются в пользу последнего успеха. Каждая запись содержит subject, scope, реальные действия/проверки, ограничения и следующий шаг. Самореферентный SHA текущего файла не требуется: ссылаться на проверенный предшествующий subject или отдельный отчёт публикации.

## FOUNDATION-R1 — Инициализация плана

Основание: запрос владельца сохранить обсуждённые цели и планы в новом rootfabric/NanoLab. Репозиторий прочитан через подключённый GitHub: исходно пустой, веток не было. Создан bootstrap commit `1eb156bc83e3b86afaeebd2e6ea8444e5d85f697`.

Подготовлены миссия, архитектура, NL0–NL8, паспорта E0–E6, очередь работ, правила агентов, контракты и реестр источников. Сохранены будущие направления наноматериалов, наноэлектроники, управления и наномашин. Ранее предложенный 2D-Materials MVP перенесён в портфель, а не потерян.

Проверены описания основных upstream-инструментов и часть первичной литературы; это не проверка их интеграции. Уточнены библиографические ссылки на исследования подвижных ДНК-компонентов. Полные исходные пакеты экспериментов пока не получены.

Научный runtime не написан; физические симуляции, AI-кампании и внешнее воспроизведение не выполнялись. Не запускались Actions, runner или платные вычисления. Лицензия NanoLab не назначалась.

Следующее действие: **NL0-001 — выбрать фактически воспроизводимый эталон**, затем аудит прав и пререгистрация. Результаты технической проверки документального пакета фиксируются в отдельном evidence-отчёте после выполнения проверки.

## HARNESS-R1 — Development + Experiment Harness

Основание: запрос владельца использовать действующий harness `rootfabric/distributed-world-simulator` как базу для NanoLab и обязать агентов фиксировать начало, продолжение и конец задач/экспериментов в Git.

Base canonical main: `3714ae7d7dacb7ba90eedea4c1d6539c9d80225b`. Создана ветка `control/nanolab-harness-r1`. Из DWS перенесены control principles: main-owned state, bounded Work Orders, durable Git memory, risk routing, independent evidence review и preauthorized routine Git. DWS-specific Godot scheduler не переносился.

NanoLab extension: `Experiment Run` как отдельная scientific execution unit; preregistration; frozen subject; START/CONTINUATION/END; отдельные technical/scientific outcomes; claim ladder C0–C5; artifact manifest с SHA-256/provenance. Добавлены cross-platform control wrappers и standard-library Python validators для project/work/experiment state.

Проверенный machine subject: `253b44262001bf36779a2c4ea2cd5bff9bfbe5b2`, tree `94b46bfb76ab5a3eb63af5d5cfeaf877a2427bfd`. Positive/negative isolated smokes для Work и Experiment validators прошли ожидаемо. Full clone контейнера заблокирован DNS; Actions и Windows runtime не использовались. Полный отчёт: `docs/evidence/HARNESS_R1_CHECKS.md`.

Harness setup не изменяет scientific frontier: `NL0`, next `NL0-001`, E0–E6 `NOT_RUN`.

Следующее действие после канонизации harness: начать `NL0-001` уже по новым правилам — создать execution passport + `WORK_ORDER_STARTED` в Git до substantive research.
