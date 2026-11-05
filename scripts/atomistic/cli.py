"""python -m atomistic.cli validate|run|verify"""
import argparse
import json
import sys
from .api import read_config, run, verify_run, ValidationError, RunError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bounded real Cu/EMT engineering demonstrator")
    subs = parser.add_subparsers(dest="command", required=True)
    validate = subs.add_parser("validate")
    validate.add_argument("--config", required=True)
    launch = subs.add_parser("run")
    launch.add_argument("--config", required=True)
    launch.add_argument("--output-root", required=True)
    launch.add_argument("--run-id", required=True)
    launch.add_argument("--timeout-seconds", type=int, default=120)
    verify = subs.add_parser("verify")
    verify.add_argument("run_dir")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            config = read_config(args.config)
            result = {"valid": True, "atom_count": 4 * __import__("math").prod(config["structure"]["size"])}
        elif args.command == "verify":
            result = verify_run(args.run_dir)
        else:
            receipt = run(read_config(args.config), args.output_root, args.run_id, timeout_seconds=args.timeout_seconds)
            result = {"run_id": receipt["run_id"], "run_dir": receipt["run_dir"], "status": receipt["status"], "wall_seconds": receipt["manifest"]["wall_seconds"], "scientific_outcome": "NOT_EVALUATED"}
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValidationError, RunError, OSError, json.JSONDecodeError) as exc:
        print(f"atomistic: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
