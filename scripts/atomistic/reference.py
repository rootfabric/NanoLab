"""Offline checks for the Cu bulk reference draft. No calculator or launch path."""

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sys


DEFAULT_PACKAGE = Path(__file__).resolve().parents[2] / "docs/atomistic/reference/cu-r1"
REFERENCE_ID = "CU_BULK_EMT_R1"
MODEL = {
    "id": "ASE_EMT_Cu",
    "ase_version": "3.26.0",
    "calculator": "ase.calculators.emt.EMT",
    "parameters": {"asap_cutoff": False},
}
MATERIAL = {"element": "Cu", "crystal_structure": "fcc", "boundary": "periodic_bulk"}
SOURCE_ID = "overton-gaffney-1955"
DOI = "10.1103/PhysRev.98.969"
LOCATOR = "p. 975, Table II, T = 0 K row, K^T column"
OBSERVABLE_ID = "bulk_modulus_isothermal_0k"
ROLE = "fit_sensitive_bulk_consistency"
TEMPERATURE_BASIS = "extrapolated_from_measurements"
PRESSURE_BASIS = "ambient_pressure_not_quantified"
UNCERTAINTY_BASIS = (
    "Отдельная погрешность K^T для строки 0 K в статье не указана. Число 0,34 % относится к вероятной "
    "погрешности K^S (с. 974, текст перед Eq. (5)), не к интервалу неопределённости K^T."
)
ARTIFACT_ARCHIVES = {
    "ase-wheel": "https://files.pythonhosted.org/packages/dd/f0/6e52d797bee63530f4b778cb4cbb3a01970f104197c364a8ff51bc9f5a21/ase-3.26.0-py3-none-any.whl",
    "ase-sdist": "https://files.pythonhosted.org/packages/30/33/2ffa44950267450f6a5cdb711c68e12d0d72d626e246e5897e3bada7bac6/ase-3.26.0.tar.gz",
}
ARTIFACT_MEMBERS = {
    "ase-emt-module": ("ase-wheel", "ase/calculators/emt.py"),
    "ase-license-notice": ("ase-wheel", "ase-3.26.0.dist-info/licenses/LICENSE"),
    "ase-wheel-metadata": ("ase-wheel", "ase-3.26.0.dist-info/METADATA"),
    "ase-lgpl-text": ("ase-sdist", "ase-3.26.0/COPYING.LESSER"),
}


class ValidationError(ValueError):
    """The reference draft is missing or inconsistent."""


def _check(ok, label):
    if not ok:
        raise ValidationError(label)


def _expect(record, expected, label):
    _check(isinstance(record, dict), f"{label}: expected an object")
    for name, value in expected.items():
        # JSON distinguishes true/false from 1/0, unlike Python equality.
        _check(json.dumps(record.get(name), sort_keys=True) == json.dumps(value, sort_keys=True)
               and name in record, f"{label}.{name}: unexpected value")


def _fields(record, names, label):
    _check(isinstance(record, dict) and record.keys() == set(names.split()),
           f"{label}: missing or unexpected fields")


def _only(items, label):
    _check(isinstance(items, list) and len(items) == 1 and isinstance(items[0], dict),
           f"{label}: expected one record")
    return items[0]


def _pairs(pairs):
    data = {}
    for key, value in pairs:
        _check(key not in data, f"duplicate JSON key: {key}")
        data[key] = value
    return data


def _bad_constant(token):
    raise ValidationError(f"non-finite JSON constant: {token}")


def _read(root, relative):
    # relative is always a fixed package path, never a path supplied by JSON.
    path = root / relative
    try:
        _check(path.resolve() == path and path.is_file(), f"{relative}: missing or unsafe file")
        return path.read_bytes()
    except (OSError, RuntimeError) as exc:
        raise ValidationError(f"{relative}: {exc}") from exc


def _json(raw, relative):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_bad_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{relative}: {exc}") from exc


def _pin(record, label, raw=None):
    sha256, size = record.get("sha256"), record.get("size_bytes")
    _check(isinstance(sha256, str) and re.fullmatch(r"[0-9a-f]{64}", sha256)
           and type(size) is int and size > 0, f"{label}: invalid SHA-256 or byte count")
    if raw is not None:
        _check(len(raw) == size and hashlib.sha256(raw).hexdigest() == sha256,
               f"{label}: SHA-256 or byte count does not match local file")


def _local(root, record, relative):
    _fields(record, "local_path sha256 size_bytes", relative)
    _expect(record, {"local_path": relative}, relative)
    raw = _read(root, relative)
    _pin(record, relative, raw)
    return raw


def _validate_model(model):
    _fields(model, "id ase_version calculator parameters license distribution_policy upstream_url "
            "release_metadata_url theory_url theory_doi artifacts", "model")
    _expect(model, {
        **MODEL, "license": "LGPL-2.1-or-later", "distribution_policy": "download_on_setup",
        "upstream_url": "https://gitlab.com/ase/ase/-/raw/3.26.0/ase/calculators/emt.py",
        "release_metadata_url": "https://pypi.org/pypi/ase/3.26.0/json",
        "theory_url": "https://docs.ase-lib.org/ase/calculators/emt.html#theory",
        "theory_doi": "10.1016/0039-6028(96)00816-3",
    }, "model")
    expected_ids = {*ARTIFACT_ARCHIVES, *ARTIFACT_MEMBERS}
    pins = model["artifacts"]
    _check(isinstance(pins, list) and len(pins) == len(expected_ids), "model.artifacts: expected release pins")
    artifacts = {}
    for pin in pins:
        _check(isinstance(pin, dict) and isinstance(pin.get("id"), str), "model.artifacts: invalid ID")
        artifact_id = pin["id"]
        _check(artifact_id in expected_ids and artifact_id not in artifacts, f"model.artifacts: unexpected ID {artifact_id}")
        keys = "id url sha256 size_bytes" + (" member" if artifact_id in ARTIFACT_MEMBERS else "")
        _fields(pin, keys, artifact_id)
        _pin(pin, artifact_id)
        artifacts[artifact_id] = pin
    for archive, url in ARTIFACT_ARCHIVES.items():
        _expect(artifacts[archive], {"url": url}, archive)
    for artifact_id, (archive, member) in ARTIFACT_MEMBERS.items():
        _expect(artifacts[artifact_id], {"url": artifacts[archive]["url"], "member": member}, artifact_id)


def _validate_source(root, manifest):
    source = _only(manifest["sources"], "sources")
    _fields(source, "id doi url full_text_url citation locator rights access artifact", "source")
    _expect(source, {
        "id": SOURCE_ID, "doi": DOI,
        "url": f"https://journals.aps.org/pr/abstract/{DOI}",
        "full_text_url": f"https://harvest.aps.org/v2/journals/articles/{DOI}/fulltext",
        "citation": "W. C. Overton, Jr., J. Gaffney, Physical Review 98 (1955), 969–977.",
        "locator": f"pp. 969 and 972–976; Eq. (5), Tables I–III; reference datum: {LOCATOR}",
        "rights": {"copyright": "© 1955 American Physical Society", "redistribute_full_text": False,
                   "policy": "reference_only"},
        "access": {"full_text_inspected": True, "inspection_method": "publisher_pdf_via_web_index",
                   "direct_pdf_status": "HTTP_401_OR_403", "original_pdf_sha256": None},
    }, "source")
    observable = _only(manifest["observables"], "observables")
    _fields(observable, "id source_id locator role value unit temperature_k temperature_basis "
            "pressure_basis original source_uncertainty", "source observable")
    _expect(observable, {
        "id": OBSERVABLE_ID, "source_id": SOURCE_ID, "role": ROLE, "locator": LOCATOR,
        "value": 142.03, "unit": "GPa", "temperature_k": 0,
        "temperature_basis": TEMPERATURE_BASIS, "pressure_basis": PRESSURE_BASIS,
        "original": {"value": 14.203, "unit": "1e11 dyn/cm^2"},
    }, "source observable")
    uncertainty = observable["source_uncertainty"]
    _fields(uncertainty, "value unit basis related_reported_relative_percent", "source uncertainty")
    _expect(uncertainty, {"value": None, "unit": "GPa", "basis": UNCERTAINTY_BASIS,
                          "related_reported_relative_percent": 0.34}, "source uncertainty")

    facts_path = "source-artifacts/overton-gaffney-1955-facts.json"
    facts = _json(_local(root, source["artifact"], facts_path), facts_path)
    _fields(facts, "schema_version source_id doi observable measurement_temperature_range_k", "source facts")
    _expect(facts, {
        "schema_version": 1, "source_id": SOURCE_ID, "doi": DOI, "measurement_temperature_range_k": [4.2, 300],
        "observable": {key: val for key, val in observable.items() if key not in ("source_id", "role")},
    }, "source facts")
    return observable


def _validate_method(protocol):
    scenario = {**MATERIAL, "pbc": [True, True, True], "temperature_k": 0,
                "external_pressure_gpa": 0, "reference_temperature_basis": TEMPERATURE_BASIS,
                "reference_pressure_basis": PRESSURE_BASIS, "phase": "static_classical_perfect_crystal",
                "conventional_cell_atoms": 4, "repeat_cubes_per_axis": [4, 5], "anchor_lattice_angstrom": 3.60,
                "reference_calibration_independence": "UNVERIFIED"}
    _expect(protocol, {"scenario": scenario}, "protocol")
    numerics = {
        "energy_unit": "eV/atom", "volume_unit": "angstrom^3/atom", "gpa_per_ev_per_angstrom3": 160.2176634,
        "primary_method": "narrow_cubic_energy_volume_fit",
        "coarse_volume_fraction_offsets": [i and i / 100 for i in range(-8, 9, 2)],
        "wide_volume_fraction_offsets": [i and i / 100 for i in range(-4, 5)],
        "narrow_volume_fraction_offsets": [i and i / 200 for i in range(-4, 5)],
        "finite_difference_volume_fraction_steps": [0.005, 0.0025],
        "checks": ["wide_cubic", "narrow_quartic", "larger_cell_narrow_cubic", "direct_finite_differences"],
        "max_force_ev_per_angstrom": 1e-6, "max_deviatoric_stress_gpa": 1e-6,
        "max_absolute_equilibrium_pressure_gpa": 0.10,
    }
    _fields(protocol["numerics"], " ".join(numerics), "numerics")
    _expect(protocol["numerics"], numerics, "numerics")
    n_evaluations = (len(numerics["coarse_volume_fraction_offsets"]) + len(numerics["wide_volume_fraction_offsets"])
                     + 2 * len(numerics["narrow_volume_fraction_offsets"])
                     + 1 + 2 * len(numerics["finite_difference_volume_fraction_steps"]))
    budget = {"max_campaign_attempts": 1, "max_static_evaluations": n_evaluations,
              "max_atoms": scenario["conventional_cell_atoms"] * max(scenario["repeat_cubes_per_axis"]) ** 3,
              "max_threads": 1, "max_wall_seconds": 120, "max_output_bytes": 16 * 1024**2, "md_steps": 0}
    _expect(protocol, {"proposed_future_budget": budget}, "protocol")


def validate_package(package=DEFAULT_PACKAGE):
    """Check local files and pin declarations; return a structural validation record."""
    root = Path(package).resolve()
    raw_protocol = _read(root, "protocol.json")
    protocol = _json(raw_protocol, "protocol.json")
    _fields(protocol, "schema_version reference_id status claim_class scientific_outcome scientific_runs_allowed "
            "physics_runs source_manifest method_document source_document model scenario observable numerics "
            "proposed_future_budget", "protocol")
    prep_state = {"status": "DRAFT_PREP_ONLY", "claim_class": "C0_SOFTWARE_ONLY", "scientific_outcome": "NOT_EVALUATED",
                  "scientific_runs_allowed": False, "physics_runs": 0}
    _expect(protocol, {"schema_version": 1, "reference_id": REFERENCE_ID, "model": MODEL, **prep_state}, "protocol")
    _local(root, protocol["method_document"], "PROTOCOL.md")
    _local(root, protocol["source_document"], "SOURCES.md")
    sources = _json(_local(root, protocol["source_manifest"], "sources.json"), "sources.json")
    _fields(sources, "schema_version reference_id material model sources observables", "sources.json")
    _expect(sources, {"schema_version": 1, "reference_id": REFERENCE_ID, "material": MATERIAL}, "sources.json")
    _validate_model(sources["model"])
    datum = _validate_source(root, sources)
    _validate_method(protocol)

    reference = Decimal(str(datum["value"]))
    _check(Decimal(str(datum["original"]["value"])) * 10 == reference, "source observable: GPa conversion mismatch")
    comparison = {"id": datum["id"], "source_id": datum["source_id"], "role": datum["role"],
                  "reference_value": datum["value"], "unit": datum["unit"], "engineering_tolerance_relative": 0.10,
                  "numerical_envelope_limit_relative": 0.01,
                  "comparison": "full_numerical_envelope_vs_closed_engineering_band"}
    _fields(protocol["observable"], " ".join(comparison), "comparison")
    _expect(protocol["observable"], comparison, "comparison")
    tolerance = reference * Decimal(str(comparison["engineering_tolerance_relative"]))
    return {
        "validation": "PACKAGE_VALID", "reference_id": REFERENCE_ID, **prep_state,
        "protocol_sha256": hashlib.sha256(raw_protocol).hexdigest(),
        "sources_sha256": protocol["source_manifest"]["sha256"],
        "remote_pins": "DECLARED_NOT_RECHECKED", "observable": datum["id"], "reference_gpa": float(reference),
        "engineering_band_gpa": [float(reference - tolerance), float(reference + tolerance)],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE, help="reference package directory")
    args = parser.parse_args(argv)
    try:
        report = validate_package(args.package)
    except ValidationError as exc:
        print(f"INVALID_PACKAGE: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
