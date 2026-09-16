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
