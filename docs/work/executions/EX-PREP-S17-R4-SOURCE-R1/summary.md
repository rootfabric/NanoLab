# EX-PREP-S17-R4-SOURCE-R1 — Summary (handoff)

Work Order: `WO-PREP-S17-R4-SOURCE-R1` (GitHub issue #64, parent issue #63).
Branch: `work/prep-s17-r4-source-r1`, worktree `/home/rdpuser/NanoLab/prep-s17-r4-source`.
Base: canonical `main @ 513c4fa86470d939e9f9b7829e9c67c489c15a57` (tree `6d3a2132ae6ecdfed6269fe39697e8ac9bab152a`, merge of PR #57).
Implementation subject head: `98c3d72dec14d44f3b90254dac9c57f55737fbe5` (tree `d836baff56362700f202af077d06582594ad1d59`).
Risk: MEDIUM; claim class: C0_SOFTWARE_ONLY; научных прогонов: 0; сообщений авторам: 0.

## 1. Result (verdict)

- **G1 (структура follower) = `BLOCKED_SOURCE`.** Оригинальные topology/config/caDNAno-файлы
  follower не существуют ни в одной аудитированной поверхности. Негативное evidence расширено до
  10 поверхностей с digests и resume conditions — `blocked_source_receipt` в
  `docs/research/S17_R4_FOLLOWER_PROVENANCE.json`. Официальный Data availability statement
  (PMC VoR, `ead50002…`) называет ровно 3 репозитория; полный каталог Nanobase перечислен
  (109/109 структур, `4637ff04…`) — follower-записи нет; Zenodo 8248808 без изменений
  (`5d26ec0a…`), R2-перечисления архивов переиспользованы; `sulcgroup/hinges` @ `7c8b04a6`
  (`fb5ef0d2…`) и `walterlab-um/…_SMCodes` (MIT) — без design-файлов.
- **G2 (index anchors) = `UNKNOWN`** — placeholder-последовательности в pinned-топологиях (R2);
  author design с connecting ODN не найден.
- **G3 (helix/arm assignment) — частично закрыт, `INFERRED_CANDIDATE`.** Все 10 пар оцифрованы с
  Suppl. Fig. S5b (стр. 19 SI PDF, pin `66074e7d…`, байт-идентичен R3-пину): driver 149@h0,
  173@h1, 172@h3, 174@h5, 153@h5-6 (верх) / 89@h17, 165@h6, 164@h7, 163@h9-10, 151@h12 (низ);
  follower 151r@h11-12, 163r@h10, 164r@h9, 165r@h6, 89r@h17 (верх) / 153r@h5, 174r@h4, 172r@h3,
  173r@h1-2, 149r@h11 (низ) — с явными источниками неопределённости и 2 вопросами авторам.
- **G4 (3D-ориентация портов) = `UNKNOWN`** (bitmap без масштаба/координат; «flip upside down» —
  качественный текст).
- **G6** = force-пары `SOURCE_CONFIRMED` (R2) + координаты `UNKNOWN` (= G2); добавлен
  качественный anchor с движковой caDNAno-карты (MOESM5 `dae20e28…`: handle полимеразы
  helix 15 → helix 20, inner face).
- **Candidate-реконструкция:** только hypothesis-only interface map
  (`CANDIDATE_DESIGN`/`HYPOTHESIS` в `S17_R4_PORT_CANDIDATES.json`); fabricированный
  follower `.top`/`.dat` сознательно НЕ создан (без scaffold-маршрутизации это была бы фикция).
- **Workflow test vehicle (не S17 follower):** Nanobase 256/257 (Narcissus/Echo, Huang et al.
  2024) — двухкомпонентная система с полными design-файлами обеих половин; для отдельного WO.

## 2. Deliverables

| Path | sha256 (12) |
|---|---|
| `docs/research/S17_R4_PORT_CANDIDATES.json` | `a5240e5b522d` |
| `docs/research/S17_R4_FOLLOWER_PROVENANCE.json` | `9ad9ed41254b` |
| `docs/research/S17_R4_SOURCE_GAP_CLOSURE.md` | `c129113b4804` |
| `tests/test_s17_r4_source.py` | `a77a77d7abb1` |
| `docs/work/executions/EX-PREP-S17-R4-SOURCE-R1/passport.json` | `a1e4d93617d0` |

Full digests in `evidence-map.json`. Events: `0001-work-order-started`, `0002-continuation-checkpoint`,
`0003-implementation-committed`, `0004-validation-recorded`, `0005-handoff-completed` (append-only).

## 3. Validation (exact head `98c3d72d…`, tree `d836baff…`)

```text
python3 -m unittest discover -s tests -t .        => Ran 698 tests in 58.4s, OK (679 base + 19 new)
PYTHONPATH=scripts python3 -m harness.cli check-consistency => ok: true, errors: [], warnings: []
PYTHONPATH=scripts python3 -m harness.workflow_lint         => workflows: 1, violations: 0, blocking: 0
PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-PREP-S17-R4-SOURCE-R1 => ok: true
```

## 4. Budget and discipline

- Сеть: ≈**20.7 MiB** уникальных загрузок (бюджет ≤256 MiB); multi-GB Zenodo архивы не качались;
  SI-PDF (13.9 MB) и figures (2.3 MB) — самые большие единичные fetches; Dataset S1 (101,900 B)
  перепроверен байт-в-байт = R1/R3 pin `dc3cc6c5…`.
- 0 scientific runs; 0 paid compute; 0 исходящих сообщений; project/state.json, plan.json,
  frozen artifacts, R1/R2 knowledge-pack surfaces не изменялись; сырые сторонние файлы не
  вендорятся (только digests/urls/цитаты ≤100 B; страницы-рендеры — в /tmp scratch).
- Work Queue: append-only (строка STARTED от 0001 + финальная строка handoff).

## 5. Open risks

1. Deep Blue 474299762 и bioRxiv DC1 недоступны из песочницы (Cloudflare challenge / HTTP 403);
   содержимое UNVERIFIED (оба — маловероятные поверхности follower design, но не нулевая).
2. GitHub CODE search недоступен без токена (замещено web_search по уникальным 20-mer'ам).
3. Все helix/arm assignments — оцифровка bitmap; до авторского подтверждения инженерное
   использование запрещено (статусы не поднимаются).
4. R2/R3 остаются нестеканными в main (неканонические); их артефакты использованы только как
   pinned read-only git objects.

## 6. Handoff

- Reviewer/Verifier: fresh review + exact-head verify этой ветки; merge = Human Gate.
- NEXT_ACTION (одно): owner — разрешить отправку drafted author questions
  (`S17_R4_SOURCE_GAP_CLOSURE.md` §5) авторам, либо направить two-component workflow-обкатку на
  Nanobase 256/257 отдельным bounded WO.


## Errata R4.1 (post-review, append-only)

Independent fresh Reviewer (отдельная сессия, scratch-клон /tmp/review-r4): **PASS**,
blocking findings отсутствуют, 6 non-blocking замечаний (m1–m6). Применено:

- **m1**: события 0003/0005 называют «13 provenance records» — фактически в
  `S17_R4_FOLLOWER_PROVENANCE.json` **14** записей (файл не менялся с subject 98c3d72;
  счёт устарел на момент записи событий; события append-only, текст не переписывается).
- **m4**: опечатки RU в `S17_R4_SOURCE_GAP_CLOSURE.md` исправлены in-place
  (evidenc-машиной → evidence-машиной ×2, Вfollower-паре → В follower-паре, включяя → включая)
  — содержательных изменений нет.
- Отложено (non-blocking): m2 (записи github_surveys/author_web_surfaces без одиночного
  url и с sha256=null — допустимо офлайн-тестом, ограничения честно записаны),
  m3 (sha256 записи Deep Blue хэширует challenge-страницу, помечено «pins: nothing»),
  m5 (12-hex префиксы в summary при полных дайджестах в evidence-map),
  m6 (позиция «стр. 19 = Suppl. Fig. S5b» не перепроверялась удалённо; сам пин верифицирован).
