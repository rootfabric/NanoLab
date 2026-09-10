# NL2-002 — Implementer Evidence Map

Исполнение: `EX-NL2-002-R1`. Дата: 2026-09-10. Роль: IMPLEMENTER + SCIENTIFIC_OPERATOR (одна orchestrating-сессия; независимость review/verify — fresh-сессии).

## Intent и классы

- Work Order: `NL2-002` — validate statistics and E1: T2 confirmatory кампания + confirmatory-статистика + evidence-пакет ([WO-NL2-002](../../work/WO-NL2-002.md)).
- Risk: `HIGH`. Публикуемые классы: execution facts + preregistered band-facts; campaign ceiling `C1_COMPUTATIONAL_REPRODUCTION`; campaign-level scientific_outcome = **NOT_EVALUATED** (объявление статуса E1/acceptance — Director после независимых REVIEWER + VERIFIER).

## Exact subject

- Base SHA: `0176098ed052ec29503ac5c353463be0cc8ea167` (canonical main: NL2-001 ACCEPTED, next NL2-002 READY, `E1 = RUN`, `physics_runs = 4`, merge PR #30); epoch drift отсутствовал.
- Branch: `work/nl2-002-validate-e1-r1`; START `878e1ab`; **subject кампании E1-R2: `f34e62ca67f12f0cffbd1823d584afc09900db6a`** (freeze-коммит: campaign.md + protocol.json + analyze_energy.sh байт-в-бит из E1-R1, git blob `77cfcc637df7c75446736cf1c3a71ea219a260c5`); campaign-START `42cb851` (manifests + started-events, push до первого прогона).
- Engine: oxDNA `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`, **reuse бит-в-бит зафиксированной сборки E1-R1** — бинарь `ffc80b1a7abe2a06bea601ac7f730e26c0e5c09c33a9e8c7c5f7a96a4848579f` (3375976 B), флаги Release/DOUBLE=ON/CUDA=OFF/MPI=OFF/NATIVE_COMPILATION=ON/JSON_ENABLED=ON верифицированы (CMakeCache) перед кампанией; пересборка не потребовалась (разрешено протоколом: reuse идентичной сборки строго сильнее критерия пересборки §3; устраняет конфаунд пересборки между точками set).

## Прогоны (все COMPLETED с первого и единственного запуска; без исключений, повторов, скрытых retries)

| Run | Тип | Seed | Wall, s | RSS, KB | avg col2 | Δ от оракула | Band | Evidence |
|---|---|---:|---:|---:|---:|---:|---|---|
| E1-R1-S001 (reuse) | T1 production | −200619630 | 13.13* | 6304* | −1.39393635864 | −0.014234 | IN_BAND | да (published E1-R1; *факты NL1-002) |
| E1-R2-C001 | T2 confirm 1/3 | −1641386734 | 11.00 | 6604 | −1.36722173127 | +0.012481 | IN_BAND | да |
| E1-R2-C002 | T2 confirm 2/3 | 977680137 | 10.88 | 6604 | −1.35818087512 | +0.021522 | IN_BAND | да |
| E1-R2-C003 | T2 confirm 3/3 | −999572227 | 11.03 | 6468 | −1.35653082817 | +0.023172 | IN_BAND | да |

- Distinct seed: C001–C003 попарно и относительно S001/P001–P003 — факт из `log.dat` каждого прогона (upstream-семантика случайного seed; `#seed = 4982` остался закомментированным).
- Входы: только сырые blob'ы pinned tree (`git cat-file blob`), sha256sum на месте **4/4 MATCH перед каждым прогоном** (ENGINE_ENVIRONMENT_R1 §5); модификаций: NONE.
- Бюджет: 32.91 s wall суммарно по трём прогонам ≈ 0.009 core-hour (≪ cap 1 core-hour кампании E1). Total runs = 3; failed/excluded = 0.

## Статистика (frozen правила E1-PROTO-R2; полный разбор — [statistics.md](../../experiments/evidence/E1/E1-R2/statistics.md))

- **Confirmatory set = S001 + C001–C003 (n = 4, все значения опубликованы полностью): mean = −1.36896744830; выборочное SD (n−1) = 0.01729656703** (11.5% полосы; пилот SD 0.00832919790 — 5.6%; малое n, без претензии на точный CI §6.3).
- **Per-replica критерий §5.1: 4/4 IN_BAND** (|Δ| = 0.0142 / 0.0125 / 0.0215 / 0.0232 ≤ 0.15).
- **Агрегат §9 R1 (механический факт): T1 PASS и все T2-реплики в полосе → критерий ВЫПОЛНЕН.**
- Целостность §5.2: каждая реплика 1001 строка (1 initial + 1000 prints, protocol note), 10 конфигураций, NaN/Inf = 0, N=16/molecules=2, engine facts (v3.7 / GIT COMMIT 00dc7fb / T 0.097717).
- Разделение неопределённостей §6.3: статистическая ошибка = между-репликационный SD 0.0173; физическая флуктуация (диагностика §4 R2, best-effort, НЕ gate) = ac(1) 0.59–0.83, τ_int ≈ 10–60 prints, Neff ≈ 8–48 из 1001 строки (кадры НЕ независимые наблюдения); модельные ограничения = §2.4 R1, вне scope.
- Provenance reuse S001: published `energy.dat` E1-R1 (SHA-256 `ff26bad5…`, producer `E1-R1-S001`, subject `9cc83e85…`); перезапуск не выполнялся; cross-check байт-в-бит инструментом воспроизводит published значение. Pilot в set не засчитан (§6.4).

## Команды / доказательства

- Каждый прогон: `git cat-file blob` 4 fixture'ов → `sha256sum` 4/4 MATCH → `cd <scratch>/E1-R2-C00N && /usr/bin/time -v ~/nl1-002/build-oxdna-cpu/bin/oxDNA quick_input` → exit 0 → raw-выходы в Git с artifacts.manifest.json контрактной формы-массива.
- Контрактная обвязка (уроки NL1-002 R2 + NL2-001): манифесты-массивы (name/sha256/size_bytes/producer_run_id/subject_sha 40-hex/storage_location/producer_command); события с `experiment_id`, полным 40-hex `subject_sha`, `event_id` = имя файла, терминальный `RUN_COMPLETED` перед `ANALYSIS_COMPLETED`; машинные timestamps; `resource_time.txt` (raw `/usr/bin/time -v`) — 5-й артефакт каждого прогона.
- Дайджест-контроль: 15/15 published артефактов MATCH; 15/15 committed blob'ов MATCH (binary-safe `git cat-file`).
- Анализ: `analyze_energy.sh` (байт-в-бит из E1-R1, одинаковый для всех точек) на published `energy.dat`.

## Технический outcome vs научный conclusion (раздельно)

- Технический: 3/3 `RUN_COMPLETED` (exit 0, «END OF THE SIMULATION, everything went OK!»), целостность OK — опубликовано терминальными событиями.
- Научный (механический факт): критерий §9 на confirmatory set ВЫПОЛНЕН (4/4 IN_BAND); **campaign-level scientific_outcome = NOT_EVALUATED** — объявление статуса E1/acceptance не входит в полномочия implementer.

## Recommendation для Director

**SUPPORTED** — preregistered критерий E1-PROTO-R1 §9 на confirmatory set (S001 + C001–C003) выполнен: T1 PASS, 3/3 T2-реплик IN_BAND, целостность OK, distinct seed подтверждены, бюджет соблюдён, исключений и повторов нет. Условие: приёмка только по процедуре (независимые REVIEWER + VERIFIER → Director checkpoint; merge Human Gate). Claim ceiling `C1_COMPUTATIONAL_REPRODUCTION` не превышать: воспроизведён upstream oracle на зафиксированной среде; физическая валидность oxDNA, сборка, кинетика — вне scope (S02).

## Приёмка (самопроверка implementer'а, не acceptance)

- [x] Пререгистрация: полоса/оракул/статистика/`R_confirm = 3` frozen до данных; ничего не менялось после просмотра результатов.
- [x] Уникальные run ID; технический и научный исходы раздельно; failed/inconclusive отсутствуют (и не скрывались бы).
- [x] Frozen subject (freeze + campaign-START) запушен до первого прогона; машинные timestamps; контрактный формат всех поверхностей.
- [x] `project/state.json`, `project/plan.json`, `config/**`, `scripts/harness/**`, протоколы E1, артефакты E1-R1 — не менялись.
- [x] Campaign-level NOT_EVALUATED; ACCEPTED не выставляется; recommendation — Director'у.

## Оставшиеся риски

См. `evidence-map.json` remaining_risks: одна машина/сборка (независимость повторов = distinct seed, не разные машины); SD на n=4 грубая; PyMBAR-level ESS/корреляции открыты (§4 R2); NATIVE-привязка бинаря; SD confirmatory set вдвое выше пилотного — согласуется с малой выборкой, отмечено.

## Next action (один)

Независимый REVIEWER: fresh-сессия проверить evidence-пакет NL2-002 на exact HEAD (см. `docs/work/executions/EX-NL2-002-R1/summary.md`) → `docs/evidence/NL2-002/REVIEWER_VERDICT.md`; затем VERIFIER и Director checkpoint (объявление статуса E1); merge — Human Gate.
