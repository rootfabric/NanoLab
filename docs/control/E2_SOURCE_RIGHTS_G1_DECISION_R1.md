# Control Record — E2 source rights: G1 decision R1 + durable-cache policy (U4)

Статус: DECIDED (owner decision, 2026-09-11). Authority: владелец проекта, явное решение через интерактивную сессию DSH harness. Тип: control decision record; published-документы (`E2_SETUP_R1`, `HINGE_FAMILY_R1`, `INPUT_AVAILABILITY`) не редактируются — этот record superseding по смыслу.

## Контекст

С NL0-002 права upstream-источника `gauravarya77/DNA-hinge-simulations` (pinned `23fd1ff7731e9017bd776f49206dc42d70d9fe91`, tree `b2d6cebc7a33ed13e4e9c8d79fe8350ce11e82b9`) были `UNKNOWN` → режим `REFERENCE_ONLY`, а вопрос использования source data для прогонов E2 числился открытым owner-решением (`state.json.open_decisions`; обязательная фиксация при dispatch NL3-002 — Director record NL3-001).

## Decision

**G1 = вариант B: download-on-run, `REFERENCE_ONLY` без вендоринга.**

1. Прогоны E2 разрешено выполнять на source data, получаемых **user-side download по exact pinned commit** непосредственно перед использованием, с обязательной digest-проверкой (blob SHA-1 + SHA-256 против `scripts/hinge_family/source_pins.json`) при каждом получении.
2. **Durable private cache запрещён (U4 = NO):** скачанные файлы источника не хранятся между сессиями вне execution-каталога кампании; каждая execution-сессия скачивает заново и проверяет digest; после завершения execution исходные файлы источника из рабочей области удаляются (в evidence остаются дайджесты/размеры/структурные факты, как в `INPUT_AVAILABILITY.md`).
3. **В Git по-прежнему не попадает ни один байт источника** (`0b.top`, `0b.conf`, `0b.json`, `pro_CPU.in`, файлы `Init_Hinges/`, `MD_Hinges/`, остальные варианты семейства): вендоринг, mirror, генерация-как-оригинал запрещены (без изменений с NL0-002/NL3-001).
4. **Derived results разрешены к публикации** как обычные evidence NanoLab: trajectories/их производные, анализы, отчёты, распределения угла, Component Card — при условии полной provenance (pinned commit, digest входа, engine build, seeds, protocol version). Публикация самих исходных файлов источника остаётся запрещённой.

## Последствия

- `state.json.open_decisions`: пункты «E2 DNA-hinge-simulations explicit license/permission or replacement seed» и «Policy for durable private caching of UNKNOWN-rights files» закрыты этим record и из списка открытых удалены.
- Для dispatch NL3-002 предусловие «зафиксировать G1» выполнено; процедура получения данных не меняется (совпадает с режимом NL3-001).
- Остаются открытыми: лицензия собственного кода/документации NanoLab; пререгистрируемые численные tolerances/целевой интервал угла (`E2-PROTO-R1` после пилота); measured resource budget.
- Вопросы, выходящие за scope E2 (например, future redistribution отчётов, содержащих восстановимые фрагменты источника, или публикация, требующая прав на исходники) — новыми control records по мере возникновения.

## Не меняет

- `REFERENCE_ONLY` как режим обращения с источником в репозитории; `HINGE_FAMILY_R1` жёсткие правила; NL3-001 evidence; prerерегистрационные документы.
