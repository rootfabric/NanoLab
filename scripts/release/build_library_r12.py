"""R1.2 deterministic repair builder for nanolab-components-v0.1.

The historical R1 builder remains durable evidence. This module reuses its
non-authoritative assembly/templates, then rewrites emitted machine-readable
scientific/protocol/reproduction fields from published evidence and creates a
deterministic full-package manifest.

Normative commands after B-Repair R1:
    PYTHONPATH=scripts python3 -m release.build_library_r12 build
    PYTHONPATH=scripts python3 -m release.build_library_r12 check
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from release import build_library as legacy
from release import card_lint, reproduction_rule

REPO_ROOT = Path(__file__).resolve().parents[2]
PKG_ROOT = legacy.PKG_ROOT
RULE_DOC = REPO_ROOT / "docs" / "release" / "REPRODUCTION_RULE_V0_1.md"
CARD_0B_EVIDENCE = legacy.CARD_0B_EVIDENCE
PARAM_SUMMARY = legacy.PARAM_SUMMARY
FINAL_VERSION = "0.1.0"
FINAL_CODE_LICENSE = "Apache-2.0"
FINAL_DOCS_DATA_LICENSE = "CC-BY-4.0"
FINAL_CITATION_CFF = """cff-version: 1.2.0
message: "If you use this component library, please cite it and the upstream scientific sources referenced in RIGHTS.json."
title: "NanoLab Component Library (nanolab-components)"
version: "0.1.0"
date-released: 2026-09-18
license: Apache-2.0
authors:
  - name: "NanoLab project"
keywords:
  - DNA nanomechanics
  - component library
  - reproducibility
"""


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _variant_summary_path(variant: str) -> Path:
    return legacy.PARAM_EXEC[variant] / "evidence" / f"PARAM-{variant.upper()}-summary.json"


def _reference_replica_medians(card: dict[str, Any]) -> list[float]:
    observables = card["measured_observables"]
    if "hinge_angle_confirmatory_200k" in observables:
        dist = observables["hinge_angle_confirmatory_200k"]["distribution"]
    else:
        dist = observables["hinge_angle_common_window_150k"]["distribution"]
    values = dist["per_replica_median_deg"]
    if isinstance(values, dict):
        return [float(values[key]) for key in sorted(values)]
    return [float(v) for v in values]


def _reproduction_expected(card: dict[str, Any], observable_name: str) -> dict[str, Any]:
    target = card["measured_observables"][observable_name]["estimate"]
    return {
        "reference_observable_estimate_deg": target,
        **reproduction_rule.reference_rule_payload(_reference_replica_medians(card)),
    }


def _reproduction_steps(window_steps: int, bootstrap_resamples: int, bootstrap_seed: int) -> list[str]:
    return [
        "1. download-on-run; verify mandatory size + blob_sha1; interpret sha256 only together with sha256_status",
        "2. freeze three fresh seeds before execution; do not reuse reference seeds",
        "3. run the pinned CPU/double oxDNA model and apply the frozen E2 frame-validity/angle convention",
        f"4. analyze the frozen comparison window t <= {window_steps}; report per-replica medians and descriptive bootstrap ({bootstrap_resamples} resamples, seed {bootstrap_seed})",
        f"5. classify with {reproduction_rule.RULE_ID} using independent replica medians; pooled bootstrap CI is descriptive only, never a prediction/tolerance interval",
    ]


def _repair_0b(card: dict[str, Any], evidence: dict[str, Any]) -> None:
    env = evidence["environment"]
    boot = evidence["angle_distribution_confirmatory_200k"]["pooled"]["bootstrap"]
    seeds = evidence["simulation_confidence"]["seeds"]
    confirmatory_steps = int(env["steps_confirmatory"])

    card["protocol_pins"]["steps"] = confirmatory_steps
    card["protocol_pins"]["seeds"] = list(seeds)
    card["protocol_pins"]["temperature"] = env["temperature"]
    card["protocol_pins"]["platform"] = env["platform"]
    card["protocol_pins"]["options"] = {
        "print_conf_interval": env["print_conf_interval"],
        "print_energy_every": env["print_energy_every"],
        "salt_concentration": env["salt_concentration"],
    }
    card["operating_range"]["salt_concentration_M"] = env["salt_concentration"]
    card["operating_range"]["temperature"] = env["temperature"]

    observable = "hinge_angle_confirmatory_200k"
    card["reproduction"]["expected"] = _reproduction_expected(card, observable)
    card["reproduction"]["steps"] = _reproduction_steps(confirmatory_steps, int(boot["resamples"]), int(boot["seed"]))
    card["reproduction"]["tolerance_policy"] = (
        f"{reproduction_rule.RULE_ID}; independent unit=replica median; MATCH/MISMATCH/INCONCLUSIVE per docs/release/REPRODUCTION_RULE_V0_1.md; bootstrap CI is descriptive only"
    )


def _repair_parametric(card: dict[str, Any], variant: str, param: dict[str, Any], env: dict[str, Any]) -> None:
    summary = _read_json(_variant_summary_path(variant))
    reports = summary["run_reports"]
    ordered = [reports[key] for key in sorted(reports)]
    seeds = [int(row["seed"]) for row in ordered]
    requested = sorted({int(row["steps_requested"]) for row in ordered})
    if len(requested) != 1:
        raise ValueError(f"{variant}: inconsistent steps_requested {requested}")

    pooled = param["variants"][variant]["pooled_common_window"]["angle_stats_valid_frames"]
    boot = pooled["bootstrap"]
    window_steps = int(param["variants"][variant]["common_window_steps"])

    card["protocol_pins"]["steps"] = requested[0]
    card["protocol_pins"]["seeds"] = seeds
    card["protocol_pins"]["temperature"] = env["temperature"]
    card["protocol_pins"]["platform"] = env["platform"]
    card["protocol_pins"]["options"] = {
        "print_conf_interval": env["print_conf_interval"],
        "print_energy_every": env["print_energy_every"],
        "salt_concentration": env["salt_concentration"],
    }
    card["operating_range"]["salt_concentration_M"] = env["salt_concentration"]
    card["operating_range"]["temperature"] = env["temperature"]

    observable = "hinge_angle_common_window_150k"
    card["reproduction"]["expected"] = _reproduction_expected(card, observable)
    card["reproduction"]["steps"] = _reproduction_steps(window_steps, int(boot["resamples"]), int(boot["seed"]))
    card["reproduction"]["tolerance_policy"] = (
        f"{reproduction_rule.RULE_ID}; independent unit=replica median; MATCH/MISMATCH/INCONCLUSIVE per docs/release/REPRODUCTION_RULE_V0_1.md; bootstrap CI is descriptive only"
    )


def _finalize_release_metadata(root: Path) -> None:
    """Apply owner decision D2 without touching scientific/card content."""
    rights_path = root / "RIGHTS.json"
    rights = _read_json(rights_path)
    rights["package_version"] = FINAL_VERSION
    rights["own_code_license"] = FINAL_CODE_LICENSE
    rights["own_docs_data_license"] = FINAL_DOCS_DATA_LICENSE
    for item in rights["items"]:
        if item["path"] == "families/**":
            item["notes"] = (
                "карточки и family.json — собственные производные результаты NanoLab под CC-BY-4.0; "
                "reproduction-код NanoLab — Apache-2.0; upstream-файлы в пакет не включены и не перелицензируются"
            )
        elif item["path"] == "reports/**":
            item["notes"] = "собственные отчёты и evidence-снапшоты NanoLab публикуются под CC-BY-4.0"
    _write_json(rights_path, rights)

    (root / "VERSION").write_text(FINAL_VERSION + "\n", encoding="utf-8")
    (root / "CITATION.cff").write_text(FINAL_CITATION_CFF, encoding="utf-8")


def _postprocess(root: Path) -> None:
    evidence_0b = _read_json(CARD_0B_EVIDENCE)
    param = _read_json(PARAM_SUMMARY)
    env = evidence_0b["environment"]
    cards_dir = root / "families" / "dna_hinge" / "cards"

    for variant in legacy.VARIANTS:
        path = cards_dir / f"{variant}.card.json"
        card = _read_json(path)
        if variant == "0b":
            _repair_0b(card, evidence_0b)
        elif variant in ("11b", "32b", "53b"):
            _repair_parametric(card, variant, param, env)
        # 74b remains NOT_MEASURED; no reproduction threshold is invented.
        card["provenance"]["generation"] = (
            "assembled by release.build_library_r12.py (WO-NL5-001-B-REPAIR-R1); scientific/protocol machine fields are evidence-derived; full package deterministic check includes manifest"
        )
        _write_json(path, card)

    rule_target = root / "reproduction" / "REPRODUCTION_RULE_V0_1.md"
    rule_target.write_bytes(RULE_DOC.read_bytes())

    _finalize_release_metadata(root)\n\n    manifest = card_lint.manifest_create(root, generated_by="release.build_library_r12 deterministic-r1.2")
    _write_json(root / card_lint.MANIFEST_NAME, manifest)


def build(root: Path = PKG_ROOT) -> list[Path]:
    legacy.build(root)
    _postprocess(root)
    return sorted(p for p in root.rglob("*") if p.is_file())


def _snapshot(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def check() -> list[str]:
    """Prove two independent full builds are byte-identical, including manifest."""
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "a"
        b = Path(tmp) / "b"
        build(a)
        build(b)
        sa, sb = _snapshot(a), _snapshot(b)
        problems: list[str] = []
        for rel in sorted(set(sa) | set(sb)):
            if rel not in sa:
                problems.append(f"missing in build A: {rel}")
            elif rel not in sb:
                problems.append(f"missing in build B: {rel}")
            elif sa[rel] != sb[rel]:
                problems.append(f"byte mismatch between independent builds: {rel}")
        if "RELEASE_MANIFEST.json" not in sa:
            problems.append("RELEASE_MANIFEST.json missing from deterministic build")
        return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="release.build_library_r12")
    parser.add_argument("mode", choices=["build", "check"])
    args = parser.parse_args(argv)
    if args.mode == "build":
        files = build()
        print(json.dumps({"schema": "nanolab.release_build_output.v1", "mode": "build", "ok": True, "files": len(files)}, ensure_ascii=False, indent=2))
        return 0
    problems = check()
    print(json.dumps({"schema": "nanolab.release_build_output.v1", "mode": "check", "ok": not problems, "problems": problems}, ensure_ascii=False, indent=2))
    return 0 if not problems else 3


if __name__ == "__main__":
    raise SystemExit(main())
