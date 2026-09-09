# Verifier pytest runs (fresh exact-head P1.3)

Subject: verify/bus-001-r1 @ 60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c
Environment: Windows, Python 3.11.8, git 2.53.0.windows.1
User gitconfig: core.autocrlf=true, safe.bareRepository=explicit

## Run A - logs/pytest-windows-default-config.log
Command: python -m pytest tests/task_bus/ -v
Result: 1 failed, 38 passed, 1 skipped (49-51s)
Only failure: GitIntegrationTests::test_independent_clones_full_cycle_and_main_untouched
Failure point: tests/task_bus/test_task_bus.py:326 - the TEST harness itself calls
  git -C <temp bare remote> rev-parse main
and git refuses with:
  fatal: cannot use bare repository ... (safe.bareRepository is explicit)
This is the verification-harness assertion on the bare remote, NOT broker code
(tools/task_bus.py runs all git calls against non-bare working clones; ls-remote/push
address the bare remote by URL, which safe.bareRepository=explicit does not block).

## Run B - logs/pytest-windows-GIT_CONFIG_GLOBAL-NUL.log
Command: GIT_CONFIG_GLOBAL=NUL python -m pytest tests/task_bus/ -v
Result: 39 passed, 1 skipped (51.6s) - GREEN
Skipped: test_symlink_candidate_and_local_smoke_are_rejected
(skipTest: platform does not permit unprivileged symlinks - Windows without symlink privilege)

Conclusion: hypothesis confirmed; green/red conditions fully determined by user gitconfig
safe.bareRepository=explicit; broker behavior identical in both runs (all broker-side
operations passed in Run A as well - the red check is the tests own assertion).

## Run C - logs/cli-probes-run1.jsonl (scratch bare remote, CLI-only)
Script: C:\NanoLab\scratch\bus-verifier-probes\probe.py (verifier harness, outside repo)
Run dir: C:\NanoLab\scratch\bus-verifier-probes\probe-run-20260909-212122
Confirmed denials: P1 wrong-role claim -> TASK_NOT_CLAIMABLE;
P3 foreign token finish -> STALE_OR_FOREIGN_LEASE; P10 unknown actor status -> ACTOR_NOT_ALLOWED;
P7 duplicate init -> BUS_ALREADY_EXISTS; P5 candidate ref drift -> CANDIDATE_REF_DRIFT
(then repair in scratch, retry through pending message-id reuse -> committed);
P6 reviewer subject mismatch -> SUBJECT_MISMATCH; P9 PASS with failed check -> PASS_WITH_FAILED_CHECK;
P11 claim after terminal -> TASK_TERMINAL. Full happy path through CLI reached
COMPLETED_SANDBOX; status reports canonical_acceptance=false, mode=SANDBOX.
Lease expiry was demonstrated indirectly: reclaim succeeded only after 61s
(probe policy lease_seconds=60) - director reclaim of the still-active lease had
LEASE_NOT_EXPIRED available but the flow required expiry; explicit
LEASE_EXPIRED finish is covered in run 2.
Harness defects in run 1 (verifier-side, not broker): --message-id passed after
subcommand was rejected by argparse (claim implementer-a never landed), so
competing-claim/idempotent/lease-expired probes were re-run in run 2.

## Run D - subject/hash verification (exact 60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c)
git ls-remote origin:
  refs/heads/control/git-task-bus-r1   = 60bdca6a7c6fffed4c541d39bb44ec3cc8b0295c  MATCH (exact subject)
  refs/heads/work/bus-smoke-001-r1     = d5bfc55956722e241151e0ef6db5299ee7e55123  MATCH frozen pilot candidate (no drift)
  refs/heads/control/task-bus-pilot-r1 = 6e95891db110438c3a888aec9af7721ccdb63ceb  MATCH frozen pilot bus ref
rev-parse d5bfc55^{tree} = 07dc90857bb40f9bb7e4d991ff782d5ebbc044c3          MATCH frozen pilot tree
receipt blob in candidate tree:
  docs/work/pilots/BUS-SMOKE-001/receipt.json = 379c597d940fa9ded54ed9549d63a68ad48ead48 (100644)
  MATCH GIT_BLOB_SHA1 declared in POST_PILOT_CORRECTION_R1 section 3.
Blob identity vs EX-BUS-001-R1/evidence/validation.json:
  tools/task_bus.py            git blob a3d0556717f3320e885f4092f242bed53bf0584f  MATCH
  tests/task_bus/test_task_bus.py git blob 7f8c93972be0b4efe88204457eda92f15fa043b4  MATCH
Canonical blob sha256 (git cat-file blob | sha256, exact stored bytes):
  tools/task_bus.py            191b0d3004eebf03ee2424df44a08c78001c82de005f58285a29bb674021f825 (27313 B) MATCH
  tests/task_bus/test_task_bus.py 3f1a5d8ebd054abe7416d44b76cc03059f88c434734c21126b1a78018e5be341 (22996 B) MATCH
Windows checkout sha256 differs (CRLF): tools 33352007... (27839 B), tests 68eeef0a... (23472 B).
These are CHECKOUT_SHA256 values, exactly the terminology correction documented in
POST_PILOT_CORRECTION_R1 section 3; validation.json values are canonical blob hashes.

## Run E - canonical acceptance scan
git grep ACCEPTED over the subject tree (AGENTS.md, DIRECTOR.md, docs/control,
docs/work/executions/EX-BUS-*, config/control/task-bus): every hit is a
prohibition or negation ("COMPLETED_SANDBOX != ACCEPTED", "not ACCEPTED",
"DO NOT treat COMPLETED_SANDBOX as ACCEPTED"). validation.json:
canonical_acceptance=false, production_activation=false. No canonical acceptance
of BUS-SMOKE-001 or BUS-001 is declared anywhere in the subject.
