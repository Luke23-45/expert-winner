#!/usr/bin/env python3
"""Exact-rational audit of the signed-bias saturation-exit bound."""

from __future__ import annotations

import json
import random
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "signed_bias_saturation_exit" / "summary.json"
E, K, T = 4, 2, 8
CAPACITY = (1, 2, 3, 3)
PAIRS = ((0, 1), (0, 3), (1, 3), (1, 3), (1, 3), (2, 3), (2, 3), (2, 3))
PERTURBATIONS = 20
GAINS = (F(1, 1000), F(1, 500), F(1, 100))
SEED = 20261018


def plant(seed: int | None) -> tuple[tuple[F, ...], ...]:
    rng = random.Random(seed)
    rows = []
    for pair in PAIRS:
        row = []
        for expert in range(E):
            value = F(int(expert in pair))
            if seed is not None:
                value += F(rng.choice((-1, 0, 1)), 100)
            row.append(value)
        rows.append(tuple(row))
    return tuple(rows)


def route(affinities: tuple[tuple[F, ...], ...], bias: tuple[F, ...]):
    selected = []
    for row in affinities:
        scores = tuple(row[e] + bias[e] for e in range(E))
        selected.append(tuple(sorted(range(E), key=lambda e: (-scores[e], e))[:K]))
    requested = tuple(sum(e in choices for choices in selected) for e in range(E))
    admitted = tuple(min(requested[e], CAPACITY[e]) for e in range(E))
    return tuple(selected), requested, admitted


def sign_feedback(load: tuple[int, ...]) -> tuple[F, ...]:
    mean = F(sum(load), E)
    return tuple(F(1) if value < mean else F(-1) if value > mean else F(0) for value in load)


def exit_bound(affinities, slope, gain: F, initial_bias=(F(0),) * E) -> int:
    ordered = sorted(range(E), key=lambda e: (-slope[e], e))
    selected, rejected = ordered[:K], ordered[K:]
    gap = slope[selected[-1]] - slope[rejected[0]]
    assert gap > 0
    bound = 0
    for row in affinities:
        for i in selected:
            for j in rejected:
                numerator = row[j] + initial_bias[j] - row[i] - initial_bias[i]
                theta = numerator / (gain * (slope[i] - slope[j]))
                bound = max(bound, theta.numerator // theta.denominator + 1)
    return max(0, bound)


def simulate(affinities, gain: F, signal: str, limit: int = 10_000):
    bias = (F(0),) * E
    for state in range(limit + 1):
        selected, requested, admitted = route(affinities, bias)
        saturated = all(requested[e] >= CAPACITY[e] for e in range(E))
        if not saturated:
            overflow = sum(requested) - sum(admitted)
            return {
                "first_unsaturated_state": state,
                "requested_at_exit": list(requested),
                "admitted_at_exit": list(admitted),
                "overflow_at_exit": overflow,
                "bias_at_exit": [str(x) for x in bias],
                "previous_routes": [list(x) for x in selected],
            }
        if state == limit:
            return {
                "first_unsaturated_state": None,
                "saturated_through_state": state,
                "requested_at_last_state": list(requested),
                "admitted_at_last_state": list(admitted),
                "bias_at_last_state": [str(x) for x in bias],
            }
        load = admitted if signal == "admitted" else requested
        signs = sign_feedback(load)
        bias = tuple(bias[e] + gain * signs[e] for e in range(E))
    raise AssertionError("unreachable")


def audit(affinities, gain: F):
    _, initial_r, initial_a = route(affinities, (F(0),) * E)
    assert initial_r == (2, 4, 3, 7), initial_r
    assert initial_a == CAPACITY, initial_a
    admitted_slope = sign_feedback(initial_a)
    requested_slope = sign_feedback(initial_r)
    n_bound = exit_bound(affinities, admitted_slope, gain)
    a = simulate(affinities, gain, "admitted")
    r = simulate(affinities, gain, "requested")
    assert a["first_unsaturated_state"] <= n_bound
    return {
        "gain": str(gain),
        "initial_requested": list(initial_r),
        "initial_admitted": list(initial_a),
        "admitted_saturated_slope": [int(x) for x in admitted_slope],
        "requested_saturated_slope": [int(x) for x in requested_slope],
        "admitted_theorem_upper_bound_state": n_bound,
        "admitted": a,
        "requested": r,
    }


def main() -> None:
    base_rows = [audit(plant(None), gain) for gain in GAINS]
    paired = []
    for seed in range(SEED, SEED + PERTURBATIONS):
        affinities = plant(seed)
        for gain in GAINS:
            paired.append({"seed": seed, **audit(affinities, gain)})

    result = {
        "status": "PASS",
        "model": "E=4,K=2,T=8 fixed Top-2 affinity batch; per-expert clipping; signed integral update; exact Fraction arithmetic",
        "capacities": list(CAPACITY),
        "aggregate_capacity": sum(CAPACITY),
        "requested_slots": K * T,
        "base_affinity_pairs_zero_based": [list(pair) for pair in PAIRS],
        "base_plant": base_rows,
        "perturbation_design": {
            "plants": PERTURBATIONS,
            "entrywise_perturbations": [-0.01, 0, 0.01],
            "gains": [str(x) for x in GAINS],
            "paired_cells": len(paired),
            "seed_range": [SEED, SEED + PERTURBATIONS - 1],
            "all_route_changes_occur_within_theorem_bound": all(
                row["admitted"]["first_unsaturated_state"] <= row["admitted_theorem_upper_bound_state"]
                for row in paired
            ),
            "all_initial_plants_have_identical_route_counts": all(
                row["initial_requested"] == [2, 4, 3, 7]
                and row["initial_admitted"] == list(CAPACITY)
                for row in paired
            ),
        },
        "perturbed_cells": paired,
        "scope": "verifies a sufficient finite saturation-exit bound for this signed controller; does not bound repeated saturation episodes or imply a long-run performance ranking",
    }
    assert result["perturbation_design"]["all_route_changes_occur_within_theorem_bound"]
    assert result["perturbation_design"]["all_initial_plants_have_identical_route_counts"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "paired_cells": len(paired),
        "all_routes_preserve_initial_saturated_counts": result["perturbation_design"]["all_initial_plants_have_identical_route_counts"],
        "all_admitted_exit_times_within_bound": result["perturbation_design"]["all_route_changes_occur_within_theorem_bound"],
        "base_plant": base_rows,
    }, indent=2))


if __name__ == "__main__":
    main()
