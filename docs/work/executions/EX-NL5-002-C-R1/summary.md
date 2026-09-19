# EX-NL5-002-C-R1 — Summary: compare + bounded repair v0.1.1

- Work Order: `WO-NL5-002-C-R1` (parent `NL5-002`)
- Base: `main @ 48c55b3c4acdd2264527083e3072757be8bd9ada`
- Branch: `work/nl5-002-c-compare-repair-r1`
- Status: HANDOFF_READY (B-R2 dispatch следующий)

## Сравнение (механическое, frozen rule)

Вход: внешний отчёт B-R1 (sha256 `5b6d1f06…`, verdict исполнителя
INCONCLUSIVE). Per-card: `0b/11b/32b/53b = INCONCLUSIVE`, `74b = N/A`.
WO-level: **INCONCLUSIVE + PORTABILITY_FINDING** → repair по плану §2.3.

## Root cause (portability findings)

| ID | Находка | Repair в 0.1.1 |
|---|---|---|
| F1 | frozen convention не публикуется (arm manifests, оси/erratum, detector v2, gates) | `convention/`: манифесты + `nlbl_convention/` + `analyze_hinge.py` + спецификация |
| F2 | URL движка не указан | `requires` карточек: github URL + codeload tarball путь |
| F3 | нет корневого README | `README.md` с быстрым стартом и историей |
| F4 | overlay `print_energy_every=100` не объяснён | `protocol_pins.notes` карточек |
| F5 | tarball-получение коммита не описано | `requires` карточек + reproduction README |
| F6 | неоднозначность окна 0b (200k basis) vs common 150k | в карточке/конвенции задокументировано `--window` + basis; числа не менялись |

Средовое усечение 12 реплик B-R1 — orchestration issue, учтено в протоколе
B-R2 (robust detached execution + обязательные exit-code записи).

## Repair-ревизия v0.1.1 (v0.1.0 не тронут — контракт R1.2)

42 файла (было 20). Научные значения карточек
(expected/integrity/design) — **программно верифицированная бит-в-бит
идентичность v0.1.0**.

## Валидации (PASS)

- `reproduce.py verify` → ok, 42/42; `plan` → ok; `card_lint package` → ok;
- **frame-0 oracle EXACT MATCH ×4**: 66.886745865 / 74.357957026 /
  77.477102136 / 132.949606811;
- полный конвейер: `analyze_hinge.py run` на эталонной траектории
  NL5-001-C-0B-S001 → медиана 66.159296437, кадры 50/37/37 (== записанному);
  `campaign` → MATCH по карточному envelope.

## Exact HEAD/TREE

См. evidence-map.json (deliverables commit фиксируется аналогично фазе A).

## Next action (один)

Staging `/home/rdpuser/nl5-002-external-r2` (package v0.1.1 + EXECUTOR_PROTOCOL_R2)
→ fresh external executor B-R2 → отчёт → фаза D.
