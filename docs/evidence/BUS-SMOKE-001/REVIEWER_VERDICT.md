# BUS-001 Implementation Review — Fresh Reviewer R1 Verdict

```text
Verdict:        PASS
Claim ceiling:  C0_SOFTWARE_ONLY
Subject:        control/git-task-bus-r1 @ 60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c
Reviewed tree:  (см. ниже, проверен blob-хэш ключевых файлов)
Reviewer:       независимая fresh-сессия, P1.2 из GIT_TASK_BUS_POST_PILOT_CORRECTION_R1.md
Worktree:       C:\NanoLab\review-bus-001, ветка review/bus-001-r1
Merge:          НЕ выполнялся и не разрешён; merge в main остаётся Human Gate
```

Брокер `tools/task_bus.py` и его протокол по всем пунктам bounded scope дефектов
не показали. Найден один MEDIUM finding средовой природы в тестовой обвязке
(не в брокере) и несколько LOW/INFO замечаний — см. Findings. PASS дан с
условием: MEDIUM finding должен быть закрыт до P1.4 Human Gate, поскольку
merge policy требует `NO_UNRESOLVED_BLOCKERS`.

## 1. Subject и целостность

- Reviewed subject: `control/git-task-bus-r1` @ `60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c` (PR #20 draft), получен свежим `git fetch` с origin.
- Код менялся только в commit `99a93c0` (`git log main..HEAD -- tools/task_bus.py tests/` — единственная запись); после него менялись только docs/evidence.
- Blob-хэши совпадают с `EX-BUS-001-R1/evidence/validation.json`:
  - `tools/task_bus.py` = `a3d0556717f3320e885f4092f242bed53bf0584f` ✓
  - `tests/task_bus/test_task_bus.py` = `7f8c93972be0b4efe88204457eda92f15fa043b4` ✓
- Историческое evidence имплементёра (40/40 на Python 3.13.5 / Git 2.47.3 / Linux) пересчитано и не принималось на веру; см. §3.

## 2. Проверенные команды и результаты

Среда fresh-прогона: Windows, Python 3.11.8, Git 2.53.0.windows.1
(отличается от ссылочной среды имплементёра — Linux, Python 3.13.5, Git 2.47.3).

| # | Команда | Результат |
|---|---|---|
| 1 | `git fetch origin control/git-task-bus-r1` | `FETCH_HEAD = 60bdca6a…` — exact HEAD подтверждён |
| 2 | `git worktree add --detach C:\NanoLab\review-bus-001 60bdca6a…` | создан; затем ветка `review/bus-001-r1` от exact HEAD |
| 3 | `python -m pytest tests/task_bus/ -v` | **1 failed, 38 passed, 1 skipped** (47.7 s) — лог `pytest-run-r1.log`; failed = средовой (см. F-1), skipped = symlink-тест на Windows |
| 4 | probe `git -C <bare> rev-parse` vs `git --git-dir=<bare> rev-parse` | `-C` → exit 128 `safe.bareRepository is 'explicit'`; `--git-dir` → OK; с пустым `GIT_CONFIG_GLOBAL` `-C` → OK. Root cause F-1 подтверждён |
| 5 | CLI negative-probes на scratch bare remote (`cli-negative-probes-r1.ps1`, лог `cli-negative-probes-r1.log`) | 12/13 probe OK на прогоне; 13-й (stolen token) перепроверен вручную — см. §4; journal после 8 событий реплеится (`status` exit 0) |
| 6 | Статический аудит `tools/task_bus.py` (полное чтение) + диф `main...HEAD` (9 коммитов, +2951) | см. §5 |

## 3. Тест-сьют: расхождение с историческим 40/40

- `test_independent_clones_full_cycle_and_main_untouched` падает на
  `run_git(<bare remote>, "rev-parse", "main")` →
  `fatal: cannot use bare repository … (safe.bareRepository is 'explicit')`.
- Root cause: в глобальном конфиге пользователя (`C:/Users/root/.gitconfig`)
  задано `safe.bareRepository = explicit`; при нём `git -C <bare>` (implicit
  discovery) запрещён, `git --git-dir=<bare>` (explicit) разрешён. Проверено
  на scratch bare repo в обеих конфигурациях.
- Падает тестовая обвязка, а не брокер: `GitBus` никогда не обращается к bare
  репозиторию через `-C` (в пилоте каждый актор работает из non-bare клона).
- Ссылочный результат 40/40 объясним: в ссылочной среде этот конфиг
  отсутствует. Несоответствие честно покрыто оговоркой имплементёра
  «Windows этим проходом не проверялся», а зона «safe.bareRepository behavior»
  прямо заявлена в POST_PILOT_CORRECTION §6 — воспроизведена данным ревью.
- `test_symlink_candidate_and_local_smoke_are_rejected` — skip на Windows
  (`Platform does not permit unprivileged symlinks`); транспортная проверка
  mode 100644 в брокере при этом сохраняется.

## 4. Независимые CLI negative-контролы (scratch remote)

Все 13: OK.

```text
dup-init                        -> BUS_ALREADY_EXISTS            OK
open-by-implementer             -> OPEN_DENIED                   OK
unknown-actor                   -> ACTOR_NOT_ALLOWED             OK
wrong-role-claim                -> TASK_NOT_CLAIMABLE            OK
competing-claim (после claim-a) -> TASK_NOT_CLAIMABLE            OK
foreign-actor-with-stolen-token -> STALE_OR_FOREIGN_LEASE        OK (перепроверено вручную:
   первый прогон показал OSError, т.к. probe-скрипт ссылался на несуществующий
   файл отчёта; с существующим файлом CLI вернул ровно STALE_OR_FOREIGN_LEASE, exit 2)
wrong-token-heartbeat           -> STALE_OR_FOREIGN_LEASE        OK
heartbeat-no-receipt            -> fail-closed, exit 2           OK
early-reclaim (lease живой)     -> LEASE_NOT_EXPIRED             OK
pass-with-failed-check          -> PASS_WITH_FAILED_CHECK        OK
reviewer-subject-drift          -> SUBJECT_MISMATCH              OK
candidate-ref-drift             -> CANDIDATE_REF_DRIFT           OK
cli-claim-race (2 процесса)     -> ровно 1 победитель, второй TASK_NOT_CLAIMABLE, журнал без дубликатов OK
```

Живой тайминг-тест истечения lease (60 s минимум) не выполнялся; поведение
истёкшего lease покрыто редьюсер-тестами (`LEASE_EXPIRED`, `reclaim` после
истечения, `STALE_OR_FOREIGN` для старого владельца) и статическим аудитом
условий `at >= lease["until"]` / `at < lease["until"]`.

## 5. Аудит broker'а по bounded scope

```text
CAS/claim race        PASS — commit c единственным родителем = прочитанный HEAD;
                      non-FF push = compare-and-swap; при конфликте fresh re-read и
                      повторная валидация редьюсером (rebase старого claim исключён);
                      конкурентность подтверждена in-process гонкой, гонкой клонов и
                      CLI-гонкой двух процессов (всегда 1 победитель).
Lease/fencing         PASS — один активный lease на задачу; token = event id claim'а;
                      все операции кроме reclaim/resume/cancel/invalidate требуют
                      actor+token+`at < until`; старый token после release/reclaim/
                      invalidate/переклейма отвергается (STALE_OR_FOREIGN_LEASE);
                      reclaim только для DIRECTOR и только после истечения.
Idempotency/retry     PASS — дедупликация по event id с контролем содержимого
                      (IDEMPOTENCY_KEY_COLLISION при коллизии); CLI pending message-id
                      переживает рестарт; потерянный ACK восстанавливается поиском id
                      в журнале без дубля; retry не сбрасывает исходный receipt.
Subject drift         PASS — check_subject на каждом finish заново fetch-ит candidate
                      ref: head/tree/base-ancestry/непустой diff/scope/mode 100644;
                      reviewer/verifier/director проверяют сохранённый subject;
                      drift инвалидирует прежний PASS; INSUFFICIENT_EVIDENCE -> BLOCKED
                      -> resume в ту же роль.
State/evidence sync   PASS — state выводится редьюсером из append-only журнала,
                      ручной копии нет; blob-хэши evidence совпадают с HEAD;
                      stale-статусы live trial явно superseded correction-документом
                      и DIRECTOR.md §8; live-queue-snapshot.json помечен как
                      неавторитетный; отрицательные исходы сохраняются в журнале.
Role separation       PASS — phase==role; actor не может войти в approvals дважды
                      (ROLE_SEPARATION_REQUIRED); FAIL/INSUFFICIENT_EVIDENCE от
                      IMPLEMENTER запрещены; реализация APPROVALS_MISSING только при
                      полном наборе 4 ролей; repair сбрасывает approvals и subject.
Repair loops          PASS — бюджет max_repairs (в пилоте 2) проверяется и на FAIL
                      reviewer/verifier, и на invalidate; repairs монотонно растёт;
                      отрицательный отчёт остаётся в истории.
Negative controls     PASS — 40 тестов (38 passed + 1 средовой fail + 1 skip здесь,
                      40/40 в ссылочной среде) плюс 13 независимых CLI-probe (§4).
Concurrency writers   PASS — параллельные writer'ы на разные задачи сохраняют все
                      события (retry без потери), на одну задачу — единственный
                      победитель; отравленный GIT_DIR/GIT_WORK_TREE окружения
                      нейтрализуется; dirty index/worktree клонов не затрагивается.
```

Замечания по дизайну, признанные корректными для пилота: heartbeat допускает
бесконечное продление lease (cooperative-модель); нет exactly-once внешних
side effects (явно задокументировано); 2 MB лимит журнала «кирпичирует» шину
fail-closed без ротации (заявленное ограничение пилота); identity — protocol
identities (граница задокументирована в correction §4).

## 6. Findings

| ID | Severity | Область | Суть | Требуемое действие |
|---|---|---|---|---|
| F-1 | MEDIUM | test harness, Windows | Сьют не зелёный «из коробки» на Windows/Git 2.53 при `safe.bareRepository=explicit` в user gitconfig: обвязка обращается к bare remote через `git -C <bare>`. Брокер не затронут; ссылочная среда зелёная | Закрыть до P1.4 Human Gate: в тестовой обвязке использовать `--git-dir`/`git -c safe.bareRepository=contains`/safe.directory, либо зафиксировать требование к среде в docs. Не блокирует P1.3 |
| F-2 | LOW | test platform coverage | Symlink negative-control skip'ается на Windows — live-проверка отказа symlink на Windows отсутствует | Опционально: Windows-эквивалент проверки (junction/reparse point) или явная пометка в docs |
| F-3 | LOW | broker robustness | `decode()` не ловит `RecursionError` на глубоко вложенном JSON — вместо чистого `BusError` будет traceback; fail-closed сохраняется (записи не будет), модель доверенного writer'а | Исправить в production-ревизии (P2): ловить `RecursionError`/ограничивать глубину |
| F-4 | LOW | CLI ergonomics | `--actor` по умолчанию `director-pilot`: забытый флаг молча даёт Director-операции. Редьюсер fail-closed для чужих фаз, но в production ревизии стоит требовать явный `--actor` для мутаций | В production-ревизии (P2) |
| F-5 | INFO | protocol | Истечение lease не проверялось живым таймингом (см. §4); clock skew guard ±60 s cooperative | Покрыто редьюсер-тестами; опционально живой контроль в P1.3 |
| F-6 | INFO | identity | Разные actor_id не доказывают независимость исполнителей — корректно задокументировано; P2 требует protected writer/identity proof | Уже в плане (correction §4); без действий |

## 7. Claim ceiling и границы вердикта

```text
SCIENTIFIC CLAIM:          НЕ заявляется. C0_SOFTWARE_ONLY.
ЧЕКПОИНТ:                  Ни один NL*/INFRA* чекпоинт не закрывается данным ревью.
COMPLETED_SANDBOX:         Не равно ACCEPTED (BUS-SMOKE-001 остаётся sandbox-фактом).
ЧТО ДОКАЗАНО:              Механические свойства транспорта/автомата (CAS, fencing,
                           idempotency, role separation, exact-subject binding,
                           negative controls) на reviewed subject.
ЧТО НЕ ДОКАЗАНО:           Production-пригодность (P2+), identity independence,
                           Windows-first-class поддержка, масштабирование.
NEXT GATE:                 P1.3 Fresh exact-head Verifier на том же subject
                           60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c; затем P1.4
                           Human Gate с условием закрытия F-1.
```

## 8. Review-ветка и артефакты

- Ветка: `review/bus-001-r1` (создана от exact HEAD `60bdca6a…`, non-force push, merge не выполнялся).
- Артефакты: `docs/evidence/BUS-SMOKE-001/REVIEWER_VERDICT.md` (этот файл),
  `pytest-run-r1.log`, `cli-negative-probes-r1.log`, `cli-negative-probes-r1.ps1`.
- Ограничения ревью: ссылочная Linux-среда не воспроизводилась; живой тайминг
  lease не выполнялся; ревью ограничено bounded scope broker'а (state/evidence
  sync, lease/fencing, CAS, retry/idempotency, subject drift, role separation,
  repair loops, negative controls) и не является full-repository regression.
