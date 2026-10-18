#!/usr/bin/env python3
"""Exact one-batch TV audit plus paired synthetic control experiment.

The model is Top-1 Gumbel-max routing with canonical per-expert clipping.
The exact TV calculation uses integer multinomial weights; the control arm
uses multinomial draws (the exact count law induced by iid Gumbel-max tokens)
and evaluates next-batch population overflow under the resulting pressure.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np


P0 = (0.4, 0.4, 0.2)
P1 = (0.5, 0.3, 0.2)
ETA = 15.0 * math.log(2.0)
MU = np.array([1.0 / 3.0] * 3)


def exact_law_audit(t: int) -> dict[str, object]:
    if t % 20:
        raise ValueError("T must be divisible by 20 (capacity and classifier grid)")
    caps = (t // 4, t // 4, t // 2)
    denominator = 10**t
    r0: dict[tuple[int, int, int], int] = {}
    r1: dict[tuple[int, int, int], int] = {}
    a0: dict[tuple[int, int, int], int] = {}
    a1: dict[tuple[int, int, int], int] = {}
    failure_weights = [0, 0]

    for n1 in range(t + 1):
        for n2 in range(t - n1 + 1):
            n3 = t - n1 - n2
            coefficient = math.comb(t, n1) * math.comb(t - n1, n2)
            w0 = coefficient * 4**n1 * 4**n2 * 2**n3
            w1 = coefficient * 5**n1 * 3**n2 * 2**n3
            key_r = (n1, n2, n3)
            key_a = tuple(min(n, c) for n, c in zip(key_r, caps))
            r0[key_r] = w0
            r1[key_r] = w1
            a0[key_a] = a0.get(key_a, 0) + w0
            a1[key_a] = a1.get(key_a, 0) + w1
            good = n1 >= caps[0] and n2 >= caps[1] and n3 < caps[2]
            if not good:
                failure_weights[0] += w0
                failure_weights[1] += w1

    assert sum(r0.values()) == denominator
    assert sum(r1.values()) == denominator
    assert sum(a0.values()) == denominator
    assert sum(a1.values()) == denominator
    tv_r = Fraction(sum(abs(r0.get(k, 0) - r1.get(k, 0)) for k in r0), 2 * denominator)
    tv_a = Fraction(sum(abs(a0.get(k, 0) - a1.get(k, 0)) for k in a0.keys() | a1.keys()), 2 * denominator)
    fail0 = Fraction(failure_weights[0], denominator)
    fail1 = Fraction(failure_weights[1], denominator)
    assert tv_a <= fail0 + fail1

    classification_threshold = 9 * t // 20
    error0_r = sum(w for (n1, _, _), w in r0.items() if n1 >= classification_threshold)
    error1_r = sum(w for (n1, _, _), w in r1.items() if n1 < classification_threshold)
    error0_a = sum(w for (n1, _, _), w in a0.items() if n1 >= classification_threshold)
    error1_a = sum(w for (n1, _, _), w in a1.items() if n1 < classification_threshold)
    classifier_error_r = Fraction(error0_r + error1_r, 2 * denominator)
    classifier_error_a = Fraction(error0_a + error1_a, 2 * denominator)
    return {
        "T": t,
        "capacity": list(caps),
        "request_TV_exact": str(tv_r),
        "request_TV": float(tv_r),
        "admitted_TV_exact": str(tv_a),
        "admitted_TV": float(tv_a),
        "admitted_coupling_failure_h0_exact": str(fail0),
        "admitted_coupling_failure_h1_exact": str(fail1),
        "admitted_TV_coupling_bound": float(fail0 + fail1),
        "request_gap_classifier_error_exact": str(classifier_error_r),
        "request_gap_classifier_error": float(classifier_error_r),
        "admitted_gap_classifier_error_exact": str(classifier_error_a),
        "admitted_gap_classifier_error": float(classifier_error_a),
        "request_h0_false_positive_probability": float(
            Fraction(error0_r, denominator)
        ),
        "request_h0_false_positive_probability_exact": str(
            Fraction(error0_r, denominator)
        ),
        "request_h1_false_negative_probability": float(
            Fraction(error1_r, denominator)
        ),
        "request_h1_false_negative_probability_exact": str(
            Fraction(error1_r, denominator)
        ),
        "admitted_equal_prior_Bayes_error": float((1 - tv_a) / 2),
        "request_equal_prior_Bayes_error": float((1 - tv_r) / 2),
    }


def next_batch_population_overflow(
    p: tuple[float, float, float], signal_counts: np.ndarray | None, t: int
) -> np.ndarray:
    capacities = np.array([0.25, 0.25, 0.5])
    if signal_counts is None:
        q = np.zeros((1, 3), dtype=np.float64)
    else:
        q = ETA * (signal_counts / t - MU[None, :])
        q -= q.min(axis=1, keepdims=True)
    logits = np.log(np.asarray(p))[None, :] - q
    logits -= logits.max(axis=1, keepdims=True)
    probs = np.exp(logits)
    probs /= probs.sum(axis=1, keepdims=True)
    return np.maximum(probs - capacities[None, :], 0.0).sum(axis=1)


def paired_control_audit(t: int, replicates: int, seed: int) -> dict[str, object]:
    out: dict[str, object] = {"T": t, "replicates_per_world": replicates, "worlds": {}}
    for world_index, p in enumerate((P0, P1)):
        rng = np.random.default_rng(seed + 1009 * t + 9176 * world_index)
        requested = rng.multinomial(t, p, size=replicates)
        capacities = np.array([t // 4, t // 4, t // 2])
        admitted = np.minimum(requested, capacities[None, :])
        cost_r = next_batch_population_overflow(p, requested, t)
        cost_a = next_batch_population_overflow(p, admitted, t)
        cost_none = next_batch_population_overflow(p, None, t)

        def paired_summary(left: np.ndarray, right: np.ndarray) -> dict[str, float]:
            diff = left - right
            mean = float(diff.mean())
            se = float(diff.std(ddof=1) / math.sqrt(replicates))
            return {
                "mean_difference": mean,
                "standard_error": se,
                "ci95_low": mean - 1.96 * se,
                "ci95_high": mean + 1.96 * se,
            }

        request_decision = requested[:, 0] / t >= 0.45
        admitted_decision = admitted[:, 0] / t >= 0.45
        target = world_index == 1
        request_error = float(np.mean(request_decision != target))
        admitted_error = float(np.mean(admitted_decision != target))
        out["worlds"][f"h{world_index}"] = {
            "mean_next_population_overflow_requested": float(cost_r.mean()),
            "mean_next_population_overflow_admitted": float(cost_a.mean()),
            "mean_next_population_overflow_no_update": float(cost_none.mean()),
            "paired_admitted_minus_requested": paired_summary(cost_a, cost_r),
            "paired_no_update_minus_requested": paired_summary(cost_none, cost_r),
            "request_classifier_error_R1_fraction_ge_0.45": request_error,
            "admitted_classifier_error_A1_fraction_ge_0.45": admitted_error,
            "fraction_A1_equals_A2": float(np.mean(admitted[:, 0] == admitted[:, 1])),
        }
    return out


def exact_control_expectation(t: int, p: tuple[float, float, float]) -> dict[str, float]:
    """Enumerate the full first-batch multinomial law (stable log weights).

    The expectation is deterministic over every count vector. Floating-point
    arithmetic is used only for log probabilities and the Gumbel-Max
    population probabilities; there is no first-batch Monte Carlo error.
    """
    n1_parts: list[np.ndarray] = []
    n2_parts: list[np.ndarray] = []
    n3_parts: list[np.ndarray] = []
    for n1 in range(t + 1):
        n2 = np.arange(t - n1 + 1, dtype=np.int64)
        n1_parts.append(np.full(n2.size, n1, dtype=np.int64))
        n2_parts.append(n2)
        n3_parts.append(t - n1 - n2)
    n1 = np.concatenate(n1_parts)
    n2 = np.concatenate(n2_parts)
    n3 = np.concatenate(n3_parts)
    log_weights = (
        math.lgamma(t + 1)
        - np.fromiter((math.lgamma(int(n) + 1) for n in n1), dtype=np.float64)
        - np.fromiter((math.lgamma(int(n) + 1) for n in n2), dtype=np.float64)
        - np.fromiter((math.lgamma(int(n) + 1) for n in n3), dtype=np.float64)
        + n1 * math.log(p[0])
        + n2 * math.log(p[1])
        + n3 * math.log(p[2])
    )
    log_weights -= log_weights.max()
    probabilities = np.exp(log_weights)
    probabilities /= probabilities.sum()

    requested = np.column_stack((n1, n2, n3))
    capacities = np.array([t // 4, t // 4, t // 2])
    admitted = np.minimum(requested, capacities[None, :])
    costs_r = next_batch_population_overflow(p, requested, t)
    costs_a = next_batch_population_overflow(p, admitted, t)
    no_update = float(next_batch_population_overflow(p, None, t)[0])
    return {
        "request_population_overflow": float(np.dot(probabilities, costs_r)),
        "admitted_population_overflow": float(np.dot(probabilities, costs_a)),
        "no_update_population_overflow": no_update,
        "admitted_minus_requested": float(np.dot(probabilities, costs_a - costs_r)),
        "probability_mass": float(probabilities.sum()),
        "count_vectors_enumerated": int(probabilities.size),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", type=int, nargs="+", default=[40, 80, 160, 320, 640])
    parser.add_argument("--replicates", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=20261017)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/two_saturated_expert_indistinguishability/results.json"),
    )
    args = parser.parse_args()
    result = {
        "model": {
            "router": "Top-1 Gumbel-Max; iid token requests are Multinomial(T,p)",
            "world_h0_p": list(P0),
            "world_h1_p": list(P1),
            "capacities_fraction": [0.25, 0.25, 0.5],
            "capacity_sum_fraction": 1.0,
            "admission": "A_e=min(R_e,C_e)",
            "pressure_update": "Pi_g(q + eta*(signal/T - uniform_target))",
            "eta": ETA,
            "population_cost": "next-batch sum_e max(p_e(q)-C_e/T,0)",
            "finite_T_expectation": "enumerate all first-batch multinomial count vectors; float64 log weights and Gumbel-Max population cost",
            "classification_rule": "equal-prior decision: H1 iff signal_1/T >= 0.45",
            "randomness": "NumPy multinomial sampler; paired controller arms share each first-batch count vector",
        },
        "exact_law_audits": [exact_law_audit(t) for t in args.sizes],
        "optimal_policy_value_bounds": [],
        "exact_control_expectations": [
            {
                "T": t,
                "worlds": {
                    f"h{world_index}": exact_control_expectation(t, p)
                    for world_index, p in enumerate((P0, P1))
                },
            }
            for t in args.sizes
        ],
        "paired_control_audits": [
            paired_control_audit(t, args.replicates, args.seed) for t in args.sizes
        ],
    }
    for law in result["exact_law_audits"]:
        requested_witness_cost_exact = Fraction(1, 2) * (
            Fraction(law["request_h0_false_positive_probability_exact"])
            * Fraction(9, 124)
            + Fraction(law["request_h1_false_negative_probability_exact"])
            * Fraction(1, 16)
        )
        admitted_value_lower_exact = max(
            Fraction(0),
            Fraction(1, 32) - Fraction(law["admitted_TV_exact"]) / 2,
        )
        gap_lower_exact = admitted_value_lower_exact - requested_witness_cost_exact
        result["optimal_policy_value_bounds"].append(
            {
                "T": law["T"],
                "admitted_optimal_value_lower": float(admitted_value_lower_exact),
                "admitted_optimal_value_lower_exact": str(admitted_value_lower_exact),
                "admitted_optimal_value_upper": 1 / 32,
                "admitted_optimal_value_upper_exact": "1/32",
                "requested_optimal_value_lower": 0.0,
                "requested_classifier_policy_upper": float(requested_witness_cost_exact),
                "requested_classifier_policy_upper_exact": str(requested_witness_cost_exact),
                "optimal_value_gap_lower": float(gap_lower_exact),
                "optimal_value_gap_lower_exact": str(gap_lower_exact),
                "optimal_value_gap_upper": 1 / 32,
                "optimal_value_gap_upper_exact": "1/32",
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
