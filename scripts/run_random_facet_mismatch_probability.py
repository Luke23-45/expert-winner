#!/usr/bin/env python3
"""Exact finite probability and Monte Carlo check for a planted Top-K facet.

The distinguished token is constructed to have a regular i/j exchange facet.
Each other token independently chooses a uniform K-subset, as happens at a
fixed pressure under iid exchangeable continuous router scores. The script
compares the exact clipped-count mismatch probability to paired simulation.
"""

from __future__ import annotations

import itertools
import json
import math
import random
from fractions import Fraction as F
from pathlib import Path


E = 4
KS = (1, 2, 3)
TOKENS = (8, 16, 32, 64, 128)
REPLICATES = 20_000
SEED = 20261017
OUT = Path("results/random_facet_mismatch_probability")


def exact_mismatch_probability(e: int, k: int, t: int) -> F:
    """Evaluate the exact multinomial sum for a planted i->j facet."""
    assert 1 <= k < e and (k * t) % e == 0
    n = t - 1
    capacity = k * t // e
    c = capacity - 1
    m11 = math.comb(e - 2, k - 2) if k >= 2 else 0
    m10 = math.comb(e - 2, k - 1)
    m00 = math.comb(e - 2, k)
    total_subsets = math.comb(e, k)
    numerator = 0
    for i_only in range(n + 1):
        for j_only in range(n - i_only + 1):
            for both in range(n - i_only - j_only + 1):
                neither = n - i_only - j_only - both
                x_i = i_only + both
                x_j = j_only + both
                if (x_i <= c) == (x_j <= c):
                    continue
                multinomial = (
                    math.comb(n, i_only)
                    * math.comb(n - i_only, j_only)
                    * math.comb(n - i_only - j_only, both)
                )
                multiplicity = (
                    pow(m10, i_only + j_only)
                    * pow(m11, both)
                    * pow(m00, neither)
                )
                numerator += multinomial * multiplicity
    return F(numerator, pow(total_subsets, n))


def simulate(e: int, k: int, t: int, replicates: int, seed: int) -> int:
    n = t - 1
    capacity = k * t // e
    threshold = capacity - 1
    subsets = tuple(itertools.combinations(range(e), k))
    rng = random.Random(seed)
    mismatches = 0
    for _ in range(replicates):
        x_i = x_j = 0
        for _ in range(n):
            selected = rng.choice(subsets)
            x_i += int(0 in selected)
            x_j += int(1 in selected)
        mismatches += int((x_i <= threshold) != (x_j <= threshold))
    return mismatches


def asymptotic_tangent_energy(e: int) -> float:
    return (e - 2) / (2 * e) * math.acos(-1 / (e - 1)) / math.pi


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for k in KS:
        for t in TOKENS:
            exact = exact_mismatch_probability(E, k, t)
            mismatches = simulate(E, k, t, REPLICATES, SEED + 1000 * k + t)
            empirical = F(mismatches, REPLICATES)
            p = float(exact)
            se = math.sqrt(p * (1 - p) / REPLICATES)
            rows.append({
                "experts": E,
                "top_k": k,
                "tokens": t,
                "capacity_each": k * t // E,
                "other_tokens": t - 1,
                "exact_mismatch_probability": str(exact),
                "exact_decimal": f"{p:.8f}",
                "exact_expected_squared_tangential_jump_count_units": str(
                    exact * F(E - 2, 2 * E)
                ),
                "asymptotic_expected_squared_tangential_jump_count_units": f"{asymptotic_tangent_energy(E):.8f}",
                "replicates": REPLICATES,
                "seed": SEED + 1000 * k + t,
                "empirical_mismatch_probability": str(empirical),
                "empirical_decimal": f"{float(empirical):.8f}",
                "mc_standard_error_at_exact_p": f"{se:.8f}",
                "absolute_error_in_mc_se": f"{abs(float(empirical)-p)/se:.4f}",
            })

    asymptotic = math.acos(-1 / (E - 1)) / math.pi
    result = {
        "design": {
            "experts": E,
            "top_k_values": list(KS),
            "token_counts": list(TOKENS),
            "capacity": "uniform exact total C=K*T/E",
            "facet_sampling": "planted regular i-to-j exchange at q=0; the other T-1 tokens independently choose uniform K-subsets",
            "replicates_per_configuration": REPLICATES,
            "primary_metric": "probability that admitted source decrease differs from admitted destination increase",
            "scope": "conditional planted-facet distribution, not a uniformly sampled facet from an arbitrary router",
        },
        "asymptotic_normal_prediction_fixed_E_K": asymptotic,
        "rows": rows,
        "checks": {
            "all_mc_errors_within_5_standard_errors": all(
                float(r["absolute_error_in_mc_se"]) <= 5 for r in rows
            ),
            "no_clipping_control": "not part of this exact-total probability experiment; tested separately in the ensemble audit",
        },
    }
    assert result["checks"]["all_mc_errors_within_5_standard_errors"]
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
