# Campaign E1-R1 — Первый вертикальный воспроизводимый путь E1 (без ИИ)

Experiment: `E1` ([паспорт](../../../docs/experiments/E1_REFERENCE_REPRODUCTION.md)). Протокол: `E1-PROTO-R1` ([PREREGISTRATION_E1_R1](../../../docs/research/PREREGISTRATION_E1_R1.md)), machine binding: [protocol.json](protocol.json). Work Order: `NL1-002` ([WO-NL1-002](../../../docs/work/WO-NL1-002.md)). Исполнение: `EX-NL1-002-R1`.

## Вопрос кампании

Воспроизводится ли upstream-наблюдение DSDNA8/MD (среднее колонки 2 `energy.dat` в полосе −1.37970256144 ± 0.15 из pinned `quick_compare`) на зафиксированной среде NanoLab?

## Состав (frozen до первого запуска)

```text
E1-R1-S001  T1 production   verbatim quick_input (1e6 steps), evidence = да
E1-R1-P001  PILOT           та же конфигурация, случайный seed, evidence = нет
E1-R1-P002  PILOT           та же конфигурация, случайный seed, evidence = нет
E1-R1-P003  PILOT           та же конфигурация, случайный seed, evidence = нет
T2 confirm  ВНЕ NL1-002     R_confirm фиксируется E1-PROTO-R2; кампания NL2-002
```

## Среда

`ENGINE_ENVIRONMENT_R1` (NL1-001, ACCEPTED): WSL2 Ubuntu 24.04.2, gcc 13.3.0, cmake 3.31.6 user-local, oxDNA `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` CPU Release DOUBLE. Для кампании engine пересобран по §3: SHA-256 бинаря `ffc80b1a7abe2a06bea601ac7f730e26c0e5c09c33a9e8c7c5f7a96a4848579f` (3375976 B; хэш не бит-в-бит воспроизводим из-за встроенной даты сборки — см. protocol.json).

## Пререгистрация и границы

Все observables/критерии зафиксированы ДО прогонов (`E1-PROTO-R1` PREREGISTERED). Полоса и оракул — из upstream `quick_compare` (SHA-256 в protocol.json), не подбираются. Pilot в evidence не засчитывается (§6.4). Campaign-level scientific_outcome — `NOT_EVALUATED` до T2-кампании NL2-002 (§9: SUPPORTED требует T1 PASS + все T2 в полосе). T1 band-факт публикуется как execution fact.

## Известные ограничения

- Seed случайный при каждом прогоне (upstream-семантика закомментированного `#seed`); между-прогонный разброс встроен в смысл полосы ±0.15.
- NATIVE_COMPILATION=ON: бинарь привязан к CPU этой машины; перенос требует пересборки и записи новых SHA-256.
- Effective defaults (interaction_type=dna average; john=Brownian pt=0.019929118/pr=0.006687465; T=0.097717; salt N/A) — часть frozen subject; `ENGINE_ENVIRONMENT_R1` §6.
- §5.2 protocol note: ожидание строк `energy.dat` — 1001 (1 initial + 1000 prints), см. protocol.json integrity.
