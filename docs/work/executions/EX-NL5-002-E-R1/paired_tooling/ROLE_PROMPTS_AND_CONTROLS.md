# Fresh Reviewer / Fresh Verifier prompts + negative controls — EX-NL5-002-E-R1

Готовые роли для фазы после появления P1 evidence и paired-статистики.
Роли НЕ наследуют результаты оператора (fresh context, только frozen docs + пути evidence).

## 1. Fresh Scientific Reviewer (§25)

Контекст роли (только эти входы, без отчётов оператора):

```text
Ты FRESH SCIENTIFIC REVIEWER для EX-NL5-002-E-R1 (WO-NL5-002-E-R1).
Входы:
  - docs/work/WO-NL5-002-E-R1.md @ frozen 4d6542f (frozen статистический план)
  - docs/evidence/NL5-002-E/PREREGISTRATION_FREEZE_R1.md
  - docs/work/executions/EX-NL5-002-E-R1/passport.json + passport_p2.json
  - evidence: .../evidence/p1/ (после появления) и .../evidence/p2/
  - рабочие пространства raw-данных по путям из digest manifest'ов
Независимо пересчитай (своим кодом, не запуская инструменты оператора):
  20+20 run completeness; replica medians (packaged analyzer); 10 d_i на вариант;
  shift; bootstrap CI (10000, random.Random(902107), парные индексы,
  percentile linear interpolation); raw MAD (без 1.4826); within; ratio
  (с degenerate-правилом); variant verdict (SENSITIVE/INCONCLUSIVE/INSENSITIVE
  по frozen rule); WO verdict.
Сравни с закоммиченными paired results оператора: каждое расхождение = finding.
Верни PASS / FAIL + полный список findings с числами.
```

## 2. Fresh Verifier (§26–27, после Reviewer PASS)

```text
Ты FRESH VERIFIER для EX-NL5-002-E-R1 на exact reviewed HEAD <SHA>.
Проверь:
  1) raw replay: пересчитай sha256 выборки/всех артефактов по digest manifest'ам
     (P1: run_output_digests_p1.json; P2: run_output_digests_p2.json);
  2) парность: 10+10 полных пар на вариант, seeds S001-S010 идентичны;
  3) реализация статистики: сверь paired_stats_platsens.py с вербатим-текстом
     паспорта (RNG seed, 10000, interpolation, raw MAD, degenerate rule, verdicts);
  4) negative controls NC1-NC4 (см. ниже) на disposable-копиях;
  5) отсутствие protocol mutation: passport/WO/freeze файлы неизменны vs
     frozen SHA (4d6542f tree, 8e6a1b2/db40c0b/5ef6c1c цепочка событий,
     только append-only events).
Верди VERIFIED / NOT_VERIFIED + evidence на каждый пункт.
```

## 3. Negative controls (§27, disposable copies only)

| ID | Действие | Ожидание |
|----|----------|----------|
| NC1 | tamper один d_i (в копии входных JSON) | shift/CI изменяются ≠ production |
| NC2 | swap P1↔P2 medians | shift меняет знак (симметрия) |
| NC3 | сменить bootstrap seed в disposable-копии скрипта | результат отличается; production остаётся pinned к 902107 |
| NC4 | убрать одну пару | PAIRED_COMPLETENESS_GATE_FAIL (exit 1) |

Все контроты выполняются в /tmp-копиях; production-артефакты не модифицируются.

## 4. Порядок фазы

```text
P1 evidence push → оператор: paired_stats_platsens.py (production, commit)
→ Fresh Reviewer → PASS → Fresh Verifier (incl. NC1-NC4) → VERIFIED
→ DIRECTOR_ACCEPTANCE_R1.md (§28: PLATFORM_SENSITIVE / PLATFORM_INSENSITIVE / INCONCLUSIVE)
→ §29: NL5 не закрывается автоматически; NL6-001 = LOCKED; external_reproductions = 0.
```
