#!/usr/bin/env python3
"""Reproduce floating-point threshold diagnostics for the Top-1 value bound."""

from __future__ import annotations

import json
import math
from pathlib import Path

from run_top1_arbitrary_e_exact_swapped_value import exact_sign_classifier_errors
from scipy.stats import binom


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "top1_arbitrary_e_exact_swapped_value" / "finite_batch_bound_thresholds.json"
EXPERT_COUNTS = (3, 4, 8, 16, 32, 64)
CHERNOFF_BASE = 4 * (1 + math.sqrt(5)) / 13


def evaluate(e: int, t: int) -> dict[str, float | int]:
    n = e - 2
    capacities = [t // 4, t // 4] + [t // (2 * n)] * n
    if t % 4 or t % (2 * n):
        raise ValueError("T does not make all capacity fractions integral")
    eps_admitted = float(
        binom.cdf(capacities[0] - 1, t, 5 / 13)
        + binom.cdf(capacities[1] - 1, t, 4 / 13)
    )
    eps_requested_exact, _ = exact_sign_classifier_errors(t, int(capacities[0]))
    eps_requested_chernoff = CHERNOFF_BASE**t
    c = [1 / 4, 1 / 4] + [1 / (2 * n)] * n
    target_cost = 0.0
    for fraction, cap in zip(c, capacities, strict=True):
        target_cost += fraction * float(binom.sf(cap - 1, t - 1, fraction))
        target_cost -= fraction * float(binom.sf(cap, t, fraction))
    lower_bound = 1 / 36 - eps_admitted / 2 - eps_requested_exact - target_cost
    return {
        "E": e,
        "T": t,
        "capacity_denominator": math.lcm(4, 2 * n),
        "eps_admitted": eps_admitted,
        "eps_requested_exact_sign_error": eps_requested_exact,
        "eps_requested_chernoff_upper_bound": eps_requested_chernoff,
        "target_action_expected_overflow": target_cost,
        "all_policy_gap_lower_bound": lower_bound,
    }


def main() -> None:
    rows = []
    for e in EXPERT_COUNTS:
        n = e - 2
        denominator = math.lcm(4, 2 * n)
        found = None
        # Scan every admissible T in order; do not assume monotonicity of the
        # discrete tail expression between capacity jumps.
        for multiplier in range(1, 100_001):
            row = evaluate(e, multiplier * denominator)
            if row["all_policy_gap_lower_bound"] > 0:
                found = row
                break
        if found is None:
            raise RuntimeError(f"No positive bound found for E={e} within scan limit")
        rows.append(found)

    payload = {
        "status": "floating-point binomial-tail diagnostic; not interval certified",
        "bound": "1/36 - eps_admitted/2 - exact_sign_classifier_error - target_action_expected_overflow",
        "thresholds": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(
            f"E={row['E']} first_admissible_T={row['T']} "
            f"gap_lower_bound={row['all_policy_gap_lower_bound']:.8g}"
        )


if __name__ == "__main__":
    main()
