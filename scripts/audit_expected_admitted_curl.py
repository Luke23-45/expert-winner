#!/usr/bin/env python3
"""Exact finite-binomial evaluation of the stochastic Top-1 curl theorem."""

from __future__ import annotations

import json
from fractions import Fraction as F
from math import comb
from pathlib import Path


TOKENS = (10, 20, 50, 100, 200, 500)
PIS = (F(1, 2), F(3, 10), F(1, 5))
CAPACITY_RATIOS = (F(2, 5), F(1, 2), F(1, 10))
J_OFF_DIAGONAL = (F(3, 20), F(1, 10), F(3, 50))  # times gamma/lambda
OUT = Path("results/expected_admitted_curl/summary.json")


def clipped_sensitivity(n_tokens: int, p: F, cap: int) -> F:
    """P[Binomial(T-1,p)<C], computed exactly as a rational number."""
    n = n_tokens - 1
    return sum(
        (F(comb(n, k)) * p**k * (1 - p) ** (n - k) for k in range(cap)),
        F(0),
    )


def curl_coefficient(alpha: tuple[F, F, F]) -> F:
    a1, a2, a3 = alpha
    j12, j13, j23 = J_OFF_DIAGONAL
    return (a1 - a2) * j12 + (a3 - a1) * j13 + (a2 - a3) * j23


def fraction_record(value: F) -> dict[str, str | float]:
    return {"exact": f"{value.numerator}/{value.denominator}", "float": float(value)}


def main() -> None:
    rows = []
    for tokens in TOKENS:
        capacities = tuple(int(tokens * ratio) for ratio in CAPACITY_RATIOS)
        if sum(capacities) != tokens:
            raise AssertionError("capacity vector must have exact total KT")
        alpha = tuple(
            clipped_sensitivity(tokens, p, cap) for p, cap in zip(PIS, capacities)
        )
        clipped_curl = curl_coefficient(alpha)
        no_clip = (F(1), F(1), F(1))
        no_clip_curl = curl_coefficient(no_clip)
        if no_clip_curl != 0:
            raise AssertionError("no-clipping control must have zero curl")
        rows.append(
            {
                "T": tokens,
                "capacities": capacities,
                "alpha": [fraction_record(value) for value in alpha],
                "curl_over_gamma_over_lambda": fraction_record(clipped_curl),
                "no_clipping_curl_over_gamma_over_lambda": fraction_record(no_clip_curl),
            }
        )

    payload = {
        "model": "Top-1 Gumbel-softmax routing; A_e=min(R_e,C_e)",
        "pi": [str(value) for value in PIS],
        "capacity_ratios": [str(value) for value in CAPACITY_RATIOS],
        "limit_curl_over_gamma_over_lambda": "-9/100",
        "by_T": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
