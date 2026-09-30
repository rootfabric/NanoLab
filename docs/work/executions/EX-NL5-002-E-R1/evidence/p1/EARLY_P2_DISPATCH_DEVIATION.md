# Early P2 Dispatch Deviation — EX-NL5-002-E-R1

```text
EXECUTION_ORCHESTRATION_DEVIATION = YES
SCIENTIFIC_PROTOCOL_MUTATION     = NO
```

## Record (append-only, added with P1 completion evidence)

- **What happened**: The P2 leg was dispatched (event `0004-continuation-p2-dispatched.json`,
  2026-09-21T21:27:22Z) **before durable P1-complete evidence existed**, by explicit
  Director override, after the P1 24h per-replica hard-kill deadline (2026-09-21T18:54Z)
  passed with no P1 evidence push and an unresponsive P1 operator session on the author
  machine (DESKTOP-QNAGSTI).
- **Why it is an orchestration deviation only**: the scientific pins were frozen before any
  campaign data and were NOT changed by the early dispatch — identical seed list
  S001–S010 on both legs (paired design), same steps (0b: 200000, 32b: 150000),
  same variants, same engine source commit `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`,
  same package `nanolab-components 0.1.1` (RELEASE_MANIFEST sha256 exact match),
  same frozen analyzer `convention/analyze_hinge.py`.
- **Actual P1 condition at dispatch time**: 8/20 P1 runs COMPLETE_EXIT_0 (0b S001–S008);
  8 runs interrupted mid-flight (processes killed, no exit codes, truncated trajectories);
  4 runs (32b S007–S010) never launched. P1 was subsequently recovered append-only on the
  author machine: 8 technical retries with `-R1` suffixes keeping frozen seeds, 4 missing
  runs launched with their original IDs; no exit=0 run was restarted.
- **Paired-inference impact**: pairing is by frozen seed and identical protocol, not by
  wall-clock ordering; P2 results could not feed back into P1 execution (P1 seeds, inputs
  and engine were frozen and already on disk; nothing about P1 was selected or tuned after
  seeing P2 data). The fresh Reviewer must still explicitly answer whether this deviation
  invalidates paired scientific inference (YES/NO) with justification.

```text
Recorded: 2026-09-25, SCIENTIFIC_OPERATOR / RECOVERY AGENT (DESKTOP-QNAGSTI)
Supersedes: nothing. Rewrites: nothing. P2 evidence: untouched.
```
