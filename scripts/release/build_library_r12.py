"""R1.2 deterministic repair builder for nanolab-components-v0.1.

The historical R1 builder remains durable evidence. This module calls it only
for non-authoritative assembly/template work, then rewrites every emitted
machine-readable scientific/protocol comparison field from published evidence
and creates a deterministic full-package manifest.

Normative command after B-Repair R1:
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


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _variant_summary_path(variant: str) -> Path:
    return legacy.PARAM_EXEC[variant] / "evidence" / f"PARAM-{variant.upper()}-summary.json"


def _common_environment() -> dict[str, Any]:
    return _read_json(CARD_0B_EVIDENCE)["environment"]


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
    payload = reproduction_rule.reference_rule_payload(_reference_replica_medians(card))
    return {"reference_observable_estimate_deg": target, **payload}


def _reproduction_steps(window_steps: int, bootstrap_resamples: int, bootstrap_seed: int) -> list[str]:
    return [
        "1. download-on-run; verify mandatory size + blob_sha1; interpret sha256 only together with sha256_status",
        "2. freeze three fresh seeds before execution; do not reuse reference seeds",
        "3. run the pinned CPU/double oxDNA model and apply the frozen E2 frame-validity/angle convention",
        f"4. analyze the frozen comparison window t <= {window_steps}; report per-replica medians and descriptive bootstrap ({bootstrap_resamples} resamples, seed {bootstrap_seed})",
        f"5. classify with {reproduction_rule.RULE_ID} using independent replica medians; pooled bootstrap CI is descriptive only, never a prediction/tolerance interval",
    ]


def _repair_0b(card: dict[str, Any], evidence: dict[str, Any], param: dict[str, Any]) -> None:
    env = evidence["environment"]
    conf = evidence["angle_distribution_confirmatory_200k"]["pooled"]["bootstrap"]
    seeds = evidence["simulation_confidence"]["seeds"]
    window_steps = int(param["variants"]["0b"]["common_window_steps"])

    card["protocol_pins"]["steps"] = int(env["steps_confirmatory"])
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
    card["reproduction"]["steps"] = _reproduction_steps(window_steps, int(conf["resamples"]), int(conf["seed"]))
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


def _postprocess(root: Path) -> None:
    evidence_0b = _read_json(CARD_0B_EVIDENCE)
    param = _read_json(PARAM_SUMMARY)
    env = evidence_0b["environment"]

    cards_dir = root / "families" / "dna_hinge" / "cards"
    for variant in legacy.VARIANTS:
        path = cards_dir / f"{variant}.card.json"
        card = _read_json(path)
        if variant == "0b":
            _repair_0b(card, evidence_0b, param)
        elif variant in ("11b", "32b", "53b"):
            _repair_parametric(card, variant, param, env)
        # 74b remains NOT_MEASURED; no reproduction threshold is invented.
        card["provenance"]["generation"] = (
            "assembled by release.build_library_r12.py (WO-NL5-001-B-REPAIR-R1); scientific/protocol machine fields are evidence-derived; full package deterministic check includes manifest"
        )
        _write_json(path, card)

    rule_target = root / "reproduction" / "REPRODUCTION_RULE_V0_1.md"
    rule_target.write_bytes(RULE_DOC.read_bytes())

    protocol_readme = root / "protocols" / "README.md"
    text = protocol_readme.read_text(encoding="utf-8")
    marker = "\nIndependent reproduction classification: `reproduction/REPRODUCTION_RULE_V0_1.md`"
    if marker.strip() not in text:
        protocol_readme.write_text(text.rstrip() + marker + "\n", encoding="utf-8")

    manifest = card_lint.manifest_create(root, generated_by="release.build_library_r12 deterministic-r1.2")
    _write_json(root / card_lint.MANIFEST_NAME, manifest)


def build(root: Path = PKG_ROOT) -> list[Path]:
    written = legacy.build(root)
    _postprocess(root)
    return sorted(p for p in root.rglob("*") if p.is_file())


def check(root: Path = PKG_ROOT) -> list[str]:
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        built_root = Path(tmp) / "pkg"
        build(built_root)
        built = {p.relative_to(built_root).as_posix(): p for p in built_root.rglob("*") if p.is_file()}
        committed = {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}
        for rel in sorted(set(built) | set(committed)):
            if rel not in committed:
                problems.append(f"built file not committed: {rel}")
            elif rel not in built:
                problems.append(f"committed file not produced: {rel}")
            elif built[rel].read_bytes() != committed[rel].read_bytes():
                problems.append(f"byte mismatch: {rel}")
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
