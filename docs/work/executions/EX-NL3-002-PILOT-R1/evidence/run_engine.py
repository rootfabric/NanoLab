"""Run a pilot engine command inside WSL and measure wall time (time.perf_counter around subprocess)."""
import argparse
import json
import subprocess
import time


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wsl-dir", required=True)
    parser.add_argument("--engine", default="/home/yurig/nl1-002/build-oxdna-cpu/bin/oxDNA")
    parser.add_argument("--input", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--timeout", type=int, default=7200)
    args = parser.parse_args()
    cmd = f"cd '{args.wsl_dir}' && '{args.engine}' '{args.input}'"
    started = time.perf_counter()
    completed = subprocess.run(["wsl", "-e", "bash", "-c", cmd + " > engine_stdout.txt 2> engine_stderr.txt; echo EXIT:$?"],
                               capture_output=True, text=True, timeout=args.timeout)
    wall = time.perf_counter() - started
    exit_code = None
    for line in completed.stdout.splitlines():
        if line.startswith("EXIT:"):
            exit_code = int(line.split(":", 1)[1])
    tail = subprocess.run(["wsl", "-e", "bash", "-c",
                           f"cd '{args.wsl_dir}' && tail -c 3000 engine_stdout.txt; echo ---STDERR---; tail -c 3000 engine_stderr.txt"],
                          capture_output=True, text=True, timeout=60)
    report = {"wsl_dir": args.wsl_dir, "input": args.input, "engine": args.engine,
              "exit_code": exit_code, "wall_time_s": wall,
              "combined_output_tail": tail.stdout[-4000:]}
    with open(args.report, "w", encoding="utf-8", newline="\n") as h:
        json.dump(report, h, ensure_ascii=False, indent=2)
    print(json.dumps({"exit_code": exit_code, "wall_time_s": wall}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
