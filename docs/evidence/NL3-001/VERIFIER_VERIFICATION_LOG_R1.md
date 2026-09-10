# NL3-001 — VERIFIER VERIFICATION LOG R1 (машинный журнал независимой верификации)

Верификатор: независимый fresh-агент (VERIFIER), без доступа к контексту имплементёра/рецензента; только факты Git и собственные прогоны. Все скачивания/прогоны отчётов — disposable scratch вне любого репозитория NanoLab; durable-кэш не создавался; published-поверхности не изменялись.

Окружение: Python 3.11.8, git 2.53.0.windows.1, Windows; worktree `C:\NanoLab\verify-nl3-001`, ветка `verify/nl3-001-hinge-family-r1` @ `d01ff03` (base `5fbd6d54341947c890cc5aa5f8031de10a0de1eb`). Сеть: только бесплатное публичное чтение pinned-объектов GitHub (GitHub API + raw.githubusercontent.com; ~2.7 MB) — разрешённый режим источника (WO §Resource budget, HINGE_FAMILY_R1 §4).

## 1. Ancestry / scope

```text
git rev-parse d01ff03^{commit}  -> d01ff0332848caaa1f687314dd3e5d9c04be1935 (= origin/work/nl3-001-hinge-family-r1)
git rev-parse 5fbd6d5^{commit}  -> 5fbd6d54341947c890cc5aa5f8031de10a0de1eb
git merge-base --is-ancestor 5fbd6d5 d01ff03 -> exit 0 (base является предком)
git diff --stat 5fbd6d5..d01ff03 -> 23 files changed, 2660 insertions(+), 0 deletions(-)
```

Per-commit diff-tree: `01bef0b` = WO + паспорт + event 0001; `08585a2` = `scripts/hinge_family/**` (11) + `tests/test_hinge_family.py`; `80aed84` = `docs/research/HINGE_FAMILY_R1.md`; `d01ff03` = SESSION_LOG + события 0002–0004 + evidence-отчёт + summary + паспорт-статус. Все пути — внутри allowed_paths паспорта; `experiments/evidence/**`, published-research, `config/control/harness/**`, `scripts/harness/**`, `.github/workflows/**` — 0 изменений.

```text
blob project/state.json  @base = @subject = b3fe19db16e19fa5cc86841685475c8117af52e0 (идентичны)
blob project/plan.json   @base = @subject = c3e854dacbcac9dd0b50fc611a01aef3f2008f4b (идентичны)
SESSION_LOG.md: строго append, +10 строк (дифф без удалений)
```

Вендоринг: скан всех +2660 добавленных строк — 0 строк формата oxDNA-топологии (`<sid> <ACGT> <n3> <n5>`), 0 15-колоночных строк конфигурации, 0 байтов `pro_CPU.in`. Срабатывания регэкспа на `key = value` — 8 строк значений пинов в `source_pins.json` (DNA2/0.5/300K/2e7/CPU/double/7777/john) + 2 строки кода пакета; эти значения уже опубликованы на base (`INPUT_AVAILABILITY.md`, `E2_SETUP_R1.md` §5). Pinned-байты источника в Git отсутствуют (`git ls-files` + diff-stat).

## 2. source_pins vs внешний мир

### 2.1 Preregistered blob'ы NL0-001 (vs `INPUT_AVAILABILITY.md` на base `5fbd6d5`)

Все 6 `NL0_001_PREREGISTERED` записей реестра совпадают с published-фактами NL0-001 бит-в-бит (blob SHA-1 + размер):

```text
Design_Hinges/0b.json  0ed4075c3a0d2f29601d35c5ce70f2df6b0be1ed  173059 B
Design_Hinges/11b.json 7f1936970196ace1f9d30fc5da8f8387e80f9a3e  173145 B
Design_Hinges/32b.json 6adb55af1d46f0a2f751b0bf1ba14ab17293ff28  173315 B
Design_Hinges/53b.json 3ffdb753a63f799e8d08f9e6b42846c8f4f53e69  173481 B
Design_Hinges/74b.json 776725c154457ff6b4001a4c150098d90347acf4  173595 B
MD_Hinges/pro_CPU.in   89d76310ce726eaec9e7acb312bd7b0fc43fa735    933 B
```

### 2.2 Полные 18 поверхностей vs GitHub API tree

```text
GET api.github.com/repos/gauravarya77/DNA-hinge-simulations/git/trees/b2d6ceb…?recursive=1
truncated: False, entries: 33 (27 blob + 3 tree + 3 корневых tree… полный листинг в журнале прогона)
Сверка всех 18 записей source_pins.json: blob SHA-1 + size — 0 mismatches
```

Классы: 6 × `NL0_001_PREREGISTERED`, 12 × `R1_TREE_LISTING` — согласованы с содержимым реестра. SHA-256: ровно 5 поверхностей `0b` = `R1_CONTENT_VERIFIED` (все 5 воспроизведены собственным скачиванием, §3); остальные 13 — `sha256: null` + `NOT_VERIFIED`; контракт `pins.py` enforcement'ит «null ⇔ NOT_VERIFIED» в обе стороны (проверено чтением кода + негатив-тестами набора).

## 3. КЛЮЧЕВОЕ — независимое воспроизведение 8/8 (ВЫПОЛНЕНО, не NOT_OBSERVED)

Pinned-объекты получены тем же разрешённым способом, что и у имплементёра: user-side download по exact commit с `raw.githubusercontent.com/gauravarya77/DNA-hinge-simulations/23fd1ff7731e9017bd776f49206dc42d70d9fe91/<path>` в scratch-каталог вне репозиториев NanoLab.

```text
 Digest-гейт (size + SHA-256 + git blob SHA-1 против source_pins.json):
MD_Hinges/0b.top      size 120204 OK  sha256 OK  blob OK
MD_Hinges/0b.conf     size 2294162 OK sha256 OK  blob OK
Design_Hinges/0b.json size 173059 OK  sha256 OK  blob OK   <- preregistered NL0-001
MD_Hinges/pro_CPU.in  size 933 OK     sha256 OK  blob OK   <- preregistered NL0-001
MD_Hinges/README.md   size 1335 OK    sha256 OK  blob OK
ALL DIGESTS: PASS

PYTHONPATH=scripts python -m hinge_family validate --source-dir <scratch>/source-0b --report r1.json
  run1 exit 0; run2 exit 0; 8/8 checks PASS в обоих
SHA-256(run1) = SHA-256(run2) = F8EF3EA4F9BA6CE5C9995894BF43743E853E9C582A596ABE9EE121C592D449A5
  = ровно заявленный в HINGE_FAMILY_R1 §5 дайджест
git cat-file blob d01ff03:docs/.../hinge-0b-structural-report.json -> SHA-256 = F8EF3EA4… (байт-в-байт совпадает с воспроизведённым отчётом)
```

Замечание F-4 подтверждено: рабочая копия отчёта в worktree имеет SHA-256 `14DFA702A32378DB4CE8C33A67B450EE245DF596EA303FEFF1710BCFF94AA3A4` (CRLF-нормализация, `core.autocrlf=true`); канонические LF-байты в Git = `F8EF3EA4…`. Верификация выполнена по `git cat-file blob`.

## 4. Арифметика published-артефактов (34/34 инвариантов)

Пересчитано скриптом из собственного воспроизведённого отчёта (семантически и байтно идентичен published): состав A2081+C2076+G2075+T2146=8378; 112 страндов, Σ длин = 8378 (max 644, min 18); 103 linear + 9 circular (ids 2–7, 42–44); связанных дистанций 8275 = 8378 − 103; Σ гистограммы = 8275; длинных (>0.95) 456 = Σ(buckets ≥ 1.0); пик bucket `"0.5"` = 4677 — максимум гистограммы; scaffold 4266 + staples 4112 = 8378 == 8378 нуклеотидов топологии (check `design_bases_equal_topology_nucleotides` PASS); 117 staple-путей Σ = 4112; 2×4110 paired + 158 single = 8378; ssDNA 16×2+6×9+6×12 = 158; кроссоверы 46+413 = 459; пути 1+117 = 118; 18 виртуальных хеликсов; `t = 20000000` == `steps = 2e7`; ориентации 2.15e-07 ≤ 1e-06; бокс 402.56³; energy-line 3 поля; 6 подтверждённых ключей sim-input; digest-гейт по всем 4 поверхностям ok. Итого 34/34 PASS.

## 5. Тесты и harness-чеки

```text
python -m unittest tests.test_hinge_family -v   -> Ran 22 tests ... OK
python -m unittest discover -s tests -t .       -> Ran 160 tests ... OK (138 + 22)
python -m harness.work_cli validate <EX>        -> 15/15 EX ok (EX-NL3-001-R1: ok=true,
                                                   status=HANDOFF_READY, terminal=true, post-terminal corrections=false)
python -m harness.cli check-consistency         -> ok, exit 0 (state/plan не тронуты)
python -m harness.workflow_lint                 -> ok=true, violations 0, blocking 0
experiment_cli verify-digests E1-R1 / E1-R2 / E0-R4 -> ok=true x3, 0 mismatch
                                                  (E1-R1: 4 runs, 16 entries)
JSON-гейт: 721 tracked *.json @ d01ff03 (= 717 @ 80aed84 + 4 records-JSON, как в event 0003);
unparseable ровно 2 designed-NEG фикстуры, sha256 = CI-пинам:
  n001_empty_passport  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  n002_truncated_json  1de18ae447d83f621e98f64ef928858e9c0b1456144f10b4870bfcea8a3c4a85
```

## 6. E2-SETUP-R1 §5 machine-confirm + FAIL-проба

На скачанных реальных байтах `pro_CPU.in`: `interaction_type = DNA2`, `salt_concentration = 0.5`, `T = 300K`, `steps = 2e7`, `backend = CPU`, `backend_precision = double`; также `seed = 7777`, `thermostat = john`, `dt = 0.005`, `rcut = 2.0`, `external_forces = 0`, `verlet_skin = 0.05`, `refresh_vel = 1` — все OBSERVED-позиции §3.2 HINGE_FAMILY_R1 подтверждены. Дефолт `topology = 74b.top`, `conf_file = 74b.conf` — подстановка `74b` → `0b` зафиксирована в коде/отчёте как обязательное документируемое отклонение.

Независимая проба (scratch-копия вне Git): `T = 300K → T = 310K` → `check_preregistered` → SimInputError «preregistered sim-input values mismatch: [{'key': 'T', 'expected': '300K', 'actual': '310K'}]» = FAIL как ожидается; немодифицированный контроль → PASS. Публикуемый набор `sim_input.py PREREGISTERED` == OBSERVED-факты §5 published `E2_SETUP_R1.md` (base; не менялся).

## 7. События, паспорт, self-acceptance

```text
events 0001..0004: WORK_ORDER_STARTED -> CONTINUATION_CHECKPOINT -> VALIDATION_RECORDED -> HANDOFF_COMPLETED
actor = IMPLEMENTER во всех; timestamps монотонны (14:37:34Z -> 15:15:11Z); терминал 0004 последний
subject_sha всех событий = base 5fbd6d5…; tree(content-HEAD 80aed84) = f437c3ae8d1725a2c3929135fc9ce976be800823
  == заявленному в event 0003
JSON: 717 @ 80aed84 / 721 @ d01ff03 — сходится с событием и records-коммитом
```

Self-acceptance отсутствует: статус `ACCEPTED` не выставлен ни в одной новой поверхности; паспорт `HANDOFF_READY`; `state.json`/`plan.json` blob-идентичны base; маршрут REVIEWER (84f71e7, review/nl3-001-hinge-family-r1) → VERIFIER (этот вердикт) → Director checkpoint; merge — Human Gate.
