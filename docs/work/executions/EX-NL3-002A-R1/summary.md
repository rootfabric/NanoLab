# Summary — EX-NL3-002A-R1 (NL3-002A, pre-E2 technical readiness)

- Base: `ba750af0f929f1b49aebe65ab6cc449fbc59a7b1` (local canonical main с docs-sync и G1/U4 owner decisions). Ветка: `work/nl3-002a-pre-e2-r1`. Коммиты: `6190a85` START, `98d2d1e` feat(e2) (substantive), records-коммит (события/summary/evidence — content-HEAD см. handoff event).
- Роль: IMPLEMENTER (та же DSH-сессия ранее исполняла control docs-sync по прямой миссии владельца; Reviewer/Verifier — отдельные fresh-сессии).
- Научные прогоны: НЕТ. campaign-level scientific_outcome = NOT_EVALUATED, E2 = NOT_RUN. state.json/plan.json не менялись.

## Поставлено (по пунктам WO-NL3-002A)

| # | Блок WO | Статус | Артефакт |
|---|---|---|---|
| 1 | Compatibility audit (авторский sim-input vs pinned engine) | DONE | `scripts/e2/compat_audit.py` + `scripts/e2/engine_options.json` (222 опции из `input_options.md` @ `00dc7fb9`, SHA-256 источника в реестре); на реальном `pro_CPU.in`: `unknown_keys = []` |
| 2 | Design→topology mapping (gap G2) | DONE (PARTIAL, честно) | `scripts/e2/topology_mapping.py`; на реальных 0b-поверхностях: 8378==8378 CONSERVED; 118→112 = 91 exact + scaffold 4266→split 16 + merges 19→568, 3→126 + остаток 4↔3 (176==176) — `PARTIAL_ASSOCIATION`, residual G2-R1 |
| 3 | Spring/restraint semantics | DONE (production-часть) | `scripts/e2/restraints_inventory.py`; на реальном `pro_CPU.in`: `external_forces = 0` → production-прогон автора БЕЗ внешних рестраинтов; Init_Hinges скрипты не сканировались (не скачивались) — оставшийся пункт перед пилотом |
| 4 | Hinge-angle observable v1 | DONE (first-principles, U-obs-1) | `scripts/e2/observables.py` + freeze `docs/research/E2_OBSERVABLES_R1.md` ДО данных; валидация на синтетике 0°/45°/90° в 1e-6 |
| 5 | Integrity observable v1 | DONE | pairs_fraction / long_bond_fraction / displacement_max; негатив «красивый угол развалившейся конструкции» покрыт тестом |
| 6 | Synthetic cost probe | DONE | `E2A-PROBE-S001`: 5000-step MD, pinned binary (build source `00dc7fb9` подтверждён), engine-owned DSDNA8 fixture (GPL-3.0 CLEAR): completed, wall 2.02 s (вкл. WSL/bash overhead); memory NOT_MEASURED (INFRA2-002) |

## Ключевые научные факты для E2 (не claim'ы, вход в E2-PROTO-R1)

1. **Production-прогон автора не держится на рестраинтах** (`external_forces = 0`) — hinge angle в production будет определяться структурой, если Init_Hinges не оставляет сил (проверить при пилоте).
2. **118→112 — нормальное length-сохраняющее преобразование** (split скаффолда + merge стейплов), потерь информации нет (8378==8378); полная per-strand идентификация — не блокер E2, residual G2-R1.
3. **Документация движка неполна**: `dt/debug/log_file/refresh_vel` используются бинарником (подтверждено source), но отсутствуют в `input_options.md` (U-compat-1); `rcut` в авторском input вообще не парсится движком (U-compat-2).
4. **Замеры стоимости**: 5000-step / 16 частиц ≈ 2.0 s wall (incl. overhead) → экстрополяция для бюджета кампании сознательно НЕ делается (честный measured budget появится после пилота на реальном 0b).

## Открытые пункты

- U-obs-1: SI-pinning / манифест рук 0b — до E2-PROTO-R1 (owner).
- U-compat-1/2, U-rest-1 (см. отчёты).
- Сканирование Init_Hinges-скриптов — при пилоте (download-on-run).

## Чеки

- `python -m unittest discover -s tests -t .` → **227 OK** (1 skip; 27 новых).
- `CONTROL_DEVELOPMENT -CheckConsistency` → ok (state/plan не тронуты).
- `work_cli validate docs/work/executions/EX-NL3-002A-R1` → структурные чеки PASS.
- Детерминизм отчётов: два прогона → байт-идентичный JSON (тестами).
- Digest-гейт реальных данных 3/3 PASS; скачанные байты удалены (U4 = NO).

## Next action

Независимый REVIEWER (fresh-сессия) на exact HEAD: evidence-пакет `EX-NL3-002A-R1` (frozen observables до данных; корректность mapping-классификации; digest-гейт; отсутствие научных claim'ов) → `docs/evidence/NL3-002A/REVIEWER_VERDICT.md`. После приёмки — пилот E2 (0b × 1–3, отдельный WO кампании) с предварительным решением по SI/U-obs-1.
