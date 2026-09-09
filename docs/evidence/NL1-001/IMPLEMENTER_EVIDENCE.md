# NL1-001 — Implementer Evidence Map

Исполнение: `EX-NL1-001-R1`. Дата: 2026-09-09. Роль: IMPLEMENTER (orchestrating session DSH harness; actor = главный агент миссии «выполняй NL1»).

## Intent и классы

- Work Order: `NL1-001` — зафиксировать среду и upstream smoke (см. [WO-NL1-001](../../work/WO-NL1-001.md)).
- Risk: `HIGH` (protocol/environment pin). Claim: `C0_SOFTWARE_ONLY` — научный claim из NL1-001 НЕ выставляется.
- Checkpoint: NL1; acceptance каталога: «one frozen non-AI reference path executes end-to-end with measured resources» (закрывается связкой NL1-001 + NL1-002, не этим WO в одиночку).

## Exact subject

- Base SHA: `57c1e63733ea3b10f991c0f9609c426dc75b17a5` (= `origin/main` на старте).
- Branch: `work/nl1-001-env-pin-smoke-r1` (START-коммит `dd4692d`).
- Engine subject: oxDNA `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` (см. [ENGINE_ENVIRONMENT_R1](../../research/ENGINE_ENVIRONMENT_R1.md)).

## Изменённые поверхности

```text
docs/work/WO-NL1-001.md                                  (dispatch)
docs/research/ENGINE_ENVIRONMENT_R1.md                   (environment pin)
docs/evidence/NL1-001/**                                 (evidence: этот файл + smoke-run/)
docs/work/executions/EX-NL1-001-R1/**                    (passport, events)
docs/work/SESSION_LOG.md                                 (append)
```

Вне scope изменённых поверхностей: `project/state.json`, `project/plan.json`, policies, `E1-PROTO-R1` — не тронуты.

## Входы и дигесты

Fixture `test/DNA/DSDNA8` @ pinned commit — извлечены сырыми blob'ами (bash redirect, WSL), **SHA-256 4/4 MATCH** против пинов `E1-PROTO-R1` §2.2:

| Файл | SHA-256 (пин → факт) | Size |
|---|---|---|
| dsdna8.top | f1aded90…03fc4 → f1aded90…03fc4 **MATCH** | 148 B |
| init.dat | 0ff76d54…1a9e0 → 0ff76d54…1a9e0 **MATCH** | 4498 B |
| quick_input | 8935c4bc…f74a2 → 8935c4bc…f74a2 **MATCH** | 533 B |
| quick_compare | 86a8b6ac…e3ce27 → 86a8b6ac…e3ce27 **MATCH** | 51 B |

Blob SHA-1 в pinned tree совпали с пинами §2.2 (4/4) — проверено `git ls-tree`.

**Негативный артефакт (сохраняется):** Windows working-tree checkout при `core.autocrlf=true` даёт CRLF-копии; их SHA-256 расходятся с пинами: dsdna8.top `a9e8cb7e…24bd2`, init.dat `354ccb3e…3e3a6`, quick_input `e3313646…67b1e4`, quick_compare `a65227cd…b29761a`. Промежуточная попытка извлечения через PowerShell-пайплайн (`git cat-file | Out-File`) также искажает байты (хэши `5b1edb7b…84f39`, `2f1e1f68…8a837e`, `7efbc153…19accb`, `25a45a18…b6db`). Вывод: только `git cat-file blob` с bash-редиректом в WSL/Linux. Это правило включено в ENGINE_ENVIRONMENT_R1 §5 и §9.

## Команды и exit codes (ключевые)

```text
git -C C:\NanoLab\main fetch origin / rev-parse HEAD        -> base = origin/main = 57c1e63
git worktree add C:\NanoLab\nl1-001 -b work/nl1-001-env-pin-smoke-r1 57c1e63
git clone/fetch oxDNA; checkout pinned commit               -> HEAD = 00dc7fb9...
sha256sum (WSL) fixture                                     -> 4/4 MATCH
curl cmake-3.31.6-linux-x86_64.tar.gz + official checksum   -> SHA-256 MATCH Kitware
cmake ../oxdna-src -DCMAKE_BUILD_TYPE=Release -DCUDA=OFF -DMPI=OFF  -> CONFIGURE_EXIT=0
make -j20                                                   -> BUILD_EXIT=0, wall 14.1 s
oxDNA quick_input_smoke (EX-NL1-001-SMOKE-001)              -> SMOKE_EXIT=0
```

Полная воспроизводимость — ENGINE_ENVIRONMENT_R1 §2–§4.

## Запуски (_runs_ NL1-001)

Единственный запуск: `EX-NL1-001-SMOKE-001` (технический go/no-go, не E1):

```text
execution_outcome  = COMPLETED (exit 0)
scientific_outcome = NOT_EVALUATED (smoke вне научного сравнения; C0)
wall 0.13 s; max RSS 6424 KB; 11 строк energy.dat; NaN/Inf = 0; 1 конфигурация
артефакты в Git: docs/evidence/NL1-001/smoke-run/{log.dat, energy.dat, time.log, quick_input_smoke}
  log.dat           85267114c7e25314389906107fa4820ae7f5a0c015dfa3832bf3354a355145d7
  energy.dat        ede2f7e2efcd14a0b1d6f5152bbacbb489ad229cd1f105cce9c8f01bd2e2bd00
  quick_input_smoke 579cc93a9d0490b532867633cfcd49e50fba94d1ad7f1f140de1dd127e6148e0
  time.log          b0638ed05f4435db2d4de1f94f9c73cd7a0df245ba918d2c1cd17ef82eb7a652
```

Verbatim `quick_input` (1e6 steps) НЕ запускался — запрет `E1-PROTO-R1` §7 соблюдён.

## Критерии приёмки WO (самопроверка implementer'а, не acceptance)

- [x] Чистая установка воспроизводима по командам/версиям (ENGINE_ENVIRONMENT_R1 §2–§4).
- [x] Fixture 4/4 SHA-256 MATCH.
- [x] CPU-сборка из pinned commit; version string `v3.7` + `GIT COMMIT: 00dc7fb` из лога; flags/ОС/компилятор записаны.
- [x] Smoke go/no-go COMPLETED; scientific claims отсутствуют.
- [x] Measured wall/RAM зафиксированы; бюджет-оценка для NL1-002 опубликована как planning input.
- [x] Effective defaults §11.1–2 закрыты (ENGINE_ENVIRONMENT_R1 §6), включая подтверждение семантики колонки 2 (§11.3) из исходников.
- [x] GPU-путь задокументирован (§8): CPU only в R1 по протоколу.

## Acceptance / следующим ролям

Реализация соответствует dispatch-границам; ценность для приёмки: acceptance NL1-001 = durable evidence (этот пакет) + независимые REVIEWER/VERIFIER verdicts + Director checkpoint + Human Gate merge. Претензий на ACCEPTED от implementer'а нет.

## Оставшиеся риски

1. NATIVE_COMPILATION=ON (`-march=native`) — бинарь привязан к i9-13900H; на другом executor'е обязательна пересборка (правило §9.4).
2. WSL-окружение владельца не эфемерно; воспроизводимость гарантируется версиями §2 и командами §3, но не snapshot'ом машины.
3. Docs pinned commit не упоминают `john`-алиас — если upstream изменит alias, формула §6 перепроверяется по фактическому логу прогона.
4. Прокси-маршрут: WSL без прямого интернета; все fetch — через Windows-сторону (зафиксировано в event 0001).

## Next action (один)

Независимый REVIEWER: проверить evidence-пакет NL1-001 (exact HEAD, hashes, границы WO, отсутствие научных claims) и выставить вердикт `PASS | FAIL | INSUFFICIENT_EVIDENCE` в `docs/evidence/NL1-001/REVIEWER_VERDICT.md`.
