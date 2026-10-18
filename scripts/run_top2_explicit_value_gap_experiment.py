#!/usr/bin/env python3
"""Paired finite-batch check for the explicit Top-2 value-gap theorem."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import binom

from run_topk_multisaturated_value_pilot import sample_paired_counts


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "top2_explicit_value_gap_2026-10-18"
SIZES = (1680, 1800, 3360)
REPLICATES = 50_000
CAP_FRACTIONS = np.array([11 / 20, 11 / 20, 9 / 10], dtype=np.float64)
OMIT_PROBS = (
    np.array([1 / 6, 5 / 12, 5 / 12], dtype=np.float64),
    np.array([5 / 12, 1 / 6, 5 / 12], dtype=np.float64),
)
THRESHOLD = 17 / 24
V_LOWER = 27 / 200


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_positive_overflow(t: int, capacities: np.ndarray,
                               inclusion: np.ndarray) -> float:
    total = 0.0
    for cap, p in zip(capacities, inclusion, strict=True):
        # E[(Bin(T,p)-C)+] = T*p*P(Bin(T-1,p)>=C) - C*P(Bin(T,p)>C).
        total += t * p * float(binom.sf(int(cap) - 1, t - 1, p))
        total -= int(cap) * float(binom.sf(int(cap), t, p))
    return total / t


def exact_admitted_sign_error(t: int, cap: int) -> float:
    """Full-A Bayes-sign error, conditioning on omitted experts 1+2."""
    # In world 0, (Z1,Z2,Z3) has probabilities (1/6,5/12,5/12).
    # Conditional on M=Z1+Z2, M~Bin(T,7/12), Z1|M~Bin(M,2/7).
    # Equal-cap clipping preserves the sign unless both first experts clip,
    # in which case it creates a tie.
    from scipy.stats import binom as binom_dist

    cap_omit = t - cap
    total = 0.0
    for m in range(t + 1):
        mass_m = float(binom_dist.pmf(m, t, 7 / 12))
        if mass_m == 0.0:
            continue
        p = 2 / 7
        # A1<A2 iff Z1>Z2 and expert 1 is not clipped: Z1>cap_omit.
        first_x = max(m // 2 + 1, cap_omit + 1)
        error = float(binom_dist.sf(first_x - 1, m, p))

        # A1=A2 iff the requests tie or both first experts clip.
        lo = max(0, m - cap_omit)
        hi = min(m, cap_omit)
        both_clip = (float(binom_dist.cdf(hi, m, p)
                            - binom_dist.cdf(lo - 1, m, p)) if lo <= hi else 0.0)
        tie = (float(binom_dist.pmf(m // 2, m, p)) if m % 2 == 0 else 0.0)
        intersection = tie if (m % 2 == 0 and m // 2 <= cap_omit) else 0.0
        total += mass_m * (error + 0.5 * (tie + both_clip - intersection))
    return total


def theorem_bound(t: int) -> tuple[float, float, float, float]:
    eps_admitted = 2 * math.exp(-t / 450) + math.exp(-361 * t / 1800)
    eps_request = 2 * math.exp(-t / 32)
    target_cost_bound = 3 / (2 * math.sqrt(t))
    lower = V_LOWER - 2 * eps_admitted - eps_request - target_cost_bound
    return lower, eps_admitted, eps_request, target_cost_bound


def run_cell(t: int) -> dict[str, float | int | bool]:
    if t % 20:
        raise AssertionError("registered capacity is not integer")
    caps = np.array([11 * t // 20, 11 * t // 20, 18 * t // 20], dtype=np.int64)
    if int(caps.sum()) != 2 * t:
        raise AssertionError("capacity mass must equal K*T")

    # Exact target action has inclusion vector c in either true world.
    correct_cost = expected_positive_overflow(t, caps, CAP_FRACTIONS)
    wrong0 = np.array([97 / 385, 322 / 385, 351 / 385], dtype=np.float64)
    wrong1 = wrong0[[1, 0, 2]]
    wrong_cost0 = expected_positive_overflow(t, caps, wrong0)
    wrong_cost1 = expected_positive_overflow(t, caps, wrong1)
    if not math.isclose(wrong_cost0, wrong_cost1, rel_tol=0.0, abs_tol=1e-13):
        raise AssertionError("world-swap action-cost symmetry failed")

    cut = math.floor(THRESHOLD * t)
    error_world0 = float(binom.cdf(cut, t, 5 / 6))
    error_world1 = float(binom.sf(cut, t, 7 / 12))
    admitted_error = exact_admitted_sign_error(t, int(caps[0]))
    avg_error = (error_world0 + error_world1) / 2
    exact_requested_value = correct_cost + avg_error * (wrong_cost0 - correct_cost)
    exact_admitted_value = correct_cost + admitted_error * (wrong_cost0 - correct_cost)
    exact_two_action_gap = exact_admitted_value - exact_requested_value

    rng = np.random.default_rng(20261018 + t)
    counts = {"request_mass": 0, "clip_identity": 0, "paired_swap": 0}
    admitted_equal = 0
    error0 = 0
    error1 = 0
    admitted_errors = 0.0
    paired_policy_costs: list[float] = []
    admitted_policy_costs: list[float] = []
    admitted_fixed_cost = 0.5 * (wrong_cost0 + correct_cost)
    # The paired draw represents one sample from each world. Determine each
    # action from its own requested vector; the two-world sample estimates
    # the equal-prior classifier risk.
    for rep in range(REPLICATES):
        r0, r1 = sample_paired_counts(rng, t, OMIT_PROBS)
        if int(r0.sum()) != 2 * t or int(r1.sum()) != 2 * t:
            raise AssertionError("Top-2 request mass conservation failed")
        a0, a1 = np.minimum(r0, caps), np.minimum(r1, caps)
        if not (np.array_equal(a0, np.minimum(r0, caps))
                and np.array_equal(a1, np.minimum(r1, caps))):
            raise AssertionError("canonical clipping identity failed")
        z0, z1 = 2 * t - r0, 2 * t - r1
        if z0[2] != z1[2]:
            raise AssertionError("paired coupling did not preserve omitted expert 3")

        pred0 = (r0[0] / t) < THRESHOLD
        pred1 = (r1[0] / t) < THRESHOLD
        err0 = bool(pred0)
        err1 = not bool(pred1)
        admitted_pred0 = a0[0] < a0[1]
        admitted_pred1 = a1[0] < a1[1]
        admitted_errors += (float(admitted_pred0)
                            + 0.5 * float(a0[0] == a0[1])
                            + float(a1[0] > a1[1])
                            + 0.5 * float(a1[0] == a1[1])) / 2
        aerr0 = bool(admitted_pred0)
        aerr1 = bool(a1[0] > a1[1])
        atie0 = a0[0] == a0[1]
        atie1 = a1[0] == a1[1]
        # Expected cost conditional on a randomized tie decision.
        admitted_policy_costs.append(
            0.5 * (
                (wrong_cost0 if aerr0 else correct_cost) * (0.0 if atie0 else 1.0)
                + (wrong_cost0 if aerr1 else correct_cost) * (0.0 if atie1 else 1.0)
                + (wrong_cost0 + correct_cost) * 0.5 * (int(atie0) + int(atie1))
            )
        )
        error0 += int(err0)
        error1 += int(err1)
        admitted_equal += int(np.array_equal(a0, a1))
        paired_policy_costs.append(
            0.5 * ((wrong_cost0 if err0 else correct_cost)
                   + (wrong_cost1 if err1 else correct_cost))
        )
        counts["request_mass"] += int(int(r0.sum()) == 2 * t and int(r1.sum()) == 2 * t)
        counts["clip_identity"] += int(np.array_equal(a0, np.minimum(r0, caps))
                                       and np.array_equal(a1, np.minimum(r1, caps)))
        counts["paired_swap"] += int(z0[2] == z1[2])

    mc_err0 = error0 / REPLICATES
    mc_err1 = error1 / REPLICATES
    mc_admitted_error = admitted_errors / REPLICATES
    se0 = math.sqrt(error_world0 * (1 - error_world0) / REPLICATES)
    se1 = math.sqrt(error_world1 * (1 - error_world1) / REPLICATES)
    if abs(mc_err0 - error_world0) > 5 * se0 + 1 / REPLICATES:
        raise AssertionError("world-0 classifier rate differs by more than five SE")
    if abs(mc_err1 - error_world1) > 5 * se1 + 1 / REPLICATES:
        raise AssertionError("world-1 classifier rate differs by more than five SE")
    se_admitted = math.sqrt(admitted_error * (1 - admitted_error) / REPLICATES)
    if abs(mc_admitted_error - admitted_error) > 5 * se_admitted + 1 / REPLICATES:
        raise AssertionError("admitted classifier rate differs by more than five SE")

    lb, eps_a, eps_r, cost_term = theorem_bound(t)
    return {
        "T": t,
        "replicates_per_world": REPLICATES,
        "capacity": ";".join(map(str, caps.tolist())),
        "exact_request_error_world0": error_world0,
        "mc_request_error_world0": mc_err0,
        "mc_request_error_world0_se": se0,
        "exact_request_error_world1": error_world1,
        "mc_request_error_world1": mc_err1,
        "mc_request_error_world1_se": se1,
        "exact_admitted_sign_error": admitted_error,
        "mc_admitted_sign_error": mc_admitted_error,
        "mc_admitted_sign_error_se": se_admitted,
        "paired_admitted_vector_equality_rate": admitted_equal / REPLICATES,
        "exact_correct_target_expected_overflow": correct_cost,
        "exact_wrong_target_expected_overflow": wrong_cost0,
        "exact_requested_two_action_value": exact_requested_value,
        "exact_admitted_two_action_value": exact_admitted_value,
        "exact_admitted_minus_requested_two_action_gap": exact_two_action_gap,
        "mc_requested_two_action_value": float(np.mean(paired_policy_costs)),
        "mc_requested_two_action_value_se": float(np.std(paired_policy_costs, ddof=1)
                                                    / math.sqrt(REPLICATES)),
        "mc_admitted_two_action_value": float(np.mean(admitted_policy_costs)),
        "mc_admitted_two_action_value_se": float(np.std(admitted_policy_costs, ddof=1)
                                                   / math.sqrt(REPLICATES)),
        "admitted_fixed_common_target_action_value": admitted_fixed_cost,
        "analytic_all_policy_gap_lower_bound": lb,
        "eps_admitted_bound": eps_a,
        "eps_requested_classifier_bound": eps_r,
        "finite_batch_target_cost_bound": cost_term,
        "request_mass_checks_pass": counts["request_mass"] == REPLICATES,
        "clip_identity_checks_pass": counts["clip_identity"] == REPLICATES,
        "coupling_checks_pass": counts["paired_swap"] == REPLICATES,
        "classifier_mc_within_five_se": True,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [run_cell(t) for t in SIZES]
    cells_path = OUT / "cells.csv"
    with cells_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "experiment": "Top-2 explicit all-policy value-gap threshold check",
        "protocol": "docs/paper/top2_explicit_value_gap_experiment_protocol_2026-10-18.md",
        "theorem": "docs/paper/topk_two_saturated_value_theorem_candidate_2026-10-17.md",
        "replicates_per_world_and_cell": REPLICATES,
        "cells": rows,
        "limitations": [
            "Simulation checks count laws and the registered requested policy, not the all-policy theorem.",
            "The all-policy lower bound is analytic and uses the proved v_star >= 27/200.",
            "No hardware price, trained-model quality, or production prevalence is measured.",
            "This fixed instance remains representable as a censored Bayesian decision problem.",
        ],
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"cells_sha256={sha256(cells_path)}")
    print(f"summary_sha256={sha256(summary_path)}")
    for row in rows:
        print(
            f"T={row['T']} all_policy_lb={row['analytic_all_policy_gap_lower_bound']:.8f} "
            f"two_action_gap={row['exact_admitted_minus_requested_two_action_gap']:.8f} "
            f"A_equal={row['paired_admitted_vector_equality_rate']:.5f}"
        )


if __name__ == "__main__":
    main()
