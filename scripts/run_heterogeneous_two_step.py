#!/usr/bin/env python3
"""Run the preregistered exact-grid two-step overflow experiment."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/heterogeneous_capacity_two_step_protocol_2026-10-17.md"
OUT = ROOT / "results/heterogeneous_two_step"
GRID = 1 << 30
TS = (60, 120, 240, 480, 960, 1920)
ETAS = (Fraction(1, 2), Fraction(1), Fraction(2), Fraction(4), Fraction(5))
REPLICATES = 500
T_CRIT_95_DF499 = 1.9647


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def counts_at(affinities: np.ndarray, q_num: tuple[int, ...], q_den: int) -> tuple[np.ndarray, int]:
    """Top-1 counts with exact integer comparisons and lower-index ties."""
    scores = affinities.astype(np.int64) * q_den
    if any(q_num):
        scores = scores - np.asarray(q_num, dtype=np.int64)[None, :] * GRID
    maxima = scores.max(axis=1)
    ties = int(np.count_nonzero((scores == maxima[:, None]).sum(axis=1) > 1))
    winners = scores.argmax(axis=1)
    return np.bincount(winners, minlength=3).astype(np.int64), ties


def update_pressure(load: np.ndarray, t: int, eta: Fraction) -> tuple[tuple[int, ...], int]:
    """Compute Pi_g(eta * (load/T - uniform_mu)) as an exact rational."""
    p, q = eta.numerator, eta.denominator
    nums = p * (3 * load - t)
    den = 3 * q * t
    nums = nums - int(nums.min())
    return tuple(int(x) for x in nums), den


def overflow(requests: np.ndarray, capacities: np.ndarray) -> int:
    return int(np.maximum(requests - capacities, 0).sum())


def run_arm(
    affinities: np.ndarray,
    t: int,
    capacities: np.ndarray,
    initial_requests: np.ndarray,
    initial_ties: int,
    eta: Fraction,
    signal: str,
) -> dict[str, int | list[int]]:
    initial_admitted = np.minimum(initial_requests, capacities)
    initial_overflow = overflow(initial_requests, capacities)
    if signal == "requested":
        q_num, q_den = update_pressure(initial_requests, t, eta)
    elif signal == "admitted":
        q_num, q_den = update_pressure(initial_admitted, t, eta)
    elif signal == "none":
        q_num, q_den = (0, 0, 0), 1
    else:
        raise ValueError(signal)
    second_requests, second_ties = counts_at(affinities, q_num, q_den)
    second_admitted = np.minimum(second_requests, capacities)
    second_overflow = overflow(second_requests, capacities)
    return {
        "r0": initial_requests.tolist(),
        "a0": initial_admitted.tolist(),
        "j0": initial_overflow,
        "r1": second_requests.tolist(),
        "a1": second_admitted.tolist(),
        "j1": second_overflow,
        "tie0": initial_ties,
        "tie1": second_ties,
        "q1_num": list(q_num),
        "q1_den": q_den,
    }


def limit(eta: Fraction) -> float:
    d = float(eta / 6)
    return d - d**3 / 3


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, int | float | str]] = []
    summary_cells: list[dict[str, int | float | str]] = []
    no_clip_checks = 0

    for t in TS:
        capacities = np.asarray((t // 6, t // 2, t // 3), dtype=np.int64)
        no_clip_capacities = np.full(3, t, dtype=np.int64)
        for replicate in range(REPLICATES):
            seed = 20261019 + 100000 * t + replicate
            rng = np.random.default_rng(seed)
            affinities = rng.integers(0, GRID + 1, size=(t, 3), dtype=np.int64)
            initial_requests, initial_ties = counts_at(affinities, (0, 0, 0), 1)
            if int(initial_requests.sum()) != t:
                raise AssertionError("Top-1 mass conservation failed at step zero")

            for eta in ETAS:
                arms = {
                    signal: run_arm(affinities, t, capacities, initial_requests, initial_ties, eta, signal)
                    for signal in ("requested", "admitted", "none")
                }
                for name, result in arms.items():
                    for step in (0, 1):
                        r = np.asarray(result[f"r{step}"], dtype=np.int64)
                        a = np.asarray(result[f"a{step}"], dtype=np.int64)
                        j = int(result[f"j{step}"])
                        if int(r.sum()) != t:
                            raise AssertionError(f"mass conservation failed: {t=} {replicate=} {eta=} {name=} {step=}")
                        if not np.array_equal(a, np.minimum(r, capacities)):
                            raise AssertionError("canonical clipping identity failed")
                        if j != int((r - a).sum()):
                            raise AssertionError("overflow accounting failed")
                if len({int(arms[s]["j0"]) for s in arms}) != 1:
                    raise AssertionError("paired arms must share step-zero overflow")

                no_clip_r = run_arm(affinities, t, no_clip_capacities, initial_requests, initial_ties, eta, "requested")
                no_clip_a = run_arm(affinities, t, no_clip_capacities, initial_requests, initial_ties, eta, "admitted")
                if no_clip_r["j0"] or no_clip_r["j1"] or no_clip_a["j0"] or no_clip_a["j1"]:
                    raise AssertionError("no-clipping control had overflow")
                if no_clip_r["r1"] != no_clip_a["r1"] or no_clip_r["q1_num"] != no_clip_a["q1_num"]:
                    raise AssertionError("no-clipping R/A trajectories differ")
                no_clip_checks += 1

                total_r = int(arms["requested"]["j0"]) + int(arms["requested"]["j1"])
                total_a = int(arms["admitted"]["j0"]) + int(arms["admitted"]["j1"])
                total_n = int(arms["none"]["j0"]) + int(arms["none"]["j1"])
                paired_gap = (total_a - total_r) / t
                g = limit(eta)
                rows.append({
                    "T": t,
                    "eta": str(eta),
                    "replicate": replicate,
                    "seed": seed,
                    "r0_e0": int(initial_requests[0]),
                    "r0_e1": int(initial_requests[1]),
                    "r0_e2": int(initial_requests[2]),
                    "a0_e0": int(arms["admitted"]["a0"][0]),
                    "a0_e1": int(arms["admitted"]["a0"][1]),
                    "a0_e2": int(arms["admitted"]["a0"][2]),
                    "requested_overflow_2step": total_r,
                    "admitted_overflow_2step": total_a,
                    "no_feedback_overflow_2step": total_n,
                    "gap_normalized": paired_gap,
                    "theory_limit": g,
                    "abs_error_to_limit": abs(paired_gap - g),
                    "tie_tokens_step0": initial_ties,
                    "tie_tokens_R_step1": int(arms["requested"]["tie1"]),
                    "tie_tokens_A_step1": int(arms["admitted"]["tie1"]),
                    "tie_tokens_none_step1": int(arms["none"]["tie1"]),
                    "R_q1_num": ";".join(map(str, arms["requested"]["q1_num"])),
                    "R_q1_den": int(arms["requested"]["q1_den"]),
                    "A_q1_num": ";".join(map(str, arms["admitted"]["q1_num"])),
                    "A_q1_den": int(arms["admitted"]["q1_den"]),
                })

        for eta in ETAS:
            cell = [r for r in rows if r["T"] == t and r["eta"] == str(eta)]
            gaps = np.asarray([float(r["gap_normalized"]) for r in cell], dtype=np.float64)
            se = float(gaps.std(ddof=1) / math.sqrt(len(gaps)))
            mean = float(gaps.mean())
            summary_cells.append({
                "T": t,
                "eta": str(eta),
                "n": len(cell),
                "mean_normalized_overflow_gap_A_minus_R": mean,
                "sample_sd": float(gaps.std(ddof=1)),
                "standard_error": se,
                "ci95_t_low": mean - T_CRIT_95_DF499 * se,
                "ci95_t_high": mean + T_CRIT_95_DF499 * se,
                "theory_limit": limit(eta),
                "absolute_mean_error_to_limit": abs(mean - limit(eta)),
                "fraction_positive_paired_gap": float(np.mean(gaps > 0)),
                "fraction_equal_paired_gap": float(np.mean(gaps == 0)),
                "mean_requested_overflow_per_T": float(np.mean([r["requested_overflow_2step"] for r in cell]) / t),
                "mean_admitted_overflow_per_T": float(np.mean([r["admitted_overflow_2step"] for r in cell]) / t),
                "mean_no_feedback_overflow_per_T": float(np.mean([r["no_feedback_overflow_2step"] for r in cell]) / t),
                "mean_tied_tokens_all_routing_calls": float(np.mean([
                    int(r["tie_tokens_step0"]) + int(r["tie_tokens_R_step1"]) + int(r["tie_tokens_A_step1"]) + int(r["tie_tokens_none_step1"])
                    for r in cell
                ])),
            })

    csv_path = OUT / "plants.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha256(PROTOCOL),
        "script_sha256": sha256(Path(__file__)),
        "affinity_grid_max": GRID,
        "replicates_per_T": REPLICATES,
        "no_clipping_checks": no_clip_checks,
        "all_invariants_passed": True,
        "confidence_interval": "mean +/- t_(0.975,499) * standard error; t critical rounded to 1.9647",
        "cells": summary_cells,
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "rows": len(rows),
        "summary": str(summary_path),
        "summary_sha256": sha256(summary_path),
        "plants_sha256": sha256(csv_path),
        "protocol_sha256": summary["protocol_sha256"],
        "script_sha256": summary["script_sha256"],
        "all_invariants_passed": True,
    }, indent=2))


if __name__ == "__main__":
    main()
