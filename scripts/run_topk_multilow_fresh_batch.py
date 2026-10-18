#!/usr/bin/env python3
"""Paired fresh-batch audit of the multi-low-capacity population theorem.

Run from the repository root:
    python scripts/run_topk_multilow_fresh_batch.py

Unlike the parent static-plant experiment, a new iid Gumbel batch is sampled
at every update. At each round the same batch is shared by R/A/no-update arms.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import t as student_t

from run_topk_multilow_population_overflow import (
    ETA,
    FAMILIES,
    HORIZONS,
    T_VALUES,
    capacities,
    gumbel_high_inclusion,
    population_prediction,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "topk_multilow_fresh_batch"
REPLICATES = 12
BASE_SEED = 20261018


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gumbel_batch(rng: np.random.Generator, T: int, E: int) -> np.ndarray:
    u = rng.random((T, E), dtype=np.float64)
    u = np.clip(u, np.finfo(np.float64).tiny, 1.0 - np.finfo(np.float64).eps)
    return -np.log(-np.log(u))


def request_counts(affinity: np.ndarray, q: np.ndarray, K: int) -> tuple[np.ndarray, bool]:
    """Return counts; detect and deterministically resolve cutoff ties."""
    scores = affinity - q[None, :]
    E = scores.shape[1]
    split = E - K
    partitioned = np.argpartition(scores, split, axis=1)
    selected = partitioned[:, split:]
    selected_floor = np.min(np.take_along_axis(scores, selected, axis=1), axis=1)
    if split:
        unselected = partitioned[:, :split]
        unselected_ceil = np.max(np.take_along_axis(scores, unselected, axis=1), axis=1)
        tied = selected_floor == unselected_ceil
    else:
        tied = np.zeros(scores.shape[0], dtype=bool)
    if np.any(tied):
        # Stable descending sort makes lower expert indices win exact ties.
        rows = np.flatnonzero(tied)
        selected[tied] = np.argsort(-scores[tied], axis=1, kind="stable")[:, :K]
    counts = np.bincount(selected.reshape(-1), minlength=E).astype(np.int64)
    return counts, bool(np.any(tied))


def run_replicate(E: int, K: int, m: int, T: int, replicate: int, seed: int,
                  C: np.ndarray) -> tuple[list[dict], list[dict], dict]:
    rng = np.random.default_rng(seed)
    arms = ("requested", "admitted", "none")
    q = {arm: np.zeros(E, dtype=np.float64) for arm in arms}
    cumulative = {arm: 0 for arm in arms}
    step_rows: list[dict] = []
    checkpoint_rows: list[dict] = []
    tie_count = 0
    horizon_set = set(HORIZONS)

    for step in range(1, max(HORIZONS) + 1):
        affinity = gumbel_batch(rng, T, E)
        observed: dict[str, tuple[np.ndarray, np.ndarray, int]] = {}
        for arm in arms:
            R, had_tie = request_counts(affinity, q[arm], K)
            tie_count += int(had_tie)
            A = np.minimum(R, C)
            overflow = int(np.maximum(R - C, 0).sum())
            if int(R.sum()) != K * T:
                raise AssertionError("request mass was not conserved")
            if not np.array_equal(A, np.minimum(R, C)):
                raise AssertionError("admission did not equal coordinate clipping")
            if overflow != K * T - int(A.sum()):
                raise AssertionError("overflow identity failed")
            observed[arm] = (R, A, overflow)
            cumulative[arm] += overflow
            step_rows.append({
                "E": E, "K": K, "m_low": m, "T": T,
                "replicate": replicate, "seed": seed,
                "step": step, "arm": arm,
                "R": json.dumps(R.tolist(), separators=(",", ":")),
                "A": json.dumps(A.tolist(), separators=(",", ":")),
                "overflow": overflow,
                "overflow_per_token": overflow / T,
                "high_minus_low_pressure": float(q[arm][m:].mean() - q[arm][:m].mean()),
                "cutoff_tie_resolved": had_tie,
            })

        if step in horizon_set:
            for arm in arms:
                checkpoint_rows.append({
                    "E": E, "K": K, "m_low": m, "T": T,
                    "replicate": replicate, "seed": seed,
                    "H": step, "arm": arm,
                    "cumulative_overflow_per_token": cumulative[arm] / T,
                    "high_minus_low_pressure": float(q[arm][m:].mean() - q[arm][:m].mean()),
                })

        for arm in arms:
            R, A, _ = observed[arm]
            signal = R if arm == "requested" else A if arm == "admitted" else None
            if signal is not None:
                q[arm] = q[arm] + ETA * (signal.astype(np.float64) / (K * T) - 1.0 / E)
                q[arm] -= q[arm].mean()

    return step_rows, checkpoint_rows, {"cutoff_ties": tie_count}


def mean_ci(values: np.ndarray) -> tuple[float, float, float]:
    mean = float(values.mean())
    if len(values) < 2:
        return mean, mean, mean
    half = float(student_t.ppf(0.975, len(values) - 1) * values.std(ddof=1) / math.sqrt(len(values)))
    return mean, mean - half, mean + half


def audit_no_clipping() -> bool:
    E, K, m, T = 6, 2, 2, 96
    C = np.full(E, T, dtype=np.int64)
    rng = np.random.default_rng(BASE_SEED + 987654)
    q_r = np.zeros(E, dtype=np.float64)
    q_a = np.zeros(E, dtype=np.float64)
    for _ in range(8):
        affinity = gumbel_batch(rng, T, E)
        Rr, _ = request_counts(affinity, q_r, K)
        Ra, _ = request_counts(affinity, q_a, K)
        Ar, Aa = np.minimum(Rr, C), np.minimum(Ra, C)
        if not np.array_equal(Rr, Ar) or not np.array_equal(Ra, Aa):
            return False
        q_r = q_r + ETA * (Rr.astype(np.float64) / (K * T) - 1.0 / E)
        q_a = q_a + ETA * (Aa.astype(np.float64) / (K * T) - 1.0 / E)
        q_r -= q_r.mean()
        q_a -= q_a.mean()
        if not np.array_equal(q_r, q_a):
            return False
    return True


def audit_tie_rule() -> bool:
    # Expert 0 and 1 tie at the top; lower index must receive the Top-1 route.
    counts, had_tie = request_counts(np.array([[2.0, 2.0, 1.0, 0.0]]),
                                     np.zeros(4, dtype=np.float64), 1)
    return had_tie and np.array_equal(counts, np.array([1, 0, 0, 0], dtype=np.int64))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    step_rows: list[dict] = []
    checkpoint_rows: list[dict] = []
    checks = {
        "registered_capacities_exact_total": True,
        "population_response_and_root_checks": True,
        "mass_clipping_and_overflow_invariants": True,
        "no_clipping_fresh_batch_paths_equal": audit_no_clipping(),
        "lower_index_cutoff_tie_control": audit_tie_rule(),
    }
    family_index = {family: i for i, family in enumerate(FAMILIES)}
    total_cutoff_ties = 0

    for E, K, m in FAMILIES:
        p = K / E
        r = 1.0 / (4.0 * E)
        c_low = p - r
        x_values, gap_values, x_star = population_prediction(E, K, m, c_low, max(HORIZONS))
        grid = np.linspace(0.0, x_star, 501)
        h_grid = np.array([gumbel_high_inclusion(E, K, m, float(x)) for x in grid])
        if (not np.all(np.diff(h_grid) < 0.0)
                or abs(gumbel_high_inclusion(E, K, m, x_star) - c_low) > 2e-12
                or abs(gap_values[0]) > 1e-12
                or any(v <= 0.0 for v in gap_values[1:])):
            checks["population_response_and_root_checks"] = False

        fi = family_index[(E, K, m)]
        for t_index, T in enumerate(T_VALUES):
            C, _, c_low_actual, _ = capacities(E, K, m, T)
            if int(C.sum()) != K * T:
                checks["registered_capacities_exact_total"] = False
            for replicate in range(REPLICATES):
                seed = BASE_SEED + 100000 * fi + 1000 * t_index + replicate
                local_steps, local_checkpoints, diagnostics = run_replicate(
                    E, K, m, T, replicate, seed, C
                )
                step_rows.extend(local_steps)
                checkpoint_rows.extend(local_checkpoints)
                if diagnostics["cutoff_ties"]:
                    total_cutoff_ties += diagnostics["cutoff_ties"]
                for row in local_checkpoints:
                    if row["arm"] == "admitted":
                        continue
                    # Additional checks are performed from the paired join below.
                    if row["arm"] == "none" and row["H"] == 1 and row["cumulative_overflow_per_token"] < 0:
                        checks["mass_clipping_and_overflow_invariants"] = False

    # One step-level row per arm/replicate is retained for independent replay.
    # Pair admitted and requested cumulative values only after preserving all arms.
    checkpoints_path = OUT / "replicate_horizons.csv"
    with checkpoints_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(checkpoint_rows[0]))
        writer.writeheader()
        writer.writerows(checkpoint_rows)
    steps_path = OUT / "step_trajectories.csv"
    with steps_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(step_rows[0]))
        writer.writeheader()
        writer.writerows(step_rows)

    by_key: dict[tuple[int, int, int, int, int, int], dict[str, dict]] = {}
    for row in checkpoint_rows:
        key = (row["E"], row["K"], row["m_low"], row["T"], row["replicate"], row["H"])
        by_key.setdefault(key, {})[row["arm"]] = row
    paired_rows = []
    for key, arms in sorted(by_key.items()):
        E, K, m, T, replicate, H = key
        if set(arms) != {"requested", "admitted", "none"}:
            raise AssertionError("missing arm at checkpoint")
        _, population_gaps, _ = population_prediction(
            E, K, m, K / E - 1.0 / (4.0 * E), H
        )
        paired_rows.append({
            "E": E, "K": K, "m_low": m, "T": T,
            "replicate": replicate, "seed": arms["admitted"]["seed"], "H": H,
            "overflow_requested_per_token": arms["requested"]["cumulative_overflow_per_token"],
            "overflow_admitted_per_token": arms["admitted"]["cumulative_overflow_per_token"],
            "overflow_none_per_token": arms["none"]["cumulative_overflow_per_token"],
            "paired_admitted_minus_requested": (
                arms["admitted"]["cumulative_overflow_per_token"]
                - arms["requested"]["cumulative_overflow_per_token"]
            ),
            "population_predicted_gap": float(sum(population_gaps)),
            "admitted_high_minus_low_pressure": arms["admitted"]["high_minus_low_pressure"],
        })
    paired_path = OUT / "paired_horizons.csv"
    with paired_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(paired_rows[0]))
        writer.writeheader()
        writer.writerows(paired_rows)

    cell_rows = []
    grouped: dict[tuple[int, int, int, int, int], list[dict]] = {}
    for row in paired_rows:
        grouped.setdefault((row["E"], row["K"], row["m_low"], row["T"], row["H"]), []).append(row)
    for key, rows in sorted(grouped.items()):
        E, K, m, T, H = key
        gaps = np.array([r["paired_admitted_minus_requested"] for r in rows], dtype=np.float64)
        mean, lo, hi = mean_ci(gaps)
        pred = float(rows[0]["population_predicted_gap"])
        cell_rows.append({
            "E": E, "K": K, "m_low": m, "T": T, "H": H,
            "replicates": len(rows), "mean_paired_gap": mean,
            "ci95_low": lo, "ci95_high": hi,
            "population_prediction": pred, "mean_minus_population": mean - pred,
            "positive_replicates": int(np.sum(gaps > 0.0)),
        })

    summary_path = OUT / "summary.json"
    source_path = Path(__file__).resolve()
    parent_path = ROOT / "scripts" / "run_topk_multilow_population_overflow.py"
    protocol_path = ROOT / "docs" / "paper" / "topk_multilow_fresh_batch_protocol_2026-10-18.md"
    summary = {
        "experiment": "paired fresh-batch finite-horizon check of the multi-low-capacity Top-K population theorem",
        "families": [list(x) for x in FAMILIES], "T_values": list(T_VALUES),
        "replicates_per_cell": REPLICATES, "horizons": list(HORIZONS),
        "eta": ETA, "seed_base": BASE_SEED,
        "steps_rows": len(step_rows), "replicate_horizon_rows": len(checkpoint_rows),
        "paired_horizon_rows": len(paired_rows), "cell_count": len(cell_rows),
        "registered_cutoff_tie_rows_resolved": total_cutoff_ties,
        "checks": checks, "cells": cell_rows,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "runner_sha256": sha256(source_path),
        "parent_runner_sha256": sha256(parent_path),
        "protocol_sha256": sha256(protocol_path),
        "step_trajectories_sha256": sha256(steps_path),
        "replicate_horizons_sha256": sha256(checkpoints_path),
        "paired_horizons_sha256": sha256(paired_path),
    }
    if not all(checks.values()):
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        raise AssertionError(f"registered checks failed: {checks}")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "cells"}, indent=2))
    print(json.dumps({"cells": cell_rows}, indent=2))


if __name__ == "__main__":
    main()
