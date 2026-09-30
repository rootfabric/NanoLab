# REVIEWER_VERDICT — EX-INFRA3-NATIVE-UBUNTU-R2-R1 (R2 activation tooling)

- Дата: 2026-09-30 (UTC)
- Роль: FRESH REVIEWER (независимая изолированная сессия; контекст имплементёра недоступен — только Git-факты, закоммиченные документы и собственные механические проверки)
- Предмет: ветка `infra/infra3-native-ubuntu-r2-activation-r1`, child WO `WO-INFRA3-R2-ACTIVATION-R1`, execution `EX-INFRA3-NATIVE-UBUNTU-R2-R1`
- Review-объект: исполняемый R2 activation tooling (`scripts/r2/` + `config/infra/r2-activation.v1.json` + `tests/test_r2_activation_tooling.py`), claim ceiling `C0_SOFTWARE_ONLY` (НЕ научный WO)
- Verdict: **PASS** (2 MINOR, 4 NOTE; ни одного MAJOR; ни один из 6 machine-инвариантов tooling не опровергнут)

## 1. Binding-факты (измерены самостоятельно)

| Заявление | Измерение | Результат |
|---|---|---|
| base = `8205781def7179d6bdfa6eb7ab2a84d46776649c` = origin/main | `git fetch --all --prune`; `git rev-parse origin/main` → `8205781def7179d6bdfa6eb7ab2a84d46776649c`; `git merge-base 8205781 df6c212` → тот же SHA | ПОДТВЕРЖДЕНО |
| substantive HEAD = `9a6fb6248d697350c2e218d8bbadb34e2177bc8b` | `git rev-parse 9a6fb62` → совпадает | ПОДТВЕРЖДЕНО |
| tree(9a6fb62) = `0c73f85be4eb932ee071517914aa21dc2347273e` | `git rev-parse 9a6fb62^{tree}` → совпадает | ПОДТВЕРЖДЕНО |
| handoff HEAD = `df6c212` | `git rev-parse origin/infra/infra3-native-ubuntu-r2-activation-r1` → `df6c2122cbdf60cebc9e6aa8348aea12685f9d00` | ПОДТВЕРЖДЕНО |
| handoff delta = ровно summary.md + events 0002/0003/0004 + passport status flip | `git show --name-status df6c212`: A summary.md, A events/0002..0004, M passport.json (статус STARTED→HANDOFF_READY, остальное без изменений); код/тесты/config в df6c212 не тронуты (`git diff 26f3d08..df6c212 -- scripts/r2/ tests/ config/` пуст) | ПОДТВЕРЖДЕНО |
| Цепочка f01310e → 26f3d08 → 9a6fb62 → df6c212 | `git log --format='%h %H' 8205781..df6c212` → ровно 4 коммита, линейно, без merge | ПОДТВЕРЖДЕНО |
| WO-документ в первой ветке-коммите | `git show --name-status f01310e` → добавляет `docs/work/WO-INFRA3-R2-ACTIVATION-R1.md` + branch-passport.md + event 0001 + passport.json | ПОДТВЕРЖДЕНО |

События: timestamps машинные, ISO-8601 Z, монотонны (0001 `14:34:36Z` < 0002 `14:50:06Z` < 0003 `14:50:48Z` < 0004 `14:51:50Z`); все `subject_sha` — полные 40-hex (0001 = base, 0002–0004 = substantive HEAD). Passport: поле `notes` отсутствует (урок MINOR-1 prior review), статус `HANDOFF_READY` синхронен терминальному событию `HANDOFF_COMPLETED` (урок MINOR-5), checkpoint `INFRA3` валиден. Уроки prior review EX-NATIVE-UBUNTU-EXECUTOR-R1 (MINOR-2/MINOR-3) учтены.

## 2. Scope и surface sync

- `git diff --name-only 8205781..df6c212` → 25 файлов; каждый сопоставлен с `allowed_paths` паспорта (fnmatch): **25/25 внутри**, нарушений нет. `docs/infra/ROADMAP.md` разрешён, но не тронут (допустимо).
- НЕ тронуты (отсутствуют в diff): `project/state.json`, `project/infra-state.json`, `docs/evidence/**`, все существующие `EX-*` каталоги, `ENGINE_ENVIRONMENT_R1.md`, `AGENT_START*`, `AGENTS.md`, научная история, `docs/work/SESSION_LOG.md`.
- WORK_QUEUE: правка только строки INFRA3-003; вычисленный дельта-анализ строки — **чистая вставка 851 символа** (ACTIVATION TOOLING-блок перед приёмочной ячейкой), удалений 0; остальные строки таблицы не изменены, строки не удалялись/не добавлялись.
- project/infra-plan.json: `note` задачи INFRA3-003 — строгий append; все прочие поля задачи и весь остальной документ байт-идентичны.
- Статусы границ не изменены: `R2_STATUS = WAITING_HOST / NOT_ACTIVE`, `AUTHOR_U1 = NOT_ASSIGNED`, gates/NC `WAITING_HOST` — в surfaces ни одного нового PASS/ACTIVE/VERIFIED/ASSIGNED-статуса (проверено grep по diff и по итоговому дереву). NL5/NL6 статусы не тронуты (единственные упоминания NL5 в diff — перенос существовавшего текста приёма внутри переписанной строки INFRA3-003).

## 3. Machine-инварианты tooling (проверено КОДОМ, тестами и CLI)

| # | Инвариант | Метод проверки | Результат |
|---|---|---|---|
| 1 | Host guard `validate_native_u1` | Код `scripts/r2/fingerprint.py` (kernel Linux, virt=none с fail-closed при rc∉{1}, Microsoft-маркер, ФС ext4/xfs/btrfs, systemd, hostname вне `(outenemy,)`, hostname определён — все причины именованные); тесты `test_outenemy_never_eligible`, `test_wsl_host_rejected`, `test_vm_rejected`, `test_non_native_fs_rejected`, `test_missing_systemd_rejected`; на dev-хосте outenemy `check-host` → NOT_ELIGIBLE exit 2 с единственной причиной forbidden-as-author-host | ПОДТВЕРЖДЁН |
| 1b | build-engine/run → exit 2 BLOCKED_HOST без silent fallback | На outenemy: `build-engine` → BLOCKED_HOST exit 2; `run` → BLOCKED_HOST exit 2, ledger НЕ создан; guard до any side-effect; исключения не глотаются. fingerprint/check-host/nc-plan exit 0, безопасны | ПОДТВЕРЖДЁН (но см. MINOR-1 по gate/nc-verify/report/activation-check) |
| 2 | Run contract | `contract.py`: attempt id = `<run_base>`/`<run_base>-R<n>`; append-only JSONL; `AttemptReuseError` при повторе — в т.ч. после FAILED_TECHNICAL (тест `test_reuse_rejected_even_after_failure`); двойная проверка (executor pre-check + ledger.append); retry получает новый id (тест S001→S001-R1); FAILED_TECHNICAL сохраняет попытку; `scientific_outcome = NOT_EVALUATED` всегда (константа, не параметр) | ПОДТВЕРЖДЁН |
| 3 | Raw evidence | `<raw_root>/<execution-id>/<attempt-id>/` с stdout.txt/stderr.txt/exit.json/artifact-manifest.json (тест + повтор через API в tmp); manifest = path/sha256/size/producer/retention + digest канонического JSON; **manifest не включает сам себя** (пишется последним; тест фиксирует 3 записи: stdout/stderr/exit.json) | ПОДТВЕРЖДЁН |
| 4 | Gates U1–U5 / NC-U1..U5 | `gates.py`: WAITING_HOST→PASS\|FAIL; PASS только при непустом evidence_ref И существующем файле И size>0, иначе `GateError` (CLI: REJECTED exit 3 — воспроизведено, совпадает с committed evidence); недопустимый id/статус → GateError | ПОДТВЕРЖДЁН (но см. MINOR-2 о происхождении evidence) |
| 5 | Activation decision | `activation_decision`: r2_activated только при all gates PASS ∧ all NC PASS ∧ native-eligible fingerprint ∧ review PASS ∧ verify VERIFIED ∧ human_gate_approved; иначе WAITING_HOST / NOT_ACTIVE + полный unmet-список. Тест `test_refuses_outenemy_fingerprint_even_when_everything_passes` — outenemy-fingerprint отброшен при всех PASS; на outenemy `activation-check` → exit 2, r2_activated=false (воспроизведено) | ПОДТВЕРЖДЁН |
| 6 | Engine build | `engine_build.py`: pin `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` верифицируется ДО сборки (`verify_pinned_source`; несовпадение → BLOCKED_SOURCE_PIN exit 3); флаги Release/DOUBLE=ON/CUDA=OFF/MPI=OFF (configure_argv + EXPECTED_CACHE_PINS); CMakeCache парсится назад и верифицируется (deviation → exit 5); `binary_sha_equality_with_r1_required=false` — и в коде, и в config, и в тесте | ПОДТВЕРЖДЁН |

Дополнительно: научных прогонов нет — oxDNA нигде не вызывается (только cmake/git argv-строители и операторские команды run); секретов/credentials/сетевых вызовов нет (grep по scripts/r2 — только упоминания SSH в docstring); платформозависимости корректны (код Linux-целевой, тесты кроссплатформенные: fake runners, tmp dirs, `sys.executable`, CLI-тесты условны по hostname).

## 4. Тесты и mutation-проверки

- `PYTHONPATH=scripts python3 -m pytest tests/test_r2_activation_tooling.py -q` → **52 passed** (совпадает с заявлением; 0 skip на этом хосте).
- `python3 -m pytest tests/ -q` → **426 passed**. Канонический набор на базе: в `main` @ 8205781 collect-only → **374**; 374 + 52 = 426 — арифметика сходится.
- Mutation-проверки (правки КОПИЙ в worktree, после каждой `git checkout --`; в коммит не вошли):
  - A: удалена проверка reuse в `AttemptLedger.append` → FAIL `LedgerTest::test_reuse_rejected_even_after_failure` (executor pre-check остаётся вторым барьером — defense in depth);
  - B: удалена evidence-проверка в `GateReport.set_status` → FAIL `test_pass_requires_existing_nonempty_evidence` + `test_gate_command_rejects_pass_without_evidence`;
  - C: отключено hostname-правило в `validate_native_u1` → FAIL `test_outenemy_never_eligible` + `test_refuses_outenemy_fingerprint_even_when_everything_passes` + `test_check_host_reports_verdict_and_exit_code` (+2 skip условных CLI-тестов, корректно).
  Тесты реально ловят слом инвариантов — негативное покрытие адекватно.

## 5. CLI negative controls на dev-хосте (outenemy) и сверка с committed evidence

Хост проверки: `hostname` → `outenemy` (совпадает со средой имплементёра). Все 5 committed evidence-файлов воспроизведены:

| Evidence-файл | Повтор | Сверка |
|---|---|---|
| dev-host-check-host-NOT_ELIGIBLE.json | `check-host` → exit 2, NOT_ELIGIBLE, hostname outenemy, причина forbidden-as-author-host | БАЙТ-СОВПАДЕНИЕ |
| dev-host-build-engine-BLOCKED_HOST.json | `build-engine` → exit 2, BLOCKED_HOST | БАЙТ-СОВПАДЕНИЕ |
| dev-host-gate-rejected.json | `gate U1 PASS --evidence ''` → exit 3, REJECTED | БАЙТ-СОВПАДЕНИЕ |
| nc-plan-NC-U5.json | `nc-plan --nc NC-U5` → exit 0 | БАЙТ-СОВПАДЕНИЕ |
| dev-host-activation-refused.json | `activation-check` → exit 2, r2_activated=false | СОВПАДЕНИЕ при команде, зафиксированной в event 0002 command_refs (см. NOTE-1) |

## 6. Config ↔ код ↔ канонические документы

- `config/infra/r2-activation.v1.json` ↔ код: engine pin, intended_flags, `binary_sha_equality_with_r1_required=false`, `author_u1=NOT_ASSIGNED`, `r2_status=WAITING_HOST / NOT_ACTIVE`, `forbidden_hostnames=[outenemy]`, `new_science_without_r2=HARD_BLOCKED` — байт-согласованы (тест `ConfigContractTest` + независимая сверка).
- Канонические документы: pin `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` = `ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` §(строка 16) и `WO-NATIVE-UBUNTU-EXECUTOR-R1.md` (строка 78); флаги `CPU · DOUBLE=ON · CUDA=OFF · MPI=OFF` = тот же документ (строка 72); `AUTHOR_U1 = NOT_ASSIGNED`, `R2_STATUS = WAITING_HOST / NOT_ACTIVE`, `OUTENEMY_ROLE = EXTERNAL_U2_ONLY` = `NATIVE_UBUNTU_EXECUTION_POLICY_R1.md` (строки 20–24). Требования binary-sha-equality с R1 в канонических доках нет. Расхождений нет.

## 7. Machine-проверки репозитория (независимый прогон)

- `PYTHONPATH=scripts python3 -m harness.cli check-consistency` → `ok: true`
- `PYTHONPATH=scripts python3 -m harness.workflow_lint` → `blocking: 0`
- `python3 scripts/harness/work_cli.py validate docs/work/executions/EX-INFRA3-NATIVE-UBUNTU-R2-R1` → `ok: true`, status `HANDOFF_READY`, `has_terminal_handoff: true`, event_types START/CONTINUATION/VALIDATION/HANDOFF, post-terminal corrections отсутствуют, passport_sha256 `73caa3cf…95c`
- jsonschema Draft 2020-12 (jsonschema 4.23.0): все 4 события против `work-event.schema.v1.json` — VALID; passport против `execution-passport.schema.v1.json` — VALID

## 8. Findings

### MAJOR
Отсутствуют.

### MINOR-1 — Host-guard покрытие уже, чем заявлено в summary.md §1(7) и WO §2(инвариант 1)
- Факт: `require_u1_or_exit` вызывают только `build-engine` и `run`. `gate`, `nc-verify`, `report`, `activation-check`, `nc-plan` исполняются на любом хосте. Измерено на outenemy: `gate --status PASS --evidence <непустой файл>` → **RECORDED exit 0**; `nc-verify` с «зелёным» JSON → pass=true exit 0.
- Текст: summary.md §1(7) утверждает, что все семь subcommands «отказывают на не-eligible хосте (exit 2 BLOCKED_HOST)»; WO §2(1) прямо перечисляет `gate` и `nc` среди обязанных отказывать. Код этому тексту не соответствует (event 0002 сформулирован аккуратнее — «исполняющие»).
- Влияние: на активацию R2 не влияет (activation-check всё равно требует fingerprint + review + verify + human gate; canonical surfaces не пишутся tooling'ом); но на не-U1 хосте можно создать durable gate-отчёт с PASS-записями, противоречащий смыслу host guard.
- Рекомендация: в repair-ревизии добавить `require_u1_or_exit` в `gate` и `nc-verify` (минимальный диффит), ЛИБО явно сузить формулировки в WO/summary новой ревизией документа. Verifier/merge-гейтам: не считать gate-отчёты, созданные вне U1, валидными gate-фактами.

### MINOR-2 — Gate PASS не привязан к происхождению evidence
- Факт: проверяется только существование и непустота файла: `evidence_ref` может указывать на ЛЮБОЙ непустой файл диска (вне raw-дерева, без проверки content/digest/происхождения). Заявленный в брифе инвариант («PASS только с существующим непустым evidence-файлом») реализован точно как заявлен; пробел — относительно устойчивости к fabricated PASS: PASS-запись подтверждается произвольным файлом (`echo x > /tmp/e.txt` достаточно), и в сочетании с MINOR-1 — на любом хосте.
- Влияние: само по себе активацию не даёт (нужны ещё fingerprint/review/verify/human gate), но ослабляет evidential ценность gate-отчёта.
- Рекомендация: в следующей ревизии требовать `evidence_ref` внутри `<raw_root>/<execution-id>/…` и/или сверку digest в manifest; при исполнении на U1 связывать с artifact-manifest-run.

### NOTE-1 — Evidence activation-check не самодостаточен: не фиксирует команду; зафиксирован в event 0002
- Воспроизведение показало: committed `dev-host-activation-refused.json` (11 unmet, без строк review/verify/human-gate) получается ТОЛЬКО с флагами `--review-verdict PASS --verify-verdict VERIFIED --human-gate-approved`; без флагов код выдаёт 14 unmet (добавляются «fresh review verdict None != PASS», «fresh verify verdict None != VERIFIED», «human gate not approved»). Флаги были гипотетическими параметрами для изоляции gate/fingerprint-отказа; они честно записаны в `command_refs` event 0002, и повтор по этой команде даёт байт-совпадение (кроме `decided_utc`). Заголовок commit-сообщения «11 unmet preconditions» без упоминания флагов вводит в заблуждение о поведении по умолчанию. Рекомендация: embed CLI-команды в сами evidence-файлы.

### NOTE-2 — Ledger без tamper-evidence
- Прямая правка JSONL (удаление строки с attempt_id) сделает переиспользование id необнаружимым самим инструментом (хеш-цепочки нет; инструмент доверяет файлу). Через API инструмента переиспользование обнаруживается двойным барьером (executor pre-check + ledger.append). Кросс-чек ledger ↔ raw-дерево (незанятые id при наличии raw-каталогов) кодом не выполняется. Для C0-уровня допустимо; рекомендация — периодический reconcile + digest-цепочка в будущей ревизии.

### NOTE-3 — Hostname deny-list точного совпадения
- `hostname in forbidden` — точное сравнение; FQDN-форма (`outenemy.lab.local`) правило бы обошла. На текущем dev-хосте hostname ровно `outenemy` — работает; рекомендация — сравнивать также short-name (`hostname -s`) / суффиксные формы в следующей ревизии.

### NOTE-4 — Provenance сборки не содержит верифицированный commit
- `provenance_record` кладёт `"source_commit": "resolved-at-execution"` (плейсхолдер): pin верифицируется до сборки (BLOCKED_SOURCE_PIN иначе), но фактический 40-hex commit в provenance-артефакт не встраивается (встраивается tree digest — сильный, но косвенный факт). Рекомендация — записывать результат `verify_pinned_source` в provenance.

## 9. Явные утверждения ревьюера

1. Я независимо получил origin/main = `8205781def7179d6bdfa6eb7ab2a84d46776649c` после `git fetch --all --prune` и подтвердил, что base ветки == origin/main, цепочка линейна (4 коммита), handoff-дельта ровно как заявлена.
2. Я прочитал все 8 модулей `scripts/r2/` (1361 строка) и весь тестовый файл (638 строк) целиком; выводы об инвариантах сделаны из кода и собственных прогонов, не из описаний.
3. Все 6 заявленных machine-инвариантов подтверждены кодом, тестами и CLI-прогонами; mutation-проверки (A/B/C) показали, что тесты падают при удалении инвариантов.
4. Все committed evidence-файлы воспроизведены на dev-хосте outenemy; 4 из 5 байт-совпадают, пятый совпадает по команде из event 0002 (NOTE-1).
5. Никаких scientific runs, oxDNA-вызовов, секретов, сетевых вызовов, изменений NL5/NL6 статусов, глобальных surfaces и существующих execution-каталогов в ветке нет; статусы границ (WAITING_HOST/NOT_ACTIVE/NOT_ASSIGNED/HARD_BLOCKED) не изменены ни в одном surface.
6. Findings MINOR-1/MINOR-2 не обнуляют ценности tooling для C0-цели и не создают пути к активации R2 без Human Gate; они подлежат repair-ревизии или явному re-scoping'у документации до/при фактической активации U1.
7. Верификация фактического исполнения на U1 (systemd-launcher, сборка oxDNA, gates/NC) вне этого review и честно помечена имплементёром как не выполненная; я это подтверждает по коду и тестам (systemd-run путь — argv-строитель; исполнение только через CLI-guard на eligible-хосте).

## 10. Независимые валидации (команды, фактические результаты)

```text
git -C /home/rdpuser/NanoLab/main fetch --all --prune                          # ok
git rev-parse origin/main                                                      # 8205781def7179d6bdfa6eb7ab2a84d46776649c
git rev-parse origin/infra/infra3-native-ubuntu-r2-activation-r1               # df6c2122cbdf60cebc9e6aa8348aea12685f9d00
git rev-parse 9a6fb62^{tree}                                                   # 0c73f85be4eb932ee071517914aa21dc2347273e
git diff --name-only 8205781..df6c212                                          # 25 файлов, все ⊂ allowed_paths
PYTHONPATH=scripts python3 -m pytest tests/test_r2_activation_tooling.py -q    # 52 passed
python3 -m pytest tests/ -q                                                    # 426 passed
PYTHONPATH=scripts python3 -m r2.cli check-host                                # NOT_ELIGIBLE, exit 2
PYTHONPATH=scripts python3 -m r2.cli build-engine --src … --build-dir …        # BLOCKED_HOST, exit 2
PYTHONPATH=scripts python3 -m r2.cli run --spec … --ledger …                   # BLOCKED_HOST, exit 2, ledger не создан
PYTHONPATH=scripts python3 -m r2.cli gate --gate U1 --status PASS --evidence ''# REJECTED, exit 3
PYTHONPATH=scripts python3 -m r2.cli activation-check --report <fresh>         # exit 2, r2_activated=false, 14 unmet
PYTHONPATH=scripts python3 -m r2.cli activation-check --report <fresh> --review-verdict PASS --verify-verdict VERIFIED --human-gate-approved
                                                                               # exit 2, 11 unmet == committed evidence
PYTHONPATH=scripts python3 -m r2.cli gate --status PASS --evidence <непустой>  # на outenemy: RECORDED exit 0  → MINOR-1
PYTHONPATH=scripts python3 -m harness.cli check-consistency                    # ok: true
PYTHONPATH=scripts python3 -m harness.workflow_lint                            # blocking: 0
python3 scripts/harness/work_cli.py validate docs/work/executions/EX-INFRA3-NATIVE-UBUNTU-R2-R1
                                                                               # ok, HANDOFF_READY, terminal present
python3 (jsonschema Draft202012: 4 events + passport против schema.v1)         # VALID ×5
mutations A/B/C в copies + git checkout --                                     # тесты ловят (1/2/3 FAIL соответственно)
```

## 11. Verdict

**PASS** — при условиях: findings MINOR-1/MINOR-2 учесть repair-ревизией (или явной doc-ревизией формулировок) до либо при фактической активации на U1; NOTE-1..NOTE-4 — в бэклог. Merge остаётся Human Gate. R2 остаётся `WAITING_HOST / NOT_ACTIVE`, `AUTHOR_U1 = NOT_ASSIGNED`, gates/NC `WAITING_HOST`, claim `C0_SOFTWARE_ONLY` не превышен.

— FRESH REVIEWER (CONTROL), 2026-09-30, worktree `review-infra3-r2-activation` @ df6c2122cbdf60cebc9e6aa8348aea12685f9d00

---

## Review refresh R1 (post-repair) @ c12b88b

- Дата: 2026-09-30 (UTC)
- Refresh-объект: repair R1 ветки `infra/infra3-native-ubuntu-r2-activation-r1` — substantive `7a357b1` + reclassification `c12b88b8b290592c5357755aa1844af007a0121e` (post-repair HEAD), поверх df6c212; review-база моего первичного вердикта — 89fdbb0.
- Метод: `git fetch --all --prune`; ff-only merge в review-ветку невозможен (review-ветка дивержировала моим вердикт-коммитом 89fdbb0 — by design), поэтому c12b88b верифицирован в detached worktree на exact HEAD; вердикт-файл дополняется на моей review-ветке.

### Scope repair-дельты (измерено)

`git diff --name-status df6c212..c12b88b` (по коммитам 7a357b1 + c12b88b): ровно `scripts/r2/{cli,engine_build,fingerprint,gates}.py`, `tests/test_r2_activation_tooling.py`, `summary.md` (errata §6, append), `WO-INFRA3-R2-ACTIVATION-R1.md` (errata §8, append), `events/0005-repair-r1-completed.json` (A в 7a357b1, M в c12b88b — reclassification), `evidence/repair-r1-gate-pass-BLOCKED_HOST.json` (A). Посторонних файлов нет; WORK_QUEUE/infra-plan/config/passport/state-файлы не тронуты. (В diff `89fdbb0..c12b88b` дополнительно виден только `D` моего вердикт-файла — артефакт сравнения дивергированных веток, не действие repair.)

### Finding → fix → подтверждение (все измерено на exact c12b88b, dev-хост outenemy)

| Finding | Fix в repair R1 | Подтверждён |
|---|---|---|
| MINOR-1 (guard покрытие) | `require_u1_or_exit` добавлен в `gate` и `nc-verify`; точное покрытие задокументировано в WO errata §8 + summary errata §6(1): build-engine/run/gate/nc-verify = U1-only; fingerprint/check-host/nc-plan/report/activation-check = read-only/аналитика | ДА: мой собственный repro — `gate --report /tmp/x.json --gate U1 --status PASS --evidence <непустой файл>` на outenemy → **BLOCKED_HOST exit 2**, файл отчёта НЕ создан; `nc-verify` → BLOCKED_HOST exit 2; build-engine → exit 2; committed `evidence/repair-r1-gate-pass-BLOCKED_HOST.json` байт-совпадает с текущим поведением |
| MINOR-2 (evidence provenance) | `GateReport.set_status('PASS')` записывает `evidence_sha256` (sha256 файла) + `evidence_size` — PASS пинует конкретный контент | ДА: код (`gates.py`), тест (`test_pass_requires_existing_nonempty_evidence` — assert на sha256/size), независимый API-repro в tmp (digest совпал с `hashlib.sha256`). Расположение внутри raw-дерева — честно отложено как future hardening |
| NOTE-1 (evidence не самодостаточен) | `invocation` (полная command line) добавлена в outputs `gate` (RECORDED), `nc-verify`, `activation-check`; ранее опубликованные evidence не перезаписываются (errata §6(5)) | ДА: код cli.py (3 точки emit); BLOCKED_HOST-evidence без invocation соответствует фактическому выводу guard-пути |
| NOTE-2 (ledger tamper-evidence) | Не фиксится; явно задокументировано как future hardening (summary errata §6(6)) | ДА (честный defer, а не молчаливый пропуск) |
| NOTE-3 (hostname deny-list) | Сравнение full-name И short-name, case-insensitive (`fingerprint.py`) | ДА: `outenemy.lab.local` → ineligible с named-причиной; `OUTENEMY` → ineligible; тест `test_outenemy_fqdn_form_also_rejected` |
| NOTE-4 (provenance commit) | `provenance_record(source_commit=verified)` из CLI (`actual_commit` после `verify_pinned_source`) + флаг `source_commit_verified` | ДА: код + тест (verified → 40-hex pin + `source_commit_verified=True`; без верификации → плейсхолдер + `False`) |

### Machine-проверки на exact c12b88b (независимый прогон)

- `PYTHONPATH=scripts python3 -m pytest tests/test_r2_activation_tooling.py -q` → **53 passed** (+1 к моим 52: FQDN-тест; gate/nc-verify CLI-тесты переписаны host-условными без ослабления: на eligible-хосте по-прежнему требуют REJECTED/pass-логику)
- `python3 -m pytest tests/ -q` → **427 passed** (374 канонических + 53)
- `check-consistency` → ok:true; `workflow_lint` → blocking=0
- `work_cli validate docs/work/executions/EX-INFRA3-NATIVE-UBUNTU-R2-R1` → ok:true, `has_terminal_handoff: true`, **`has_post_terminal_corrections: true`** — честно отражает post-terminal event 0005
- jsonschema Draft202012: все 5 событий (0001–0005) VALID; timestamps монотонны (…14:51:50Z < 0005 15:16:11Z); event 0005 = CONTINUATION_CHECKPOINT (reclassification c REPAIR_COMPLETED после терминала — сам инцидент и фикс честно в истории коммитов; валидатор это принимает и помечает)
- Scope/passport: passport_sha256 не изменился (73caa3cf…), статус HANDOFF_READY; статусы границ не тронуты

### Refresh-вердикт

**PASS** — repair R1 закрывает MINOR-1 и MINOR-2 фактически (не редактурой), смягчает NOTE-1, закрывает NOTE-3/NOTE-4, NOTE-2 честно defer'нут. Все 6 machine-инвариантов подтверждены заново на c12b88b; новых findings не обнаружено. Оставшиеся открытые пункты (в бэклог, не блокируют): raw-tree binding для gate evidence, ledger tamper-evidence (hash-chain/reconcile), `SystemdTransientLauncher.run` остаётся stub'ом (вне repair-scope; задокументированное ограничение — CLI default `--launcher systemd` на U1 потребует либо stub-removal, либо `--launcher direct`; рекомендация зафиксирована в первичном вердикте). Merge остаётся Human Gate; R2 остаётся `WAITING_HOST / NOT_ACTIVE`.

— FRESH REVIEWER (CONTROL), refresh R1, 2026-09-30, верификация на detached worktree @ c12b88b8b290592c5357755aa1844af007a0121e
