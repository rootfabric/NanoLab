# Campaign E1-R2 — T2 confirmatory кампания E1 (статистика воспроизведения)

Experiment: `E1` ([паспорт](../../../docs/experiments/E1_REFERENCE_REPRODUCTION.md)). Протоколы: `E1-PROTO-R1` ([PREREGISTRATION_E1_R1](../../../docs/research/PREREGISTRATION_E1_R1.md)) + superseding `E1-PROTO-R2` ([PREREGISTRATION_E1_R2](../../../docs/research/PREREGISTRATION_E1_R2.md), freeze `R_confirm = 3`), machine binding: [protocol.json](protocol.json). Work Order: `NL2-002` ([WO-NL2-002](../../../docs/work/WO-NL2-002.md)). Исполнение: `EX-NL2-002-R1`.

## Вопрос кампании

Держится ли upstream-наблюдение DSDNA8/MD (среднее колонки 2 `energy.dat` в полосе −1.37970256144 ± 0.15 из pinned `quick_compare`) на независимых повторах с различными seed — то есть выполняется ли полный критерий `E1-PROTO-R1` §9 (T1 PASS **и** все T2-реплики в полосе) на confirmatory set из 4 точек?

## Состав (frozen до первого запуска)

```text
E1-R1-S001  T1 production   verbatim quick_input (1e6 steps), seed −200619630, IN_BAND  — reuse из E1-R1 (не перезапускается; дайджест energy.dat в protocol.json)
E1-R2-C001  T2 confirm      та же конфигурация, случайный seed, evidence = да
E1-R2-C002  T2 confirm      та же конфигурация, случайный seed, evidence = да
E1-R2-C003  T2 confirm      та же конфигурация, случайный seed, evidence = да
```

- Ровно 3 T2-реплики — frozen `R_confirm = 3` (`E1-PROTO-R2` §2), зафиксирован ДО confirmatory кампании; после старта не уменьшается.
- Distinct seed: фактически записанные значения C001–C003 обязаны быть попарно различны и отличаться от S001/P001–P003; коллизия → техническая классификация прогона, повтор только с новым run ID.
- Pilot-прогоны P001–P003 в confirmatory set не засчитываются (`E1-PROTO-R1` §6.4, `R2` §3).

## Статистика (frozen до данных)

- Confirmatory set = `S001 + C001–C003` (4 значения, публикуются полностью).
- Оценки: mean и выборочное SD (n−1) — та же оценка, что в пилоте (`E1-PROTO-R2` §1); малое n — без претензии на точный CI (§6.3 R1).
- Per-replica: `|ColumnAvg − (−1.37970256144)| ≤ 0.15` → IN_BAND (§5.1 R1).
- Агрегат (§9 R1, механически): campaign-критерий §9 выполнен ⟺ T1 = PASS **и** все T2-реплики IN_BAND. Иначе — NOT_SUPPORTED-путь с сохранением отрицательного результата; пост-хок исключения прогонов запрещены (§10 R1).
- Статистическая ошибка (между-репликационный разброс), физическая флуктуация (внутри-траектории) и модельные ограничения (§2.4 R1) разделяются и не смешиваются (§6.3 R1).

## Среда

`ENGINE_ENVIRONMENT_R1` (NL1-001, ACCEPTED): WSL2 Ubuntu 24.04.2, gcc 13.3.0, oxDNA `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` CPU Release DOUBLE. Engine — **reuse зафиксированной сборки кампании E1-R1**: бинарь `ffc80b1a7abe2a06bea601ac7f730e26c0e5c09c33a9e8c7c5f7a96a4848579f` (3375976 B) верифицирован SHA-256/размером/флагами (CMakeCache: Release, DOUBLE=ON, CUDA=OFF, MPI=OFF, NATIVE_COMPILATION=ON, JSON_ENABLED=ON) и commit-строкой лога перед прогонами. Reuse бит-в-бит сборки S001 устраняет пересборку как конфаунд между точками confirmatory set; fallback — пересборка по §3 с записью новых SHA-256 (`binary_hash_note` в protocol.json).

## Пререгистрация и границы

Все observables/критерии/статистика унаследованы из пререгистрированных протоколов БЕЗ изменений; ни одна оценка не подбирается по данным (полоса/оракул — upstream `quick_compare`). Campaign-level scientific_outcome публикуется как `NOT_EVALUATED`: механическая оценка критерия §9 на confirmatory set — execution/analysis fact, объявление статуса E1/acceptance — Director после независимого REVIEWER + VERIFIER. Claim ceiling: `C1_COMPUTATIONAL_REPRODUCTION`. Analysis tool: [analyze_energy.sh](analyze_energy.sh) — байт-в-бит из E1-R1 (git blob `77cfcc637df7c75446736cf1c3a71ea219a260c5`, SHA-256 `747c5216589ab9270830a21eaf7f15d1aea742681360ac048f4392c2edfabd4d`).

## Известные ограничения

- Seed случайный при каждом прогоне (upstream-семантика закомментированного `#seed`); между-прогонный разброс встроен в смысл полосы ±0.15.
- NATIVE_COMPILATION=ON: бинарь привязан к CPU этой машины; перенос требует пересборки и записи новых SHA-256.
- 4 точки confirmatory set — одна машина/сборка; между-репликационная независимость обеспечена distinct seed (upstream-семантика), НЕ разными машинами.
- Effective defaults (interaction_type=dna average; john=Brownian pt=0.019929118/pr=0.006687465; T=0.097717; salt N/A) — часть frozen subject; `ENGINE_ENVIRONMENT_R1` §6.
- §5.2 protocol note: ожидание строк `energy.dat` — 1001 (1 initial + 1000 prints).
