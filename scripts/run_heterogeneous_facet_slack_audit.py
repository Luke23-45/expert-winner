#!/usr/bin/env python3
"""Exact probability and controlled Monte Carlo for unequal facet capacities."""

from __future__ import annotations

import itertools
import json
import math
import random
from fractions import Fraction as F
from pathlib import Path


E = 4
KS = (1, 2, 3)
TOKENS = (32, 64, 128)
Z_PAIRS = ((0, 0), (-1, 1), (-1, 0), (0, 1))
REPLICATES = 5_000
SEED = 20261018
OUT = Path("results/heterogeneous_facet_slack")


def capacity_at_slack(n: int, k: int, z: int) -> int:
    p = k / E
    sd = math.sqrt(n * p * (1 - p))
    return max(1, math.floor(n * p + z * sd + 0.5))


def exact_probability(e: int, k: int, n: int, cap_i: int, cap_j: int) -> F:
    """Exact XOR probability for X_i < cap_i versus X_j < cap_j."""
    m11 = math.comb(e - 2, k - 2) if k >= 2 else 0
    m10 = math.comb(e - 2, k - 1)
    m00 = math.comb(e - 2, k) if k <= e - 2 else 0
    m = math.comb(e, k)
    numerator = 0
    for i_only in range(n + 1):
        for j_only in range(n - i_only + 1):
            for both in range(n - i_only - j_only + 1):
                neither = n - i_only - j_only - both
                x_i = i_only + both
                x_j = j_only + both
                if (x_i < cap_i) == (x_j < cap_j):
                    continue
                ways = (
                    math.comb(n, i_only)
                    * math.comb(n - i_only, j_only)
                    * math.comb(n - i_only - j_only, both)
                )
                multiplicity = (
                    pow(m10, i_only + j_only)
                    * pow(m11, both)
                    * pow(m00, neither)
                )
                numerator += ways * multiplicity
    return F(numerator, pow(m, n))


def simulate(e: int, k: int, n: int, cap_i: int, cap_j: int,
             replicates: int, seed: int) -> int:
    subsets = tuple(itertools.combinations(range(e), k))
    rng = random.Random(seed)
    mismatches = 0
    for _ in range(replicates):
        x_i = x_j = 0
        for _ in range(n):
            selected = rng.choice(subsets)
            x_i += int(0 in selected)
            x_j += int(1 in selected)
        mismatches += int((x_i < cap_i) != (x_j < cap_j))
    return mismatches


def normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def bivariate_normal_cdf(x: float, y: float, rho: float) -> float:
    """Deterministic Simpson quadrature of the conditional-normal integral."""
    lo = -10.0
    hi = x
    if hi <= lo:
        return 0.0
    steps = 20_000
    width = (hi - lo) / steps
    conditional_sd = math.sqrt(1 - rho * rho)

    def integrand(u: float) -> float:
        density = math.exp(-0.5 * u * u) / math.sqrt(2 * math.pi)
        return density * normal_cdf((y - rho * u) / conditional_sd)

    total = integrand(lo) + integrand(hi)
    total += 4 * sum(integrand(lo + i * width) for i in range(1, steps, 2))
    total += 2 * sum(integrand(lo + i * width) for i in range(2, steps, 2))
    return total * width / 3


def asymptotic_probability(z_i: float, z_j: float, e: int) -> float:
    rho = -1 / (e - 1)
    return normal_cdf(z_i) + normal_cdf(z_j) - 2 * bivariate_normal_cdf(z_i, z_j, rho)


def binomial_error(exact: F, successes: int, replicates: int) -> tuple[float, float]:
    """Return empirical proportion and SE error, evaluated stably in the tail."""
    if exact <= F(1, 2):
        target = float(exact)
        observed = successes / replicates
    else:
        target = float(1 - exact)
        observed = (replicates - successes) / replicates
    se = math.sqrt(target * (1 - target) / replicates)
    if se == 0:
        return observed, 0.0 if observed == target else math.inf
    return observed, abs(observed - target) / se


def main() -> None:
    rows = []
    for k in KS:
        p = k / E
        for z_i, z_j in Z_PAIRS:
            limit = asymptotic_probability(z_i, z_j, E)
            for t in TOKENS:
                n = t - 1
                sd = math.sqrt(n * p * (1 - p))
                cap_i = capacity_at_slack(n, k, z_i)
                cap_j = capacity_at_slack(n, k, z_j)
                exact = exact_probability(E, k, n, cap_i, cap_j)
                seed = SEED + 10_000 * k + 100 * z_i + 10 * z_j + t
                mismatches = simulate(E, k, n, cap_i, cap_j, REPLICATES, seed)
                empirical = F(mismatches, REPLICATES)
                exact_float = float(exact)
                _, error_in_se = binomial_error(exact, mismatches, REPLICATES)
                minority_p = float(min(exact, 1 - exact))
                se = math.sqrt(minority_p * (1 - minority_p) / REPLICATES)
                rows.append(
                    {
                        "experts": E,
                        "top_k": k,
                        "tokens": t,
                        "other_tokens_n": n,
                        "target_z_i": z_i,
                        "target_z_j": z_j,
                        "capacity_i": cap_i,
                        "capacity_j": cap_j,
                        "capacity_centered_z_i": (cap_i - n * p) / sd,
                        "capacity_centered_z_j": (cap_j - n * p) / sd,
                        "strict_event_threshold_z_i": (cap_i - 1 - n * p) / sd,
                        "strict_event_threshold_z_j": (cap_j - 1 - n * p) / sd,
                        "exact_mismatch_probability": str(exact),
                        "exact_decimal": f"{exact_float:.8f}",
                        "asymptotic_probability_at_target_z": f"{limit:.8f}",
                        "empirical_mismatch_probability": str(empirical),
                        "empirical_decimal": f"{float(empirical):.8f}",
                        "mc_standard_error_at_exact_p": f"{se:.8f}",
                        "absolute_error_in_mc_se": f"{error_in_se:.4f}",
                        "replicates": REPLICATES,
                        "seed": seed,
                    }
                )

        # Exact-total-capacity control with one expert below and one above
        # the per-expert mean request rate. The other E-2 capacities equal
        # that mean, so the complete capacity vector sums to K*T.
        for t in TOKENS:
            n = t - 1
            mean_full_batch = k * t // E
            assert (k * t) % E == 0 and mean_full_batch % 2 == 0
            cap_i = mean_full_batch // 2
            cap_j = 3 * mean_full_batch // 2
            capacity_vector = [mean_full_batch] * E
            capacity_vector[0] = cap_i
            capacity_vector[1] = cap_j
            assert sum(capacity_vector) == k * t
            exact = exact_probability(E, k, n, cap_i, cap_j)
            seed = SEED + 100_000 + 1_000 * k + t
            mismatches = simulate(E, k, n, cap_i, cap_j, REPLICATES, seed)
            empirical = F(mismatches, REPLICATES)
            exact_float = float(exact)
            _, error_in_se = binomial_error(exact, mismatches, REPLICATES)
            minority_p = float(min(exact, 1 - exact))
            se = math.sqrt(minority_p * (1 - minority_p) / REPLICATES)
            rows.append(
                {
                    "experts": E,
                    "top_k": k,
                    "tokens": t,
                    "other_tokens_n": n,
                    "profile": "cross_mean_exact_total",
                    "capacity_vector": capacity_vector,
                    "capacity_i": cap_i,
                    "capacity_j": cap_j,
                    "capacity_ratio_i_to_mean": cap_i / mean_full_batch,
                    "capacity_ratio_j_to_mean": cap_j / mean_full_batch,
                    "exact_mismatch_probability": str(exact),
                    "exact_decimal": f"{exact_float:.8f}",
                    "asymptotic_probability": "1",
                    "empirical_mismatch_probability": str(empirical),
                    "empirical_decimal": f"{float(empirical):.8f}",
                    "mc_standard_error_at_exact_p": f"{se:.8f}",
                    "absolute_error_in_mc_se": f"{error_in_se:.4f}",
                    "replicates": REPLICATES,
                    "seed": seed,
                }
            )

    result = {
        "status": "PASS",
        "design": {
            "experts": E,
            "top_k_values": list(KS),
            "token_counts": list(TOKENS),
            "target_capacity_slack_pairs": [list(pair) for pair in Z_PAIRS],
            "capacity_rule": "round((T-1)K/E + z*sqrt((T-1)(K/E)(1-K/E)))",
            "additional_control": "exact-total capacity vector with exchanged capacities at 0.5x and 1.5x mean request; remaining capacities at mean",
            "facet_sampling": "one planted regular i-to-j exchange; other T-1 tokens independently choose uniform K-subsets",
            "replicates_per_configuration": REPLICATES,
            "paired_design": "exact multinomial probability and seeded route-level Monte Carlo at each capacity pair",
            "scope": "conditional planted-facet law, not uniformly sampled facets from a complete arrangement",
        },
        "number_of_configurations": len(rows),
        "all_mc_errors_within_5_standard_errors": all(
            float(row["absolute_error_in_mc_se"]) <= 5 for row in rows
        ),
        "rows": rows,
    }
    assert result["all_mc_errors_within_5_standard_errors"]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
