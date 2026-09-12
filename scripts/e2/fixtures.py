"""Deterministic synthetic fixtures with analytically known observables.

Fixtures are generated (never copied from the upstream source) so that every
observable has an exact expected value:

* ``parallel``  -- two paired arms along +x offset in y: angle 0 deg;
* ``angled``    -- two straight arms at a given angle with a 2-base duplex
                   brace between them: angle = the constructed angle;
* ``broken``    -- a two-frame trajectory whose second frame translates the
                   second arm and its brace strand by (0, 0, jump): the angle
                   stays the same (straight arms) while integrity fails.

All coordinates live well inside the box; no minimum-image wrap-around can
occur for the built values.
"""
from __future__ import annotations

import math
import os

BOX = (100.0, 100.0, 100.0)
ORIGIN = (20.0, 20.0, 20.0)
SPACING = 0.35
JUMP = 40.0


class FixtureError(Exception):
    pass


def _fmt(values) -> str:
    return " ".join(f"{v:.12f}" for v in values)


def _conf_text(t: int, particles) -> str:
    lines = [f"t = {t}", f"b = {_fmt(BOX)}", "E = 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0"]
    for pos, a1, a2 in particles:
        lines.append(_fmt(pos) + " " + _fmt(a1) + " " + _fmt(a2) + " " + _fmt((0.0, 0.0, 0.0)) + " " + _fmt((0.0, 0.0, 0.0)))
    return "\n".join(lines) + "\n"


def _orientation(dir_vec):
    norm = math.sqrt(sum(x * x for x in dir_vec))
    a1 = [x / norm for x in dir_vec]
    ref = (0.0, 0.0, 1.0) if abs(a1[2]) < 0.9 else (1.0, 0.0, 0.0)
    cross = [
        a1[1] * ref[2] - a1[2] * ref[1],
        a1[2] * ref[0] - a1[0] * ref[2],
        a1[0] * ref[1] - a1[1] * ref[0],
    ]
    cn = math.sqrt(sum(x * x for x in cross))
    a2 = [x / cn for x in cross]
    return a1, a2


class _Builder:
    def __init__(self):
        self.rows = []  # (strand_id, base, n3, n5)
        self.particles = []  # (pos, a1, a2) per nucleotide in file order

    def add_strand(self, base_letter, coords):
        sid = len(self.rows_slots()) + 1
        return self._add(sid, base_letter, coords)

    def rows_slots(self):
        strands = sorted({row[0] for row in self.rows})
        return strands

    def _add(self, sid, base_letter, coords):
        start = len(self.particles)
        a1, a2 = _orientation(
            (coords[1][0] - coords[0][0], coords[1][1] - coords[0][1], coords[1][2] - coords[0][2])
        ) if len(coords) > 1 else _orientation((1.0, 0.0, 0.0))
        for offset, pos in enumerate(coords):
            self.particles.append((pos, a1, a2))
            self.rows.append((sid, base_letter, -1, -1))
        for k in range(len(coords) - 1):
            self.rows[start + k] = (sid, base_letter, start + k + 1, self.rows[start + k][3])
            self.rows[start + k + 1] = (sid, base_letter, self.rows[start + k + 1][2], start + k)
        return list(range(start, start + len(coords)))

    def topology_text(self) -> str:
        lines = [f"{len(self.rows)} {max(row[0] for row in self.rows)}"]
        for sid, base, n3, n5 in self.rows:
            lines.append(f"{sid} {base} {n3} {n5}")
        return "\n".join(lines) + "\n"

    def shift(self, indices, delta):
        new_particles = []
        for i, (pos, a1, a2) in enumerate(self.particles):
            if i in indices:
                pos = (pos[0] + delta[0], pos[1] + delta[1], pos[2] + delta[2])
            new_particles.append((pos, a1, a2))
        self.particles = new_particles


def build(angle_deg=None, mode="parallel", arm_len=12, n_frames=1, broken=False, spacing=SPACING):
    """Build fixture data: returns dict with topology text, frame texts, manifest, expected.

    ``spacing`` overrides the inter-nucleotide distance along each arm. The
    default (0.35, close to the oxDNA helical rise) is used for observables
    validation; the cost probe passes a wider spacing because the engine's
    FENE bonded check rejects near-nucleotide center distances for
    backbone sites.
    """
    if mode not in ("parallel", "angled"):
        raise FixtureError(f"unknown mode {mode!r}")
    sp = spacing
    builder = _Builder()

    if mode == "parallel":
        coords_a = [(ORIGIN[0] + sp * i, ORIGIN[1], ORIGIN[2]) for i in range(arm_len)]
        coords_b = [(ORIGIN[0] + sp * i, ORIGIN[1] + 0.4, ORIGIN[2]) for i in range(arm_len)]
        idx_a = builder.add_strand("A", coords_a)
        idx_b = builder.add_strand("T", coords_b)
        expected_pairs = arm_len
        expected_angle = 0.0
        manifest = {"arm_a": {"nucleotides": idx_a}, "arm_b": {"nucleotides": idx_b}}
    else:
        if angle_deg is None or not 0.0 < angle_deg < 180.0:
            raise FixtureError("angled mode requires 0 < angle_deg < 180")
        theta = math.radians(angle_deg)
        u_a = (1.0, 0.0, 0.0)
        u_b = (math.cos(theta), math.sin(theta), 0.0)
        coords_a = [
            (ORIGIN[0] + sp * i * u_a[0], ORIGIN[1] + sp * i * u_a[1], ORIGIN[2])
            for i in range(arm_len)
        ]
        coords_b = [
            (ORIGIN[0] + sp * j * u_b[0], ORIGIN[1] + sp * j * u_b[1], ORIGIN[2])
            for j in range(arm_len)
        ]
        idx_a = builder.add_strand("A", coords_a)
        idx_b = builder.add_strand("T", coords_b)
        # 2-base duplex brace between arm A (index k) and arm B (index k)
        k = 1
        while True:
            gap = 2.0 * sp * k * math.sin(theta / 2.0)
            inset = gap / 2.0 - 0.2
            if inset > 0.02 and gap <= 1.2:
                break
            k += 1
            if k >= arm_len:
                raise FixtureError("no brace placement found for this angle")
        anchor_a = coords_a[k]
        anchor_b = coords_b[k]
        gap_vec = [anchor_b[axis] - anchor_a[axis] for axis in range(3)]
        gap_len = math.sqrt(sum(x * x for x in gap_vec))
        w = [x / gap_len for x in gap_vec]
        inset = gap_len / 2.0 - 0.2
        c0 = [anchor_a[axis] + inset * w[axis] for axis in range(3)]
        c1 = [c0[axis] + sp * w[axis] for axis in range(3)]
        d0 = [anchor_b[axis] - inset * w[axis] for axis in range(3)]
        d1 = [d0[axis] - sp * w[axis] for axis in range(3)]
        idx_c = builder.add_strand("G", [c0, c1])
        idx_d = builder.add_strand("C", [d0, d1])
        expected_pairs = 4  # 2 brace pairs + 2 near-hinge arm/arm complementary pairs
        expected_angle = angle_deg
        manifest = {
            "arm_a": {"nucleotides": idx_a},
            "arm_b": {"nucleotides": idx_b},
            "_brace_c": {"nucleotides": idx_c},
            "_brace_d": {"nucleotides": idx_d},
        }

    if n_frames < 1:
        raise FixtureError("n_frames must be >= 1")
    frames = [_conf_text(100 * (f + 1), builder.particles) for f in range(n_frames)]
    if broken:
        # translate the second arm and only the D side of the brace: every
        # reference pair must break while both arm axes stay straight
        target = set(manifest["arm_b"]["nucleotides"]) | set(
            manifest.get("_brace_d", {}).get("nucleotides", [])
        )
        builder.shift(target, (0.0, 0.0, JUMP))
        frames.append(_conf_text(100 * (n_frames + 1), builder.particles))

    return {
        "mode": mode,
        "angle_deg": expected_angle,
        "topology_text": builder.topology_text(),
        "frame_texts": frames,
        "manifest": {k: v for k, v in manifest.items() if not k.startswith("_")},
        "manifest_with_brace": manifest,
        "expected": {
            "angle_deg": expected_angle,
            "reference_pairs": expected_pairs,
            "jump": JUMP if broken else 0.0,
        },
    }


def write_fixture(directory, angle_deg=None, mode="parallel", arm_len=12, n_frames=1, broken=False):
    os.makedirs(directory, exist_ok=True)
    fixture = build(angle_deg=angle_deg, mode=mode, arm_len=arm_len, n_frames=n_frames, broken=broken)
    paths = {}
    paths["topology"] = os.path.join(directory, "fixture.top")
    with open(paths["topology"], "w", encoding="utf-8", newline="\n") as handle:
        handle.write(fixture["topology_text"])
    paths["trajectory"] = os.path.join(directory, "fixture_traj.dat")
    with open(paths["trajectory"], "w", encoding="utf-8", newline="\n") as handle:
        handle.write("".join(fixture["frame_texts"]))
    paths["manifest"] = os.path.join(directory, "fixture_manifest.json")
    import json

    with open(paths["manifest"], "w", encoding="utf-8", newline="\n") as handle:
        json.dump(fixture["manifest"], handle, sort_keys=True, indent=2)
        handle.write("\n")
    return {"paths": paths, "fixture": fixture}


def _empty_cell():
    return [-1, -1, -1, -1]


def design_pair_fixture():
    """Tiny consistent caDNAno design + matching oxDNA topology.

    2 helices x 8 columns. Scaffold: one path over all 16 cells (h0 0..7,
    crossover to h1 7..0). Staples: three paths (h0: 0..3, h0: 4..7,
    h1: 0..7). Topology strands mirror the four paths one-to-one, so the
    expected association is FULLY_ASSOCIATED_ONE_TO_ONE with 4 exact entries
    and conserved totals (16 + 16 bases/nucleotides).
    """
    vstrand0_scaf = []
    vstrand1_scaf = []
    vstrand0_stap = []
    vstrand1_stap = []
    for _ in range(8):
        vstrand0_scaf.append(_empty_cell())
        vstrand1_scaf.append(_empty_cell())
        vstrand0_stap.append(_empty_cell())
        vstrand1_stap.append(_empty_cell())
    # scaffold: h0 0..7 forward, crossover (0,7)->(1,7), h1 7..0 backward
    for i in range(8):
        cell = _empty_cell()
        if i > 0:
            cell[0], cell[1] = 0, i - 1
        if i < 7:
            cell[2], cell[3] = 0, i + 1
        else:
            cell[2], cell[3] = 1, 7
        vstrand0_scaf[i] = cell
    for i in range(7, -1, -1):
        cell = _empty_cell()
        if i < 7:
            cell[0], cell[1] = 1, i + 1
        else:
            cell[0], cell[1] = 0, 7
        if i > 0:
            cell[2], cell[3] = 1, i - 1
        vstrand1_scaf[i] = cell
    # staples: h0 0..3, h0 4..7, h1 0..7
    for start, end in ((0, 3), (4, 7)):
        for i in range(start, end + 1):
            cell = _empty_cell()
            if i > start:
                cell[0], cell[1] = 0, i - 1
            if i < end:
                cell[2], cell[3] = 0, i + 1
            vstrand0_stap[i] = cell
    for i in range(8):
        cell = _empty_cell()
        if i > 0:
            cell[0], cell[1] = 1, i - 1
        if i < 7:
            cell[2], cell[3] = 1, i + 1
        vstrand1_stap[i] = cell

    def vstrand(num):
        return {"num": num, "row": 0, "col": num, "scaf": None, "stap": None, "stap_colors": []}

    v0 = vstrand(0)
    v0["scaf"] = vstrand0_scaf
    v0["stap"] = vstrand0_stap
    v1 = vstrand(1)
    v1["scaf"] = vstrand1_scaf
    v1["stap"] = vstrand1_stap
    import json

    design_text = json.dumps({"name": "mapfix", "vstrands": [v0, v1]}, sort_keys=True, indent=2) + "\n"

    blocks = [(16, "A", 1), (4, "T", 2), (4, "T", 3), (8, "T", 4)]
    total = sum(block[0] for block in blocks)
    # emit rows with absolute neighbour indices per contiguous strand block
    top_lines = [f"{total} 4"]
    index = 0
    for length, base, sid in blocks:
        for k in range(length):
            n3 = index + k + 1 if k < length - 1 else -1
            n5 = index + k - 1 if k > 0 else -1
            top_lines.append(f"{sid} {base} {n3} {n5}")
        index += length
    topology_text = "\n".join(top_lines) + "\n"
    return {
        "design_text": design_text,
        "topology_text": topology_text,
        "expected": {
            "design_paths": 4,
            "topology_strands": 4,
            "exact_entries": [{"length": 4, "count": 2}, {"length": 8, "count": 1}, {"length": 16, "count": 1}],
            "association_status": "FULLY_ASSOCIATED_ONE_TO_ONE",
            "conservation": "CONSERVED",
            "total": 32,
        },
    }
