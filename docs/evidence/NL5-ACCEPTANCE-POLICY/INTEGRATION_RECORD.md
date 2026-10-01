# INTEGRATION_RECORD — integration/nl5-acceptance-policy-r3

```text
integration branch = integration/nl5-acceptance-policy-r3
base               = 8205781def7179d6bdfa6eb7ab2a84d46776649c (fresh origin/main)
integrated subject = control/nl5-acceptance-policy-r3 @ 290cba6e4be40d3afa91e670ab50e58f7bbd7d35
merge              = --no-ff, без squash; история subject-ветки сохранена полностью
```

## Referenced gates (by exact SHA; review/verify branches remain verdict refs)

```text
review R3           = review/nl5-acceptance-policy-r3 @ 846a5a2 PASS
review refresh R3.1 = @ fa30772 PASS (post-repair 290cba6; MINOR-1/3 CLOSED,
                      MINOR-2 accepted/documented)
fresh verify R3     = verify/nl5-acceptance-policy-r3 @ 0c708e2 VERIFIED
                      (35 проверок; gate bit-exact; exclusion 34 независимо;
                       N-инварианты 64/64/10/10=148 на всех поверхностях)
```

## Статусы (честные, не меняются этим merge)

```text
candidate            = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL revision R3
status               = PRE-DATA / NOT FROZEN / 0 simulations / NO SCIENCE
SELECTED_N           = 64 primaries (declared grid, headroom 0.80) / 10 controls
freeze chain         = HG-B → Director freeze record → fresh review/verify FROZEN
HG-B                 = WAITING_OWNER (proposal docs/control/NL5_ACCEPTANCE_PRINCIPLE_HG_B_PROPOSAL_R1.md)
merge в main         = Human Gate (этот integration PR)
```

## Валидация integration-HEAD

```text
pytest tests/ -q   -> полный набор incl. 29 seed-tool тестов (см. PR-описание)
check-consistency  -> ok:true
workflow_lint      -> blocking=0
work_cli validate  -> ok:true HANDOFF_READY
```
