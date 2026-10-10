# DIRECTOR_FRESH_AUDIT_R1 — Director fresh audit: NL5 v0.2 FROZEN_R2 chain + R2 activation readiness

```text
RECORD_ID          = NL5-V02-FREEZE/DIRECTOR_FRESH_AUDIT_R1
RECORD_KIND        = DIRECTOR_FRESH_AUDIT
ISSUER_CLASS       = DIRECTOR
AUDIT_DATE         = 2026-10-10
BASE_MAIN_HEAD     = 8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad (origin/main, fresh fetch)
BASE_MAIN_TREE     = 0eba7b901ab9991cca6b9439df227d71a90a82df
AUDIT_BRANCH       = control/nl5-v02-fresh-audit-r1
EXECUTION          = EX-NL5-V02-FRESH-AUDIT-R1
WORK_ORDER         = WO-NL5-V02-FRESH-AUDIT-R1

CHAIN_VERDICT      = INTACT (S → F → D → R → V verified fresh on exact Git objects)
R2_VERDICT         = WAITING_HOST / NOT_ACTIVE — HARD BLOCKER: U1 NOT AVAILABLE
SCIENTIFIC_RUNS    = 0 (no confirmatory run authorized or executed)
CANONICAL_CHANGES  = NONE (no canonical status changed by this audit)
```

## 1. Назначение

Central-agent mission «NL5 FINAL CLOSURE» требует: fresh fetch, fresh audit
фактического состояния, попытку реальной активации R2 и — если U1 отсутствует —
максимально полный activation package с точным препятствием и честным
WAITING_HOST. Этот record — durable результат этого аудита. Он ничего не
активирует и не меняет канонические статусы.

## 2. Verified authority chain (fresh fetch 2026-10-10)

Все проверки выполнены в этом сеансе на свежем fetch; команды и сырые выводы —
в `docs/work/executions/EX-NL5-V02-FRESH-AUDIT-R1/evidence/`.

```text
S  HG-B APPROVED        = docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.{md,json}
                          (decision_id NL5-ACCEPTANCE-POLICY/HG-B/R1; canonical main
                          3b0dd01e... на момент решения; merge PR #50)
F  FROZEN PACKAGE F2    = commit 60da9a846511265a8ac7564da088c3d74cb073f0
                          tree  e565c8a6cee9e829fac14008ebc9c2ea1609931d
                          (rev-parse ^{tree} = exact; F2 входит в историю main)
D  Director FREEZE R2   = a2f7304ebbb5973b81cf49dee60c21c85c6a974d
                          (merge-base --is-ancestor F2 D → strict descendant;
                          pins exact artifact blobs/digests — сверены ниже)
R  fresh Reviewer(F2)   = PASS; branch review/nl5-v02-frozen-r2-scientific-review-r1
                          tip d63eb5c088133f92ebd20501835a159cc3e4b865;
                          REVIEWED_HEAD = F2, REVIEWED_TREE = F2_TREE (из тела verdict);
                          tip является потомком F2 (ancestry проверен)
V  fresh Verifier(F2)   = VERIFIED; branch verify/nl5-v02-frozen-r2-r1
                          tip f12d0b497cb28a2f18476ded90b4b1bd079bb414;
                          VERIFIED_HEAD/TREE = F2 exact; независимая reproduction
                          605 tests + M-1 matrix + pinned scan re-run;
                          tip является потомком F2 (ancestry проверен)
```

Frozen artifact digests (Git blob bytes at F2, пересчитаны в этом сеансе,
совпадают с Director FREEZE R2 record и с FRESH_VERIFIER_R2):

```text
protocol    docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md
            blob 4835719622bae49a8e8b480536a482b4b222d408
            sha256 2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d
contract    .../EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-freeze-contract-FROZEN_R2.json
            blob d6a9ccde4d1dadf42d1a8cd9b88faa02646cf70b
            sha256 7e6476544e82af73d5d7e0672666ece99bf4d499a0da30645b02886bcdc45b3a
seed record .../EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-seed-record-FROZEN_R2.json
            blob 0164e0e3f5dda6dbf63174df3730b1bd921d2c76
            sha256 8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28
```

Вывод §2: chain `S → F → D / R / V` цел; единственный отсутствующий элемент
lifecycle — `A` (dispatch authority schema v3), который по конструкции требует
`r2_record` с R2 ACTIVE и потому не может существовать до активации R2.

## 3. Машинные гейты (fresh run в этом сеансе)

```text
freeze contract gate  = PASS / PREFREEZE_VALIDATION_PASS / DISPATCH_BLOCKED
                        (scripts/nl5/repro_v02_freeze_contract.py, pinned
                        collision-scan re-run выполнен gate'ом; fail-closed
                        dispatch_blockers перечислены машиной корректно)
                        evidence: evidence/frozen-gate-PASS-audit-R1.json
feasibility N-grid    = SELECTED_N = 64 (bit-exact воспроизведение §10.1:
                        N=64 → 0b 0.071 / 32b 0.736 ≤ 0.80; строки 40/48 FAIL
                        сохранены) на committed R1 planning data
                        (sha256 источника 2b0df07deb62add3… зафиксирован)
                        evidence: evidence/feasibility-n-grid-audit-R1.json
harness suite         = 605 tests OK (58.6 s) — совпадает с числом верификации F2
check-consistency     = ok (branch control/nl5-v02-fresh-audit-r1)
workflow_lint         = blocking = 0
```

Mandatory feasibility gate: **PASS** — dispatch-инвариант §10.3 выполнен на
актуальных допустимых planning inputs.

## 4. R2 / U1 probe (точное препятствие)

Полная инвентаризация — `evidence/u1-host-search-R1.json`; negative control
`check-host` на этом хосте и честное machine-решение активации:

```text
r2 check-host (outenemy) = NOT_ELIGIBLE (hostname forbidden: EXTERNAL_U2_ONLY)
activation decision      = r2_activated=false; WAITING_HOST / NOT_ACTIVE;
                           author_u1=NOT_ASSIGNED; 14 unmet preconditions
                           (evidence/r2-activation-decision-WAITING_HOST-audit-R1.json)
```

Кандидаты U1 (все проверены в этом сеансе):

```text
outenemy (этот хост; Ubuntu 22.04.5 native, virt=none, 64 threads)
         → FORBIDDEN_AS_U1 (owner decree: EXTERNAL_U2_ONLY; физически = U2)
192.168.0.19  → Windows-хост (SMB/RDP, SSH отсутствует) — NOT_ELIGIBLE
192.168.0.27  → SSH 22 открыт, publickey отклонён для
                rdpuser/nanolab/ubuntu/root/ape/nobody единственным доступным
                ключом; парольных кредов нет → BLOCKED_NO_CREDENTIALS
прочие LAN    → открытых портов нет
локальные VM/LXD на outenemy → та же физическая машина, что U2 → FORBIDDEN
```

**HARD BLOCKER:** ни один хост не удовлетворяет контракту U1
(`ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` §2: независимая физическая машина,
native Ubuntu/ext4/systemd, hostname не в forbidden list, креды доступны).
По owner decree активация не может быть сымитирована: `AUTHOR_U1 = NOT_ASSIGNED`,
`R2 = WAITING_HOST / NOT_ACTIVE` — честные канонические статусы.

Минимальное действие владельца: выделить/назначить один независимый native
Ubuntu host (никогда outenemy, никогда VM/LXD на outenemy) и опубликовать его
SSH-доступ для executor-сессии.

## 5. Что уже готово для немедленной активации (activation package)

1. Tooling: `scripts/r2/*` merged в main (fingerprint, check-host,
   build-engine, run contract + append-only ledger, systemd executor,
   gates U1–U5, NC-U1..U5 plan/verify, activation decision machine) —
   протестирован (test_r2_activation_tooling в 605-suite).
2. Machine contract: `config/infra/r2-activation.v1.json` (engine pin
   `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`; CPU/DOUBLE=ON/CUDA=OFF/MPI=OFF;
   canonical paths; host eligibility; process isolation; raw evidence manifest).
3. Frozen научный пакет F2: готов и проверен (§2); seeds/contract заморожены,
   replacement pools frozen, campaign identities deterministic.
4. Научный WO-скелет кампаний объявлен протоколом §12:
   `EX-NL5-REPRO-V0-2-U1-R1` (author) + `EX-NL5-REPRO-V0-2-U2-R1` (external).

## 6. Activation runbook (механическая последовательность после выделения U1)

```bash
# 0) на U1: ssh <u1>, cd ~/src/NanoLab, git fetch --all --prune
# 1) fingerprint + eligibility
PYTHONPATH=scripts python3 -m r2.cli fingerprint --out ~/nanolab/u1-fingerprint.json
PYTHONPATH=scripts python3 -m r2.cli check-host            # должен быть eligible
# 2) U1 gate: чистая сборка oxDNA (pin 00dc7fb9…)
PYTHONPATH=scripts python3 -m r2.cli build-engine --src <oxdna-src> --build-dir <dir> --jobs <n>
# 3) U2..U5 gates + evidence-binding
PYTHONPATH=scripts python3 -m r2.cli gate --report <report> --gate U2 --status PASS --evidence <file>
# 4) negative controls NC-U1..U5 (план/verify)
PYTHONPATH=scripts python3 -m r2.cli nc-plan --nc NC-U1
PYTHONPATH=scripts python3 -m r2.cli nc-verify --nc NC-U1 --evidence <file>
# 5) machine decision
PYTHONPATH=scripts python3 -m r2.cli activation-check --report <report> \
  --fingerprint ~/nanolab/u1-fingerprint.json
# 6) fresh Reviewer + fresh Verifier activation package (новые bounded WO)
# 7) HG-A owner decision (Human Gate; без него R2 НЕ переводится в ACTIVE)
# 8) R2 ACTIVE фиксация в canonical surfaces; затем dispatch authority v3 (A)
#    (scripts/nl5/repro_v02_freeze_contract.py plan --authority <record>;
#     machine_launch_authorized остаётся false — launch = HUMAN_PROTECTED_WRITER)
# 9) отдельное owner-разрешение запуска → campaign legs U1/U2
```

Все шаги (6)–(9) требуют новых независимых ролей/решений и не могут быть
выполнены одной сессией Director (независимость review/verify + Human Gates).

## 7. Границы этого record

- Этот audit НЕ активирует R2, НЕ назначает U1, НЕ авторизует scientific runs,
  НЕ создаёт dispatch authority, НЕ меняет state.json/WORK_QUEUE статусы
  границ (только surface-sync строка самого audit WO).
- Fingerprint outenemy в evidence — audit-time capture для будущей U2-ноги
  кампании; campaign fingerprint U2 фиксируется отдельно в момент кампании.
- Исторический NL5-002 MISMATCH и PLATFORM_INSENSITIVE не пересматриваются.
- `NL5 = IN_PROGRESS`, `NL6-001 = LOCKED`, `external_reproductions = 0`,
  `machine_launch_authorized = false` — без изменений.
