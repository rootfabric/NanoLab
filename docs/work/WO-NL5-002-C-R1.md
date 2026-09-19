# WO-NL5-002-C-R1 — Compare external result, root cause, repair package v0.1.1

## Паспорт

- Work Order: `WO-NL5-002-C-R1` (`NL5-002-C`, parent `NL5-002`; план `docs/control/NL5_NL8_EXECUTION_PLAN_R1.md` §2.3, §11 п.4)
- Base: `main @ 48c55b3c4acdd2264527083e3072757be8bd9ada`
- Branch: `work/nl5-002-c-compare-repair-r1`
- Risk: MEDIUM; claim ceiling `C1_COMPUTATIONAL_REPRODUCTION` (repair не поднимает научных claims)
- Вход: принятый внешний отчёт B-R1 (`docs/work/executions/EX-NL5-002-B-R1/evidence/EXTERNAL_REPRODUCTION_REPORT.md`, sha256 `5b6d1f06…`, вердикт исполнителя INCONCLUSIVE)

## Сравнение (frozen rule, mechanical)

Per-card контрактная классификация внешней кампании B-R1 (по
`NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`, отчёт §9): `0b/11b/32b/53b = INCONCLUSIVE`;
`74b = N/A NOT_MEASURED`. WO-level внешний вердикт по frozen mapping
(WO-NL5-002-A-R1 §Frozen classification): **INCONCLUSIVE + PORTABILITY_FINDING**.
Это не FAILED_TECHNICAL кампании и не MISMATCH: научные tolerance/envelope
не скомпрометированы; техническая цепочка (verify, пины, digest gates, seeds,
детерминизм) воспроизведена полностью.

## Root cause (portability findings, подтверждают risks R1–R2 протокола)

- **F1 (blocking)**: frozen observable convention не публикуется пакетом —
  arm-manifest'ы, конвенция осей (erratum R1 §2.5), detector v2 constants,
  определения frame-validity gates (E2_PROTO_R1 §4) отсутствуют; 12 семейств
  реконструкции исполнителя не сошлись с оракулами пакета.
- **F2**: URL репозитория движка не указан (исполнитель нашёл сам).
- **F3**: нет корневого README пакета.
- **F4**: расхождение `print_energy_every` (карточка-пин 100 против upstream 4e3)
  не объяснено в шагах карточки.
- **F5**: tarball-получение точного коммита не описано (git-транспорт ломается
  на ограниченных сетях; у автора та же практика, ENGINE_ENVIRONMENT_R1).
- Средовое усечение 12 реплик (9.5 h, ~64–92% пути) — orchestration issue
  исполнителя, не дефект пакета; учтено в протоколе повтора B-R2.

## Repair (bounded, без изменения научного содержания)

Новая ревизия пакета **`releases/nanolab-components-v0.1.1/`** (v0.1.0 не
переписывается — контракт R1.2: «старый release не переписывается задним
числом»). Дельта v0.1.0 → v0.1.1:

1. `convention/` (NEW):
   - `arm-manifest-{0b,11b,32b,53b}.json` — точные копии frozen манифестов
     из `docs/work/executions/EX-NL3-002-PROTO-R1` / `EX-NL3-002-PARAM-*-R1`;
   - `nlbl_convention/` — stdlib-only референс-реализация frozen конвенции
     (observables, topology/conf parser, reproduction rule) из `scripts/`
     с относительными импортами;
   - `analyze_hinge.py` — CLI: `frame0` (оракул `design.angle_frame0_deg`),
     `run` (gates + per-replica median), `campaign` (median-of-3 +
     классификация по envelope карточки);
   - `OBSERVABLE_CONVENTION_V0_1.md` — самодостаточная спецификация конвенции.
2. Карточки MEASURED (0b/11b/32b/53b): `reproduction.steps` ссылаются на
   in-package `convention/`; `requires` дополнен URL движка и tarball-путём;
   пояснение overlay `print_energy_every=100`. **`expected`/envelopes/пороги —
   byte-identical v0.1.0.**
3. `reproduction/README.md`: шаг конвенции; корневой `README.md` (NEW);
   `VERSION` → 0.1.1; `CITATION.cff` → 0.1.1.
4. `RELEASE_MANIFEST.json` перегенерирован штатным тулингом
   (`release.card_lint`), `reproduce.py verify` обязан проходить.

## Validation (до dispatch B-R2)

- `reproduce.py verify` на v0.1.1 → ok, файлы пересчитаны;
- оракул: `analyze_hinge.py frame0` на upstream .conf + .top для всех 4
  вариантов воспроизводит `design.angle_frame0_deg` карточек (числа
  опубликованы, ожидание точного совпадения);
- v2 pair counts на upstream frame 0 согласованы с published
  `reference_pairs_v2_count`;
- schema/lint карточек; научные числа карточек byte-identical v0.1.0
  (кроме полей `reproduction.steps`/`requires`/`protocol_pins.notes`).

## Forbidden

- изменение expected/envelopes/порогов; правка v0.1.0; значения для 74b;
  merge в main (Human Gate).

## Start record

`docs/work/executions/EX-NL5-002-C-R1/` (passport + event 0001) до substantive work.

## Completion

Exact HEAD/TREE, validation records, next action: dispatch B-R2 на v0.1.1.
