#!/usr/bin/env python3
"""Exact paired trajectory experiment joining sampled facet geometry to cost.

Run from the exploration repository root:
    python scripts/run_facet_trajectory_bridge.py

The input protocol is docs/paper/facet_to_trajectory_bridge_protocol_2026-10-17.md.
All controller arithmetic and cumulative overflow are exact Fractions.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path


E, K, T = 4, 2, 12
HORIZON = 120
ETA = F(1, 10)
GAMMA = F(1)
DELTA = F(0)
SEEDS = tuple(range(40))
CAPACITIES = {
    "no_clipping": (12, 12, 12, 12),
    "exact_total_uniform": (6, 6, 6, 6),
    "exact_total_heterogeneous": (2, 4, 8, 10),
    "aggregate_shortage": (3, 3, 3, 3),
}
ARMS = ("requested", "admitted", "none")
ROOT = Path(__file__).resolve().parents[1]
FACET_INPUT = ROOT / "results/admission_facet_ensemble/facet_observations.csv"
OUT = ROOT / "results/facet_trajectory_bridge"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def affinity_plant(seed: int) -> tuple[tuple[int, ...], ...]:
    rng = random.Random(seed)
    return tuple(tuple(rng.randint(-4, 4) for _ in range(E)) for _ in range(T))


def gauge_project(z: tuple[F, ...]) -> tuple[F, ...]:
    minimum = min(z)
    return tuple(value - minimum for value in z)


def route_token(affinity: tuple[int, ...], q: tuple[F, ...]) -> tuple[int, ...]:
    scores = tuple(F(a) - GAMMA * pressure for a, pressure in zip(affinity, q))
    return tuple(sorted(sorted(range(E), key=lambda e: (-scores[e], e))[:K]))


def request_counts(affinities: tuple[tuple[int, ...], ...], q: tuple[F, ...]) -> tuple[int, ...]:
    counts = [0] * E
    for affinity in affinities:
        for expert in route_token(affinity, q):
            counts[expert] += 1
    return tuple(counts)


def l1(values: tuple[int, ...]) -> int:
    return sum(abs(value) for value in values)


def norm_sq(values: tuple[F, ...]) -> F:
    return sum((value * value for value in values), F(0))


def one_arm(affinities, capacity, arm):
    q = tuple(F(0) for _ in range(E))
    previous_routes = None
    route_change_updates = 0
    first_global_saturation = None
    cumulative_overflow = F(0)
    trajectory = []
    initial_q = q
    for step in range(HORIZON):
        routes = tuple(route_token(affinity, q) for affinity in affinities)
        requested = [0] * E
        for selected in routes:
            for expert in selected:
                requested[expert] += 1
        requested = tuple(requested)
        assert sum(requested) == K * T
        admitted = tuple(min(r, c) for r, c in zip(requested, capacity))
        overflow = sum(requested) - sum(admitted)
        assert overflow == sum(r - a for r, a in zip(requested, admitted))
        cumulative_overflow += overflow
        saturated = all(r >= c for r, c in zip(requested, capacity))
        if saturated and first_global_saturation is None:
            first_global_saturation = step
        if previous_routes is not None and routes != previous_routes:
            route_change_updates += 1
        previous_routes = routes

        trajectory.append({
            "step": step,
            "requested": list(requested),
            "admitted": list(admitted),
            "overflow": overflow,
            "globally_saturated": saturated,
            "pressure": [str(x) for x in q],
        })

        if arm == "requested":
            observed = requested
        elif arm == "admitted":
            observed = admitted
        elif arm == "none":
            observed = None
        else:
            raise ValueError(arm)

        if observed is not None:
            feedback = tuple(
                F(observed[e], K * T) - F(1, E) for e in range(E)
            )
            z = tuple(
                (1 - DELTA) * q[e] + ETA * GAMMA * feedback[e]
                for e in range(E)
            )
            q = gauge_project(z)

    final_r = tuple(trajectory[-1]["requested"])
    target = F(K * T, E)
    return {
        "trajectory": trajectory,
        "cumulative_overflow": cumulative_overflow,
        "final_request_l1": sum(abs(F(x) - target) for x in final_r),
        "final_pressure_norm_sq": norm_sq(q),
        "route_change_updates": route_change_updates,
        "first_global_saturation": first_global_saturation,
        "initial_pressure_unchanged": q == initial_q if arm == "none" else None,
    }


def average_ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    result = [0.0] * len(values)
    cursor = 0
    while cursor < len(order):
        end = cursor + 1
        while end < len(order) and values[order[end]] == values[order[cursor]]:
            end += 1
        rank = ((cursor + 1) + end) / 2.0
        for position in range(cursor, end):
            result[order[position]] = rank
        cursor = end
    return result


def spearman(xs, ys):
    if len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    rx, ry = average_ranks(xs), average_ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    numerator = sum((x - mx) * (y - my) for x, y in zip(rx, ry))
    denominator = (sum((x - mx) ** 2 for x in rx) * sum((y - my) ** 2 for y in ry)) ** 0.5
    return numerator / denominator


def load_facet_fractions():
    if not FACET_INPUT.exists():
        raise FileNotFoundError(f"Required paired facet observations missing: {FACET_INPUT}")
    grouped = defaultdict(list)
    with FACET_INPUT.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            grouped[(int(row["seed"]), row["capacity_profile"])].append(row)
    output = {}
    for seed in SEEDS:
        for profile in CAPACITIES:
            rows = grouped[(seed, profile)]
            if not rows:
                raise ValueError(f"Missing facet observations for {(seed, profile)}")
            mismatched = sum(row["matched_facet"].lower() == "false" for row in rows)
            output[(seed, profile)] = F(mismatched, len(rows))
    return output


def exact_summary(values):
    values = sorted(values)
    n = len(values)
    median = values[n // 2] if n % 2 else (values[n // 2 - 1] + values[n // 2]) / 2
    return {
        "n": n,
        "mean": str(sum(values, F(0)) / n),
        "median": str(median),
        "min": str(values[0]),
        "max": str(values[-1]),
        "negative": sum(value < 0 for value in values),
        "zero": sum(value == 0 for value in values),
        "positive": sum(value > 0 for value in values),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    facet_fractions = load_facet_fractions()
    plant_hashes = {}
    trajectories = []
    paired = []
    initial_global_saturation_counts = {profile: 0 for profile in CAPACITIES}
    verified_uniform_admitted_freezes = 0
    for seed in SEEDS:
        affinities = affinity_plant(seed)
        encoded = json.dumps(affinities, separators=(",", ":")).encode()
        plant_hashes[str(seed)] = hashlib.sha256(encoded).hexdigest()
        for profile, capacity in CAPACITIES.items():
            results = {}
            for arm in ARMS:
                result = one_arm(affinities, capacity, arm)
                assert len(result["trajectory"]) == HORIZON
                results[arm] = result
                for step_row in result["trajectory"]:
                    trajectories.append({
                        "seed": seed,
                        "capacity_profile": profile,
                        "capacity": ",".join(map(str, capacity)),
                        "feedback": arm,
                        **step_row,
                    })

            if profile == "no_clipping":
                assert results["requested"]["trajectory"] == results["admitted"]["trajectory"]
            # A globally saturated initial state with uniform capacity must
            # remain fixed under admitted feedback for the full horizon.
            if len(set(capacity)) == 1 and all(
                r >= c for r, c in zip(results["admitted"]["trajectory"][0]["requested"], capacity)
            ):
                initial_global_saturation_counts[profile] += 1
                assert all(
                    row["pressure"] == results["admitted"]["trajectory"][0]["pressure"]
                    for row in results["admitted"]["trajectory"]
                )
                verified_uniform_admitted_freezes += 1

            delta = results["admitted"]["cumulative_overflow"] - results["requested"]["cumulative_overflow"]
            paired.append({
                "seed": seed,
                "capacity_profile": profile,
                "facet_mismatch_fraction": str(facet_fractions[(seed, profile)]),
                "overflow_requested": str(results["requested"]["cumulative_overflow"]),
                "overflow_admitted": str(results["admitted"]["cumulative_overflow"]),
                "overflow_none": str(results["none"]["cumulative_overflow"]),
                "D_admitted_minus_requested": str(delta),
                "request_l1_final_requested": str(results["requested"]["final_request_l1"]),
                "request_l1_final_admitted": str(results["admitted"]["final_request_l1"]),
                "pressure_norm_sq_final_requested": str(results["requested"]["final_pressure_norm_sq"]),
                "pressure_norm_sq_final_admitted": str(results["admitted"]["final_pressure_norm_sq"]),
                "route_change_updates_requested": results["requested"]["route_change_updates"],
                "route_change_updates_admitted": results["admitted"]["route_change_updates"],
                "first_global_saturation_requested": results["requested"]["first_global_saturation"],
                "first_global_saturation_admitted": results["admitted"]["first_global_saturation"],
            })

    trajectory_path = OUT / "trajectories.csv"
    with trajectory_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(trajectories[0]))
        writer.writeheader()
        writer.writerows(trajectories)
    paired_path = OUT / "paired_plants.csv"
    with paired_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)

    profile_summaries = {}
    for profile in CAPACITIES:
        subset = [row for row in paired if row["capacity_profile"] == profile]
        ds = [F(row["D_admitted_minus_requested"]) for row in subset]
        geometry = [F(row["facet_mismatch_fraction"]) for row in subset]
        profile_summaries[profile] = {
            "capacity": list(CAPACITIES[profile]),
            "paired_overflow_difference_D_admitted_minus_requested": exact_summary(ds),
            "mean_cumulative_overflow": {
                arm: str(sum((F(row[f"overflow_{arm}"]) for row in subset), F(0)) / len(subset))
                for arm in ("requested", "admitted", "none")
            },
            "spearman_facet_mismatch_fraction_vs_D": spearman(geometry, ds),
            "facet_mismatch_fraction_varies": len(set(geometry)) > 1,
            "D_varies": len(set(ds)) > 1,
        }

    protocol = ROOT / "docs/paper/facet_to_trajectory_bridge_protocol_2026-10-17.md"
    summary = {
        "status": "PASS",
        "experiment": "facet_to_trajectory_bridge",
        "evidence_class": "exploratory paired exact-rational synthetic mechanism study",
        "protocol": str(protocol.relative_to(ROOT)),
        "protocol_sha256": sha256(protocol),
        "script_sha256": sha256(Path(__file__)),
        "facet_input_sha256": sha256(FACET_INPUT),
        "dimensions": {"E": E, "K": K, "T": T, "horizon": HORIZON, "seeds": list(SEEDS)},
        "controller": {"eta": str(ETA), "gamma": str(GAMMA), "delta": str(DELTA), "target": "uniform", "projection": "min-coordinate gauge"},
        "plant_hashes": plant_hashes,
        "trajectory_rows": len(trajectories),
        "paired_plant_rows": len(paired),
        "exact_controls": {
            "all_mass_and_overflow_identities_pass": True,
            "requested_equals_admitted_under_no_clipping": True,
            "initially_globally_saturated_uniform_admitted_arms_freeze": verified_uniform_admitted_freezes == sum(initial_global_saturation_counts.values()),
            "initially_globally_saturated_uniform_admitted_arms_checked": verified_uniform_admitted_freezes,
            "initial_global_saturation_counts_by_profile": initial_global_saturation_counts,
            "all_arms_have_exact_horizon_length": True,
        },
        "profiles": profile_summaries,
        "interpretation": "Descriptive within this declared 40-plant generator only; correlation is not causal, and sampled facet mismatch is not a complete-arrangement prevalence estimate.",
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "trajectory_rows": len(trajectories), "profiles": profile_summaries, "summary": str(summary_path)}, indent=2))


if __name__ == "__main__":
    main()
