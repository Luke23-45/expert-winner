#!/usr/bin/env python3
"""Finite-weight E=4,K=2 audit of the sparse two-saturation construction."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "topk_sparse_family_e4_pilot"
CAP = np.array([7 / 8, 1 / 8, 1 / 8, 7 / 8], dtype=np.float64)
CAP_FRAC = (Fraction(7, 8), Fraction(1, 8), Fraction(1, 8), Fraction(7, 8))
WEIGHTS_INT = ((100, 2, 1, 1), (100, 1, 2, 1))
WEIGHTS = tuple(np.array(w, dtype=np.float64) for w in WEIGHTS_INT)
SUBSETS = tuple(itertools.combinations(range(4), 2))
PERMS = tuple(itertools.permutations(range(4)))
SIZES = (1600, 6400, 25600)
REPS = 500


def pl_subset_probs_exact(weights: tuple[int, ...]) -> dict[tuple[int, ...], Fraction]:
    e = len(weights)
    out = {s: Fraction(0) for s in itertools.combinations(range(e), 2)}
    for perm in PERMS:
        rem = sum(weights)
        prob = Fraction(1)
        for expert in perm:
            prob *= Fraction(weights[expert], rem)
            rem -= weights[expert]
        out[tuple(sorted(perm[:2]))] += prob
    return out


def pl_subset_probs(weights: np.ndarray) -> dict[tuple[int, ...], float]:
    out = {s: 0.0 for s in SUBSETS}
    for perm in PERMS:
        rem = float(weights.sum())
        prob = 1.0
        for expert in perm:
            prob *= float(weights[expert]) / rem
            rem -= float(weights[expert])
        out[tuple(sorted(perm[:2]))] += prob
    return out


def inclusion(weights: np.ndarray) -> np.ndarray:
    probs = pl_subset_probs(weights)
    return np.array([sum(p for s, p in probs.items() if i in s) for i in range(4)])


def exact_inclusion(probs: dict[tuple[int, ...], Fraction]) -> tuple[Fraction, ...]:
    return tuple(sum((p for s, p in probs.items() if i in s), Fraction(0)) for i in range(4))


def solve_target(h: int) -> tuple[np.ndarray, float]:
    def residual(q: np.ndarray) -> np.ndarray:
        w = WEIGHTS[h] * np.exp(-np.r_[q, 0.0])
        return inclusion(w)[:3] - CAP[:3]
    fit = least_squares(residual, np.zeros(3), xtol=1e-14, ftol=1e-14,
                        gtol=1e-14, max_nfev=30000)
    q = np.r_[fit.x, 0.0]
    err = float(np.max(np.abs(inclusion(WEIGHTS[h] * np.exp(-q)) - CAP)))
    if err > 1e-9:
        raise RuntimeError(f"target pressure residual too large: {err}")
    return q, err


def overflow(p: np.ndarray) -> float:
    return float(np.maximum(p - CAP, 0).sum())


def paired_requests(rng: np.random.Generator, t: int,
                    probs0: dict[tuple[int, ...], Fraction],
                    probs1: dict[tuple[int, ...], Fraction]) -> tuple[np.ndarray, np.ndarray]:
    # Projection onto expert 3 is identical in the two worlds by the 1<->2
    # symmetry. Share its total count, then sample each world conditionally.
    p3 = float(exact_inclusion(probs0)[3])
    if exact_inclusion(probs0)[3] != exact_inclusion(probs1)[3]:
        raise AssertionError("expert-3 marginal must be invariant across worlds")
    n3 = int(rng.binomial(t, p3))
    result = []
    for probs in (probs0, probs1):
        inc3 = [s for s in SUBSETS if 3 in s]
        no3 = [s for s in SUBSETS if 3 not in s]
        p_inc = np.array([float(probs[s] / sum(probs[x] for x in inc3)) for s in inc3])
        p_no = np.array([float(probs[s] / sum(probs[x] for x in no3)) for s in no3])
        counts_inc = rng.multinomial(n3, p_inc)
        counts_no = rng.multinomial(t - n3, p_no)
        counts = {s: 0 for s in SUBSETS}
        counts.update({s: int(n) for s, n in zip(inc3, counts_inc)})
        counts.update({s: int(n) for s, n in zip(no3, counts_no)})
        r = np.zeros(4, dtype=np.int64)
        for s, n in counts.items():
            for e in s:
                r[e] += n
        if int(r.sum()) != 2 * t:
            raise AssertionError("Top-2 request mass conservation failed")
        result.append(r)
    return result[0], result[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    exact_probs = tuple(pl_subset_probs_exact(w) for w in WEIGHTS_INT)
    pi_exact = tuple(exact_inclusion(p) for p in exact_probs)
    if pi_exact[0] != (Fraction(68225, 68289), Fraction(670, 1339),
                       Fraction(34183, 136578), Fraction(34183, 136578)):
        raise AssertionError(f"unexpected world-0 exact inclusion vector: {pi_exact[0]}")
    if pi_exact[1] != (pi_exact[0][0], pi_exact[0][2], pi_exact[0][1], pi_exact[0][3]):
        raise AssertionError(f"worlds are not exact pair swaps: {pi_exact[1]}")
    for h in range(2):
        for e, cap in enumerate(CAP_FRAC):
            if e in (0, 1, 2) and not pi_exact[h][e] > cap:
                raise AssertionError(f"expected expert {e} saturated in world {h}")
            if e == 3 and not pi_exact[h][e] < cap:
                raise AssertionError("expert 3 should be unsaturated")

    q0, err0 = solve_target(0)
    q1, err1 = solve_target(1)
    p_at_zero = [inclusion(w) for w in WEIGHTS]
    cross_risk = overflow(inclusion(WEIGHTS[1] * np.exp(-q0)))
    q0_risk = overflow(inclusion(WEIGHTS[0] * np.exp(-q0)))
    q1_risk = overflow(inclusion(WEIGHTS[1] * np.exp(-q1)))
    q1_cross_risk = overflow(inclusion(WEIGHTS[0] * np.exp(-q1)))
    no_feedback = 0.5 * (overflow(p_at_zero[0]) + overflow(p_at_zero[1]))
    fixed_common = 0.5 * (q0_risk + cross_risk)
    threshold = 0.5 * (float(pi_exact[0][1]) + float(pi_exact[1][1]))

    all_rows = []
    summaries = []
    for ti, t in enumerate(SIZES):
        caps = (CAP * t).astype(np.int64)
        if not np.allclose(caps / t, CAP, rtol=0, atol=0):
            raise AssertionError("capacity fractions must be integral")
        counts = {"admitted_equal": 0, "no_clip_equal": 0, "classifier_error": 0}
        for rep in range(REPS):
            rng = np.random.default_rng(2026101702 + 100000 * ti + rep)
            r0, r1 = paired_requests(rng, t, exact_probs[0], exact_probs[1])
            a0, a1 = np.minimum(r0, caps), np.minimum(r1, caps)
            if not np.array_equal(a0, np.minimum(r0, caps)) or not np.array_equal(a1, np.minimum(r1, caps)):
                raise AssertionError("canonical admission identity failed")
            pred0 = r0[1] / t > threshold
            pred1 = r1[1] / t > threshold
            error = bool(not pred0 or pred1)  # world 0 should be high; world 1 low
            equal_a, equal_r = bool(np.array_equal(a0, a1)), bool(np.array_equal(r0, r1))
            counts["admitted_equal"] += int(equal_a)
            counts["no_clip_equal"] += int(equal_r)
            counts["classifier_error"] += int(error)
            all_rows.append({
                "T": t, "replicate": rep,
                "R0": r0.tolist(), "R1": r1.tolist(),
                "A0": a0.tolist(), "A1": a1.tolist(),
                "admitted_equal": equal_a,
                "no_clip_equal": equal_r,
                "classifier_error": error,
            })
        summaries.append({
            "T": t, "replicates": REPS,
            "identical_admitted_pairs": counts["admitted_equal"],
            "identical_admitted_rate": counts["admitted_equal"] / REPS,
            "identical_no_clip_pairs": counts["no_clip_equal"],
            "classifier_errors": counts["classifier_error"],
            "classifier_error_rate": counts["classifier_error"] / REPS,
        })

    csv_path = OUT / "paired_plants.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0]))
        writer.writeheader(); writer.writerows(all_rows)
    summary = {
        "status": "controlled finite-weight synthetic audit; not a theorem proof",
        "E": 4, "K": 2, "world_weights": [list(w) for w in WEIGHTS_INT],
        "capacity_fractions": [str(x) for x in CAP_FRAC],
        "exact_world0_inclusions": [str(x) for x in pi_exact[0]],
        "exact_world1_inclusions": [str(x) for x in pi_exact[1]],
        "classifier_threshold": threshold,
        "target_pressures": [q0.tolist(), q1.tolist()],
        "target_pressure_max_residual": max(err0, err1),
        "population_overflow": {
            "q0_in_world0": q0_risk,
            "q0_in_world1": cross_risk,
            "q1_in_world0": q1_cross_risk,
            "q1_in_world1": q1_risk,
            "fixed_common_q0_equal_prior": fixed_common,
            "no_feedback_equal_prior": no_feedback,
        },
        "replicates_per_T": REPS,
        "seed_rule": "2026101702 + 100000*T_index + replicate",
        "cells": summaries,
        "limits": [
            "The fixed common action is a diagnostic and is not asserted to be optimal for admitted telemetry.",
            "Finite Monte Carlo outcomes support the finite-weight construction but do not prove the family theorem.",
            "No trained-model gain, measured telemetry cost, or benchmark separation is tested.",
        ],
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"summary": str(summary_path), "plants": str(csv_path),
                      "summary_sha256": sha(summary_path), "plants_sha256": sha(csv_path),
                      "summary_data": summary}, indent=2))


if __name__ == "__main__":
    main()
