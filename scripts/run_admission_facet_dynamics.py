#!/usr/bin/env python3
"""Paired exact synthetic pressure-dynamics audit for the facet ensemble.

This follow-up asks whether the local potential-geometry distinction alone
orders finite-horizon overflow. It is exploratory: a potential obstruction
does not imply a controller ranking.
"""

from __future__ import annotations

import csv
import json
import random
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from run_admission_facet_ensemble import (
    CAPACITIES,
    E,
    K,
    SEEDS,
    T,
    admit,
    counts,
    route_batch,
    scores,
)


HORIZON = 80
ETA = F(1, 10)
OUT = Path("results/admission_facet_dynamics")
CONTROLLERS = ("requested", "admitted", "no_feedback")


def make_plant(seed: int):
    rng = random.Random(seed)
    return tuple(tuple(rng.randint(-4, 4) for _ in range(E)) for _ in range(T))


def project_gauge(q):
    low = min(q)
    return tuple(value - low for value in q)


def run(seed: int, capacity_name: str, controller: str):
    affinities = make_plant(seed)
    capacity = CAPACITIES[capacity_name]
    q = tuple(F(0) for _ in range(E))
    rows = []
    route_history = None
    total_overflow = 0
    total_requested_imbalance = 0
    total_admitted_imbalance = 0
    state_changes = 0
    saturation_steps = 0
    for step in range(HORIZON):
        routes = route_batch(affinities, q)
        requested = counts(routes)
        admitted = admit(requested, capacity)
        overflow = sum(r - a for r, a in zip(requested, admitted))
        total_overflow += overflow
        saturation_steps += int(all(r >= c for r, c in zip(requested, capacity)))
        total_requested_imbalance += sum(abs(E * r - K * T) for r in requested)
        total_admitted_imbalance += sum(abs(E * a - K * T) for a in admitted)
        if route_history is not None:
            state_changes += sum(old != new for old, new in zip(route_history, routes))
        route_history = routes

        if controller == "requested":
            signal = requested
        elif controller == "admitted":
            signal = admitted
        else:
            signal = None
        if signal is None:
            update = tuple(F(0) for _ in range(E))
        else:
            update = tuple(F(signal[e], K * T) - F(1, E) for e in range(E))
        q = project_gauge(tuple(q[e] + ETA * update[e] for e in range(E)))

        rows.append({
            "seed": seed,
            "capacity_profile": capacity_name,
            "controller": controller,
            "step": step,
            "requested": list(requested),
            "admitted": list(admitted),
            "overflow": overflow,
            "pressure": [str(x) for x in q],
        })
    return {
        "seed": seed,
        "capacity_profile": capacity_name,
        "controller": controller,
        "horizon": HORIZON,
        "eta": str(ETA),
        "cumulative_overflow": total_overflow,
        "mean_overflow_per_step": F(total_overflow, HORIZON),
        "final_overflow": rows[-1]["overflow"],
        "saturation_steps": saturation_steps,
        "route_changes_across_updates": state_changes,
        "cumulative_requested_imbalance_scaled": total_requested_imbalance,
        "cumulative_admitted_imbalance_scaled": total_admitted_imbalance,
        "final_pressure": rows[-1]["pressure"],
        "trajectory": rows,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    runs = [
        run(seed, profile, controller)
        for profile in CAPACITIES
        for seed in SEEDS
        for controller in CONTROLLERS
    ]
    flat = [row for item in runs for row in item.pop("trajectory")]
    for row in flat:
        requested = tuple(row["requested"])
        admitted = tuple(row["admitted"])
        assert sum(requested) == K * T
        assert admitted == admit(requested, CAPACITIES[row["capacity_profile"]])
        assert row["overflow"] == sum(r - a for r, a in zip(requested, admitted))
        pressure = tuple(F(value) for value in row["pressure"])
        assert min(pressure) == 0
    with (OUT / "step_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0]))
        writer.writeheader()
        writer.writerows(flat)
    with (OUT / "run_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(runs[0]))
        writer.writeheader()
        writer.writerows(runs)

    paired = {}
    for profile in CAPACITIES:
        by_seed = {
            (r["seed"], r["controller"]): r
            for r in runs if r["capacity_profile"] == profile
        }
        result = {}
        for arm in ("admitted", "no_feedback"):
            diffs = [
                by_seed[(seed, arm)]["cumulative_overflow"]
                - by_seed[(seed, "requested")]["cumulative_overflow"]
                for seed in SEEDS
            ]
            ordered_diffs = sorted(diffs)
            median = F(ordered_diffs[19] + ordered_diffs[20], 2)
            result[f"{arm}_minus_requested_cumulative_overflow"] = {
                "mean_exact": str(F(sum(diffs), len(diffs))),
                "median_exact": str(median),
                "arm_worse_count": sum(d > 0 for d in diffs),
                "tie_count": sum(d == 0 for d in diffs),
                "arm_better_count": sum(d < 0 for d in diffs),
                "paired_differences": diffs,
            }
        result["mean_cumulative_overflow_by_controller"] = {
            controller: str(
                F(sum(by_seed[(seed, controller)]["cumulative_overflow"] for seed in SEEDS), len(SEEDS))
            )
            for controller in CONTROLLERS
        }
        paired[profile] = result

    # Exact negative control: no clipping makes requested and admitted signals
    # identical, so every step of those trajectories must match.
    by_step = {
        (int(r["seed"]), r["capacity_profile"], r["controller"], int(r["step"])): r
        for r in flat
    }
    for seed in SEEDS:
        for step in range(HORIZON):
            r_row = by_step[(seed, "no_clipping", "requested", step)]
            a_row = by_step[(seed, "no_clipping", "admitted", step)]
            for metric in ("requested", "admitted", "overflow", "pressure"):
                assert r_row[metric] == a_row[metric]

    summary = {
        "design": {
            "experts": E, "top_k": K, "tokens": T,
            "seeds": list(SEEDS), "horizon": HORIZON, "eta": str(ETA),
            "gamma": 1, "leak": 0,
            "affinities": "same per seed as the facet ensemble: iid integer Uniform[-4,4]",
            "pressure_step": "q_next = min-gauge(q + eta * (signal/(K*T) - uniform_target))",
            "controllers": list(CONTROLLERS),
            "primary_metric": "cumulative total overflow over the fixed 80-step horizon",
            "scope": "paired deterministic synthetic trajectories; not training or production evidence",
        },
        "paired_results": paired,
        "interpretation": (
            "This is a finite-horizon outcome audit of the same plants. It can show whether "
            "the potential-geometry result predicts behavior in this generator, but it cannot "
            "turn a local non-potential obstruction into a general performance theorem."
        ),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
