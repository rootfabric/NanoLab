# NL0-002 — Fresh Independent Verifier R1

Роль: `VERIFIER`. Work Order: `NL0-002`. PR: `#17`.

```text
VERIFIED_HEAD        = 495b03391e7eff72bbfbb5c5912e35ef9035b868
VERIFIED_TREE        = 81d287a7b74b61edd10ecfa0a82d0cf92dfd545b
SUBSTANTIVE_HEAD     = 712dab78170b2ac50c088cda4265905e3b77a12a
SUBSTANTIVE_TREE     = 968aafd9e538835419070a7b75da579f8e33ef8e
BASE_SHA             = 95b1319600bcc64572d84c0456acb927802ab806
CURRENT_MAIN         = 95b1319600bcc64572d84c0456acb927802ab806
EPOCH_DRIFT          = NONE / CONTINUE

VERDICT              = FAIL
DISPOSITION          = FIX_REQUIRED
```

Причина FAIL не в основных фактах прав или Harness. Основные факты независимо подтвердились. Блокируют приёмку три точечных дефекта самого licensing guidance, который является главным deliverable NL0-002.

## 1. Exact-head / scope / Harness — PASS

Live PR #17 остаётся OPEN/mergeable и указывает на exact candidate `495b03391e7eff72bbfbb5c5912e35ef9035b868`. Commit tree = `81d287a7b74b61edd10ecfa0a82d0cf92dfd545b`.

Candidate имеет parent `712dab78170b2ac50c088cda4265905e3b77a12a`; compare `712dab7...495b033` показывает один handoff commit. Он меняет только terminal binding/status surfaces; substantive research result не меняется.

Все 16 changed files PR находятся внутри `passport.allowed_paths`; `project/state.json` и `project/plan.json` не изменены. Self-accept отсутствует.

Execution package `EX-NL0-002-R1` содержит ровно:

```text
0001 WORK_ORDER_STARTED
0002 CONTINUATION_CHECKPOINT
0003 IMPLEMENTATION_COMMITTED
0004 VALIDATION_RECORDED
0005 HANDOFF_COMPLETED
```

`passport.json` имеет `LOW / C0_SOFTWARE_ONLY / HANDOFF_READY`. Terminal event последний и привязан к substantive HEAD `712dab78170b2ac50c088cda4265905e3b77a12a`. `summary.md` существует.

Текущий `scripts/harness/work_cli.py` прочитан независимо. По exact live package его predicates воспроизводятся как `close => ok=true`: один START, START первый, один terminal, terminal последний, IDs совпадают, все subject SHA = 40 lowercase hex, summary существует.

```text
HARNESS_CLOSE_CHECK = PASS
SCOPE_CHECK         = PASS
STATE_SAFETY_CHECK  = PASS
```

## 2. Core rights facts — PASS

### E1 oxDNA

Pinned subject: `lorenzo-rovigatti/oxDNA@00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`.

Commit tree independently read as `f03ce1de5c0f3a336cb00ad363686c4841600d10`. Root tree contains:

```text
LICENSE blob = 94a9ed024d3859793618152ea559a168bbcbb5e2
```

LICENSE content is GNU GPL Version 3, 29 June 2007. Therefore the recorded primary fact `E1 upstream root license = GPL-3.0` is confirmed.

Conservative project policy `DOWNLOAD_ON_SETUP` is acceptable and avoids copying the selected fixture into NanoLab while the project's own release policy is unresolved.

```text
E1_LICENSE_FACT = PASS
```

### E2 hinge pack

Pinned tree `b2d6cebc7a33ed13e4e9c8d79fe8350ce11e82b9` was independently read recursively (`truncated=false`). It contains the five design JSONs, Init_Hinges, five top/conf pairs, pro_CPU/pro_GPU and MovieS1, but no `LICENSE`, `COPYING` or `NOTICE` anywhere.

Therefore:

```text
REDISTRIBUTION_RIGHTS = UNKNOWN
REFERENCE_ONLY        = conservative safe project policy
```

is correct. The candidate correctly does not turn public GitHub visibility into permission.

```text
E2_RIGHTS_FACT = PASS
```

### Software dependencies

Primary LICENSE files independently checked:

```text
scadnano       = MIT
oxView         = GPL-3.0
PyMBAR         = MIT
AiiDA          = MIT
aiida-shell    = MIT
Ax             = MIT
BoTorch        = MIT
```

BoTorch has moved from historical `pytorch/botorch` to canonical `meta-pytorch/botorch`; the old repository selector redirects to the same repository ID and current canonical LICENSE remains MIT.

The main license classifications are therefore factually supported.

## 3. REQUIRED FIX 1 — audit evidence for non-E1/E2 dependencies is not pinned

The matrix column is named `Exact source/version`, but for scadnano, oxView, PyMBAR, AiiDA, aiida-shell, Ax and BoTorch it records only repository/package names, not an exact commit/tag/release or immutable LICENSE object identity.

That is insufficient for a durable NanoLab rights audit: a later license change could make the report impossible to reconstruct. NL1 may pin runtime versions later, but NL0-002 still needs to pin **the license evidence it actually inspected**.

Required repair for each software dependency:

```text
canonical repository
checked commit SHA or release tag
license path
license blob SHA (or immutable content digest)
SPDX/license conclusion
```

Runtime package version may remain delegated to NL1-001; the license snapshot itself must be immutable now.

Also update BoTorch source to canonical `meta-pytorch/botorch`, optionally recording `pytorch/botorch` as redirect/historical alias.

## 4. REQUIRED FIX 2 — GPL aggregation/compatibility wording is too strong

`RIGHTS_AND_REDISTRIBUTION_AUDIT.md` currently says, in effect, that vendoring GPLv3 fixtures into the NanoLab repository with permissively licensed NanoLab code creates a mixed work/conflict with Apache/MIT options.

That is too categorical. GPLv3 itself explicitly distinguishes an **aggregate** of separate independent works from a covered combined work. Merely placing GPL-covered files and permissively licensed independent files in one repository/distribution does not by itself determine that all independent NanoLab code becomes GPL-covered.

At the same time, the opposite shortcut is also unsafe: the matrix groups `oxDNA / oxpy` as separately installed dependencies and says copyleft does not automatically reach NanoLab. `oxpy` is a Python binding and future same-process import/linking/integration can raise a different combined-work question than invoking an independent executable.

Required repair:

- replace categorical `conflict with Option A/B` wording with neutral, accurate language;
- distinguish `aggregate / separate executable / same-process binding or linking / modified GPL code`;
- state that Apache-2.0 and MIT source files can coexist with GPLv3 material under appropriate distribution structure, while obligations for a combined covered work depend on integration and conveyance;
- classify the future `oxpy` integration/bundling boundary as `REQUIRES_OWNER_DECISION / LEGAL_REVIEW` before a release architecture is fixed;
- keep the current conservative `DOWNLOAD_ON_SETUP / do not vendor yet` recommendation if desired.

Verifier is not issuing a legal conclusion; the required change is precisely to avoid the candidate issuing one too strongly.

## 5. REQUIRED FIX 3 — GPLv3 obligations should not be summarized as `+NOTICE`

The matrix says for E1 fixtures: `allowed under GPLv3 (+NOTICE)` and later speaks about a future NOTICE file.

A generic standalone `NOTICE` file is not itself the defining GPLv3 obligation. For source conveyance the license requires preserving appropriate copyright/license/no-warranty notices and providing the GPL license text; object-code conveyance has corresponding-source requirements depending on the chosen method.

Required repair:

- replace `(+NOTICE)` with wording such as `under GPLv3 terms; preserve applicable notices and provide license copy; corresponding-source obligations apply where relevant`;
- keep scientific citation policy separate from legal license obligations.

## 6. NON-BLOCKING RANK-UP MOVES

1. `summary.md` should contain literal `CANDIDATE_HEAD` and `CANDIDATE_TREE` values instead of referring to PR/binding indirectly. Current Harness validator does not require this, so it is not a blocking defect.
2. Clarify the count `9 CLEAR`: the table also has the E1 fixture as a separate CLEAR row; distinguish `9 software dependencies CLEAR` from `E1 fixture CLEAR` to avoid ambiguity.
3. When the owner eventually chooses a NanoLab license, re-evaluate actual packaging architecture rather than deciding compatibility from dependency license names alone.

## 7. What does NOT need repair

Do not redo the whole audit. These conclusions survived falsification:

```text
E1 upstream GPL-3.0                         CONFIRMED
E2 no license in full pinned tree           CONFIRMED
E2 redistribution UNKNOWN                   CONFIRMED
REFERENCE_ONLY for E2                       ACCEPTABLE conservative policy
S08 kept out of executable seed             ACCEPTABLE
NANOBASE per-record UNKNOWN                 ACCEPTABLE
NanoLab license not self-assigned           PASS
third-party files copied                    NONE
simulations run                             NONE
state self-accept                           NONE
Harness close structure                     PASS
```

## Final

```text
VERIFIED_HEAD          = 495b03391e7eff72bbfbb5c5912e35ef9035b868
CURRENT_MAIN           = 95b1319600bcc64572d84c0456acb927802ab806
EPOCH_DRIFT            = CONTINUE
VERDICT                 = FAIL
REQUIRED_FIXES          = 3
NEXT_ACTOR              = IMPLEMENTER_REPAIR
```

После bounded repair нужен fresh exact-head Verifier. Reviewer остаётся optional по LOW-risk routing, но был бы полезен, если repair снова вводит substantive interpretation GPL linking/bundling.