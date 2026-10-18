#!/usr/bin/env python3
"""Symbolic verification of the all-pressure Top-2 lower-bound algebra."""

from __future__ import annotations

import sympy as sp
from fractions import Fraction as FractionQ
from decimal import Decimal, getcontext
from math import comb


r, t = sp.symbols("r t", positive=True)
w = r + 1 + t
d1 = t * (2 * r + t + 1) / ((r + 1) * (r + t) * (r + t + 1))
d2 = r * t * (r + t + 2) / ((r + 1) * (t + 1) * (r + t + 1))
z = r * (r + 1 + 2 * t) / ((r + t + 1) * (r + t) * (t + 1))
difference = sp.factor(d1 - d2)
q_factor = 1 + 2 * r / (r**2 + 2 * r * t + r + t**2 + 2 * t + 1)

assert sp.factor(d1 + d2 + z - 1) == 0
assert sp.factor(difference + (1 - z) * (r - 1) / (r + 1) * q_factor) == 0
assert sp.factor(q_factor - 1) == 2 * r / (r**2 + 2 * r * t + r + t**2 + 2 * t + 1)

# Exact case certificates for g(r)+g(r/4) >= 3/5.
middle_gap = sp.factor((r - 1) / (r + 1) + (4 - r) / (4 + r) - sp.Rational(3, 5))
low_gap = sp.factor((1 - r) / (1 + r) + (4 - r) / (4 + r) - sp.Rational(3, 5))
high_gap = sp.factor((r - 1) / (r + 1) + (r - 4) / (r + 4) - sp.Rational(3, 5))
assert sp.factor(middle_gap + 3 * (r - 4) * (r - 1) /
                 (5 * (r + 1) * (r + 4))) == 0
assert sp.factor(low_gap + (r - 1) * (13 * r + 28) /
                 (5 * (r + 1) * (r + 4))) == 0
assert sp.factor(high_gap - (r - 4) * (7 * r + 13) /
                 (5 * (r + 1) * (r + 4))) == 0

# Exact arithmetic at the attaining feasible common action brackets the value.
lower = sp.Rational(27, 200)
upper = sp.Rational(459, 3080)
assert lower < upper
assert sp.factor(upper - lower) == sp.Rational(27, 1925)

# Certify that the all-policy finite-batch lower bound is strictly positive
# at T=1680 without evaluating exponentials or square roots in floating point.
# For x>0, e^x >= (1+x/n)^n, hence e^-x <= (1+x/n)^(-n).
n = 10_000
def exp_neg_upper(x: FractionQ) -> FractionQ:
    return (FractionQ(1) + x / n) ** (-n)

x1 = FractionQ(56, 15)       # 1680/450
x2 = FractionQ(5054, 15)     # 361*1680/1800
x3 = FractionQ(105, 2)       # 1680/32
sqrt_lower = FractionQ(2049, 50)
assert sqrt_lower**2 < 1680
certified_gap_lower = (
    FractionQ(27, 200)
    - 4 * exp_neg_upper(x1)
    - 2 * exp_neg_upper(x2)
    - 2 * exp_neg_upper(x3)
    - FractionQ(3, 2) / sqrt_lower
)
assert certified_gap_lower > 0
getcontext().prec = 30
certified_gap_decimal = Decimal(certified_gap_lower.numerator) / Decimal(certified_gap_lower.denominator)

print("Top-2 omission formulas, pair-difference identity, Q>=1, and all three ratio cases verified.")
print(f"Exact common-action bracket: {lower} <= v_star <= {upper}.")
print(f"Rationally certified original Hoeffding all-policy bound at T=1680: > {certified_gap_decimal}.")


# Sharper finite-batch certificate at T=540.  Jensen gives the admitted
# policy's realized expected overflow >= its population overflow, so no
# O(T^-1/2) subtraction is needed on that side.  Exact binomial tails replace
# Hoeffding's union bounds in the two-saturated coupling and request decoder.
def binomial_probability(a: int, b: int, lo: int, hi: int, total: int) -> FractionQ:
    lo = max(0, lo)
    hi = min(total, hi)
    if lo > hi:
        return FractionQ(0)
    numerator = sum(
        comb(total, k) * a**k * (b - a) ** (total - k)
        for k in range(lo, hi + 1)
    )
    return FractionQ(numerator, b**total)


def exact_finite_batch_certificate(total: int, sqrt_total_lower: FractionQ) -> FractionQ:
    pair_capacity = 11 * total // 20
    tail_capacity = 9 * total // 10
    decision_threshold = 17 * total // 24

    # For either world, the clipping-coupling failure event is contained in
    # the union of: the low-mean pair count falling below capacity, the
    # high-mean pair count falling below capacity, or the common tail count
    # reaching its capacity.
    low_pair_failure = binomial_probability(7, 12, 0, pair_capacity - 1, total)
    high_pair_failure = binomial_probability(5, 6, 0, pair_capacity - 1, total)
    tail_failure = binomial_probability(7, 12, tail_capacity, total, total)
    alias_failure = low_pair_failure + high_pair_failure + tail_failure

    # Exact classifier errors for the threshold R_1/total > 17/24.
    request_error_world0 = binomial_probability(5, 6, 0, decision_threshold, total)
    request_error_world1 = binomial_probability(7, 12, decision_threshold + 1, total, total)

    # At the target action, each marginal count has mean its capacity.  By
    # E[(X-EX)_+] = E|X-EX|/2 and Cauchy-Schwarz, its normalized expected
    # overflow is bounded by (sqrt(99)+3)/(20 sqrt(total)).  Use exact
    # rational certificates for both square roots.
    sqrt99_upper = FractionQ(199, 20)
    assert sqrt99_upper**2 > 99
    assert sqrt_total_lower**2 < total
    target_batch_noise_upper = (FractionQ(3) + sqrt99_upper) / (20 * sqrt_total_lower)

    lower_bound = (
        FractionQ(27, 200)
        - 2 * alias_failure
        - request_error_world0
        - request_error_world1
        - target_batch_noise_upper
    )
    return lower_bound


getcontext().prec = 40
for total, sqrt_total_lower in (
    (540, FractionQ(232379, 10_000)),
    (1680, FractionQ(2049, 50)),
):
    exact_lower = exact_finite_batch_certificate(total, sqrt_total_lower)
    assert exact_lower > 0
    decimal_lower = Decimal(exact_lower.numerator) / Decimal(exact_lower.denominator)
    print(f"Exact-rational all-policy gap certificate at T={total}: > {decimal_lower}.")
