# EX-PREP-S17-R2 — Implementation handoff

## Identity / scope

- Base: `main @ 513c4fa86470d939e9f9b7829e9c67c489c15a57` (tree `6d3a2132ae6ecdfed6269fe39697e8ac9bab152a`).
- Working branch: `work/prep-s17-r2-r1` (isolated worktree `/home/rdpuser/NanoLab/prep-s17-r2`).
- Result: **SOURCE RECOVERY + INDEX/TOPOLOGY MAPPING IMPLEMENTED / REVIEW REQUIRED**; risk MEDIUM,
  claim ceiling — **`PINNED_IMPORT_VERIFIED`** (унаследован и усилен R2-фактами байт-идентичности;
  НЕ симуляция, НЕ MODEL_REPRODUCED, НЕ ASSEMBLY_VALIDATED).
- New scientific runs: **0**; E5: **not started**; NL5/NL6 статусы: **не изменялись**;
  `project/state.json` / `project/plan.json`: **unchanged**; frozen artifacts: **untouched**;
  raw-файлы в Git: **не вендорены** (только digests/manifests/цитаты ≤100 B).

## Что сделано (стадии A–E)

### A. Source recovery (полностью закрыта)

Bounded multi-range восстановление из хвостов четырёх архивов Zenodo 8248808 (CC-BY-4.0),
без скачивания архивов целиком: **99 членов получено, все CRC-32 ok**
(ne23 53/53, ne37 9/9, pr23 25/25, pr37 12/12). Передача ≈ **28.4 MiB** уникальной нагрузки
(хвосты 18.0 MiB + span-байты 10.4 MiB) из бюджета ≤256 MiB; повторные попытки ограничены
(сеть: TLS-разрывы rc=35, троттлинг retry-after 52–60 c, «зависание» после body — всё
обработано и задокументировано).

**Все 9 content-пинов R1 (кроме документов) выведены заново байт-в-байт из Zenodo:**
NE.top, nNE.top, NE_NB.top, NE.dat, nNE.dat, NE_NB.dat, input_equilibrium,
input_pull, T7_force.txt → `evidence/s17-r2-pin-identity.json`.

Ключевые закрытия R1 missing-inputs:

- `polymerase_positioning.txt` — **RESOLVED**: есть во всех pull/release-прогонах; три
  варианта по семействам: nNE(8694,7374) = Nanobase T7_force.txt **байт-идентичен**;
  NE/NE_NS(8514,14288); soft(14102,13840) — полные цитаты в
  `evidence/s17-r2-force-file-variants.json`.
- `linked.top` рецепт — **RESOLVED_NEGATIVE**: linked.top ≡ nNE.top байт-в-байт во всех
  четырёх архивах (никакой «сборки» не существует в публичном датасете).
- 23 °C-инпуты: hinge23/nNE1/input ≡ pin input_equilibrium минус одна строка `T = 37C→23C`;
  input_relax добавлен (dt=0.0003, старт от last_conf_trap.dat).
- Точный пин oxDNA — остаётся **UNKNOWN** (источник не публикует).

### B. Index mapping (полностью закрыта)

`S17_R2_PORT_MAP.json` + `evidence/s17-r2-structures-analysis.json`:

- get_k arm refs [2034,6657], [4593,4411] и старые [2609,6336] — circular-скаффолд
  (strand 1, 7,249 nt) в NE и nNE.
- ss_ids.txt: **322** индекса (уточнение R1-оценки 319), 7 окон (6×53 + 4), только скаффолд.
- 12 из 20 проанализированных arm-файлов выходят за 14,011 частиц NE_NB → жёсткое bounds-исключение;
  per-file namespace-атрибуция сверх этого — INFERRED_CANDIDATE максимум.
- Trap-пары разрешены в своих namespace: у всех семейств `particle` — 5'-конец короткого
  выступающего стейпла, `ref_particle` — середина длинной цепи.
- r0 = 8.8 oxDNA-единиц = **7.496 нм ≈ 7.5 нм** — радиус T7RNAP из статьи.
- Bridge-ODN порты — **UNKNOWN** (placeholder-последовательности во всех pinned-топологиях).

### C. Driver–follower topology (fail-closed)

**NOT_RECONSTRUCTED**: в полных CD-перечислениях всех четырёх архивов
(276+207+949+894 записей) нет ни одного driver/follower каталога/файла. Receipt:
`evidence/s17-r2-df-not-reconstructed.json`. Static preflight трёх дизайнов Nanobase —
PASS (NE 14,343/161; nNE 14,343/163; NE_NB 14,011/163).

### D/E. Tools + tests

- `scripts/knowledge_pack/s17_zip_probe.py` — EOCD/ZIP64/CD-парсер + CRC-верификация.
- `scripts/knowledge_pack/s17_index_map.py` — verified index maps (строгие парсеры
  `hinge_family` переиспользованы импортом, без модификации).
- `scripts/knowledge_pack/s17_assembly.py` — static preflight + fail-closed receipts.
- `scripts/knowledge_pack/s17_recovery.py` — spec→verdict evidence-генератор.
- `scripts/knowledge_pack/s17_range_fetch.py` — bounded multi-range fetcher
  (ZIP64 extra **сканируется** в списке extra-полей — реальный кейс Zenodo; multipart
  парсер с length-валидацией; CRC fail-closed).
- `tests/test_s17_r2_*.py` — **67 offline-тестов** с негативными контролами (**эратум R2.1:** было 66)
  (CRC-повреждение, усечённые окна, нерезолвимый ZIP64, короткие части, oversize).

## Validation (exact HEAD/TREE см. evidence-map.json)

- `python3 -m unittest discover -s tests -t .` → **746 tests OK** (base 679 + 67 новых; **эратум R2.1:** ранее записано 745/66 до финального прогона).
- `PYTHONPATH=scripts python3 -m harness.cli check-consistency` → ok:true (stages 9, tasks 19, experiments 7).
- `PYTHONPATH=scripts python3 -m harness.workflow_lint` → blocking:0.
- `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-PREP-S17-R2` → ok:true.

## Границы (не изменены)

- Claim ceiling: `PINNED_IMPORT_VERIFIED` + статусы SOURCE_CONFIRMED / INFERRED_CANDIDATE /
  UNKNOWN по каждому факту; никаких MODEL_REPRODUCED / ASSEMBLY_VALIDATED / S17_ASSEMBLY_READY.
- 0 scientific runs; никакого E5; canonical статусы NL5/NL6 не тронуты.
- Zenodo трафик только по явному opt-in Range-фетчу в рамках бюджета (паспорт).
- sulcgroup/hinges — REFERENCE_ONLY (алгоритмы описаны, код не вендорен).
- Merge в main = Human Gate (draft PR).

## Ограничения / честные оговорки

- Извлечено 99 членов из 2,326 суммарных CD-записей (**эратум R2.1:** было 2,324; канон — df-receipt full enumeration) (целевой набор по WO); остальной
  контент архивов не скачивался и не анализировался.
- Per-file namespace-атрибуция arm-файлов по выравниванию цепей статистически неубедительна;
  зафиксированы только bounds-факты и наблюдения.
- Учёт передачи — по уникальным байтам успешных диапазонов; retry-overhead ограничен
  механикой повторов (не логировался поэлементно).
- Корневые polymerase_positioning.txt различаются между pr23 (96 B, nNE) и pr37 (97 B, NE).
- Repeat-детерминизм реплик (1–3) — наблюдение на статических входах, не гарантия.

## Next action (single)

Fresh independent Reviewer + exact-head Verifier ветки `work/prep-s17-r2-r1`; затем Human Gate.

## Errata R2.1 (post-review corrections, append-only)

Independent fresh Reviewer (отдельная сессия, scratch-клон `/tmp/review-r2`): **PASS**,
blocking findings отсутствуют, 6 non-blocking находок (N1–N6). Применённые коррекции:

- **N1**: счётчик гейта 745 → **746 = 679 + 67** (событие 0004 признавало «pending final run»;
  финальный прогон на исправленном дереве: 746 OK — см. событие 0005).
- **N2**: негативные контроли капы теперь реально доходят до капы:
  `s17_range_fetch.extract_members` — zip-bomb guard перенесён ВЫШЕ парсинга
  local-header и inflate (закрыто окно decompress-before-cap, часть N6), оба теста
  (`test_extract_oversize_member_rejected`, `test_local_entry_rejects_oversized_uncompressed`)
  требуют «safety cap» в сообщении — пройти по чужой причине больше нельзя.
- **N3**: «2,324» → **2,326** (276+207+949+894; канон — full enumeration df-receipt).
- **N4**: «66 offline-тестов» → **67** (recovery doc §1/§7, summary).
- Отложено (non-blocking, отдельный scoped follow-up): N5 (passport status
  «STARTED» при HANDOFF_COMPLETED — sibling-конвенция), N6 (EOCD count cross-check в
  range_fetch `parse_central_directory`; docstring `iter_member_blobs`; CRLF-хрупкость
  multipart-парсера; учёт retry-трафика в `--fetch`; чистка scratch `.range_*.bin`).
