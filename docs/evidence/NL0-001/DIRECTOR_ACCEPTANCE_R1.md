# NL0-001 — Director Acceptance R1

Дата: 2026-09-08. Роль: `DIRECTOR`. Work Order: `NL0-001 — Select accessible references`.

## Exact subjects

```text
IMPLEMENTER_CANDIDATE = f738bff77f2406552b4383c05989ffc6e56a3bd5
REVIEW_EVIDENCE      = e0303aa05bbcc3f6839c3af31d7a28ecbd66a932
VERIFIER_EVIDENCE    = 1a9bf9ca2288021b0371b858c77bd648dac2faaf
PRE_MERGE_MAIN        = f4d2979a1d2502d86c035f25e36961b4d5ac2764
CANDIDATE_MERGE       = 142ed2df0a971763567d6cc672a218d04ee85201
```

Fresh Reviewer и Fresh Verifier независимо связали свои PASS-verdict с одним и тем же exact candidate HEAD. Оба отдельно классифицировали epoch drift от исходного base к текущему `main` как `CONTINUE`.

## Director decision

```text
REVIEW_VERDICT   = PASS
VERIFIER_VERDICT = PASS
EPOCH_DRIFT      = CONTINUE
DIRECTOR_VERDICT = ACCEPTED
```

PR #11 объединён только с `expected_head_sha=f738bff77f2406552b4383c05989ffc6e56a3bd5`; изменение candidate после review/verification не произошло.

## Что канонически принято

### E1 reference

Принят выбор официального oxDNA `DSDNA8/MD` quick regression fixture на pinned upstream commit `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` как минимального первого вычислительного reference path. Его exact input/oracle identities и SHA-256 сохранены в `docs/research/INPUT_AVAILABILITY.md`.

Это выбор источника, а не выполненный E1. Claim ceiling для будущего quick regression остаётся вычислительным; физическая экспериментальная валидация не заявлена.

### E2 reference family

Принято семейство Shi–Castro–Arya, DOI `10.1021/acsnano.7b00242`, и авторский repository `gauravarya77/DNA-hinge-simulations@23fd1ff7731e9017bd776f49206dc42d70d9fe91` как приоритетный executable seed для будущего E2.

Сохраняются известные ограничения:

- статья: 298 K; pinned CPU/GPU inputs: 300 K — решение передано `NL0-003`;
- redistribution rights для E2 repository остаются `UNKNOWN` — аудит `NL0-002`;
- S08 остаётся `INPUT_PACK_NOT_LOCATED`, не `NO_DATA_EXISTS`;
- leaf-spring benchmark остаётся будущим rich benchmark.

## State transition

После этого acceptance record каноническое состояние должно быть:

```text
frontier               = NL0
NL0                     = IN_PROGRESS
NL0-001                 = ACCEPTED
NL0-002                 = READY
NL0-003                 = READY
next_work_order         = NL0-002
E0..E6                  = NOT_RUN
physics_runs            = 0
```

`NL0` целиком **не закрыт**. Следующая scheduler priority — `NL0-002`; `NL0-003` также разблокирован и может готовиться параллельно при соблюдении правил conflict/scope.

## Rank-up moves preserved

Reviewer non-blocking improvements не потеряны:

1. `NL0-003`: preregister canonical temperature choice и seed/thermostat/dt policy;
2. `NL0-003`: закрепить hinge-angle observable по статье и reported comparison targets;
3. `NL0-002`: включить media/data и reference-vs-copy режимы в rights audit;
4. Harness hardening: terminal work event в будущем должен лучше привязываться к финальному handoff HEAD;
5. Leaf-spring archive size/provenance перепроверить только при его активации.

## Limitations

Ни Implementer, ни Reviewer, ни Verifier не запускали E1 physics simulation — это соответствует scope `NL0-001`. Verifier не смог выполнить clean-clone wrapper invocation из-за DNS контейнера, но независимо воспроизвёл текущие `work_cli.py close` predicates на live exact execution package и получил PASS.

## Final

```text
NL0-001 = ACCEPTED
NEXT = NL0-002
PARALLEL_READY = NL0-003
```
