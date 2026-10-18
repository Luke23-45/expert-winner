#!/usr/bin/env python3
"""Controlled Top-2 multi-saturation pilot under canonical per-expert clipping."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, least_squares, minimize_scalar


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "topk_multisaturated_value_pilot"
WORLD_WEIGHTS = (np.array([2.0, 1.0, 1.0]), np.array([1.0, 2.0, 1.0]))
CAPACITY = np.array([11 / 20, 11 / 20, 9 / 10], dtype=float)
SIZES = (1800, 7200, 28800)
REPLICATES = 500
THRESHOLD = 17 / 24


def pl_topk_inclusion(weights: np.ndarray, k: int = 2) -> np.ndarray:
    """Exact finite sum over Plackett-Luce rankings, returned in float64."""
    e = len(weights)
    inclusion = np.zeros(e, dtype=np.float64)
    for perm in itertools.permutations(range(e)):
        remaining = float(weights.sum())
        prob = 1.0
        for expert in perm:
            prob *= float(weights[expert]) / remaining
            remaining -= float(weights[expert])
        inclusion[list(perm[:k])] += prob
    return inclusion


def pl_topk_inclusion_exact(weights: tuple[int, ...], k: int = 2) -> tuple[Fraction, ...]:
    """Exact Plackett-Luce inclusion probabilities for integer weights."""
    e = len(weights)
    inclusion = [Fraction(0) for _ in range(e)]
    for perm in itertools.permutations(range(e)):
        remaining = sum(weights)
        prob = Fraction(1)
        for expert in perm:
            prob *= Fraction(weights[expert], remaining)
            remaining -= weights[expert]
        for expert in perm[:k]:
            inclusion[expert] += prob
    return tuple(inclusion)


def exact_overflow(probabilities: tuple[Fraction, ...]) -> Fraction:
    caps = (Fraction(11, 20), Fraction(11, 20), Fraction(9, 10))
    return sum((p - c for p, c in zip(probabilities, caps) if p > c), Fraction(0))


def inclusion_at(world: int, q: np.ndarray) -> np.ndarray:
    # q[2] is fixed to zero as the gauge representative.
    weights = WORLD_WEIGHTS[world] * np.exp(-np.asarray([q[0], q[1], 0.0]))
    return pl_topk_inclusion(weights)


def overflow_fraction(world: int, q: np.ndarray) -> float:
    return float(np.maximum(inclusion_at(world, q) - CAPACITY, 0.0).sum())


def solve_target_pressure(world: int) -> tuple[np.ndarray, float]:
    fit = least_squares(
        lambda q: inclusion_at(world, q)[:2] - CAPACITY[:2],
        x0=np.zeros(2), xtol=1e-14, ftol=1e-14, gtol=1e-14,
        max_nfev=20_000,
    )
    q = np.array([fit.x[0], fit.x[1], 0.0])
    err = float(np.max(np.abs(inclusion_at(world, q) - CAPACITY)))
    if err > 1e-10:
        raise RuntimeError(f"target pressure residual too large: {err}")
    return q, err


def common_action_search() -> dict[str, float | list[float]]:
    def risk(x: np.ndarray) -> float:
        q = np.array([x[0], x[1], 0.0])
        return 0.5 * (overflow_fraction(0, q) + overflow_fraction(1, q))

    result = differential_evolution(
        risk, [(-8.0, 8.0), (-8.0, 8.0)], seed=20261017,
        tol=1e-11, atol=1e-13, polish=True, updating="immediate",
        workers=1, popsize=30, maxiter=3000,
    )
    q = np.array([result.x[0], result.x[1], 0.0])
    # Symmetry-constrained one-dimensional check is useful as a diagnostic,
    # but is not assumed to equal the unrestricted common-action optimum.
    sym = minimize_scalar(
        lambda z: risk(np.array([z, z])), bounds=(-8.0, 8.0),
        method="bounded", options={"xatol": 1e-13, "maxiter": 10000},
    )
    return {
        "bounded_domain": [-8.0, 8.0],
        "optimizer_success": bool(result.success),
        "optimizer_message": str(result.message),
        "common_action_q": [float(x) for x in q],
        "common_action_risk": float(result.fun),
        "symmetric_q1_q2": float(sym.x),
        "symmetric_action_risk": float(sym.fun),
        "interpretation": "numerically found feasible common-action risk; not a certified global minimum",
    }


def sample_paired_counts(rng: np.random.Generator, t: int, omit_probs: tuple[np.ndarray, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    # Both worlds have the same probability of omitting expert 3. Couple that
    # count, then split the remaining omitted-1/omitted-2 tokens by each exact
    # conditional Plackett-Luce probability.
    p3 = float(omit_probs[0][2])
    if not math.isclose(p3, float(omit_probs[1][2]), rel_tol=0.0, abs_tol=1e-13):
        raise AssertionError("worlds must have the same omitted-3 probability")
    omit3_n = int(rng.binomial(t, p3))
    remaining = t - omit3_n
    requests = []
    for probs in omit_probs:
        conditional_omit1 = float(probs[0] / (probs[0] + probs[1]))
        omit1_n = int(rng.binomial(remaining, conditional_omit1))
        omit2_n = remaining - omit1_n
        omitted = np.array([omit1_n, omit2_n, omit3_n], dtype=np.int64)
        requests.append(t - omitted)  # Each Top-2 token selects every non-omitted expert.
    return requests[0], requests[1]


def wilson(k: int, n: int) -> list[float]:
    if n == 0:
        return [float("nan"), float("nan")]
    z = 1.959963984540054
    p = k / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [max(0.0, center - half), min(1.0, center + half)]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    q0, res0 = solve_target_pressure(0)
    q1, res1 = solve_target_pressure(1)
    pi0 = inclusion_at(0, np.zeros(3))
    pi1 = inclusion_at(1, np.zeros(3))
    pi0_exact = pl_topk_inclusion_exact((2, 1, 1))
    pi1_exact = pl_topk_inclusion_exact((1, 2, 1))
    target_exact = pl_topk_inclusion_exact((1, 1, 3))
    cross_exact = pl_topk_inclusion_exact((1, 4, 6))
    no_feedback_exact = Fraction(1, 2) * (
        exact_overflow(pi0_exact) + exact_overflow(pi1_exact)
    )
    common_target_action_exact = (
        exact_overflow(target_exact) + exact_overflow(cross_exact)
    ) / 2
    if pi0_exact != (Fraction(5, 6), Fraction(7, 12), Fraction(7, 12)):
        raise AssertionError(f"incorrect exact world-0 inclusion probabilities: {pi0_exact}")
    if pi1_exact != (Fraction(7, 12), Fraction(5, 6), Fraction(7, 12)):
        raise AssertionError(f"incorrect exact world-1 inclusion probabilities: {pi1_exact}")
    if target_exact != tuple(map(Fraction, (Fraction(11, 20), Fraction(11, 20), Fraction(9, 10)))):
        raise AssertionError(f"target pressure does not realize capacity exactly: {target_exact}")
    if common_target_action_exact != Fraction(459, 3080):
        raise AssertionError(f"unexpected exact common-action risk: {common_target_action_exact}")
    if no_feedback_exact != Fraction(19, 60):
        raise AssertionError(f"unexpected exact no-feedback risk: {no_feedback_exact}")
    omit0 = 1.0 - pi0
    omit1 = 1.0 - pi1
    if not np.allclose(pi0, [5 / 6, 7 / 12, 7 / 12], atol=1e-13):
        raise AssertionError(f"unexpected world-0 Top-2 inclusion probabilities: {pi0}")
    if not np.allclose(pi1, [7 / 12, 5 / 6, 7 / 12], atol=1e-13):
        raise AssertionError(f"unexpected world-1 Top-2 inclusion probabilities: {pi1}")
    if not np.allclose(CAPACITY.sum(), 2.0):
        raise AssertionError("capacity fractions must be exact-total")

    common = common_action_search()
    no_feedback_risk = 0.5 * (
        overflow_fraction(0, np.zeros(3)) + overflow_fraction(1, np.zeros(3))
    )
    target_risks = [overflow_fraction(0, q0), overflow_fraction(1, q1)]
    swapped_risks = [overflow_fraction(0, q1), overflow_fraction(1, q0)]
    rows: list[dict[str, object]] = []
    summaries = []
    for ti, t in enumerate(SIZES):
        caps = (CAPACITY * t).astype(np.int64)
        if not np.allclose(caps / t, CAPACITY, atol=0, rtol=0):
            raise AssertionError("registered capacity fractions must be integral")
        outcomes = {"admitted_equal": 0, "requested_classifier_error": 0, "no_clip_equal": 0}
        requested_policy_risks: list[float] = []
        admitted_policy_risks: list[float] = []
        max_mass_error = 0
        max_clip_error = 0
        for rep in range(REPLICATES):
            rng = np.random.default_rng(2026101701 + ti * 100000 + rep)
            r0, r1 = sample_paired_counts(rng, t, (omit0, omit1))
            a0 = np.minimum(r0, caps)
            a1 = np.minimum(r1, caps)
            max_mass_error = max(max_mass_error, abs(int(r0.sum()) - 2 * t), abs(int(r1.sum()) - 2 * t))
            max_clip_error = max(max_clip_error, int(np.max(np.abs(a0 - np.minimum(r0, caps)))), int(np.max(np.abs(a1 - np.minimum(r1, caps)))))
            admitted_equal = bool(np.array_equal(a0, a1))
            no_clip_equal = bool(np.array_equal(r0, r1))
            pred_world1_0 = (r0[0] / t) < THRESHOLD
            pred_world1_1 = (r1[0] / t) < THRESHOLD
            classifier_error = bool(pred_world1_0 or not pred_world1_1)
            chosen0 = 1 if pred_world1_0 else 0
            chosen1 = 1 if pred_world1_1 else 0
            request_policy_risk = 0.5 * (
                overflow_fraction(0, q1 if chosen0 else q0)
                + overflow_fraction(1, q1 if chosen1 else q0)
            )
            admitted_policy_risk = 0.5 * (
                overflow_fraction(0, q0) + overflow_fraction(1, q0)
            )
            requested_policy_risks.append(request_policy_risk)
            admitted_policy_risks.append(admitted_policy_risk)
            outcomes["admitted_equal"] += int(admitted_equal)
            outcomes["requested_classifier_error"] += int(classifier_error)
            outcomes["no_clip_equal"] += int(no_clip_equal)
            rows.append({
                "T": t, "replicate": rep,
                "R0": r0.tolist(), "R1": r1.tolist(),
                "A0": a0.tolist(), "A1": a1.tolist(),
                "admitted_equal": admitted_equal,
                "no_clip_equal": no_clip_equal,
                "requested_classifier_error": classifier_error,
                "requested_policy_population_risk": request_policy_risk,
                "admitted_fixed_q0_population_risk": admitted_policy_risk,
                "no_feedback_population_risk": no_feedback_risk,
                "world0_overflow_at_q0": target_risks[0],
                "world1_overflow_at_q1": target_risks[1],
                "world0_overflow_at_q1": swapped_risks[0],
                "world1_overflow_at_q0": swapped_risks[1],
            })
        n = REPLICATES
        summaries.append({
            "T": t,
            "replicates": n,
            "identical_admitted_pairs": outcomes["admitted_equal"],
            "identical_admitted_rate": outcomes["admitted_equal"] / n,
            "identical_admitted_wilson95": wilson(outcomes["admitted_equal"], n),
            "identical_no_clip_request_pairs": outcomes["no_clip_equal"],
            "identical_no_clip_rate": outcomes["no_clip_equal"] / n,
            "requested_classifier_errors": outcomes["requested_classifier_error"],
            "requested_classifier_error_rate": outcomes["requested_classifier_error"] / n,
            "requested_classifier_error_wilson95": wilson(outcomes["requested_classifier_error"], n),
            "requested_classifier_mean_population_risk": float(np.mean(requested_policy_risks)),
            "admitted_fixed_q0_population_risk": float(np.mean(admitted_policy_risks)),
            "max_mass_error": max_mass_error,
            "max_clipping_identity_error": max_clip_error,
        })

    plants_path = OUT / "paired_plants.csv"
    with plants_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = list(rows[0])
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "status": "exploratory controlled synthetic pilot; not proof or preregistered confirmation",
        "model": "E=3, K=2 Gumbel-Top-2 / Plackett-Luce, static base weights, pressure multiplies weights by exp(-q), A=min(R,C)",
        "world_weights": [w.tolist() for w in WORLD_WEIGHTS],
        "capacity_fractions": CAPACITY.tolist(),
        "world0_inclusion_at_zero": pi0.tolist(),
        "world1_inclusion_at_zero": pi1.tolist(),
        "exact_world0_inclusion_at_zero": [str(x) for x in pi0_exact],
        "exact_world1_inclusion_at_zero": [str(x) for x in pi1_exact],
        "exact_target_inclusion": [str(x) for x in target_exact],
        "exact_cross_world_inclusion_under_q0": [str(x) for x in cross_exact],
        "world0_omission_at_zero": omit0.tolist(),
        "world1_omission_at_zero": omit1.tolist(),
        "target_pressure_world0": q0.tolist(),
        "target_pressure_world1": q1.tolist(),
        "max_target_solver_residual": max(res0, res1),
        "target_action_population_overflow": target_risks,
        "no_feedback_population_risk": no_feedback_risk,
        "exact_no_feedback_population_risk": str(no_feedback_exact),
        "exact_common_target_action_population_risk": str(common_target_action_exact),
        "cross_world_action_overflow": swapped_risks,
        "common_action_search": common,
        "classifier_threshold": THRESHOLD,
        "capacity_integer_units": {str(t): (CAPACITY * t).astype(int).tolist() for t in SIZES},
        "replicates_per_T": REPLICATES,
        "seed_rule": "2026101701 + T_index*100000 + replicate",
        "cells": summaries,
        "limits": [
            "The common-action minimization is numerical on [-8,8]^2, not a certified global minimum.",
            "The requested classifier and fixed admitted action are concrete policies, not optimal policies.",
            "Finite-batch admitted vectors are only coupled to be equal on the event that both saturated coordinates clip and the common third count remains uncapped.",
            "No training run, system cost, multi-round result, Top-K theorem, or venue-level novelty claim is established by this pilot.",
        ],
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "summary": str(summary_path),
        "plants": str(plants_path),
        "summary_sha256": sha(summary_path),
        "plants_sha256": sha(plants_path),
        "target_pressures": [q0.tolist(), q1.tolist()],
        "target_population_costs": target_risks,
        "common_action_search": common,
        "cells": summaries,
    }, indent=2))


if __name__ == "__main__":
    main()
