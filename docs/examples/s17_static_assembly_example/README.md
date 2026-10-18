# S17 static assembly example — CANDIDATE_DESIGN

> **СТАТУС: CANDIDATE_DESIGN / HYPOTHESIS.** Это синтетический двух-ODN пример
> для офлайн-тестов CLI сборки. Последовательности НЕ являются реальными
> последовательностями S17 (driver/follower); пример не имеет внешнего
> источника, не делает никакого научного утверждения и никогда не поднимает
> claim выше `ASSEMBLED_STATIC_ONLY` + `GEOMETRY_UNVERIFIED`.

## Что это

Минимальная пара «driver + follower» для детерминированного офлайн-пути
«MechanicalComponentSpec + AssemblySpec → oxDNA topology/config + Evidence
Receipt» (WO-S17-STATIC-ASSEMBLY-HARDENING-R1, issue #66):

- driver: одна синтетическая цепь 12 nt `ACGTGACTGGAG`, 3′-overhang = вся цепь;
- follower: одна синтетическая цепь 12 nt `CTCCAGTCACGT` (точный
  reverse-complement), 5′-overhang = вся цепь;
- одно соединение `c1` (`SS_DNA_OVERHANG_HYBRIDIZATION`, non-covalent:
  гибридизация никогда не создаёт n3/n5-связей);
- follower сдвигается на `[6, 0, 0]` декларированным rigid-body transform;
  geometry-проверки включены (anchor band + coarse clash scan), итог честно
  остаётся `GEOMETRY_UNVERIFIED`.

## Файлы

| Файл | Назначение |
| --- | --- |
| `driver.top` / `driver.dat` | синтетическая oxDNA topology/configuration driver-компоненты |
| `follower.top` / `follower.dat` | синтетическая oxDNA topology/configuration follower-компоненты |
| `driver_component_spec.json` | MechanicalComponentSpec v1 driver-компоненты |
| `follower_component_spec.json` | MechanicalComponentSpec v1 follower-компоненты |
| `assembly_spec.json` | AssemblySpec v1 (mode `CANDIDATE_DESIGN`, design_basis `HYPOTHESIS`) |
| `expected_receipt.json` | эталонный детерминированный Evidence Receipt для этого примера |

## Запуск (из корня репозитория, офлайн)

```bash
PYTHONPATH=scripts python3 -m knowledge_pack.assembly_cli assemble \
  --driver-spec docs/examples/s17_static_assembly_example/driver_component_spec.json \
  --follower-spec docs/examples/s17_static_assembly_example/follower_component_spec.json \
  --assembly-spec docs/examples/s17_static_assembly_example/assembly_spec.json \
  --input-root . \
  --outdir example-output/s17-static

PYTHONPATH=scripts python3 -m knowledge_pack.assembly_cli verify \
  --artifact-dir example-output/s17-static
```

`--outdir` обязан быть относительным путём без `..` внутри рабочего каталога и
не существовать (или быть пустым) — fail-closed границы CLI. Два запуска на
одних входах дают байт-в-байт идентичные артефакты (sorted JSON keys,
фиксированный float-формат, без timestamps в байтах артефактов).

## Честные границы

- Статусы вывода — только `ASSEMBLED_STATIC_ONLY` / `NOT_RECONSTRUCTED` /
  `BLOCKED_*` из `assembly_spec.ASSEMBLY_STATUSES`; геометрия —
  `GEOMETRY_UNVERIFIED`. Никогда `ASSEMBLY_VALIDATED`, никогда
  `MODEL_REPRODUCED`; exit code 0 — программный исход, не научный PASS.
- `receipt.json` примера байт-в-байт равен `expected_receipt.json`;
  тест `tests/test_s17_static_assembly_cli.py` закрепляет и эту дельту, и
  byte-determinism двух прогонов.
- `knowledge_pack_ref.pack_sha256` в трёх spec-файлах пинирует **этот README**;
  любое изменение README инвалидирует пин (fail-closed по дизайну) и требует
  обновления трёх spec-файлов. Правка входных `.top`/`.dat` аналогично
  инвалидирует дайджесты в component specs и `expected_receipt.json`.
