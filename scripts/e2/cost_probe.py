"""Bounded engine cost probe (no science, no hinge source data).

Measures wall time of a short MD run of the pinned engine binary on the
engine-owned DSDNA8 fixture (``test/DNA/DSDNA8`` from the pinned oxDNA tree
@ 00dc7fb9; GPL-3.0, rights CLEAR per NL0-002 — a different, engine-owned
subject, NOT the DNA-hinge-simulations source). Digests of the fixture files
are recorded in the report; raw artifact reuse therefore satisfies the
digest + provenance rule.

Rationale for using the engine fixture instead of a generated synthetic
structure: a hand-built configuration that passes DNA2 FENE bonded checks
(backbone-site distance within ~[0.506, 1.006]) must be a physically valid
DNA2 structure, otherwise the dynamics explode and the measurement is
meaningless. The DSDNA8 fixture is the accepted E1 smoke subject and is
known-good for the pinned binary.

The probe is a technical run with a unique run ID; it is not an experiment
campaign run and produces no scientific claim. Memory instrumentation is
deliberately NOT faked: the report records ``memory: NOT_MEASURED``
(instrumentation is owned by the INFRA2-002 reproducible executor).
"""
from __future__ import annotations

import subprocess
import time

try:
    from .canonical import canonical_json
except ImportError:
    from canonical import canonical_json

INPUT_TEMPLATE = """\
backend = CPU
steps = {steps}
newtonian_steps = 103
diff_coeff = 2.50
thermostat = john
T = 300K
dt = 0.005
verlet_skin = 0.05
sim_type = MD
interaction_type = DNA2
salt_concentration = 0.5
refresh_vel = 1
log_file = probe_log.dat
no_stdout_energy = 1
restart_step_counter = 1
time_scale = linear
external_forces = 0
print_conf_interval = {steps}
print_energy_every = 100
trajectory_file = probe_traj.dat
energy_file = probe_energy.dat
lastconf_file = probe_last.dat
topology = {topology}
conf_file = {conf}
seed = 7777
print_timings = 1
"""


def run_probe(
    engine_path: str,
    workdir: str,
    fixture_dir: str,
    steps: int,
    run_id: str,
    topology: str = "dsdna8.top",
    conf: str = "init.dat",
) -> dict:
    """Run the probe entirely inside WSL (engine binaries are Linux builds).

    ``engine_path``/``workdir``/``fixture_dir`` are WSL-side absolute paths.
    """
    input_text = INPUT_TEMPLATE.format(steps=steps, topology=topology, conf=conf)
    script = f"""
set -e
mkdir -p '{workdir}'
cd '{workdir}'
cp '{fixture_dir}/{topology}' .
cp '{fixture_dir}/{conf}' .
sha256sum '{topology}' '{conf}' > digests.txt
cat > probe_input.in <<'PROBE_EOF'
{input_text}
PROBE_EOF
'{engine_path}' probe_input.in > probe_stdout.txt 2> probe_stderr.txt
echo PROBE_OK
sha256sum probe_last.dat probe_energy.dat > probe_digests.txt
"""
    started = time.perf_counter()
    completed = subprocess.run(
        ["wsl", "-e", "bash", "-c", script],
        capture_output=True,
        text=True,
        timeout=900,
    )
    wall = time.perf_counter() - started
    ok = "PROBE_OK" in completed.stdout
    digests = {}
    if ok:
        listed = subprocess.run(
            ["wsl", "-e", "bash", "-c", f"cat '{workdir}/digests.txt' '{workdir}/probe_digests.txt'"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        for line in listed.stdout.splitlines():
            parts = line.split()
            if len(parts) == 2:
                digests[parts[1]] = parts[0]
    return {
        "schema_version": 1,
        "kind": "e2_synthetic_cost_probe",
        "run_id": run_id,
        "note": "technical probe on the engine-owned DSDNA8 fixture; NOT an experiment campaign run; scientific_outcome = NOT_APPLICABLE",
        "engine_path": engine_path,
        "engine_source_commit": "00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591 (git rev-parse of the build source tree, verified before the probe)",
        "fixture_subject": {
            "origin": f"pinned oxDNA tree @ 00dc7fb9, test/DNA/DSDNA8 (engine-owned fixture; GPL-3.0, rights CLEAR per NL0-002)",
            "topology": topology,
            "conf": conf,
            "digests_sha256": digests,
        },
        "steps": steps,
        "wall_time_s": wall,
        "wall_time_includes": ["wsl process startup", "bash script", "engine run", "digest pass"],
        "exit_code": completed.returncode,
        "probe_completed": ok,
        "stdout_tail": completed.stdout[-1500:],
        "stderr_tail": completed.stderr[-1500:],
        "memory": "NOT_MEASURED (stdlib-only; instrumentation owned by INFRA2-002 reproducible executor)",
    }


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="bounded engine cost probe on the DSDNA8 fixture")
    parser.add_argument("--engine", required=True, help="WSL-side absolute engine binary path")
    parser.add_argument("--workdir", required=True, help="WSL-side scratch directory (created)")
    parser.add_argument("--fixture-dir", required=True, help="WSL-side directory with dsdna8.top and init.dat")
    parser.add_argument("--steps", type=int, default=5000)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    report = run_probe(args.engine, args.workdir, args.fixture_dir, args.steps, args.run_id)
    rendered = canonical_json(report)
    if args.report:
        with open(args.report, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
    print(rendered, end="")
    return 0 if report["probe_completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
