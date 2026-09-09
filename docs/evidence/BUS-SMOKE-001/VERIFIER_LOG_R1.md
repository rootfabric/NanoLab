# VERIFIER LOG R1 (P1.3, fresh exact-head) — рабочие заметки

Verifier: отдельная fresh-сессия. Worktree: `C:\NanoLab\verify-bus-001`, ветка `verify/bus-001-r1` @ `60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c`.
Роль: независимый exact-head Verifier реализации BUS-001 (не наследует чужой PASS; scripted fixtures не считаются review).

## 1. Сверка окружения

- merge-base(main, 60bdca6) = `95b1319600bcc64572d84c0456acb927802ab806` — совпадает с frozen BASE пилота и `base_sha` в `pilot-task.json`. Ветка `control/git-task-bus-r1` основана на exact main, зафиксированном в work order.
- Диф main..60bdca6 содержит также удаления (evidence NL0-002/NL0-003/NL1-001 и др.) — это эффект устаревшей базы (main ушёл вперёд), а не удалений на ветке; для вердикта значимы только добавленные файлы bus-линии.

## 2. Прочитано полностью

- `AGENTS.md` (main и ветка: в ветке добавлены DIRECTOR fast path + запрет P2 до P1.1–P1.4 + `COMPLETED_SANDBOX IS NOT CANONICAL ACCEPTANCE`).
- `docs/control/GIT_TASK_BUS_RU.md` (Rev NL-BUS-PILOT-R1): claim ceiling C0_SOFTWARE_ONLY; bus = SANDBOX; production merge — Human Gate.
- `docs/control/GIT_TASK_BUS_POST_PILOT_CORRECTION_R1.md` (Rev NL-BUS-POST-PILOT-R1): BUS-SMOKE-001 = COMPLETED_SANDBOX, NOT ACCEPTED; gates P1.1–P1.4; P1.3 = fresh exact-head Verifier (эта сессия); терминология хэшей (GIT_BLOB_SHA1 / CANONICAL_BLOB_SHA256 / CHECKOUT_SHA256); identity boundary (actor_id != независимый executor).
- `tools/task_bus.py` (526 строк), `tests/task_bus/test_task_bus.py` (476 строк, 40 тестов: 24 reducer + 16 git-интеграция).
- `config/control/task-bus/pilot-policy.json`, `pilot-task.json`.
- `docs/work/executions/EX-BUS-001-R1/evidence/validation.json` + смежные evidence-файлы (см. ниже).

## 3. Ключевые наблюдения по коду (предварительные, до исполнения)

- Reducer `apply()`: fail-closed проверки ролей/lease/token/budget; `finish` IMPLEMENTER требует subject{head,tree,ref=work/*}; PASS только при всех checks exit 0; ROLE_SEPARATION_REQUIRED запрещает один actor в двух approvals; DIRECTOR finish требует все 4 approval → COMPLETED_SANDBOX (не ACCEPTED).
- Транспорт: fetch в уникальный `refs/task-bus/<uuid>`, exact-parent commit-tree, non-force push; при потере ACK — поиск message_id в журнале (idempotent recovery), максимум 5 попыток.
- `decode()`: дубль JSON-ключей, NaN/Infinity, >2MB — отклоняются. `validate_policy`: mode=SANDBOX обязателен, lease 60–3600s, claims 4–32, repairs 0–5, DIRECTOR required.
- `check_subject()`: candidate ref drift, tree mismatch, ancestry от base, непустой diff, только allowed paths (`docs/work/pilots/<ID>/`), только mode 100644 blob (symlink/commit-entries отклоняются).
- CLI: `task-bus-receipts/<actor>/<task>.json` хранит token; pending message-id для retry; receipt mismatch по remote/branch/actor/task проверяется.
- Environment-защита: `git()` вычищает GIT_DIR/GIT_WORK_TREE/... из env; `GIT_TERMINAL_PROMPT=0`.

## 4. План верификации (по mandate)

1. `pytest tests/task_bus/` в этом worktree — точный результат; при падении проверить гипотезу `safe.bareRepository=explicit` в user gitconfig (повтор с `GIT_CONFIG_GLOBAL=NUL`); зафиксировать условия зелёного/красного.
2. ≥5 собственных негативных CLI-проб на scratch bare remote: competing claim, stale/stolen lease, subject mismatch/drift, dup-init/idempotent append, wrong role (плюс смежные по времени).
3. Сверка subject: `git ls-remote` ветки `control/git-task-bus-r1` = `60bdca6…`; blob-хэши `tools/task_bus.py` и `tests/task_bus/test_task_bus.py` против EX-BUS-001-R1/evidence/validation.json (GIT_BLOB_SHA1 = a3d0556… / 7f8c939…; sha256 из working-tree при LF-чекнуте должен совпасть с canonical, т.к. checkout без CTE).
4. Отсутствие canonical acceptance: BUS-SMOKE-001 = COMPLETED_SANDBOX, не ACCEPTED; validation.json: `canonical_acceptance: false`, `production_activation: false`.

## 5. Статус

- [x] Чтение диффа и документов
- [ ] pytest
- [ ] Негативные CLI-пробы
- [ ] Сверка subject/хэшей
- [ ] VERIFIER_VERDICT.md (финальный коммит)

CONTINUATION: заметки материализованы до pytest-прогона.
