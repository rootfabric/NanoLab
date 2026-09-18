# Лицензии и права

Состояние: **OWNER_DECISION D2 принят 2026-09-18**. Код NanoLab лицензируется по **Apache-2.0**; документация и NanoLab-owned производные данные/результаты — по **CC-BY-4.0**. Root `LICENSE` и `LICENSE-DOCS-DATA.md` являются release-поверхностями этого решения. Сторонние/upstream материалы не перелицензируются.

На NL0 варианты были подготовлены; финальное решение принято владельцем в D2 и зафиксировано в `docs/control/NL5_001_D_LICENSE_DECISION_R1.md`. Будущая смена лицензии требует нового явного owner decision.

Для каждой сторонней зависимости или конструкции фиксируются источник, версия, copyright/лицензионный текст, ограничения распространения и требуемое цитирование. Лицензия кода не переносится автоматически на веса моделей, данные, изображения или дополнительные материалы статьи.

До проверки прав исходные научные файлы не копируются в репозиторий. Допускается хранить библиографическую ссылку и статус доступа. Нельзя обещать открытый downloadable benchmark, если входные файлы нельзя законно передать другим.

Это рабочая политика проекта, а не юридическое заключение. Вопрос выбора и совместимости лицензий остаётся отдельным пунктом NL0-002.

## Обновление NL0-002 (EX-NL0-002-R1)

Аудит прав выполнен и передан на review: [DEPENDENCY_LICENSE_MATRIX.md](docs/research/DEPENDENCY_LICENSE_MATRIX.md), [RIGHTS_AND_REDISTRIBUTION_AUDIT.md](docs/research/RIGHTS_AND_REDISTRIBUTION_AUDIT.md). Установленные режимы до решения владельца:

- E1 (oxDNA DSDNA8 fixtures): GPL-3.0 — `DOWNLOAD_ON_SETUP`, вендоринг не рекомендуется до выбора лицензии NanoLab.
- E2 (DNA-hinge-simulations): LICENSE в pinned tree отсутствует — права `UNKNOWN`; режим `REFERENCE_ONLY` + user-side download by exact commit; никакое копирование/mirror/release до разрешения авторов или решения владельца.
- S08 (ACS article/SI/movies): `RESTRICTED` — только ссылка и цитирование.
- NANOBASE: права конкретной записи ≠ условия сайта; per-record `REFERENCE_ONLY`.
- Собственная лицензия после D2: код `Apache-2.0`; документация и NanoLab-owned derived data/results `CC-BY-4.0`.

`UNKNOWN` не является разрешением; отсутствие явного запрета не является разрешением.

## Owner decision D2 (2026-09-18)

Каноническая запись: `docs/control/NL5_001_D_LICENSE_DECISION_R1.md`. Решение снимает publication blocker только для материалов, принадлежащих NanoLab. `REFERENCE_ONLY`, GPL, restricted и UNKNOWN поверхности продолжают регулироваться собственными upstream-правами и соответствующими rights records.
