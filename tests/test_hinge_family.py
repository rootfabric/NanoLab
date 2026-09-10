"""NL3-001 tests for the hinge-family toolchain (scripts/hinge_family).

Coverage contract (WO-NL3-001):
- determinism: two invocations produce byte-identical canonical reports;
- digest gate: any tampered source byte fails the run;
- structural negatives: broken topology/configuration/design/sim-input
  parameters fail with explicit errors, never pass silently;
- positive: a consistent synthetic surface passes;
- the bundled source_pins.json satisfies the fail-closed registry contract.

All tests are stdlib-only and network-free; source surfaces are synthetic.
"""
from __future__ import annotations

import json
import math
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from hinge_family.canonical import canonical_json  # noqa: E402
from hinge_family.pins import PinsError, git_blob_sha1, load_pins, sha256_hex  # noqa: E402
from hinge_family.validate import run_validation  # noqa: E402


# --------------------------------------------------------------------- helpers
def make_topology(strand_lengths=(8, 8)):
    """Two linear strands listed 3'->5' (first row of a strand has n3 = -1)."""
    rows = []
    for sid, length in enumerate(strand_lengths, start=1):
        start = len(rows)
        for i in range(length):
            n3 = start + i - 1 if i > 0 else -1
            n5 = start + i + 1 if i < length - 1 else -1
            base = "ATCG"[i % 4]
            rows.append((sid, base, n3, n5))
    header = f"{len(rows)} {len(strand_lengths)}\n"
    body = "".join(f"{sid} {base} {n3} {n5}\n" for sid, base, n3, n5 in rows)
    return header + body, len(rows)


def make_conf(nucleotides, spacing=0.6):
    lines = [
        "t = 1000",
        "b = 100.0 100.0 100.0",
        "E = -1.0 2.0 1.0",
    ]
    for i in range(nucleotides):
        pos = (1.0 + spacing * i, 2.0, 3.0)
        o1 = (0.0, 0.0, 1.0)
        o2 = (1.0, 0.0, 0.0)
        vel = (0.01, -0.02, 0.03)
        angular = (0.0, 0.0, 0.0)
        values = [*pos, *o1, *o2, *vel, *angular]
        lines.append(" ".join(repr(v) for v in values))
    return "\n".join(lines) + "\n"


def make_design(cells_per_helix=(8,), helix_count=1):
    """Minimal caDNAno design: each helix carries one scaffold and one staple path."""
    vstrands = []
    for num in range(helix_count):
        n = cells_per_helix[num % len(cells_per_helix)]
        rows = 2 * n

        def cell_list():
            return [[-1, -1, -1, -1] for _ in range(rows)]

        scaf, stap = cell_list(), cell_list()
        for kind, grid in (("scaf", scaf), ("stap", stap)):
            for i in range(n):
                grid[i] = [
                    num if i > 0 else -1,
                    i - 1 if i > 0 else -1,
                    num if i < n - 1 else -1,
                    i + 1 if i < n - 1 else -1,
                ]
        vstrands.append(
            {
                "num": num,
                "row": num,
                "col": num,
                "scaf": scaf,
                "stap": stap,
                "loop": [0] * rows,
                "skip": [0] * rows,
                "scafLoop": [0] * rows,
                "stapLoop": [0] * rows,
                "stap_colors": [],
            }
        )
    return json.dumps({"name": "synthetic.json", "vstrands": vstrands}, indent=1) + "\n"


SIM_INPUT = """##############################
####  PROGRAM PARAMETERS  ####
##############################
backend = CPU
backend_precision = double
seed = 7777

##############################
####    SIM PARAMETERS    ####
##############################
steps = 2e7
thermostat = john
interaction_type = DNA2
salt_concentration = 0.5

T = 300K
"""


def write_pins(path: Path, files: dict, variant: str = "0b") -> None:
    registry = {
        "schema_version": 1,
        "registry_id": "SYNTHETIC-PINS",
        "work_order": "TEST",
        "execution_id": "TEST",
        "source": {
            "repository": "synthetic/source",
            "commit": "a" * 40,
            "tree": "b" * 40,
            "rights": "UNKNOWN",
            "mode": "REFERENCE_ONLY",
            "obtain_procedure": "synthetic test surface; nothing is downloaded",
        },
        "files": files,
        "variants": {
            variant: {
                "role": "FIRST_INSTANCE_CONTROL",
                "topology": "syn.top",
                "configuration": "syn.conf",
                "design": "syn.json",
                "sim_input_cpu": "syn.in",
                "spring_layers_reported_bases": [0, 24],
                "spring_layers_source": "REPORTED (synthetic)",
            }
        },
        "sim_input_preregistered_values": {
            "interaction_type": "DNA2",
            "salt_concentration": "0.5",
            "T": "300K",
            "steps": "2e7",
            "backend": "CPU",
            "backend_precision": "double",
            "source": "synthetic",
        },
    }
    path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def pin_entry(data: bytes, with_sha256: bool = True) -> dict:
    entry = {
        "size_bytes": len(data),
        "blob_sha1": git_blob_sha1(data),
        "sha256": sha256_hex(data) if with_sha256 else None,
        "blob_sha1_provenance": "R1_TREE_LISTING",
        "sha256_provenance": "R1_CONTENT_VERIFIED" if with_sha256 else "NOT_VERIFIED",
    }
    return entry


class SyntheticSurfaceCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hinge-family-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        top_text, n = make_topology()
        self.top_bytes = top_text.encode("utf-8")
        self.conf_bytes = make_conf(n).encode("utf-8")
        self.design_bytes = make_design().encode("utf-8")
        self.sim_bytes = SIM_INPUT.encode("utf-8")
        (self.tmp / "src").mkdir()
        (self.tmp / "src" / "syn.top").write_bytes(self.top_bytes)
        (self.tmp / "src" / "syn.conf").write_bytes(self.conf_bytes)
        (self.tmp / "src" / "syn.json").write_bytes(self.design_bytes)
        (self.tmp / "src" / "syn.in").write_bytes(self.sim_bytes)
        self.pins_path = self.tmp / "pins.json"
        write_pins(
            self.pins_path,
            {
                "syn.top": pin_entry(self.top_bytes),
                "syn.conf": pin_entry(self.conf_bytes),
                "syn.json": pin_entry(self.design_bytes),
                "syn.in": pin_entry(self.sim_bytes),
            },
        )

    def validate(self, pins=None, source=None, variant="0b"):
        return run_validation(pins or self.pins_path, source or (self.tmp / "src"), variant)

    # ------------------------------------------------------------- positives
    def test_consistent_surface_passes(self):
        outcome = self.validate()
        self.assertTrue(outcome.ok, outcome.text)
        for check in outcome.report["checks"]:
            self.assertEqual(check["status"], "PASS", check)

    def test_design_bases_equal_topology_nucleotides(self):
        outcome = self.validate()
        ids = [c["id"] for c in outcome.report["checks"] if c["status"] == "PASS"]
        self.assertIn("design_bases_equal_topology_nucleotides", ids)
        self.assertEqual(outcome.report["facts"]["design"]["total_bases"], 16)
        self.assertEqual(outcome.report["facts"]["topology"]["nucleotides"], 16)

    def test_determinism_byte_identical_reports(self):
        first = self.validate()
        second = self.validate()
        self.assertEqual(first.text, second.text)
        self.assertTrue(first.ok)
        path_a = self.tmp / "report-a.json"
        path_b = self.tmp / "report-b.json"
        from hinge_family.validate import main as cli_main

        for path in (path_a, path_b):
            exit_code = cli_main(
                [
                    "validate",
                    "--source-dir",
                    str(self.tmp / "src"),
                    "--pins",
                    str(self.pins_path),
                    "--report",
                    str(path),
                ]
            )
            self.assertEqual(exit_code, 0)
        self.assertEqual(path_a.read_bytes(), path_b.read_bytes())
        # canonical serialization: sorted keys, trailing newline
        text = path_a.read_text(encoding="utf-8")
        self.assertTrue(text.endswith("}\n"))
        self.assertEqual(json.loads(text), json.loads(canonical_json(json.loads(text))[:-1]))

    def test_report_contains_no_wall_clock_fields(self):
        outcome = self.validate()
        blob = outcome.text.lower()
        for forbidden in ("timestamp", "generated", "wall_clock", "utc", "iso_date"):
            self.assertNotIn(forbidden, blob)
        # machine time may not leak through the parsed configuration header either
        self.assertNotIn("timestamp", blob)

    # ------------------------------------------------------------- negatives
    def test_tampered_byte_fails_digest_gate(self):
        tampered = bytearray(self.top_bytes)
        tampered[0] = ord("9") if tampered[0] != ord("9") else ord("8")
        (self.tmp / "src" / "syn.top").write_bytes(bytes(tampered))
        outcome = self.validate()
        self.assertFalse(outcome.ok)
        failed = {c["id"] for c in outcome.report["checks"] if c["status"] == "FAIL"}
        self.assertIn("source_digests_match_pins", failed)
        self.assertIs(outcome.report["digest_verification"]["topology"]["sha256_ok"], False)

    def test_truncated_file_fails_size_gate(self):
        (self.tmp / "src" / "syn.conf").write_bytes(self.conf_bytes[:-4])
        outcome = self.validate()
        self.assertFalse(outcome.ok)
        self.assertIs(outcome.report["digest_verification"]["configuration"]["size_ok"], False)

    def test_missing_source_file_fails(self):
        (self.tmp / "src" / "syn.json").unlink()
        outcome = self.validate()
        self.assertFalse(outcome.ok)
        self.assertIn("read_error", outcome.report["digest_verification"]["design"])

    def test_topology_invalid_base_letter(self):
        top_text, _ = make_topology()
        bad = top_text.replace(" A ", " X ", 1).encode("utf-8")
        self.assertNotEqual(bad, self.top_bytes)
        self._rewrite_pins_for_topology(bad)
        outcome = self.validate()
        self.assertFalse(outcome.ok)
        self.assertTrue(any("invalid base letter" in c["detail"] for c in outcome.report["checks"] if c["status"] == "FAIL"))

    def test_topology_broken_chain_links(self):
        top_text, _ = make_topology()
        lines = top_text.splitlines()
        # break the mutual n3/n5 consistency of the first strand
        lines[1] = lines[1].replace(" -1 1", " -1 3", 1)
        bad = "\n".join(lines) + "\n"
        self._rewrite_pins_for_topology(bad.encode("utf-8"))
        outcome = self.validate()
        self.assertFalse(outcome.ok)

    def test_topology_row_count_mismatch(self):
        top_text, _ = make_topology()
        lines = top_text.splitlines()
        lines[0] = "9 2"
        bad = ("\n".join(lines) + "\n").encode("utf-8")
        self._rewrite_pins_for_topology(bad)
        outcome = self.validate()
        self.assertFalse(outcome.ok)
        self.assertTrue(any("declares" in c["detail"] for c in outcome.report["checks"] if c["status"] == "FAIL"))

    def test_conf_nan_fails(self):
        lines = self.conf_bytes.decode("utf-8").splitlines()
        lines[3] = lines[3].replace(repr(2.0), repr(float("nan")), 1)
        self._rewrite_pins_for_conf(("\n".join(lines) + "\n").encode("utf-8"))
        outcome = self.validate()
        self.assertFalse(outcome.ok)
        self.assertTrue(any("NaN" in c["detail"] for c in outcome.report["checks"] if c["status"] == "FAIL"))

    def test_conf_column_count_fails(self):
        lines = self.conf_bytes.decode("utf-8").splitlines()
        lines[3] = " ".join(lines[3].split()[:14])
        self._rewrite_pins_for_conf(("\n".join(lines) + "\n").encode("utf-8"))
        outcome = self.validate()
        self.assertFalse(outcome.ok)
        self.assertTrue(any("15 columns" in c["detail"] for c in outcome.report["checks"] if c["status"] == "FAIL"))

    def test_conf_non_unit_orientation_fails(self):
        lines = self.conf_bytes.decode("utf-8").splitlines()
        parts = lines[3].split()
        parts[3] = repr(0.5)
        lines[3] = " ".join(parts)
        self._rewrite_pins_for_conf(("\n".join(lines) + "\n").encode("utf-8"))
        outcome = self.validate()
        self.assertFalse(outcome.ok)
        self.assertTrue(any("unit/orthogonal" in c["detail"] for c in outcome.report["checks"] if c["status"] == "FAIL"))

    def test_conf_particle_count_mismatch_fails(self):
        conf = self.conf_bytes.decode("utf-8").splitlines()
        conf = conf[:-1]
        self._rewrite_pins_for_conf(("\n".join(conf) + "\n").encode("utf-8"))
        outcome = self.validate()
        self.assertFalse(outcome.ok)
        self.assertTrue(any("particles" in c["detail"] for c in outcome.report["checks"] if c["status"] == "FAIL"))

    def test_design_pointer_inconsistency_fails(self):
        design = json.loads(self.design_bytes.decode("utf-8"))
        v0 = design["vstrands"][0]
        v0["scaf"][0] = [-1, -1, 0, 5]  # next jumps past the used cell (0,1)
        bad = (json.dumps(design, indent=1) + "\n").encode("utf-8")
        self._rewrite_pins_for_design(bad)
        outcome = self.validate()
        self.assertFalse(outcome.ok)

    def test_design_base_count_mismatch_fails(self):
        design = json.loads(self.design_bytes.decode("utf-8"))
        v0 = design["vstrands"][0]
        # drop two cells from each grid (truncate the path at row 6)
        for grid in (v0["scaf"], v0["stap"]):
            grid[6] = [-1, -1, -1, -1]
            grid[7] = [-1, -1, -1, -1]
        v0["scaf"][5] = [0, 4, -1, -1]
        v0["stap"][5] = [0, 4, -1, -1]
        bad = (json.dumps(design, indent=1) + "\n").encode("utf-8")
        self._rewrite_pins_for_design(bad)
        outcome = self.validate()
        self.assertFalse(outcome.ok)
        self.assertTrue(
            any("bases" in c["detail"] and "nucleotides" in c["detail"] for c in outcome.report["checks"] if c["status"] == "FAIL")
        )

    def test_sim_input_wrong_temperature_fails(self):
        bad = SIM_INPUT.replace("T = 300K", "T = 310K").encode("utf-8")
        self._rewrite_pins_for_sim(bad)
        outcome = self.validate()
        self.assertFalse(outcome.ok)
        self.assertTrue(any("preregistered" in c["detail"] for c in outcome.report["checks"] if c["status"] == "FAIL"))

    # ------------------------------------------------------------ pins gate
    def test_pins_registry_rejects_malformed_blob_sha(self):
        files = {
            "syn.top": pin_entry(self.top_bytes),
            "syn.conf": pin_entry(self.conf_bytes),
            "syn.json": pin_entry(self.design_bytes),
            "syn.in": pin_entry(self.sim_bytes),
        }
        files["syn.top"]["blob_sha1"] = "zz" * 20
        bad_pins = self.tmp / "bad-pins.json"
        write_pins(bad_pins, files)
        with self.assertRaises(PinsError):
            load_pins(bad_pins)

    def test_pins_registry_requires_reference_only_mode(self):
        files = {
            "syn.top": pin_entry(self.top_bytes),
            "syn.conf": pin_entry(self.conf_bytes),
            "syn.json": pin_entry(self.design_bytes),
            "syn.in": pin_entry(self.sim_bytes),
        }
        bad_pins = self.tmp / "bad-mode.json"
        write_pins(bad_pins, files)
        data = json.loads(bad_pins.read_text(encoding="utf-8"))
        data["source"]["mode"] = "VENDORED"
        bad_pins.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(PinsError):
            load_pins(bad_pins)

    def test_bundled_pins_registry_satisfies_contract(self):
        pins = load_pins(REPO_ROOT / "scripts" / "hinge_family" / "source_pins.json")
        self.assertEqual(pins["source"]["mode"], "REFERENCE_ONLY")
        self.assertEqual(pins["source"]["commit"], "23fd1ff7731e9017bd776f49206dc42d70d9fe91")
        self.assertEqual(pins["source"]["tree"], "b2d6cebc7a33ed13e4e9c8d79fe8350ce11e82b9")
        for name, entry in pins["files"].items():
            self.assertTrue(entry["size_bytes"] > 0, name)
        verified = {name for name, entry in pins["files"].items() if entry["sha256"]}
        self.assertEqual(
            verified,
            {
                "MD_Hinges/0b.top",
                "MD_Hinges/0b.conf",
                "Design_Hinges/0b.json",
                "MD_Hinges/pro_CPU.in",
                "MD_Hinges/README.md",
            },
        )
        # preregistered NL0-001 blob pins must be unchanged
        self.assertEqual(pins["files"]["Design_Hinges/0b.json"]["blob_sha1"], "0ed4075c3a0d2f29601d35c5ce70f2df6b0be1ed")
        self.assertEqual(pins["files"]["MD_Hinges/pro_CPU.in"]["blob_sha1"], "89d76310ce726eaec9e7acb312bd7b0fc43fa735")
        self.assertTrue(pins["variants"]["0b"]["validated_in_R1"])
        for name in ("11b", "32b", "53b", "74b"):
            self.assertEqual(pins["variants"][name]["role"], "REGISTERED_NOT_VALIDATED")

    # -------------------------------------------------------------- plumbing
    def _rewrite_pins_for_topology(self, data: bytes):
        files = json.loads(self.pins_path.read_text(encoding="utf-8"))["files"]
        files["syn.top"] = pin_entry(data)
        write_pins(self.pins_path, files)
        (self.tmp / "src" / "syn.top").write_bytes(data)

    def _rewrite_pins_for_conf(self, data: bytes):
        files = json.loads(self.pins_path.read_text(encoding="utf-8"))["files"]
        files["syn.conf"] = pin_entry(data)
        write_pins(self.pins_path, files)
        (self.tmp / "src" / "syn.conf").write_bytes(data)

    def _rewrite_pins_for_design(self, data: bytes):
        files = json.loads(self.pins_path.read_text(encoding="utf-8"))["files"]
        files["syn.json"] = pin_entry(data)
        write_pins(self.pins_path, files)
        (self.tmp / "src" / "syn.json").write_bytes(data)

    def _rewrite_pins_for_sim(self, data: bytes):
        files = json.loads(self.pins_path.read_text(encoding="utf-8"))["files"]
        files["syn.in"] = pin_entry(data)
        write_pins(self.pins_path, files)
        (self.tmp / "src" / "syn.in").write_bytes(data)


class GitBlobShaCase(unittest.TestCase):
    def test_known_vector(self):
        # "blob 3\x00abc" must hash like git would label an "abc" blob
        self.assertEqual(git_blob_sha1(b"abc"), "f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f")
        self.assertEqual(len(sha256_hex(b"abc")), 64)

    def test_orientation_scale_is_unit(self):
        # guard the helper used by fixtures: vectors are unit and orthogonal
        a = (0.0, 0.0, 1.0)
        b = (1.0, 0.0, 0.0)
        self.assertAlmostEqual(math.sqrt(sum(x * x for x in a)), 1.0)
        self.assertAlmostEqual(sum(x * y for x, y in zip(a, b)), 0.0)


if __name__ == "__main__":
    unittest.main()
