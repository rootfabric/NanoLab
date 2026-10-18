# WO-PREP-S17-R4-SOURCE-R1 — PREP-S17 R4: закрытие source-гэпов G1–G4/G6 follower-компонента (targeted source recovery)

Статус: **IN_PROGRESS / PREPARATORY (NO CONFIRMATORY SCIENCE)**. Основание: GitHub issue #64 (дочерний к parent-программе issue #63), линия PREP-S17 (R1 → PR #57 merged → R2/R3 — stacked, НЕ канонические; их факты переиспользуются только как pinned read-only references).

## Scope

- Цель: максимально закрыть source-гэпы **G1** (структура follower: topology/config/caDNAno), **G2** (nucleotide-index anchors connecting-ODN), **G3** (per-ODN helix/arm assignment), **G4** (точная 3D-ориентация портов) и **G6** (координатная связь trap↔полимераза с оверхэнгами) для S17 driver–follower (Centola et al., Nature Nanotechnology `10.1038/s41565-023-01516-x`).
- Допустимые исходы (любой из трёх, честно): (a) восстановленные оригинальные design-файлы follower с exact provenance; (b) явно помеченная candidate-реконструкция (`CANDIDATE_DESIGN`/`HYPOTHESIS`); (c) честный `BLOCKED_SOURCE` receipt с негативной evidenc-машиной и черновиком вопросов авторам (черновик НЕ отправляется никогда в этом WO).
- Base: `main @ 513c4fa86470d939e9f9b7829e9c67c489c15a57` (merge of PR #57), tree `6d3a2132ae6ecdfed6269fe39697e8ac9bab152a`.
- Pinned read-only references: R3 head `2cf8297f10ab5ec98b8c8023ff76b39d92ef398b` (`S17_R3_SOURCE_GAPS.md`, `S17_KNOWLEDGEPACK_R2.json`, `S17_SOURCE_RECOVERY_R2.md`, `S17_R3_INTERFACE_AUDIT.md`, recipe 10 пар), R2 head `26c4cd51151167634815c531b9c49dcc54ba6243` (`S17_R2_PORT_MAP.json`). Dataset S1 pin: sha256 `dc3cc6c53a9a116630db25a423c8439910d9e2d0ba159ef32424b546bcf3036c` (101,900 B).
- Risk: **MEDIUM**; claim class: **C0_SOFTWARE_ONLY**; научных прогонов **0**; платных сервисов 0.
- Бюджет: суммарная сетевая передача **≤ 256 MiB** (только targeted fetches; НИКОГДА не скачивать multi-GB Zenodo архивы целиком; сперва listing содержимого zip/python-zipfile, затем маленькие файлы), scratch ≤ 2 GiB, локальный Python.

## Allowed paths

```text
docs/work/WO-PREP-S17-R4-SOURCE-R1.md
docs/work/WORK_QUEUE.md                (только append новой строки WO)
docs/work/executions/EX-PREP-S17-R4-SOURCE-R1/**
docs/research/S17_R4_PORT_CANDIDATES.json
docs/research/S17_R4_FOLLOWER_PROVENANCE.json
docs/research/S17_R4_SOURCE_GAP_CLOSURE.md
tests/test_s17_r4_source.py
```

## Forbidden paths / actions

```text
project/state.json, project/plan.json, project/infra-state.json
frozen NL5 artifacts, frozen scientific evidence, scientific protocols
scripts/nl4/**, scripts/nl5/**, scripts/e2/**, scripts/r2/**, scripts/hinge_family/**, scripts/nl2_003* (import reuse allowed, modification forbidden)
R1/R2 knowledge-pack surfaces (scripts/knowledge_pack/contract.py, import_validation.py — import reuse allowed, modification forbidden)
научные прогоны (oxDNA MD, E5, NL6), paid compute, статус-переходы NL5/NL6
vendoring сырых сторонних файлов в репозиторий (в evidence — только digests + urls + цитаты ≤ 100 B)
отправка любых сообщений авторам (только draft)
direct push в main, force-push, merge, история-rewrite
чужие worktree (/home/rdpuser/NanoLab/* кроме prep-s17-r4-source)
```

## Non-goals (жёстко)

- Не запускать oxDNA MD/E5/confirmatory science; не повышать claim level выше `PINNED_IMPORT_VERIFIED`/`C0_SOFTWARE_ONLY`.
- Не объявлять найденную candidate-реконструкцию оригиналом: только `CANDIDATE_DESIGN`/`HYPOTHESIS` с явной маркировкой.
- Не создавать фиктивные соответствия ODN↔helix/index: `UNKNOWN` остаётся `UNKNOWN`.
- Не отправлять сообщения авторам/репозиториям (никаких GitHub issues/писем).

## Required outputs

1. Web-research + bounded fetch оригинальных поверхностей follower-дизайна (статья, SI PDF/Dataset S1, Nanobase 196 + соседние записи, Zenodo 8248808 + связанные записи, GitHub/GitLab/scadnano-поверхности) с URL/version/sha256/license для каждой.
2. `docs/research/S17_R4_PORT_CANDIDATES.json` — machine-readable evidence map всех 10 connecting 20nt-пар: driver-side helix/arm/index evidence, follower-side mapping или точная причина unknown, per-hop `SOURCE_CONFIRMED`/`INFERRED_CANDIDATE`/`UNKNOWN`, digests источников.
3. `docs/research/S17_R4_FOLLOWER_PROVENANCE.json` — per candidate source file: url, retrieved_at_utc, sha256, size_bytes, license, content summary, что пинит/не пинит; если ничего не найдено — вместо него `BLOCKED_SOURCE` receipt с полным негативным evidence (запросы, поверхности, что отсутствовало).
4. При реальном recovery — import + mapping validation; при частичных данных — явно гипотетическая candidate-модель (`CANDIDATE_DESIGN`/`HYPOTHESIS`) или одна альтернативная опубликованная DNA-компонента с полной топологией как workflow test vehicle (явно НЕ S17 follower).
5. `docs/research/S17_R4_SOURCE_GAP_CLOSURE.md` (русский): матрица закрытия G1/G2/G3/G4/G6 + drafted author questions (НЕ отправлены).
6. `docs/work/executions/EX-PREP-S17-R4-SOURCE-R1/`: passport.json (schema по образцу `git show 2cf8297:docs/work/executions/EX-PREP-S17-R3/passport.json`), append-only events (0001-work-order-started.json и далее), evidence-map.json, summary.md; все события — exact SHAs + UTC timestamps.
7. `tests/test_s17_r4_source.py` — offline unittest: JSON deliverables parse, required fields, статусы из разрешённого словаря, sha256 = 64-hex; проходит без сети.
8. Append-строка в `docs/work/WORK_QUEUE.md`.

## Validation and review

- `python3 -m unittest discover -s tests -t .`; `PYTHONPATH=scripts python3 -m harness.cli check-consistency`; `PYTHONPATH=scripts python3 -m harness.workflow_lint`; `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-PREP-S17-R4-SOURCE-R1` — все зелёные; exact HEAD/TREE/outputs → summary.md.
- Fresh independent Reviewer + exact-head Verifier по control policy; merge = Human Gate.
