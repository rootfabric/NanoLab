# NL2-002 — VERIFIER VERIFICATION LOG (сырые проверки)

Независимый fresh VERIFIER. Worktree: `verify/nl2-002` @ `6cc7fdef24d9d3275b5a5a8efab4dc806e7cf893`, ветка `verify/nl2-002-validate-e1-r1`. Все команды исполнены верификатором непосредственно; выводы дословные.

## 1. Git-факты scope

```text
git fetch --all --prune (bare repo)                       -> ok
cat-file -t 6cc7fde... = commit; cat-file -t 0176098... = commit
rev-parse work/nl2-002-validate-e1-r1                     -> 6cc7fdef24d9d3275b5a5a8efab4dc806e7cf893
merge-base --is-ancestor 0176098 6cc7fde                  -> exit 0 (ANCESTRY OK)
diff --name-status 0176098..6cc7fde                       -> 48 файлов: 47 x A + 1 x M
M docs/work/SESSION_LOG.md                                -> removed=0, added=10 (APPEND-ONLY OK)
все 48 путей внутри allowed_paths WO-NL2-002              -> OUT-OF-SCOPE: нет
```

Forbidden-поверхности base vs subject (tree/blob SHA-256 git, идентичность = blob-идентичность рекурсивно): 13/13 IDENTICAL — `project/state.json` (264985a12a13), `project/plan.json` (c3e854dacbca), `PREREGISTRATION_E1_R1.md` (e04c68825d8b), `PREREGISTRATION_E1_R2.md` (315003ca5c9f), `ENGINE_ENVIRONMENT_R1.md` (a67b54353061), `PREREGISTRATION_E0_R1.md` (ec86972c4e43), `config` (6b72a59b04b1), `scripts/harness` (54eb97850970), `experiments/evidence/E1/E1-R1` (7adf8692981b), `docs/evidence/NL1-002` (d3098dd12f43), `docs/evidence/NL2-001` (a4f78b153df9), `docs/experiments` (1693a2cbdae9), `experiments/evidence/E0` (8ff493efce74).

Timeline freeze→campaign-start: `f34e62c` 21:21:21+10 < `42cb851` 21:23:45+10; freeze-коммит содержит ровно campaign.md + protocol.json + analyze_energy.sh; merge-base(freeze ⊂ campaign-start) = ok.

## 2. Инструмент анализа (байт-в-бит)

```text
git cat-file blob 77cfcc637df7c75446736cf1c3a71ea219a260c5 (не working copy)
sha256sum -> 747c5216589ab9270830a21eaf7f15d1aea742681360ac048f4392c2edfabd4d  MATCH пину protocol.json
git ls-tree: blob E1-R1/analyze_energy.sh == blob E1-R2/analyze_energy.sh == 77cfcc63  (байт-в-бит OK)
```

## 3. Digest-vs-blob (git cat-file, 15 записей ≥ 12)

Каждый из 5 артефактов (log.dat, energy.dat, trajectory.dat, last_conf.dat, resource_time.txt) × C001–C003 извлечён `git cat-file blob 6cc7fde:<path>` и сверён против `artifacts.manifest.json` (тоже из blob): SHA-256 + size_bytes + producer_run_id + subject_sha (f34e62ca…).

```text
DIGEST RESULT: pass=15 fail=0
MATCH E1-R2-C001 log.dat 6f5de751… 2203B | energy.dat 102d5331… 49049B | trajectory.dat 6c3a6de9… 44778B | last_conf.dat 106c59d6… 4477B | resource_time.txt 0b681816… 777B
MATCH E1-R2-C002 log.dat cdad3fe0… 2199B | energy.dat 08ddbbab… 49049B | trajectory.dat f22dd974… 44780B | last_conf.dat b2b91069… 4488B | resource_time.txt 139bba34… 775B
MATCH E1-R2-C003 log.dat bdda1547… 2198B | energy.dat d33dcd94… 49049B | trajectory.dat a0b136cb… 44862B | last_conf.dat 0ffd766c… 4505B | resource_time.txt 42be911e… 775B
```

Fixture pinned upstream (свежий `git fetch --depth 1 origin 00dc7fb9…` в пустой репозиторий; `rev-parse HEAD` = `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`): 4/4 SHA-256 MATCH с пинами protocol.json §protocol_subject: dsdna8.top f1aded90… 148B, init.dat 0ff76d54… 4498B, quick_input 8935c4bc… 533B, quick_compare 86a8b6ac… 51B.

## 4. Per-replica observable (опубликованный инструмент + независимый Decimal)

`analyze_energy.sh` (blob 77cfcc63) на published `energy.dat` blob'ах; независимый пересчёт среднего колонки 2 через Python Decimal (prec 50):

```text
E1-R2-C001: rows=1001 avg_col2=-1.36722173127 delta=+0.01248083017 T1_band=IN_BAND | decimal_mean=-1.3672217312687… IN_BAND
E1-R2-C002: rows=1001 avg_col2=-1.35818087512 delta=+0.02152168632 T1_band=IN_BAND | decimal_mean=-1.3581808751248… IN_BAND
E1-R2-C003: rows=1001 avg_col2=-1.35653082817 delta=+0.02317173327 T1_band=IN_BAND | decimal_mean=-1.3565308281718… IN_BAND
E1-R1-S001: rows=1001 avg_col2=-1.39393635864 delta=-0.01423379720 T1_band=IN_BAND | decimal_mean=-1.3939363586413… IN_BAND
```

Все 4 значения воспроизводят опубликованные дословно (11 знаков). NaN/Inf = 0; trajectory configs = 10/10/10; engine facts из log.dat blob'ов: RELEASE v3.7, GIT COMMIT 00dc7fb, T 0.097717, N=16 molecules=2, «END OF THE SIMULATION, everything went OK!» 3/3; wall/RSS resource_time.txt: 11.00/6604, 10.88/6604, 11.03/6468 — совпадают с published.

## 5. Независимый T2-прогон C-VERIFY (fresh rebuild)

Среда: WSL2 Ubuntu 24.04.2, та же машина. cmake 3.31.6 user-local tarball `cmake-3.31.6-linux-x86_64.tar.gz` SHA-256 `5a1133ff103c71eb5120e2cc3de922733e7d8a26a98ae716397e8676adb367bf` — MATCH пину ENGINE_ENVIRONMENT_R1 §2. Сборка §3: fetch exact `00dc7fb9…`, `cmake ../oxdna-src -DCMAKE_BUILD_TYPE=Release -DCUDA=OFF -DMPI=OFF`, `make -j20` → BUILD_EXIT=0.

```text
sizes (критерий §4): oxDNA 3375976 B | DNAnalysis 2957400 B | confGenerator 2201664 B  -> 3/3 байт-в-байт с пинами
sha256 (свежая сборка, ожидаемо != implementer из-за COMPILED ON): oxDNA c8fc06b671bf714c2e99af50f5cde6958282dbd8a624bb63d03fae9cc0a76b44
CMakeCache: CMAKE_BUILD_TYPE=Release, DOUBLE=ON, CUDA=OFF, MPI=OFF, NATIVE_COMPILATION=ON, JSON_ENABLED=ON, CMAKE_CXX_FLAGS пуст — флаги MATCH
```

Прогон (layout как у implementer: verbatim quick_input в run-каталоге, dsdna8.top/init.dat в родителе — `topology = ../dsdna8.top`, `conf_file = ../init.dat`):

```text
on-place sha256sum перед прогоном: 4/4 MATCH
command: /usr/bin/time -v ~/verify-nl2-002/build-oxdna-cpu/bin/oxDNA quick_input
EXIT_CODE=0; wall 0:11.11; max RSS 6332 KB; Exit status 0
log.dat: seeding the RNG with 319832093 | RELEASE: v3.7 | GIT COMMIT: 00dc7fb | N: 16, N molecules: 2 | END OF THE SIMULATION, everything went OK!
seed 319832093 — НОВЫЙ: не входит в опубликованные 7 (-200619630, -473348953, -547126645, -1610133928, -1641386734, 977680137, -999572227)
integrity: energy_rows=1001, trajectory_configs=10, NaN/Inf=0
analyze_energy.sh (blob 77cfcc63) на СОБСТВЕННОМ energy.dat:
  rows=1001
  avg_col2=-1.39396936364
  T1_band=IN_BAND
  delta_from_oracle=-0.01426680220
независимый Decimal: n=1001 mean=-1.3939693636363… verdict=IN_BAND
артефакты верификатора (disposable scratch, не в Git): energy.dat 39db0fb5… 49049B; trajectory.dat d1ca2fd2… 44737B; last_conf.dat d2088a62… 4463B; log.dat 42c3c329… 2200B
```

Техническая попытка №1 C-VERIFY: FAILED_TECHNICAL по вине верификатора (run-каталог без родительских `../init.dat`/`../dsdna8.top` — engine завершился fail-closed с `ERROR: Can't read configuration file '../init.dat'`, exit 1, wall 0.00 s, данных нет). Повтор — в новом каталоге с корректным layout; seed первой попытки (-516800233) нигде не используется. Технический исход и научный вывод разделены.

## 6. Статистика (Decimal, prec 60, из 11-значных published значений)

```text
vals = [-1.39393635864 (S001), -1.36722173127 (C001), -1.35818087512 (C002), -1.35653082817 (C003)]
mean    = -1.36896744830   MATCH (quantize 1E-11 == published)
SD(n-1) =  0.0172965670268… -> 0.01729656703  MATCH
range   =  0.03740553047   MATCH
per-replica |Δ|: 0.01423379720 / 0.01248083017 / 0.02152168632 / 0.02317173327 — все ≤ 0.15 -> 4/4 IN_BAND
Критерий E1-PROTO-R1 §9 (T1 PASS И все T2 IN_BAND) на 4 published-точках: ВЫПОЛНЕН (механически, воспроизведено)
```

## 7. Seed distinctness (из log.dat blob'ов)

```text
C001=-1641386734, C002=977680137, C003=-999572227  -> попарно различны: 3/3
vs S001=-200619630, P001=-473348953, P002=-547126645, P003=-1610133928 -> пересечений нет
```

## 8. Схемы и CLI (Windows Python 3.11.8 + jsonschema 4.22.0)

```text
experiment_cli validate runs/E1-R2-C001|C002|C003 -> ok=true, errors=[], warnings=[] 3/3 (terminal execution + analysis present)
work_cli    validate docs/work/executions/EX-NL2-002-R1 -> ok=true, HANDOFF_COMPLETED терминальный, has_post_terminal_corrections=false
cli        check-consistency -> ok=true (head 6cc7fde, frontier NL2, next NL2-002)
jsonschema Draft2020-12 + FormatChecker: 20/21 OK
  OK: 3 run-manifest.json + 9 run-events + 3 artifacts.manifest.json + passport.json + 4 work-events (16) + evidence-map... см. строку ниже
  FAIL: experiments/evidence/E1/E1-R2/evidence-map.json против config/control/harness/evidence-map.schema.v1.json (11 ошибок: additionalProperties + required checkpoint/claim_class/subject_sha/validation)
  КЛАССИФИКАЦИЯ: campaign-level evidence_map того же вида в ПРИНЯТЫХ предшественниках E1-R1 и E0-R4 даёт идентичные 11 ошибок — v1-схема описывает другой вид артефакта (checkpoint-уровень); форма campaign-map следует принятой конвенции E1-R1. Не является нарушением NL2-002; см. finding F-1 вердикта.
```
