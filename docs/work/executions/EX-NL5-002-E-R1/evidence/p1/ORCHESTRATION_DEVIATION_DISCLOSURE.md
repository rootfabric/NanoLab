# EX-NL5-002-E-R1 — Execution orchestration deviation disclosure (P1 leg)

```text
EXECUTION_ORCHESTRATION_DEVIATION = YES
SCIENTIFIC_PROTOCOL_MUTATION     = NO
```

## What happened

The P2 leg was dispatched on the frozen P2 platform (outenemy) at
2026-09-21T21:25Z by an explicit **Director override**, BEFORE durable
P1-complete evidence existed on this branch (event
`0004-continuation-p2-dispatched.json`). The stated cause: the P1 24h
per-replica hard-kill deadline had passed with no P1 evidence push and the
P1 operator session on the author machine (DESKTOP-QNAGSTI) unresponsive
for ~24h.

## What was NOT changed (scientific pins untouched)

- seeds S001–S010 (identical paired list on P1 and P2, frozen in WO before any data);
- variants 0b + 32b, steps (200000 / 150000), windows;
- engine commit 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591 (fresh convention builds per platform);
- package nanolab-components 0.1.1, convention/analyze_hinge.py (single frozen analyzer);
- frozen statistical plan (shift_v, raw MAD, within_v, ratio_v, bootstrap
  RNG seed 902107, decision rule) — no paired statistic was computed before
  BOTH legs' evidence existed in Git;
- concurrency policy (max 8) and run-ID discipline (failed IDs never reused;
  technical retries take `-R1` with the same frozen seed).

## P1-side technical history (recovery facts)

- Original wave (2026-09-20): PLATSENS-P1-0B-S001..S008 completed exit=0.
- PLATSENS-P1-0B-S009/S010 and PLATSENS-P1-32B-S001..S006 were killed
  mid-run by a WSL shutdown (no exit code, truncated trajectories) —
  recorded as superseded failed attempts, directories preserved untouched.
- PLATSENS-P1-32B-S007..S010 never started in the original wave (no
  simulation output existed) — launched by the recovery scheduler under their
  ORIGINAL IDs with frozen inputs.
- Retries PLATSENS-P1-0B-S009-R1 / S010-R1 / 32B-S001-R1..S006-R1 use the
  same frozen seed, variant, steps, engine, package and protocol; superseded
  attempt directories were not overwritten.
- **Second host interruption (2026-09-25 ~12:55Z)**: a WSL VM restart killed
  all 8 running -R1 retry processes mid-run (~61k/200k steps; no exit codes,
  truncated trajectories). Recorded as superseded failed attempts;
  second-generation retries (-R2) were opened with the same frozen
  seeds/inputs via an idempotent supervisor (append-only IDs preserved).
  This is an infrastructure failure on the author machine, not a scientific
  protocol change; no completed exit-0 run was ever touched.

## Inference impact assessment (for the fresh Reviewer to confirm)

The paired design is defined by frozen seeds/inputs/engine/package/analyzer,
which are platform-independent and were never exposed to dispatch ordering.
P2 execution could not observe P1 results (P1 angles were not read before P2
completion; P1 evidence did not exist at P2 dispatch). Therefore the
orchestration deviation does not alter the statistical pairing or the
frozen decision rule; it must nevertheless be explicitly reviewed
(Reviewer must answer: does early P2 dispatch invalidate paired scientific
inference? YES/NO).
