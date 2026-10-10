# Work Order WO-INFRA3-U2-OUTENEMY-READINESS-R1 — Техническая готовность U2-исполнителя (outenemy) к кампании v0.2 (без confirmatory runs)

Статус: **IN_PROGRESS** (execution `EX-INFRA3-U2-OUTENEMY-READINESS-R1`, ветка
`infra/u2-outenemy-executor-readiness-r1`, base `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad`
= canonical main HEAD / merge PR #52). Родительская линия: INFRA3 (parallel
capability train; sibling INFRA3-003 `WO-NATIVE-UBUNTU-EXECUTOR-R1` = U1-side,
R2 = WAITING_HOST / NOT_ACTIVE) + NL5 `WO-NL5-V02-DIRECTOR-FREEZE-R2` (FROZEN_R2
ready; кампания U2-ноги = `EX-NL5-REPRO-V0-2-U2-R1`, остаётся ЗАКРЫТОЙ до
полного authority chain). Track: INFRA. Risk: **MEDIUM** (реальные сборки и
systemd-механика на общем рабочем сервере). Claim ceiling: **C0_SOFTWARE_ONLY**.

Дата открытия: 2026-10-10. Trigger: central-agent mission «NL5 — продолжение
работы на существующем сервере» (Case B): агент фактически исполняется на
`outenemy` — закреплённой внешней платформе независимого воспроизведения (U2).
Машина по политике НЕ является U1 (`r2 check-host` = NOT_ELIGIBLE, hostname
`outenemy` forbidden as author host — негативный контроль корректен). Настоящий
WO доводит U2-исполнителя до максимальной технической готовности БЕЗ запуска
какой-либо части confirmatory кампании v0.2.

## 1. Проблема / задача

Frozen protocol `NANOLAB_REPRO_V0_2_FROZEN_R2.md` §5 определяет P-B (external)
= «U2 outenemy, независимая external сессия из release package + frozen WO +
pinned source acquisition; workspace НЕ копируется из author; свежий
fingerprint фиксируется отдельно»; у P-B своя build-цепочка по контракту
`ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` §5. До настоящего WO техническая
готовность именно U2-плеча (build engine, release package, storage, systemd
survival) на фактической машине не проверялась как единый комплект: проверки
2026-10-10 ограничились audit-fingerprint + check-host BLOCKED записью
(`EX-NL5-V02-FRESH-AUDIT-R1`). Задача — закрыть этот пробел механически.

## 2. Scope (allowed paths)

```text
docs/work/WO-INFRA3-U2-OUTENEMY-READINESS-R1.md
docs/work/executions/EX-INFRA3-U2-OUTENEMY-READINESS-R1/**
docs/evidence/INFRA3-U2-READINESS/**
docs/infra/U2_OUTENEMY_EXECUTOR_READINESS_R1.md
docs/work/WORK_QUEUE.md            (одна surface-sync строка U2-readiness WO)
```

## 3. Вне scope (запрещено)

- Любые confirmatory scientific runs: campaign legs
  `EX-NL5-REPRO-V0-2-U1-R1` / `EX-NL5-REPRO-V0-2-U2-R1` закрыты до полного
  authority chain (R2 ACTIVE + dispatch authority v3 + Human Protected Writer
  Gate). Разрешены ТОЛЬКО технические smoke/fixtures в пределах, допущенных
  mission (не научные утверждения, claim ceiling C0_SOFTWARE_ONLY).
- Изменение frozen package F2, FROZEN_R1 history, HG-B записей, verdicts R/V,
  `project/state.json`, `project/infra-state.json` canonical статусов.
- Назначение AUTHOR_U1; объявление R2 ACTIVE; любые фиктивные
  host/fingerprint; переименование hostname; изменение системных настроек и
  чужих сервисов сервера (microk8s/docker/чужие unit'ы не трогаются).
- Merge в main (остаётся Human Gate); draft PR разрешён.
- Широкий LAN scan (U1 host search уже задокументирован
  `EX-NL5-V02-FRESH-AUDIT-R1/evidence/u1-host-search-R1.json`).

## 4. Required outputs (все machine-checkable)

1. U2 fingerprint + R2 tooling факты: `r2.cli fingerprint` полный JSON +
   `r2.cli check-host` NOT_ELIGIBLE запись (негативный контроль) — в
   execution evidence.
2. Release package validation: `reproduce.py self-test` на свежей копии
   `nanolab-components-v0.1.1` — JSON-отчёт; известные documented v0.1.1 pyc
   findings фиксируются как DOCUMENTED_FINDING (контракт R2 §6 U2 gate:
   допустимы), отличия от них = дефект.
3. Pinned oxDNA source acquisition: clone lorenzo-rovigatti/oxDNA, checkout
   `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`, verify_pinned_source = True.
4. Engine build U2: CPU · DOUBLE=ON · CUDA=OFF · MPI=OFF (Release) с полным
   provenance (source tree digest, cmake argv, CMakeCache pins, compiler,
   binary sha256+size, build log) через переиспользование
   `scripts/r2/engine_build.py` (без второго исполнительного механизма).
5. Технический smoke движка на U2 (exit=0, finite outputs; НЕ научное
   утверждение).
6. Storage plan: канонические пути `~/nanolab/{workspaces,raw,cache,tools}`
   созданы; оценка ёмкости raw для 296+56 runs на фактических размерах
   historical U2 runs (EX-NL5-002-B-R2) + решение raw_root.
7. systemd executor mechanics: disposable transient unit запускается,
   `is-active` машинно проверяется, journal persist проверен, unit корректно
   снят (чужие сервисы не затронуты).
8. Harness readiness: полный unit-test набор репозитория на этой машине.
9. `docs/infra/U2_OUTENEMY_EXECUTOR_READINESS_R1.md` — готовностный документ
   U2-плеча (полномочия НЕ повышает; dispatch остаётся заблокирован).
10. Execution events START → CONTINUATION → HANDOFF + summary; work_cli valid.

## 5. Validation plan

- `work_cli validate docs/work/executions/EX-INFRA3-U2-OUTENEMY-READINESS-R1` → ok.
- `check-consistency` ok; `workflow_lint` blocking=0; полный unittest набор OK.
- Каждое техническое утверждение в evidence = JSON с command/returncode/paths.

## 6. Честные границы

Этот WO НЕ активирует R2, НЕ назначает U1, НЕ меняет статусы и НЕ запускает
научную кампанию. U2-плечо после исполнения = «технически готово, ожидает
authority chain». Точное требование ко второй машине для U1 фиксируется в
готовностном документе без нового LAN scan (основание — уже
опубликованный `u1-host-search-R1`).
