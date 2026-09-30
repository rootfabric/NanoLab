"""Process isolation supervisor and negative-control scenario logic.

Contract (mission §11/§14; NATIVE_UBUNTU_EXECUTION_POLICY_R1 §3):
- scientific jobs run OUTSIDE agent sessions through systemd transient
  units; they must survive SSH disconnect, agent restart, terminal close
  and GitHub-runner service restart;
- CI is never the lifecycle owner of a scientific job: CI must not issue
  systemctl reboot/shutdown nor kill the executor cgroup;
- a deliberately killed job is recorded FAILED_TECHNICAL with the attempt
  preserved and the next retry receiving a NEW attempt ID (NC-U5).

Scenario evaluation functions are pure: the CLI executes real scenarios on
an eligible U1 host, while unit tests verify the decision logic itself.
"""

from __future__ import annotations

from typing import Any


def transient_service_argv(
    unit: str,
    command: list[str],
    working_directory: str | None = None,
    description: str | None = None,
    collect: bool = True,
) -> list[str]:
    """Build `systemd-run` argv for a detached transient service unit.

    The unit is owned by PID 1: closing the SSH session, restarting the
    agent process or restarting the GitHub runner service does not affect
    it. `--wait --pipe` lets the executor collect exit code/output; a
    long-lived scientific campaign drops `--wait --pipe` and reads results
    from the raw tree instead.
    """
    argv = ["systemd-run"]
    if collect:
        argv.append("--collect")
    argv.append(f"--unit={unit}")
    if description:
        argv.append(f"--description={description}")
    if working_directory:
        argv.append(f"--working-directory={working_directory}")
    return argv + list(command)


def scope_argv(unit: str, command: list[str], working_directory: str | None = None) -> list[str]:
    """Build `systemd-run --scope` argv (job in a dedicated scope unit)."""
    argv = ["systemd-run", "--scope", f"--unit={unit}"]
    if working_directory:
        argv.append(f"--working-directory={working_directory}")
    return argv + list(command)


def parse_is_active(result: dict[str, Any] | None) -> bool:
    """Interpret `systemctl is-active <unit>` output."""
    if not result:
        return False
    return (result.get("returncode") == 0) and ((result.get("stdout") or "").strip() == "active")


FORBIDDEN_CI_ACTIONS = (
    "systemctl reboot",
    "systemctl shutdown",
    "kill executor cgroup",
)


def ci_actions_policy_violation(actions: list[str]) -> list[str]:
    """Return violations when a CI workflow attempts forbidden lifecycle actions."""
    violations = []
    for action in actions:
        normalized = " ".join(str(action).split()).lower()
        for forbidden in FORBIDDEN_CI_ACTIONS:
            key = " ".join(forbidden.split()).lower()
            if key in normalized:
                violations.append(f"{action} (CI must not own scientific executor lifecycle)")
                break
    return violations


def nc_u1_evaluate(owner_session_gone: bool, job_still_running: bool) -> dict[str, Any]:
    """NC-U1: disposable job must keep running after SSH session close."""
    ok = owner_session_gone and job_still_running
    return {
        "control": "NC-U1",
        "pass": ok,
        "reason": "" if ok else "job must keep running after its owner session is gone",
    }


def nc_u2_evaluate(agent_restarted: bool, job_still_running: bool) -> dict[str, Any]:
    """NC-U2: job must survive agent process restart."""
    ok = agent_restarted and job_still_running
    return {
        "control": "NC-U2",
        "pass": ok,
        "reason": "" if ok else "job must survive agent process restart",
    }


def nc_u3_evaluate(runner_service_restarted: bool, job_still_running: bool) -> dict[str, Any]:
    """NC-U3: job must survive GitHub runner service restart (CI isolation)."""
    ok = runner_service_restarted and job_still_running
    return {
        "control": "NC-U3",
        "pass": ok,
        "reason": "" if ok else "job must survive GitHub runner service restart",
    }


def nc_u4_evaluate(ci_workspace_deleted: bool, raw_intact: bool, raw_outside_ci: bool) -> dict[str, Any]:
    """NC-U4: deleting the CI workspace must not touch scientific raw tree."""
    ok = ci_workspace_deleted and raw_intact and raw_outside_ci
    return {
        "control": "NC-U4",
        "pass": ok,
        "reason": "" if ok else "scientific raw tree must survive CI workspace cleanup",
    }


def nc_u5_evaluate(
    killed_deliberately: bool,
    recorded_failed_technical: bool,
    attempt_preserved: bool,
    retry_id_new: bool,
) -> dict[str, Any]:
    """NC-U5: deliberate kill => FAILED_TECHNICAL, attempt kept, retry new ID."""
    ok = killed_deliberately and recorded_failed_technical and attempt_preserved and retry_id_new
    return {
        "control": "NC-U5",
        "pass": ok,
        "reason": "" if ok else "kill must yield FAILED_TECHNICAL with preserved attempt and a fresh retry ID",
    }
