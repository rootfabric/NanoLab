"""Fixed subprocess entry point. Never accept commands, imports or model paths."""
import sys
import json
from pathlib import Path


def main():
    import resource
    from atomistic.api import (MAX_MEMORY_BYTES, MAX_OUTPUT_BYTES, MAX_WALL_SECONDS,
                               PINS, CLAIM, digest, read_config, write_json)
    resource.setrlimit(resource.RLIMIT_CPU, (MAX_WALL_SECONDS, MAX_WALL_SECONDS))
    resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY_BYTES, MAX_MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_BYTES, MAX_OUTPUT_BYTES))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    import importlib.metadata
    import inspect
    import platform
    import numpy as np
    import ase.calculators.emt as emt
    from ase.build import bulk
    from ase import units
    from ase.optimize import BFGS
    from ase.md.langevin import Langevin
    from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary

    run_dir = Path(sys.argv[1])
    config = read_config(run_dir / "config.json")
    frozen = json.loads((run_dir / "protocol.json").read_text())
    if frozen["input_config"]["sha256"] != digest(run_dir / "config.json")["sha256"]:
        raise RuntimeError("frozen config integrity failure")
    versions = {name: importlib.metadata.version(name) for name in PINS}
    if versions != PINS:
        raise RuntimeError(f"dependency pin mismatch: {versions}")
    if frozen["source_model"]["module_digest"] != digest(inspect.getfile(emt)):
        raise RuntimeError("frozen EMT source integrity failure")
    environment = {"python": platform.python_version(), "platform": platform.platform(), "dependencies": versions,
                   "installed_distributions": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},
                   "source_model": {"module": "ase.calculators.emt", "module_digest": digest(inspect.getfile(emt)), "Cu_parameters": list(emt.parameters["Cu"]), "asap_cutoff": False},
                   "resource_limits": {"address_space_bytes": MAX_MEMORY_BYTES, "cpu_seconds": MAX_WALL_SECONDS, "single_file_bytes": MAX_OUTPUT_BYTES}, "threads": 1}
    write_json(run_dir / "environment.json", environment)
    s, r, m = config["structure"], config["relaxation"], config["md"]
    atoms = bulk("Cu", "fcc", a=s["lattice_constant_angstrom"], cubic=True).repeat(s["size"])
    atoms.pbc = False
    atoms.center(vacuum=8.0)
    atoms.calc = emt.EMT(asap_cutoff=False)

    def finite_state():
        values = [atoms.positions, atoms.get_forces(), atoms.get_potential_energy(), atoms.get_kinetic_energy(), atoms.get_temperature()]
        if not all(np.isfinite(value).all() for value in values):
            raise RuntimeError("nonfinite simulation state")

    finite_state()
    # Predeclared internal derivative check on an asymmetric displacement.
    original = atoms.positions.copy()
    atoms.positions[0, 0] += 0.03
    force = float(atoms.get_forces()[0, 0])
    delta = 1e-5
    atoms.positions[0, 0] += delta
    plus = atoms.get_potential_energy()
    atoms.positions[0, 0] -= 2 * delta
    minus = atoms.get_potential_energy()
    fd_force = -(plus - minus) / (2 * delta)
    control = {"analytic_force_ev_per_angstrom": force, "central_difference_force_ev_per_angstrom": float(fd_force), "absolute_error_ev_per_angstrom": abs(force - float(fd_force)), "tolerance_ev_per_angstrom": 1e-4, "passed": abs(force - float(fd_force)) <= 1e-4}
    write_json(run_dir / "numerical-control.json", control)
    if not control["passed"]:
        raise RuntimeError("EMT force finite-difference control failed")
    atoms.positions[:] = original
    initial_energy = float(atoms.get_potential_energy())
    optimizer = BFGS(atoms, logfile=str(run_dir / "relaxation.log"), maxstep=0.1)
    optimizer.attach(finite_state, interval=1)
    converged = bool(optimizer.run(fmax=r["fmax_ev_per_angstrom"], steps=r["max_steps"]))
    relaxation = {"converged": converged, "steps": optimizer.nsteps, "initial_potential_energy_ev": initial_energy,
                  "final_potential_energy_ev": float(atoms.get_potential_energy()), "final_max_force_ev_per_angstrom": float(np.linalg.norm(atoms.get_forces(), axis=1).max()),
                  "fmax_ev_per_angstrom": r["fmax_ev_per_angstrom"]}
    write_json(run_dir / "relaxation.json", relaxation)
    if not converged:
        raise RuntimeError("relaxation did not converge; MD not started")
    rng = np.random.default_rng(m["seed"])
    MaxwellBoltzmannDistribution(atoms, temperature_K=m["temperature_k"], rng=rng)
    Stationary(atoms, preserve_temperature=True)
    dynamics = Langevin(atoms, timestep=m["timestep_fs"] * units.fs, temperature_K=m["temperature_k"], friction=m["friction_per_fs"] / units.fs, fixcm=True, rng=rng, logfile=None)
    frames, series = [], []

    def record(step):
        finite_state()
        row = {"step": step, "time_fs": step * m["timestep_fs"], "potential_energy_ev": float(atoms.get_potential_energy()), "kinetic_energy_ev": float(atoms.get_kinetic_energy()), "temperature_k": float(atoms.get_temperature())}
        row["total_energy_ev"] = row["potential_energy_ev"] + row["kinetic_energy_ev"]
        series.append(row)
        if step == 0 or step % m["sample_interval"] == 0 or step == m["steps"]:
            frames.append(dict(row, positions_angstrom=atoms.positions.tolist()))

    record(0)
    for step in range(1, m["steps"] + 1):
        dynamics.run(1)
        record(step)
    metrics = {"schema_version": "atomistic-metrics-v1", "status": "COMPLETED", "claim_ceiling": CLAIM,
               "scientific_outcome": "NOT_EVALUATED", "material": "Cu", "model": "ASE_EMT_Cu", "atom_count": len(atoms),
               "relaxation": relaxation, "md": dict(m, integrator="ASE Langevin", boundary="nonperiodic", temperature_definition="ASE 3N kinetic temperature", fix_center_of_mass=True),
               "numerical_control": control, "series": series, "final": series[-1],
               "resource_usage": {"cpu_user_seconds": resource.getrusage(resource.RUSAGE_SELF).ru_utime, "cpu_system_seconds": resource.getrusage(resource.RUSAGE_SELF).ru_stime, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    trajectory = {"schema_version": "atomistic-trajectory-v1", "claim_ceiling": CLAIM, "material": "Cu", "model": "ASE_EMT_Cu", "atom_count": len(atoms), "symbols": atoms.get_chemical_symbols(), "cell_angstrom": atoms.cell.tolist(), "pbc": [False, False, False], "frames": frames}
    write_json(run_dir / "metrics.json", metrics)
    write_json(run_dir / "trajectory.json", trajectory)
    (run_dir / "report.md").write_text(
        f"# Cu / ASE EMT — инженерная демонстрация\n\n"
        f"Claim ceiling: `{CLAIM}`. Scientific outcome: `NOT_EVALUATED`.\n\n"
        f"Реальный расчёт: {len(atoms)} атомов Cu, непериодический FCC-кластер; "
        f"BFGS {optimizer.nsteps} steps, затем {m['steps']} Langevin MD steps по {m['timestep_fs']} fs.\n\n"
        f"Релаксация: {initial_energy:.8f} → {relaxation['final_potential_energy_ev']:.8f} eV; "
        f"max force {relaxation['final_max_force_ev_per_angstrom']:.6f} eV/Å.\n\n"
        f"Последний кадр: T={series[-1]['temperature_k']:.6f} K, "
        f"potential={series[-1]['potential_energy_ev']:.8f} eV.\n\n"
        f"Проверка производной энергии: ошибка {control['absolute_error_ev_per_angstrom']:.3g} eV/Å "
        f"при заранее заданном допуске 1e-4 eV/Å. Это внутренняя численная проверка той же модели.\n\n"
        "Короткая термостатированная траектория не устанавливает равновесие, долговременную устойчивость "
        "или точность свойств меди. Независимый material benchmark не выполнен. "
        "P0/E6 и исторические NL checkpoints не принимаются этим расчётом.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
