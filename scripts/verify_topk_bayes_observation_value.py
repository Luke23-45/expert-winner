#!/usr/bin/env python3
"""Exact rational checks for the swapped Top-K Bayes likelihood and errors."""

from __future__ import annotations

from fractions import Fraction
from math import factorial

import numpy as np

from run_topk_swapped_saturation_value import (
    capacity_fractions,
    exact_bayes_errors,
    subset_distribution,
)


def pair_probabilities(e: int, k: int):
    weights = (Fraction(5, 4),) + (Fraction(1),) * (e - 1)
    masks, probabilities, _ = subset_distribution(weights, k)
    plus, minus, both = Fraction(0), Fraction(0), Fraction(0)
    plus_orbit, minus_orbit = set(), set()
    for mask, probability in zip(masks, probabilities, strict=True):
        has_1, has_2 = bool(mask & 1), bool(mask & 2)
        if has_1 and not has_2:
            plus += probability
            plus_orbit.add(probability)
        elif has_2 and not has_1:
            minus += probability
            minus_orbit.add(probability)
        elif has_1 and has_2:
            both += probability
    assert len(plus_orbit) == len(minus_orbit) == 1
    assert plus > minus
    return plus, minus, both


def brute_errors(t: int, cap: int, plus: Fraction, minus: Fraction, both: Fraction):
    neutral = 1 - plus - minus
    neither = neutral - both
    probs = (plus, minus, both, neither)
    request_error = Fraction(0)
    admitted_error = Fraction(0)
    for n_plus in range(t + 1):
        for n_minus in range(t - n_plus + 1):
            for n_both in range(t - n_plus - n_minus + 1):
                n_neither = t - n_plus - n_minus - n_both
                counts = (n_plus, n_minus, n_both, n_neither)
                coefficient = factorial(t)
                for count in counts:
                    coefficient //= factorial(count)
                probability = Fraction(coefficient)
                for p, count in zip(probs, counts, strict=True):
                    probability *= p**count

                d = n_plus - n_minus
                request_error += probability * (Fraction(1) if d < 0 else Fraction(1, 2) if d == 0 else Fraction(0))
                r1, r2 = n_plus + n_both, n_minus + n_both
                a1, a2 = min(r1, cap), min(r2, cap)
                admitted_error += probability * (
                    Fraction(1) if a1 < a2 else Fraction(1, 2) if a1 == a2 else Fraction(0)
                )
    assert sum(probs) == 1
    return request_error, admitted_error


def main() -> None:
    # Check the orbit-likelihood structure for every K in the registered E grid.
    for e in (3, 4, 6, 8):
        for k in range(1, e):
            p_plus, p_minus, p_both = pair_probabilities(e, k)
            assert p_plus > p_minus
            assert 0 <= p_both <= 1 - p_plus - p_minus

    # Brute-force exact category-count laws against the binomial-sum formula.
    profiles = ((3, 1), (3, 2), (4, 2), (6, 3), (8, 4))
    checked = 0
    for e, k in profiles:
        capacities = capacity_fractions(e, k)
        t = 1
        for value in capacities:
            t = int(np.lcm(t, value.denominator))
        cap = int(capacities[0] * t)
        p_plus, p_minus, p_both = pair_probabilities(e, k)
        exact = brute_errors(t, cap, p_plus, p_minus, p_both)
        calculated = exact_bayes_errors(t, cap, float(p_plus), float(p_minus), float(p_both))
        assert np.allclose([float(x) for x in exact], calculated, rtol=0.0, atol=2e-12), (
            e, k, exact, calculated
        )
        print(f"E={e} K={k} T={t}: exact-rational enumeration matches both Bayes error sums")
        checked += 1
    print(f"verified likelihood-ratio structure for all K in E={{3,4,6,8}}; brute-force error cells={checked}")


if __name__ == "__main__":
    main()
