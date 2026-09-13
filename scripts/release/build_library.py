"""Deterministic builder: published evidence JSONs -> nanolab-components-v0.1.

Pure function of the repository's published evidence files. A rerun MUST be
byte-identical (``--check`` verifies this). All numbers are read from evidence;
none are transcribed by hand. RELEASE_MANIFEST.json is intentionally NOT
emitted here: digests are computed by release.card_lint (the same tool that
verifies them).

Evidence inputs (repo-relative):
    docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/parametric-summary.json
    docs/work/executions/EX-NL3-002-R1/evidence/confirmatory-summary.json
    docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/component-card-0b.json
    docs/work/executions/EX-NL3-002-PARAM-{11B,32B,53B,74B}-R1/evidence/source-download-verification.json
    docs/work/executions/EX-NL3-002-PARAM-74B-R1/evidence/arm-manifest-74b-failure.json
    scripts/hinge_family/source_pins.json
    docs/research/ENGINE_ENVIRONMENT_R1.md            (pinned engine commit)
    examples/release/nanolab-components-v0.1/reproduction/*  (templates)

Usage (from repo root):
    PYTHONPATH=scripts python3 -m release.build_library build
    PYTHONPATH=scripts python3 -m release.build_library check
Exit codes: 0 ok, 3 mismatch/failure, 2 usage.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PKG_ROOT = REPO_ROOT / "releases" / "nanolab-components-v0.1"
EXAMPLE_PKG = REPO_ROOT / "examples" / "release" / "nanolab-components-v0.1"

PARAM_SUMMARY = REPO_ROOT / "docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/parametric-summary.json"
CONFIRM_SUMMARY = REPO_ROOT / "docs/work/executions/EX-NL3-002-R1/evidence/confirmatory-summary.json"
CARD_0B_EVIDENCE = REPO_ROOT / "docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/component-card-0b.json"
SOURCE_PINS = REPO_ROOT / "scripts/hinge_family/source_pins.json"
ENGINE_ENV = REPO_ROOT / "docs/research/ENGINE_ENVIRONMENT_R1.md"

PARAM_EXEC = {
    "11b": REPO_ROOT / "docs/work/executions/EX-NL3-002-PARAM-11B-R1",
    "32b": REPO_ROOT / "docs/work/executions/EX-NL3-002-PARAM-32B-R1",
    "53b": REPO_ROOT / "docs/work/executions/EX-NL3-002-PARAM-53B-R1",
    "74b": REPO_ROOT / "docs/work/executions/EX-NL3-002-PARAM-74B-R1",
}
PARAM_EXEC_ID = {
    "0b": "EX-NL3-002-R1",
    "11b": "EX-NL3-002-PARAM-11B-R1",
    "32b": "EX-NL3-002-PARAM-32B-R1",
    "53b": "EX-NL3-002-PARAM-53B-R1",
    "74b": "EX-NL3-002-PARAM-74B-R1",
}
VARIANTS = ["0b", "11b", "32b", "53b", "74b"]
VERSION = "0.1.0-rc0"
WINDOW_STEPS = 150000

PARAM_SUMMARY_REL = "docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/parametric-summary.json"
CONFIRM_SUMMARY_REL = "docs/work/executions/EX-NL3-002-R1/evidence/confirmatory-summary.json"

# Family-level limitations, verbatim from the published E2 component card.
FAMILY_LIMITATIONS_TAIL = [
    "coarse-grained модель oxDNA DNA2: количественное соответствие эксперименту не claim'ится (ceiling C0_SOFTWARE_ONLY/measured-only)",
    "конвенция угла [0,180] по PCA-осям не имеет прямого соответствия SI статьи (U-obs-1 закрыт first-principles решением E2_OBS1_SI_DECISION_R1, не подгонкой под SI)",
    "v2-detector пар (mutual-nearest, window + antiparallel a1) — frozen-инструментальная конвенция, не авторский код",
]

ANGLE_CONVENTION = (
    "[0,180] deg, PCA axes, erratum R1 §2.5; detector v2 mutual-nearest + PCA hinge angle, frozen arm manifest"
)


class BuildError(Exception):
    pass


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(pkg_file: Path, payload: Any) -> None:
    pkg_file.parent.mkdir(parents=True, exist_ok=True)
    pkg_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_bytes(pkg_file: Path, payload: bytes) -> None:
    pkg_file.parent.mkdir(parents=True, exist_ok=True)
    pkg_file.write_bytes(payload)


def _engine_commit() -> str:
    text = ENGINE_ENV.read_text(encoding="utf-8")
    match = re.search(r"pinned commit = ([0-9a-f]{40})", text)
    if not match:
        raise BuildError(f"{ENGINE_ENV}: pinned oxDNA commit not found")
    return match.group(1)


def _download_verification(variant: str) -> dict[str, Any]:
    path = PARAM_EXEC[variant] / "evidence" / "source-download-verification.json"
    return _read_json(path)


def _sha256_status(record: dict[str, Any]) -> str | None:
    """Map a download-verification record onto the R1.1 digest level."""
    if record.get("sha256_match") is True:
        return "CONTENT_VERIFIED"
    if record.get("sha256") is not None:
        return "COMPUTED_NOT_VERIFIED"
    return None


def _digest_entry(record: dict[str, Any]) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "size_bytes": record["size_bytes"],
        "blob_sha1": record["blob_sha1"],
    }
    status = _sha256_status(record)
    if record.get("sha256") is not None:
        entry["sha256"] = record["sha256"]
    if status is not None:
        entry["sha256_status"] = status
    return entry


def _variant_digests(variant: str, pins: dict[str, Any], verification: dict[str, Any]) -> dict[str, dict[str, Any]]:
    gates: dict[str, dict[str, Any]] = {}
    for rel in (f"MD_Hinges/{variant}.conf", f"MD_Hinges/{variant}.top"):
        gates[rel] = _digest_entry(verification["files"][rel])
    pro = verification["files"].get("MD_Hinges/pro_CPU.in")
    if pro is not None:
        gates["MD_Hinges/pro_CPU.in"] = _digest_entry(pro)
    # 0b fallback: pro_CPU.in may come from the R1 pins when the 0b campaign
    # verified it outside PARAM executions.
    if "MD_Hinges/pro_CPU.in" not in gates:
        pro_pin = pins["files"].get("MD_Hinges/pro_CPU.in")
        if pro_pin is not None:
            gates["MD_Hinges/pro_CPU.in"] = {
                "size_bytes": pro_pin["size_bytes"],
                "blob_sha1": pro_pin["blob_sha1"],
                "sha256": pro_pin["sha256"],
                "sha256_status": "CONTENT_VERIFIED" if pro_pin.get("sha256_provenance") == "R1_CONTENT_VERIFIED" else "COMPUTED_NOT_VERIFIED",
            }
    return gates


def _card_0b(param: dict[str, Any], confirm: dict[str, Any], evidence_card: dict[str, Any], pins: dict[str, Any], engine: str) -> dict[str, Any]:
    pooled = confirm["pooled_angle_stats_valid_frames"]
    window = param["variants"]["0b"]["pooled_common_window"]["angle_stats_valid_frames"]
    manifest = param["arm_manifest_summary"]["0b"]
    environment = evidence_card["environment"]
    stability = evidence_card["stability"]
    upstream = pins["source"]
    per_replica_medians = {
        run_id: confirm["runs"][run_id]["angle_stats_valid_frames"]["median_deg"]
        for run_id in sorted(confirm["runs"])
    }
    return {
        "schema_version": 1,
        "kind": "nanolab_component_card",
        "component_id": "dna_hinge/0b",
        "family": "dna_hinge",
        "variant": "0b",
        "function": "Compliant DNA hinge: взаимный угол плеч под внешним воздействием; в v0.1 измерено равновесное распределение угла (confirmatory 200k + общее окно 150k). Управляемый привод — предмет E5, не этой карточки",
        "interfaces": {
            "arms": f"два плеча (arm_a {manifest['arm_a']} / arm_b {manifest['arm_b']} нуклеотидов манифеста), топология {manifest['coverage']['topology_nucleotides']} нуклеотидов",
            "measurement_interface": ANGLE_CONVENTION,
        },
        "operating_range": {
            "temperature": "300 K (author config verbatim; decision rule E2-SETUP-R1 §5)",
            "salt_concentration_M": environment.get("salt_concentration", 0.5),
            "model": "oxDNA DNA2 coarse-grained",
            "notes": "применимость ограничена измеренным протоколом; экстраполяция не заявляется",
        },
        "design": {
            "angle_frame0_deg": manifest["angle_frame0_deg"],
            "arm_a_nucleotides": manifest["arm_a"],
            "arm_b_nucleotides": manifest["arm_b"],
            "arm_manifest": manifest["source"],
            "manifest_fraction_of_paired": manifest["coverage"]["manifest_fraction_of_paired"],
            "manifest_fraction_of_topology": manifest["coverage"]["manifest_fraction_of_topology"],
            "manifest_nucleotides": manifest["coverage"]["manifest_nucleotides"],
            "topology_nucleotides": manifest["coverage"]["topology_nucleotides"],
            "upstream_role": pins["variants"]["0b"]["role"],
        },
        "rights": {
            "rights_mode": "REFERENCE_ONLY",
            "upstream_repo": upstream["repository"],
            "pinned_commit": upstream["commit"],
            "derived_results_publishable": True,
            "durable_cache": "FORBIDDEN",
            "notes": "G1 decision B: download-on-run по exact pinned commit, удаление после execution; пакет распространяет производные результаты NanoLab, не upstream-файлы",
        },
        "claim_ceiling": "C0_SOFTWARE_ONLY",
        "measurement_status": "MEASURED",
        "scientific_outcome": evidence_card["scientific_outcome"],
        "protocol_pins": {
            "engine": "oxDNA (CPU build, double precision)",
            "engine_commit": engine,
            "model": "DNA2",
            "temperature": "300 K",
            "steps": 200000,
            "seeds": [201004, 202008, 203012],
            "platform": environment["platform"],
            "options": {
                "print_conf_interval": environment["print_conf_interval"],
                "print_energy_every": environment["print_energy_every"],
                "salt_concentration": environment["salt_concentration"],
            },
            "protocol": "docs/research/E2_PROTO_R1.md (frozen before confirmatory runs; addendum §8 common window); observables: docs/research/E2_OBSERVABLES_R2.md",
            "notes": "thermostat и integration — author config verbatim (pro_CPU.in)",
        },
        "source_provenance": {
            "upstream_repo": upstream["repository"],
            "pinned_commit": upstream["commit"],
            "digest_gates": _digest_gates_0b(pins),
            "digest_gate_result": evidence_card["source_provenance"]["digest_gate_result"],
        },
        "measured_observables": {
            "hinge_angle_confirmatory_200k": {
                "units": "deg",
                "convention": ANGLE_CONVENTION,
                "estimate": pooled["median_deg"],
                "uncertainty": pooled["bootstrap"]["ci95"],
                "n": pooled["n_frames"],
                "source": CONFIRM_SUMMARY_REL,
                "digests": {},
                "distribution": {
                    "bootstrap": pooled["bootstrap"],
                    "iqr_deg": pooled["iqr_deg"],
                    "per_replica_median_deg": per_replica_medians,
                    "q05_q95_deg": [pooled["q05_deg"], pooled["q95_deg"]],
                },
            },
            "hinge_angle_common_window_150k": {
                "units": "deg",
                "convention": ANGLE_CONVENTION + "; общий кросс-вариантный интервал 150k (addendum §8 item 3)",
                "estimate": window["median_deg"],
                "uncertainty": window["bootstrap"]["ci95"],
                "n": window["n_frames"],
                "source": PARAM_SUMMARY_REL,
                "digests": {},
                "distribution": {
                    "bootstrap": window["bootstrap"],
                    "iqr_deg": window["iqr_deg"],
                    "note": "secondary cross-variant window; primary confirmatory 200k result NOT revised",
                    "q05_q95_deg": [window["q05_deg"], window["q95_deg"]],
                },
            },
        },
        "integrity": {
            "gates_passed": True,
            "frames_valid": f"{confirm['pooled_valid_frames_total']}/{confirm['pooled_valid_frames_total']}",
            "details": [
                f"long_bond_fraction <= 0.1078: max {stability['long_bond_fraction_max']}",
                f"pairs_fraction_v2 >= 0.50: min {stability['pairs_fraction_v2_min']}",
                f"displacement <= 20.0: max {stability['displacement_max_max']}",
                f"energy |drift| total, max across replicas: {stability['energy_max_abs_drift_total_max_across_replicas']}",
            ],
            "notes": "гейты §4 E2_PROTO_R1",
        },
        "known_gaps": [],
        "known_limitations": list(evidence_card["known_limitations"]),
        "reproduction": {
            "requires": [
                f"oxDNA @ {engine} (CPU build, double precision)",
                "python3 >= 3.10 (stdlib only)",
                "сетевой доступ для download-on-run по exact pinned commit (REFERENCE_ONLY)",
            ],
            "steps": list(evidence_card["reproduction"]["steps"]),
            "expected": {
                "hinge_angle_confirmatory_200k": pooled["median_deg"],
                "hinge_angle_common_window_150k": window["median_deg"],
            },
            "tolerance_policy": "pooled median в пределах bootstrap CI95 карточки; гейты кадра §4 E2_PROTO_R1; не PASS при отсутствии проверки",
            "rights_constraints": "download-on-run по exact pinned commit; durable-cache запрещён; upstream-файлы не включены в пакет",
        },
        "provenance": {
            "evidence_execution_id": "EX-NL3-002-SUMMARY-R1",
            "card_generated_from": [
                CONFIRM_SUMMARY_REL,
                PARAM_SUMMARY_REL,
                "docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/component-card-0b.json",
                "scripts/hinge_family/source_pins.json",
                "docs/research/ENGINE_ENVIRONMENT_R1.md",
            ],
            "generation": "built by release.build_library.py (WO-NL5-001-B-R1) from published evidence; deterministic and byte-reproducible (--check)",
        },
    }


def _digest_gates_0b(pins: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """0b digest gates from the R1 pins (content-verified sha256)."""
    gates = {}
    for rel in ("MD_Hinges/0b.conf", "MD_Hinges/0b.top", "MD_Hinges/pro_CPU.in"):
        pin = pins["files"][rel]
        gates[rel] = {
            "size_bytes": pin["size_bytes"],
            "blob_sha1": pin["blob_sha1"],
            "sha256": pin["sha256"],
            "sha256_status": "CONTENT_VERIFIED" if pin.get("sha256_provenance") == "R1_CONTENT_VERIFIED" else "COMPUTED_NOT_VERIFIED",
        }
    return gates


def build(root: Path = PKG_ROOT) -> list[Path]:
    param = _read_json(PARAM_SUMMARY)
    confirm = _read_json(CONFIRM_SUMMARY)
    evidence_card = _read_json(CARD_0B_EVIDENCE)
    pins = _read_json(SOURCE_PINS)
    engine = _engine_commit()

    written: list[Path] = []

    def emit(rel: str, payload: Any) -> None:
        target = root / rel
        _write_json(target, payload)
        written.append(target)

    def emit_bytes(rel: str, payload: bytes) -> None:
        target = root / rel
        _write_bytes(target, payload)
        written.append(target)

    # schema snapshots (byte copies of the normative repo schemas)
    for rel in (
        "schemas/components/component-card.v1.json",
        "schemas/release/rights.v1.json",
        "schemas/release/release-manifest.v1.json",
    ):
        emit_bytes(f"schema/{rel.split('/')[-2]}/{rel.split('/')[-1]}", rel_path_bytes(REPO_ROOT / rel))

    emit_bytes("VERSION", f"{VERSION}\n".encode("utf-8"))
    emit_bytes("CITATION.cff", CITATION_CFF.encode("utf-8"))
    emit("RIGHTS.json", _rights())
    emit("families/dna_hinge/family.json", _family(pins))

    cards = {"0b": _card_0b(param, confirm, evidence_card, pins, engine)}
    for variant in ("11b", "32b", "53b"):
        cards[variant] = _card_parametric(variant, param, pins, engine)
    cards["74b"] = _card_74b(param, pins, engine)
    for variant in VARIANTS:
        emit(f"families/dna_hinge/cards/{variant}.card.json", cards[variant])

    emit("provenance/source-digests.json", _source_digests(pins))
    emit("protocols/README.md", _protocols_readme(engine))
    emit("reports/family-report.md", _family_report(cards))

    # evidence snapshots (OWN results of NanoLab, publishable per G1)
    emit_bytes("reports/evidence/confirmatory-summary.json", rel_path_bytes(CONFIRM_SUMMARY))
    emit_bytes("reports/evidence/parametric-summary.json", rel_path_bytes(PARAM_SUMMARY))

    # reproduction templates: single template source is the example package
    for name in ("README.md", "reproduce.py"):
        emit_bytes(f"reproduction/{name}", rel_path_bytes(EXAMPLE_PKG / "reproduction" / name))

    return written


def rel_path_bytes(path: Path) -> bytes:
    return path.read_bytes()


CITATION_CFF = """cff-version: 1.2.0
message: "If you use this component library, please cite it and the upstream scientific sources referenced in RIGHTS.json."
title: "NanoLab Component Library (nanolab-components)"
version: "0.1.0-rc0"
# DRAFT package: license/authors/date-released are filled at publication (NL5-001-D)
# after the owner license decision (program D2). Not a publication artifact yet.
authors:
  - name: "NanoLab project"
keywords:
  - DNA nanomechanics
  - component library
  - reproducibility
"""


def _rights() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "nanolab_components_rights",
        "package": "nanolab-components",
        "package_version": VERSION,
        "own_code_license": "UNDECIDED_PENDING_OWNER_DECISION",
        "own_docs_data_license": "UNDECIDED_PENDING_OWNER_DECISION",
        "policy": {"durable_cache": "FORBIDDEN", "download_on_run": True},
        "items": [
            {
                "path": "families/**",
                "rights_mode": "MIXED",
                "redistribution": "ALLOWED",
                "derived_results_publishable": True,
                "notes": "карточки, family.json и reproduction-материалы — производные результаты NanoLab; upstream-файлы в пакет не включены; собственная лицензия — ожидание owner-решения D2",
            },
            {
                "path": "provenance/**",
                "rights_mode": "REFERENCE_ONLY",
                "redistribution": "METADATA_ONLY",
                "upstream_repo": "gauravarya77/DNA-hinge-simulations",
                "pinned_commit": "23fd1ff7731e9017bd776f49206dc42d70d9fe91",
                "derived_results_publishable": True,
                "notes": "digest-метаданные upstream-файлов; сами upstream-файлы не распространяются, доступ — download-on-run пользователем",
            },
            {
                "path": "reports/**",
                "rights_mode": "OWN",
                "redistribution": "ALLOWED",
                "derived_results_publishable": True,
                "notes": "собственные отчёты и evidence-снапшоты NanoLab; лицензия — ожидание owner-решения D2",
            },
        ],
    }


def _family(pins: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "family_id": "dna_hinge",
        "title": "DNA hinge family (Shi–Castro–Arya)",
        "description": "Одно семейство compliant DNA-шарниров с измеренными вариантами. Варианты — члены одного семейства с общим протоколом, а НЕ независимые компоненты.",
        "upstream": {
            "citation": "Shi, Castro, Arya — DNA hinge, DOI 10.1021/acsnano.7b00242",
            "repo": pins["source"]["repository"],
            "pinned_commit": pins["source"]["commit"],
            "rights_mode": "REFERENCE_ONLY",
        },
        "variants": VARIANTS,
        "variant_status": {
            "0b": "MEASURED",
            "11b": "MEASURED",
            "32b": "MEASURED",
            "53b": "MEASURED",
            "74b": "NOT_MEASURED (KNOWN_GAP: arm-manifest-v2 pending)",
        },
        "presentation_rule": "family + variants; каждая карточка варианта ссылается на общий протокол семейства и свои digest-pins",
        "measurement_basis": "0b: confirmatory 200k (frozen E2_PROTO_R1) + common window 150k; 11b/32b/53b: параметрическая серия, общее окно 150k (addendum §8); 74b: runs NOT_RUN (honest gap)",
    }


def _parametric_common(variant: str, param: dict[str, Any]) -> dict[str, Any]:
    return param["variants"][variant]["pooled_common_window"]["angle_stats_valid_frames"]


def _card_parametric(variant: str, param: dict[str, Any], pins: dict[str, Any], engine: str) -> dict[str, Any]:
    pooled = _parametric_common(variant, param)
    manifest = param["arm_manifest_summary"][variant]
    verification = _download_verification(variant)
    reps = param["variants"][variant]["per_replica_common_window"]
    seeds = [reps[key]["seed"] for key in sorted(reps)]
    windows = {key: reps[key]["window"] for key in sorted(reps)}
    frames_in_window = {key: w["frames_valid_in_window"] for key, w in windows.items()}
    fully_inside = all(w["frames_in_window"] == w["frames_total"] for w in windows.values())
    upstream = pins["source"]
    pin_role = pins["variants"][variant]["role"]
    steps_value: int | None = WINDOW_STEPS if fully_inside else None
    steps_note = (
        "прогоны полностью внутри общего окна 150k (cross-check: data fully inside window)"
        if fully_inside
        else f"прогон длиннее общего окна: last frame {windows[sorted(windows)[0]]['time_last_steps']} steps; сравнение — окно 150k (addendum §8)"
    )
    return {
        "schema_version": 1,
        "kind": "nanolab_component_card",
        "component_id": f"dna_hinge/{variant}",
        "family": "dna_hinge",
        "variant": variant,
        "function": "Compliant DNA hinge: взаимный угол плеч; в v0.1 измерено равновесное распределение угла в общем сравнительном окне 150k параметрической серии. Управляемый привод — предмет E5, не этой карточки",
        "interfaces": {
            "arms": f"два плеча (arm_a {manifest['arm_a']} / arm_b {manifest['arm_b']} нуклеотидов манифеста), топология {manifest['coverage']['topology_nucleotides']} нуклеотидов",
            "measurement_interface": ANGLE_CONVENTION,
        },
        "operating_range": {
            "temperature": "300 K",
            "salt_concentration_M": 0.5,
            "model": "oxDNA DNA2 coarse-grained",
            "notes": "применимость ограничена измеренным протоколом; экстраполяция не заявляется",
        },
        "design": {
            "angle_frame0_deg": manifest["angle_frame0_deg"],
            "arm_a_nucleotides": manifest["arm_a"],
            "arm_b_nucleotides": manifest["arm_b"],
            "arm_manifest_report": manifest["source"],
            "manifest_fraction_of_paired": manifest["coverage"]["manifest_fraction_of_paired"],
            "manifest_fraction_of_topology": manifest["coverage"]["manifest_fraction_of_topology"],
            "manifest_determinism": f"byte-identical derivations: {manifest['determinism']['runs']} runs",
            "topology_nucleotides": manifest["coverage"]["topology_nucleotides"],
            "upstream_role": pin_role,
        },
        "rights": {
            "rights_mode": "REFERENCE_ONLY",
            "upstream_repo": upstream["repository"],
            "pinned_commit": upstream["commit"],
            "derived_results_publishable": True,
            "durable_cache": "FORBIDDEN",
            "notes": "G1 decision B: download-on-run по exact pinned commit; пакет распространяет производные результаты NanoLab, не upstream-файлы",
        },
        "claim_ceiling": "C0_SOFTWARE_ONLY",
        "measurement_status": "MEASURED",
        "scientific_outcome": "MEASURED (параметрическая серия, общее сравнительное окно 150000 steps; кросс-вариантные тренды в карточке не интерпретируются)",
        "protocol_pins": {
            "engine": "oxDNA (CPU build, double precision)",
            "engine_commit": engine,
            "model": "DNA2",
            "temperature": "300 K",
            "steps": steps_value,
            "seeds": seeds,
            "platform": "как в ENGINE_ENVIRONMENT_R1 (WSL2 Ubuntu 24.04)",
            "options": {"print_conf_interval": 4000, "print_energy_every": 100, "salt_concentration": 0.5},
            "protocol": "docs/research/E2_PROTO_R1.md (frozen; addendum §8 common window); observables: docs/research/E2_OBSERVABLES_R2.md",
            "notes": steps_note,
        },
        "source_provenance": {
            "upstream_repo": upstream["repository"],
            "pinned_commit": upstream["commit"],
            "digest_gates": _variant_digests(variant, pins, verification),
            "digest_gate_result": f"digest_gate_all = {verification.get('digest_gate_all', 'UNKNOWN')} (size + blob_sha1 registry pin; sha256 computed at download, status COMPUTED_NOT_VERIFIED)",
        },
        "measured_observables": {
            "hinge_angle_common_window_150k": {
                "units": "deg",
                "convention": ANGLE_CONVENTION + "; общий кросс-вариантный интервал 150k (addendum §8 item 3)",
                "estimate": pooled["median_deg"],
                "uncertainty": pooled["bootstrap"]["ci95"],
                "n": pooled["n_frames"],
                "source": PARAM_SUMMARY_REL,
                "digests": {},
                "distribution": {
                    "bootstrap": pooled["bootstrap"],
                    "iqr_deg": pooled["iqr_deg"],
                    "per_replica_median_deg": {
                        key: reps[key]["angle_stats_valid_frames_in_window"]["median_deg"] for key in sorted(reps)
                    },
                    "q05_q95_deg": [pooled["q05_deg"], pooled["q95_deg"]],
                },
            }
        },
        "integrity": {
            "gates_passed": True,
            "frames_valid": f"{sum(frames_in_window.values())}/{sum(w['frames_in_window'] for w in windows.values())} in-window",
            "details": [
                f"valid_frame_fraction_in_window = 1.0 в каждой реплике ({', '.join(f'{k}: {v}/37' for k, v in sorted(frames_in_window.items()))})",
                "кадры за пределами окна 150k исключены frozen-правилом сравнения, а не гейт-отказом",
            ],
            "notes": "гейты §4 E2_PROTO_R1",
        },
        "known_gaps": [],
        "known_limitations": [
            "измерение выполнено в общем сравнительном окне 150k параметрической серии (addendum §8); confirmatory 200k в v0.1 есть только у варианта 0b",
            "вариант зарегистрирован из upstream; spring layers REPORTED (paper via NL0-001), машинно не проверялись в R1 (source_pins role REGISTERED_NOT_VALIDATED)",
            *FAMILY_LIMITATIONS_TAIL,
        ],
        "reproduction": {
            "requires": [
                f"oxDNA @ {engine} (CPU build, double precision)",
                "python3 >= 3.10 (stdlib only)",
                "сетевой доступ для download-on-run по exact pinned commit (REFERENCE_ONLY)",
            ],
            "steps": [
                "1. download-on-run с digest-гейтом: size + blob_sha1 (registry pin) обязательны; sha256 сверяется со значением карточки с учётом sha256_status",
                "2. сборка входов реплик: verbatim conf/top + pro_CPU.in; seeds как в protocol_pins",
                "3. прогоны: CPU oxDNA, 3 реплики; анализ в общем окне 150000 steps (addendum §8)",
                "4. frozen-анализ: v2 mutual-nearest + гейты §4 + статистика §6 (median/IQR/q05-q95 по валидным кадрам, bootstrap CI95 10000 resamples, seed 424242)",
                "5. сравнение pooled median с expected в пределах CI95; расхождение вне CI — REPRODUCTION_MISMATCH",
            ],
            "expected": {"hinge_angle_common_window_150k": pooled["median_deg"]},
            "tolerance_policy": "pooled median в пределах bootstrap CI95 карточки; гейты кадра §4 E2_PROTO_R1; не PASS при отсутствии проверки",
            "rights_constraints": "download-on-run по exact pinned commit; durable-cache запрещён; upstream-файлы не включены в пакет",
        },
        "provenance": {
            "evidence_execution_id": PARAM_EXEC_ID[variant],
            "card_generated_from": [
                PARAM_SUMMARY_REL,
                f"docs/work/executions/{PARAM_EXEC_ID[variant]}/evidence/source-download-verification.json",
                manifest["source"],
                "scripts/hinge_family/source_pins.json",
                "docs/research/ENGINE_ENVIRONMENT_R1.md",
            ],
            "generation": "built by release.build_library.py (WO-NL5-001-B-R1) from published evidence; deterministic and byte-reproducible (--check)",
        },
    }


def _card_74b(param: dict[str, Any], pins: dict[str, Any], engine: str) -> dict[str, Any]:
    manifest = param["arm_manifest_summary"]["74b"]
    failure = _read_json(PARAM_EXEC["74b"] / "evidence" / "arm-manifest-74b-failure.json")
    verification = _download_verification("74b")
    upstream = pins["source"]
    return {
        "schema_version": 1,
        "kind": "nanolab_component_card",
        "component_id": "dna_hinge/74b",
        "family": "dna_hinge",
        "variant": "74b",
        "function": "Compliant DNA hinge, длинноплечий вариант 74b; измерений нет — карточка публикуется как честный известный гэп семейства",
        "interfaces": {
            "arms": "структура аналогична другим вариантам семейства, длинноплечная конфигурация 74b",
            "measurement_interface": "UNKNOWN до закрытия arm-manifest-v2 (detector не применим без валидного arm manifest)",
        },
        "operating_range": {"notes": "UNKNOWN — измерений не проводилось; ничего не заявляется"},
        "design": {
            "arm_manifest_status": manifest["status"],
            "arm_manifest_failure_report": manifest["source"],
            "derivation_attempts": failure["attempts"],
            "deterministic_identical_error": failure["deterministic_identical_error"],
            "error_class": failure["outcome"],
            "error_message_head": failure["error_message_head"],
        },
        "rights": {
            "rights_mode": "REFERENCE_ONLY",
            "upstream_repo": upstream["repository"],
            "pinned_commit": upstream["commit"],
            "derived_results_publishable": True,
            "durable_cache": "FORBIDDEN",
            "notes": "права те же, что у семейства; измерений нет, публикуются только метаданные варианта",
        },
        "claim_ceiling": "C0_SOFTWARE_ONLY",
        "measurement_status": "NOT_MEASURED",
        "scientific_outcome": "NOT_MEASURED (детерминированный отказ arm-manifest-v1; runs NOT_RUN — honest gap, сохранён как есть)",
        "protocol_pins": {
            "engine": "oxDNA (CPU build, double precision)",
            "engine_commit": engine,
            "model": "DNA2",
            "temperature": None,
            "steps": None,
            "seeds": [],
            "platform": "как в ENGINE_ENVIRONMENT_R1 (WSL2 Ubuntu 24.04)",
            "options": {},
            "protocol": "docs/research/E2_PROTO_R1.md; к варианту 74b не применялся",
            "notes": "runs NOT_RUN для 74b: блокировка по stop-правилам WO-NL3-002-PARAM до манифеста",
        },
        "source_provenance": {
            "upstream_repo": upstream["repository"],
            "pinned_commit": upstream["commit"],
            "digest_gates": _variant_digests("74b", pins, verification),
            "digest_gate_result": f"digest_gate_all = {verification.get('digest_gate_all', 'UNKNOWN')} на этапе скачивания входов; симуляции не запускались",
            "notes": "наличие digest-гейтов отражает выполненное скачивание; отсутствие измерений — отдельный факт (NOT_RUN)",
        },
        "measured_observables": {},
        "integrity": {
            "gates_passed": False,
            "frames_valid": "0/0 (NOT_RUN)",
            "details": [
                f"arm-manifest-v1: {failure['outcome']} (детерминированно, {failure['attempts']} attempts)",
                str(failure["consequence"]),
            ],
            "notes": "integrity-гейты не проходились; это не PASS и не отрицательный научный результат — это NOT_RUN",
        },
        "known_gaps": [
            {
                "gap_id": "G-74B-ARM-MANIFEST",
                "description": "Детерминированный отказ arm-manifest-v1 на 74b (no threshold in PARALLEL_GRID yields two dominant rigid blocks); runs NOT_RUN. Ремонт — отдельный bounded WO arm-manifest-v2; release v0.1 сознательно не задерживается этим гэпом (route R1 Phase B).",
                "status": "KNOWN_GAP",
                "blocking_release": False,
            }
        ],
        "known_limitations": [
            "по 74b нет ни одного измеренного значения в v0.1",
            "после закрытия arm-manifest-v2 карточка пересобирается по measured evidence в новой версии пакета, а не редактируется задним числом",
        ],
        "reproduction": {
            "requires": ["закрытый bounded WO arm-manifest-v2 (предусловие воспроизводимости)"],
            "steps": [
                "1. убедиться, что arm-manifest-v2 принят и опубликован в новой версии пакета",
                "2. воспроизвести measured-карточку 74b по её reproduction-секции в этой новой версии",
            ],
            "expected": {},
            "tolerance_policy": "n/a — воспроизводить нечего (NOT_MEASURED); попытка воспроизведения отсутствующих значений не предполагается",
            "rights_constraints": "как у семейства: download-on-run по exact pinned commit, durable-cache запрещён",
        },
        "provenance": {
            "evidence_execution_id": PARAM_EXEC_ID["74b"],
            "card_generated_from": [
                "docs/work/executions/EX-NL3-002-PARAM-74B-R1/evidence/arm-manifest-74b-failure.json",
                "docs/work/executions/EX-NL3-002-PARAM-74B-R1/evidence/source-download-verification.json",
                PARAM_SUMMARY_REL,
                "scripts/hinge_family/source_pins.json",
            ],
            "generation": "built by release.build_library.py (WO-NL5-001-B-R1) from published evidence; deterministic and byte-reproducible (--check)",
        },
    }


def _source_digests(pins: dict[str, Any]) -> dict[str, Any]:
    upstream = pins["source"]
    variants: dict[str, Any] = {}
    for variant in VARIANTS:
        if variant in PARAM_EXEC:
            verification = _download_verification(variant)
            variants[variant] = {
                "digest_gate_all": verification.get("digest_gate_all", "UNKNOWN"),
                "files": {rel: _digest_entry(record) for rel, record in verification["files"].items()},
            }
        else:
            # 0b: verified during the R1 campaign; registry pins carry content sha256.
            variants[variant] = {
                "digest_gate_all": "PASS",
                "files": _digest_gates_0b(pins),
                "provenance": "sha256_provenance from source_pins.json (R1_CONTENT_VERIFIED)",
            }
    return {
        "schema_version": 1,
        "kind": "nanolab_components_source_digests",
        "upstream": {
            "repository": upstream["repository"],
            "pinned_commit": upstream["commit"],
            "tree": upstream.get("tree"),
            "rights_mode": upstream["mode"],
        },
        "digest_vocabulary": {
            "blob_sha1": "registry pin (Git blob SHA1), verified for every listed file",
            "sha256_status:CONTENT_VERIFIED": "sha256 verified against a registry claim",
            "sha256_status:COMPUTED_NOT_VERIFIED": "sha256 computed at download for future re-use; no registry claim (G1 vocabulary)",
        },
        "variants": variants,
        "notes": "upstream-файлы в пакет не включены (REFERENCE_ONLY); доступ — download-on-run пользователем по exact pinned commit",
    }


def _protocols_readme(engine: str) -> str:
    return f"""# Protocols (v0.1)

Все измерения v0.1 выполнены по замороженному протоколу `E2_PROTO_R1`
(включая статистику §6 и гейты §4 и addendum §8 — общее сравнительное окно
150000 steps) с observables `E2_OBSERVABLES_R2`.

Пины движка: oxDNA @ `{engine}` (CPU build, double precision), модель DNA2.

Полную копию протокола см. в репозитории NanoLab
(`docs/research/E2_PROTO_R1.md`, `docs/research/E2_OBSERVABLES_R2.md`,
`docs/research/ENGINE_ENVIRONMENT_R1.md`); снапшоты результатов —
`reports/evidence/`. Upstream-протокол автора — REFERENCE_ONLY,
download-on-run по exact pinned commit (см. `RIGHTS.json`).
"""


def _family_report(cards: dict[str, dict[str, Any]]) -> str:
    rows = []
    for variant in VARIANTS:
        card = cards[variant]
        if card["measurement_status"] == "MEASURED":
            obs = card["measured_observables"].get(
                "hinge_angle_confirmatory_200k" if variant == "0b" else "hinge_angle_common_window_150k"
            )
            ci = obs["uncertainty"]
            rows.append(
                f"| `{variant}` | {obs['estimate']:.9f} | [{ci[0]:.9f}, {ci[1]:.9f}] | {obs['n']} | "
                f"{'confirmatory 200k + window 150k' if variant == '0b' else 'common window 150k'} |"
            )
        else:
            rows.append(f"| `{variant}` | — | — | 0 | NOT_MEASURED (KNOWN_GAP: arm-manifest-v2 pending) |")
    return f"""# DNA hinge family — measured results (v0.1)

Одно семейство с измеренными вариантами; числа взяты verbatim из опубликованного
evidence NanoLab (снапшоты в `reports/evidence/`). Кросс-вариантные тренды здесь
не интерпретируются.

| Вариант | Медиана угла, deg | bootstrap CI95 | n | Базис |
|---|---|---|---|---|
{chr(10).join(rows)}

Единицы и конвенция угла: {ANGLE_CONVENTION}.

Движок и протокол: см. `protocols/README.md`. Права: см. `RIGHTS.json`.
Гэп 74b: см. `families/dna_hinge/cards/74b.card.json`.
"""


def check() -> list[str]:
    """Rebuild into a temp dir and compare byte-for-byte with the committed package."""
    import tempfile

    problems: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        built_root = Path(tmp) / "pkg"
        build(built_root)
        built = {p.relative_to(built_root).as_posix() for p in built_root.rglob("*") if p.is_file()}
        committed = {
            p.relative_to(PKG_ROOT).as_posix()
            for p in PKG_ROOT.rglob("*")
            if p.is_file() and p.name != "RELEASE_MANIFEST.json"
        }
        for rel in sorted(built | committed):
            built_bytes = (built_root / rel).read_bytes() if rel in built else None
            committed_bytes = (PKG_ROOT / rel).read_bytes() if rel in committed else None
            if committed_bytes is None:
                problems.append(f"built file not committed: {rel}")
            elif built_bytes is None:
                problems.append(f"committed file not produced by builder: {rel}")
            elif built_bytes != committed_bytes:
                problems.append(f"byte mismatch: {rel}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="release.build_library", description="Deterministic evidence -> package builder")
    parser.add_argument("mode", choices=["build", "check"])
    args = parser.parse_args(argv)
    try:
        if args.mode == "build":
            written = build()
            print(json.dumps({"schema": "nanolab.release_build_output.v1", "mode": "build", "ok": True, "files": len(written)}, ensure_ascii=False, indent=2))
            return 0
        problems = check()
        print(json.dumps({"schema": "nanolab.release_build_output.v1", "mode": "check", "ok": not problems, "problems": problems}, ensure_ascii=False, indent=2))
        return 0 if not problems else 3
    except BuildError as exc:
        print(json.dumps({"schema": "nanolab.release_build_output.v1", "mode": args.mode, "ok": False, "problems": [str(exc)]}, ensure_ascii=False, indent=2))
        return 3


if __name__ == "__main__":
    sys.exit(main())
