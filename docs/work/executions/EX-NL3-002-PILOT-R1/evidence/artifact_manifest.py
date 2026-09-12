"""Artifact manifests for pilot runs: SHA-256 + size of every run artifact (WSL side, outside Git)."""
import argparse
import json
import subprocess


def wsl_stat(wsl_dir, name):
    out = subprocess.run(
        ["wsl", "-e", "bash", "-c", f"cd '{wsl_dir}' && sha256sum '{name}' && stat -c %s '{name}'"],
        capture_output=True, text=True, timeout=300,
    )
    if out.returncode != 0:
        return {"file": name, "error": out.stderr.strip()}
    digest = out.stdout.splitlines()[0].split()[0]
    size = int(out.stdout.splitlines()[1].strip())
    return {"file": name, "sha256": digest, "size_bytes": size, "location": wsl_dir}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wsl-dir", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--files", nargs="+", required=True)
    args = parser.parse_args()
    manifest = {
        "schema_version": 1,
        "kind": "e2_pilot_artifacts_manifest",
        "storage_location": args.wsl_dir + " (WSL, outside Git; raw artifacts not committed)",
        "files": [wsl_stat(args.wsl_dir, name) for name in args.files],
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as h:
        json.dump(manifest, h, ensure_ascii=False, indent=2, sort_keys=True)
        h.write("\n")
    print(json.dumps({"out": args.out, "files": len(manifest["files"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
