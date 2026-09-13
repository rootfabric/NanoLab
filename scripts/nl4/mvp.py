"""User-facing MVP CLI for NL4 (WO-NL4-003): goal JSON -> bounded experiment
-> real engine runs -> best -> fresh-seed re-validation -> report.

Pipeline (deterministic, scripted, NO LLM):

1. parse the user goal JSON ({"target_angle", "max_simulations", "steps",
   "revalidation_runs"});
2. informed-greedy strategy: rank the published parametric variants by
   |pooled common-window median (EX-NL3-002-SUMMARY-R1) - target|, take the
   top ``max_simulations`` variants, assign the frozen E2 seed triple in
   order; the published medians are embedded below as DATA with a source
   reference (no interpretation, no inference beyond nearest-first order);
3. execute the candidates as REAL parallel oxDNA runs through
   ``RealExecutorAdapter`` (pinned engine, digest-gated inputs, per-run
   evidence), then replay the identical action stream through the frozen
   ``Controller`` for canonical budget accounting;
4. pick best by score = |median_angle - target| over runs whose frozen
   E2_PROTO_R1 s.4 gates pass (nl4.scoring);
5. re-validate best with ONE fresh seed (206024 by default — outside the
   frozen E2 triple on purpose, anti-bias rule inherited from NL4-002;
   executed directly through the executor, not through the candidate
   space of the frozen allowlist);
6. final claimed score = re-validation score; write mvp-report.md +
   canonical mvp-report.json with goal, runs+digests, angle distribution,
   gates, chosen candidate + revalidated score, confidence (frames + CI),
   provenance, limitations, reproduction instructions and the verdict
   FOUND / NOT_FOUND (search failure is a supported outcome).

Usage (from the repo root, proxy env set for source downloads):
  python scripts/nl4/mvp.py --goal user-goal.json --out-dir <evidence-dir>
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from nl4 import real_executor as re_mod  # noqa: E402
from nl4.controller import Controller, ExecutorAdapter, load_allowlist  # noqa: E402
from nl4.real_executor import (  # noqa: E402
    ENGINE,
    ENGINE_SOURCE_COMMIT,
    RealExecutorAdapter,
    ReplayExecutor,
    candidate_digest,
)
from nl4.scoring import score_run, score_session  # noqa: E402
from e2.canonical import canonical_json  # noqa: E402

# --------------------------------------------------------------- published data
# Embedded as DATA (WO-NL4-003 s.1): pooled common-window medians of the
# published parametric series. 74b is NOT_MEASURED (BLOCKED manifest
# derivation) and is therefore absent from this prior table.
PUBLISHED_SERIES = {
    "source": (
        "docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/parametric-summary.json "
        "(pooled common-window t <= 150000 medians, valid frames only)"
    ),
    "median_deg": {
        "0b": 65.870460546,
        "11b": 73.928725839,
        "32b": 78.091845516,
        "53b": 132.35778773,
    },
    "excluded": {"74b": "NOT_MEASURED (arm-manifest derivation BLOCKED, EX-NL3-002-PARAM-74B-R1)"},
}

FROZEN_SEED_TRIPLE = (201004, 202008, 203012)
DEFAULT_REVALIDATION_SEED = 206024  # fresh by design: outside the frozen E2 triple
BOOTSTRAP_RESAMPLES = 10000
BOOTSTRAP_SEED = 424242  # E2_PROTO_R1 s.6 frozen bootstrap seed

ALLOWED_STEPS = (50000, 100000, 150000)  # frozen allowlist enum


# ----------------------------------------------------------------- goal parsing
def parse_user_goal(goal_json: dict) -> dict:
    """Validate the MVP user-goal JSON (WO-NL4-003 contract)."""
    if not isinstance(goal_json, dict):
        raise ValueError("goal must be a JSON object")
    target = goal_json.get("target_angle")
    if not isinstance(target, (int, float)) or isinstance(target, bool):
        raise ValueError("goal.target_angle must be a number (degrees, [0,180])")
    if not 0.0 <= float(target) <= 180.0:
        raise ValueError("goal.target_angle must lie in [0,180] (angle convention R1)")
    max_sims = goal_json.get("max_simulations")
    if not isinstance(max_sims, int) or isinstance(max_sims, bool) or max_sims < 1:
        raise ValueError("goal.max_simulations must be a positive integer")
    steps = goal_json.get("steps")
    if steps not in ALLOWED_STEPS:
        raise ValueError(f"goal.steps must be one of {list(ALLOWED_STEPS)} (frozen allowlist)")
    rev = goal_json.get("revalidation_runs")
    if not isinstance(rev, int) or isinstance(rev, bool) or rev < 0:
        raise ValueError("goal.revalidation_runs must be a non-negative integer")
    return {
        "target_angle": float(target),
        "max_simulations": int(max_sims),
        "steps": int(steps),
        "revalidation_runs": int(rev),
    }


def controller_goal(user_goal: dict) -> dict:
    """Map the user goal onto the frozen Controller goal contract.

    max_wall_minutes: cumulative executor-wall budget = (candidates +
    revalidation runs) x 72 min (per-run hard cap is 1.2 h, enforced by the
    adapter itself).
    """
    total_runs = user_goal["max_simulations"] + user_goal["revalidation_runs"]
    return {
        "target_angle_deg": user_goal["target_angle"],
        "max_simulations": user_goal["max_simulations"],
        "max_wall_minutes": float(total_runs * 72),
        "integrity_gate": "E2_PROTO_R1_S4_FROZEN",
    }


# ------------------------------------------------------------ informed-greedy
def plan_candidates(user_goal: dict) -> list:
    """Deterministic informed-greedy candidate plan (no LLM, no adaptivity).

    Rank published variants by |pooled median - target| (ties broken by
    variant name), take the top max_simulations, assign the frozen E2 seed
    triple in order.
    """
    target = user_goal["target_angle"]
    ranked = sorted(
        PUBLISHED_SERIES["median_deg"].items(),
        key=lambda kv: (abs(kv[1] - target), kv[0]),
    )
    chosen = [variant for variant, _ in ranked[: user_goal["max_simulations"]]]
    return [
        {
            "variant": variant,
            "steps": user_goal["steps"],
            "seed": FROZEN_SEED_TRIPLE[i % len(FROZEN_SEED_TRIPLE)],
        }
        for i, variant in enumerate(chosen)
    ]


class InformedGreedyAgent:
    """Scripted bounded agent emitting the informed-greedy plan verbatim."""

    name = "mvp-informed-greedy-r1"

    def __init__(self, candidates: list):
        self._plan = [dict(c) for c in candidates]
        self._index = 0
        self._pending = None

    def next_action(self, observations) -> dict | None:
        if self._pending is not None:
            candidate = self._pending
            self._pending = None
            return {"action": "request_run", "candidate": dict(candidate)}
        if self._index >= len(self._plan):
            return {"action": "stop"}
        candidate = self._plan[self._index]
        self._index += 1
        self._pending = candidate
        return {"action": "propose_candidate", "candidate": dict(candidate)}


# ------------------------------------------------------------------ statistics
def bootstrap_ci_median(values: list, resamples: int = BOOTSTRAP_RESAMPLES,
                         seed: int = BOOTSTRAP_SEED) -> list | None:
    """Deterministic bootstrap CI95 for the median (E2_PROTO_R1 s.6 method).

    Percentile bootstrap, resampling with replacement, frozen seed.
    """
    if len(values) < 2:
        return None
    rng = random.Random(seed)
    n = len(values)
    medians = []
    for _ in range(resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        sample.sort()
        medians.append(sample[n // 2] if n % 2 else 0.5 * (sample[n // 2 - 1] + sample[n // 2]))
    medians.sort()
    lo = medians[int(0.025 * (resamples - 1))]
    hi = medians[int(0.975 * (resamples - 1))]
    return [round(lo, 9), round(hi, 9)]


# --------------------------------------------------------------------- verdict
def published_best_gap(target: float) -> float:
    """|published-best median - target|: the bar a revalidated run must beat."""
    return round(min(abs(m - target) for m in PUBLISHED_SERIES["median_deg"].values()), 9)


def compute_verdict(candidate_scores: list, revalidation: dict | None, target: float) -> dict:
    """FOUND/NOT_FOUND per WO-NL4-003 s.D (frozen before the clean-room run).

    FOUND iff (a) a best valid candidate exists, (b) its re-validation run
    passed the frozen gates, and (c) the revalidated score is strictly below
    the published-best gap. Anything else — including gate failures, engine
    crashes and 'no valid run at all' — is NOT_FOUND (a supported outcome).
    """
    gap = published_best_gap(target)
    best = None
    valid = [s for s in candidate_scores if s["score"] is not None]
    if valid:
        valid.sort(key=lambda s: (s["score"], s["run_id"]))
        best = valid[0]
    reasons = []
    if best is None:
        reasons.append("NO_VALID_CANDIDATE_RUN")
        verdict = "NOT_FOUND"
    elif revalidation is None:
        reasons.append("NO_REVALIDATION_RUN")
        verdict = "NOT_FOUND"
    elif revalidation.get("revalidated_score", revalidation.get("score")) is None:
        reasons.append("REVALIDATION_GATE_FAIL")
        verdict = "NOT_FOUND"
    elif revalidation.get("revalidated_score", revalidation.get("score")) >= gap:
        reasons.append("REVALIDATED_SCORE_NOT_BELOW_PUBLISHED_BEST")
        verdict = "NOT_FOUND"
    else:
        verdict = "FOUND"
    return {
        "verdict": verdict,
        "rule": (
            "FOUND iff best valid candidate exists AND revalidation passes frozen gates "
            "AND revalidated |median - target| < published-best gap"
        ),
        "published_best_gap_deg": gap,
        "reasons": reasons,
    }


# ---------------------------------------------------------------------- report
def _run_rows(controller_report: dict, target: float) -> list:
    rows = []
    for run in controller_report["runs"]:
        scored = score_run(run["analysis"], target)
        rows.append(
            {
                "run_id": run["run_id"],
                "candidate": dict(run["candidate"]),
                "input_digest_sha256": run["input_digest_sha256"],
                "wall_seconds": run["wall_seconds"],
                "median_angle_deg": scored["median_angle_deg"],
                "score": scored["score"],
                "integrity_status": scored["status"],
            }
        )
    return rows


def build_report(user_goal: dict, controller_report: dict, revalidation: dict | None,
                 full_analyses: dict | None, provenance: dict) -> dict:
    """Assemble the canonical MVP report (pure function of its inputs)."""
    target = user_goal["target_angle"]
    rows = _run_rows(controller_report, target)
    scoring = score_session(controller_report)
    best_row = None
    valid_rows = [r for r in rows if r["score"] is not None]
    if valid_rows:
        valid_rows.sort(key=lambda r: (r["score"], r["run_id"]))
        best_row = valid_rows[0]
    full_analyses = full_analyses or {}

    def dist_for(run_id: str) -> dict:
        full = full_analyses.get(run_id) or {}
        stats = full.get("angle_stats_valid_frames") or {}
        frames = full.get("frames") or []
        angles = sorted(f["angle_deg"] for f in frames if f.get("valid") and f.get("angle_deg") is not None)
        return {
            "n_frames_total": full.get("frames_total"),
            "n_frames_valid": full.get("frames_valid"),
            "valid_frame_fraction": full.get("valid_frame_fraction"),
            "median_deg": stats.get("median_deg"),
            "min_deg": stats.get("min_deg"),
            "max_deg": stats.get("max_deg"),
            "bootstrap_ci95_median": bootstrap_ci_median(angles),
        }

    reval_block = None
    if revalidation is not None:
        rev_scored = score_run(revalidation["analysis"], target)
        reval_block = {
            "run_id": revalidation["run_id"],
            "candidate": dict(revalidation["candidate"]),
            "input_digest_sha256": revalidation["input_digest_sha256"],
            "wall_seconds": revalidation["wall_seconds"],
            "median_angle_deg": rev_scored["median_angle_deg"],
            "revalidated_score": rev_scored["score"],
            "integrity_status": rev_scored["status"],
            "distribution": dist_for(revalidation["run_id"]),
        }

    verdict = compute_verdict(rows, reval_block, target)
    return {
        "schema_version": 1,
        "kind": "nl4_mvp_report",
        "goal": dict(user_goal),
        "strategy": {
            "name": InformedGreedyAgent.name,
            "policy": "deterministic informed-greedy: published-nearest variant first, then next-ranked alternatives; seeds from the frozen E2 triple in order; no LLM, no adaptivity",
            "published_series": PUBLISHED_SERIES,
            "planned_candidates": plan_candidates(user_goal),
        },
        "runs": rows,
        "angle_distribution": {r["run_id"]: dist_for(r["run_id"]) for r in rows},
        "gates": {
            "source": "docs/research/E2_PROTO_R1.md s.4 (FROZEN)",
            "long_bond_fraction_max": 0.1078,
            "pairs_fraction_v2_min": 0.50,
            "displacement_max_max": 20.0,
            "per_run_status": {r["run_id"]: r["integrity_status"] for r in rows},
        },
        "scoring": scoring,
        "chosen": {
            "run_id": best_row["run_id"] if best_row else None,
            "candidate": best_row["candidate"] if best_row else None,
            "candidate_score": best_row["score"] if best_row else None,
            "published_prior_median_deg": (
                PUBLISHED_SERIES["median_deg"].get(best_row["candidate"]["variant"]) if best_row else None
            ),
        },
        "revalidation": reval_block,
        "confidence": {
            "note": "frames-based bootstrap CI95 for the median of valid frames (10000 resamples, seed 424242, E2_PROTO_R1 s.6 method)",
            "revalidation": reval_block["distribution"] if reval_block else None,
        },
        "provenance": dict(provenance),
        "limitations": [
            "discrete candidate space: 4 published variants only (74b NOT_MEASURED — arm-manifest derivation BLOCKED)",
            "coarse-grained oxDNA model (DNA2), no claim of physical manufacturability",
            "angle convention R1: [0,180] deg PCA-axes unsigned; erratum E2_PROTO_R1 s.2.5 (no theta <-> 180-theta folding)",
            "budget: %d candidates x %d steps + %d revalidation run(s); no finer parameter search"
            % (user_goal["max_simulations"], user_goal["steps"], user_goal["revalidation_runs"]),
            "final claimed score is the re-validation score on ONE fresh seed (anti-bias rule NL4-002)",
        ],
        "reproduction": {
            "goal_file": provenance.get("goal_file"),
            "command": (
                "python scripts/nl4/mvp.py --goal <user-goal.json> --out-dir <evidence-dir> "
                "(from a fresh clone of commit %s; proxy env required for digest-gated source download)"
                % provenance.get("repo_commit")
            ),
            "goal_json": dict(user_goal),
        },
        "verdict": verdict,
    }


def render_markdown(report: dict) -> str:
    """Human-facing mvp-report.md (Russian, card style)."""
    g = report["goal"]
    lines = []
    lines.append("# MVP-отчёт NL4 (EX-NL4-003-R1)")
    lines.append("")
    lines.append("Статус: measured-only clean-room прогон (claim C0_SOFTWARE_ONLY).")
    lines.append("")
    lines.append("## Цель (goal)")
    lines.append("")
    lines.append(
        "- target_angle = %g°; max_simulations = %d; steps = %d; revalidation_runs = %d"
        % (g["target_angle"], g["max_simulations"], g["steps"], g["revalidation_runs"])
    )
    lines.append("- Стратегия: %s (детерминированная, без LLM)" % report["strategy"]["name"])
    lines.append(
        "- Published-prior: %s" % report["strategy"]["published_series"]["source"]
    )
    lines.append("")
    lines.append("## Раны (кандидаты)")
    lines.append("")
    lines.append("| RUN_ID | variant/seed/steps | median° | score | валидность | wall, с | digest |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in report["runs"]:
        lines.append(
            "| %s | %s/%s/%s | %s | %s | %s | %s | `%s` |"
            % (
                r["run_id"],
                r["candidate"]["variant"],
                r["candidate"]["seed"],
                r["candidate"]["steps"],
                "%.2f" % r["median_angle_deg"] if r["median_angle_deg"] is not None else "—",
                "%.3f" % r["score"] if r["score"] is not None else "—",
                r["integrity_status"],
                r["wall_seconds"],
                r["input_digest_sha256"][:12],
            )
        )
    lines.append("")
    dist = report["angle_distribution"]
    lines.append("## Распределение угла (валидные кадры, observables v2 mutual)")
    lines.append("")
    lines.append("| RUN_ID | кадров (валид/всего) | min° | median° | max° | CI95 median |")
    lines.append("|---|---|---|---|---|---|")
    ids = [r["run_id"] for r in report["runs"]]
    if report["revalidation"]:
        ids.append(report["revalidation"]["run_id"])
    for run_id in ids:
        d = dist.get(run_id) or (report["revalidation"] or {}).get("distribution")
        if d is None:
            continue
        ci = d.get("bootstrap_ci95_median")
        lines.append(
            "| %s | %s/%s | %s | %s | %s | %s |"
            % (
                run_id,
                d.get("n_frames_valid"),
                d.get("n_frames_total"),
                "%.2f" % d["min_deg"] if d.get("min_deg") is not None else "—",
                "%.2f" % d["median_deg"] if d.get("median_deg") is not None else "—",
                "%.2f" % d["max_deg"] if d.get("max_deg") is not None else "—",
                "[%.2f, %.2f]" % tuple(ci) if ci else "—",
            )
        )
    lines.append("")
    lines.append("## Гейты")
    lines.append("")
    lines.append(
        "- E2_PROTO_R1 §4 (frozen): lbf ≤ 0.1078, pf_v2 ≥ 0.50, disp ≤ 20.0; "
        "статусы по ранам: %s" % json.dumps(report["gates"]["per_run_status"], ensure_ascii=False)
    )
    lines.append("")
    chosen = report["chosen"]
    lines.append("## Выбранный кандидат")
    lines.append("")
    if chosen.get("run_id"):
        lines.append(
            "- best = %s (%s, seed %s), candidate score = %.3f (published prior для варианта: %.3f°)"
            % (
                chosen["run_id"],
                chosen["candidate"]["variant"],
                chosen["candidate"]["seed"],
                chosen["candidate_score"],
                chosen["published_prior_median_deg"],
            )
        )
    else:
        lines.append("- ни один ран не прошёл гейты (поиск не удался — поддерживаемый исход)")
    lines.append("")
    lines.append("## Re-validation и финальный score")
    lines.append("")
    rev = report["revalidation"]
    if rev:
        lines.append(
            "- %s: %s, свежий seed %s; median = %.2f°, revalidated score = %.3f (%s)"
            % (
                rev["run_id"],
                rev["candidate"]["variant"],
                rev["candidate"]["seed"],
                rev["median_angle_deg"] if rev["median_angle_deg"] is not None else float("nan"),
                rev["revalidated_score"] if rev["revalidated_score"] is not None else float("nan"),
                rev["integrity_status"],
            )
        )
        lines.append(
            "- Финальный заявляемый score = **%s** (по re-validation; анти-bias правило NL4-002)"
            % (("%.3f" % rev["revalidated_score"]) if rev["revalidated_score"] is not None else "—")
        )
    else:
        lines.append("- re-validation не выполнялся/не валиден")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    v = report["verdict"]
    lines.append(
        "- **%s** (правило: %s; published-best gap = %.3f°)%s"
        % (
            v["verdict"],
            v["rule"],
            v["published_best_gap_deg"],
            ("; причины: " + ", ".join(v["reasons"])) if v["reasons"] else "",
        )
    )
    lines.append(
        '- Формулировка: «ближайший найденный в пространстве %s при бюджете %d×%d шагов, revalidated score %s»'
        % (
            "/".join(PUBLISHED_SERIES["median_deg"]),
            g["max_simulations"],
            g["steps"],
            (("%.3f" % rev["revalidated_score"]) if rev and rev["revalidated_score"] is not None else "—"),
        )
    )
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    for key, value in report["provenance"].items():
        lines.append("- %s: `%s`" % (key, value))
    lines.append("")
    lines.append("## Ограничения (limitations)")
    lines.append("")
    for lim in report["limitations"]:
        lines.append("- %s" % lim)
    lines.append("")
    lines.append("## Воспроизведение")
    lines.append("")
    rep = report["reproduction"]
    lines.append("- goal JSON: `%s`" % json.dumps(rep["goal_json"]))
    lines.append("- команда: `%s`" % rep["command"])
    lines.append("")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------- real engine pipeline
def run_candidates_parallel(adapter: RealExecutorAdapter, candidates: list, run_ids: list) -> list:
    """Real parallel candidate runs with WO-assigned RUN_IDs (E3-MVP-C00X)."""
    preps = []
    for candidate, run_id in zip(candidates, run_ids):
        prep = adapter.prepare_run(candidate, run_id, run_id.lower())
        preps.append((candidate, prep))
        print("[mvp] prepared %s (%s)" % (run_id, canonical_json(candidate)), flush=True)
    launched = []
    for candidate, prep in preps:
        proc, started = adapter.launch(prep["wsl_dir"])
        launched.append((candidate, prep, proc, started))
        print("[mvp] launched %s" % prep["run_id"], flush=True)
    results = [None] * len(launched)
    pending = set(range(len(launched)))
    import time as _time

    while pending:
        for idx in list(pending):
            candidate, prep, proc, started = launched[idx]
            if proc.poll() is not None:
                engine_out = adapter._collect(prep["run_id"], proc, started)
                results[idx] = adapter.analyse_run(candidate, prep, engine_out)
                print(
                    "[mvp] finished %s exit=%s wall=%ss" % (prep["run_id"], engine_out["exit_code"], engine_out["wall_seconds"]),
                    flush=True,
                )
                pending.discard(idx)
            elif _time.perf_counter() - started > adapter.run_wall_cap_s:
                run_id = prep["run_id"]
                import subprocess as _sp

                _sp.run(["wsl", "-e", "bash", "-c", "pkill -f 'runs/%s' || true" % run_id], timeout=120)
                proc.wait()
                engine_out = adapter._collect(run_id, proc, started, interrupted=True)
                results[idx] = adapter.analyse_run(candidate, prep, engine_out)
                print("[mvp] BUDGET-INTERRUPTED %s" % run_id, flush=True)
                pending.discard(idx)
        if pending:
            _time.sleep(20)
    return results


def run_revalidation(adapter: RealExecutorAdapter, best_candidate: dict, rev_seed: int,
                     run_id: str) -> dict:
    """One fresh-seed re-validation run (direct executor path)."""
    candidate = dict(best_candidate)
    candidate["seed"] = rev_seed
    prep = adapter.prepare_run(candidate, run_id, run_id.lower())
    print("[mvp] prepared %s (fresh seed %s)" % (run_id, rev_seed), flush=True)
    proc, started = adapter.launch(prep["wsl_dir"])
    print("[mvp] launched %s" % run_id, flush=True)
    engine_out = adapter.wait(run_id, proc, started)
    result = adapter.analyse_run(candidate, prep, engine_out)
    print(
        "[mvp] finished %s exit=%s wall=%ss" % (run_id, engine_out["exit_code"], engine_out["wall_seconds"]),
        flush=True,
    )
    return result


def load_full_analyses(out_dir: str, run_ids: list) -> dict:
    full = {}
    for run_id in run_ids:
        path = os.path.join(out_dir, run_id, "analysis.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", newline="") as handle:
                full[run_id] = json.load(handle)
    return full


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="nl4-mvp", description=__doc__.splitlines()[0])
    parser.add_argument("--goal", required=True, help="user goal JSON file")
    parser.add_argument("--out-dir", required=True, help="evidence/output directory")
    parser.add_argument("--runs-root", default="/home/yurig/nl4-003-mvp/runs",
                        help="WSL root for run directories (WO-NL4-003)")
    parser.add_argument("--rev-seed", type=int, default=DEFAULT_REVALIDATION_SEED)
    args = parser.parse_args(argv)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    with open(args.goal, "r", encoding="utf-8") as handle:
        user_goal = parse_user_goal(json.load(handle))
    candidates = plan_candidates(user_goal)
    print("[mvp] goal: %s" % canonical_json(user_goal), flush=True)
    print("[mvp] informed-greedy plan: %s" % canonical_json(candidates), flush=True)

    # WSL runs root per WO-NL4-003 (module-level override; frozen toolchain files unchanged)
    re_mod.WSL_RUNS_ROOT = args.runs_root
    run_ids = ["E3-MVP-C%03d" % (i + 1) for i in range(len(candidates))]

    adapter = RealExecutorAdapter(repo_root, out_dir, run_prefix="E3-MVP")
    adapter.tmp_read_dir = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "nl4-003-mvp-read")

    # --- candidate phase: real parallel runs + canonical Controller replay
    results = run_candidates_parallel(adapter, candidates, run_ids)
    replay = ReplayExecutor(results)
    controller = Controller(controller_goal(user_goal), replay, allowlist=load_allowlist())
    agent = InformedGreedyAgent(candidates)
    controller_report = controller.run(agent)
    scoring = score_session(controller_report)
    print("[mvp] scoring: %s" % canonical_json(scoring), flush=True)

    # --- re-validation of best (fresh seed, direct executor path)
    revalidation = None
    best = scoring.get("best")
    rev_run_id = "E3-MVP-REV001"
    if best is not None and user_goal["revalidation_runs"] >= 1:
        best_candidate = None
        for run in controller_report["runs"]:
            if run["run_id"] == best["run_id"]:
                best_candidate = dict(run["candidate"])
        revalidation = run_revalidation(adapter, best_candidate, args.rev_seed, rev_run_id)
    else:
        print("[mvp] no valid best -> re-validation skipped (NOT_FOUND path)", flush=True)

    all_run_ids = run_ids + ([rev_run_id] if revalidation else [])
    full_analyses = load_full_analyses(out_dir, all_run_ids)

    import subprocess

    repo_commit = subprocess.run(
        ["git", "-C", repo_root, "rev-parse", "HEAD"], capture_output=True, text=True
    ).stdout.strip()

    provenance = {
        "repo": "rootfabric/NanoLab",
        "repo_commit": repo_commit,
        "goal_file": os.path.abspath(args.goal),
        "engine": ENGINE,
        "engine_source_commit": ENGINE_SOURCE_COMMIT,
        "allowlist_revision": load_allowlist()["revision"],
        "observables": "scripts/e2/observables.py v2 mutual-nearest (frozen)",
        "arm_manifests": "frozen per-variant (EX-NL3-002 arm-manifest-v1)",
        "runs_root": args.runs_root,
        "revalidation_seed": args.rev_seed,
        "input_digests": {
            r["run_id"]: r["input_digest_sha256"] for r in results
        } | ({rev_run_id: revalidation["input_digest_sha256"]} if revalidation else {}),
    }
    report = build_report(user_goal, controller_report, revalidation, full_analyses, provenance)

    json_path = os.path.join(out_dir, "mvp-report.json")
    md_path = os.path.join(out_dir, "mvp-report.md")
    with open(json_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json(report) + "\n")
    with open(md_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_markdown(report))
    with open(os.path.join(out_dir, "mvp-session-report.json"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json(controller_report) + "\n")
    print("[mvp] verdict: %s" % report["verdict"]["verdict"], flush=True)
    print("[mvp] wrote %s and %s" % (json_path, md_path), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
