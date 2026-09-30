# EX-INFRA3-NATIVE-UBUNTU-R2-R1 — Summary

```text
execution_id = EX-INFRA3-NATIVE-UBUNTU-R2-R1
work_order   = WO-INFRA3-R2-ACTIVATION-R1 (child of WO-NATIVE-UBUNTU-EXECUTOR-R1 / INFRA3-003)
branch       = infra/infra3-native-ubuntu-r2-activation-r1
base         = 8205781def7179d6bdfa6eb7ab2a84d46776649c (origin/main)
substantive_head = 9a6fb6248d697350c2e218d8bbadb34e2177bc8b
risk / claim = MEDIUM / C0_SOFTWARE_ONLY (infrastructure tooling; НЕ научный WO)
status       = HANDOFF_READY (fresh Reviewer + fresh Verifier -> Human Gate)
```

## 1. Что сделано

Реализован исполняемый R2 activation tooling — подготовка к механической
активации R2 после выделения U1 (см. `WO-INFRA3-R2-ACTIVATION-R1.md` §2):

1. `scripts/r2/contract.py` — run contract: attempt id `<run_base>` |
   `<run_base>-R<n>`, append-only ledger c запретом переиспользования attempt id
   (включая после FAILED_TECHNICAL), technical outcome отдельно от scientific
   (`NOT_EVALUATED` на этом слое всегда), artifact manifest
   (path/sha256/size/producer/retention) + digest.
2. `scripts/r2/fingerprint.py` — capture 15 fingerprint-команд + парсеры +
   `validate_native_u1` (native kernel, virt=none, не-WSL, native ФС
   ext4/xfs/btrfs, systemd, hostname вне запрещённых — `outenemy` никогда не
   проходит) + детерминированный markdown-блок для будущего §10 контракта R2.
3. `scripts/r2/executor.py` — `RunExecutor`: direct launcher (dev-тесты) и
   systemd-run transient launcher (argv-builder чистый; исполнение только через
   CLI-guard на eligible U1); raw
   `<raw_root>/<execution-id>/<attempt-id>/` с stdout/stderr/exit.json/artifact
   manifest; nonzero exit / timeout / deliberate kill → `FAILED_TECHNICAL`
   с сохранением попытки; retry получает новый id (S001 → S001-R1).
4. `scripts/r2/supervisor.py` — transient service/scope argv builders,
   `is-active` парсер, CI lifecycle violation detector (systemctl
   reboot/shutdown/kill executor cgroup), чистые NC-U1..U5 evaluators.
5. `scripts/r2/gates.py` — GateReport U1–U5 + NC-U1..U5: WAITING_HOST→PASS|FAIL,
   PASS только с существующим непустым evidence-файлом; `activation_decision`:
   `R2_ACTIVATED = YES` вычислим только при all gates PASS ∧ all NC PASS ∧
   frozen native-eligible fingerprint ∧ fresh review PASS ∧ fresh verify
   VERIFIED ∧ human gate approved — policy-инвариант зашит кодом.
6. `scripts/r2/engine_build.py` — pinned oxDNA source check
   (`00dc7fb9…`), configure/build argv (Release/DOUBLE=ON/CUDA=OFF/MPI=OFF),
   CMakeCache pin verification, binary sha256+size, source tree digest,
   provenance record (`binary_sha_equality_with_r1_required = false`).
7. `scripts/r2/cli.py` — fingerprint/check-host безопасны на любом хосте;
   build-engine/run/gate/report/activation-check/nc-plan/nc-verify отказывают
   на не-eligible хосте (exit 2 `BLOCKED_HOST`), без silent fallback.
8. `config/infra/r2-activation.v1.json` — machine-readable pins/policy,
   согласованы с кодом (ConfigContractTest).
9. `tests/test_r2_activation_tooling.py` — 52 теста; полный набор 426 passed.
10. Surface sync: WORK_QUEUE (INFRA3-003 append), project/infra-plan.json
    (note INFRA3-003 append). Статусы границ не менялись.

## 2. Негативные контроли tooling (записаны на dev-хосте outenemy)

- `check-host` → `NOT_ELIGIBLE` exit 2: единственная причина — hostname
  forbidden (хост нативный; это согласуется с ролью outenemy = внешняя
  платформа репродукции U2, но author-хостом он не становится).
- `build-engine` → `BLOCKED_HOST` exit 2.
- `gate U1 PASS` без evidence → `REJECTED` exit 3.
- `activation-check` (review PASS + verify VERIFIED + human gate, но gates
  WAITING_HOST и без fingerprint) → `r2_activated = false` exit 2 (11 unmet).

## 3. Чего НЕ сделано (честно)

- Машина U1 не выделена (`AUTHOR_U1 = NOT_ASSIGNED`,
  `R2_STATUS = WAITING_HOST / NOT_ACTIVE`): gates U1–U5 и NC-U1..U5 НЕ
  исполнялись, fingerprint R2 не снимался, oxDNA не собирался, никаких
  scientific runs.
- systemd-исполнение launcher не валидировалось (доступно только на eligible
  U1 by design; argv-строители покрыты unit-тестами).
- `project/state.json`, `project/infra-state.json`, научная история,
  `ENGINE_ENVIRONMENT_R1.md`, существующие execution-каталоги — не тронуты.
- Runner не регистрировался; secrets нет; платный compute нет.

## 4. Валидация этой ветки

- `python3 -m pytest tests/ -q` → 426 passed (374 canonical + 52 новых).
- `check-consistency` → ok:true; `workflow_lint` → blocking=0.
- `work_cli validate docs/work/executions/EX-INFRA3-NATIVE-UBUNTU-R2-R1` → ok.
- CLI negative controls — см. §2 (файлы в `evidence/`).

## 5. NEXT_ACTION

Fresh Reviewer + fresh Verifier на exact HEAD этой ветки → Human Gate (merge).
Отдельно, вне этого WO: owner выделяет U1 → на U1 механически: fingerprint →
build-engine → gates U1–U5 → NC-U1..U5 → activation-check → review/verify →
Human Gate активации R2 (порядок и условия —
`ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` §9, policy §1).

## 6. Errata (repair R1, после fresh review PASS @ 89fdbb0)

Fresh review (`docs/infra/evidence/INFRA3-R2-ACTIVATION-R1/REVIEWER_VERDICT.md`,
PASS, 2 MINOR + 4 NOTE) вскрыл неточности и пробелы; repair (event 0005):

1. §1(7) этого summary и WO §2(инвариант 1) заявляли host-guard шире
   фактического. Точное покрытие ПОСЛЕ repair: `build-engine`, `run`,
   `gate`, `nc-verify` — U1-only (BLOCKED_HOST exit 2 вне eligible-хоста);
   `fingerprint`, `check-host`, `nc-plan`, `report`, `activation-check` —
   read-only/аналитика, безопасны на любом хосте.
2. Gate PASS теперь привязывает содержимое evidence (`evidence_sha256`,
   `evidence_size`), а не только путь; требование расположения evidence
   внутри raw-дерева — future hardening (NOTE).
3. Hostname deny-list сравнивает full-name и short-name (FQDN-форма
   `outenemy.*` также отклоняется).
4. Build provenance содержит верифицированный source commit
   (`source_commit` + `source_commit_verified`), а не плейсхолдер.
5. CLI outputs (`gate`, `nc-verify`, `activation-check`) несут `invocation`
   (полная command line) — evidence самодостаточнее; ранее опубликованные
   evidence-файлы остаются историческими фактами ревизии 9a6fb62 и не
   перезаписываются.
6. Ledger tamper-evidence (hash-chain/внешний reconcile) — задокументировано
   как future hardening, не входит в repair R1.

Тесты после repair: 53 tooling / 427 full, все зелёные.
