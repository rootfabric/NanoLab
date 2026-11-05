"""Explicit real MD integration command; consumes one pilot, never auto-retries."""
import argparse
from pathlib import Path
from .api import read_config, run, verify_run


def check_real_run(output_root=None, run_id="integration-cu-001"):
    config_path = Path(__file__).resolve().parents[2] / "examples/atomistic/cu-demo.json"
    if output_root is None:
        raise RuntimeError("explicit output_root required to retain real run evidence")
    result = run(read_config(config_path), output_root, run_id)
    metrics, trajectory = result["metrics"], result["trajectory"]
    assert metrics["atom_count"] == 32
    assert metrics["relaxation"]["converged"]
    assert metrics["relaxation"]["final_potential_energy_ev"] <= metrics["relaxation"]["initial_potential_energy_ev"]
    assert metrics["numerical_control"]["passed"]
    assert len(metrics["series"]) == 51
    assert len(trajectory["frames"]) == 11
    assert trajectory["frames"][-1]["step"] == 50
    assert trajectory["frames"][0]["positions_angstrom"] != trajectory["frames"][-1]["positions_angstrom"]
    verify_run(result["run_dir"])
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    result = check_real_run(args.output_root, args.run_id)
    print(f"COMPLETED {result['run_dir']} wall={result['manifest']['wall_seconds']:.3f}s NOT_EVALUATED")
