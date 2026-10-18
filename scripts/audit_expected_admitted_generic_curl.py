#!/usr/bin/env python3
"""Exact rational audit of the E=3 Top-1 admitted-field curl corollary.

This enumerates rational request-probability grids.  It does not estimate the
curl by finite differences: all binomial sensitivities and quotient-curl
values are evaluated with fractions.Fraction.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def alpha(p: Fraction, *, trials: int = 5, capacity: int = 2) -> Fraction:
    """P[Binomial(trials,p) < capacity], exactly."""
    return sum(
        Fraction(_choose(trials, j)) * p**j * (1 - p) ** (trials - j)
        for j in range(capacity)
    )


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    out = 1
    for j in range(1, min(k, n - k) + 1):
        out = out * (n - j + 1) // j
    return out


def quotient_curl(
    p: tuple[Fraction, Fraction, Fraction], *, clipped: bool = True
) -> Fraction:
    """Curl on (e1-e3,e2-e3) for T=6, C=(2,2,2), gamma=K=1."""
    p1, p2, p3 = p
    if clipped:
        a1, a2, a3 = (alpha(value) for value in p)
    else:
        a1 = a2 = a3 = Fraction(1)
    return (
        p1 * p2 * (a1 - a2)
        - p1 * p3 * (a1 - a3)
        + p2 * p3 * (a2 - a3)
    )


def factorized_curl(
    p: tuple[Fraction, Fraction, Fraction]
) -> Fraction:
    """Symbolic factorization specialized to T=6 and C_e=2."""
    p1, p2, p3 = p
    s2 = p1 * p2 + p2 * p3 + p3 * p1
    s3 = p1 * p2 * p3
    q_sym = 4 * s2**2 - 2 * s2 - 7 * s3 - 1
    return (p1 - p2) * (p2 - p3) * (p1 - p3) * q_sym


def summarize_grid(denominator: int) -> dict[str, int | str]:
    nonzero = zero = positive = negative = 0
    min_abs: Fraction | None = None
    total = 0
    for n1 in range(1, denominator - 1):
        for n2 in range(1, denominator - n1):
            n3 = denominator - n1 - n2
            if n3 <= 0:
                continue
            total += 1
            p = (
                Fraction(n1, denominator),
                Fraction(n2, denominator),
                Fraction(n3, denominator),
            )
            value = quotient_curl(p)
            assert value == factorized_curl(p), (denominator, p, value)
            repeated_probability = len(set(p)) < 3
            assert (value == 0) == repeated_probability, (denominator, p, value)
            if value == 0:
                zero += 1
            else:
                nonzero += 1
                positive += value > 0
                negative += value < 0
                min_abs = abs(value) if min_abs is None else min(min_abs, abs(value))
    assert total == (denominator - 1) * (denominator - 2) // 2
    return {
        "denominator": denominator,
        "interior_grid_points": total,
        "zero_curl_points": zero,
        "nonzero_curl_points": nonzero,
        "positive_curl_points": positive,
        "negative_curl_points": negative,
        "minimum_nonzero_absolute_curl": (
            str(min_abs) if min_abs is not None else "none"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--denominators", type=int, nargs="+", default=[30, 60, 120, 240]
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/expected_admitted_generic_curl/audit.json"),
    )
    args = parser.parse_args()
    witness = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    uniform = (Fraction(1, 3),) * 3
    result = {
        "model": {
            "experts": 3,
            "top_k": 1,
            "tokens": 6,
            "capacities": [2, 2, 2],
            "noise": "iid standard Gumbel",
            "admission": "A_e=min(R_e,C_e)",
            "arithmetic": "exact rational",
        },
        "witness": {
            "probabilities": [str(x) for x in witness],
            "curl_clipped": str(quotient_curl(witness)),
            "curl_no_clipping": str(quotient_curl(witness, clipped=False)),
        },
        "symmetric_control": {
            "probabilities": [str(x) for x in uniform],
            "curl_clipped": str(quotient_curl(uniform)),
        },
        "grids": [summarize_grid(n) for n in args.denominators],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
