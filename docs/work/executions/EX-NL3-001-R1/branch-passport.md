# Branch Passport — work/nl3-001-hinge-family-r1 (EX-NL3-001-R1)

- **Work Order:** NL3-001 «Register hinge design family» (проверенная параметризация семейства Shi–Castro–Arya, digest-gated процедура воспроизведения/экспорта `0b`, структурное воспроизведение без E2-прогонов)
- **Base:** `5fbd6d54341947c890cc5aa5f8031de10a0de1eb` (canonical main, merge PR #33; NL2-003 ACCEPTED, стадия NL2 закрыта, next NL3-001 READY)
- **Branch:** `work/nl3-001-hinge-family-r1` (worktree `C:\NanoLab\nl3-001`)
- **Risk / claim:** MEDIUM / C0_SOFTWARE_ONLY
- **Started:** 2026-09-10T14:37:34Z (START commit — до substantive work)

## Scope

| Блок | Суть | Где |
|---|---|---|
| Регистрация семейства | family → parameter space → первый экземпляр `0b`; каждая позиция с классом данных (REPORTED/OBSERVED/UNKNOWN) и ссылкой; unknowns не заполняются | `docs/research/HINGE_FAMILY_R1.md` |
| Процедура воспроизведения/экспорта | права источника UNKNOWN → REFERENCE_ONLY: НЕ генерация «с нуля» и НЕ вендоринг, а digest-gated user-side download by exact commit + строгие структурные проверки; заморожено, детерминировано, stdlib-only | `scripts/hinge_family/**` |
| Структурное воспроизведение `0b` | топология/число нуклеотидов/связность/геометрия против характеристик, выводимых из источника; при недоступности источника — честный gap | отчёт в `docs/work/executions/EX-NL3-001-R1/evidence/` |
| Тесты | детерминизм (два вызова → байт-идентичный отчёт), позитив на синтетических фикстурах, негативы (битые параметры/файлы → FAIL, tamper → digest FAIL) | `tests/test_hinge_family.py` |

## Жёсткие ограничения режима REFERENCE_ONLY

- Байты upstream-источника (`0b.top`, `0b.conf`, `0b.json`, `pro_CPU.in`, …) в Git не вендорятся; durable-кэш не создаётся (policy — открытое owner-решение с NL0-002).
- В Git публикуются только дайджесты (blob SHA-1 preregistered из NL0-001, где есть; SHA-256, верифицированные в R1, где получено), размеры и структурные факты (прецедент `INPUT_AVAILABILITY.md`).
- Вычисленный digest ≠ preregistered → BLOCKER, значения не подгоняются.

## Не входит

E2-кампания (прогоны динамики — NL3-002), SI/определение угла и пороги целостности (`E2-PROTO-*`/pre-E2 WO), валидация `11b/32b/53b/74b` (только первый экземпляр `0b`), права/policy кэширования (владелец), compatibility audit `Init_Hinges/` (pre-E2 WO).

## Отклонения от allowed_paths

- Нет (на момент START).
