"""[REVIEWER-76] RED->GREEN re-verification without modifying the repo.

Runs the HEAD test module tests/test_alt_pair_source_gate.py against:
  (a) the R1.1-era gate blob 1064c879 (head 3d0b55b9)  -> the 3 R1.2 falsifiers must FAIL
  (b) the HEAD gate blob c2fdf3a1 (head 2e199d6)       -> all must PASS
The R1.2 falsifier tests are the ones whose names contain:
  falsifier_reversed_duplicate_port_pair, falsifier_nonunit_particle_orientation,
  falsifier_nonfinite_box, distinct_terminal_bonds_with_overlapping_nucleotides,
  distinct_terminal_bonds_with_nonoverlapping_nucleotides
"""
import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path("/home/rdpuser/NanoLab/review-pr76-r1")
OLD_BLOB = "1064c879baca5bc21db31298413a141f901dd252"  # R1.1 gate code blob

FALSIFIERS = (
    "test_falsifier_reversed_duplicate_port_pair_must_block",
    "test_falsifier_nonunit_particle_orientation_must_block",
    "test_falsifier_nonfinite_box_must_block",
    "test_distinct_terminal_bonds_with_overlapping_nucleotides_blocked",
    "test_distinct_terminal_bonds_with_nonoverlapping_nucleotides_allowed",
)


def load_suite(gate_file: Path, label: str):
    scratch = Path("/tmp/redgreen") / label
    (scratch / "scripts" / "knowledge_pack").mkdir(parents=True, exist_ok=True)
    (scratch / "scripts" / "hinge_family").mkdir(parents=True, exist_ok=True)
    import shutil
    for src in (REPO / "scripts/hinge_family").glob("*.py"):
        shutil.copy(src, scratch / "scripts/hinge_family" / src.name)
    for src in (REPO / "scripts/knowledge_pack").glob("*.py"):
        shutil.copy(src, scratch / "scripts/knowledge_pack" / src.name)
    shutil.copy(gate_file, scratch / "scripts/knowledge_pack/alt_pair_source_gate.py")

    # 1) import the candidate gate from the scratch scripts dir
    sys.path.insert(0, str(scratch / "scripts"))
    for mod in [m for m in list(sys.modules) if m.startswith(("knowledge_pack", "hinge_family"))]:
        del sys.modules[mod]
    import knowledge_pack.alt_pair_source_gate as loaded  # noqa: F401

    # 2) load the HEAD test module with repo root patched so PACK_FILE still resolves
    spec = importlib.util.spec_from_file_location(
        f"tests_under_{label}", REPO / "tests/test_alt_pair_source_gate.py")
    mod = importlib.util.module_from_spec(spec)
    saved = mod.__dict__
    spec.loader.exec_module(mod)  # module inserts REPO/scripts into sys.path, but
    # knowledge_pack is already cached from the scratch dir, so `gate` is the candidate build
    assert loaded is mod.gate, "test module must bind the candidate gate build"
    suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
    return suite


def run(label: str, gate_source: Path):
    suite = load_suite(gate_source, label)
    buf = io.StringIO()
    runner = unittest.TextTestRunner(stream=buf, verbosity=0)
    with redirect_stdout(buf):
        result = runner.run(suite)
    print(f"=== gate build {label}: {gate_source.read_bytes()[:0]}")
    print(f"run={label} tests={result.testsRun} failures={len(result.failures)} errors={len(result.errors)}")
    failed = {t.id().split(".")[-1] for t, _ in result.failures + result.errors}
    print("  raw failures on this build:", sorted(failed))
    for name in FALSIFIERS:
        print(f"  {'FAIL' if name in failed else 'PASS'}  {name}")
    return failed


if __name__ == "__main__":
    import subprocess
    old = Path("/tmp/redgreen_old_gate.py")
    old.write_bytes(subprocess.run(
        ["git", "-C", str(REPO), "cat-file", "blob", OLD_BLOB],
        check=True, capture_output=True).stdout)
    head = REPO / "scripts/knowledge_pack/alt_pair_source_gate.py"
    old_failed = run("r11_old", old)
    head_failed = run("head", head)
    print("\n=== REVIEWER CONCLUSION ===")
    print("old R1.1 build falsifier failures:", sorted(old_failed & set(FALSIFIERS)))
    print("HEAD build falsifier failures:", sorted(head_failed & set(FALSIFIERS)))
    ok = old_failed and not head_failed
    print("RED->GREEN independently reproduced:" , bool(ok))
