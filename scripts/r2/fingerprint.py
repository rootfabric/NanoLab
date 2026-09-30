"""Host fingerprint capture and native-U1 eligibility validation.

Contract: docs/research/ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md §2/§4/§9 and
docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md §1 (OUTENEMY_ROLE =
EXTERNAL_U2_ONLY). Values are captured AS FACT; nothing is tuned toward R1.

Eligibility (all required, any failure is a named reason):
- Linux kernel (uname);
- virtualization "none" per systemd-detect-virt (exit code 1 means none) and
  no Microsoft kernel marker in /proc/version (WSL exclusion);
- native filesystem for "/" among ext4/xfs/btrfs (no bind mount, no overlay);
- systemd available (systemctl --version);
- hostname NOT in the forbidden author-host list ("outenemy" is
  EXTERNAL_U2_ONLY and can never become AUTHOR_U1).

All command execution is injected via a ``runner`` callable so validation
logic is unit-testable on any host without spawning processes.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from . import FORBIDDEN_AUTHOR_HOSTNAMES, NATIVE_FILESYSTEMS

Runner = Callable[[Iterable[str]], dict[str, Any]]

FINGERPRINT_COMMANDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("hostname", ("hostname",)),
    ("uname", ("uname", "-a")),
    ("os_release", ("cat", "/etc/os-release")),
    ("virtualization", ("systemd-detect-virt",)),
    ("proc_version", ("cat", "/proc/version")),
    ("cpu", ("lscpu",)),
    ("memory", ("free", "-h")),
    ("root_filesystem", ("df", "-T", "/")),
    ("gcc", ("gcc", "--version")),
    ("gxx", ("g++", "--version")),
    ("cmake", ("cmake", "--version")),
    ("make", ("make", "--version")),
    ("python3", ("python3", "--version")),
    ("git", ("git", "--version")),
    ("systemctl", ("systemctl", "--version")),
)


def default_runner(argv: Iterable[str]) -> dict[str, Any]:
    """Spawn argv, return {'returncode': int, 'stdout': str, 'stderr': str}."""
    import subprocess

    completed = subprocess.run(
        list(argv),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def collect_fingerprint(runner: Runner = default_runner) -> dict[str, Any]:
    """Run every fingerprint command; missing tools are recorded, never fatal."""
    raw: dict[str, Any] = {}
    for key, argv in FINGERPRINT_COMMANDS:
        try:
            raw[key] = runner(argv)
        except Exception as error:  # missing tool / timeout: record honestly
            raw[key] = {"returncode": None, "stdout": "", "stderr": f"unavailable: {error}"}
    return {"commands": raw, "parsed": parse_fingerprint(raw)}


def parse_os_release(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or "=" not in line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def parse_virtualization(result: dict[str, Any] | None) -> str:
    if not result:
        return "unknown"
    stdout = (result.get("stdout") or "").strip()
    if result.get("returncode") == 1 and not stdout:
        return "none"  # systemd-detect-virt exits 1 on bare metal
    return stdout or "unknown"


def parse_proc_version(result: dict[str, Any] | None) -> str:
    if not result:
        return ""
    return (result.get("stdout") or "").strip()


def has_microsoft_marker(proc_version_text: str) -> bool:
    return "microsoft" in proc_version_text.lower()


def parse_root_filesystem(result: dict[str, Any] | None) -> str:
    """Extract the filesystem type column from `df -T /` output."""
    if not result:
        return "unknown"
    lines = (result.get("stdout") or "").splitlines()
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 2 and line.startswith("/"):
            return parts[1]
    return "unknown"


def parse_hostname(result: dict[str, Any] | None) -> str:
    if not result:
        return "unknown"
    return (result.get("stdout") or "").strip() or "unknown"


def first_line(result: dict[str, Any] | None) -> str:
    if not result:
        return ""
    stdout = (result.get("stdout") or "").strip()
    return stdout.splitlines()[0] if stdout else ""


def parse_fingerprint(raw: dict[str, Any]) -> dict[str, Any]:
    commands = raw.get("commands", raw)
    os_release = parse_os_release((commands.get("os_release") or {}).get("stdout", ""))
    return {
        "hostname": parse_hostname(commands.get("hostname")),
        "uname": first_line(commands.get("uname")),
        "os_pretty_name": os_release.get("PRETTY_NAME", "unknown"),
        "os_id": os_release.get("ID", "unknown"),
        "os_version_id": os_release.get("VERSION_ID", "unknown"),
        "virtualization": parse_virtualization(commands.get("virtualization")),
        "wsl_marker": has_microsoft_marker(parse_proc_version(commands.get("proc_version"))),
        "root_filesystem": parse_root_filesystem(commands.get("root_filesystem")),
        "systemd_available": (commands.get("systemctl") or {}).get("returncode") == 0,
        "tools": {
            key: first_line(commands.get(key))
            for key in ("gcc", "gxx", "cmake", "make", "python3", "git")
        },
    }


def validate_native_u1(
    fingerprint: dict[str, Any],
    forbidden_hostnames: Iterable[str] = FORBIDDEN_AUTHOR_HOSTNAMES,
) -> tuple[bool, list[str]]:
    """Return (eligible, reasons). Values come from the fingerprint as fact."""
    parsed = fingerprint.get("parsed", fingerprint)
    reasons: list[str] = []
    uname = str(parsed.get("uname", ""))
    if "Linux" not in uname:
        reasons.append("kernel is not Linux")
    if parsed.get("virtualization") != "none":
        reasons.append(f"virtualization is {parsed.get('virtualization')!r}, native required")
    if parsed.get("wsl_marker"):
        reasons.append("Microsoft kernel marker present (WSL family)")
    if parsed.get("root_filesystem") not in NATIVE_FILESYSTEMS:
        reasons.append(
            f"root filesystem {parsed.get('root_filesystem')!r} is not native "
            f"(expected one of {', '.join(NATIVE_FILESYSTEMS)})"
        )
    if not parsed.get("systemd_available"):
        reasons.append("systemd (systemctl) is not available")
    hostname = str(parsed.get("hostname", ""))
    forbidden = tuple(forbidden_hostnames)
    if hostname in forbidden:
        reasons.append(
            f"hostname {hostname!r} is forbidden as author host "
            f"(external reproduction platform only: {', '.join(forbidden)})"
        )
    if hostname in ("", "unknown"):
        reasons.append("hostname could not be determined")
    return (not reasons), reasons


def fingerprint_markdown(fingerprint: dict[str, Any]) -> str:
    """Deterministic markdown block for ENGINE_ENVIRONMENT_R2 §10 (frozen fact)."""
    parsed = fingerprint.get("parsed", fingerprint)
    tools = parsed.get("tools", {})
    lines = [
        f"- hostname: `{parsed.get('hostname')}`",
        f"- uname: `{parsed.get('uname')}`",
        f"- os: `{parsed.get('os_pretty_name')}` (id={parsed.get('os_id')}, version_id={parsed.get('os_version_id')})",
        f"- virtualization: `{parsed.get('virtualization')}`; wsl_marker={parsed.get('wsl_marker')}",
        f"- root filesystem: `{parsed.get('root_filesystem')}`",
        f"- systemd available: {parsed.get('systemd_available')}",
    ]
    for key in ("gcc", "gxx", "cmake", "make", "python3", "git"):
        lines.append(f"- {key}: `{tools.get(key, '')}`")
    return "\n".join(lines) + "\n"
