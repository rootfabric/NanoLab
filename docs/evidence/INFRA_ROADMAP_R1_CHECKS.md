# INFRA ROADMAP R1 — control validation

Тип: `DOCUMENTATION / CONTROL PLAN CHECK`. Научные эксперименты и compute jobs не запускались.

Проверенный candidate перед добавлением этого отчёта:

```text
HEAD fe79befccea5d2bf0ff13fb63592f02b3556bda7
BASE 9d8ea394c6c037b0560908689e2ce932bf0c511c
```

## Checks

- 8 checkpoint IDs `INFRA0..INFRA7` уникальны.
- 14 task IDs уникальны.
- Все checkpoint dependencies существуют.
- Все task dependencies существуют.
- Checkpoint graph acyclic: PASS.
- Task graph acyclic: PASS.
- `mvp_checkpoint = INFRA3` существует.
- `project/infra-state.json` frontier = `INFRA0`, next = `INFRA0-001`.
- Единственная READY-задача: `INFRA0-001`.
- `scientific_state_owned = false`.
- Scientific `project/state.json` в candidate имеет тот же Git blob SHA, что canonical base: `c2b819a912c45e92cd29b2b688cca425de5e1e63`.
- E0–E6 не изменялись и не запускались.
- GitHub tracking создан: roadmap issue #12, ready task issue #13.

## Security invariant

INFRA roadmap явно запрещает автоматический запуск произвольного public PR-кода на trusted self-hosted scientific runner. Реализация технического negative control является задачей INFRA0-001, а не доказана этим документом.

## Scope conclusion

Candidate создаёт параллельный compute capability frontier и не меняет scientific/product frontier. INFRA acceptance не является scientific acceptance.
