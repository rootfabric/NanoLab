# EX-NL4-001-R1 — Summary

**Execution:** EX-NL4-001-R1 (WO-NL4-001, checkpoint NL4)
**Branch:** `work/nl4-001-bounded-agent-r1` от exact base `404618902734c56e0e5f853ee8e68bbd5f91ccb3` (= свежий origin/main)
**Risk / claim:** MEDIUM / `C0_SOFTWARE_ONLY` — infrastructure, no science runs; `physics_runs = 0`; scientific_outcome NOT_EVALUATED
**Статус:** HANDOFF_READY (→ REVIEWER, MEDIUM routing)

## Что сделано

Замороженный stdlib-only пакет `scripts/nl4/` — контроллер экспериментов, ограниченный исследовательский агент и baselines, вся логика на mock-исполнителе (детерминированные псевдо-наблюдаемые из sha256 фикстурных параметров, run IDs `NL4-MOCK-R000N`; НИКАКОЙ физики/движка/LLM/сети):

| Файл | Роль |
|---|---|
| `allowlist.json` | frozen r1: actions `{propose_candidate, request_run, read_analysis, stop}`; variant `{0b,11b,32b,53b,74b}`; steps `{50000,100000,150000}` (опц., default 150000); seed triple `201004/202008/203012`; бюджеты `max_simulations`/`max_wall_minutes`; явные forbidden-поля (physics/protocol/engine/criteria/…) |
| `controller.py` | детерминированный цикл goal→candidates→ExecutorAdapter→analysis→evidence→score→next; fail-closed rejects (исполнение НЕ происходит); бюджет — жёсткий кап; evidence — canonical JSON (`e2.canonical`, import без изменений) |
| `mock_executor.py` | ExecutorAdapter на моке: псевдо-наблюдаемые (angle/lbf/pf_v2/disp) + digest входа + pseudo wall; `estimate_wall_seconds` для точного wall-энфорсмента |
| `agents/baseline_random.py` | random без ИИ: `random.Random(seed из sha256 goal-JSON)`, выборка без повторов |
| `agents/baseline_grid.py` | полный перебор allowlist-пространства (45 комбинаций) в каноническом порядке |
| `agents/bounded_agent.py` | обёртка внешнего «мозга» (pluggable; LLM в E3): валидация против allowlist ДО контроллера, budget mirror, `rejected_actions` log; `ScriptedBrain` для тестов |
| `scoring.py` | score = \|median_angle − target\| под frozen гейтами E2_PROTO_R1 §4 (`lbf ≤ 0.1078`, `pf_v2 ≥ 0.50`, `disp ≤ 20.0`); invalid/rejected — честный учёт |
| `__main__.py` | CLI: `demo --agent random|grid|scripted`, `validate-candidate` |

Плюс фикс согласованности: `tests/test_e2_pilot.py` получил стандартный path-insert (единственный тест-файл без него; CI-команда `python -m unittest discover -s tests -t .` без PYTHONPATH теперь зелёная).

## Валидации

- **unittest:** 287 тестов OK (1 skip) — 242 прежних + 45 новых `tests/test_nl4_*.py`; командой CI точно (`discover -s tests -t .`, без PYTHONPATH).
- **work_cli validate / close** EX-NL4-001-R1: ok.
- **check-consistency:** ok. `state.json` не менялся.
- **Детерминизм:** два прогона `demo` (random и grid) → байт-идентичные файлы (`fc /b`: no differences).

## Демонстрация end-to-end (goal: target 45°, budget 5, mock)

- **random** (seed из goal): `32b/100000/203012` → `32b/150000/201004` → `53b/50000/202008` → `0b/100000/202008` → `53b/50000/201004`; гейты: 1 scored / 4 STRUCTURALLY_INVALID; best score 90.36 (псевдо-данные).
- **grid**: `0b/50000/{201004,202008,203012}` → `0b/100000/{201004,202008}`; 2 scored / 3 invalid; best score 24.46 (псевдо-данные).
- **bounded-negative**: 3 вне-allowlist предложения (неизвестное действие `tune_protocol`; `variant 99b`; forbidden-поле `engine`) — все отклонены, залогированы (`ACTION_NOT_IN_ALLOWLIST`, `CANDIDATE_PARAM_NOT_IN_ALLOWLIST`, `FORBIDDEN_CANDIDATE_FIELD`), исполнен только валидный `0b`.

Evidence: `evidence/demo-random-goal45-budget5.json`, `evidence/demo-grid-goal45-budget5.json`, `evidence/demo-bounded-negative.json` (+ вход `bounded-negative-proposals.json`).

## Открытые риски

1. Mock-наблюдаемые — детерминированные псевдо-данные (sha256), не физика; к E3 не применяются.
2. Wall-бюджет в mockе точен (estimate == факт); реальный адаптер (NL4-002) должен декларировать консервативную оценку.
3. `bounded_agent` budget mirror дублирует контроллер сознательно (defense in depth), не единственная линия защиты.

## Next action (одно)

REVIEWER fresh-сессия на exact HEAD ветки → Director → merge (Human Gate); далее NL4-002 (E3 кампания, реальный движок через `ExecutorAdapter`).
