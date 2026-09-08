# NL0-002 — Immutable license evidence pins (REPAIR1)

Исполнение: `EX-NL0-002-R1-REPAIR1`. Назначение: устранение Verifier finding FIX 1 (`docs/evidence/NL0-002/FRESH_VERIFIER_R1.md` §3, commit `48d6d0c0089d985118e629ac459c7aa9d85e85eb`).

Проблема: колонка матрицы «Exact source/version» содержала только имена репозиториев/пакетов без immutable identity проверенной лицензии, поэтому license audit не был воспроизводимым. Решение: для каждой программной зависимости зафиксирован проверенный license subject — canonical repository (с GitHub repository id), checked commit, license path, Git blob SHA-1 и SHA-256 содержимого файла лицензии, SPDX-результат. Любой будущий аудит может восстановить точный проверенный текст по этим identity, независимо от дальнейшего движения upstream.

Метод проверки: GitHub REST API (`repos/…`, `repos/…/commits/…`, `repos/…/git/trees/…`, `repos/…/git/blobs/…`), дата проверки **2026-09-08** (checked_at для всех строк). Целостность содержимого подтверждена дважды: локальный git-style blob hash (`sha1("blob <size>\0" + content)`) совпал с blob SHA из tree API для всех 7 файлов (byte-exact). Это фиксация проверенного license subject, **не** выбор runtime-версий — пин конкретных releases/PyPI-версий остаётся за NL1-001.

## Таблица пинов

| Dependency | Canonical repository | Checked commit (2026-09-08) | License path | License blob SHA-1 | License SHA-256 | SPDX / license result |
|---|---|---|---|---|---|---|
| scadnano | github.com/UC-Davis-molecular-computing/scadnano (id 226161722), default branch `main` | `70f0e4bde70025cd43abfce1e390095f0d86625a` | `LICENSE.txt` | `191a099d5d32c0399669cd7b7df9aaadeeeb2331` | `1573dffcff6a09abe8e5369e5299377b9f43b8fa89ef9f48bcda976cabac1e15` | MIT (license endpoint: MIT; текст: «MIT License», Copyright (c) 2020 David Doty) |
| oxView | github.com/sulcgroup/oxdna-viewer (id 130886462), default branch `master` | `047e0bf718f315577556de2ba5a6be64dede48dc` | `LICENSE` | `94a9ed024d3859793618152ea559a168bbcbb5e2` | `8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903` | GPL-3.0 (license endpoint: GPL-3.0; текст: GNU GPL v3, 29 June 2007) |
| PyMBAR | github.com/choderalab/pymbar (id 9991771), default branch `main` | `ed40ec3bbef03bb08938ad1a74d459b0d1ab81f7` | `LICENSE` | `9cbae2a7e0268fef2d497cf112b5f41403016c4e` | `b06216b25962856729369804671b10ac7daed2237597f285abc540c363c19da2` | MIT (license endpoint: MIT; текст: copyright Shirts Lab / Chodera Lab, 2017) |
| AiiDA (aiida-core) | github.com/aiidateam/aiida-core (id 77234579), default branch `main` | `8cad70e2d235f54093406d8af06359450209f49e` | `LICENSE.txt` | `68314cde76f81978f36fb7cb0e2ca49fa04b1aab` | `ff614a96e214fded6f5745709783676e46d032b5fa3a32aaaabf80020bb3f388` | текст `LICENSE.txt` = MIT («The MIT License (MIT)»); GitHub repo-level detection = `NOASSERTION` (см. замечания) |
| aiida-shell | github.com/aiidateam/aiida-shell (id 451099332), default branch `master` | `e420c1d2cd7fc06882e538c643c5f0defa231789` | `LICENSE.txt` | `3985753502c0a5a4c1a4c225382b0c283ce19da3` | `fe6d111964cc801aac228825510d43d0bc3202fdcd4dfbeec36f4c63244b41b1` | MIT (license endpoint: MIT; текст: «MIT License») |
| Ax (Adaptive Experimentation) | github.com/facebook/Ax (id 169880381), default branch `main` | `778e22ffdb05fb8a0a5e8527c283d102a598f7da` | `LICENSE` | `b93be90515ccd0b9daedaa589e42bf5929693f1f` | `da6d3703ed11cbe42bd212c725957c98da23cbff1998c05fa4b3d976d1a58e93` | MIT (license endpoint: MIT; текст: «MIT License») |
| BoTorch | github.com/meta-pytorch/botorch (id 142940093), default branch `main` | `d4b9fc655034f6c6186f1cdc73398b47d3d55b7f` | `LICENSE` | `b93be90515ccd0b9daedaa589e42bf5929693f1f` | `da6d3703ed11cbe42bd212c725957c98da23cbff1998c05fa4b3d976d1a58e93` | MIT (license endpoint: MIT; текст: «MIT License») |

## BoTorch — canonical source и исторический alias

```text
BOTORCH_CANONICAL_SOURCE = github.com/meta-pytorch/botorch (repository id 142940093)
BOTORCH_HISTORICAL_ALIAS = github.com/pytorch/botorch -> server-side redirect
```

- Canonical репозиторий проекта BoTorch — `meta-pytorch/botorch`.
- Исторический селектор `pytorch/botorch` — redirect на **тот же** repository id `142940093` (проверено live 2026-09-08: запрос `repos/pytorch/botorch` отвечает `full_name = meta-pytorch/botorch`). Это один и тот же репозиторий, переименованный владельцем, а не fork.
- Проверенный commit `d4b9fc655034f6c6186f1cdc73398b47d3d55b7f`, `LICENSE` blob `b93be90515ccd0b9daedaa589e42bf5929693f1f` — байтово идентичен MIT blob Ax (`da6d3703…` SHA-256, стандартный MIT-текст Meta Platforms). Вывод матрицы «BoTorch = MIT» подтверждён по canonical source.

## Замечания

- **oxView**: blob `94a9ed024d3859793618152ea559a168bbcbb5e2` — тот же канонический Git blob полного текста GNU GPL v3, что и root `LICENSE` oxDNA (см. `RIGHTS_AND_REDISTRIBUTION_AUDIT.md` §1). Два независимых репозитория содержат идентичный GPLv3-текст; классификация GPL-3.0 подтверждена по immutable identity, а не по детекции GitHub.
- **AiiDA (aiida-core)**: repo-level license detection GitHub — `NOASSERTION` (в дереве есть дополнительные лицензионные файлы, напр. `open_source_licenses.txt` со списком зависимостей). Это не меняет вывод: проверенный root `LICENSE.txt` — стандартный MIT-текст (blob `68314cde…`, SHA-256 `ff614a96…`). Формулировка матрицы сохраняет оба факта.
- **Git blob SHA-1** — immutable identity в Git content-addressed storage: совпадение blob SHA гарантирует байтовое совпадение файла (проверено локально git-style hashing для всех 7 файлов). **SHA-256** записан как второй независимый дайджест содержимого.
- E1 (oxDNA root LICENSE, blob `94a9ed0…` @ `00dc7fb9…`) и E2 (отсутствие LICENSE в pinned tree) не пересматривались — их факты подтверждены Fresh Verifier R1 (§2, PASS) и остаются в `RIGHTS_AND_REDISTRIBUTION_AUDIT.md`.
- Записи отражают состояние default branch на момент проверки; последующее движение upstream не отслеживалось. Повторная проверка перед release — через сравнение blob SHA/SHA-256 с этой таблицей.

Это техническая фиксация проверенных лицензионных фактов, не юридическое заключение.
