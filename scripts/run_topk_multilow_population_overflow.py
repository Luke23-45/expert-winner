#!/usr/bin/env python3
"""Paired finite-batch audit of the multi-low-capacity Top-K theorem.

Run from the repository root:
    python scripts/run_topk_multilow_population_overflow.py

Population Top-K inclusion probabilities are exact Plackett-Luce dynamic
programs. Finite arms use the same static iid Gumbel batch and the canonical
hard Top-K/per-expert-capacity/proportional-pressure implementation.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "topk_multilow_population_overflow"
FAMILIES = tuple(
    (E, K, m)
    for E in (4, 6)
    for K in range(1, E)
    for m in range(1, E)
    if 1.0 / (4 * E) < min(
        K / E - max(K - m, 0) / (E - m),
        (1.0 - K / E) * (E - m) / m,
    )
)
T_VALUES = (1440, 2880, 5760)
REPLICATES = 12
HORIZONS = (1, 2, 4, 8, 16, 32)
ETA = 0.5
BASE_SEED = 20261017


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gumbel_high_inclusion(E: int, K: int, m: int, x: float) -> float:
    """Exact PL-DP inclusion probability of one high-group expert."""
    if x == 0.0:
        return K / E
    n_high = E - m
    high_weight = math.exp(-x)
    # dp[l,h] is probability that the first l+h ranks contain l low and h high.
    dp = np.zeros((m + 1, n_high + 1), dtype=np.float64)
    dp[0, 0] = 1.0
    for depth in range(K):
        next_dp = np.zeros_like(dp)
        for low_used in range(min(m, depth) + 1):
            high_used = depth - low_used
            if high_used < 0 or high_used > n_high:
                continue
            mass = dp[low_used, high_used]
            if mass == 0.0:
                continue
            low_left = m - low_used
            high_left = n_high - high_used
            if low_left == 0:
                # Once every low expert has been selected, the remaining
                # high experts are equiprobable even if their common weight
                # underflows to zero at the root-bracketing limit.
                if high_left:
                    next_dp[low_used, high_used + 1] += mass
            elif high_left == 0:
                next_dp[low_used + 1, high_used] += mass
            else:
                denom = low_left + high_left * high_weight
                next_dp[low_used + 1, high_used] += mass * low_left / denom
                next_dp[low_used, high_used + 1] += mass * high_left * high_weight / denom
        dp = next_dp
    expected_high = sum(
        high_used * dp[low_used, high_used]
        for low_used in range(m + 1)
        for high_used in range(n_high + 1)
    )
    return float(expected_high / n_high)


def capacities(E: int, K: int, m: int, T: int) -> tuple[np.ndarray, float, float, float]:
    p = K / E
    r = 1.0 / (4.0 * E)
    c_low = p - r
    c_high = p + m * r / (E - m)
    low = int(round(T * c_low))
    residual = K * T - m * low
    high, rem = divmod(residual, E - m)
    if rem or not math.isclose(low / T, c_low, abs_tol=1e-14):
        raise AssertionError("registered T must yield exact integer capacities")
    if not math.isclose(high / T, c_high, abs_tol=1e-14):
        raise AssertionError("integer high capacity does not match design")
    C = np.array([low] * m + [high] * (E - m), dtype=np.int64)
    if int(C.sum()) != K * T or np.any(C <= 0) or np.any(C >= T):
        raise AssertionError("invalid exact-total capacity profile")
    if not (low < T * p < high):
        raise AssertionError("capacity profile does not straddle mean load")
    return C, r, c_low, c_high


def root_for_response(E: int, K: int, m: int, c_low: float) -> float:
    lo, hi = 0.0, 1.0
    while gumbel_high_inclusion(E, K, m, hi) > c_low:
        hi *= 2.0
        if hi > 1024:
            raise AssertionError("failed to bracket population equilibrium")
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if gumbel_high_inclusion(E, K, m, mid) > c_low:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def population_prediction(E: int, K: int, m: int, c_low: float,
                          horizon: int) -> tuple[list[float], list[float], float]:
    p = K / E
    x_star = root_for_response(E, K, m, c_low)
    x = 0.0
    xs, gaps = [], []
    for _ in range(horizon):
        h = gumbel_high_inclusion(E, K, m, x)
        xs.append(x)
        gaps.append((E - m) * (p - h))
        x += ETA / K * (h - c_low)
    return xs, gaps, x_star


def request_counts(affinity: np.ndarray, q: np.ndarray, K: int) -> np.ndarray:
    scores = affinity - q[None, :]
    selected = np.argpartition(scores, affinity.shape[1] - K, axis=1)[:, -K:]
    return np.bincount(selected.reshape(-1), minlength=affinity.shape[1]).astype(np.int64)


def paired_arm(affinity: np.ndarray, C: np.ndarray, K: int, m: int,
               arm: str, horizons: tuple[int, ...]) -> dict[int, tuple[float, float]]:
    # Same update as one_arm, with the correct known group boundary for the
    # reported high-minus-low pressure separation.
    T, E = affinity.shape
    q = np.zeros(E, dtype=np.float64)
    cumulative = 0
    out: dict[int, tuple[float, float]] = {}
    horizon_set = set(horizons)
    for step in range(1, max(horizons) + 1):
        R = request_counts(affinity, q, K)
        A = np.minimum(R, C)
        overflow = int(np.maximum(R - C, 0).sum())
        if int(R.sum()) != K * T or overflow != K * T - int(A.sum()):
            raise AssertionError("mass/admission/overflow invariant failed")
        cumulative += overflow
        if step in horizon_set:
            out[step] = (cumulative / T, float(q[m:].mean() - q[:m].mean()))
        if arm == "requested":
            signal = R
        elif arm == "admitted":
            signal = A
        elif arm == "none":
            signal = None
        else:
            raise ValueError(arm)
        if signal is not None:
            q = q + ETA * (signal.astype(np.float64) / (K * T) - 1.0 / E)
            q -= q.mean()
    return out


def mean_ci(values: np.ndarray) -> tuple[float, float, float]:
    n = len(values)
    mean = float(np.mean(values))
    if n < 2:
        return mean, mean, mean
    half = float(student_t.ppf(0.975, n - 1) * np.std(values, ddof=1) / math.sqrt(n))
    return mean, mean - half, mean + half


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    checks = {
        "registered_capacities_exact_total": True,
        "gumbel_response_starts_at_K_over_E": True,
        "gumbel_response_strictly_decreases_on_grid": True,
        "population_equilibrium_root_residual_small": True,
        "population_gaps_start_zero_then_positive": True,
        "population_gaps_converge_to_theorem_limit": True,
        "all_finite_batch_mass_and_clipping_invariants": True,
        "no_clipping_feedback_trajectories_equal": True,
    }
    all_by_cell: dict[tuple[int, int, int, int], list[dict]] = {}

    for family_index, (E, K, m) in enumerate(FAMILIES):
        p = K / E
        r = 1.0 / (4.0 * E)
        c_low = p - r
        _, pop_gaps, x_star = population_prediction(E, K, m, c_low, max(HORIZONS))
        grid = np.linspace(0.0, x_star, 501)
        h_grid = np.array([gumbel_high_inclusion(E, K, m, float(x)) for x in grid])
        if not math.isclose(h_grid[0], p, rel_tol=0.0, abs_tol=1e-12):
            checks["gumbel_response_starts_at_K_over_E"] = False
        if not np.all(np.diff(h_grid) < 0.0):
            checks["gumbel_response_strictly_decreases_on_grid"] = False
        if abs(gumbel_high_inclusion(E, K, m, x_star) - c_low) > 2e-12:
            checks["population_equilibrium_root_residual_small"] = False
        if not (abs(pop_gaps[0]) < 1e-12 and all(v > 0 for v in pop_gaps[1:])):
            checks["population_gaps_start_zero_then_positive"] = False
        if abs((E - m) * (p - gumbel_high_inclusion(E, K, m, x_star)) - (E - m) * r) > 2e-12:
            checks["population_gaps_converge_to_theorem_limit"] = False

        for t_index, T in enumerate(T_VALUES):
            C, r_actual, c_low_actual, _ = capacities(E, K, m, T)
            if int(C.sum()) != K * T:
                checks["registered_capacities_exact_total"] = False
            for replicate in range(REPLICATES):
                seed = BASE_SEED + 100000 * family_index + 1000 * t_index + replicate
                rng = np.random.default_rng(seed)
                u = rng.random((T, E), dtype=np.float64)
                u = np.clip(u, np.finfo(np.float64).tiny, 1.0 - np.finfo(np.float64).eps)
                affinity = -np.log(-np.log(u))
                requested = paired_arm(affinity, C, K, m, "requested", HORIZONS)
                admitted = paired_arm(affinity, C, K, m, "admitted", HORIZONS)
                none = paired_arm(affinity, C, K, m, "none", HORIZONS)
                for H in HORIZONS:
                    pred = float(sum(pop_gaps[:H]))
                    row = {
                        "E": E, "K": K, "m_low": m, "T": T,
                        "replicate": replicate, "seed": seed, "H": H,
                        "r": r_actual, "C_low": int(C[0]),
                        "C_high": int(C[-1]),
                        "overflow_requested_per_token": requested[H][0],
                        "overflow_admitted_per_token": admitted[H][0],
                        "overflow_none_per_token": none[H][0],
                        "paired_admitted_minus_requested": admitted[H][0] - requested[H][0],
                        "population_predicted_gap": pred,
                        "admitted_high_minus_low_pressure": admitted[H][1],
                        "population_pressure_separation": float(
                            population_prediction(E, K, m, c_low_actual, H)[0][-1]
                        ),
                        "population_limit_per_round": (E - m) * r_actual,
                    }
                    rows.append(row)
                    all_by_cell.setdefault((E, K, m, T), []).append(row)

    # Independent pathwise negative control under no clipping.
    for E, K, m in FAMILIES:
        T = 96
        affinity = np.random.default_rng(BASE_SEED + E * 100 + K * 10 + m).standard_normal((T, E))
        C = np.full(E, T, dtype=np.int64)
        req = paired_arm(affinity, C, K, m, "requested", HORIZONS[:4])
        adm = paired_arm(affinity, C, K, m, "admitted", HORIZONS[:4])
        if req != adm:
            checks["no_clipping_feedback_trajectories_equal"] = False

    csv_path = OUT / "plant_horizons.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary_cells = []
    for key, cell_rows in sorted(all_by_cell.items()):
        E, K, m, T = key
        for H in HORIZONS:
            here = [row for row in cell_rows if row["H"] == H]
            gaps = np.array([row["paired_admitted_minus_requested"] for row in here])
            pred = float(here[0]["population_predicted_gap"])
            mean, lo, hi = mean_ci(gaps)
            summary_cells.append({
                "E": E, "K": K, "m_low": m, "T": T, "H": H,
                "replicates": len(here), "mean_paired_gap": mean,
                "ci95_low": lo, "ci95_high": hi,
                "population_predicted_gap": pred,
                "mean_minus_population": mean - pred,
                "positive_seed_count": int(np.sum(gaps > 0.0)),
            })
    if not all(checks.values()):
        raise AssertionError(f"one or more registered checks failed: {checks}")

    summary_path = OUT / "summary.json"
    summary = {
        "experiment": "paired finite-batch check of multi-low-capacity Top-K population theorem",
        "families": [list(x) for x in FAMILIES],
        "T_values": list(T_VALUES), "replicates_per_cell": REPLICATES,
        "horizons": list(HORIZONS), "eta": ETA,
        "capacity_margin": "r=1/(4E)",
        "finite_plant_horizon_rows": len(rows),
        "cell_count": len(summary_cells),
        "checks": checks,
        "cells": summary_cells,
        "runner_sha256": sha256(Path(__file__)),
        "plant_horizons_sha256": sha256(csv_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "cells"}, indent=2))
    print(json.dumps({"cells": summary_cells}, indent=2))


if __name__ == "__main__":
    main()
