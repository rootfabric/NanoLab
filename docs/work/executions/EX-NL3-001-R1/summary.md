# EX-NL3-001-R1 — Summary (NL3-001: register hinge design family)

**Ветка:** `work/nl3-001-hinge-family-r1` (worktree `C:\NanoLab\nl3-001`)
**Base:** `5fbd6d54341947c890cc5aa5f8031de10a0de1eb` (canonical main, PR #33; NL2-003 ACCEPTED, стадия NL2 закрыта, next NL3-001 READY)
**Final HEAD:** см. терминальное событие 0004 и git log ветки (записывается фактический HEAD; content-HEAD на момент валидации — `80aed84f9a48942829bde4f775760830e565f2c8`)
**Risk / claim:** MEDIUM / C0_SOFTWARE_ONLY; научных прогонов не было; кампания E2 = NOT_RUN; state.json/plan.json не менялись (Director gate).

## Сделано (bounded scope WO-NL3-001)

| Блок | Суть | Контроль |
|---|---|---|
| **Регистрация семейства** | `docs/research/HINGE_FAMILY_R1.md`: источник/права (commit `23fd1ff…`, tree `b2d6ceb…`, REFERENCE_ONLY, rights UNKNOWN), семейство пяти вариантов `0b/11b/32b/53b/74b` с классами REPORTED/OBSERVED/UNKNOWN, parameter space (только опубликованные дискретные значения; один параметр за раз; монотонность не предполагается), таблица UNKNOWN U1–U6 с местами решения | каждая позиция с классом данных и ссылкой; nothing invented |
| **Digest-реестр** | `scripts/hinge_family/source_pins.json` (заморожен): 18 поверхностей семейства; blob SHA-1 с provenance (NL0-001 preregistered / R1 tree-listing), SHA-256 с provenance (R1 content-verified для 5 поверхностей `0b`, NOT_VERIFIED для остальных); preregistered sim-input значения E2-SETUP-R1 §5 | fail-closed контракт реестра (pins.py), unittest |
| **Инструмент воспроизведения** | `scripts/hinge_family/`: digest-гейт (size + SHA-256 + git blob SHA-1) → строгие парсеры (oxDNA `.top`, oxDNA restart-конфигурация, caDNAno-дизайн с расшифрованной семантикой ячейки `[prev_helix, prev_base, next_helix, next_base]`) → структурные проверки → канонический байт-детерминированный JSON-отчёт (без wall-clock данных) | fail-closed: любое отклонение = ошибка |
| **Структурное воспроизведение `0b`** | На user-side полученных реальных pinned-объектах (вне Git): exit 0, 8/8 PASS; отчёт `evidence/hinge-0b-structural-report.json` | детерминизм: два прогона → SHA-256 отчётов совпали (`F8EF3EA4…`) |
| **Тесты** | `tests/test_hinge_family.py`: 22 unittest — детерминизм (2 вызова → байт-идентично, включая CLI), tamper-негативы (изменённый байт / усечённый файл / отсутствующий файл → digest FAIL), структурные негативы (base letter, n3/n5, row count, NaN, колонки, ориентация, particle count, pointer consistency, design↔topology count, T ≠ 300K), контракт реестра, целостность bundled-пинов | 160/160 OK (138 + 22) |

## Ключевые результаты воспроизведения `0b` (все — OBSERVED из отчёта)

- **Digest-гейт**: preregistered blob'ы NL0-001 (`0b.json` = `0ed4075c…`, `pro_CPU.in` = `89d76310…`) сошлись бит-в-бит; tree pinned-коммита = preregistered `b2d6ceb…`; SHA-256 пяти поверхностей заморожены.
- **Точный кросс-чек**: баз в дизайне 4266 (scaffold) + 4112 (staples) = **8378 == 8378 нуклеотидов топологии**; целостность указателей дизайна 0 ошибок; целостность цепей топологии 0 ошибок; NaN/Inf 0; ориентации точные unit+ортогональные (max dev 2.15e-07).
- **Топология**: 112 странд (103 linear + 9 circular: id 2–7, 42–44), макс. длина 644; конфигурация: 8378 частиц × 15 колонок, `t = 2e7` (конец авторского equilibration-прогона).
- **Согласующиеся наблюдения** (не критерии): 456 длинных связей (>0.95) ≈ 459 шагам кроссоверов дизайна; 118 путей дизайна vs 112 страндов топологии — соответствие не декомпозировано (gap G2).
- **Machine-confirm E2-SETUP-R1 §5**: `DNA2 / salt 0.5 / T=300K / 2e7 / CPU / double`; **`pro_CPU.in` по умолчанию указывает `74b.top`/`74b.conf`** — подстановка на `0b` зафиксирована как обязательное документируемое отклонение.

## Что НЕ сделано (честно, гэпы G1–G6 в HINGE_FAMILY_R1 §7)

- Права источника (G1) — владелец; **никакие байты источника не вендорены и не кэшированы**.
- Точное соответствие «путь дизайна → странд топологии» (G2) — нужны авторские `Init_Hinges`/последовательности (REFERENCE_ONLY) — pre-E2 compatibility audit.
- Атрибуция spring layers (REPORTED 0/24) к ssDNA-сериям (G3) — нужен SI; machine-check помечен inconclusive, не подогнан.
- Семантика колонок 9:15 конфигурации (G4) — интерпретация до pre-E2 engine-input check.
- SHA-256 поверхностей `11b/32b/53b/74b` (G5) — scope R1 ограничен первым экземпляром `0b`.
- Прогоны динамики (G6) — NL3-002/E2; пререгистрация угла/целостности — `E2-PROTO-*`.

## Результаты чеков (subject `80aed84` + records)

- JSON: 717 tracked; unparseable ровно 2 — designed-NEG фикстуры (sha256 = CI-пинам).
- `check-consistency`: ok, exit 0 (state/plan не тронуты).
- `work_cli validate`: 15/15 EX OK (14 pre-existing + EX-NL3-001-R1).
- `workflow lint`: 0 violations.
- `unittest discover`: **160 OK** (138 + 22 новых).
- `verify-digests`: E1-R1 / E1-R2 / E0-R4 — ok, 0 mismatch (регрессия).
- Валидатор на реальном `0b`: exit 0, 8/8 PASS; детерминизм байт-в-байт.

## Open risks

- Расшифровка семантики caDNAno-ячейки верифицирована исчерпывающей симметрией на `0b`; для других вариантов дизайна не перепроверялась (при их валидации — та же механика проверок, ожидание согласованности).
- Порог длинной связи 0.95 и допуск ориентаций 1e-06 — конвенции инструмента (задокументированы), не характеристики источника.
- Durable private caching UNKNOWN-rights файлов остаётся открытым owner-решением; R1 не оставлял кэша (скачанные объекты существуют только в scratch вне репозитория и подлежат повторному получению по пинам).

## Next action (одно)

Независимый REVIEWER (fresh-сессия): проверить evidence-пакет EX-NL3-001-R1 на exact HEAD — реестр пинов vs NL0-001 preregistered факты, воспроизводимость 8/8 PASS процедуры из HINGE_FAMILY_R1 §4–§5 (user-side download + digest-гейт), 22 unittest негатив/позитив, гэпы G1–G6 как не закрытые без оснований, отсутствие вендоренных байтов источника → `docs/evidence/NL3-001/REVIEWER_VERDICT.md`; затем VERIFIER; merge — Human Gate.
