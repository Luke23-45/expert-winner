#!/usr/bin/env python3
"""Exact symbolic checks for the Top-1 arbitrary-E value proof."""

from __future__ import annotations

import sympy as sp


X, Y = sp.symbols("X Y", nonnegative=True)
r = sp.Rational(5, 4)
d0 = 1 + r * X + Y
d1 = 1 + X + r * Y
A = 1 - r * X - Y
B = 1 - X - r * Y
positive_denominator = 9 * (4 + 5 * X + 4 * Y) * (4 + 4 * X + 5 * Y)
pair_term = (r - 1) * (X + Y + 2 * (r + 1) * X * Y) / (d0 * d1)

expected_numerators = {
    (1, 1): -8 * (25 * X**2 + 31 * X * Y + 25 * Y**2 - 16),
    (1, -1): -20 * X**2 + 121 * X * Y - 36 * X - 20 * Y**2 + 36 * Y - 16,
    (-1, 1): -20 * X**2 + 121 * X * Y + 36 * X - 20 * Y**2 - 36 * Y - 16,
    (-1, -1): 10 * (16 * X**2 + 49 * X * Y + 16 * Y**2 - 16),
}

for (sign_a, sign_b), expected in expected_numerators.items():
    expression = (pair_term + sign_a * A / (2 * d0) + sign_b * B / (2 * d1) - sp.Rational(1, 9))
    numerator = sp.factor(sp.together(expression * positive_denominator))
    assert sp.expand(numerator - expected) == 0

# Exact side calculations used in the sign-region proof.
q_positive = 25 * X**2 + 31 * X * Y + 25 * Y**2
polygon_vertices = ((0, 0), (sp.Rational(4, 5), 0), (sp.Rational(4, 9), sp.Rational(4, 9)), (0, sp.Rational(4, 5)))
assert tuple(q_positive.subs({X: x, Y: y}) for x, y in polygon_vertices) == (0, 16, 16, 16)

s = sp.symbols("s", real=True)
negative_region_lower = 16 * s**2 + 68 * (1 - s) * (5 * s - 4)
assert sp.expand(negative_region_lower) == -324 * s**2 + 612 * s - 272
assert sp.diff(negative_region_lower, s, 2) == -648
assert negative_region_lower.subs(s, sp.Rational(8, 9)) == 16
assert negative_region_lower.subs(s, 1) == 16

mixed = expected_numerators[(1, -1)]
assert sp.factor(mixed.subs(Y, 1 - sp.Rational(5, 4) * X)) == -sp.Rational(45, 2) * X * (9 * X - 4)
assert sp.factor(mixed.subs(Y, sp.Rational(4, 5) * (1 - X))) == -sp.Rational(72, 5) * X * (9 * X - 4)

target_x = sp.Rational(4, 9)
target_d0 = d0.subs({X: target_x, Y: target_x})
target_d1 = d1.subs({X: target_x, Y: target_x})
p0 = (r * target_x / target_d0, target_x / target_d0, 1 / target_d0)
p1 = (target_x / target_d1, r * target_x / target_d1, 1 / target_d1)
assert p0 == (sp.Rational(5, 18), sp.Rational(2, 9), sp.Rational(1, 2))
assert p1 == (sp.Rational(2, 9), sp.Rational(5, 18), sp.Rational(1, 2))
assert sum(abs(p0[i] - (sp.Rational(1, 4), sp.Rational(1, 4), sp.Rational(1, 2))[i]) for i in range(3)) / 2 == sp.Rational(1, 36)
assert sum(abs(p1[i] - (sp.Rational(1, 4), sp.Rational(1, 4), sp.Rational(1, 2))[i]) for i in range(3)) / 2 == sp.Rational(1, 36)

print("Exact sign-region identities, positivity side-calculations, and equality action verified.")
