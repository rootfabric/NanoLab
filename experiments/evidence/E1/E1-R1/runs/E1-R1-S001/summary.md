# E1-R1-S001 — summary

Тип: T1_PRODUCTION. Протокол: E1-PROTO-R1 (verbatim quick_input, без модификаций).

## Исполнение

- execution_outcome: COMPLETED (exit 0)
- wall: 13.13 s; max RSS: 6304 KB
- seed (engine random): -200619630
- engine: oxDNA v3.7 @ 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591 (лог: GIT COMMIT 00dc7fb), бинарь ffc80b1a7abe2a06bea601ac7f730e26c0e5c09c33a9e8c7c5f7a96a4848579f

## Целостность (§5.2)

- energy.dat: 1001 строка (1 initial + 1000 prints; protocol note)
- trajectory.dat: 10 конфигураций; last_conf.dat записан
- NaN/Inf: 0
- N=16, molecules=2 (совпадает с topology)

## Анализ (§5.1, механический)

- ColumnAverage(col2) = **-1.39393635864**
- oracle = −1.37970256144, band = ±0.15
- |Δ| = 0.01423379720 -> **IN_BAND** (факт, не acceptance)
- scientific_outcome: NOT_EVALUATED (campaign-level решает NL2-002 по полному критерию §9)

## Артефакты

См. artifacts.manifest.json (SHA-256/size/producer); все файлы в Git.
