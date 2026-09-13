# Branch passport — EX-NL4-002-E3-MECH-R1

- Branch: `work/nl4-002-e3-mech-r1` (from `main` @ `592c4a1`), worktree `C:\NanoLab\nl4-002-e3`.
- Scope (WO-NL4-002 phase 1): (1) real `ExecutorAdapter` (`scripts/nl4/real_executor.py`, oxDNA via WSL, digest-gated inputs); (2) mechanical E3 arms **random** and **grid** — 5 runs × 50000 steps each, equal budget, parallel runs.
- LLM arm is explicitly out of scope here (separate fresh session on `work/nl4-002-e3-llm-r1` after mech merge).
- Claim ceiling: C0_SOFTWARE_ONLY / measured E3 comparison data for two mechanical arms, no physics interpretation, no "AI contribution" claims (LLM arm not yet run).
- Engine: WSL `/home/yurig/nl1-002/build-oxdna-cpu/bin/oxDNA` (source `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`).
- Candidate space narrowing (runner-level, documented as deviation): variants {0b, 11b, 32b, 53b}; 74b excluded by BLOCKED status (EX-NL3-002-PARAM-74B-R1). `scripts/nl4/allowlist.json` is NOT modified.
- Arm manifests: 0b frozen in-tree (EX-NL3-002-PROTO-R1); 11b/32b/53b copied verbatim from `origin/work/nl3-002-summary-r1`.
- Stop conditions: digest FAIL → BLOCKED; WSL infra failure → BLOCKED; ≤1.2 h wall per run.
