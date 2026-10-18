#!/usr/bin/env python3
"""Exact small-batch audit of the Top-1 requested/admitted Bayes rules."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from math import factorial


def multinomial_mass(t: int, r1: int, r2: int, r3: int, *, swapped: bool) -> Fraction:
    coeff = factorial(t) // (factorial(r1) * factorial(r2) * factorial(r3))
    p1, p2 = (Fraction(4, 13), Fraction(5, 13)) if swapped else (Fraction(5, 13), Fraction(4, 13))
    return coeff * p1**r1 * p2**r2 * Fraction(4, 13) ** r3


def verify_batch(t: int) -> int:
    if t % 4:
        raise ValueError("T must make capacities (T/4,T/4,T/2) integral")
    cap = t // 4
    admitted_worlds: dict[tuple[int, int, int], list[Fraction]] = defaultdict(
        lambda: [Fraction(0), Fraction(0)]
    )
    states = 0
    total0 = Fraction(0)
    total1 = Fraction(0)

    for r1 in range(t + 1):
        for r2 in range(t - r1 + 1):
            r3 = t - r1 - r2
            p0 = multinomial_mass(t, r1, r2, r3, swapped=False)
            p1 = multinomial_mass(t, r1, r2, r3, swapped=True)
            total0 += p0
            total1 += p1
            states += 1

            request_sign = (r1 > r2) - (r1 < r2)
            assert (p0 > p1) - (p0 < p1) == request_sign

            observed = (min(r1, cap), min(r2, cap), min(r3, 2 * cap))
            admitted_worlds[observed][0] += p0
            admitted_worlds[observed][1] += p1

    assert total0 == total1 == 1
    for (a1, a2, _), (p0, p1) in admitted_worlds.items():
        admitted_sign = (a1 > a2) - (a1 < a2)
        assert (p0 > p1) - (p0 < p1) == admitted_sign

    return states


def main() -> None:
    for t in (4, 8, 12, 16):
        print(f"T={t}: exact request and full-admission Bayes signs verified over {verify_batch(t)} request states")


if __name__ == "__main__":
    main()
