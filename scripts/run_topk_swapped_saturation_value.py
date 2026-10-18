#!/usr/bin/env python3
"""Controlled count-law audit for the Top-K swapped-saturation theorem."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.stats import binom


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "topk_swapped_saturation_value"
EXPERT_COUNTS = (3, 4, 6, 8)
REPLICATES = 2_000
WEIGHT = Fraction(5, 4)
SCALES = (4, 16, 64)
MASTER_SEED = 20261017


def candidate_ks(e: int) -> tuple[int, ...]:
    return tuple(sorted({1, e // 2, e - 1}))


def capacity_fractions(e: int, k: int) -> tuple[Fraction, ...]:
    uniform = Fraction(k, e)
    delta = min(uniform, 1 - uniform) / 4
    low = uniform - delta
    high = uniform + 2 * delta / (e - 2)
    return (low, low, *([high] * (e - 2)))


def subset_distribution(weights: tuple[Fraction, ...], k: int):
    """Exact unordered Top-K subset law under Gumbel/Plackett-Luce sampling."""
    e = len(weights)
    total = sum(weights)
    layer: dict[int, Fraction] = {0: Fraction(1)}
    for _ in range(k):
        next_layer: dict[int, Fraction] = {}
        for mask, probability in layer.items():
            remaining_weight = total - sum(
                weights[i] for i in range(e) if mask & (1 << i)
            )
            for i in range(e):
                if not mask & (1 << i):
                    new_mask = mask | (1 << i)
                    next_layer[new_mask] = next_layer.get(new_mask, Fraction(0)) + (
                        probability * weights[i] / remaining_weight
                    )
        layer = next_layer
    masks = tuple(sorted(layer))
    probabilities = tuple(layer[mask] for mask in masks)
    inclusion = tuple(
        sum(prob for mask, prob in layer.items() if mask & (1 << i))
        for i in range(e)
    )
    assert sum(probabilities) == 1
    assert sum(inclusion) == k
    return masks, probabilities, inclusion


def float_inclusion(logits: np.ndarray, k: int) -> np.ndarray:
    e = len(logits)
    weights = np.exp(logits - np.max(logits))
    total = float(weights.sum())
    layer = {0: 1.0}
    for _ in range(k):
        next_layer: dict[int, float] = {}
        for mask, probability in layer.items():
            remaining_weight = total - sum(
                weights[i] for i in range(e) if mask & (1 << i)
            )
            for i in range(e):
                if not mask & (1 << i):
                    new_mask = mask | (1 << i)
                    next_layer[new_mask] = next_layer.get(new_mask, 0.0) + (
                        probability * weights[i] / remaining_weight
                    )
        layer = next_layer
    return np.array(
        [sum(prob for mask, prob in layer.items() if mask & (1 << i)) for i in range(e)],
        dtype=float,
    )


def target_score(capacities: np.ndarray, k: int) -> tuple[np.ndarray, float]:
    e = len(capacities)

    def residual(head: np.ndarray) -> np.ndarray:
        logits = np.concatenate((head, np.zeros(1)))
        return float_inclusion(logits, k)[:-1] - capacities[:-1]

    result = least_squares(
        residual,
        np.log(capacities[:-1] / (1 - capacities[:-1])),
        xtol=1e-13,
        ftol=1e-13,
        gtol=1e-13,
        max_nfev=20_000,
    )
    logits = np.concatenate((result.x, np.zeros(1)))
    residual_norm = float(np.max(np.abs(float_inclusion(logits, k) - capacities)))
    if not result.success or residual_norm > 1e-8:
        raise RuntimeError(f"target solve failed: success={result.success}, residual={residual_norm}")
    return logits, residual_norm


def expected_overflow(t: int, caps: np.ndarray, inclusion: np.ndarray, k: int) -> float:
    """Exact binomial-marginal expectation, normalized by K*T."""
    total = 0.0
    for cap, probability in zip(caps, inclusion, strict=True):
        if probability <= 0.0:
            continue
        first_tail = binom.sf(int(cap) - 1, t - 1, probability)
        second_tail = binom.sf(int(cap), t, probability)
        positive_part = t * probability * first_tail - int(cap) * second_tail
        total += max(0.0, float(positive_part))
    return total / (k * t)


def exact_bayes_errors(
    t: int, pair_capacity: int, p_plus: float, p_minus: float, p_both: float
) -> tuple[float, float]:
    """Exact Bayes errors for full R and full A in the swapped-pair family.

    Each token contributes (+1,-1,0) to R1-R2. Conditional on M asymmetric
    tokens, the plus count is binomial; among the other tokens, the number
    selecting both experts is independently binomial. Equal first-two caps
    make the full admitted-vector Bayes rule the sign of A1-A2.
    """
    pair_mass = p_plus + p_minus
    neutral_mass = 1.0 - pair_mass
    if not (0.0 < p_minus < p_plus and neutral_mass > 0.0 and 0.0 <= p_both <= neutral_mass):
        raise ValueError("invalid swapped-pair subset probabilities")

    m_values = np.arange(t + 1, dtype=np.int64)
    m_mass = binom.pmf(m_values, t, pair_mass)
    conditional_plus = p_plus / pair_mass
    request_conditional_error = binom.cdf((m_values - 1) // 2, m_values, conditional_plus)
    even = (m_values % 2) == 0
    request_conditional_error[even] += 0.5 * binom.pmf(
        m_values[even] // 2, m_values[even], conditional_plus
    )
    request_error = float(np.dot(m_mass, request_conditional_error))

    conditional_both = p_both / neutral_mass
    admitted_error = 0.0
    for m, mass_m in enumerate(m_mass):
        if mass_m == 0.0:
            continue
        n_plus = np.arange(m + 1, dtype=np.int64)
        plus_mass = binom.pmf(n_plus, m, conditional_plus)
        n_minus = m - n_plus
        tie = n_plus == n_minus
        error_given_pair_counts = np.empty(m + 1, dtype=float)
        error_given_pair_counts[tie] = 0.5

        lower = n_plus < n_minus
        if np.any(lower):
            threshold = pair_capacity - n_plus[lower]
            tail_tie = binom.sf(threshold - 1, t - m, conditional_both)
            # Below this threshold the clipped pair preserves the wrong sign;
            # at or above it both experts saturate and the decision ties.
            error_given_pair_counts[lower] = 1.0 - 0.5 * tail_tie

        higher = n_plus > n_minus
        if np.any(higher):
            threshold = pair_capacity - n_minus[higher]
            tail_tie = binom.sf(threshold - 1, t - m, conditional_both)
            error_given_pair_counts[higher] = 0.5 * tail_tie

        admitted_error += float(mass_m) * float(np.dot(plus_mass, error_given_pair_counts))

    return request_error, admitted_error


def standard_error(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return float(np.std(values, ddof=1) / math.sqrt(len(values)))


def one_cell(e: int, k: int, cell_index: int):
    caps_fraction = capacity_fractions(e, k)
    denominator = math.lcm(*(value.denominator for value in caps_fraction))
    caps_float = np.array([float(value) for value in caps_fraction])
    weights0 = (WEIGHT,) + (Fraction(1),) * (e - 1)
    weights1 = (Fraction(1), WEIGHT) + (Fraction(1),) * (e - 2)
    masks, subset_probs_fraction, inclusion0_fraction = subset_distribution(weights0, k)
    _, _, inclusion1_fraction = subset_distribution(weights1, k)
    p0 = np.array([float(x) for x in inclusion0_fraction])
    p1 = np.array([float(x) for x in inclusion1_fraction])

    if not (p0[0] > p0[1] and p0[0] > caps_float[0] and p0[1] > caps_float[1]):
        raise RuntimeError(f"saturation/ordering condition failed for E={e}, K={k}")
    if not all(p0[j] < caps_float[j] for j in range(2, e)):
        raise RuntimeError(f"unsaturated expert condition failed for E={e}, K={k}")
    if tuple(inclusion1_fraction) != (inclusion0_fraction[1], inclusion0_fraction[0], *inclusion0_fraction[2:]):
        raise RuntimeError("world laws do not satisfy exact swap symmetry")

    target_logits, target_residual = target_score(caps_float, k)
    theta0 = np.log(np.array([float(x) for x in weights0]))
    theta1 = np.log(np.array([float(x) for x in weights1]))
    q0 = theta0 - target_logits
    q1 = theta1 - target_logits
    q0 -= q0.mean()
    q1 -= q1.mean()

    subset_probabilities = np.array([float(p) for p in subset_probs_fraction], dtype=float)
    subset_probabilities /= subset_probabilities.sum()
    p_plus_fraction = sum(
        (prob for mask, prob in zip(masks, subset_probs_fraction, strict=True)
         if mask & 1 and not mask & 2),
        Fraction(0),
    )
    p_minus_fraction = sum(
        (prob for mask, prob in zip(masks, subset_probs_fraction, strict=True)
         if mask & 2 and not mask & 1),
        Fraction(0),
    )
    p_both_fraction = sum(
        (prob for mask, prob in zip(masks, subset_probs_fraction, strict=True)
         if mask & 1 and mask & 2),
        Fraction(0),
    )
    one_only_masks = [
        (mask, prob) for mask, prob in zip(masks, subset_probs_fraction, strict=True)
        if bool(mask & 1) != bool(mask & 2)
    ]
    plus_orbit = {prob for mask, prob in one_only_masks if mask & 1}
    minus_orbit = {prob for mask, prob in one_only_masks if mask & 2}
    if len(plus_orbit) != 1 or len(minus_orbit) != 1 or not p_plus_fraction > p_minus_fraction:
        raise AssertionError("swapped-pair likelihood ratio is not constant and ordered on subset orbits")
    mask_membership = np.array(
        [[bool(mask & (1 << i)) for i in range(e)] for mask in masks], dtype=np.int8
    )

    rows: list[dict[str, object]] = []
    replicate_rows: list[dict[str, object]] = []
    for scale_index, scale in enumerate(SCALES):
        t = denominator * scale
        caps = np.array([int(value * t) for value in caps_fraction], dtype=np.int64)
        if int(caps.sum()) != k * t:
            raise AssertionError("integer capacities do not sum to K*T")

        inclusion_by_world_action = np.empty((2, 2, e), dtype=float)
        for world, theta in enumerate((theta0, theta1)):
            for action, pressure in enumerate((q0, q1)):
                inclusion_by_world_action[world, action] = float_inclusion(theta - pressure, k)
        risk = np.empty((2, 2), dtype=float)
        for world in range(2):
            for action in range(2):
                risk[world, action] = expected_overflow(
                    t, caps, inclusion_by_world_action[world, action], k
                )

        q_zero_inclusion = (p0, p1)
        no_update_risk = sum(
            expected_overflow(t, caps, q_zero_inclusion[world], k) for world in range(2)
        ) / 2
        fixed_world0_risk = (risk[0, 0] + risk[1, 0]) / 2
        correct_signal_risk = (risk[0, 0] + risk[1, 1]) / 2
        wrong_signal_risk = (risk[0, 1] + risk[1, 0]) / 2
        common_action_upper_v = (risk[0, 0] + risk[1, 0]) / 2
        if not wrong_signal_risk > correct_signal_risk:
            raise AssertionError("wrong target action must have higher expected overflow")
        request_bayes_error, admitted_bayes_error = exact_bayes_errors(
            t, int(caps[0]), float(p_plus_fraction), float(p_minus_fraction), float(p_both_fraction)
        )
        no_signal_two_action_risk = (correct_signal_risk + wrong_signal_risk) / 2
        request_bayes_risk = correct_signal_risk + request_bayes_error * (
            wrong_signal_risk - correct_signal_risk
        )
        admitted_bayes_risk = correct_signal_risk + admitted_bayes_error * (
            wrong_signal_risk - correct_signal_risk
        )

        seed = MASTER_SEED + 100_000 * cell_index + scale_index
        rng = np.random.default_rng(seed)
        admitted_equal: list[float] = []
        unclipped_equal: list[float] = []
        requested_error: list[float] = []
        admitted_error: list[float] = []
        requested_risk: list[float] = []
        admitted_risk: list[float] = []
        mass_ok = True
        no_clip_identity_ok = True

        for replicate in range(REPLICATES):
            subset_counts = rng.multinomial(t, subset_probabilities)
            request0 = subset_counts @ mask_membership
            request1 = request0.copy()
            request1[0], request1[1] = request0[1], request0[0]
            mass_ok &= int(request0.sum()) == k * t and int(request1.sum()) == k * t
            admit0 = np.minimum(request0, caps)
            admit1 = np.minimum(request1, caps)
            admit_no_clip0 = np.minimum(request0, np.full(e, t, dtype=np.int64))
            no_clip_identity_ok &= np.array_equal(request0, admit_no_clip0)
            admitted_equal.append(float(np.array_equal(admit0, admit1)))
            unclipped_equal.append(float(np.array_equal(request0, request1)))

            d_request = int(request0[0] - request0[1])
            if d_request > 0:
                request_error, request_loss = 0.0, correct_signal_risk
            elif d_request < 0:
                request_error, request_loss = 1.0, wrong_signal_risk
            else:
                request_error, request_loss = 0.5, (correct_signal_risk + wrong_signal_risk) / 2
            requested_error.append(request_error)
            requested_risk.append(request_loss)

            d_admitted = int(admit0[0] - admit0[1])
            if d_admitted > 0:
                admitted_err, admitted_loss = 0.0, correct_signal_risk
            elif d_admitted < 0:
                admitted_err, admitted_loss = 1.0, wrong_signal_risk
            else:
                admitted_err, admitted_loss = 0.5, (correct_signal_risk + wrong_signal_risk) / 2
            admitted_error.append(admitted_err)
            admitted_risk.append(admitted_loss)
            replicate_rows.append(
                {
                    "E": e,
                    "K": k,
                    "T": t,
                    "seed": seed,
                    "replicate": replicate,
                    "request_world0": request0.tolist(),
                    "request_world1_coupled": request1.tolist(),
                    "admitted_world0": admit0.tolist(),
                    "admitted_world1_coupled": admit1.tolist(),
                    "request_classifier_pair_error": request_error,
                    "admitted_classifier_pair_error": admitted_err,
                    "request_classifier_pair_expected_overflow": request_loss,
                    "admitted_classifier_pair_expected_overflow": admitted_loss,
                    "paired_admitted_vectors_equal": bool(np.array_equal(admit0, admit1)),
                    "paired_unclipped_vectors_equal": bool(np.array_equal(request0, request1)),
                }
            )

        margins = [p0[0] - caps_float[0], p0[1] - caps_float[1]] + [
            caps_float[j] - p0[j] for j in range(2, e)
        ]
        delta_p = float(p0[0] - p0[1])
        eps_a = sum(math.exp(-2 * t * margin * margin) for margin in margins)
        eps_r = math.exp(-t * delta_p * delta_p / 2)

        row: dict[str, object] = {
            "E": e,
            "K": k,
            "T": t,
            "replicates": REPLICATES,
            "seed": seed,
            "capacity_fraction": [str(value) for value in caps_fraction],
            "capacity_integer": [int(value) for value in caps],
            "inclusion_world0": [float(x) for x in p0],
            "inclusion_world1": [float(x) for x in p1],
            "request_mean_gap_delta": delta_p,
            "minimum_saturation_margin": min(margins[:2]),
            "minimum_unsaturated_margin": min(margins[2:]),
            "hoeffding_admitted_tv_upper": eps_a,
            "hoeffding_request_classifier_error_upper": eps_r,
            "population_target_solver_residual": target_residual,
            "no_update_expected_overflow": no_update_risk,
            "fixed_world0_action_expected_overflow": fixed_world0_risk,
            "world_aware_target_expected_overflow": correct_signal_risk,
            "wrong_target_expected_overflow": wrong_signal_risk,
            "two_target_action_no_signal_expected_overflow": no_signal_two_action_risk,
            "request_bayes_error_exact": request_bayes_error,
            "admitted_bayes_error_exact": admitted_bayes_error,
            "request_bayes_expected_overflow_exact": request_bayes_risk,
            "admitted_bayes_expected_overflow_exact": admitted_bayes_risk,
            "request_signal_value_vs_no_signal_exact": no_signal_two_action_risk - request_bayes_risk,
            "admitted_signal_value_vs_no_signal_exact": no_signal_two_action_risk - admitted_bayes_risk,
            "request_vs_admitted_bayes_gap_exact": admitted_bayes_risk - request_bayes_risk,
            "pair_subset_probabilities_exact": {
                "plus": str(p_plus_fraction),
                "minus": str(p_minus_fraction),
                "both": str(p_both_fraction),
                "neither": str(1 - p_plus_fraction - p_minus_fraction - p_both_fraction),
            },
            "requested_classifier_overflow_mean": float(np.mean(requested_risk)),
            "requested_classifier_overflow_mc_se": standard_error(requested_risk),
            "requested_classifier_error_mean": float(np.mean(requested_error)),
            "requested_classifier_error_mc_se": standard_error(requested_error),
            "admitted_classifier_overflow_mean": float(np.mean(admitted_risk)),
            "admitted_classifier_overflow_mc_se": standard_error(admitted_risk),
            "admitted_classifier_error_mean": float(np.mean(admitted_error)),
            "admitted_classifier_error_mc_se": standard_error(admitted_error),
            "paired_admitted_vector_equality_rate": float(np.mean(admitted_equal)),
            "paired_unclipped_vector_equality_rate": float(np.mean(unclipped_equal)),
            "same_world_no_clipping_identity_pass": no_clip_identity_ok,
            "common_action_feasible_upper_bound_on_v_star": common_action_upper_v,
            "mass_conservation_pass": mass_ok,
        }
        rows.append(row)
    return rows, replicate_rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    replicate_rows = []
    cell_index = 0
    for e in EXPERT_COUNTS:
        for k in candidate_ks(e):
            cell_rows, cell_replicates = one_cell(e, k, cell_index)
            rows.extend(cell_rows)
            replicate_rows.extend(cell_replicates)
            cell_index += 1

    if any(not row["mass_conservation_pass"] for row in rows):
        raise RuntimeError("mass conservation check failed")
    if any(float(row["population_target_solver_residual"]) > 1e-8 for row in rows):
        raise RuntimeError("target solver residual check failed")

    csv_path = OUT / "controlled_cells.csv"
    fieldnames = list(rows[0])
    import csv

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    raw_path = OUT / "paired_replicates.csv"
    raw_fields = list(replicate_rows[0])
    with raw_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=raw_fields)
        writer.writeheader()
        writer.writerows(replicate_rows)

    summary = {
        "experiment": "Top-K swapped-saturation signal-value audit",
        "design": {
            "expert_counts": list(EXPERT_COUNTS),
            "K_rule": "deduplicated {1, floor(E/2), E-1}",
            "base_weight_favored_expert": str(WEIGHT),
            "scales_times_capacity_denominator": list(SCALES),
            "replicates_per_cell": REPLICATES,
            "master_seed": MASTER_SEED,
            "cell_count": len(rows),
            "paired_replicate_count": len(replicate_rows),
        },
        "checks": {
            "all_mass_conservation_pass": all(bool(row["mass_conservation_pass"]) for row in rows),
            "all_target_solver_residuals_below_1e-8": all(
                float(row["population_target_solver_residual"]) <= 1e-8 for row in rows
            ),
            "all_same_world_no_clipping_identities_pass": all(
                bool(row["same_world_no_clipping_identity_pass"]) for row in rows
            ),
            "all_strict_saturation_and_unsaturated_margins_pass": all(
                float(row["minimum_saturation_margin"]) > 0
                and float(row["minimum_unsaturated_margin"]) > 0
                for row in rows
            ),
            "exact_world_swap_verified": True,
            "per_expert_clipping_applied": True,
        },
        "interpretation_guardrails": [
            "The Monte Carlo policy metrics evaluate the registered sign classifiers, not optimal policies.",
            "The common-action value is a feasible-action upper bound on v_star, not a lower bound or certified optimum.",
            "The strict positive v_star and optimal-policy value gap come from the theorem proof, not the simulation.",
            "No hardware telemetry price, real-router performance, or benchmark separation is measured.",
        ],
        "rows": rows,
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"cells={len(rows)} rows={len(rows)} replicates_per_row={REPLICATES}")
    print(f"summary={summary_path}")
    print(f"csv={csv_path}")
    print(f"paired_replicates={raw_path}")
    print(f"checks={json.dumps(summary['checks'], sort_keys=True)}")


if __name__ == "__main__":
    main()
