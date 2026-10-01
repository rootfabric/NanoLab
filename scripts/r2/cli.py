"""CLI for the R2 activation tooling.

Every executing subcommand (build-engine, run, nc-verify with real checks)
is guarded by native-U1 host validation: on an ineligible host it prints a
BLOCKED_HOST record and exits with code 2 — never a silent fallback, never a
fabricated PASS (mission §5; NATIVE_UBUNTU_EXECUTION_POLICY_R1 §1).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import TOOLING_VERSION
from . import engine_build
from .contract import AttemptLedger, AttemptReuseError, utc_now_iso
from .executor import DirectLauncher, RunExecutor, RunSpec
from .fingerprint import (
    collect_fingerprint,
    fingerprint_markdown,
    validate_native_u1,
)
from .gates import GateError, GateReport, activation_decision
from .supervisor import (
    nc_u1_evaluate,
    nc_u2_evaluate,
    nc_u3_evaluate,
    nc_u4_evaluate,
    nc_u5_evaluate,
)


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def load_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def real_runner(argv: list[str]) -> dict[str, Any]:
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=600, check=False)
    return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def require_u1_or_exit(args: argparse.Namespace) -> dict[str, Any] | None:
    fingerprint = collect_fingerprint(real_runner)
    eligible, reasons = validate_native_u1(fingerprint)
    if not eligible:
        emit(
            {
                "command": getattr(args, "command", ""),
                "status": "BLOCKED_HOST",
                "eligible": False,
                "reasons": reasons,
                "r2_status": "WAITING_HOST / NOT_ACTIVE",
            }
        )
        return None
    return fingerprint


def cmd_fingerprint(args: argparse.Namespace) -> int:
    fingerprint = collect_fingerprint(real_runner)
    payload = {
        "tooling_version": TOOLING_VERSION,
        "fingerprint": fingerprint,
        "eligible": validate_native_u1(fingerprint)[0],
        "reasons": validate_native_u1(fingerprint)[1],
    }
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        emit({"status": "RECORDED", "out": str(out)})
    print(fingerprint_markdown(fingerprint), end="")
    return 0


def cmd_check_host(args: argparse.Namespace) -> int:
    fingerprint = collect_fingerprint(real_runner)
    eligible, reasons = validate_native_u1(fingerprint)
    emit(
        {
            "status": "ELIGIBLE_U1" if eligible else "NOT_ELIGIBLE",
            "hostname": fingerprint["parsed"]["hostname"],
            "eligible": eligible,
            "reasons": reasons,
        }
    )
    return 0 if eligible else 2


def cmd_build_engine(args: argparse.Namespace) -> int:
    if require_u1_or_exit(args) is None:
        return 2
    src, build_dir = Path(args.src), Path(args.build_dir)
    pinned_ok, actual_commit = engine_build.verify_pinned_source(real_runner, src)
    if not pinned_ok:
        emit({"status": "BLOCKED_SOURCE_PIN", "expected": engine_build.ENGINE_PINNED_COMMIT, "actual": actual_commit})
        return 3
    build_dir.mkdir(parents=True, exist_ok=True)
    log_path = build_dir / "build-r2.log"
    configure = real_runner(engine_build.configure_argv(src, build_dir))
    build = real_runner(engine_build.build_argv(build_dir, jobs=args.jobs))
    with log_path.open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(engine_build.configure_argv(src, build_dir)) + "\n")
        log.write(configure.get("stdout", "") + configure.get("stderr", ""))
        log.write("$ " + " ".join(engine_build.build_argv(build_dir, jobs=args.jobs)) + "\n")
        log.write(build.get("stdout", "") + build.get("stderr", ""))
    if configure["returncode"] != 0 or build["returncode"] != 0:
        emit({"status": "FAILED_TECHNICAL", "log": str(log_path)})
        return 4
    cache_values = engine_build.parse_cmake_cache((build_dir / "CMakeCache.txt").read_text(encoding="utf-8", errors="replace"))
    pins_ok, deviations = engine_build.verify_cache_pins(cache_values)
    fingerprint = collect_fingerprint(real_runner)
    provenance = engine_build.provenance_record(
        src, build_dir, cache_values, fingerprint["parsed"]["tools"], log_path,
        source_commit=actual_commit,
    )
    provenance["cache_pins_verified"] = pins_ok
    provenance["cache_pin_deviations"] = deviations
    (build_dir / "build-r2-provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    emit({"status": "COMPLETED" if pins_ok else "COMPLETED_WITH_DEVIATIONS", "provenance": str(build_dir / "build-r2-provenance.json")})
    return 0 if pins_ok else 5


def cmd_run(args: argparse.Namespace) -> int:
    if require_u1_or_exit(args) is None:
        return 2
    spec_json = load_json(Path(args.spec))
    ledger = AttemptLedger(Path(args.ledger))
    launcher = SystemdLauncherChoice(args.launcher)
    executor = RunExecutor(ledger, launcher=launcher.resolve())
    spec = RunSpec(
        execution_id=str(spec_json["execution_id"]),
        run_base=str(spec_json["run_base"]),
        attempt=int(spec_json.get("attempt", 0)),
        command=[str(item) for item in spec_json["command"]],
        seed=spec_json.get("seed"),
        subject_pins=dict(spec_json.get("subject_pins", {})),
        raw_root=Path(spec_json["raw_root"]) if spec_json.get("raw_root") else None,
        workspace=Path(spec_json["workspace"]) if spec_json.get("workspace") else None,
        timeout_seconds=spec_json.get("timeout_seconds"),
    )
    try:
        record = executor.execute(spec)
    except AttemptReuseError as error:
        emit({"status": "BLOCKED_ATTEMPT_REUSE", "reason": str(error)})
        return 3
    emit({"status": "RECORDED", "record": record.to_dict()})
    return 0


class SystemdLauncherChoice:
    def __init__(self, choice: str):
        self.choice = choice

    def resolve(self):
        if self.choice == "direct":
            return DirectLauncher()
        from .executor import SystemdTransientLauncher

        return SystemdTransientLauncher()


def cmd_gate(args: argparse.Namespace) -> int:
    # Repair R1 (review MINOR-1): R2 gate reports are U1 facts; recording them
    # from a non-eligible host would contradict the host guard.
    if require_u1_or_exit(args) is None:
        return 2
    report = GateReport(Path(args.report))
    try:
        entry = report.set_status(args.gate, args.status, args.evidence or "")
    except GateError as error:
        emit({"status": "REJECTED", "reason": str(error)})
        return 3
    emit({"status": "RECORDED", "entry": entry, "invocation": " ".join(sys.argv)})
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    report = GateReport(Path(args.report))
    emit(
        {
            "entries": report.state["entries"],
            "unmet": report.unmet(),
            "all_gates_pass": report.all_gates_pass(),
            "all_controls_pass": report.all_controls_pass(),
        }
    )
    return 0


def cmd_activation_check(args: argparse.Namespace) -> int:
    report = GateReport(Path(args.report))
    fingerprint = load_json(Path(args.fingerprint)) if args.fingerprint else None
    decision = activation_decision(
        report,
        fingerprint=fingerprint,
        review_verdict=args.review_verdict,
        verify_verdict=args.verify_verdict,
        human_gate_approved=args.human_gate_approved,
    )
    decision["invocation"] = " ".join(sys.argv)
    emit(decision)
    return 0 if decision["r2_activated"] else 2


NC_PROCEDURES = {
    "NC-U1": (
        "1) через systemd-run запустить disposable job (например sleep 300); "
        "2) закрыть SSH-сессию владельца; 3) переподключиться; "
        "4) machine-check: systemctl is-active <unit> == active. "
        "Факт фиксируется оператором в evidence-файл, nc-verify считает verdict."
    ),
    "NC-U2": (
        "1) убедиться, что disposable job активен; 2) перезапустить agent-процесс "
        "(владелец job'а); 3) machine-check: systemctl is-active <unit> == active."
    ),
    "NC-U3": (
        "1) убедиться, что disposable job активен; 2) systemctl restart "
        "github-actions-runner.service (или эквивалент); 3) machine-check: "
        "scientific job продолжает работать (is-active == active)."
    ),
    "NC-U4": (
        "1) создать disposable CI workspace; 2) удалить его полностью; "
        "3) machine-check: scientific workspace/raw directory существует, "
        "находится вне CI workspace (~/nanolab/raw/...), digest не изменился."
    ),
    "NC-U5": (
        "1) запустить disposable scientific-process через run (ledger); "
        "2) deliberately kill процесс; 3) machine-check: ledger содержит "
        "FAILED_TECHNICAL с сохранённой попыткой; retry получает новый attempt id."
    ),
}


def cmd_nc_plan(args: argparse.Namespace) -> int:
    procedure = NC_PROCEDURES.get(args.nc)
    if not procedure:
        emit({"status": "REJECTED", "reason": f"unknown control {args.nc!r}"})
        return 3
    emit({"control": args.nc, "procedure": procedure, "note": "execution only on eligible U1 host"})
    return 0


def cmd_nc_verify(args: argparse.Namespace) -> int:
    # Repair R1 (review MINOR-1): NC evidence is produced on U1; verifying it
    # elsewhere would decouple the verdict from the execution host.
    if require_u1_or_exit(args) is None:
        return 2
    evidence = load_json(Path(args.evidence))
    evaluators = {
        "NC-U1": lambda data: nc_u1_evaluate(data["owner_session_gone"], data["job_still_running"]),
        "NC-U2": lambda data: nc_u2_evaluate(data["agent_restarted"], data["job_still_running"]),
        "NC-U3": lambda data: nc_u3_evaluate(data["runner_service_restarted"], data["job_still_running"]),
        "NC-U4": lambda data: nc_u4_evaluate(data["ci_workspace_deleted"], data["raw_intact"], data["raw_outside_ci"]),
        "NC-U5": lambda data: nc_u5_evaluate(
            data["killed_deliberately"], data["recorded_failed_technical"], data["attempt_preserved"], data["retry_id_new"]
        ),
    }
    evaluator = evaluators.get(args.nc)
    if not evaluator:
        emit({"status": "REJECTED", "reason": f"unknown control {args.nc!r}"})
        return 3
    verdict = evaluator(evidence)
    verdict["verified_utc"] = utc_now_iso()
    verdict["invocation"] = " ".join(sys.argv)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(verdict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    emit(verdict)
    return 0 if verdict["pass"] else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="r2", description="NanoLab R2 activation tooling (science-free)")
    parser.add_argument("--version", action="version", version=TOOLING_VERSION)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("fingerprint", help="capture host fingerprint (safe on any host)")
    p.add_argument("--out", default="", help="write full JSON fingerprint to this path")
    p.set_defaults(func=cmd_fingerprint)

    p = sub.add_parser("check-host", help="validate native-U1 eligibility (safe on any host)")
    p.set_defaults(func=cmd_check_host)

    p = sub.add_parser("build-engine", help="pinned oxDNA R2 build (U1 only)")
    p.add_argument("--src", required=True)
    p.add_argument("--build-dir", required=True)
    p.add_argument("--jobs", type=int, default=4)
    p.set_defaults(func=cmd_build_engine)

    p = sub.add_parser("run", help="execute one attempt of a run spec (U1 only)")
    p.add_argument("--spec", required=True)
    p.add_argument("--ledger", required=True)
    p.add_argument("--launcher", choices=["direct", "systemd"], default="systemd")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("gate", help="record a gate status (PASS requires existing evidence file)")
    p.add_argument("--report", required=True)
    p.add_argument("--gate", required=True)
    p.add_argument("--status", required=True, choices=["WAITING_HOST", "PASS", "FAIL"])
    p.add_argument("--evidence", default="")
    p.set_defaults(func=cmd_gate)

    p = sub.add_parser("report", help="print gate report summary")
    p.add_argument("--report", required=True)
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("activation-check", help="compute R2 activation decision (policy in code)")
    p.add_argument("--report", required=True)
    p.add_argument("--fingerprint", default="")
    p.add_argument("--review-verdict", default=None)
    p.add_argument("--verify-verdict", default=None)
    p.add_argument("--human-gate-approved", action="store_true")
    p.set_defaults(func=cmd_activation_check)

    p = sub.add_parser("nc-plan", help="print negative-control procedure (safe anywhere)")
    p.add_argument("--nc", required=True)
    p.set_defaults(func=cmd_nc_plan)

    p = sub.add_parser("nc-verify", help="verify recorded negative-control evidence")
    p.add_argument("--nc", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--out", default="")
    p.set_defaults(func=cmd_nc_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
