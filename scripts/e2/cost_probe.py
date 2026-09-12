"""Bounded synthetic cost probe (no science, no source data).

Runs the local engine binary on a generated synthetic fixture for a small
number of steps and records wall time / exit code / scale facts as input to
the measured resource budget. Memory instrumentation is deliberately NOT
faked: stdlib-only tooling on Windows cannot measure it reliably, so the
report records ``memory: NOT_MEASURED`` (the reproducible-executor line
INFRA2-002 will own real instrumentation).

This is a technical run with a unique run ID; it is not an experiment
campaign run and produces no scientific claim.
"""
from __future__ import annotations

import argparse
import subprocess
import time

try:
    from .canonical import canonical_json
    from . import fixtures
except ImportError:
    from canonical import canonical_json
    import fixtures

INPUT_TEMPLATE = """\
interaction_type = DNA2
salt_concentration = 0.5
T = 300K
steps = {steps}
backend = CPU
backend_precision = double
topology = fixture.top
conf_file = fixture_conf.dat
trajectory_file = probe_traj.dat
energy_file = probe_energy.dat
lastconf_file = probe_last.dat
seed = 7777
"""


def probe_input_text(steps: int) -> str:
    return INPUT_TEMPLATE.format(steps=steps)


def run_probe(engine_cmd: list, workdir: str, steps: int, run_id: str, angle_deg: float = 45.0) -> dict:
    if not engine_cmd:
        raise ValueError("engine_cmd must be a non-empty argument list")
    fixture = fixtures.build(mode="angled", angle_deg=angle_deg, arm_len=12, n_frames=1, broken=False)
    with open(f"{workdir}/fixture.top", "w", encoding="utf-8", newline="\n") as handle:
        handle.write(fixture["topology_text"])
    with open(f"{workdir}/fixture_conf.dat", "w", encoding="utf-8", newline="\n") as handle:
        handle.write(fixture["frame_texts"][0])
    input_path = f"{workdir}/probe_input.in"
    with open(input_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(probe_input_text(steps))
    command = engine_cmd + [input_path]
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=workdir, capture_output=True, text=True, timeout=900)
    wall = time.perf_counter() - started
    particles = fixture["topology_text"].splitlines()[0].split()[0]
    return {
        "schema_version": 1,
        "kind": "e2_synthetic_cost_probe",
        "run_id": run_id,
        "note": "technical synthetic probe; NOT an experiment campaign run; scientific_outcome = NOT_APPLICABLE",
        "engine_command": command,
        "fixture_mode": fixture["mode"],
        "fixture_angle_deg": fixture["expected"]["angle_deg"],
        "particles": int(particles),
        "steps": steps,
        "wall_time_s": wall,
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
        "memory": "NOT_MEASURED (stdlib-only; instrumentation owned by INFRA2-002 reproducible executor)",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="bounded synthetic engine cost probe")
    parser.add_argument("--engine", required=True, help="engine command, e.g. 'wsl -e /path/oxDNA' (space-separated)")
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    report = run_probe(args.engine.split(), args.workdir, args.steps, args.run_id)
    rendered = canonical_json(report)
    if args.report:
        with open(args.report, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
    print(rendered, end="")
    return 0 if report["exit_code"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
