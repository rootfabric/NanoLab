# U2_OUTENEMY_EXECUTOR_READINESS_R1 — Техническая готовность внешней платформы воспроизведения (U2, outenemy)

Статус: **TECHNICALLY_READY — AWAITING_AUTHORITY_CHAIN** (2026-10-10).
Execution: `EX-INFRA3-U2-OUTENEMY-READINESS-R1`; WO:
`WO-INFRA3-U2-OUTENEMY-READINESS-R1`; ветка
`infra/u2-outenemy-executor-readiness-r1`; base main `8bf7e3a`.

> Этот документ фиксирует **машинные факты готовности U2-плеча** кампании
> `NANOLAB_REPRO_V0_2_DISTRIBUTIONAL` (FROZEN_R2, §5: P-B = U2 outenemy). Он
> НЕ активирует R2, НЕ назначает U1, НЕ меняет canonical статусы и НЕ
> разрешает ни одного confirmatory запуска. Dispatch кампании U2 остаётся
> ЗАКРЫТ до: R2 ACTIVE (U1-нога) → dispatch authority v3 → Human Protected
> Writer Gate.

## 1. Идентификация машины (машинный fingerprint)

```text
hostname            = outenemy
OS                  = Ubuntu 22.04.5 LTS (jammy), kernel 5.15.0-190-generic
virtualization      = none (systemd-detect-virt = none; нативная физмашина)
systemd             = available (system + user manager, Linger=yes для uid 1001)
CPU                 = 2x Intel Xeon E5-2698 v3 @ 2.30GHz (32 ядра / 64 потока, NUMA x2)
RAM                 = 125 GiB total; на момент аудита ~26 GiB available
                      (машина РАЗДЕЛЯЕТСЯ с посторонними нагрузками: microk8s,
                      docker, load average ~14.5; budget кампании обязан это
                      учитывать — см. §7)
filesystem          = ext4 (нативный, /dev/nvme0n1p2), /mnt/gig ext4 (nvme1n1)
toolchain           = gcc/g++ 11.4.0, cmake 3.22.1, GNU Make 4.3,
                      python 3.10.12, git 2.34.1
r2 fingerprint      = docs/work/executions/EX-INFRA3-U2-OUTENEMY-READINESS-R1/
                      evidence/u2-fingerprint-R1.json
r2 check-host       = NOT_ELIGIBLE — hostname 'outenemy' forbidden as author
                      host (external reproduction platform only) — НАМИНАЛЬНЫЙ
                      НЕГАТИВНЫЙ КОНТРОЛЬ: машина закреплена как U2 и НЕ
                      является U1 (политика NATIVE_UBUNTU_EXECUTION_POLICY_R1)
```

Свежий полный fingerprint U2 отдельно от author-машины — требование FROZEN_R2
§5 («свежий fingerprint фиксируется отдельно») — ВЫПОЛНЕНО.

## 2. Engine build U2 (собственная build-цепочка P-B)

Переиспользован `scripts/r2/engine_build.py` (без второго исполнительного
механизма); CLI-гейт U1 НЕ обходился — авторская команда `r2.cli build-engine`
остаётся U1-only, для U2 выполнена документированная operator-процедура с теми
же функциями provenance (`~/nanolab/tools/u2-engine-build.py`).

```text
source              = lorenzo-rovigatti/oxDNA
pinned commit       = 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591 (verify_pinned_source = TRUE)
source_tree_sha256  = b1742ce91de072c59f4b3febea97647e813b9a5bd23900465bbbf227d22a911c
flags               = CPU; -DCMAKE_BUILD_TYPE=Release -DDOUBLE=ON -DCUDA=OFF -DMPI=OFF
CMakeCache pins     = Release / ON / OFF / OFF — ALL VERIFIED (после ремонта F-2)
binary              = <build>/bin/oxDNA; sha256 6effd00a09628895fac48b8b4c60c4dc82557d05910da6bebe276b8355126b78; size 3 380 728
clean rebuild       = ДЕТЕРМИНИРОВАН: повторная чистая сборка дала байт-в-байт
                      тот же binary sha256; wall ~67 s при -j4
compiler            = gcc/g++ 11.4.0 (другая GCC line относительно R1 допустима:
                      контракт R2 §4/§5)
provenance          = ~/nanolab/cache/oxdna-build-r2-u2/build-r2-u2-provenance.json
                      (+ копия в execution evidence)
build log           = ~/nanolab/cache/oxdna-build-r2-u2/build-r2-u2.log
```

## 3. Технический smoke (НЕ научное утверждение)

```text
basis               = examples/HAIRPIN из pinned source tree (upstream пример),
                      steps сокращены до 2000 — технический smoke, НЕ protocol run
exit                = 0; «END OF THE SIMULATION, everything went OK!»
outputs             = trajectory.dat (4 кадра), energy.dat (значения finite),
                      last_conf.dat; files см. smoke-evidence-r1.json
claim               = C0_SOFTWARE_ONLY: движок исполняется и пишет корректные
                      файлы на этой машине. Никакого научного сравнения не было.
```

## 4. Release package validation (nanolab-components v0.1.1)

```text
метод               = свежий export пакета из git (git archive) в чистый
                      workspace + reproduction/reproduce.py self-test
plan mode           = ok; 5/5 карточек (0b, 11b, 32b, 53b, 74b NOT_MEASURED)
verify mode         = FAIL: ровно 7 ошибок, ВСЕ — отсутствующие
                      convention/nlbl_convention/__pycache__/*.pyc
```

Классификация: это **documented v0.1.1 pyc finding** (контракт
`ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` §6 gate U2: «documented v0.1.1 pyc
findings допустимы; либо bounded packaging v0.1.2 repair»). Причина
установлена точно: `card_lint._package_files()` включает в манифест ВСЁ
содержимое каталога пакета, и при генерации v0.1.1 на author-машине в манифест
попали 7 непитоновско-версионных CPython-артефактов `__pycache__` (в git НЕ
трекаются, в дереве отсутствуют). `reproduce.py verify` на любой свежей копии
завершается exit 3 — fail-closed, внешняя сессия без знания контекста не может
проверить пакет. Отклонений ОТ этого finding не обнаружено (0 non-pyc ошибок).
Подготовлен bounded packaging repair v0.1.2 — см. §8 / Repair Map R-4.

## 5. systemd executor mechanics (survival-механика)

```text
systemd-run --user (transient, --wait --pipe)   = RC 0, unit выполнен, success
systemd-run (SYSTEM manager, без root)          = FAIL: "Interactive
                                                  authentication required."
loginctl Linger (uid 1001)                      = yes
detached --user unit                            = active; journalctl --user
                                                  сохраняет журнал; transient
                                                  unit корректно снят
вывод                                           = U2-нога обязана использовать
                                                  systemd-run --user (Linger=yes
                                                  присутствует); системный
                                                  менеджер требует root
evidence            = evidence/u2-systemd-mechanics-R1.json
```

Session-independence: пользовательский менеджер с Linger=yes переживает
закрытие SSH-сессии — это та же машинная собственность, которую NC-U1/NC-U2
проверяют для U1; полные NC-U1..U5 на U2 будут исполнены в рамках frozen WO
кампании U2 после dispatch (НЕ в этом WO).

## 6. Harness readiness

```text
unit tests          = python3 -m unittest discover -s tests -t .
                      → 605 OK (до ремонтов этого WO) / 612 OK (после; +7
                      регрессионных тестов ремонтов) на этой машине
check-host негативный контроль = корректен (NOT_ELIGIBLE, exit 2)
```

## 7. Raw storage plan (ёмкость на фактических размерах)

Канонические пути созданы: `~/nanolab/{workspaces,raw,cache,tools}`.

Оценка per-run по historical EX-NL5-002-B-R2 (та же машина/платформа):

```text
0b  (200k steps)    traj ~114.7 MB/run
11b (150k)          traj ~115.5 MB/run
32b (150k)          traj ~43.4 MB/run
53b (150k)          traj ~44.0 MB/run
```

Проекция на frozen v0.2 leg (U2-сторона):

```text
primaries  0b  64 x 114.7 MB      ≈ 7.34 GB
           32b 64 x  43.4 MB      ≈ 2.78 GB
controls   11b 10 x 115.5 MB      ≈ 1.16 GB
           53b 10 x  44.0 MB      ≈ 0.44 GB
replacement cap 56 runs           ≈ ≤ 2.3 GB
analysis + manifests             ≈ < 1 GB
ИТОГО raw (worst case)            ≈ ~15 GB на U2-ногу
```

Ёмкость: `/` (home) — 34.5 GB free; `/mnt/gig` — 49.2 GB free, но
root-owned (запись без owner-решения НЕ предполагается). План: raw_root =
`~/nanolab/raw/<execution-id>/` (помещается с ~2x запасом при current
utilisation); контроль заполнения с порогом 80% до dispatch; вторичная копия
на `/mnt/gig` — только отдельным owner-решением. Машина разделяется с
посторонними нагрузками: RAM available ~26 GiB, load ~14.5/64 — WO кампании
обязан зафиксировать budget (одновременность ~2-4 runs, не больше).

## 8. Tooling defects found and repaired (в этой ветке; F2 не изменён)

```text
F-1  engine_build.binary_digest искал только <build>/oxdna; pinned oxDNA
     кладёт бинарники в <build>/bin с engine-регистром (bin/oxDNA) →
     provenance падал на реальной сборке. FIX: resolve_engine_binary()
     (root → bin/имя → единственный case-insensitive match в bin/),
     fail-closed; +2 unit-теста.
F-2  engine_build.parse_cmake_cache парсил синтетический формат
     "KEY:=VALUE"; реальный CMakeCache = "KEY:TYPE=VALUE" → на реальной
     сборке парсер возвращал {} и ВСЕ pins объявлялись missing
     (COMPLETED_WITH_DEVIATIONS ложноположительно). FIX: regex-грамматика
     реального формата, комментарии #/// пустые строки пропускаются; +1
     регрессионный тест на реальном формате; существующие фикстуры
     переключены на реальный формат.
F-3  SystemdTransientLauncher / supervisor argv строили ТОЛЬКО system-manager
     systemd-run, который для non-root оператора требует интерактивной
     root-аутентификации (проверено на этой машине). FIX: явный opt-in
     user_manager=True → "systemd-run --user" (+ CLI launcher choice
     "systemd-user"); дефолт U1 (system manager) не изменён; +3 unit-теста.
R-4  release packaging pyc finding (§4) — подготовлен ОТДЕЛЬНЫЙ bounded
     branch (packaging-only v0.1.2 repair, science byte-identical):
     ветка work/nl5-v012-packaging-pyc-repair-r1, отдельный draft PR.
```

Все ремонты — tooling/infrastructure; научное содержание frozen package F2,
протокола и seed record не затронуто (0 scientific leaves).

## 9. Что осталось для запуска кампании U2 (не в этом WO)

```text
1. R2 ACTIVE на U1-ноге (гл. precondition — физически независимый U1; см. §10)
2. dispatch authority v3 (S → F → D/R/V → A; HUMAN_PROTECTED_WRITER gate)
3. frozen WO кампании с exact launch планом U2-ноги
   (EX-NL5-REPRO-V0-2-U2-R1): 148 confirmatory + replacement pool, seed
   identities из authoritative contract F2, observables через packaged
   convention, budget §7
4. fresh review/verify dispatch-пакета; только потом — первый scientific run
```

## 10. Требование к U1 (точная формулировка, БЕЗ нового LAN scan)

Единственный hard blocker R2-активации остаётся прежним
(`EX-NL5-V02-FRESH-AUDIT-R1/evidence/u1-host-search-R1.json`): нужна
**физически независимая от outenemy машина** — native Ubuntu (не WSL/VM/LXD
на outenemy — это та же физмашина), ext4/xfs/btrfs, native systemd с
возможностью systemd-run для scientific jobs, SSH-доступ для агента
(`~/src/NanoLab`, git fetch), ~50 GB диска и ≥16 GB RAM free под кампанию,
сетевой доступ к github.com. Не подходит: 192.168.0.19 (Windows),
192.168.0.27 (SSH publickey отклоняется для всех проверенных пользователей,
паролей нет), прочие LAN-узлы без открытых портов — по ранее опубликованному
inventory. Роль U1/U2 закреплена FROZEN-политикой и не переносится без
нового протокольного решения.
