# NL0-002 — Exact-Head Verifier R2

Роль: `VERIFIER`. Work Order: `NL0-002`. PR: `#17`. Это новый exact-head verification pass после bounded repair R1; Verifier не участвовал в Implementer repair.

```text
ORIGINAL_FAILED_HEAD = 495b03391e7eff72bbfbb5c5912e35ef9035b868
REPAIRED_PR_HEAD     = 86be310c93aeb0dc92e7992f5492933b08265984
REPAIRED_PR_TREE     = 45be9fe20ceddc6f04e96daa3a457afac9d5004e
SUBSTANTIVE_HEAD     = cd55320441c2c904f8e406870c902fbff587c602
SUBSTANTIVE_TREE     = 131a54fe787294dbf43c45279270521326d4f939
CURRENT_MAIN         = 95b1319600bcc64572d84c0456acb927802ab806
EPOCH_DRIFT          = NONE / CONTINUE

VERDICT              = PASS
NEXT_ACTOR           = DIRECTOR / HUMAN MERGE GATE
```

## 1. Exact-head binding — PASS

Live PR #17 remains OPEN, mergeable, unmerged and points to `86be310c93aeb0dc92e7992f5492933b08265984`. Current canonical `main` remains `95b1319600bcc64572d84c0456acb927802ab806`, so no epoch drift has appeared since the original NL0-002 base.

Repair ancestry is linear from the previously failed candidate:

```text
495b0339
  -> ba389582   repair execution START
  -> 2e551d31   immutable license evidence pins
  -> 9e481258   GPL boundary/obligations corrections
  -> cd553204   validation/substantive repaired head
  -> 86be310c   handoff commit
```

Terminal `HANDOFF_COMPLETED.subject_sha` is bound to `cd553204...`, and `cd553204...86be310c` is a single handoff commit. It does not change the licensing conclusions; it adds handoff/status/summary material and appends the repair record to `SESSION_LOG.md`.

## 2. Verifier R1 FIX 1 — immutable license evidence — PASS

`docs/evidence/NL0-002/LICENSE_EVIDENCE_PINS_R1.md` now records for all seven non-E1/E2 software dependencies:

- canonical repository and GitHub repository id;
- exact checked commit;
- license path;
- Git blob SHA-1;
- content SHA-256;
- SPDX/license conclusion.

Independent exact-ref reads confirmed that the recorded commits resolve to the expected license texts:

```text
scadnano     @ 70f0e4bd... LICENSE.txt = MIT
oxView       @ 047e0bf7... LICENSE     = GPLv3
PyMBAR       @ ed40ec3b... LICENSE     = MIT
AiiDA        @ 8cad70e2... LICENSE.txt = MIT text (repo detection NOASSERTION retained)
aiida-shell  @ e420c1d2... LICENSE.txt = MIT
Ax           @ 778e22ff... LICENSE     = MIT
BoTorch      @ d4b9fc65... LICENSE     = MIT
```

BoTorch is correctly bound to canonical `meta-pytorch/botorch` repository id `142940093`; historical `pytorch/botorch` is documented as the redirect/old alias.

The repair distinguishes immutable license-evidence pins from future runtime package/version pins, which remain NL1-001 work. Required FIX 1 is closed.

## 3. Verifier R1 FIX 2 — GPL boundary wording — PASS

The categorical pre-repair statement about permissive NanoLab code and vendored GPL material has been removed. The repaired matrix/audit explicitly distinguish:

```text
AGGREGATE
SEPARATE_EXECUTABLE
SAME_PROCESS_BINDING
MODIFIED_GPL_CODE
```

They now state conservatively that independent permissive works can coexist with GPL-covered material in an aggregate, while obligations for a combined covered work depend on the actual integration/conveyance model.

Crucially, `oxDNA executable` and future same-process `oxpy` binding are no longer treated as the same packaging situation. Same-process `oxpy` integration is explicitly:

```text
REQUIRES_OWNER_DECISION
REQUIRES_LEGAL_REVIEW
```

before release architecture is fixed. `DOWNLOAD_ON_SETUP / NO_VENDORING_YET` remains a conservative project policy, not a legal conclusion. Required FIX 2 is closed.

## 4. Verifier R1 FIX 3 — GPL obligations wording — PASS

The shorthand `GPLv3 (+NOTICE)` has been removed. The repaired text instead separates scientific citation from legal license obligations and summarizes GPLv3 conveyance conservatively as preserving applicable notices, providing the GPL license copy for covered-source conveyance, and satisfying corresponding-source obligations where relevant.

The documents explicitly say that a generic standalone `NOTICE` file is not itself the defining GPLv3 requirement. Required FIX 3 is closed.

## 5. Repair Harness / scope / state safety — PASS

Repair execution:

```text
EX-NL0-002-R1-REPAIR1
risk  = LOW
claim = C0_SOFTWARE_ONLY
status = HANDOFF_READY
```

contains exactly five ordered events:

```text
0001 WORK_ORDER_STARTED
0002 CONTINUATION_CHECKPOINT
0003 IMPLEMENTATION_COMMITTED
0004 VALIDATION_RECORDED
0005 HANDOFF_COMPLETED
```

The current `work_cli.py` predicates are satisfied: one START and it is first; one terminal and it is last; execution/work-order ids match; all subject SHAs are 40 lowercase hex; `summary.md` exists. Repair passport allowed paths contain all repair surfaces.

The original `EX-NL0-002-R1` terminal chain is not superseded or appended; the repair uses a distinct execution package. `project/state.json` and `project/plan.json` remain unchanged. No simulation was run and no third-party scientific input was copied.

```text
HARNESS_CLOSE_CHECK = PASS
SCOPE_CHECK         = PASS
STATE_SAFETY_CHECK  = PASS
```

## 6. Confirmed core findings retained

The bounded repair did not regress the already verified core conclusions:

```text
E1 oxDNA root license       = GPL-3.0
E1 project mode             = DOWNLOAD_ON_SETUP
E2 license in pinned tree   = NOT LOCATED
E2 redistribution rights    = UNKNOWN
E2 project mode             = REFERENCE_ONLY
NANOBASE                    = UNKNOWN per-record
S08                         = RESTRICTED/reference-only project policy
NanoLab own license         = NOT ASSIGNED
SIMULATIONS_RUN             = NONE
THIRD_PARTY_FILES_COPIED    = NONE
```

## 7. Non-blocking provenance warnings

These do not alter the verdict but should feed Harness hardening:

1. `cd553204...86be310c` also appends the repair summary to `docs/work/SESSION_LOG.md`; therefore the handoff description saying the final commit changes only terminal/status/summary surfaces is slightly incomplete. The added log text merely restates already committed repair facts and does not change the substantive licensing result.
2. Manual `timestamp_utc` values in the repair event JSON are not reliably tied to Git commit timestamps. Git commit ancestry is authoritative for ordering, so acceptance is not blocked, but future Harness should either generate timestamps automatically or validate them against commit time/monotonicity.

## 8. Final verdict

All three blocking findings from Fresh Verifier R1 are repaired at the exact PR head. No new blocking scope, state, or scientific claim defect was found.

```text
VERIFIED_HEAD       = 86be310c93aeb0dc92e7992f5492933b08265984
VERIFIED_TREE       = 45be9fe20ceddc6f04e96daa3a457afac9d5004e
EPOCH_DRIFT         = CONTINUE
VERDICT             = PASS
REQUIRED_FIXES      = NONE
NON_BLOCKING        = 2 provenance/harness hardening notes
NEXT_ACTOR          = DIRECTOR / HUMAN MERGE GATE
```
