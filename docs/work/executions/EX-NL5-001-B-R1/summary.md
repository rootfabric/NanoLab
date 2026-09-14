# EX-NL5-001-B-R1 — Summary / Handoff

## Result

`IMPLEMENTED / REVIEW_REQUIRED` (MEDIUM risk; физика не запускалась, canonical не менялся).

Substantive subject: `be73c5408bee54bc66105f0dee3e3262905eb2ad` on
`work/nl5-001-b-library-assembly-r1`, based exactly on
`work/nl5-001-a-release-contract-r1 @ 9cbde33b854eeeb00abde84346c17fe3080bbe50` (stacked: PR #37 → A → B).

## Что сделано

**Библиотека v0.1 собрана**: `releases/nanolab-components-v0.1/` — одно семейство
`dna_hinge`, варианты `0b / 11b / 32b / 53b / 74b`, всё сгенерировано детерминированным
builder'ом `scripts/release/build_library.py` из опубликованного evidence
(ни одного числа не вписано вручную; режим `--check` доказывает байт-в-байт
воспроизводимость).

| Вариант | Статус | Медиана, deg | CI95 | n |
|---|---|---|---|---|
| 0b | MEASURED | 65.976921401 | [65.674963662, 66.318271836] | 150 |
| 11b | MEASURED | 73.928725839 | [73.709568565, 74.116753782] | 111 |
| 32b | MEASURED | 78.091845516 | [77.794798276, 78.665129150] | 111 |
| 53b | MEASURED | 132.357787730 | [131.776207377, 132.988423322] | 111 |
| 74b | NOT_MEASURED | — | — | 0 |

0b — confirmatory 200k (frozen E2_PROTO_R1) + окно 150k; 11b/32b/53b — параметрическая
серия, общее окно 150k (в каждой карточке указано). 74b — честный
`KNOWN_GAP / NOT_MEASURED` (FAILED_TWO_DOMINANT_BLOCKS, 2 attempts, runs NOT_RUN,
`blocking_release=false`) — release не задержан, ремонт остаётся будущим bounded
arm-manifest-v2 WO.

**Contract amendment R1.1** (обнаружено при сборке): digest-объект — обязательны
`size_bytes` + `blob_sha1` (registry-пин); `sha256` опционален и допускается только с
`sha256_status` (0b/pro_CPU.in — CONTENT_VERIFIED; 11b/32b/53b/74b — COMPUTED_NOT_VERIFIED,
«no registry claim» по G1-словарю). Линтер S5; пример-пакет A обновлён; запись в
Revision history контракта.

## Валидации

```text
python3 -m unittest discover -s tests -t .   -> Ran 351 tests, OK
release.build_library check                  -> ok, byte-identical, problems: []
card_lint package releases/...v0.1           -> ok (1 ожидаемый D2-warning UNDECIDED)
CONTROL_DEVELOPMENT.sh --check-consistency   -> ok (frontier NL5, next NL5-001)
CONTROL_WORK.sh validate/close EX-...-R1     -> ok
```

## Open risks / границы

- merge-порядок: PR #37 → A → B (stacked); каждый merge — Human Gate;
- публикация пакета заблокирована: D2 (лицензия, UNDECIDED) + NL5-001-D;
- `11b` прогон длиннее окна 150k — `steps: null` с пояснением в notes;
- arm-manifest-v2 (74b) — вне scope, отдельный bounded WO.

## Next action

REVIEWER: independent review exact head `be73c54` (вместе с amendment R1.1). После
merge-цепочки — `NL5-001-C`: clean-room воспроизведение из пакета (fresh env →
download-on-run с digest-гейтами → прогоны → сравнение с expected).

---

## Repair R1 (FIX_REQUIRED → repaired candidate)

Fresh Review R1 (`review/nl5-001-b-r1 @ ab55eb5`) вернул **FIX_REQUIRED**
(F-B1..F-B6); reviewer-authored `REPAIR_MAP_R1.md` (`@ 0761e53`) — полномочие и
scope ремонта. Копии обоих сохранены в `docs/evidence/NL5-001-B/` как
исторические evidence. Ремонт выполнен на этой же ветке как continuation
(события 0004-0005; старые события не редактировались). Точные subjects ремонта:

```text
0004 START base : 628526594784ded8bb2067976cefbe53c4ac0e48 (точноReviewed head)
1936aac         : R1 freeze REPRODUCTION_RULE_R1 (F-B3)
05dbb25         : R2 evidence-derived pins + R3 deterministic manifest + R6 manifest hardening (F-B1/F-B2/F-B6)
861d583         : R4 contract R1.2 sync + R5 stale planning refs (F-B4/F-B5)
```

### Что изменено (по findings)

- **F-B3 (HIGH)**: заморожено правило независимого воспроизведения
  [REPRODUCTION_RULE_R1](../../../research/REPRODUCTION_RULE_R1.md): band =
  `[min, max]` пер-репличных медиан карточки (k≥2, без подгоночных параметров),
  статистика кампании — медиана пер-репличных медиан ≥3 валидных реплик;
  вердикты MATCH / MISMATCH / INCONCLUSIVE / TECHNICAL_FAILURE; pooled
  bootstrap CI95 — только информационно, НЕ полоса допуска. Нормативный
  исполнитель `scripts/release/reproduction.py`; clean-room исполнитель —
  `evaluate` в `reproduce.py` пакета (conformance-тест). NL5-001-C до этого
  коммита не начиналась — критерий заморожен до любых новых данных.
- **F-B1**: builder читает все научные/протокольные пины из evidence
  (run-config `c00*/s00*_input.in`, сводки кампаний, run-reports
  `engine_source_commit`, ENGINE doc, source_pins) с fail-closed
  cross-check-гейтами (включая shared-config гейт `pro_CPU.in`); «ни одного
  ручного числа» теперь фактически истинно; код-own — только явно
  классифицированные release-метаданные.
- **F-B2**: манифест генерируется builder-ом детерминированно
  (`generated_at_utc` — замороженный штамп релиза, не wall-clock;
  `manifest create` требует явный штамп) и входит в byte-for-byte `--check`.
- **F-B4**: нормативный текст контракта синхронизирован с R1.1/S5
  (обязательны `size_bytes`+`blob_sha1`; `sha256` опционален c
  `sha256_status`; таблица правил S1–S5); revision history → R1.2.
- **F-B5**: битая ссылка `POST_MVP_EXECUTION_PROGRAM_R1.md` заменена на
  durable `POST_MVP_DEVELOPMENT_ROUTE_R1` (контракт, WO-A, WO-B, паспорта A/B
  — с corrections-записью оригинала; исторические events не редактировались).
- **F-B6**: `manifest verify` отвергает duplicate paths и плохую path-семантику
  fail-closed ДО словарной свёртки; negative-тесты (идентичные/конфликтующие
  дубликаты, `/…`, `\…`, `..`).

### Supersession

A @ `9cbde33` (FIX_REQUIRED по F-A2) — **SUPERSEDED** интегрированным
отремонтированным кандидатом B (стратегия Repair Map «integrated B repair»);
B содержит A + amendment R1.1 + repair R1. Отдельный ре-accept старого A не
проводится, если harness явно не потребует.

### Валидации repair R1

```text
python3 -m unittest discover -s tests -t .   -> Ran 385 tests, OK (было 351; +34 repair-теста)
release.build_library check                  -> ok, byte-identical ВЕСЬ пакет, manifest включён
card_lint package releases/...v0.1           -> ok (1 ожидаемый D2-warning)
card_lint package examples/...v0.1           -> ok (1 ожидаемый D2-warning)
CONTROL_DEVELOPMENT.sh --check-consistency   -> ok (frontier NL5, next NL5-001)
CONTROL_WORK.sh validate EX-...-R1           -> ok (события 0004-0005 как corrections-tail)
```

### Next action

FRESH REVIEWER: re-review нового exact head `work/nl5-001-b-library-assembly-r1`
(см. событие 0005) против Repair Map. Только после PASS — отдельный exact-head
VERIFIER, Human merge; затем NL5-001-C clean-room по замороженному
REPRODUCTION_RULE_R1. Роли Reviewer/Verifier реализатором не исполнялись.
