# E1-R2-C001 — summary

Тип: T2_CONFIRM_PRODUCTION (реплика 1/3, frozen `R_confirm = 3`). Протокол: E1-PROTO-R1 §3 verbatim `quick_input` + E1-PROTO-R2 (без модификаций). Subject: `f34e62ca67f12f0cffbd1823d584afc09900db6a` (freeze-коммит кампании E1-R2).

## Исполнение

- execution_outcome: COMPLETED (exit 0; «END OF THE SIMULATION, everything went OK!»)
- wall: 11.00 s; max RSS: 6604 KB (`/usr/bin/time -v`, raw: artifacts/resource_time.txt)
- seed (engine random): **−1641386734** (distinct: ≠ S001/P001–P003 и ≠ C002/C003)
- engine: oxDNA v3.7 @ 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591 (лог: GIT COMMIT 00dc7fb), reuse бит-в-бит сборки E1-R1 — бинарь `ffc80b1a7abe2a06bea601ac7f730e26c0e5c09c33a9e8c7c5f7a96a4848579f` (3375976 B), верифицирован SHA-256/size/флаги перед кампанией

## Подготовка (go/no-go)

- Входы: сырые blob'ы pinned tree (`git cat-file blob`), sha256sum на месте 4/4 MATCH пинам E1-PROTO-R1 §2.2 перед запуском
- Модификации входов: NONE (verbatim byte-exact)

## Целостность (§5.2)

- energy.dat: 1001 строка (1 initial + 1000 prints; protocol note)
- trajectory.dat: 10 конфигураций; last_conf.dat записан
- NaN/Inf: 0; T = 0.097717; N = 16, molecules = 2

## Анализ (§5.1, механический; analyze_energy.sh байт-в-бит из E1-R1)

- ColumnAverage(col2) = **−1.36722173127**
- oracle = −1.37970256144, band = ±0.15
- |Δ| = 0.01248083017 → **IN_BAND** (per-replica факт T2)
- scientific_outcome: NOT_EVALUATED (campaign-level агрегат §9 — Director по evidence-пакету после независимого review)

## Артефакты

См. artifacts.manifest.json (SHA-256/size/producer_run_id/subject_sha/storage_location); все файлы в Git.
