# FLOW-R1: команды агента

```bash
export PYTHONPATH=scripts
python3 -m harness.cli drive --root .
python3 -m harness.operations --format markdown
python3 -m harness.work_cli start docs/work/executions/EX-MY-TASK-R1 --root . --work-order WO-MY-TASK-R1 --checkpoint NL5 --risk MEDIUM --allow scripts/my_module.py --summary "Начало C0 работы" --next-action "Реализация"
python3 -m harness.work_cli record docs/work/executions/EX-MY-TASK-R1 --root . --event-type VALIDATION_RECORDED --summary "Проверки выполнены; см. evidence" --evidence path/to/receipt.json
# Перед finish создать содержательный summary.md в execution directory.
python3 -m harness.work_cli finish docs/work/executions/EX-MY-TASK-R1 --root . --summary "Передача независимому reviewer" --next-action "Review"
python3 -m harness.work_cli correct docs/work/executions/EX-MY-TASK-R1 --root . --summary "Append-only correction; предыдущие записи сохранены"
python3 -m harness.batch_validate json --root .
python3 -m harness.batch_validate executions --root .
python3 -m unittest discover -s tests -t . -v
```

Команды start/record/finish/correct не коммитят и не пушат автоматически. После START до substantive работы нужен commit/push. Writer ограничен новыми C0 sequence-v1 executions; historical/scientific profiles не переписывать. Реальный SHA разрешается из Git; вымышленный hex отвергается. Не объявлять Reviewer/Verifier своей же работы. Коррекция independent review публикуется реальным независимым executor с `--role REVIEWER` или `VERIFIER`, а не сменой имени текущей сессии.

Для сравнения двух коммитов только после чтения diff:

```bash
python3 -m harness.review_impact --base REVIEWED_SHA --head NEW_SHA --publication-path docs/work/executions/EX-MY-TASK-R1/summary.md
```

PUBLICATION_ONLY_CANDIDATE требует delta review текста и ссылки на прежние валидные subject evidence. Это не PASS и не merge authorization.
