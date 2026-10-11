# Summary — EX-INFRA3-U2-OUTENEMY-READINESS-R1

WO: `WO-INFRA3-U2-OUTENEMY-READINESS-R1` · ветка:
`infra/u2-outenemy-executor-readiness-r1` · base main `8bf7e3a` (merge PR
#52) · финальное состояние на handoff: `b87d61d1a101e8b85415a079288efa46384be201`
(включая tooling-repair R1) · 0 scientific runs · claim ceiling
C0_SOFTWARE_ONLY · PR #55.

## Что сделано

1. **Host-role зафиксирован машинно**: `outenemy` = закреплённое U2/P-B плечо
   по FROZEN_R2 §5 (native Ubuntu 22.04.5, `systemd-detect-virt=none`,
   Linger=yes); `r2 check-host` = NOT_ELIGIBLE — номинальный негативный
   контроль корректен, машина никогда не U1.
2. **P-B build chain**: pinned oxDNA `00dc7fb9` собран собственной цепочкой
   (CPU/Release/DOUBLE=ON/CUDA=OFF/MPI=OFF), binary `6effd00a…` воспроизведён
   байт-в-байт чистой пересборкой (~67 s), полный provenance через
   `scripts/r2/engine_build.py` (U1 CLI guard не обходился).
3. **Технический smoke движка** (HAIRPIN, 2000 steps): exit 0, finite
   outputs — НЕ научное утверждение.
4. **Release package v0.1.1**: свежий git-archive self-test → plan 5/5 ok;
   verify fail = ровно 7 documented pyc findings → подготовлен bounded
   packaging repair v0.1.2 (ветка `work/nl5-v012-packaging-pyc-repair-r1`,
   PR #56).
5. **systemd mechanics**: `systemd-run --user` RC 0 + journal persist;
   system manager требует root → U2-нога использует user manager.
6. **Storage**: `~/nanolab/{workspaces,raw,cache,tools}`; raw-проекция
   ~15 GB на U2-ногу (запас ~2x; порог контроля 80%).
7. **Tooling repairs** (science untouched): F-1 engine binary path, F-2
   CMakeCache реальная грамматика, F-3 `systemd-run --user` opt-in;
   **scope-repair**: покрытие F-1..F-3 выделено в отдельный bounded
   `WO-INFRA3-R2-TOOLING-REPAIR-R1` (та же ветка; история и START этого
   execution сохранены — см. событие 0003); F-4 неоднозначный binary →
   fail-closed; **U2-dispatch path** `r2.cli run-u2` подготовлен и проверен
   end-to-end на disposable технических fixtures (обязательная dispatch
   authority schema v3; fixture ceiling; launch gate
   HUMAN_PROTECTED_WRITER не подменяется; frozen campaign id — отказ).

## Валидация (host outenemy)

- Полный unittest набор: **630 OK** (612 base + 18 новых регрессионных).
- `work_cli validate` — ok (оба исполнения ветки); `check-consistency` ok;
  `workflow_lint` blocking=0; hosted CI — на push (PR #55 head).
- Evidence: `u2-fingerprint-R1.json`, `u2-check-host-BLOCKED-R1.json`,
  `u2-engine-build-provenance-R1.json`, `u2-engine-build-result-R1.json`,
  `u2-engine-smoke-R1.json`, `u2-release-package-selftest-R1.json`,
  `u2-systemd-mechanics-R1.json`, `u2-dispatch-fixture-selftest-R1.json`.

## Границы на handoff (НЕ изменены)

R2 = WAITING_HOST / NOT_ACTIVE · AUTHOR_U1 = NOT_ASSIGNED · NL5 =
IN_PROGRESS · external_reproductions = 0 · SCIENTIFIC_RUNS = 0 · F2/frozen
artifacts не тронуты · canonical статусы не менялись · real dispatch
authority не создавался · merge = Human Gate (PR #55).

## Open risks

- Машина разделяется с посторонними нагрузками (microk8s/docker; ~26 GiB RAM
  available на момент аудита) — WO кампании обязан зафиксировать budget.
- U1 остаётся неназначенным — единственный hard blocker R2-активации.

## Next action

Fresh independent Reviewer на exact branch HEAD/TREE → narrow repair при
находках → fresh independent Verifier на финальный exact HEAD/TREE; затем
owner Human Gate на PR #55.
