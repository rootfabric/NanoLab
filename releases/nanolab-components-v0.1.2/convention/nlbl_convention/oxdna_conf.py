"""Strict parser and structural checks for oxDNA configuration/restart files.

Column layout recorded from the pinned Shi-Castro-Arya surfaces (15 numeric
columns per particle):

    0:3   position
    3:6   orientation triple (exactly unit)
    6:9   orientation triple (exactly unit, orthogonal to 3:6)
    9:12  bounded triple, velocity-like scale
    12:15 bounded triple, velocity-like scale

The mechanical properties enforced here are the unit norm and orthogonality of
the two orientation triples plus finiteness of all values; the semantic labels
of columns 9:15 are an interpretation consistent with oxDNA configuration
conventions and remain pending confirmation against engine documentation
(pre-E2 engine-input check).
"""
from __future__ import annotations

import math

ORIENTATION_TOLERANCE = 1e-6


class ConfError(Exception):
    pass


class Configuration:
    def __init__(self, time: str, box: list, energy_line: str, particles: list):
        self.time = time
        self.box = box
        self.energy_line = energy_line
        self.particles = particles  # list of 5 triples

    @classmethod
    def parse(cls, text: str) -> "Configuration":
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if len(lines) < 4:
            raise ConfError("configuration has too few lines")
        if not lines[0].startswith("t ="):
            raise ConfError("configuration line 0 must start with 't ='")
        time = lines[0].split("=", 1)[1].strip()
        if not lines[1].startswith("b ="):
            raise ConfError("configuration line 1 must start with 'b ='")
        try:
            box = [float(x) for x in lines[1].split("=", 1)[1].split()]
        except ValueError as exc:
            raise ConfError(f"configuration box not floats: {exc}") from exc
        if len(box) != 3 or any(x <= 0 for x in box):
            raise ConfError("configuration box must be three positive floats")
        if not lines[2].startswith("E ="):
            raise ConfError("configuration line 2 must start with 'E ='")
        energy_line = lines[2]
        body = lines[3:]
        particles = []
        for idx, line in enumerate(body):
            parts = line.split()
            if len(parts) != 15:
                raise ConfError(f"configuration particle {idx} does not have 15 columns")
            try:
                values = [float(x) for x in parts]
            except ValueError as exc:
                raise ConfError(f"configuration particle {idx} has non-numeric fields: {exc}") from exc
            for v in values:
                if math.isnan(v) or math.isinf(v):
                    raise ConfError(f"configuration particle {idx} contains NaN/Inf")
            particles.append((values[0:3], values[3:6], values[6:9], values[9:12], values[12:15]))
        return cls(time, box, energy_line, particles)

    @classmethod
    def from_file(cls, path) -> "Configuration":
        with open(path, "r", encoding="utf-8", newline="") as handle:
            return cls.parse(handle.read())

    # ----------------------------------------------------------------- checks
    def check_orientation(self) -> dict:
        """Both orientation triples must be unit and mutually orthogonal."""
        max_dev = 0.0
        for _, o1, o2, _, _ in self.particles:
            n1 = math.sqrt(sum(x * x for x in o1))
            n2 = math.sqrt(sum(x * x for x in o2))
            dot = sum(x * y for x, y in zip(o1, o2))
            dev = max(abs(n1 - 1.0), abs(n2 - 1.0), abs(dot))
            if dev > max_dev:
                max_dev = dev
        if max_dev > ORIENTATION_TOLERANCE:
            raise ConfError(
                f"orientation vectors deviate from unit/orthogonal beyond tolerance: {max_dev!r}"
            )
        return {"max_deviation": max_dev, "tolerance": ORIENTATION_TOLERANCE}

    def check_positions_in_box(self) -> dict:
        """All particle positions must lie inside the declared box."""
        outside = 0
        for pos, _, _, _, _ in self.particles:
            if not all(0.0 <= pos[axis] <= self.box[axis] for axis in range(3)):
                outside += 1
        if outside:
            raise ConfError(f"{outside} particle positions outside the declared box")
        return {"outside": 0}

    def bonded_distance_stats(self, topology) -> dict:
        """Distance statistics over topology n3 links (minimum image, PBC)."""
        box = self.box
        total = 0.0
        minimum = float("inf")
        maximum = 0.0
        histogram = {}
        long_threshold = 0.95
        long_bonds = 0
        for i, (_, _, _, _, _) in enumerate(self.particles):
            j = topology.rows[i][2]
            if j == -1:
                continue
            delta = [self.particles[i][0][axis] - self.particles[j][0][axis] for axis in range(3)]
            for axis in range(3):
                delta[axis] -= box[axis] * round(delta[axis] / box[axis])
            dist = math.sqrt(sum(x * x for x in delta))
            total += dist
            minimum = min(minimum, dist)
            maximum = max(maximum, dist)
            bucket = round(dist, 1)
            histogram[bucket] = histogram.get(bucket, 0) + 1
            if dist > long_threshold:
                long_bonds += 1
        count = sum(histogram.values())
        if count == 0:
            raise ConfError("no bonded links found for distance statistics")
        return {
            "count": count,
            "min": minimum,
            "max": maximum,
            "mean": total / count,
            "histogram_0_1_buckets": {str(k): histogram[k] for k in sorted(histogram)},
            "long_bond_threshold": long_threshold,
            "long_bond_count": long_bonds,
        }


def configuration_facts(conf: Configuration, orientation: dict, bonded: dict) -> dict:
    return {
        "particles": len(conf.particles),
        "columns_per_particle": 15,
        "time": conf.time,
        "box": list(conf.box),
        "energy_line_fields": conf.energy_line.split("=", 1)[1].split(),
        "orientation_max_deviation": orientation["max_deviation"],
        "orientation_tolerance": orientation["tolerance"],
        "bonded_distances": bonded,
    }
