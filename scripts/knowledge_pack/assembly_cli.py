"""assembly_cli — deterministic OFFLINE CLI for the static two-component assembler.

WO-S17-STATIC-ASSEMBLY-HARDENING-R1 (issue #66). Thin, fail-closed command
line boundary over ``knowledge_pack.assembly_spec`` (the repaired R3 static
assembler library). Stdlib only; no network access; no scientific runs; no
timestamps in artifact bytes (timestamps live in evidence records, never in
artifacts).

Subcommands
-----------
``assemble``
    Inputs: driver + follower MechanicalComponentSpec JSON, an AssemblySpec
    JSON, an optional ``--recipe`` interface-recipe JSON (resolved against
    ``--recipe-base`` exactly like ``assembly_spec.assemble(recipe_base=...)``)
    and ``--outdir``. Output: ``<assembly_id>.top`` (oxDNA topology),
    ``<assembly_id>.dat`` (oxDNA configuration) and ``receipt.json`` (the
    deterministic Evidence Receipt), written atomically (temp files + rename,
    temp cleanup on failure). Byte-determinism: sorted JSON keys, fixed
    float formatting from the library, no wall-clock input of any kind — two
    runs over identical inputs produce identical sha256 digests.

``verify``
    Re-verifies an artifact directory against its own receipt: sha256
    cross-check of both oxDNA files plus a strict reparse via the
    ``hinge_family`` parsers (topology chain integrity + configuration).
    Exit 0 = verified, exit 1 = verification failed. No stdout science.

Fail-closed CLI boundaries (every refusal = clean exit code + stderr message,
no partial artifacts): unknown arguments (argparse), missing/oversized
(> ``MAX_INPUT_BYTES``) or non-UTF-8/invalid-JSON inputs, absolute or ``..``
(out-of-tree) ``--outdir`` paths, duplicate particle ids (one anchor particle
bound by two different connections), a ``--recipe`` on a non-SOURCE_VERIFIED
assembly, an ``--recipe`` file that is not the spec-declared recipe, unsafe
``assembly_id`` (unusable as an artifact file stem), and remote-only
topology/configuration pins (the offline CLI never fetches).

Exit codes
----------
0 — deterministic execution completed (``ASSEMBLED_STATIC_ONLY`` with all
  three artifacts, or an honest ``NOT_RECONSTRUCTED`` receipt). Exit 0 is a
  software outcome, NEVER a scientific pass.
1 — ``verify`` failed (artifact/receipt mismatch or incomplete artifact set).
2 — refusal: CLI boundary violation, or a ``BLOCKED_*`` assembly receipt
  (the refusal receipt itself is still written as evidence; no .top/.dat).

Claim ceiling: output statuses come only from
``knowledge_pack.assembly_spec.ASSEMBLY_STATUSES``
(``ASSEMBLED_STATIC_ONLY`` / ``NOT_RECONSTRUCTED`` / ``BLOCKED_*``) with the
``GEOMETRY_UNVERIFIED`` discipline; the CLI additionally refuses to write any
artifact byte containing a forbidden claim marker (``ASSEMBLY_VALIDATED``,
``MODEL_REPRODUCED``).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

if __package__ in (None, ""):  # direct script invocation: make the repo importable
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hinge_family.oxdna_conf import ConfError, Configuration  # noqa: E402
from hinge_family.oxdna_topology import Topology, TopologyError  # noqa: E402
from knowledge_pack import assembly_spec  # noqa: E402
from knowledge_pack.assembly_spec import ASSEMBLY_STATUSES, AssemblySpecError  # noqa: E402

CLI_SCHEMA = "nanolab.assembly_cli.v1"
MAX_INPUT_BYTES = 4 * 1024 * 1024  # 4 MiB fail-closed cap per JSON input
ASSEMBLY_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
# Claim-ceiling guard: these strings must never appear in any CLI-written byte.
FORBIDDEN_MARKERS = ("ASSEMBLY_VALIDATED", "MODEL_REPRODUCED")

EXIT_OK = 0
EXIT_VERIFY_FAILED = 1
EXIT_REFUSED = 2


class CliRefusal(Exception):
    """A fail-closed CLI boundary violation (exit 2, nothing written)."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _refuse(message: str) -> None:
    raise CliRefusal(message)


# --------------------------------------------------------------------------
# input loading (fail-closed boundaries)
# --------------------------------------------------------------------------

def _load_json_input(path: Path, label: str) -> dict:
    if not path.exists():
        _refuse(f"{label} not found: {path}")
    if not path.is_file():
        _refuse(f"{label} is not a regular file: {path}")
    size = path.stat().st_size
    if size > MAX_INPUT_BYTES:
        _refuse(
            f"{label} exceeds the {MAX_INPUT_BYTES}-byte input cap: {path} is {size} bytes "
            "(oversized inputs are refused fail-closed)"
        )
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        _refuse(f"{label} is not readable UTF-8 text: {path}: {exc}")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        _refuse(f"{label} is not valid JSON: {path}: {exc}")
    if not isinstance(value, dict):
        _refuse(f"{label} must be a JSON object: {path}")
    return value


def _safe_outdir(raw: str) -> Path:
    """Outdir must stay inside the current working directory tree."""
    if not isinstance(raw, str) or not raw.strip():
        _refuse("--outdir must be a non-empty relative path")
    if "\\" in raw:
        _refuse(f"--outdir must not contain backslashes: {raw!r}")
    candidate = Path(raw)
    if candidate.is_absolute():
        _refuse(
            f"--outdir must be a relative path inside the working directory tree, "
            f"got absolute path {raw!r} (out-of-tree artifact paths are refused)"
        )
    if any(part == ".." for part in candidate.parts):
        _refuse(
            f"--outdir must not contain '..' segments: {raw!r} "
            "(out-of-tree artifact paths are refused)"
        )
    outdir = Path.cwd() / candidate
    if outdir.exists():
        if not outdir.is_dir():
            _refuse(f"--outdir exists and is not a directory: {outdir}")
        if any(outdir.iterdir()):
            _refuse(f"--outdir exists and is not empty (refusing to overwrite artifacts): {outdir}")
    return outdir


def _artifact_stem(spec: dict) -> str:
    assembly_id = spec.get("assembly_id")
    if not isinstance(assembly_id, str) or not ASSEMBLY_ID_RE.match(assembly_id):
        _refuse(
            f"assembly_id {assembly_id!r} is not usable as a deterministic artifact file stem "
            f"(must match {ASSEMBLY_ID_RE.pattern})"
        )
    return assembly_id


def _materialize_role_inputs(role: str, component_spec: dict, input_root: Path) -> dict:
    """Resolve the pinned topology/configuration files for one role (read-only).

    Remote-only pins (http/https) are refused: the offline CLI never fetches.
    UNKNOWN-status blocks are left unmaterialized — the library's decisive
    structural pass then produces the honest NOT_RECONSTRUCTED receipt.
    """
    inputs: dict = {}
    for label in ("topology", "configuration"):
        block = component_spec.get(label)
        if not isinstance(block, dict):
            continue  # structural validation inside assemble() reports this
        if block.get("status") == "UNKNOWN":
            continue
        uri = block.get("uri")
        if not isinstance(uri, str) or not uri.strip():
            _refuse(f"{role} component spec: {label} pin carries no uri")
        if uri.startswith(("http://", "https://")):
            _refuse(
                f"{role} component spec: {label} pin is remote-only ({uri}) - the offline CLI "
                "never fetches; materialize the pinned file locally and pin its sha256"
            )
        path = Path(uri)
        if not path.is_absolute():
            path = input_root / path
        if not path.is_file():
            _refuse(f"{role} component spec: pinned {label} file not found on disk: {path}")
        inputs[f"{label}_path"] = path
    return inputs


def _check_duplicate_particle_bindings(spec: dict, component_specs: dict) -> None:
    """CLI boundary: one physical anchor particle serves at most one connection.

    In the oxDNA index space a particle's id is its position; the only place an
    input spec can reference one is a port anchor index. The same anchor
    particle bound by two different connections would declare one physical
    particle as part of two distinct interfaces — refused before any assembly.
    """
    port_index = assembly_spec._port_index(component_specs)
    bound: dict[tuple, str] = {}
    for conn in spec.get("connections", []) or []:
        if not isinstance(conn, dict) or conn.get("kind") != "SS_DNA_OVERHANG_HYBRIDIZATION":
            continue
        cid = conn.get("connection_id")
        for role_key, role in (("driver_port", "driver"), ("follower_port", "follower")):
            port = port_index.get((role, conn.get(role_key)))
            if not isinstance(port, dict):
                continue  # unknown port references are reported by the library
            anchors = port.get("anchors") or []
            if not isinstance(anchors, list):
                continue
            for anchor in anchors:
                value = anchor.get("anchor") if isinstance(anchor, dict) else None
                if not isinstance(value, int) or isinstance(value, bool):
                    continue
                key = (role, value)
                previous = bound.get(key)
                if previous is not None and previous != cid:
                    _refuse(
                        f"duplicate particle id: {role} particle index {value} is bound by "
                        f"connections {previous!r} and {cid!r} - one anchor particle cannot "
                        "serve two declared interfaces (fail-closed)"
                    )
                bound[key] = cid


def _resolve_recipe_base(args, spec: dict) -> Path:
    """Resolve the recipe base for SOURCE_VERIFIED assemblies (fail-closed)."""
    if args.recipe is None:
        if spec.get("mode") == "SOURCE_VERIFIED" and not isinstance(
            spec.get("interface_recipe_ref"), dict
        ):
            # No recipe materialized: let the library produce the precise
            # BLOCKED_SPEC receipt (the declared ref itself is missing).
            return Path.cwd()
        return Path(args.recipe_base) if args.recipe_base else Path.cwd()
    recipe_path = Path(args.recipe)
    if not recipe_path.exists():
        _refuse(f"--recipe file not found: {recipe_path}")
    if not recipe_path.is_file():
        _refuse(f"--recipe is not a regular file: {recipe_path}")
    if recipe_path.stat().st_size > MAX_INPUT_BYTES:
        _refuse(f"--recipe exceeds the {MAX_INPUT_BYTES}-byte input cap: {recipe_path}")
    if spec.get("mode") != "SOURCE_VERIFIED":
        _refuse(
            f"--recipe was given but the assembly spec mode is {spec.get('mode')!r} - a recipe "
            "is only consulted for SOURCE_VERIFIED assemblies (contradictory input is refused)"
        )
    ref = spec.get("interface_recipe_ref")
    if not isinstance(ref, dict) or not isinstance(ref.get("path"), str) or not ref["path"].strip():
        _refuse(
            "--recipe was given but the assembly spec carries no interface_recipe_ref.path "
            "(SOURCE_VERIFIED requires the declared relative recipe path)"
        )
    base = Path(args.recipe_base) if args.recipe_base else recipe_path.parent
    declared = (base / ref["path"]).resolve()
    if declared != recipe_path.resolve():
        _refuse(
            f"--recipe {recipe_path} is not the spec-declared recipe file: interface_recipe_ref."
            f"path {ref['path']!r} resolves to {declared} against recipe base {base} "
            "(substituting a different recipe file is refused)"
        )
    return base


# --------------------------------------------------------------------------
# deterministic artifact writing (atomic, no timestamps)
# --------------------------------------------------------------------------

def _receipt_json_bytes(receipt: dict) -> bytes:
    text = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    return (text + "\n").encode("utf-8")


def _guard_claim_ceiling(receipt: dict) -> None:
    """Claim-ceiling guard: no status field may carry a forbidden claim marker.

    The receipt's ``claim`` field *quotes* the forbidden marker inside its
    disclaimer text (``... Never ASSEMBLY_VALIDATED ...``) — that is the
    library's own ceiling statement and stays. Only structured status values
    are guarded: a status must never BE a forbidden claim.
    """
    for key in ("assembly_status", "geometry_status"):
        value = receipt.get(key)
        if isinstance(value, str) and any(marker == value for marker in FORBIDDEN_MARKERS):
            _refuse(
                f"internal guard: receipt {key} would be the forbidden claim {value!r} - "
                "refusing to write (claim ceiling violation)"
            )
    if not isinstance(receipt.get("assembly_status"), str) or \
            receipt["assembly_status"] not in ASSEMBLY_STATUSES:
        _refuse(
            f"internal guard: receipt assembly_status {receipt.get('assembly_status')!r} is "
            f"outside ASSEMBLY_STATUSES - refusing to write"
        )


def _write_artifacts_atomically(outdir: Path, files: dict) -> dict:
    """Write all payloads via temp files + rename; clean temps on any failure."""
    outdir.mkdir(parents=True, exist_ok=True)
    temps: dict = {}
    try:
        for name in sorted(files):
            payload = files[name]
            fd, tmp = tempfile.mkstemp(dir=outdir, prefix=".assembly_cli-tmp-")
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            temps[name] = tmp
        for name in sorted(temps):
            os.replace(temps[name], outdir / name)
            del temps[name]
    finally:
        for tmp in temps.values():  # only reached on failure
            try:
                os.unlink(tmp)
            except OSError:
                pass
    return {
        name: hashlib.sha256((outdir / name).read_bytes()).hexdigest() for name in sorted(files)
    }


# --------------------------------------------------------------------------
# subcommands
# --------------------------------------------------------------------------

def cmd_assemble(args) -> int:
    outdir = _safe_outdir(args.outdir)
    driver_spec = _load_json_input(Path(args.driver_spec), "driver component spec")
    follower_spec = _load_json_input(Path(args.follower_spec), "follower component spec")
    spec = _load_json_input(Path(args.assembly_spec), "assembly spec")
    component_specs = {"driver": driver_spec, "follower": follower_spec}
    recipe_base = _resolve_recipe_base(args, spec)
    _check_duplicate_particle_bindings(spec, component_specs)
    input_root = Path(args.input_root) if args.input_root else Path.cwd()
    inputs = {
        role: _materialize_role_inputs(role, component_specs[role], input_root)
        for role in ("driver", "follower")
    }
    stem = _artifact_stem(spec)
    try:
        topology_text, configuration_text, receipt = assembly_spec.assemble_artifacts(
            spec, component_specs, inputs, recipe_base=recipe_base
        )
    except AssemblySpecError as exc:
        _refuse(f"assembler internal refusal: {exc}")
    status = receipt["assembly_status"]
    files: dict = {"receipt.json": _receipt_json_bytes(receipt)}
    if status == "ASSEMBLED_STATIC_ONLY":
        files[f"{stem}.top"] = topology_text.encode("utf-8")
        files[f"{stem}.dat"] = configuration_text.encode("utf-8")
    _guard_claim_ceiling(receipt)
    digests = _write_artifacts_atomically(outdir, files)
    print(json.dumps(
        {
            "schema": CLI_SCHEMA,
            "command": "assemble",
            "artifact_dir": str(outdir),
            "assembly_status": status,
            "geometry_status": receipt["geometry_status"],
            "artifacts": digests,
        },
        ensure_ascii=False,
        sort_keys=True,
    ))
    if status in ("ASSEMBLED_STATIC_ONLY", "NOT_RECONSTRUCTED"):
        return EXIT_OK
    print(
        f"assembly_cli: assembly refused: {status}: {receipt.get('reason')}",
        file=sys.stderr,
    )
    return EXIT_REFUSED


def cmd_verify(args) -> int:
    def fail(message: str) -> int:
        print(f"assembly_cli: verify FAILED: {message}", file=sys.stderr)
        return EXIT_VERIFY_FAILED

    artifact_dir = Path(args.artifact_dir)
    if not artifact_dir.is_dir():
        return fail(f"artifact dir not found: {artifact_dir}")
    receipt_path = artifact_dir / "receipt.json"
    if not receipt_path.is_file():
        return fail(f"receipt.json not found in {artifact_dir}")
    if receipt_path.stat().st_size > MAX_INPUT_BYTES:
        return fail(f"receipt.json exceeds the {MAX_INPUT_BYTES}-byte input cap")
    try:
        receipt_bytes = receipt_path.read_bytes()
        receipt = json.loads(receipt_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return fail(f"receipt.json is not readable UTF-8 JSON: {exc}")
    if not isinstance(receipt, dict) or receipt.get("kind") != "assembly_receipt":
        return fail("receipt.json is not an assembly_receipt object")
    for key in ("assembly_status", "geometry_status"):
        value = receipt.get(key)
        if isinstance(value, str) and any(marker == value for marker in FORBIDDEN_MARKERS):
            return fail(f"receipt {key} is the forbidden claim {value!r}")
    status = receipt.get("assembly_status")
    if status not in ASSEMBLY_STATUSES:
        return fail(f"receipt assembly_status {status!r} is outside ASSEMBLY_STATUSES")
    if status != "ASSEMBLED_STATIC_ONLY":
        return fail(
            f"receipt records {status!r}; only ASSEMBLED_STATIC_ONLY artifact sets are verifiable"
        )
    assembled = receipt.get("assembled")
    if not isinstance(assembled, dict):
        return fail("receipt carries no assembled manifest")
    assembly_id = receipt.get("assembly_id")
    if not isinstance(assembly_id, str) or not ASSEMBLY_ID_RE.match(assembly_id):
        return fail(f"receipt assembly_id {assembly_id!r} is not a usable artifact stem")
    for label, key in ((f"{assembly_id}.top", "topology_text_sha256"),
                       (f"{assembly_id}.dat", "configuration_text_sha256")):
        path = artifact_dir / label
        if not path.is_file():
            return fail(f"missing artifact file: {label}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != assembled.get(key):
            return fail(
                f"{label} sha256 {digest} does not match the receipt digest {assembled.get(key)!r} "
                "(tampered or foreign artifact)"
            )
    try:
        topology = Topology.parse((artifact_dir / f"{assembly_id}.top").read_text(encoding="utf-8"))
        topology.check_chain_integrity()
    except (OSError, UnicodeDecodeError, TopologyError) as exc:
        return fail(f"strict topology reparse failed: {exc}")
    if topology.nucleotides != assembled.get("nucleotides"):
        return fail(
            f"topology nucleotides {topology.nucleotides} != receipt nucleotides "
            f"{assembled.get('nucleotides')}"
        )
    if topology.strand_count != assembled.get("strands"):
        return fail(
            f"topology strand count {topology.strand_count} != receipt strand count "
            f"{assembled.get('strands')}"
        )
    try:
        configuration = Configuration.parse(
            (artifact_dir / f"{assembly_id}.dat").read_text(encoding="utf-8")
        )
    except (OSError, UnicodeDecodeError, ConfError) as exc:
        return fail(f"strict configuration reparse failed: {exc}")
    if len(configuration.particles) != assembled.get("nucleotides"):
        return fail(
            f"configuration particle count {len(configuration.particles)} != receipt nucleotides "
            f"{assembled.get('nucleotides')}"
        )
    print(f"verify ok: {artifact_dir}")
    return EXIT_OK


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="assembly_cli",
        description="Deterministic offline static two-component DNA assembly CLI "
                    "(ASSEMBLED_STATIC_ONLY ceiling; never a scientific pass).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_assemble = sub.add_parser(
        "assemble",
        help="assemble driver+follower component specs into oxDNA artifacts + receipt",
    )
    p_assemble.add_argument("--driver-spec", required=True,
                            help="driver MechanicalComponentSpec JSON")
    p_assemble.add_argument("--follower-spec", required=True,
                            help="follower MechanicalComponentSpec JSON")
    p_assemble.add_argument("--assembly-spec", required=True, help="AssemblySpec JSON")
    p_assemble.add_argument("--recipe", default=None,
                            help="interface recipe JSON for SOURCE_VERIFIED assemblies "
                                 "(must be the file declared by interface_recipe_ref.path)")
    p_assemble.add_argument("--recipe-base", default=None,
                            help="directory against which interface_recipe_ref.path is resolved "
                                 "(default: the --recipe file's directory)")
    p_assemble.add_argument("--input-root", default=".",
                            help="root for resolving relative pinned topology/configuration uris "
                                 "(default: current working directory)")
    p_assemble.add_argument("--outdir", required=True,
                            help="output directory (must be a relative path without '..' inside "
                                 "the working directory tree; must not exist or must be empty)")

    p_verify = sub.add_parser(
        "verify",
        help="re-verify an artifact dir against its receipt (sha256 + strict reparse)",
    )
    p_verify.add_argument("--artifact-dir", required=True,
                          help="artifact directory produced by 'assemble'")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "assemble":
            return cmd_assemble(args)
        return cmd_verify(args)
    except CliRefusal as refusal:
        print(f"assembly_cli: error: {refusal.message}", file=sys.stderr)
        return EXIT_REFUSED


if __name__ == "__main__":
    raise SystemExit(main())
