# VERIFIER VERDICT — Fresh Exact-Head Verification of BUS-001 implementation (P1.3)

- Verdict: **PASS** (BUS_001_VERIFICATION = PASS) для exact subject `60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c`
- Verifier: независимая fresh-сессия P1.3 (перезапуск после сбоя предыдущей verify-сессии; её контекст не использовался)
- Worktree: `C:\NanoLab\verify-bus-001`, ветка `verify/bus-001-r1`, база = `60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c`
- Дата: 2026-09-09 (UTC+3 вечер), среда: Windows, Python 3.11.8, git 2.53.0.windows.1
- Claim ceiling подтверждён: C0_SOFTWARE_ONLY; результат верификации не является canonical acceptance

## 1. Subject binding (exact-head)

| Проверка | Факт | Ожидание | Результат |
|---|---|---|---|
| `git ls-remote origin refs/heads/control/git-task-bus-r1` | `60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c` | `60bdca6…` | MATCH |
| merge-base(main, subject) | `95b1319600bcc64572d84c0456acb927802ab806` | `base_sha` в `config/control/task-bus/pilot-task.json`, frozen BASE пилота | MATCH |
| `refs/heads/work/bus-smoke-001-r1` | `d5bfc55956722e241151e0ef6db5299ee7e55123` | frozen candidate HEAD (POST_PILOT_CORRECTION_R1 §1) | MATCH, дрифта нет |
| `d5bfc55…^{tree}` | `07dc90857bb40f9bb7e4d991ff782d5ebbc044c3` | frozen TREE | MATCH |
| `refs/heads/control/task-bus-pilot-r1` | `6e95891db110438c3a888aec9af7721ccdb63ceb` | frozen BUS ref | MATCH |
| receipt blob в candidate tree | `379c597d940fa9ded54ed9549d63a68ad48ead48` (mode 100644) | `GIT_BLOB_SHA1` (correction §3) | MATCH |

Хэши кода против `docs/work/executions/EX-BUS-001-R1/evidence/validation.json`:

| Файл | GIT_BLOB_SHA1 | CANONICAL_BLOB_SHA256 | Результат |
|---|---|---|---|
| `tools/task_bus.py` | `a3d0556717f3320e885f4092f242bed53bf0584f` | `191b0d30…58285a29bb674021f825` (27313 B, `git cat-file blob` → SHA-256) | MATCH |
| `tests/task_bus/test_task_bus.py` | `7f8c93972be0b4efe88204457eda92f15fa043b4` | `3f1a5d8e…a78018e5be341` (22996 B) | MATCH |

Windows working-tree SHA-256 отличаются (CRLF-чекнут: +526/+476 байт CR) — это `CHECKOUT_SHA256`, что ровно соответствует терминологической поправке POST_PILOT_CORRECTION_R1 §3. Подтверждено: `validation.json."sha256"` — канонические хэши байтов blob, не checkout-хэши.

## 2. Исполнение тестов (fresh re-run в этом worktree)

`python -m pytest tests/task_bus/ -v` (собраны все 40 тестов: 24 reducer + 16 git-integration):

- **Run A — дефолтный user gitconfig** (`safe.bareRepository=explicit`, `core.autocrlf=true`): `1 failed, 38 passed, 1 skipped`. Единственное падение — `GitIntegrationTests::test_independent_clones_full_cycle_and_main_untouched`, причём падает собственная assertion теста на строке 326: `git -C <временный bare remote> rev-parse main` → `fatal: cannot use bare repository … (safe.bareRepository is 'explicit')`. Код брокера в момент падения уже успешно завершил полный 4-ролевой цикл; все git-вызовы `tools/task_bus.py` идут в non-bare рабочие клоны, а `ls-remote`/`push` адресуют bare remote по URL как аргумент — этот случай `safe.bareRepository` не блокирует. Гипотеза из мандата подтверждена: красный тест — артефакт тест-харнесса, не брокера.
- **Run B — `GIT_CONFIG_GLOBAL=NUL`**: **39 passed, 1 skipped** — зелёный. Условия зелёного/красного полностью определяются `safe.bareRepository=explicit` в user gitconfig.
- **Skipped** (в обоих прогонах): `test_symlink_candidate_and_local_smoke_are_rejected` — Windows без привилегии symlink (skipTest по OSError). Symlink-защита позитивно не проверена на этой платформе; REDUCE-ветки symlink-контроля покрыты другими тестами (`path_ok`, scope-фильтр) и CLI-пробами.
- `python -m py_compile tools/task_bus.py tests/task_bus/test_task_bus.py` → exit 0.
- Логи: `logs/pytest-windows-default-config.log`, `logs/pytest-windows-GIT_CONFIG_GLOBAL-NUL.log`, условия — `logs/README.md`.

## 3. Негативные CLI-пробы (13 отказов, scratch bare remote, CLI-only)

Скрипты верификатора: `C:\NanoLab\scratch\bus-verifier-probes\probe.py` / `probe2.py` (вне репозитория); журналы: `logs/cli-probes-run1.jsonl`, `logs/cli-probes-run2.jsonl`. Политика проб: `lease_seconds=60`, actors пилота; task `BUS-VPROBE-001`; candidata `work/vprobe-001-r1`. Все отказы — exit 2 с точным кодом ошибки; события при отказе в журнал очереди не попадали (полный happy-path цикл завершился штатно).

| # | Проба | Результат |
|---|---|---|
| P1 | wrong role: `reviewer-a claim` в фазе IMPLEMENTER | `TASK_NOT_CLAIMABLE` |
| P2/Q2 | competing claim: второй implementer при активном lease | `TASK_NOT_CLAIMABLE` |
| Q3 | foreign/stolen token: `implementer-b finish --token <чужой>` при active lease | `STALE_OR_FOREIGN_LEASE` |
| Q4a | stale lease: `finish` с валидным токеном спустя 61 c (> lease 60 c) | `LEASE_EXPIRED` |
| P4b/Q4b | director `reclaim` только после истечения lease | OK (ранний reclaim отвергается reducer-ом; факт: reclaim прошёл только после expiry) |
| Q4c/P4d | старый worker возвращается после reclaim/перекхватa | `STALE_OR_FOREIGN_LEASE` |
| Q5d | token после `release` и нового claim другим actor | `STALE_OR_FOREIGN_LEASE` (fencing по token) |
| P5 | candidate drift: пустой commit в work-ветку до handoff | `CANDIDATE_REF_DRIFT`; после восстановления scratch-кандидата retry через сохранённый pending message-id успешно закоммичен |
| P6b | reviewer report с чужим `subject_head` | `SUBJECT_MISMATCH` |
| P7 | duplicate `init` на существующем bus ref | `BUS_ALREADY_EXISTS` |
| Q1b | idempotent append: повтор claim с тем же `--message-id` | exit 0, `duplicate: true`, bus_head не изменился |
| P9b | PASS-верdict с failing check | `PASS_WITH_FAILED_CHECK` |
| P10/P11 | unknown actor status / claim после terminal | `ACTOR_NOT_ALLOWED` / `TASK_TERMINAL` |

Дополнительно happy-path через CLI доведён до `COMPLETED_SANDBOX`; финальный `status` честно отдаёт `mode=SANDBOX`, `canonical_acceptance=false`. Замечание верификатора: в run 1 два проба (competing/idempotent/lease-expired) сначала дали ложно-нейтральный результат из-за дефекта моего probe-скрипта (`--message-id` после подкоманды отклонил argparse); оба перепроверены в run 2 в чистом виде. Force-push в scratch-окружении использовал только probe-харнесс для восстановления кандидата после дрифта; брокер force-push не выполняет (подтверждено кодом и журналами).

## 4. Canonical acceptance

Проверка `git grep -i ACCEPTED` по subject-дереву (AGENTS.md, DIRECTOR.md, docs/control, docs/work/executions/EX-BUS-*, config/control/task-bus): все вхождения — запреты/отрицания («COMPLETED_SANDBOX != ACCEPTED», «not ACCEPTED», «DO NOT treat COMPLETED_SANDBOX as ACCEPTED»). `validation.json`: `canonical_acceptance: false`, `production_activation: false`. Нигде не объявлено canonical acceptance: BUS-SMOKE-001 = COMPLETED_SANDBOX, BUS-001 ACCEPTANCE = NOT YET — соответствует POST_PILOT_CORRECTION_R1 §1–2.

## 5. Findings (не блокируют PASS, передаются в P1.4/Human Gate)

1. **F1 (test-harness, низкий риск):** `GitIntegrationTests` выполняет прямые `git -C <bare>` вызовы и падает при `safe.bareRepository=explicit` (умолчание в свежих Git for Windows). Предложение repair (следующая ревизия тестов, не этот subject): в тестовом `run_git` добавлять `-c safe.bareRepository=` или выставлять `GIT_CONFIG_GLOBAL` на temp-файл; либо документировать `GIT_CONFIG_GLOBAL=NUL` для Windows-агентов в `GIT_TASK_BUS_RU.md` §8 (сейчас там сказано «Windows этим проходом не проверялся» — теперь проверен, вывод выше).
2. **F2 (наблюдение):** 1 skipped symlink-тест на Windows; контроль symlink остаётся непроверенным позитивно на этой платформе (на Linux в исходном evidence — пройден).
3. **F3 (уже задокументировано):** `epoch_drift` из validation.json усугубился — `main` ушёл с `81e299f` (на момент пилота) до `71535d0`; файлы bus-линии в main отсутствуют, пересечений путей нет, но merge в main будет не fast-forward и требует Human Gate по POST_PILOT_CORRECTION_R1 §8 (включая `PR_HEAD == VERIFIED_HEAD`).
4. **F4 (терминология подтверждена):** различие GIT_BLOB_SHA1 / CANONICAL_BLOB_SHA256 / CHECKOUT_SHA256 на практике воспроизведено; валидационные хэши — канонические.

## 6. Ограничения вердикта

- Вердикт относится строго к `60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c`; любой drift subject инвалидирует этот PASS (correction §7).
- Scripted tests и пробы верификатора доказывают механические свойства транспорта/автомата, не независимость executor-идентичностей (correction §4): `ROLE_SEPARATION_CONFIRMED`, `INDEPENDENT_EXECUTOR_IDENTITY_PROVEN` — не доказано.
- Это P1.3: P2 production activation остаётся заблокированной до P1.4 Human Gate.

## 7. Итог для Director

```text
BUS_001_VERIFICATION = PASS
EXACT SUBJECT        = 60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c
PYTEST               = 39 passed / 1 skipped (GIT_CONFIG_GLOBAL=NUL), Windows
                       1 failed только из-за safe.bareRepository=explicit (тест-харнесс, F1)
NEGATIVE CLI PROBES  = 13 отказов с ожидаемыми кодами, happy-path до COMPLETED_SANDBOX
SUBJECT/HASH BINDING = MATCH (blob SHA1 + canonical SHA256 + frozen pilot refs)
CANONICAL ACCEPTANCE = не объявлена (COMPLETED_SANDBOX, NOT ACCEPTED)
NEXT ACTION          = Director сводит P1.2+P1.3 в BUS-001 = READY_FOR_HUMAN_GATE
                       (с findings F1–F4), P2 остаётся LOCKED до Human Gate
```

Верификатор: fresh exact-head сессия P1.3. Evidence: `docs/evidence/BUS-SMOKE-001/logs/*`.
