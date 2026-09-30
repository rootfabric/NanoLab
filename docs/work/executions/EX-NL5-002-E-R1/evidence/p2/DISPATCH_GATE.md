# P2 DISPATCH GATE — durable note (EX-NL5-002-E-R1, leg P2)

Status: PREPARED, DISPATCH GATED.

Gate condition (binding, per director routing decision of 2026-09-21):
P2 physics (scheduler.sh) may start only AFTER the durable P1 evidence commit
(P1 20/20 final runs + artifact digest manifest + packaged analysis) exists on
origin branch work/nl5-002-e-platform-sensitivity-r1.

Watched state as of this note:
- origin tip = db40c0b041a39297f9bd55723936d6eb25fa0ede
  (= START+launch+wave1 checkpoints; NO P1-complete commit yet)
- last durable P1 record: wave 1 complete 8/8 (0b S001-S008 exit=0, ended
  18:54:05-18:59:00Z), wave 2 in flight since 18:54:18Z (0b S009/S010,
  32b S001-S006), queue 32b S007-S010
- P1 projected 20/20 was ~2026-09-21T01:30Z; P1 24h hard-kill deadline is
  2026-09-21T18:54Z (from wave-2 start)

On gate open, dispatch sequence (all pre-validated):
1. bash /home/rdpuser/nl5-002-e-p2/workspace/scheduler.sh   (detached: setsid nohup)
2. monitor: bash /home/rdpuser/nl5-002-e-p2/workspace/status.sh   (technical only)
3. bash /home/rdpuser/nl5-002-e-p2/workspace/wait_and_analyze.sh  (detached; auto-runs packaged analysis)
4. python3 /home/rdpuser/nl5-002-e-p2/workspace/build_run_output_digests.py
5. commit P2 evidence (passport_p2.json + gate/digest evidence + events) to
   local worktree /home/rdpuser/NanoLab/nl5-002-e-p2-exec, rebase on live
   origin tip, push

Boundary (frozen): per-replica medians are recorded by the packaged analyzer
only as execution outputs; NO paired differences, shift_v, bootstrap CI,
ratio_v, or any platform verdict may be computed until P1+P2 data for the same
10 seeds exist per variant (10 complete pairs each).

## Session wake-up map (operator session on outenemy, 2026-09-21)

- origin watcher (10-min poll, started ~12:11Z, 60 polls): exits EARLY with
  "NEW_ORIGIN_TIP=..." on the P1 evidence push; expires ~22:11Z otherwise.
- hard-kill tripwire: fires 19:24Z (18:54Z P1 deadline + 30 min grace) ->
  escalate P1 recovery to the human (P1 machine session required).
- goal rounds: exhausted ~14:35Z; thereafter the two background-job
  notifications above are the wake-up mechanism.
- P2 pre-flight validation completed 12:28-12:57Z: engine launch x2 (smoke),
  scheduler concurrency logic, packaged analyzer on a real 4000-step
  trajectory (report structurally identical to accepted B-R2 analyses),
  digest manifest builder. All PASS. Nothing left to pre-build.

## GATE OPENED BY DIRECTOR DECISION
- 2026-09-21T19:25Z: P1 hard-kill deadline (18:54Z) passed with no evidence push;
  origin tip still db40c0b. Director selected 'Dispatch P2 now' (early dispatch),
  accepting that paired statistics still wait for the P1 evidence commit.
- P2 dispatch executed 2026-09-21T19:26Z on outenemy (host = frozen P2 platform).
- P1 recovery remains a human-side dependency on DESKTOP-QNAGSTI; origin watcher continues.
