"""Controlled numerical check for symmetric pair-skew Top-K value scaling.

The deterministic population calculation compares a 2-D global optimizer of
the common-action overflow objective with the analytic first-order
coefficient. A finite Plackett-Luce prefix-sum grid audits the general E,K
sensitivity formula. A paired multinomial simulation checks request-sign
identification and admitted-vector aliasing for the rational E=3,K=2 profile.
Numerical optimization and Monte Carlo are diagnostics, not proofs.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution
from scipy.integrate import quad
from scipy.stats import binom


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "topk_small_skew_scaling_2026-10-18"
EPSILONS = (0.04, 0.02, 0.01, 0.005)
CAPACITIES = (0.55, 0.65, 0.80)
BASELINE_MARGINS = (0.04, 0.08)
MC_EPSILONS = (0.04, 0.02, 0.01)
MC_BATCHES = (1000, 5000, 20000)
MC_REPLICATES = 20000
JOINT_BATCHES = (20000, 160000, 1280000)
ROOT_SEED = 20261018
PAIR_RATIOS = (1.0 / 3.0, 1.0, 3.0)


def x_of_ratio(r: float) -> float:
    return (4.0 * r * r + 3.0 * r + 1.0) / (2.0 * (r + 1.0) * (2.0 * r + 1.0))


def ratio_for_x(x: float) -> float:
    disc = (6.0 * x - 3.0) ** 2 + 16.0 * (1.0 - x) * (2.0 * x - 1.0)
    return ((6.0 * x - 3.0) + math.sqrt(disc)) / (8.0 * (1.0 - x))


def j_of_ratio(r: float) -> float:
    return (5.0 * r * r + 4.0 * r + 1.0) / (2.0 * (r + 1.0) ** 2 * (2.0 * r + 1.0))


def pair_inclusion_and_sensitivity(e: int, k: int, r: float, eps: float = 0.0) -> tuple[float, float]:
    """Finite PL-prefix sum for x_(E,K)(r) and its antisymmetric derivative."""
    weights = np.array([r * math.exp(eps), r * math.exp(-eps), *([1.0] * (e - 2))], dtype=np.float64)
    direction = np.array([1.0, -1.0, *([0.0] * (e - 2))], dtype=np.float64)
    omission = 0.0
    omission_derivative = 0.0
    for prefix in itertools.permutations(range(1, e), k):
        remaining = list(range(e))
        probability = 1.0
        log_score_derivative = 0.0
        for item in prefix:
            denom = float(weights[remaining].sum())
            log_score_derivative += float(direction[item] - np.dot(weights[remaining], direction[remaining]) / denom)
            probability *= float(weights[item]) / denom
            remaining.remove(item)
        omission += probability
        omission_derivative += probability * log_score_derivative
    return 1.0 - omission, -omission_derivative


def pair_sensitivity_dp(e: int, k: int, r: float) -> tuple[float, float]:
    """O(K) two-state DP, aggregating the E-2 identical tail experts."""
    n = e - 2
    a = b = r
    da, db = r, -r
    # State h=0: expert 2 not selected; h=1: it has been selected.
    p = np.array([1.0, 0.0], dtype=np.float64)
    dp = np.array([0.0, 0.0], dtype=np.float64)
    for selected in range(k):
        pn = np.zeros(2, dtype=np.float64)
        dpn = np.zeros(2, dtype=np.float64)
        for h in (0, 1):
            if p[h] == 0.0 and dp[h] == 0.0:
                continue
            tails_remaining = n - (selected - h)
            if tails_remaining < 0:
                continue
            denom = a + (1 - h) * b + tails_remaining
            ddenom = da + (1 - h) * db
            if h == 0:
                prob_expert2 = b / denom
                dprob_expert2 = db / denom - b * ddenom / (denom * denom)
                pn[1] += p[h] * prob_expert2
                dpn[1] += dp[h] * prob_expert2 + p[h] * dprob_expert2
            if tails_remaining:
                prob_tail = tails_remaining / denom
                dprob_tail = -tails_remaining * ddenom / (denom * denom)
                pn[h] += p[h] * prob_tail
                dpn[h] += dp[h] * prob_tail + p[h] * dprob_tail
        p, dp = pn, dpn
    omission = float(p.sum())
    omission_derivative = float(dp.sum())
    return 1.0 - omission, -omission_derivative


def _standard_gumbel_pdf(x: float) -> float:
    if x < -50.0:
        return 0.0
    z = math.exp(-x)
    return z * math.exp(-z)


def _standard_gumbel_survival(x: float) -> float:
    if x < -50.0:
        return 1.0
    if x > 50.0:
        return math.exp(-x)
    return -math.expm1(-math.exp(-x))


def _top2_root_facet_weight(s_a: float, s_b: float, s_c: float) -> float:
    """Density flux through the facet where a,b tie below c (E=3,K=2)."""
    value, error = quad(
        lambda t: _standard_gumbel_pdf(t - s_a)
        * _standard_gumbel_pdf(t - s_b)
        * _standard_gumbel_survival(t - s_c),
        -np.inf,
        np.inf,
        epsabs=2e-13,
        epsrel=2e-13,
        limit=300,
    )
    assert error < 1e-10
    return float(value)


def root_facet_sensitivity_grid() -> list[dict[str, object]]:
    """Independent root-facet integral for the symmetric E=3,K=2 slope."""
    rows: list[dict[str, object]] = []
    for r in PAIR_RATIOS:
        s = math.log(r)
        w12 = _top2_root_facet_weight(s, s, 0.0)
        w13 = _top2_root_facet_weight(s, 0.0, s)
        w23 = _top2_root_facet_weight(0.0, s, s)
        # d=e1-e2; root pair (1,2) has squared pairing 4, and (1,3),(2,3)
        # each have squared pairing 1. j is one half of d^T Hessian d.
        j_facet = 2.0 * w12 + 0.5 * (w13 + w23)
        _, j_prefix = pair_sensitivity_dp(3, 2, r)
        rows.append(
            {
                "E": 3,
                "K": 2,
                "pair_ratio_r": r,
                "facet_flux_12": w12,
                "facet_flux_13": w13,
                "facet_flux_23": w23,
                "root_facet_sensitivity_j": j_facet,
                "prefix_dp_sensitivity_j": j_prefix,
                "absolute_difference": abs(j_facet - j_prefix),
                "relative_difference": abs(j_facet - j_prefix) / j_prefix,
            }
        )
    return rows


def expected_clipped_binomial(t: int, p: float, capacity: int) -> float:
    """Exact finite-sum expectation E[min(Binomial(t,p), capacity)]."""
    if capacity <= 0:
        return 0.0
    # E[min(X,C)] = sum_{k=1}^C Pr[X >= k].
    return float(np.sum(binom.sf(np.arange(capacity), t, p)))


def clipping_attenuation_grid() -> list[dict[str, object]]:
    """Check the exact Top-K Jacobian x binomial-clipping attenuation bridge.

    Each cell uses symmetric pair logits (log r, log r, 0, ...), an
    antisymmetric score perturbation e1-e2, and exact-total integer
    capacities. The finite difference is computed from exact binomial
    expectations, independently of the analytic alpha_T formula.
    """
    rows: list[dict[str, object]] = []
    eps = 2e-5
    for e in (3, 4, 8):
        ks = sorted({1, max(1, e // 2), e - 1})
        for k in ks:
            for r in PAIR_RATIOS:
                x, j = pair_sensitivity_dp(e, k, r)
                tail = (k - 2.0 * x) / (e - 2)
                # Keep a positive pair overload margin while leaving all
                # identical tail experts strictly below their capacities.
                margin = min(0.05, x / 4.0, (e - 2) * (1.0 - tail) / 4.0)
                assert margin > 0.0 and tail + 2.0 * margin / (e - 2) < 1.0
                c_pair = x - margin
                for t in (600, 1500, 3000):
                    cap_pair = int(math.floor(t * c_pair))
                    residual = k * t - 2 * cap_pair
                    q_tail, r_tail = divmod(residual, e - 2)
                    caps = [cap_pair, cap_pair] + [
                        q_tail + int(idx < r_tail) for idx in range(e - 2)
                    ]
                    assert sum(caps) == k * t and all(1 <= c <= t for c in caps)
                    assert all(c / t > tail for c in caps[2:])

                    p_plus, _ = pair_inclusion_and_sensitivity(e, k, r, eps)
                    p_minus, _ = pair_inclusion_and_sensitivity(e, k, r, -eps)
                    request_fd = (p_plus - p_minus) / (eps * k)
                    alpha = float(binom.cdf(cap_pair - 1, t - 1, x))
                    m_plus = expected_clipped_binomial(t, p_plus, cap_pair)
                    m_minus = expected_clipped_binomial(t, p_minus, cap_pair)
                    admitted_fd = (m_plus - m_minus) / (t * eps * k)
                    predicted_request = 2.0 * j / k
                    predicted_admitted = alpha * predicted_request
                    rows.append(
                        {
                            "E": e,
                            "K": k,
                            "pair_weight_ratio_r": r,
                            "T": t,
                            "pair_request_probability_x": x,
                            "pair_capacity_fraction": cap_pair / t,
                            "pair_overload_margin": x - cap_pair / t,
                            "tail_capacity_fractions": ";".join(
                                f"{c / t:.12g}" for c in caps[2:]
                            ),
                            "capacity_sum_exact": sum(caps),
                            "capacity_total_KT": k * t,
                            "topk_sensitivity_j": j,
                            "analytic_request_contrast_slope": predicted_request,
                            "finite_difference_request_contrast_slope": request_fd,
                            "binomial_attenuation_alpha": alpha,
                            "analytic_admitted_contrast_slope": predicted_admitted,
                            "finite_difference_admitted_contrast_slope": admitted_fd,
                            "finite_difference_attenuation_ratio": admitted_fd / request_fd,
                            "request_slope_abs_error": abs(request_fd - predicted_request),
                            "admitted_slope_abs_error": abs(admitted_fd - predicted_admitted),
                        }
                    )
    return rows


def pair_sensitivity_grid() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    h = 1e-4
    for e in range(3, 9):
        for k in range(1, e):
            for r in PAIR_RATIOS:
                x, j = pair_inclusion_and_sensitivity(e, k, r)
                x_dp, j_dp = pair_sensitivity_dp(e, k, r)
                x_plus, _ = pair_inclusion_and_sensitivity(e, k, r, h)
                j_half_step = pair_inclusion_and_sensitivity(e, k, r, h / 2.0)[1]
                x_double, _ = pair_inclusion_and_sensitivity(e, k, 2.0 * r)
                tail = (k - 2.0 * x) / (e - 2)
                finite_difference_j = (x_plus - pair_inclusion_and_sensitivity(e, k, r, -h)[0]) / (2.0 * h)
                relative_error = abs(finite_difference_j - j) / max(abs(j), 1e-15)
                assert j > 0.0 and x_double > x and 0.0 < tail < 1.0
                assert abs(x_dp - x) <= 1e-12 and abs(j_dp - j) / j <= 1e-11
                rows.append(
                    {
                        "E": e,
                        "K": k,
                        "target_ratio_r": r,
                        "pair_target_capacity_x": x,
                        "tail_target_capacity_y": tail,
                        "baseline_ratio_u": 2.0 * r,
                        "baseline_pair_margin": x_double - x,
                        "exact_prefix_sum_sensitivity_j": j,
                        "two_state_dp_sensitivity_j": j_dp,
                        "prefix_dp_relative_error": abs(j_dp - j) / j,
                        "capacity_value_slope_j_over_K": j / k,
                        "central_difference_j_h_1e-4": finite_difference_j,
                        "analytic_vs_finite_difference_relative_error": relative_error,
                        "half_step_relative_change": abs(j_half_step - j) / max(abs(j), 1e-15),
                    }
                )
    return rows


def large_pair_sensitivity_grid() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for e in (8, 16, 32, 64, 128, 256, 512):
        ks = sorted({1, max(1, e // 4), max(1, e // 2), e - 1})
        for k in ks:
            for r in PAIR_RATIOS:
                x, j = pair_sensitivity_dp(e, k, r)
                y = (k - 2.0 * x) / (e - 2)
                x_base, _ = pair_sensitivity_dp(e, k, 2.0 * r)
                rows.append(
                    {
                        "E": e,
                        "K": k,
                        "target_ratio_r": r,
                        "pair_target_capacity_x": x,
                        "tail_target_capacity_y": y,
                        "baseline_pair_margin": x_base - x,
                        "pair_sensitivity_j": j,
                        "capacity_value_slope_j_over_K": j / k,
                    }
                )
    return rows


def inclusion_from_logits(logits: np.ndarray) -> np.ndarray:
    """Exact E=3,K=2 Plackett-Luce inclusion probabilities."""
    w = np.exp(logits - np.max(logits))
    out = np.empty(3, dtype=np.float64)
    total = float(w.sum())
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        omit_i = (w[j] * w[k] / total) * (1.0 / (w[i] + w[k]) + 1.0 / (w[i] + w[j]))
        out[i] = 1.0 - omit_i
    return out


def normalized_overflow(probabilities: np.ndarray, capacities: np.ndarray) -> float:
    # Sum capacities and inclusion probabilities are both K=2; normalized
    # overflow is sum of positive excess divided by K.
    return float(np.maximum(probabilities - capacities, 0.0).sum() / 2.0)


def common_action_objective(q12: np.ndarray, theta_bar: np.ndarray, eps: float, c: float) -> float:
    q = np.array([q12[0], q12[1], 0.0], dtype=np.float64)
    cap = np.array([c, c, 2.0 - 2.0 * c], dtype=np.float64)
    d = np.array([1.0, -1.0, 0.0], dtype=np.float64)
    plus = inclusion_from_logits(theta_bar + eps * d - q)
    minus = inclusion_from_logits(theta_bar - eps * d - q)
    return 0.5 * (normalized_overflow(plus, cap) + normalized_overflow(minus, cap))


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = successes / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def deterministic_cells() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for c in CAPACITIES:
        rc = ratio_for_x(c)
        theta_c = np.array([math.log(rc), math.log(rc), 0.0])
        coefficient = j_of_ratio(rc) / 2.0
        for margin in BASELINE_MARGINS:
            if c + margin >= 1.0:
                continue
            u = ratio_for_x(c + margin)
            theta_bar = np.array([math.log(u), math.log(u), 0.0])
            q0 = np.array([math.log(u / rc), math.log(u / rc)])
            for eps in EPSILONS:
                value_at_q0 = common_action_objective(q0, theta_bar, eps, c)
                result = differential_evolution(
                    common_action_objective,
                    bounds=[(q0[0] - 3.0, q0[0] + 3.0), (q0[1] - 3.0, q0[1] + 3.0)],
                    args=(theta_bar, eps, c),
                    seed=ROOT_SEED + len(rows),
                    maxiter=500,
                    popsize=16,
                    tol=1e-11,
                    atol=1e-13,
                    polish=True,
                    updating="immediate",
                    workers=1,
                )
                min_pair_margin = min(
                    inclusion_from_logits(theta_bar + eps * np.array([1.0, -1.0, 0.0]))[:2] - c
                )
                contrast = float(
                    inclusion_from_logits(theta_bar + eps * np.array([1.0, -1.0, 0.0]))[0]
                    - inclusion_from_logits(theta_bar + eps * np.array([1.0, -1.0, 0.0]))[1]
                )
                rows.append(
                    {
                        "capacity_pair": c,
                        "baseline_pair_margin_at_zero": margin,
                        "target_ratio_rc": rc,
                        "baseline_ratio_u": u,
                        "epsilon": eps,
                        "analytic_slope_j_over_2": coefficient,
                        "optimized_common_value": float(result.fun),
                        "q0_common_value_upper_bound": value_at_q0,
                        "optimized_value_over_epsilon": float(result.fun) / eps,
                        "slope_abs_error": abs(float(result.fun) / eps - coefficient),
                        "optimizer_q1": float(result.x[0]),
                        "optimizer_q2": float(result.x[1]),
                        "optimizer_success": bool(result.success),
                        "optimizer_nfev": int(result.nfev),
                        "initial_min_pair_saturation_margin": float(min_pair_margin),
                        "initial_request_contrast": contrast,
                        "linear_request_contrast_prediction": 2.0 * j_of_ratio(u) * eps,
                    }
                )
    return rows


def monte_carlo_cells() -> list[dict[str, object]]:
    # Match the exact rational profile in the theorem: c=11/20, u=2/3.
    c = 11.0 / 20.0
    u = 2.0 / 3.0
    rows: list[dict[str, object]] = []
    for eps in MC_EPSILONS:
        logits = np.array([math.log(u) + eps, math.log(u) - eps, 0.0])
        probs = inclusion_from_logits(logits)
        omitted = 1.0 - probs
        min_margin = float(np.min(probs[:2] - c))
        request_contrast = float(probs[0] - probs[1])
        for t in MC_BATCHES:
            capacities = np.array([int(round(c * t)), int(round(c * t)), int(round((2.0 - 2.0 * c) * t))])
            assert int(capacities.sum()) == 2 * t
            rng = np.random.default_rng(ROOT_SEED + t + int(eps * 1_000_000))
            omitted_counts = rng.multinomial(t, omitted, size=MC_REPLICATES)
            requests = t - omitted_counts
            request_errors = int(np.count_nonzero((requests[:, 0] - requests[:, 1]) <= 0))
            swapped_requests = requests[:, [1, 0, 2]]
            admitted = np.minimum(requests, capacities)
            swapped_admitted = np.minimum(swapped_requests, capacities)
            aliases = int(np.count_nonzero(np.all(admitted == swapped_admitted, axis=1)))
            lo, hi = wilson_interval(request_errors, MC_REPLICATES)
            rows.append(
                {
                    "capacity_pair": c,
                    "baseline_ratio_u": u,
                    "epsilon": eps,
                    "T": t,
                    "replicates": MC_REPLICATES,
                    "request_contrast_mean_exact": request_contrast,
                    "request_sign_error_count": request_errors,
                    "request_sign_error_rate": request_errors / MC_REPLICATES,
                    "request_sign_error_wilson95_low": lo,
                    "request_sign_error_wilson95_high": hi,
                    "request_sign_hoeffding_upper": math.exp(-t * request_contrast**2 / 2.0),
                    "admitted_pair_alias_count": aliases,
                    "admitted_pair_alias_rate": aliases / MC_REPLICATES,
                    "pair_saturation_min_margin": min_margin,
                    "admitted_alias_failure_hoeffding_upper": min(1.0, 2.0 * math.exp(-2.0 * t * min_margin**2)),
                }
            )
    return rows


def priced_decision_cells() -> list[dict[str, object]]:
    """Paired finite-batch check of telemetry value in a declared action class.

    The action class contains only the two pressures that exactly match the
    capacity target in one of the two swapped worlds. Signal policies use the
    signed count difference, randomizing on ties. This is a controlled policy
    comparison, not an estimate of the unrestricted optimal value.
    """
    c = 11.0 / 20.0
    u = 2.0 / 3.0
    rc = ratio_for_x(c)
    cap = np.array([c, c, 2.0 - 2.0 * c], dtype=np.float64)
    rows: list[dict[str, object]] = []

    for eps in MC_EPSILONS:
        logits_plus = np.array([math.log(u) + eps, math.log(u) - eps, 0.0])
        probs_plus = inclusion_from_logits(logits_plus)
        omitted_plus = 1.0 - probs_plus
        wrong_logits = np.array([math.log(rc) - 2.0 * eps, math.log(rc) + 2.0 * eps, 0.0])
        wrong_action_loss = normalized_overflow(inclusion_from_logits(wrong_logits), cap)

        for t in MC_BATCHES:
            capacities = np.array(
                [int(round(c * t)), int(round(c * t)), int(round((2.0 - 2.0 * c) * t))],
                dtype=np.int64,
            )
            assert int(capacities.sum()) == 2 * t
            rng = np.random.default_rng(ROOT_SEED + 17 * t + int(eps * 1_000_000))
            omitted = rng.multinomial(t, omitted_plus, size=MC_REPLICATES)
            requests_plus = t - omitted
            requests_minus = requests_plus[:, [1, 0, 2]]
            admitted_plus = np.minimum(requests_plus, capacities)
            admitted_minus = np.minimum(requests_minus, capacities)

            def classifier_error_pair(plus_obs: np.ndarray, minus_obs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
                choose_plus_on_tie_plus = rng.random(MC_REPLICATES) < 0.5
                choose_plus_on_tie_minus = rng.random(MC_REPLICATES) < 0.5
                decide_plus_world = np.where(
                    plus_obs[:, 0] > plus_obs[:, 1], True,
                    np.where(plus_obs[:, 0] < plus_obs[:, 1], False, choose_plus_on_tie_plus),
                )
                decide_plus_world_minus = np.where(
                    minus_obs[:, 0] > minus_obs[:, 1], True,
                    np.where(minus_obs[:, 0] < minus_obs[:, 1], False, choose_plus_on_tie_minus),
                )
                error_plus_world = ~decide_plus_world
                error_minus_world = decide_plus_world_minus
                return error_plus_world, error_minus_world

            req_error_plus, req_error_minus = classifier_error_pair(requests_plus, requests_minus)
            adm_error_plus, adm_error_minus = classifier_error_pair(admitted_plus, admitted_minus)
            req_error = 0.5 * (float(req_error_plus.mean()) + float(req_error_minus.mean()))
            adm_error = 0.5 * (float(adm_error_plus.mean()) + float(adm_error_minus.mean()))
            no_signal_error = 0.5
            paired_error_gains = 0.5 * (
                adm_error_plus.astype(np.float64)
                + adm_error_minus.astype(np.float64)
                - req_error_plus.astype(np.float64)
                - req_error_minus.astype(np.float64)
            )
            price_gain = float(paired_error_gains.mean())
            # Paired-cluster Hoeffding bound: each plant pair contributes a
            # value in [-1,1], so this is a distribution-free 95% interval
            # that respects within-pair dependence.
            price_radius = math.sqrt(2.0 * math.log(2.0 / 0.05) / MC_REPLICATES)
            rows.append(
                {
                    "capacity_pair": c,
                    "baseline_ratio_u": u,
                    "epsilon": eps,
                    "T": t,
                    "paired_world_replicates": MC_REPLICATES,
                    "paired_clusters_for_interval": MC_REPLICATES,
                    "decision_class": "two target-matching pressures; signed R/A contrast; random tie",
                    "population_wrong_target_overflow_exact": wrong_action_loss,
                    "requested_classifier_error_mc": req_error,
                    "admitted_classifier_error_mc": adm_error,
                    "no_signal_classifier_error_exact": no_signal_error,
                    "restricted_break_even_price_R_vs_A_mc": (adm_error - req_error) * wrong_action_loss,
                    "restricted_break_even_price_R_vs_A_paired_hoeffding95_low": (
                        price_gain - price_radius
                    ) * wrong_action_loss,
                    "restricted_break_even_price_R_vs_A_paired_hoeffding95_high": (
                        price_gain + price_radius
                    ) * wrong_action_loss,
                    "restricted_break_even_price_R_vs_no_signal_mc": (no_signal_error - req_error) * wrong_action_loss,
                    "paired_admitted_vectors_equal_rate": float(
                        np.mean(np.all(admitted_plus == admitted_minus, axis=1))
                    ),
                    "scope_note": "finite Monte Carlo estimate for this classifier/two-action class; not unrestricted optimal value",
                }
            )
    return rows


def joint_limit_cells() -> list[dict[str, object]]:
    """Numerically audit one triangular array satisfying the theorem's limits."""
    c = 11.0 / 20.0
    rc = ratio_for_x(c)
    coefficient = j_of_ratio(rc) / 2.0
    rows: list[dict[str, object]] = []
    for t in JOINT_BATCHES:
        delta = 0.5 * t ** (-1.0 / 8.0)
        eps = t ** (-1.0 / 3.0)
        u = ratio_for_x(c + delta)
        theta_bar = np.array([math.log(u), math.log(u), 0.0])
        q0 = np.array([math.log(u / rc), math.log(u / rc)])
        result = differential_evolution(
            common_action_objective,
            bounds=[(q0[0] - 3.0, q0[0] + 3.0), (q0[1] - 3.0, q0[1] + 3.0)],
            args=(theta_bar, eps, c),
            seed=ROOT_SEED + t,
            maxiter=500,
            popsize=16,
            tol=1e-11,
            atol=1e-13,
            polish=True,
            updating="immediate",
            workers=1,
        )
        pplus = inclusion_from_logits(theta_bar + eps * np.array([1.0, -1.0, 0.0]))
        margin = float(np.min(pplus[:2] - c))
        contrast = float(pplus[0] - pplus[1])
        rows.append(
            {
                "capacity_pair": c,
                "T": t,
                "epsilon": eps,
                "baseline_margin_delta": delta,
                "epsilon_over_delta": eps / delta,
                "target_ratio_rc": rc,
                "baseline_ratio_u": u,
                "analytic_slope_j_over_2": coefficient,
                "optimized_common_value": float(result.fun),
                "optimized_value_over_epsilon": float(result.fun) / eps,
                "slope_abs_error": abs(float(result.fun) / eps - coefficient),
                "initial_min_pair_saturation_margin": margin,
                "request_contrast": contrast,
                "T_delta_squared": t * delta**2,
                "T_epsilon_squared_over_log_inverse_epsilon": t * eps**2 / math.log(1.0 / eps),
                "admitted_failure_bound": min(1.0, 2.0 * math.exp(-2.0 * t * margin**2)),
                "request_sign_error_bound": math.exp(-t * contrast**2 / 2.0),
                "finite_batch_noise_over_epsilon": 3.0 / (2.0 * math.sqrt(t) * eps),
                "optimizer_success": bool(result.success),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> str:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pop_rows = deterministic_cells()
    mc_rows = monte_carlo_cells()
    price_rows = priced_decision_cells()
    joint_rows = joint_limit_cells()
    pair_rows = pair_sensitivity_grid()
    facet_rows = root_facet_sensitivity_grid()
    attenuation_rows = clipping_attenuation_grid()
    large_pair_rows = large_pair_sensitivity_grid()
    pop_hash = write_csv(OUT / "population_scaling.csv", pop_rows)
    mc_hash = write_csv(OUT / "finite_batch_signal_check.csv", mc_rows)
    price_hash = write_csv(OUT / "priced_decision_class.csv", price_rows)
    joint_hash = write_csv(OUT / "joint_limit_scaling.csv", joint_rows)
    pair_hash = write_csv(OUT / "pair_sensitivity_grid.csv", pair_rows)
    facet_hash = write_csv(OUT / "root_facet_sensitivity.csv", facet_rows)
    attenuation_hash = write_csv(OUT / "root_facet_clipping_attenuation.csv", attenuation_rows)
    large_pair_hash = write_csv(OUT / "large_pair_sensitivity_grid.csv", large_pair_rows)
    errors = [row["slope_abs_error"] for row in pop_rows]
    summary = {
        "experiment": "symmetric pair-skew Top-K value and sensitivity scaling",
        "seed": ROOT_SEED,
        "population_cells": len(pop_rows),
        "finite_batch_cells": len(mc_rows),
        "priced_decision_cells": len(price_rows),
        "joint_limit_cells": len(joint_rows),
        "pair_sensitivity_cells": len(pair_rows),
        "root_facet_sensitivity_cells": len(facet_rows),
        "root_facet_clipping_attenuation_cells": len(attenuation_rows),
        "large_pair_sensitivity_cells": len(large_pair_rows),
        "finite_batch_replicates_per_cell": MC_REPLICATES,
        "population_max_slope_abs_error": max(float(x) for x in errors),
        "population_slope_abs_error_by_epsilon": {
            str(eps): max(float(row["slope_abs_error"]) for row in pop_rows if row["epsilon"] == eps)
            for eps in EPSILONS
        },
        "population_csv_sha256": pop_hash,
        "finite_batch_csv_sha256": mc_hash,
        "priced_decision_csv_sha256": price_hash,
        "joint_limit_csv_sha256": joint_hash,
        "pair_sensitivity_csv_sha256": pair_hash,
        "root_facet_sensitivity_csv_sha256": facet_hash,
        "root_facet_clipping_attenuation_csv_sha256": attenuation_hash,
        "large_pair_sensitivity_csv_sha256": large_pair_hash,
        "prefix_dp_max_relative_error": max(float(row["prefix_dp_relative_error"]) for row in pair_rows),
        "pair_sensitivity_max_central_difference_relative_error": max(
            float(row["analytic_vs_finite_difference_relative_error"]) for row in pair_rows
        ),
        "root_facet_max_relative_error": max(float(row["relative_difference"]) for row in facet_rows),
        "clipping_attenuation_max_request_slope_abs_error": max(
            float(row["request_slope_abs_error"]) for row in attenuation_rows
        ),
        "clipping_attenuation_max_admitted_slope_abs_error": max(
            float(row["admitted_slope_abs_error"]) for row in attenuation_rows
        ),
        "interpretation": "Numerical optimizer and Monte Carlo checks support the stated value theorem; root-facet quadrature checks the E=3,K=2 geometric coefficient; the exact-binomial factorial audit checks the general Top-K sensitivity times clipping-attenuation identity. The price sweep is limited to a declared two-action policy class. None establishes benchmark novelty or measured system benefit.",
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
