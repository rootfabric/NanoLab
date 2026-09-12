"""Hinge angle and structural integrity observables (v1, frozen).

Definitions implemented here are frozen in ``docs/research/E2_OBSERVABLES_R1.md``
BEFORE any production data: first-principles PCA arm axes with a fixed
sign convention (unsigned angle in [0, 90] degrees), greedy complementary
reference base pairs, bonded-link integrity and maximum displacement.

Fail-closed: NaN/Inf, truncated trajectories, invalid manifests and digest
mismatches are errors, never silent values. No wall-clock data in reports.
"""
from __future__ import annotations

import argparse
import json
import math

try:
    from .canonical import canonical_json
except ImportError:
    from canonical import canonical_json

from hinge_family.oxdna_conf import ConfError, Configuration
from hinge_family.oxdna_topology import Topology, TopologyError

# Frozen algorithmic constants (E2_OBSERVABLES_R1 section 3; ill-defined-axis
# criterion corrected to the isotropy form in R1 note 2026-09-12, pre-data)
PAIR_D_MIN = 0.05
PAIR_D_MAX = 0.55
BOND_D_MAX = 1.0
EIG_INVALID = 1e-12
ISOTROPY_EPS = 1e-9
ORIENTATION_EPS = 1e-9
ANGLE_TOLERANCE_DEG = 1e-6

COMPLEMENT = {"A": "T", "T": "A", "C": "G", "G": "C"}

COMPLEMENTS = {(b, COMPLEMENT[b]) for b in "ATCG"}


class ObservableError(Exception):
    pass


# ----------------------------------------------------------------- geometry
def mic_delta(a, b, box):
    """Minimum-image delta a - b for an orthorhombic box."""
    delta = [a[axis] - b[axis] for axis in range(3)]
    for axis in range(3):
        delta[axis] -= box[axis] * round(delta[axis] / box[axis])
    return delta


def dist_mic(a, b, box):
    d = mic_delta(a, b, box)
    return math.sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2])


def _sym_eigen(c):
    """Eigenvalues of a symmetric 3x3 matrix (trigonometric method)."""
    m00, m01, m02 = c[0][0], c[0][1], c[0][2]
    _, m11, m12 = c[1][0], c[1][1], c[1][2]
    _, _, m22 = c[2][0], c[2][1], c[2][2]
    p1 = m01 * m01 + m02 * m02 + m12 * m12
    if p1 == 0.0:
        return sorted([m00, m11, m22], reverse=True)
    q = (m00 + m11 + m22) / 3.0
    p2 = (m00 - q) ** 2 + (m11 - q) ** 2 + (m22 - q) ** 2 + 2.0 * p1
    p = math.sqrt(p2 / 6.0)
    if p == 0.0:
        return sorted([m00, m11, m22], reverse=True)
    b00, b01, b02 = (m00 - q) / p, m01 / p, m02 / p
    b11, b12 = (m11 - q) / p, m12 / p
    b22 = (m22 - q) / p
    det_b = (
        b00 * (b11 * b22 - b12 * b12)
        - b01 * (b01 * b22 - b12 * b02)
        + b02 * (b01 * b12 - b11 * b02)
    )
    r = det_b / 2.0
    r = max(-1.0, min(1.0, r))
    phi = math.acos(r) / 3.0
    eig1 = q + 2.0 * p * math.cos(phi)
    eig3 = q + 2.0 * p * math.cos(phi + 2.0 * math.pi / 3.0)
    eig2 = (m00 + m11 + m22) - eig1 - eig3
    return sorted([eig1, eig2, eig3], reverse=True)


def _sym_eigen_vector(c, lam):
    """Eigenvector of symmetric 3x3 for eigenvalue lam (row-cross method)."""
    m = [
        [c[0][0] - lam, c[0][1], c[0][2]],
        [c[1][0], c[1][1] - lam, c[1][2]],
        [c[2][0], c[2][1], c[2][2] - lam],
    ]

    def cross(u, v):
        return [
            u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0],
        ]

    candidates = [
        cross(m[0], m[1]),
        cross(m[0], m[2]),
        cross(m[1], m[2]),
    ]
    best, best_norm = None, -1.0
    for vec in candidates:
        norm = math.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
        if norm > best_norm:
            best, best_norm = vec, norm
    if best_norm <= 0.0:
        raise ObservableError("degenerate covariance: no eigenvector direction")
    return [x / best_norm for x in best]


def arm_axis(positions, centroid, other_centroid):
    """Principal axis of a point set with frozen sign convention (R1 section 2)."""
    centered = [[p[axis] - centroid[axis] for axis in range(3)] for p in positions]
    cov = [[0.0] * 3 for _ in range(3)]
    for p in centered:
        for i in range(3):
            for j in range(3):
                cov[i][j] += p[i] * p[j]
    n = len(positions)
    cov = [[cov[i][j] / n for j in range(3)] for i in range(3)]
    eigenvalues = _sym_eigen(cov)
    lam1 = eigenvalues[0]
    lam2 = eigenvalues[1]
    # Axis is ill-defined when the point set has no dominant extension
    # (isotropic cloud): the two largest eigenvalues coincide. A perfectly
    # straight line has lam2 = 0 and a perfectly well-defined axis.
    if lam1 < EIG_INVALID or (lam1 - lam2) / lam1 < ISOTROPY_EPS:
        return None, {"ill_defined": True, "eigenvalues": eigenvalues}
    axis = _sym_eigen_vector(cov, lam1)
    toward = [other_centroid[k] - centroid[k] for k in range(3)]
    dot = sum(axis[k] * toward[k] for k in range(3))
    ambiguous = abs(dot) < ORIENTATION_EPS
    if dot < 0.0 and not ambiguous:
        axis = [-x for x in axis]
    return (
        axis,
        {
            "ill_defined": False,
            "eigenvalues": eigenvalues,
            "ambiguous_orientation": ambiguous,
        },
    )


def hinge_angle(conf: Configuration, manifest: dict) -> dict:
    indices = {name: manifest[name]["nucleotides"] for name in ("arm_a", "arm_b")}
    parts = {}
    for name in sorted(indices):
        idxs = indices[name]
        if not idxs or len(idxs) < 3:
            raise ObservableError(f"arm {name} needs at least 3 nucleotides")
        if any(not isinstance(i, int) or not 0 <= i < len(conf.particles) for i in idxs):
            raise ObservableError(f"arm {name} contains an out-of-range nucleotide index")
        parts[name] = [conf.particles[i][0] for i in idxs]
    if set(indices["arm_a"]) & set(indices["arm_b"]):
        raise ObservableError("arm_a and arm_b overlap")
    centroids = {
        name: [sum(p[axis] for p in parts[name]) / len(parts[name]) for axis in range(3)]
        for name in ("arm_a", "arm_b")
    }
    axis_a, info_a = arm_axis(parts["arm_a"], centroids["arm_a"], centroids["arm_b"])
    axis_b, info_b = arm_axis(parts["arm_b"], centroids["arm_b"], centroids["arm_a"])
    if info_a["ill_defined"] or info_b["ill_defined"]:
        return {
            "angle_deg": None,
            "angle_rad": None,
            "status": "ILL_DEFINED_AXIS",
            "arm_a": info_a,
            "arm_b": info_b,
        }
    dot = sum(axis_a[axis] * axis_b[axis] for axis in range(3))
    dot = max(-1.0, min(1.0, dot))
    angle = math.degrees(math.acos(dot))
    return {
        "angle_deg": angle,
        "angle_rad": math.radians(angle),
        "status": "OK",
        "arm_a": info_a,
        "arm_b": info_b,
    }


# ---------------------------------------------------------------- integrity
def reference_pairs(conf: Configuration, topology: Topology) -> list:
    n = topology.nucleotides
    if len(conf.particles) != n:
        raise ObservableError("configuration and topology nucleotide counts differ")
    bases = [row[1] for row in topology.rows]
    n3 = [row[2] for row in topology.rows]
    n5 = [row[3] for row in topology.rows]
    bonded = set()
    for i in range(n):
        for j in (n3[i], n5[i]):
            if j != -1:
                bonded.add((min(i, j), max(i, j)))
    candidates = []
    box = conf.box
    for i in range(n):
        pi = conf.particles[i][0]
        bi = bases[i]
        for j in range(i + 1, n):
            if (bi, bases[j]) not in COMPLEMENTS:
                continue
            if (i, j) in bonded:
                continue
            d = dist_mic(pi, conf.particles[j][0], box)
            if PAIR_D_MIN < d <= PAIR_D_MAX:
                candidates.append((d, i, j))
    candidates.sort()
    used = set()
    pairs = []
    for d, i, j in candidates:
        if i in used or j in used:
            continue
        used.add(i)
        used.add(j)
        pairs.append({"i": i, "j": j, "d_ref": d})
    pairs.sort(key=lambda p: (p["i"], p["j"]))
    return pairs


def pairs_fraction(conf: Configuration, ref_pairs: list) -> dict:
    if not ref_pairs:
        return {"pairs_fraction": None, "status": "NO_REFERENCE_PAIRS", "broken": 0}
    box = conf.box
    broken = 0
    worst = 0.0
    for pair in ref_pairs:
        d = dist_mic(conf.particles[pair["i"]][0], conf.particles[pair["j"]][0], box)
        worst = max(worst, d)
        if d > PAIR_D_MAX:
            broken += 1
    return {
        "pairs_fraction": 1.0 - broken / len(ref_pairs),
        "status": "OK",
        "broken": broken,
        "worst_pair_distance": worst,
    }


def bonded_integrity(conf: Configuration, topology: Topology) -> dict:
    box = conf.box
    links = 0
    long_bonds = 0
    for i in range(topology.nucleotides):
        j = topology.rows[i][2]
        if j == -1:
            continue
        links += 1
        if dist_mic(conf.particles[i][0], conf.particles[j][0], box) > BOND_D_MAX:
            long_bonds += 1
    if links == 0:
        raise ObservableError("topology has no bonded links")
    return {
        "long_bond_fraction": long_bonds / links,
        "long_bonds": long_bonds,
        "links": links,
        "bond_d_max": BOND_D_MAX,
    }


def displacement_max(conf_ref: Configuration, conf: Configuration) -> dict:
    if len(conf_ref.particles) != len(conf.particles):
        raise ObservableError("frame particle counts differ from the reference frame")
    box = conf_ref.box
    worst = 0.0
    for i in range(len(conf.particles)):
        d = dist_mic(conf.particles[i][0], conf_ref.particles[i][0], box)
        if d > worst:
            worst = d
    return {"displacement_max": worst}


# --------------------------------------------------------------- trajectory
def iter_frames(text: str):
    """Split trajectory text into configuration blocks (fail-closed)."""
    blocks = []
    current = None
    for line in text.splitlines():
        if line.startswith("t ="):
            if current is not None:
                blocks.append(current)
            current = [line]
        elif current is not None:
            current.append(line)
    if current is not None:
        blocks.append(current)
    if not blocks:
        raise ObservableError("trajectory contains no configuration blocks")
    for block in blocks:
        yield Configuration.parse("\n".join(block))


def load_manifest(path) -> dict:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        manifest = json.load(handle)
    for name in ("arm_a", "arm_b"):
        if name not in manifest or "nucleotides" not in manifest[name]:
            raise ObservableError(f"manifest missing {name}.nucleotides")
    return manifest


def analyse(topology: Topology, frames: list, manifest: dict) -> dict:
    ref = frames[0]
    ref.check_orientation()
    ref_pairs = reference_pairs(ref, topology)
    frame_reports = []
    for pos, conf in enumerate(frames):
        conf.check_orientation()
        angle = hinge_angle(conf, manifest)
        pairs = pairs_fraction(conf, ref_pairs)
        bonds = bonded_integrity(conf, topology)
        disp = displacement_max(ref, conf)
        frame_reports.append(
            {
                "frame": pos,
                "time": conf.time,
                "hinge_angle": angle,
                "pairs": pairs,
                "bonded": bonds,
                "displacement": disp,
            }
        )
    ok_frames = [f for f in frame_reports if f["hinge_angle"]["status"] == "OK"]
    angles = [f["hinge_angle"]["angle_deg"] for f in ok_frames]
    return {
        "schema_version": 1,
        "kind": "e2_observables_v1_trace",
        "definitions": "docs/research/E2_OBSERVABLES_R1.md (v1, first-principles, open U-obs-1)",
        "manifest": {
            "arm_a": {"nucleotides": sorted(manifest["arm_a"]["nucleotides"])},
            "arm_b": {"nucleotides": sorted(manifest["arm_b"]["nucleotides"])},
        },
        "reference_pairs_count": len(ref_pairs),
        "frames_total": len(frame_reports),
        "frames_ok_angle": len(ok_frames),
        "angle_deg_all_frames": angles,
        "frames": frame_reports,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="compute frozen v1 observables on a trajectory")
    parser.add_argument("topology_path")
    parser.add_argument("trajectory_path")
    parser.add_argument("manifest_path")
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    topology = Topology.from_file(args.topology_path)
    topology.check_chain_integrity()
    with open(args.trajectory_path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    manifest = load_manifest(args.manifest_path)
    report = analyse(topology, list(iter_frames(text)), manifest)
    rendered = canonical_json(report)
    if args.report:
        with open(args.report, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
