#!/usr/bin/env python3
"""Controlled count-law experiment for the exact arbitrary-E Top-1 family."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import binom


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "top1_arbitrary_e_exact_swapped_value"
EXPERT_COUNTS = (3, 4, 8, 16, 32, 64)
SCALES = (1, 4, 16)
REPLICATES = 2_000
MASTER_SEED = 20261017


def expected_overflow(t: int, caps: np.ndarray, p: np.ndarray) -> float:
    total = 0.0
    for cap, probability in zip(caps, p, strict=True):
        first_tail = binom.sf(int(cap) - 1, t - 1, float(probability))
        second_tail = binom.sf(int(cap), t, float(probability))
        positive_part = t * float(probability) * first_tail - int(cap) * second_tail
        total += max(0.0, float(positive_part))
    return total / t


def stderr(values: list[float]) -> float:
    return float(np.std(values, ddof=1) / math.sqrt(len(values))) if len(values) > 1 else 0.0


def exact_sign_classifier_errors(t: int, capacity_pair: int) -> tuple[float, float]:
    """Exact-law sign errors via M=R1+R2 and R1|M~Bin(M,5/9)."""
    m = np.arange(t + 1, dtype=np.int64)
    mass = binom.pmf(m, t, 9 / 13)
    conditional_p = 5 / 9
    half_floor = (m - 1) // 2
    requested = binom.cdf(half_floor, m, conditional_p)
    even = (m % 2) == 0
    requested[even] += 0.5 * binom.pmf(m[even] // 2, m[even], conditional_p)

    admitted = binom.cdf(np.minimum(capacity_pair - 1, half_floor), m, conditional_p)
    unsaturated_tie = even & ((m // 2) < capacity_pair)
    admitted[unsaturated_tie] += 0.5 * binom.pmf(
        m[unsaturated_tie] // 2, m[unsaturated_tie], conditional_p
    )
    both_saturated = m >= 2 * capacity_pair
    if np.any(both_saturated):
        upper = m[both_saturated] - capacity_pair
        tie_probability = binom.cdf(upper, m[both_saturated], conditional_p) - binom.cdf(
            capacity_pair - 1, m[both_saturated], conditional_p
        )
        admitted[both_saturated] += 0.5 * tie_probability
    return float(np.dot(mass, requested)), float(np.dot(mass, admitted))


def cell(e: int, scale: int, cell_index: int):
    n = e - 2
    denominator = 4 * n
    t = denominator * scale
    caps = np.array([t // 4, t // 4] + [t // (2 * n)] * n, dtype=np.int64)
    p0 = np.array([5 / 13, 4 / 13] + [4 / (13 * n)] * n, dtype=float)
    p1 = p0.copy()
    p1[0], p1[1] = p1[1], p1[0]
    if int(caps.sum()) != t:
        raise AssertionError("capacity mass is not T")
    if not np.isclose(float(p0.sum()), 1.0, atol=1e-15):
        raise AssertionError("request probabilities do not sum to one")
    if not np.array_equal(p1, np.r_[p0[1], p0[0], p0[2:]]):
        raise AssertionError("world probabilities are not an exact pair swap")

    # World-aware pressure matches c exactly in the true world. In world 0,
    # using the world-1 target pressure multiplies target weights by r and
    # 1/r; world 1 is its exact first-two-coordinate swap.
    c = caps.astype(float) / t
    r = 5 / 4
    wrong_world0_weights = c.copy()
    wrong_world0_weights[0] *= r
    wrong_world0_weights[1] /= r
    wrong_p0 = wrong_world0_weights / wrong_world0_weights.sum()
    wrong_p1 = wrong_p0.copy()
    wrong_p1[0], wrong_p1[1] = wrong_p1[1], wrong_p1[0]
    risk_correct = expected_overflow(t, caps, c)
    risk_wrong = expected_overflow(t, caps, wrong_p0)
    risk_wrong_world1 = expected_overflow(t, caps, wrong_p1)
    if not risk_wrong > risk_correct:
        raise AssertionError("the two-target decision loss does not penalize a wrong-world action")
    if not math.isclose(risk_wrong, risk_wrong_world1, rel_tol=0.0, abs_tol=1e-14):
        raise AssertionError("world-swap symmetry failed for wrong-target overflow")

    # Substitute exact v*=1/36 into the sharper finite-batch theorem.
    # Jensen removes any population-to-finite loss penalty on the admitted
    # lower bound; the target action's exact binomial cost remains for R.
    eps_a = binom.cdf(int(caps[0]) - 1, t, float(p0[0])) + binom.cdf(
        int(caps[1]) - 1, t, float(p0[1])
    )
    request_chernoff_base = 4 * (1 + math.sqrt(5)) / 13
    eps_r = request_chernoff_base**t
    target_batch_cost = expected_overflow(t, caps, c)
    all_policy_gap_bound = 1 / 36 - eps_a / 2 - eps_r - target_batch_cost
    exact_request_error, exact_admitted_error = exact_sign_classifier_errors(t, int(caps[0]))
    exact_request_risk = risk_correct + exact_request_error * (risk_wrong - risk_correct)
    exact_admitted_risk = risk_correct + exact_admitted_error * (risk_wrong - risk_correct)
    no_signal_risk = (risk_correct + risk_wrong) / 2

    rng = np.random.default_rng(MASTER_SEED + 10_000 * cell_index + scale)
    rows = []
    req_error, adm_error = [], []
    req_risk, adm_risk = [], []
    admitted_equal, request_equal = [], []
    for rep in range(REPLICATES):
        r0 = rng.multinomial(t, p0)
        r1 = r0.copy()
        r1[0], r1[1] = r0[1], r0[0]
        a0, a1 = np.minimum(r0, caps), np.minimum(r1, caps)
        if int(r0.sum()) != t or int(r1.sum()) != t:
            raise AssertionError("request mass is not T")
        if not np.array_equal(r1, np.r_[r0[1], r0[0], r0[2:]]):
            raise AssertionError("paired world draw is not the exact swap")

        def pair_metric(signal0: np.ndarray, signal1: np.ndarray) -> tuple[float, float]:
            d0, d1 = int(signal0[0] - signal0[1]), int(signal1[0] - signal1[1])
            if d0 > 0 and d1 < 0:
                return 0.0, risk_correct
            if d0 < 0 and d1 > 0:
                return 1.0, risk_wrong
            # A tie in both paired signals is randomized symmetrically.
            return 0.5, (risk_correct + risk_wrong) / 2

        re, rr = pair_metric(r0, r1)
        ae, ar = pair_metric(a0, a1)
        req_error.append(re)
        adm_error.append(ae)
        req_risk.append(rr)
        adm_risk.append(ar)
        admitted_equal.append(float(np.array_equal(a0, a1)))
        request_equal.append(float(np.array_equal(r0, r1)))
        rows.append(
            {
                "E": e,
                "T": t,
                "seed": MASTER_SEED + 10_000 * cell_index + scale,
                "replicate": rep,
                "requests_world0": ";".join(map(str, r0.tolist())),
                "requests_world1_paired": ";".join(map(str, r1.tolist())),
                "admitted_world0": ";".join(map(str, a0.tolist())),
                "admitted_world1_paired": ";".join(map(str, a1.tolist())),
                "request_classifier_pair_error": re,
                "admitted_classifier_pair_error": ae,
                "request_classifier_expected_next_overflow": rr,
                "admitted_classifier_expected_next_overflow": ar,
                "paired_requests_equal": bool(np.array_equal(r0, r1)),
                "paired_admitted_equal": bool(np.array_equal(a0, a1)),
            }
        )

    summary = {
        "E": e,
        "K": 1,
        "T": t,
        "capacity": caps.tolist(),
        "capacity_fraction": c.tolist(),
        "proved_population_common_action_value": 1 / 36,
        "finite_batch_all_policy_gap_lower_bound": all_policy_gap_bound,
        "finite_batch_eps_admitted": eps_a,
        "finite_batch_eps_requested": eps_r,
        "finite_batch_target_action_expected_overflow": target_batch_cost,
        "world0_request_probability": p0.tolist(),
        "world1_request_probability": p1.tolist(),
        "target_action_expected_overflow": risk_correct,
        "wrong_target_action_expected_overflow": expected_overflow(t, caps, wrong_p0),
        "wrong_action_world1_expected_overflow": risk_wrong_world1,
        "two_target_action_no_signal_expected_overflow": no_signal_risk,
        "requested_full_observation_bayes_expected_overflow": exact_request_risk,
        "admitted_full_observation_bayes_expected_overflow": exact_admitted_risk,
        "requested_signal_value_vs_no_signal": no_signal_risk - exact_request_risk,
        "admitted_signal_value_vs_no_signal": no_signal_risk - exact_admitted_risk,
        "requested_vs_admitted_bayes_value_gap": exact_admitted_risk - exact_request_risk,
        "action_class": "choose one of the two world-matched target pressures",
        "replicates": REPLICATES,
        "requested_classifier_error": float(np.mean(req_error)),
        "requested_classifier_error_se": stderr(req_error),
        "requested_classifier_exact_error": exact_request_error,
        "admitted_classifier_error": float(np.mean(adm_error)),
        "admitted_classifier_error_se": stderr(adm_error),
        "admitted_classifier_exact_error": exact_admitted_error,
        "requested_classifier_expected_overflow": float(np.mean(req_risk)),
        "requested_classifier_overflow_se": stderr(req_risk),
        "requested_classifier_exact_expected_overflow": exact_request_risk,
        "admitted_classifier_expected_overflow": float(np.mean(adm_risk)),
        "admitted_classifier_overflow_se": stderr(adm_risk),
        "admitted_classifier_exact_expected_overflow": exact_admitted_risk,
        "paired_request_equality_rate": float(np.mean(request_equal)),
        "paired_admitted_equality_rate": float(np.mean(admitted_equal)),
    }
    return summary, rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summaries, all_rows = [], []
    cell_index = 0
    for e in EXPERT_COUNTS:
        for scale in SCALES:
            result, rows = cell(e, scale, cell_index)
            summaries.append(result)
            all_rows.extend(rows)
            cell_index += 1

    payload = {
        "experiment": "exact arbitrary-E Top-1 swapped-saturation family",
        "protocol": "docs/paper/top1_arbitrary_e_exact_swapped_value_protocol_2026-10-17.md",
        "theorem": "docs/paper/top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md",
        "replicates_per_cell": REPLICATES,
        "cells": summaries,
        "interpretation_limits": [
            "Classifiers are diagnostics, not optimal finite-batch policies.",
            "The population common-action value is proved analytically, not estimated by this experiment.",
            "No hardware cost, model quality, prevalence, or active-testing separation is measured.",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if all_rows:
        with (OUT / "paired_replicates.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_rows[0]))
            writer.writeheader()
            writer.writerows(all_rows)
    for result in summaries:
        print(
            f"E={result['E']:>2} T={result['T']:>5} "
            f"req_err={result['requested_classifier_error']:.4f} "
            f"adm_err={result['admitted_classifier_error']:.4f} "
            f"req_cost={result['requested_classifier_expected_overflow']:.5f} "
            f"adm_cost={result['admitted_classifier_expected_overflow']:.5f} "
            f"A_equal={result['paired_admitted_equality_rate']:.3f}"
        )


if __name__ == "__main__":
    main()
