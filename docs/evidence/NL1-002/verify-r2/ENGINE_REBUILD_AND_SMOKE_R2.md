# Verifier R2 — Пересборка engine и независимый smoke-прогон

Fresh-session VERIFIER R2, ветка `verify/nl1-002-reference-run-r2`. Сетевые/вычислительные действия выполнены независимо, без опоры на R1-вердикты. Scratch верификатора (вне Git): `C:\NanoLab\scratch\nl1-002-verify-r2\` + `~/verify-nl1-002-r2/` (WSL).

## 1. Пересборка oxDNA CPU по ENGINE_ENVIRONMENT_R1 §3

- Acquisition (Windows-сторона, свежий probe-repo): `git init oxDNA` → `fetch --depth 1 origin 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` → `checkout --detach FETCH_HEAD` → `git rev-parse HEAD` = `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` — точное попадание в пин.
- Инструменты: WSL2 Ubuntu 24.04.2, gcc 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1), 20 ядер; cmake 3.31.6 повторно приобретён как `cmake-3.31.6-linux-x86_64.tar.gz`, SHA-256 `5a1133ff103c71eb5120e2cc3de922733e7d8a26a98ae716397e8676adb367bf` — **совпал с пином §2** (первая попытка скачивания дала обрыв по прокси и забракована по SHA-mismatch).
- Команды §3 (WSL, native FS, .git сохранён в src-копии, как в §3 `cp -r oxDNA`): `cmake ../oxdna-src -DCMAKE_BUILD_TYPE=Release -DCUDA=OFF -DMPI=OFF` → **CMAKE_EXIT=0**; `make -j20` → **BUILD_EXIT=0**.
- Бинари (размеры) vs `ENGINE_ENVIRONMENT_R1` §4 и campaign-пином:
  | бинарь | верификатор R2, B | §4 / campaign, B | совпадение |
  |---|---:|---:|---|
  | oxDNA | 3375976 | 3375976 | да |
  | DNAnalysis | 2957400 | 2957400 | да |
  | confGenerator | 2201664 | 2201664 | да |
- SHA-256 бинаря верификатора: `a4810960b415f9b19b0d0e6cd4825b23677374dd1958a05eb46d62136a907d29` ≠ campaign `ffc80b1a…` — ожидаемо: `BUILD_TIME="09/09/26"` встроен в бинарь (flags.make), критерий protocol.json («успешная пересборка §3 + идентичные флаги/размер + commit строка лога») выполнен.
- Флаги (CMakeCache/flags.make): `CMAKE_BUILD_TYPE=Release` (`-O3 -DNDEBUG`), `DOUBLE=ON`, `CUDA=OFF`, `MPI=OFF`, `NATIVE_COMPILATION=ON` (`-march=native`), `JSON_ENABLED=ON`, `CMAKE_CXX_FLAGS` пуст, `-D_FORCE_INLINES`, `RELEASE="v3.7"`, `GIT_COMMIT="00dc7fb"` — 1:1 с §3/protocol.json.

## 2. Независимый smoke-прогон (новый run ID)

- Run ID: **`EX-VERIFY-NL1-002-R2-SMOKE-001`** (уникальный, переиспользования NL1-001 `EX-NL1-001-SMOKE-001` и ID кампании нет).
- Вход (только raw blobs): fixture `dsdna8.top` (148 B, sha256 `f1aded90…` MATCH пину), `init.dat` (4498 B, sha256 `0ff76d54…` MATCH пину); smoke-вход = опубликованный `docs/evidence/NL1-001/smoke-run/quick_input_smoke` (414 B, sha256 `579cc93a9d0490b532867633cfcd49e50fba94d1ad7f1f140de1dd127e6148e0`), функциональные ключи подтверждены: `steps = 1e4`, `print_conf_interval = 1e4`, `print_energy_every = 1e3` — отклонения от verbatim `quick_input` ровно те, что заявлены §7.
- Исполнение: `/usr/bin/time -v <rebuild>/bin/oxDNA quick_input` на собственной пересборке.

```text
RUN_EXIT                 = 0
wall clock               = 0.14 s (NL1-001 smoke: 0.13 s)
max RSS                  = 6620 KB   (NL1-001: 6424 KB)
engine verdict           = «END OF THE SIMULATION, everything went OK!»
seed (random)            = -588845438 (новый, из log.dat)
engine facts             = RELEASE: v3.7; GIT COMMIT: 00dc7fb; N: 16, N molecules: 2
energy.dat               = 11 строк, NaN/Inf = 0
trajectory.dat           = 1 конфигурация
```

- Observable тем же опубликованным `analyze_energy.sh`: **avg_col2 = −1.36689954545**, delta от оракула **+0.01280301599** → IN_BAND.
- Сравнение с NL1-001 smoke-артефактами (тот же инструмент на опубликованном `docs/evidence/NL1-001/smoke-run/energy.dat`, 11 строк): **avg_col2 = −1.36018000000**, delta **+0.01952256144** → IN_BAND. Оба прогона в одной полосе −1.3797±0.15, расхождение 0.0067 ≪ 0.15 — energy-полоса СОВМЕСТИМА. Это compatibility/execution-факт smoke-уровня, НЕ scientific claim (научная интерпретация — только по протоколу E1 и кампании NL2-002).
