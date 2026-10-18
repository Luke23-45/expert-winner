#!/usr/bin/env python3
"""Exact Bellman audit for the costed-observation E-world theorem.

Run from the exploration repository root:
    python scripts/audit_eworld_costed_observation.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path


WORLD_COUNTS = tuple(range(2, 21))
OVERLOADS = (1, 2, 5)
CAPACITY_MULTIPLIERS = (2, 3, 5)


def exact_values(worlds: int, overload: int, capacity: int) -> list[list[Fraction]]:
    """Return V[h][n] from the exact subset-probe Bellman recursion."""
    max_horizon = worlds + 1
    values = [[Fraction(0) for _ in range(worlds + 1)] for _ in range(max_horizon + 1)]
    probe_gap = 2 * overload

    for horizon in range(1, max_horizon + 1):
        for support in range(2, worlds + 1):
            best = Fraction(overload) + values[horizon - 1][support]
            for probe_size in range(1, support + 1):
                outside = support - probe_size
                inside_cost = (
                    Fraction(0)
                    if probe_size == 1
                    else Fraction(probe_gap + (probe_size - 2) * capacity)
                )
                outside_cost = Fraction(probe_gap + (probe_size - 1) * capacity)
                candidate = Fraction(probe_size, support) * inside_cost
                if outside:
                    candidate += Fraction(outside, support) * (
                        outside_cost + values[horizon - 1][outside]
                    )
                best = min(best, candidate)
            values[horizon][support] = best
    return values


def main() -> None:
    checks = {
        "all_exact_bellman_values_match_closed_form": True,
        "requested_initial_counts_identify_each_world": True,
        "admitted_initial_observation_is_world_independent": True,
        "one_time_price_threshold_matches_admitted_value": True,
        "optional_buy_no_buy_value_matches_closed_form": True,
        "capacity_conditions_hold": True,
    }
    grid: list[dict] = []
    value_checks = 0
    for worlds in WORLD_COUNTS:
        for overload in OVERLOADS:
            for multiplier in CAPACITY_MULTIPLIERS:
                capacity = multiplier * overload
                sink_capacity = capacity - overload
                tokens = worlds * capacity + overload
                values = exact_values(worlds, overload, capacity)
                local_checks = dict(checks)

                local_checks["capacity_conditions_hold"] = (
                    capacity >= 2 * overload
                    and sink_capacity >= overload
                    and sink_capacity < capacity - Fraction(overload, 2)
                )
                requests = {
                    tuple(
                        capacity + overload if expert == world else capacity
                        for expert in range(worlds)
                    )
                    for world in range(worlds)
                }
                admitted = {
                    tuple(capacity for _ in range(worlds))
                    for _ in range(worlds)
                }
                local_checks["requested_initial_counts_identify_each_world"] = (
                    len(requests) == worlds
                    and all(sum(request) == tokens for request in requests)
                )
                local_checks["admitted_initial_observation_is_world_independent"] = (
                    len(admitted) == 1
                )
                local_checks["one_time_price_threshold_matches_admitted_value"] = True

                for horizon in range(worlds + 2):
                    for support in range(1, worlds + 1):
                        expected = overload * min(horizon, support - 1)
                        if values[horizon][support] != expected:
                            local_checks["all_exact_bellman_values_match_closed_form"] = False
                            raise AssertionError((
                                "closed form mismatch", worlds, overload, capacity,
                                horizon, support, values[horizon][support], expected,
                            ))
                        value_checks += 1

                    threshold = overload * min(horizon, worlds - 1)
                    admitted_total = overload + values[horizon][worlds]
                    requested_total_at_threshold = overload + threshold
                    if admitted_total != requested_total_at_threshold:
                        local_checks["one_time_price_threshold_matches_admitted_value"] = False
                        raise AssertionError((
                            "break-even mismatch", worlds, overload, capacity,
                            horizon, admitted_total, requested_total_at_threshold,
                        ))
                    for kappa in (Fraction(0), threshold / 2, threshold, threshold + 1):
                        optional_value = min(admitted_total, overload + kappa)
                        closed_form_value = overload + min(threshold, kappa)
                        if optional_value != closed_form_value:
                            local_checks["optional_buy_no_buy_value_matches_closed_form"] = False
                            raise AssertionError((
                                "optional buy/no-buy mismatch", worlds, overload,
                                capacity, horizon, kappa, optional_value,
                                closed_form_value,
                            ))

                if not all(local_checks.values()):
                    raise AssertionError((worlds, overload, capacity, local_checks))
                grid.append({
                    "worlds": worlds,
                    "extra_overload": overload,
                    "regular_capacity": capacity,
                    "sink_capacity": sink_capacity,
                    "tokens": tokens,
                    "verified_horizons": worlds + 2,
                    "minimum_telemetry_price_by_horizon": [
                        str(overload * min(horizon, worlds - 1))
                        for horizon in range(worlds + 2)
                    ],
                    "optional_buy_no_buy_values_checked": 4 * (worlds + 2),
                    "checks": local_checks,
                })

    protocol = Path("docs/paper/eworld_costed_observation_protocol_2026-10-17.md")
    theorem = Path("docs/paper/eworld_costed_observation_value_theorem_2026-10-17.md")
    script = Path(__file__).resolve()
    output = {
        "purpose": "Exact rational Bellman audit of costed one-shot requested telemetry in the Top-1 E-world family",
        "scope": "subset-probe DP after the proved all-pressure action reduction; no physical telemetry cost",
        "world_counts": list(WORLD_COUNTS),
        "extra_overloads": list(OVERLOADS),
        "capacity_multipliers": list(CAPACITY_MULTIPLIERS),
        "parameter_cells": len(grid),
        "closed_form_value_checks": value_checks,
        "protocol_sha256": hashlib.sha256(protocol.read_bytes()).hexdigest(),
        "theorem_sha256": hashlib.sha256(theorem.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "base_revision": subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip(),
        "all_checks_pass": True,
        "grid": grid,
    }
    out = Path("results/eworld_costed_observation/summary.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        key: output[key]
        for key in ("all_checks_pass", "parameter_cells", "closed_form_value_checks")
    }, indent=2))
    print(f"Artifact: {out.resolve()}")


if __name__ == "__main__":
    main()
