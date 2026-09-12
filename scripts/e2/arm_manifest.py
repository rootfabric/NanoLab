"""First-principles derivation of the hinge arm manifest for 0b (U-obs-1 path).

Preregistered in docs/work/WO-NL3-002-PROTO.md and defined by decision
docs/control/E2_OBS1_SI_DECISION_R1.md: the two arm groups ("arm_a", "arm_b")
are derived deterministically from the author's 0b.top + 0b.conf frame 0 by
geometry alone (NOT from the paper SI). The manifest is a derived result and
may be published; the source bytes never enter Git (G1 = B, download-on-run,
digest-gated, no durable cache, files deleted after use).

Algorithm (ALGORITHM_VERSION below; every step is deterministic and uses
fixed tie-breaks so two runs on identical inputs produce byte-identical
canonical JSON):

1. Pair graph. Candidate base pairs from the v2 geometry detector
   (observables.reference_pairs_v2 with mutual_nearest=False): complementary
   bases, not covalently bonded, minimum-image center distance in
   (0.05, 1.3] and antiparallel a1 axes (a1_i . a1_j <= -0.3), then the
   deterministic greedy (d, i, j) one-to-one matching. The greedy variant
   (no mutual-nearest restriction) is used because the manifest needs
   maximal pair-graph coverage (94.9% of nucleotides on the author frame 0)
   rather than per-pair uniqueness. Bucketed spatial grid: O(N).

2. Duplex chains. Union-find over paired nucleotides with
   (a) base-pair edges and (b) "stacking continuation" covalent edges:
   a covalent n3/n5 link (u, v) joins the same duplex only when the partners
   p(u), p(v) are themselves covalently linked. This propagates chains along
   intact duplexes while EXCLUDING crossover links (where partners are on
   unrelated strands), so chains never cross the hinge.

3. Rigid blocks. Each chain gets a principal axis (analytic symmetric 3x3
   eigensolver, same as observables R1). Two chains are "packing contacts"
   if any of their nucleotides lie within PACK_DIST (2.5 oxDNA units ~ the
   origami helix-packing scale). Blocks grow by unioning contacted chains
   whose axes are parallel within |cos| >= threshold; the threshold is not
   hand-picked: it is selected deterministically from PARALLEL_GRID by the
   dominance-gap rule (both largest blocks >= 10% of paired nucleotides and
   second/third block size ratio maximal over the fixed grid). Bundled
   helices inside one arm are near-parallel and packed; helices meeting at
   the hinge are not parallel at a non-zero arm angle, so the contact does
   not merge the arms.

4. The two largest blocks become arm_a (larger, ties by smaller minimum
   index) and arm_b. Remaining paired chains are assigned to the nearer
   block when within PACK_DIST of exactly one closer block (strictly smaller
   distance; ties stay unassigned), iterated to a fixed point.

Validation (fail-closed): groups must be non-empty, disjoint, consist only
of paired nucleotides and pass the manifest requirements of the frozen R1
hinge angle (>= 3 nucleotides each, in range). The frame-0 hinge angle under
the frozen R1 definition is reported as a measured fact (no fitting).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import urllib.request

try:
    from .canonical import canonical_json
    from .digests import git_blob_sha1, sha256_bytes
    from .observables import (
        ObservableError,
        _sym_eigen,
        _sym_eigen_vector,
        hinge_angle,
        reference_pairs_v2,
    )
except ImportError:
    from canonical import canonical_json
    from digests import git_blob_sha1, sha256_bytes
    from observables import (
        ObservableError,
        _sym_eigen,
        _sym_eigen_vector,
        hinge_angle,
        reference_pairs_v2,
    )

from hinge_family.oxdna_conf import Configuration
from hinge_family.oxdna_topology import Topology

ALGORITHM_VERSION = "arm-manifest-v1"
PACK_DIST = 2.5
PARALLEL_GRID = (0.85, 0.90, 0.95, 0.98)
DOMINANT_MIN_FRACTION = 0.1
DOMINANT_GAP_RATIO = 3.0
SOURCE_BASE = (
    "https://raw.githubusercontent.com/gauravarya77/"
    "DNA-hinge-simulations/23fd1ff7731e9017bd776f49206dc42d70d9fe91/"
)
SOURCE_FILES = ("MD_Hinges/0b.top", "MD_Hinges/0b.conf")
PIN_REGISTRY = os.path.join(os.path.dirname(__file__), "..", "hinge_family", "source_pins.json")


class ArmManifestError(Exception):
    pass


# ------------------------------------------------------------- source access
def download_and_verify(dest_dir=None) -> dict:
    """Digest-gated download of the pinned 0b source files (G1 = B).

    Downloads into a fresh subdirectory of the system temp dir (outside any
    Git repository), verifies size + git blob SHA-1 + SHA-256 against
    scripts/hinge_family/source_pins.json and returns the report with local
    paths. No durable cache: the caller must delete the files after use.
    """
    if dest_dir is None:
        dest_dir = os.path.join(
            tempfile.gettempdir(), "nl3-002-proto-src", f"arm-manifest-{os.getpid()}"
        )
    os.makedirs(dest_dir, exist_ok=True)
    with open(PIN_REGISTRY, "r", encoding="utf-8") as handle:
        pins = json.load(handle)
    report = {
        "kind": "e2_arm_manifest_source_download",
        "download_base": SOURCE_BASE,
        "dest_dir": dest_dir,
        "durable_cache": False,
        "files": {},
    }
    ok = True
    for name in SOURCE_FILES:
        pin = pins["files"][name]
        url = SOURCE_BASE + name
        local = os.path.join(dest_dir, name.replace("/", "__"))
        with urllib.request.urlopen(url, timeout=120) as resp:
            data = resp.read()
        with open(local, "wb") as handle:
            handle.write(data)
        size_ok = len(data) == pin["size_bytes"]
        blob_ok = git_blob_sha1(data) == pin["blob_sha1"]
        sha_ok = sha256_bytes(data) == pin["sha256"]
        entry = {
            "local_path": local,
            "size_bytes": len(data),
            "size_expected": pin["size_bytes"],
            "size_match": size_ok,
            "blob_sha1": git_blob_sha1(data),
            "blob_sha1_expected": pin["blob_sha1"],
            "blob_sha1_match": blob_ok,
            "sha256": sha256_bytes(data),
            "sha256_expected": pin["sha256"],
            "sha256_match": sha_ok,
        }
        entry["digest_gate"] = "PASS" if (size_ok and blob_ok and sha_ok) else "FAIL"
        ok = ok and entry["digest_gate"] == "PASS"
        report["files"][name] = entry
    report["digest_gate_all"] = "PASS" if ok else "FAIL"
    return report


# ------------------------------------------------------------- derivation
class _UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)


def _duplex_chains(conf: Configuration, topology: Topology):
    """Pair map + duplex chains (stacking continuation, crossovers excluded)."""
    pairs = reference_pairs_v2(conf, topology, mutual_nearest=False)
    pair_of = {}
    for pair in pairs:
        pair_of[pair["i"]] = pair["j"]
        pair_of[pair["j"]] = pair["i"]
    n3 = [row[2] for row in topology.rows]
    n5 = [row[3] for row in topology.rows]
    uf = _UnionFind()
    for i in sorted(pair_of):
        if i < pair_of[i]:
            uf.union(i, pair_of[i])
    stack_edges = 0
    crossover_edges = 0
    for i in range(topology.nucleotides):
        for j in (n3[i], n5[i]):
            if j == -1 or i > j:
                continue
            if i in pair_of and j in pair_of:
                pi, pj = pair_of[i], pair_of[j]
                if pj in (n3[pi], n5[pi]):
                    uf.union(i, j)
                    stack_edges += 1
                else:
                    crossover_edges += 1
    chains = {}
    for i in sorted(pair_of):
        chains.setdefault(uf.find(i), []).append(i)
    return pairs, pair_of, chains, stack_edges, crossover_edges


def _chain_axis(conf: Configuration, members):
    positions = [conf.particles[i][0] for i in members]
    centroid = [sum(p[axis] for p in positions) / len(positions) for axis in range(3)]
    cov = [
        [
            sum(
                (p[a] - centroid[a]) * (p[b] - centroid[b]) for p in positions
            )
            / len(positions)
            for b in range(3)
        ]
        for a in range(3)
    ]
    eigenvalues = _sym_eigen(cov)
    if eigenvalues[0] <= 0.0:
        return None, centroid, eigenvalues
    return _sym_eigen_vector(cov, eigenvalues[0]), centroid, eigenvalues


def _packing_contacts(conf: Configuration, chains: dict) -> set:
    """Chain-id pairs with at least one inter-chain nucleotide pair <= PACK_DIST."""
    box = conf.box
    grid: dict = {}

    def cell_key(pos):
        return (int(pos[0] // PACK_DIST), int(pos[1] // PACK_DIST), int(pos[2] // PACK_DIST))

    chain_of = {}
    for cid in sorted(chains):
        for i in chains[cid]:
            chain_of[i] = cid
            grid.setdefault(cell_key(conf.particles[i][0]), []).append(i)
    offsets = [(dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)]
    contacts = set()

    def mic_dist2(i, j):
        delta = [conf.particles[i][0][axis] - conf.particles[j][0][axis] for axis in range(3)]
        for axis in range(3):
            delta[axis] -= box[axis] * round(delta[axis] / box[axis])
        return delta[0] * delta[0] + delta[1] * delta[1] + delta[2] * delta[2]

    for key in sorted(grid):
        for dx, dy, dz in offsets:
            neighbour = grid.get((key[0] + dx, key[1] + dy, key[2] + dz))
            if not neighbour:
                continue
            for i in grid[key]:
                for j in neighbour:
                    if j <= i:
                        continue
                    ca, cb = chain_of[i], chain_of[j]
                    if ca == cb:
                        continue
                    if mic_dist2(i, j) <= PACK_DIST * PACK_DIST:
                        contacts.add((min(ca, cb), max(ca, cb)))
    return contacts


def _cluster_blocks(axes: dict, chain_sizes: dict, contacts: set):
    """Parallel+packed clustering for every threshold in PARALLEL_GRID.

    Returns {threshold: sorted block sizes} and the selected threshold by
    the dominance-gap rule: among thresholds where both largest blocks have
    >= DOMINANT_MIN_FRACTION of paired nucleotides and the second block is
    >= DOMINANT_GAP_RATIO times the third (or only two blocks exist), pick
    the one with the maximal second/third ratio; ties resolved by the fixed
    grid order (earlier wins).
    """
    tables = {}
    for threshold in PARALLEL_GRID:
        uf = _UnionFind()
        for ca, cb in sorted(contacts):
            va, vb = axes[ca], axes[cb]
            if va is None or vb is None:
                continue
            if abs(sum(va[k] * vb[k] for k in range(3))) < threshold:
                continue
            uf.union(ca, cb)
        sizes = {}
        for cid, size in chain_sizes.items():
            sizes[uf.find(cid)] = sizes.get(uf.find(cid), 0) + size
        tables[threshold] = sorted(sizes.values(), reverse=True)
    total = sum(chain_sizes.values())

    def score(sizes):
        if len(sizes) < 2:
            return None
        if sizes[0] < DOMINANT_MIN_FRACTION * total or sizes[1] < DOMINANT_MIN_FRACTION * total:
            return None
        if len(sizes) == 2:
            return float("inf")
        if sizes[1] < DOMINANT_GAP_RATIO * sizes[2]:
            return None
        return sizes[1] / sizes[2]

    best_threshold = None
    best_score = None
    for threshold in PARALLEL_GRID:
        s = score(tables[threshold])
        if s is not None and (best_score is None or s > best_score):
            best_threshold, best_score = threshold, s
    return tables, best_threshold


def _blocks_at_threshold(axes: dict, chains: dict, contacts: set, threshold):
    uf = _UnionFind()
    for ca, cb in sorted(contacts):
        va, vb = axes[ca], axes[cb]
        if va is None or vb is None:
            continue
        if abs(sum(va[k] * vb[k] for k in range(3))) < threshold:
            continue
        uf.union(ca, cb)
    blocks = {}
    for cid in sorted(chains):
        blocks.setdefault(uf.find(cid), []).append(cid)
    return blocks


def _assign_residuals(conf: Configuration, chains: dict, arm_chains: dict):
    """Assign leftover chains to the strictly nearer arm within PACK_DIST."""
    box = conf.box
    arm_members = {
        name: sorted(i for cid in arm_chains[name] for i in chains[cid])
        for name in ("arm_a", "arm_b")
    }
    grid = {}
    for name in ("arm_a", "arm_b"):
        for i in arm_members[name]:
            grid.setdefault(
                (
                    int(conf.particles[i][0][0] // PACK_DIST),
                    int(conf.particles[i][0][1] // PACK_DIST),
                    int(conf.particles[i][0][2] // PACK_DIST),
                ),
                [],
            ).append((i, name))
    offsets = [(dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)]

    def mic_dist(i, j):
        delta = [conf.particles[i][0][axis] - conf.particles[j][0][axis] for axis in range(3)]
        for axis in range(3):
            delta[axis] -= box[axis] * round(delta[axis] / box[axis])
        return (delta[0] ** 2 + delta[1] ** 2 + delta[2] ** 2) ** 0.5

    assigned = {}
    changed = True
    while changed:
        changed = False
        for cid in sorted(chains):
            if cid in assigned or cid in arm_chains["arm_a"] or cid in arm_chains["arm_b"]:
                continue
            best = {"arm_a": None, "arm_b": None}
            for i in chains[cid]:
                key = (
                    int(conf.particles[i][0][0] // PACK_DIST),
                    int(conf.particles[i][0][1] // PACK_DIST),
                    int(conf.particles[i][0][2] // PACK_DIST),
                )
                for dx, dy, dz in offsets:
                    for j, name in grid.get(
                        (key[0] + dx, key[1] + dy, key[2] + dz), []
                    ):
                        d = mic_dist(i, j)
                        if d <= PACK_DIST and (best[name] is None or d < best[name]):
                            best[name] = d
            if best["arm_a"] is None and best["arm_b"] is None:
                continue
            if best["arm_a"] is not None and (
                best["arm_b"] is None or best["arm_a"] < best["arm_b"]
            ):
                assigned[cid] = "arm_a"
                grid.setdefault(
                    (
                        int(conf.particles[chains[cid][0]][0][0] // PACK_DIST),
                        int(conf.particles[chains[cid][0]][0][1] // PACK_DIST),
                        int(conf.particles[chains[cid][0]][0][2] // PACK_DIST),
                    ),
                    [],
                )
                for i in chains[cid]:
                    grid.setdefault(
                        (
                            int(conf.particles[i][0][0] // PACK_DIST),
                            int(conf.particles[i][0][1] // PACK_DIST),
                            int(conf.particles[i][0][2] // PACK_DIST),
                        ),
                        [],
                    ).append((i, "arm_a"))
                changed = True
            elif best["arm_b"] is not None and (
                best["arm_a"] is None or best["arm_b"] < best["arm_a"]
            ):
                assigned[cid] = "arm_b"
                for i in chains[cid]:
                    grid.setdefault(
                        (
                            int(conf.particles[i][0][0] // PACK_DIST),
                            int(conf.particles[i][0][1] // PACK_DIST),
                            int(conf.particles[i][0][2] // PACK_DIST),
                        ),
                        [],
                    ).append((i, "arm_b"))
                changed = True
    return assigned


def derive_manifest(conf: Configuration, topology: Topology, input_digests: dict = None) -> dict:
    """Derive the arm manifest report from a configuration + topology."""
    conf.check_orientation()
    pairs, pair_of, chains, stack_edges, crossover_edges = _duplex_chains(conf, topology)
    n_paired = len(pair_of)
    axes = {}
    chain_stats = {}
    for cid in sorted(chains):
        axis, centroid, eigenvalues = _chain_axis(conf, chains[cid])
        axes[cid] = axis
        chain_stats[cid] = {"size": len(chains[cid]), "centroid": centroid}
    contacts = _packing_contacts(conf, chains)
    chain_sizes = {cid: len(chains[cid]) for cid in chains}
    tables, threshold = _cluster_blocks(axes, chain_sizes, contacts)
    if threshold is None:
        raise ArmManifestError(
            "no threshold in PARALLEL_GRID yields two dominant rigid blocks; "
            f"size tables: {tables}"
        )
    blocks = _blocks_at_threshold(axes, chains, contacts, threshold)
    ordered = sorted(blocks.values(), key=lambda c: (-sum(chain_sizes[x] for x in c), min(c)))
    core_a, core_b = ordered[0], ordered[1]
    arm_chains = {"arm_a": set(core_a), "arm_b": set(core_b)}
    assigned = _assign_residuals(conf, chains, arm_chains)
    for cid, name in sorted(assigned.items()):
        arm_chains[name].add(cid)
    arms = {
        name: sorted(i for cid in sorted(arm_chains[name]) for i in chains[cid])
        for name in ("arm_a", "arm_b")
    }
    # fail-closed validation
    set_a, set_b = set(arms["arm_a"]), set(arms["arm_b"])
    if not set_a or not set_b:
        raise ArmManifestError("empty arm group")
    if set_a & set_b:
        raise ArmManifestError("arm groups overlap")
    if not set_a <= set(pair_of) or not set_b <= set(pair_of):
        raise ArmManifestError("arm group contains unpaired nucleotides")
    angle = hinge_angle(conf, {"arm_a": {"nucleotides": arms["arm_a"]}, "arm_b": {"nucleotides": arms["arm_b"]}})
    unassigned_chains = sorted(set(chains) - arm_chains["arm_a"] - arm_chains["arm_b"])
    report = {
        "schema_version": 1,
        "kind": "e2_arm_manifest",
        "algorithm": {
            "version": ALGORITHM_VERSION,
            "definition": "WO-NL3-002-PROTO preregistration; docs/control/E2_OBS1_SI_DECISION_R1.md (first-principles, not from SI)",
            "constants": {
                "pack_dist": PACK_DIST,
                "parallel_grid": list(PARALLEL_GRID),
                "dominant_min_fraction": DOMINANT_MIN_FRACTION,
                "dominant_gap_ratio": DOMINANT_GAP_RATIO,
            },
            "steps": [
                "pair graph: observables.reference_pairs_v2(mutual_nearest=False)",
                "duplex chains: pair edges + stacking-continuation covalent edges (crossovers excluded)",
                "rigid blocks: parallel+packed chain clustering, threshold by dominance-gap rule",
                "two largest blocks -> arm_a/arm_b; residuals assigned to the strictly nearer arm",
            ],
        },
        "inputs": input_digests or {},
        "pair_graph": {
            "detector": "v2 geometry (window, antiparallel a1) + greedy matching, mutual_nearest=False",
            "pairs": len(pairs),
            "paired_nucleotides": n_paired,
            "paired_fraction_of_topology": n_paired / topology.nucleotides,
            "stack_continuation_edges": stack_edges,
            "crossover_covalent_edges": crossover_edges,
        },
        "chains": {
            "count": len(chains),
            "largest_sizes": sorted(chain_sizes.values(), reverse=True)[:10],
        },
        "clustering": {
            "threshold_size_tables": {
                str(t): tables[t][:10] for t in PARALLEL_GRID
            },
            "selected_parallel_threshold": threshold,
            "selection_rule": "max second/third block size ratio subject to dominance constraints",
        },
        "arms": {
            "arm_a": {"nucleotides": arms["arm_a"], "size": len(arms["arm_a"])},
            "arm_b": {"nucleotides": arms["arm_b"], "size": len(arms["arm_b"])},
        },
        "coverage": {
            "topology_nucleotides": topology.nucleotides,
            "paired_nucleotides": n_paired,
            "manifest_nucleotides": len(set_a) + len(set_b),
            "manifest_fraction_of_topology": (len(set_a) + len(set_b)) / topology.nucleotides,
            "manifest_fraction_of_paired": (len(set_a) + len(set_b)) / n_paired,
            "unassigned_paired_nucleotides": n_paired - len(set_a) - len(set_b),
            "unassigned_chains": len(unassigned_chains),
        },
        "validation": {
            "groups_nonempty": True,
            "groups_disjoint": True,
            "only_paired_nucleotides": True,
            "hinge_angle_frame0": angle,
        },
    }
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="derive the first-principles 0b arm manifest (WO-NL3-002-PROTO)"
    )
    parser.add_argument("--top", help="local 0b.top path (offline mode)")
    parser.add_argument("--conf", help="local 0b.conf path (offline mode)")
    parser.add_argument("--download", action="store_true", help="digest-gated download-on-run")
    parser.add_argument("--report", help="write canonical JSON report here")
    parser.add_argument(
        "--keep-source", action="store_true", help="do not delete downloaded source files"
    )
    args = parser.parse_args(argv)
    if args.download == bool(args.top or args.conf):
        parser.error("use exactly one of --download or --top/--conf")
    download_report = None
    tmp_dir = None
    top_path, conf_path = args.top, args.conf
    if args.download:
        download_report = download_and_verify()
        if download_report["digest_gate_all"] != "PASS":
            print(canonical_json(download_report))
            return 1
        top_path = download_report["files"]["MD_Hinges/0b.top"]["local_path"]
        conf_path = download_report["files"]["MD_Hinges/0b.conf"]["local_path"]
        tmp_dir = os.path.dirname(top_path)
    try:
        with open(top_path, "rb") as handle:
            top_bytes = handle.read()
        with open(conf_path, "rb") as handle:
            conf_bytes = handle.read()
        digests = {
            "MD_Hinges/0b.top": {
                "size_bytes": len(top_bytes),
                "blob_sha1": git_blob_sha1(top_bytes),
                "sha256": sha256_bytes(top_bytes),
            },
            "MD_Hinges/0b.conf": {
                "size_bytes": len(conf_bytes),
                "blob_sha1": git_blob_sha1(conf_bytes),
                "sha256": sha256_bytes(conf_bytes),
            },
        }
        topology = Topology.from_file(top_path)
        topology.check_chain_integrity()
        conf = Configuration.from_file(conf_path)
        report = derive_manifest(conf, topology, {"digests": digests, "download": download_report})
        rendered = canonical_json(report)
        if args.report:
            with open(args.report, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
        print(rendered)
        return 0
    finally:
        if args.download and not args.keep_source and tmp_dir:
            import shutil

            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
