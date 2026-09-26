# P1 Recovery Incidents — EX-NL5-002-E-R1 (append-only)

```text
EXECUTION_ORCHESTRATION_DEVIATION (P1 side) = YES
SCIENTIFIC_PROTOCOL_MUTATION               = NO
```

## What happened

1. **Original wave interrupted (2026-09-20 ~21:28 UTC)**: all detached P1 processes were
   killed mid-run (no exit codes, truncated trajectories) when the WSL2 instance was
   terminated on DESKTOP-QNAGSTI. 0b S001–S008 (already exit=0) were untouched;
   0b S009–S010 and 32b S001–S006 superseded as failed attempts; 32b S007–S010 had
   never been launched.

2. **Recovery (2026-09-25)**: append-only retry chain per slot (`-R1`, `-R2`, ...),
   identical frozen seeds/steps/variants/engine/package/analyzer. Never restarted any
   exit=0 run. Superseded attempt directories are preserved verbatim in the workspace
   and enumerated in `run_output_digests_p1.json`.

3. **Attempt inflation (R1 … R21)**: during the recovery window, a parallel
   maintenance loop on the same author machine (self-hosted CI runner for
   `rootfabric/distributed-world-simulator`, job 36137485420) repeatedly executed
   `wsl --shutdown` to satisfy its `LOW_FREE_RAM`/`FOREIGN_GODOT_PROCESS` preflight,
   terminating the WSL2 VM — and with it every in-flight P1 attempt — many times.
   Root causes were later removed on the host side:
   - WSL2 memory capped (`C:\Users\root\.wslconfig`: `memory=3GB`), freeing ~10 GB;
   - foreign Godot editor processes killed;
   - the CI job then completed **success** (2026-09-26 03:34 local) and the idle
     destructive loop was stopped.
   Each termination is a purely technical event; every retry kept the frozen seed,
   so the final attempt per slot is a faithful, deterministic replication of the
   frozen protocol. Scientific pins were never changed.

## Why paired inference is not invalidated

- Pairing is by frozen seed S001–S010 and identical protocol on both legs.
- P1 inputs/seeds were frozen before any campaign data; no P1 run was selected,
  tuned, or restarted based on any scientific output (angles were never read during
  recovery; classification used exit codes and artifact completeness only).
- The final attempt per slot either reaches exit=0 (valid single uninterrupted run
  of the frozen protocol) or the slot stays incomplete. No partial trajectories are
  ever analyzed.

```text
Recorded: 2026-09-26, SCIENTIFIC_OPERATOR / RECOVERY AGENT (DESKTOP-QNAGSTI)
```
