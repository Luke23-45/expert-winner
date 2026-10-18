#!/usr/bin/env python3
"""Exact grid audit for the signed-bias balanced-request cost corollary.

The locked plants are cyclic Top-K affinity matrices with T=2E rows. Each
expert is requested exactly 2K times. The first K experts have capacity 1;
the remaining experts have capacity 2K. This gives aggregate shortage and a
strict +1/-1 admitted-feedback slope split at the Top-K boundary. Every
calculation, including biases and the finite-exit bound, uses Fraction.
"""

from __future__ import annotations

import csv
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "signed_bias_balanced_cost_2026-10-18"
EXPERT_COUNTS = (3, 4, 5, 6, 8)
GAMMAS = (Fraction(1, 1000), Fraction(1, 16), Fraction(1, 4))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def plant(e: int, k: int) -> list[list[int]]:
    """Two copies of all E cyclic windows of K consecutive experts."""
    rows: list[list[int]] = []
    for _ in range(2):
        for start in range(e):
            selected = {(start + offset) % e for offset in range(k)}
            rows.append([int(i in selected) for i in range(e)])
    return rows


def route_counts(affinities: list[list[int]], bias: list[Fraction], k: int) -> list[int]:
    counts = [0] * len(bias)
    for row in affinities:
        chosen = sorted(range(len(bias)), key=lambda i: (-(Fraction(row[i]) + bias[i]), i))[:k]
        for i in chosen:
            counts[i] += 1
    return counts


def sign_feedback(load: list[int]) -> list[int]:
    mean = Fraction(sum(load), len(load))
    return [(mean > x) - (mean < x) for x in load]


def exit_bound(affinities: list[list[int]], u: list[int], gamma: Fraction) -> int:
    e = len(u)
    k = sum(1 for value in u if value == max(u))
    # The grid has exactly K high-slope coordinates and a strict slope gap.
    if not (0 < k < e and min(u[:k]) > max(u[k:])):
        raise AssertionError("expected +1/-1 slope split at the Top-K cut")
    n = 0
    for row in affinities:
        for i in range(k):
            for j in range(k, e):
                numerator = Fraction(row[j] - row[i])
                denominator = gamma * (u[i] - u[j])
                n = max(n, numerator // denominator + 1)
    return max(0, n)


def audit_cell(e: int, k: int, gamma: Fraction) -> dict[str, int | str | bool]:
    t = 2 * e
    n = 2 * k
    affinities = plant(e, k)
    initial = route_counts(affinities, [Fraction(0)] * e, k)
    if initial != [n] * e:
        raise AssertionError(f"initial counts not balanced for E={e},K={k}: {initial}")

    capacities = [1 if i < k else n for i in range(e)]
    total_capacity = sum(capacities)
    shortage = k * t - total_capacity
    if not (all(0 < c <= n for c in capacities) and shortage > 0):
        raise AssertionError("capacity feasibility/shortage condition failed")
    u = sign_feedback(capacities)
    if u != [1] * k + [-1] * (e - k):
        raise AssertionError(f"strict slope condition failed: {u}")

    bound = exit_bound(affinities, u, gamma)
    bias = [Fraction(0)] * e
    tau = None
    cumulative_admitted = 0
    cumulative_requested = 0
    state_rows = []
    for state in range(bound + 2):
        requests = route_counts(affinities, bias, k)
        admitted = [min(r, c) for r, c in zip(requests, capacities, strict=True)]
        overflow = sum(max(r - c, 0) for r, c in zip(requests, capacities, strict=True))
        is_saturated = all(r >= c for r, c in zip(requests, capacities, strict=True))
        if overflow - shortage != sum(c - a for c, a in zip(capacities, admitted, strict=True)):
            raise AssertionError("aggregate overflow identity failed")
        if overflow < shortage:
            raise AssertionError("admitted overflow fell below aggregate-shortage floor")
        if not is_saturated and tau is None:
            tau = state
            if overflow <= shortage:
                raise AssertionError("first unsaturated state did not have strict excess overflow")
        cumulative_admitted += overflow
        cumulative_requested += shortage  # requested trajectory is stationary at b=0
        state_rows.append((state, requests, admitted, overflow, is_saturated))
        if state <= bound:
            update = sign_feedback(admitted)
            bias = [b + gamma * u_i for b, u_i in zip(bias, update, strict=True)]

    if tau is None or tau > bound:
        raise AssertionError("the admitted arm did not exit by the claimed bound")
    if cumulative_admitted <= cumulative_requested:
        raise AssertionError("registered horizon did not show strict cumulative gap")
    if state_rows[0][1] != [n] * e or state_rows[0][3] != shortage:
        raise AssertionError("initial admitted-arm condition failed")

    return {
        "E": e,
        "K": k,
        "T": t,
        "gamma": str(gamma),
        "capacity_vector": ",".join(map(str, capacities)),
        "aggregate_shortage_D": shortage,
        "N_sep": bound,
        "actual_first_unsaturated_state_tau": tau,
        "strict_gap_horizon_N_plus_1": bound + 1,
        "admitted_cumulative_overflow_through_N_plus_1": sum(row[3] for row in state_rows[: bound + 1]),
        "requested_cumulative_overflow_through_N_plus_1": shortage * (bound + 1),
        "all_state_overflow_ge_D": True,
        "strict_at_first_unsaturated_state": True,
        "passed": True,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [audit_cell(e, k, gamma)
            for e in EXPERT_COUNTS
            for k in range(1, e)
            for gamma in GAMMAS]
    csv_path = OUT / "cells.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "experiment": "exact signed-bias balanced-request overflow corollary audit",
        "registered_E": list(EXPERT_COUNTS),
        "registered_K": "all integers 1..E-1",
        "registered_gamma": [str(x) for x in GAMMAS],
        "plant": "T=2E; two copies of E cyclic windows of K consecutive experts",
        "capacities": "C_i=1 for i<K; C_i=2K for i>=K",
        "cell_count": len(rows),
        "all_cells_passed": all(bool(row["passed"]) for row in rows),
        "all_exit_bounds_passed": all(int(row["actual_first_unsaturated_state_tau"])
                                       <= int(row["N_sep"]) for row in rows),
        "all_strict_cumulative_gaps_passed": all(
            int(row["admitted_cumulative_overflow_through_N_plus_1"])
            > int(row["requested_cumulative_overflow_through_N_plus_1"])
            for row in rows),
        "max_exit_bound": max(int(row["N_sep"]) for row in rows),
        "max_actual_exit": max(int(row["actual_first_unsaturated_state_tau"]) for row in rows),
        "runner_sha256": digest(Path(__file__)),
        "cells_sha256": digest(csv_path),
        "arithmetic": "exact Python integers and fractions; no Monte Carlo",
        "scope": "deterministic controlled audit of the stated theorem hypotheses; not workload prevalence or measured runtime",
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
