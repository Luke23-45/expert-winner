#!/usr/bin/env python3
"""Exact integer audit of formal_core.md Proposition P2d.

The proof is analytic. This script checks its event sequence and cumulative
overflow formulas for many capacities and horizons using integer-scaled
affinity gaps, so no floating-point score ties are involved.
"""

from __future__ import annotations

import json
from math import ceil, floor
from pathlib import Path


CAPACITIES = range(3, 51)
HORIZONS = range(1, 101)


def route_count_expert1(capacity: int, x: int) -> int:
    """x=(b1-b2)/alpha; d/alpha is in {-1,1,3,5}."""
    multiplicities = {-1: 2, 1: capacity - 2, 3: 3, 5: capacity - 1}
    # Expert 1 wins a tie. The audited orbit never lands on a tie.
    return sum(count for margin, count in multiplicities.items() if margin + x >= 0)


def sign(value: int) -> int:
    return (value > 0) - (value < 0)


def simulate(capacity: int, horizon: int, sensor: str) -> tuple[int, list[tuple[int, int]]]:
    x = 0
    cumulative = 0
    states: list[tuple[int, int]] = []
    for _ in range(horizon):
        r1 = route_count_expert1(capacity, x)
        r2 = 2 * capacity + 2 - r1
        a1, a2 = min(r1, capacity), min(r2, capacity)
        cumulative += (r1 - a1) + (r2 - a2)
        states.append((r1, r2))

        if sensor == "none":
            continue
        c1, c2 = (r1, r2) if sensor == "requested" else (a1, a2)
        u1, u2 = sign(c2 - c1), sign(c1 - c2)
        x += u1 - u2  # normalized by alpha; each bias coordinate moves ±alpha.
    return cumulative, states


def main() -> None:
    cases = 0
    for capacity in CAPACITIES:
        for horizon in HORIZONS:
            admitted_cost, admitted_states = simulate(capacity, horizon, "admitted")
            requested_cost, requested_states = simulate(capacity, horizon, "requested")
            no_update_cost, no_update_states = simulate(capacity, horizon, "none")

            expected_admitted = capacity + 2 * (horizon - 1)
            n = horizon - 1
            expected_requested = capacity + 2 * ceil(n / 2) + 3 * floor(n / 2)
            expected_no_update = horizon * capacity
            assert admitted_cost == expected_admitted
            assert requested_cost == expected_requested
            assert no_update_cost == expected_no_update

            assert admitted_states[0] == (2 * capacity, 2)
            if horizon >= 2:
                assert admitted_states[1] == (capacity + 2, capacity)
                assert all(state == (capacity + 2, capacity) for state in admitted_states[1:])
            assert all(
                requested_states[t] == ((capacity + 2, capacity) if t % 2 == 1
                                         else (capacity - 1, capacity + 3))
                for t in range(1, horizon)
            )
            assert all(state == (2 * capacity, 2) for state in no_update_states)
            assert requested_cost - admitted_cost == (horizon - 1) // 2
            assert no_update_cost - admitted_cost == (horizon - 1) * (capacity - 2)
            cases += 1

    summary = {
        "capacity_range": [min(CAPACITIES), max(CAPACITIES)],
        "horizon_range": [min(HORIZONS), max(HORIZONS)],
        "capacity_horizon_pairs_checked": cases,
        "event_sequence_and_all_cost_identities_pass": True,
        "arithmetic": "integer-scaled margins and bias differences; no floating-point comparisons",
        "scope": "finite exact audit of Proposition P2d; analytic proof is in formal_core.md",
    }
    out = Path("results/signed_bias_top1_family")
    out.mkdir(parents=True, exist_ok=True)
    (out / "audit.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
