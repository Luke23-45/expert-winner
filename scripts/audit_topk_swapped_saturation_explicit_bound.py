#!/usr/bin/env python3
"""Numerically evaluate an explicit, conservative bound on v_*.

The formulas are derived in
docs/paper/topk_swapped_saturation_explicit_gap_bound_2026-10-17.md.
This is a floating-point diagnostic, not an interval-certified proof.
"""

from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np

from run_topk_swapped_saturation_value import subset_distribution


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "topk_swapped_saturation_explicit_bound"
EXPERT_COUNTS = (3, 4, 6, 8)
TARGET_WEIGHT = Fraction(1, 2)
WORLD_WEIGHT = Fraction(5, 4)
PATCH_HALF_WIDTH = 0.30
PATCH_GAP = 0.61


def candidate_ks(e: int) -> tuple[int, ...]:
    return tuple(sorted({1, e // 2, e - 1}))


def log_gumbel_density(x: float) -> float:
    return -x - math.exp(-x)


def audit_cell(e: int, k: int) -> dict[str, object]:
    target_weights = (TARGET_WEIGHT, TARGET_WEIGHT) + (Fraction(1),) * (e - 2)
    world0_weights = (WORLD_WEIGHT,) + (Fraction(1),) * (e - 1)
    _, _, target_fraction = subset_distribution(target_weights, k)
    _, _, request_fraction = subset_distribution(world0_weights, k)
    c = np.array([float(x) for x in target_fraction])
    p = np.array([float(x) for x in request_fraction])
    exact_margins = [request_fraction[0] - target_fraction[0], request_fraction[1] - target_fraction[1]] + [
        target_fraction[z] - request_fraction[z] for z in range(2, e)
    ]
    if not all(margin > 0 for margin in exact_margins):
        raise AssertionError(f"exact strict clipping margins failed for E={e}, K={k}")

    # The target logits are known exactly up to a common shift.
    theta_c = np.array([math.log(float(TARGET_WEIGHT))] * 2 + [0.0] * (e - 2))
    theta_c -= theta_c.mean()
    theta0 = np.array([math.log(float(WORLD_WEIGHT))] + [0.0] * (e - 1))
    theta0 -= theta0.mean()
    theta1 = theta0.copy()
    theta1[0], theta1[1] = theta1[1], theta1[0]
    distance = float(np.linalg.norm(theta0 - theta1))
    radius = distance / 2

    edge_weights: list[float] = []
    for i, j in itertools.combinations(range(e), 2):
        tie_center = (theta_c[i] + theta_c[j]) / 2
        log_patch_masses: list[float] = []
        others = [z for z in range(e) if z not in (i, j)]
        for upper_set_tuple in itertools.combinations(others, k - 1):
            upper_set = set(upper_set_tuple)
            log_mass = (e - 1) * math.log(2 * PATCH_HALF_WIDTH)
            for z in range(e):
                if z in (i, j):
                    center = tie_center
                elif z in upper_set:
                    center = max(theta_c[z], tie_center + PATCH_GAP)
                else:
                    center = min(theta_c[z], tie_center - PATCH_GAP)

                # For all theta in the radius ball and all y in this patch,
                # y_z-theta_z lies in the interval below.
                lo = center - PATCH_HALF_WIDTH - theta_c[z] - radius
                hi = center + PATCH_HALF_WIDTH - theta_c[z] + radius
                log_mass += min(log_gumbel_density(lo), log_gumbel_density(hi))
            log_patch_masses.append(log_mass)

        peak = max(log_patch_masses)
        edge_weights.append(
            math.exp(peak) * sum(math.exp(x - peak) for x in log_patch_masses)
        )

    min_edge_weight = min(edge_weights)
    # L >= min_edge_weight * Laplacian(K_E), whose quotient eigenvalue is E.
    v_lower = e * min_edge_weight * distance / (8 * k)
    margins = [p[0] - c[0], p[1] - c[1]] + [c[z] - p[z] for z in range(2, e)]
    denominator = math.lcm(*(x.denominator for x in target_fraction))
    delta = float(p[0] - p[1])

    def finite_bound(t: float) -> float:
        eps_a = sum(math.exp(-2 * t * margin * margin) for margin in margins)
        eps_r = math.exp(-t * delta * delta / 2)
        return v_lower - eps_a / 2 - eps_r - e / (k * math.sqrt(t))

    low, high = 1.0, 1.0
    while finite_bound(high) <= 0 and high < 1e300:
        high *= 2
    if high >= 1e300:
        threshold_t = math.inf
    else:
        low = high / 2
        for _ in range(200):
            mid = (low + high) / 2
            if finite_bound(mid) > 0:
                high = mid
            else:
                low = mid
        threshold_t = high

    first_admissible = math.ceil(threshold_t / denominator) * denominator
    return {
        "E": e,
        "K": k,
        "capacity_fraction": [str(x) for x in target_fraction],
        "capacity_denominator": denominator,
        "minimum_strict_margin": min(margins),
        "world0_inclusion": [str(x) for x in request_fraction],
        "world0_gap": delta,
        "score_quotient_distance": distance,
        "patch_half_width": PATCH_HALF_WIDTH,
        "patch_gap": PATCH_GAP,
        "minimum_facet_patch_weight": min_edge_weight,
        "v_star_lower_bound": v_lower,
        "continuous_T_threshold": threshold_t,
        "first_admissible_T_approx": first_admissible,
        "finite_bound_at_first_admissible_T": finite_bound(first_admissible),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [audit_cell(e, k) for e in EXPERT_COUNTS for k in candidate_ks(e)]
    result = {
        "status": "floating-point diagnostic; not interval certified",
        "profiles": rows,
    }
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(
            f"E={row['E']} K={row['K']} "
            f"v_lower={row['v_star_lower_bound']:.6e} "
            f"T_threshold~{row['continuous_T_threshold']:.6e} "
            f"denominator={row['capacity_denominator']}"
        )


if __name__ == "__main__":
    main()
