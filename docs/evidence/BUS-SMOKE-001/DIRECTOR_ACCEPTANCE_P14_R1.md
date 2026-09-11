# Director Acceptance — P1.4 Human Gate / canonical merge (Git Task Bus, BUS-001)

Дата решения: 2026-09-11 (авторизация владельца от 2026-09-10). Роль: DIRECTOR control-линии Git Task Bus (fresh-сессия; контексты implementer/reviewer/verifier не переиспользовались — только Git-факты, вердиктные документы и машинные записи GitHub). Claim ceiling линии: `C0_SOFTWARE_ONLY` — не меняется. Научные статусы экспериментов (E0/E1/E2) этим решением не затрагиваются.

## Решение

```text
P1.1 State/evidence synchronization        = CLOSED (PASS)   # correction R1 §2 + PR #20 (60bdca6)
P1.2 Fresh implementation Reviewer         = CLOSED (PASS)   # review/bus-001-r1 @ ada1135, REVIEWER PASS @ 60bdca6
P1.3 Fresh exact-head Verifier             = CLOSED (PASS)   # verify/bus-001-r1 @ 2b2db9f, VERIFIER PASS @ 60bdca6
                                                               # + VERIFIER_RECHECK_F1_R1 PASS @ 4d7febd (F1-ремонт)
P1.4 Human Gate / canonical activation     = CLOSED (APPROVED + MERGED)
P2  Production policy + protected writer   = LOCKED          # отдельное решение владельца
BUS-SMOKE-001 = COMPLETED_SANDBOX                            # НЕ ACCEPTED; canonical acceptance не объявлена
BUS-001 ACCEPTANCE                            = READY (P1 chain closed); production activation — P2, owner decision
```

Гейт-чеклист POST_PILOT_CORRECTION_R1 §8 на момент merge:

```text
LIVE_PILOT                = PASS   (BUS-SMOKE-001, frozen subject d5bfc55/07dc908, EX-BUS-001-R1)
HOUSEKEEPING_SYNC         = PASS   (P1.1: stale-статусы superseded, correction R1 в main через PR #20)
IMPLEMENTATION_REVIEW     = PASS   (P1.2: REVIEWER PASS @ 60bdca6; F-1 MEDIUM → условие до P1.4)
EXACT_HEAD_VERIFICATION   = PASS   (P1.3: VERIFIER PASS @ 60bdca6; re-check F1 PASS @ 4d7febd)
PR_HEAD == VERIFIED_HEAD  = PASS   (PR #20 head 4d7febd == re-check subject 4d7febd; вердикт-субъект 60bdca6 — его предок)
NO_UNRESOLVED_BLOCKERS    = PASS   (F-1 закрыт ремонтом 223d49b: только tests/, брокер blob-неизменен a3d05567…)
HUMAN_GATE                = APPROVED (владелец: «мержи PR #20», 2026-09-10)
```

## Основание — вердиктная цепочка

1. **P1.1 State/evidence sync**: `docs/control/GIT_TASK_BUS_POST_PILOT_CORRECTION_R1.md` (NL-BUS-POST-PILOT-R1) в canonical main; stale-статусы superseded явно; frozen pilot-факты §1 неизменны (`work/bus-smoke-001-r1` @ `d5bfc55`, tree `07dc908`, `control/task-bus-pilot-r1` @ `6e95891`, receipt blob `379c597…`) — перепроверено P1.3.
2. **P1.2 REVIEWER PASS** (`review/bus-001-r1` @ `ada1135`, субъект `60bdca6…`): bounded scope брокера — state/evidence sync, lease/fencing, CAS non-FF push, idempotency/retry, subject drift, role separation, repair loops, negative controls (40 тестов + 13 CLI-проб) — все PASS; findings F-1 MEDIUM (тест-харнесс vs `safe.bareRepository=explicit`) + F-2..F-6 LOW/INFO; условие «F-1 закрыть до P1.4».
3. **P1.3 VERIFIER PASS** (`verify/bus-001-r1` @ `2b2db9f`, субъект `60bdca6…`): exact-head binding MATCH (ls-remote, merge-base = frozen BASE `95b1319…`, frozen refs/refs/tree/blob); pytest 39 passed / 1 skipped (`GIT_CONFIG_GLOBAL=NUL`), единственный fail дефолт-конфига — тест-харнесс (F1), не брокер; 13 негативных CLI-проб с ожидаемыми кодами; canonical acceptance нигде не объявлена.
4. **F1-ремонт и re-check** (PR #20, `223d49b` + `4d7febd`): минимальный дифф только `tests/task_bus/test_task_bus.py` (8+/3−, `--git-dir` вместо `-C` для bare-адресации); брокер `tools/task_bus.py` blob-неизменен (`a3d0556717f3320e885f4092f242bed53bf0584f` = субъект-блоб P1.3); `VERIFIER_RECHECK_F1_R1` = PASS @ `4d7febd` (39 passed / 1 skipped в обеих конфигурациях). Оговорка re-check'а (NOTE): полная fresh exact-head re-verification нового HEAD `4d7febd` не проводилась — только ремонт + blob-неизменность брокера; учтена ниже как NOTE в очереди findings.
5. **Роли независимы**: implementer/reviewer/verifier — разные fresh-сессии; Human Gate — владелец. REVIEWER/VERIFIER PASS сами по себе acceptance не объявляли.

## Merge PR #20 (исполнение Human Gate)

| Факт | Значение |
|---|---|
| Авторизация владельца | «мержи PR #20», 2026-09-10 (Human Gate P1.4 открыт явно) |
| PR | rootfabric/NanoLab#20 «harness(bus): Git-backed distributed task workflow pilot» |
| Head | `control/git-task-bus-r1` @ `4d7febd2221e66ebfd73db83530a1e645becba2a` |
| База на момент merge | `main` @ `498d5ad462b6445edd696ff74baad89018e0b744` |
| Дрейф | база PR при создании `60bdca6` существенно отстала; main ушёл вперёд (NL2-002/NL2-003/NL3-001 merges + hosted-ci); histories дивергированы (merge-base `95b1319…`), GitHub trial-merge: `mergeable=true`, `mergeable_state=clean` — конфликтов нет, merge-ветка не потребовалась |
| Draft → ready | `gh pr ready 20`, 2026-09-11 |
| Merge | `gh pr merge 20 --merge` (merge commit, 2026-09-11T09:48:46Z) |
| Merge commit | `51959b6272dbaa86805e93417a4ec1d85498ad25` |
| Вердиктные ветки | `review/bus-001-r1` @ `ada1135` и `verify/bus-001-r1` @ `2b2db9f` — на origin, не переписывались (non-force) |

## Post-merge canonical verification (correction §8 «After merge»)

Свежий `origin/main` = `51959b6` (fetch после merge); expected ancestry подтверждена: `60bdca6` → `4d7febd` → merge `51959b6`, `PR_HEAD == VERIFIED_HEAD`.

Live-CI на merge-коммите — GitHub-hosted (`hosted-ci`, run **34586090475**, event push, subject `51959b6`): **completed / success**, job `RC0 hosted validation (H0)`, все 5 чеков success:

1. machine contracts JSON syntax — OK;
2. harness control consistency — OK;
3. execution passports / work events integrity (все EX-*) — OK;
4. workflow negative-control lint NC-1..NC-7 — OK;
5. validation gate unit tests (`python3 -m unittest discover -s tests -t .`) — **160 tests, OK**.

**Director observation (новая, в очередь): hosted-CI НЕ собирает `tests/task_bus`.** Check 5/5 использует `unittest discover`, а `tests/task_bus/` — не package (нет `__init__.py`): discovery в него не заходит (прямая попытка `unittest discover -s tests/task_bus` даёт «Start directory is not importable»). Факт: «Ran 160 tests» на merge-коммите — тот же счёт, что и до merge (сравнение с логом run `34586090475`: ни одного task_bus-теста). То есть задача «live-CI включает tests/task_bus» фактическим прогоном НЕ подтверждена: hosted-ci зелёный, но task_bus-покрытие в нём отсутствует. Каноническая регрессия task_bus выполнена Director локально на exact merge-коммите `51959b6` (Windows, Python 3.11.8, git 2.53.0.windows.1):

| Прогон | Условия | Результат |
|---|---|---|
| `python -m unittest discover -s tests -t .` | default config (parity с CI Check 5/5) | 160 tests, OK — task_bus НЕ собран |
| `python -m pytest tests/task_bus/ -q` | default user gitconfig (`safe.bareRepository=explicit`) | **39 passed, 1 skipped** (42.53 s) |
| `GIT_CONFIG_GLOBAL=NUL` + `python -m pytest tests/task_bus/ -q` | user gitconfig отключён (контроль) | **39 passed, 1 skipped** (43.12 s) |

Skipped в обоих прогонах — известный F-2 (symlink-негатив на Windows). Зелёный результат достигается в обеих конфигурациях — GIT_CONFIG_GLOBAL-обход не требуется после F1-ремонта, но сохраняется как контрольный. Устранение CI-разрыва (например, `tests/task_bus/__init__.py`, явный второй discover-вызов или pytest в Check 5/5) — кандидаты в P2; изменение `.github/workflows/hosted-ci.yml` требует отдельного гейта с review/verify (NC-lint).

Прочее по §8: entrypoint `AGENTS.md` → `DIRECTOR.md` подтверждён на `51959b6`; task bus tooling доступен из canonical main (`tools/task_bus.py`, `config/control/task-bus/`).

## Границы решения

- `COMPLETED_SANDBOX != ACCEPTED`: BUS-SMOKE-001 остаётся терминально `COMPLETED_SANDBOX`; canonical acceptance/production activation не объявлены. P2 (production policy + protected writer + identity proofs) — **LOCKED** и требует отдельного решения владельца.
- `ROLE_SEPARATION_CONFIRMED`; `INDEPENDENT_EXECUTOR_IDENTITY_PROVEN` — не доказано (correction §4).
- Верификационное покрытие: P1.3 PASS строго на `60bdca6`; на merge-составе `4d7febd` — re-check ремонта + blob-неизменность брокера + локальная каноническая регрессия Director'а на `51959b6` (этот документ). Полная fresh exact-head re-verification `4d7febd`/`51959b6` — NOTE в очереди.
- Frozen pilot-объекты (`work/bus-smoke-001-r1`, `control/task-bus-pilot-r1`, EX-BUS-001-R1 события) не изменялись; очередь bus-журнала вручную не редактировалась; force-push не выполнялся.

## Очередь accumulated findings (не блокируют; адресат — P2/будущие ревизии)

| ID | Источник | Severity | Суть | Куда |
|---|---|---|---|---|
| F-2 | REVIEWER_VERDICT §6 | LOW | Symlink negative-control skip'ается на Windows; live-проверка отказа symlink на Windows отсутствует | P2: Windows-эквивалент (junction/reparse) или пометка в docs |
| F-3 | REVIEWER_VERDICT §6 | LOW | `decode()` не ловит `RecursionError` на глубоко вложенном JSON (traceback вместо чистого `BusError`; fail-closed сохраняется) | P2 production-ревизия брокера |
| F-4 | REVIEWER_VERDICT §6 | LOW | `--actor` по умолчанию `director-pilot` — забытый флаг молча даёт Director-операции | P2: явный `--actor` для мутаций |
| F-5 | REVIEWER_VERDICT §6 | INFO | Истечение lease не проверялось живым таймингом; clock skew guard ±60 s cooperative | Опционально: живой контроль |
| F-6 | REVIEWER_VERDICT §6 | INFO | Разные actor_id не доказывают независимость исполнителей | P2: protected writer/identity proof (уже в плане) |
| NOTE | VERIFIER_RECHECK_F1_R1 §3 | LOW | Полная fresh exact-head re-verification HEAD `4d7febd` не проводилась (re-check покрывает ремонт + blob-неизменность брокера); symlink-скип воспроизведён | P2/следующая ревизия: свежая re-verification при следующих изменениях брокера |
| DIR-1 | этот документ (Director, live-CI R1) | MEDIUM | hosted-ci Check 5/5 (`unittest discover`) не собирает `tests/task_bus` (нет `__init__.py`); CI зелёный без task_bus-покрытия | P2: включить task_bus в CI-коллекцию (отдельный гейт с NC-lint) |

## Следующее действие

P2 «Production policy + protected writer» — только по отдельному явному решению владельца. До него: bus-инструменты доступны из canonical main (`tools/task_bus.py`), но production activation, protected writer и identity proofs не начинаются. Научная линия проекта — без изменений: frontier NL3, next NL3-002 (E2), вопрос прав источника G1 — owner decision при dispatch.

— DIRECTOR, control/git-task-bus-p14-r1 @ `51959b6`, 2026-09-11.
