# Branch Passport — work/nl2-003-provenance-recovery-r1 (EX-NL2-003-R1)

- **Work Order:** NL2-003 «Integrate workflow provenance and recovery» (validator hardening + provenance/recovery; AiiDA — вне scope)
- **Base:** `d121119add4533c77c40db287c292d0c8e542188` (canonical main, merge PR #32; NL2-002 ACCEPTED, E1 = SUPPORTED, next NL2-003 READY)
- **Branch:** `work/nl2-003-provenance-recovery-r1` (worktree `C:\NanoLab\nl2-003`)
- **Risk / claim:** MEDIUM / C0_SOFTWARE_ONLY
- **Started:** 2026-09-10T13:04:53Z (START commit — до substantive work)

## Scope (закрываемые hardening-кандидаты)

| ID | Источник | Суть | Где закрывается |
|---|---|---|---|
| S003 | REVIEWER_VERDICT NL2-001 §1.8/§3, VERIFIER §4 | terminal RUN_COMPLETED + SUPPORTED принимается тихо | experiment_cli: SUPPORTED только на ANALYSIS_COMPLETED с verification-поверхностью |
| digest-vs-blob | REVIEWER F1, VERIFIER §4.2 | валидаторы не сверяют sha256/size с байтами | experiment_cli verify-digests (git-блобы, не working copy) |
| emit_run | REVIEWER F1, REPAIR_MAP_F1_R1 §5.1 (обязательный фикс) | манифест сериализовался до финального case_record (+35 B) | e0_runner.py emit_run: финальный case_record ДО манифеста + digest-инвариантность |
| O1 | VERIFIER NL2-001 findings #4 | 55 stale storage_location (сегмент чужой кампании) в superseded E0-R2 | experiment_cli: storage_location in-Git формата обязан содержать сегменты campaign_id/run_id манифеста |
| O2/F3 | REVIEWER F3, VERIFIER findings #4/#5 | placeholder-timestamps (round/midnight, copy-повторы) | work_cli: midnight-placeholder и константный copy-timestamp (≥3 события) → ошибка |
| F-1/O3 | VERIFIER NL2-002 §5 (F-1), NL2-001 O3 | campaign evidence-map не соответствует v1-схеме | evidence-map.schema.v1.json → де-факто campaign-конвенция (schema follow facts) |
| F-3 (урок) | VERIFIER NL2-002 | CRLF working-copy vs блобы | PROVENANCE_RECOVERY_R1 §6 readback-требования + verify-digests читает блобы |

## Новое (provenance/recovery)

- `docs/research/PROVENANCE_RECOVERY_R1.md` — цепочка subject→seeds→inputs→binaries→runs→analysis→evidence-map; stop/resume (run ID не переиспользуется; RESUMED-маркер на RUN_CHECKPOINT нового run); дедупликация идентичной поверхности; readback-требования.
- `config/infra/provenance-recovery.v1.json` — machine-readable проекция правил.

## Не входит

AiiDA/HPC-интеграция (отдельный bounded WO), изменение event-схем v1, graceful crash-пути валидаторов, engine-coupled E0-кейсы, F-2 эстиматоры.

## Отклонения от allowed_paths

Нет. `e0_runner.py` включён в allowed_paths сознательно: REPAIR_MAP_F1_R1 §5.1 объявляет emit_run-фикс ОБЯЗАТЕЛЬНЫМ для будущих E0-tooling кампаний; зафиксировать его иначе (вне published-инструмента) невозможно. Исторические subject'ы кампаний сохраняют старые блобы в git-истории (provenance не нарушается).
