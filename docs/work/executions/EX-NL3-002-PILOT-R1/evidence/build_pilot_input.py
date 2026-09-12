"""Build pilot run inputs from the pinned author pro_CPU.in (verbatim + recorded deviations)."""
import argparse


def build_input(src_text: str, run: dict) -> str:
    deviations = []
    lines = src_text.splitlines()
    out = []
    seen = set()
    key_map = {
        "steps": str(run["steps"]),
        "seed": str(run["seed"]),
        "topology": run.get("topology", "0b.top"),
        "conf_file": run.get("conf_file", "0b.conf"),
        "trajectory_file": run["traj"],
        "energy_file": run["energy"],
        "log_file": run["log"],
        "lastconf_file": run["last"],
        "print_conf_interval": str(run["print_conf_interval"]),
        "print_energy_every": str(run["print_energy_every"]),
    }
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in key_map:
                value = key_map[key]
                if line.split("=", 1)[1].strip() != value:
                    deviations.append({"key": key, "author": line.split("=", 1)[1].strip(), "pilot": value, "reason": run.get("reason", {}).get(key, "WO NL3-002-PILOT bounded pilot / per-run naming")})
                out.append(f"{key} = {value}")
                seen.add(key)
                continue
        out.append(line)
    # lastconf_file is absent from the author input; add it (recorded deviation)
    if "lastconf_file" not in seen:
        out.append(f"lastconf_file = {run['last']}")
        deviations.append({"key": "lastconf_file", "author": None, "pilot": run["last"], "reason": "author input has no lastconf_file; pilot records final configuration"})
    return "\n".join(out) + "\n", deviations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True, help="path to pinned pro_CPU.in")
    parser.add_argument("--out", required=True)
    parser.add_argument("--steps", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--print-conf-interval", type=int, required=True)
    parser.add_argument("--print-energy-every", type=int, required=True)
    args = parser.parse_args()
    with open(args.src, "r", encoding="utf-8") as h:
        src_text = h.read()
    run = {
        "steps": args.steps,
        "seed": args.seed,
        "traj": f"{args.prefix}_traj.dat",
        "energy": f"{args.prefix}_energy.dat",
        "log": f"{args.prefix}_log.dat",
        "last": f"{args.prefix}_last.dat",
        "print_conf_interval": args.print_conf_interval,
        "print_energy_every": args.print_energy_every,
    }
    text, deviations = build_input(src_text, run)
    with open(args.out, "w", encoding="utf-8", newline="\n") as h:
        h.write(text)
    import json
    print(json.dumps({"input_path": args.out, "deviations": deviations}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
