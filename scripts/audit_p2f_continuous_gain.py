#!/usr/bin/env python3
"""Exact piecewise-constant gain audit for the existing P2f Top-2 family.

The audit partitions alpha in (1/5, 11/40) at every pairwise score crossing
encountered by the closed loop. Each resulting open interval has one exact
route trajectory; all isolated crossing gains are simulated with the stated
Top-2 tie rule. This is exploratory research code, not a general theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "run_top2_signed_bias_separation.py"
OUT = ROOT / "results" / "top2_signed_bias_separation" / "continuous_gain_audit.json"
GAIN_LO = F(1, 5)
GAIN_HI = F(11, 40)
MAX_STEPS = 5000
MAX_BRANCHES = 20000


def centered(values: tuple[F, ...]) -> tuple[F, ...]:
    mean = sum(values, F(0)) / len(values)
    return tuple(x - mean for x in values)


def omitted_expert(scores: tuple[F, ...]) -> int:
    # Top-2 among three experts; lower index wins a score tie, so the higher
    # index is omitted when the two lowest scores tie.
    return min(range(3), key=lambda e: (scores[e], -e))


def roots_inside(lo: F, hi: F, z: tuple[F, ...], rows: tuple[tuple[F, ...], ...]) -> list[F]:
    roots: set[F] = set()
    for row in rows:
        for i in range(3):
            for j in range(i + 1, 3):
                dz = z[i] - z[j]
                if dz:
                    root = (row[j] - row[i]) / dz
                    if lo < root < hi:
                        roots.add(root)
    return sorted(roots)


def route_counts(alpha: F, z: tuple[F, ...], rows: tuple[tuple[F, ...], ...]) -> tuple[int, int, int]:
    omitted = [omitted_expert(tuple(rows_t[e] + alpha * z[e] for e in range(3))) for rows_t in rows]
    return tuple(sum(x != e for x in omitted) for e in range(3))


def sign_feedback(signal: str, requested: tuple[int, ...], capacity: int) -> tuple[int, ...]:
    if signal == "none":
        return (0, 0, 0)
    observed = requested if signal == "requested" else tuple(min(x, capacity) for x in requested)
    total = sum(observed)
    return tuple((total > 3 * x) - (total < 3 * x) for x in observed)


def step(alpha: F, z: tuple[F, ...], rows: tuple[tuple[F, ...], ...], capacity: int, signal: str):
    req = route_counts(alpha, z, rows)
    adm = tuple(min(x, capacity) for x in req)
    overflow = sum(req) - sum(adm)
    u = sign_feedback(signal, req, capacity)
    z_next = centered(tuple(z[e] + u[e] for e in range(3)))
    return req, overflow, z_next


def simulate_point(alpha: F, rows: tuple[tuple[F, ...], ...], capacity: int, signal: str) -> dict:
    z = (F(0), F(0), F(0))
    seen: dict[tuple[F, ...], int] = {}
    costs: list[int] = []
    for t in range(MAX_STEPS):
        if z in seen:
            start = seen[z]
            cycle = costs[start:]
            return {
                "alpha": str(alpha),
                "cycle_start": start,
                "cycle_period": len(cycle),
                "cycle_cost": cycle,
                "cycle_mean_overflow": str(F(sum(cycle), len(cycle))),
                "all_horizons_certified": True,
            }
        seen[z] = t
        _, cost, z = step(alpha, z, rows, capacity, signal)
        costs.append(cost)
    raise RuntimeError(f"point trajectory did not cycle within {MAX_STEPS}: alpha={alpha}")


def audit_open_intervals(rows: tuple[tuple[F, ...], ...], capacity: int, signal: str):
    # Each work item is one open alpha interval plus its exact state-history
    # certificate. Intervals are never merged across score-crossing roots.
    pending = deque([(GAIN_LO, GAIN_HI, (F(0), F(0), F(0)), {}, [])])
    leaves: list[dict] = []
    roots: set[F] = set()
    branches = 0
    max_preperiod = 0
    max_period = 0
    while pending:
        lo, hi, z, seen, costs = pending.popleft()
        branches += 1
        if branches > MAX_BRANCHES:
            raise RuntimeError(f"branch cap {MAX_BRANCHES} exceeded")
        # The interval's score ordering is constant unless a pairwise root is
        # inside. Split first, preserving the crossing itself for point audit.
        cuts = roots_inside(lo, hi, z, rows)
        if cuts:
            roots.update(cuts)
            bounds = [lo, *cuts, hi]
            for left, right in zip(bounds, bounds[1:]):
                pending.append((left, right, z, dict(seen), list(costs)))
            continue
        if z in seen:
            start = seen[z]
            cycle = costs[start:]
            leaves.append({
                "alpha_interval": [str(lo), str(hi)],
                "cycle_start": start,
                "cycle_period": len(cycle),
                "cycle_cost": cycle,
                "cycle_mean_overflow": str(F(sum(cycle), len(cycle))),
            })
            max_preperiod = max(max_preperiod, start)
            max_period = max(max_period, len(cycle))
            continue
        if len(costs) >= MAX_STEPS:
            raise RuntimeError(f"step cap {MAX_STEPS} exceeded on ({lo},{hi})")
        seen[z] = len(costs)
        mid = (lo + hi) / 2
        _, cost, z_next = step(mid, z, rows, capacity, signal)
        pending.append((lo, hi, z_next, seen, [*costs, cost]))
    return leaves, sorted(roots), branches, max_preperiod, max_period


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capacity", type=int, default=11)
    parser.add_argument("--signal", choices=("admitted", "requested", "none"), default="admitted")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    spec = __import__("importlib.util", fromlist=["spec_from_file_location"])
    source_spec = spec.spec_from_file_location("p2f_fixture", SOURCE)
    if source_spec is None or source_spec.loader is None:
        raise RuntimeError(f"cannot load fixture source {SOURCE}")
    fixture = spec.module_from_spec(source_spec)
    source_spec.loader.exec_module(fixture)
    rows = tuple(tuple(F(x) for x in row) for row in fixture.BASE_AFFINITIES)

    leaves, roots, branches, max_pre, max_period = audit_open_intervals(rows, args.capacity, args.signal)
    # Endpoints and all encountered crossing gains are isolated parameter
    # cells, where exact tie-breaking can create a trajectory absent nearby.
    points = [simulate_point(x, rows, args.capacity, args.signal) for x in [GAIN_LO, *roots, GAIN_HI]]
    all_means = [F(x["cycle_mean_overflow"]) for x in leaves + points]
    result = {
        "status": "PASS",
        "model": "existing P2f static E=3,K=2 Top-2 signed-bias model",
        "capacity": args.capacity,
        "signal": args.signal,
        "gain_domain_open": [str(GAIN_LO), str(GAIN_HI)],
        "tie_rule": "Top-2; lower expert index wins exact score ties",
        "arithmetic": "exact fractions.Fraction and integer counts",
        "open_interval_count": len(leaves),
        "encountered_crossing_count": len(roots),
        "explored_branch_count": branches,
        "max_cycle_preperiod": max_pre,
        "max_cycle_period": max_period,
        "eventual_mean_overflow_values": sorted({str(x) for x in all_means}, key=F),
        "open_intervals": leaves,
        "isolated_points": points,
        "fixture_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "audit_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope_note": "Exact continuous-gain result only for this fixed P2f affinity multiset, capacity, feedback signal, and controller.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "status", "capacity", "signal", "open_interval_count",
        "encountered_crossing_count", "explored_branch_count",
        "max_cycle_preperiod", "max_cycle_period", "eventual_mean_overflow_values",
    )}, indent=2))


if __name__ == "__main__":
    main()
