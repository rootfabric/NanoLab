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
