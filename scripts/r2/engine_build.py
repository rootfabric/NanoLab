"""Pinned oxDNA R2 build procedure with full provenance capture.

Contract: docs/research/ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md §1/§5.
- source is pinned: commit 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591 (verified,
  never assumed);
- intended flags: CPU, DOUBLE=ON, CUDA=OFF, MPI=OFF (Release). Effective
  CMakeCache values are parsed back and verified against the intent;
- binary-sha equality with the historical WSL R1 build is explicitly NOT
  required and NOT checked (migration gate = same source + same intended
  flags + clean build + smoke + frame0 + fixtures);
- provenance records source commit, source tree digest, compiler/cmake/make
  versions, cmake argv, CMakeCache pins, binary sha256+size and the build log
  path.

All process execution is injected (runner) for unit testing; the CLI layer
guards execution behind native-U1 host validation.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable

from .contract import sha256_file

ENGINE_SOURCE = "lorenzo-rovigatti/oxDNA"
ENGINE_PINNED_COMMIT = "00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591"
ENGINE_CMAKE_ARGS = ("-DCMAKE_BUILD_TYPE=Release", "-DDOUBLE=ON", "-DCUDA=OFF", "-DMPI=OFF")
EXPECTED_CACHE_PINS = {
    "CMAKE_BUILD_TYPE": "Release",
    "DOUBLE": "ON",
    "CUDA": "OFF",
    "MPI": "OFF",
}

Runner = Callable[[list[str]], dict[str, Any]]


def source_commit(runner: Runner, src_dir: Path) -> str:
    result = runner(["git", "-C", str(src_dir), "rev-parse", "HEAD"])
    if result.get("returncode") != 0:
        raise RuntimeError(f"cannot resolve source commit in {src_dir}: {result.get('stderr', '').strip()}")
    return (result.get("stdout") or "").strip()


def tree_digest(root: Path) -> str:
    """Content digest of a source tree (sorted per-file sha256 canonical list)."""
    entries = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        entries.append({"path": rel, "sha256": sha256_file(path)})
    payload = "\n".join(f"{e['path']}  {e['sha256']}" for e in entries)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_pinned_source(runner: Runner, src_dir: Path) -> tuple[bool, str]:
    actual = source_commit(runner, src_dir)
    return (actual == ENGINE_PINNED_COMMIT), actual


def configure_argv(src_dir: Path, build_dir: Path) -> list[str]:
    return ["cmake", "-S", str(src_dir), "-B", str(build_dir), *ENGINE_CMAKE_ARGS]


def build_argv(build_dir: Path, jobs: int = 4) -> list[str]:
    return ["cmake", "--build", str(build_dir), "--parallel", str(jobs)]


def parse_cmake_cache(cache_text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in cache_text.splitlines():
        if ":=" not in line:
            continue
        key, _, value = line.partition(":=")
        values[key.strip()] = value.strip()
    return values


def verify_cache_pins(cache_values: dict[str, str]) -> tuple[bool, list[str]]:
    deviations = []
    for key, expected in EXPECTED_CACHE_PINS.items():
        actual = cache_values.get(key)
        if actual is None:
            deviations.append(f"{key} missing from CMakeCache")
        elif actual != expected:
            deviations.append(f"{key}={actual!r}, intended {expected!r}")
    return (not deviations), deviations


def binary_digest(build_dir: Path, binary_name: str = "oxdna") -> dict[str, Any]:
    binary = build_dir / binary_name
    if not binary.is_file():
        raise FileNotFoundError(f"engine binary not found: {binary}")
    return {
        "path": str(binary),
        "sha256": sha256_file(binary),
        "size": binary.stat().st_size,
    }


def provenance_record(
    src_dir: Path,
    build_dir: Path,
    cache_values: dict[str, str],
    tools: dict[str, str],
    build_log_path: Path,
    source_commit: str | None = None,
) -> dict[str, Any]:
    """Provenance for one R2 engine build.

    ``source_commit``: pass the value verified by ``verify_pinned_source`` so
    the artifact carries the actual 40-hex commit (repair R1, review NOTE-4);
    the placeholder only appears when the caller could not verify it.
    """
    return {
        "engine_source": ENGINE_SOURCE,
        "source_commit": source_commit or "resolved-at-execution",
        "source_commit_verified": bool(
            source_commit and source_commit == ENGINE_PINNED_COMMIT
        ),
        "source_tree_sha256": tree_digest(src_dir),
        "cmake_argv": configure_argv(src_dir, build_dir),
        "build_argv": build_argv(build_dir),
        "cmake_cache_pins": {key: cache_values.get(key) for key in EXPECTED_CACHE_PINS},
        "tools": tools,
        "build_log": str(build_log_path),
        "binary": binary_digest(build_dir),
        "binary_sha_equality_with_r1_required": False,
    }


def source_commit_probe(src_dir: Path) -> str:
    git_head = Path(src_dir) / ".git" / "HEAD"
    return "resolved-at-execution" if git_head.exists() else "unknown"
