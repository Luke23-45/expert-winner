#!/usr/bin/env python3
"""Exact controlled audit for the balanced-request saturation-cost theorem."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "balanced_saturation_cost"
PROTOCOL = ROOT / "docs" / "paper" / "balanced_saturation_cost_experiment_protocol_2026-10-17.md"
SEEDS = tuple(range(10))
E_VALUES = (3, 4, 5, 6)
ETA = Fraction(1)
GAMMA = Fraction(1)
DELTA = Fraction(0)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def choose_ks(e: int) -> tuple[int, ...]:
    return tuple(dict.fromkeys((1, e // 2, e - 1)))


def make_plant(e: int, k: int, seed: int):
    m = e + 2
    subsets = list(itertools.combinations(range(e), k))
    t = m * len(subsets)
    n = k * t // e
    assert k * t % e == 0
    rng = random.Random(seed * 1_000_003 + e * 10_007 + k * 101)

    rows: list[tuple[Fraction, ...]] = []
    for subset in subsets:
        selected = set(subset)
        for _ in range(m):
            row = []
            for expert in range(e):
                jitter = Fraction(rng.randrange(1000), 100_000)
                row.append((Fraction(1) + jitter) if expert in selected else jitter)
            rows.append(tuple(row))
    rng.shuffle(rows)

    capacity_order = list(range(e))
    rng.shuffle(capacity_order)
    capacities = [0] * e
    for rank, expert in enumerate(capacity_order):
        capacities[expert] = n - (e - 1 - rank)
    assert min(capacities) > 0
    assert max(capacities) <= n
    ordered = sorted(capacities)
    assert ordered[k - 1] < ordered[k]
    assert sum(capacities) < k * t
    return rows, tuple(capacities), t, n


def project_gauge(q: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    minimum = min(q)
    return tuple(x - minimum for x in q)


def route_counts(rows, q: tuple[Fraction, ...], k: int):
    e = len(q)
    counts = [0] * e
    for row in rows:
        scores = [row[j] - GAMMA * q[j] for j in range(e)]
        order = sorted(range(e), key=lambda j: (-scores[j], j))
        selected = order[:k]
        for expert in selected:
            counts[expert] += 1
    return tuple(counts)


def normalized_minimum(q: tuple[Fraction, ...]):
    return project_gauge(q)


def update(q, signal, e: int, k: int, t: int):
    total = k * t
    mu = Fraction(1, e)
    raw = tuple(q[j] + ETA * GAMMA * (Fraction(signal[j], total) - mu) for j in range(e))
    return normalized_minimum(raw)


def n_sep_bound(rows, capacities, e: int, k: int, t: int):
    total = k * t
    mu = Fraction(1, e)
    cap_mean = Fraction(sum(capacities), e * total)
    # P_0(C/(KT)-mu); the uniform target is removed by projection.
    v = tuple(Fraction(c, total) - cap_mean for c in capacities)
    order = sorted(range(e), key=lambda j: (capacities[j], j))
    s = set(order[:k])
    assert capacities[order[k - 1]] < capacities[order[k]]
    alpha = ETA * GAMMA * GAMMA
    thresholds = []
    for row in rows:
        for i in s:
            for j in range(e):
                if j in s:
                    continue
                denominator = alpha * (v[j] - v[i])
                assert denominator > 0
                theta = -(row[i] - row[j]) / denominator
                thresholds.append(theta.numerator // theta.denominator)
    return max(0, 1 + max(thresholds)), tuple(sorted(s))


def one_arm(rows, capacities, e: int, k: int, t: int, h: int, arm: str):
    q = tuple(Fraction(0) for _ in range(e))
    trajectory = []
    tau = None
    d = k * t - sum(capacities)
    for state in range(h):
        request = route_counts(rows, q, k)
        admitted = tuple(min(request[j], capacities[j]) for j in range(e))
        overflow = sum(request) - sum(admitted)
        saturated = all(request[j] >= capacities[j] for j in range(e))
        if not saturated and tau is None:
            tau = state
        assert sum(request) == k * t
        assert overflow == sum(request[j] - admitted[j] for j in range(e))
        assert overflow - d == sum(capacities[j] - admitted[j] for j in range(e))
        trajectory.append({
            "state": state,
            "q": q,
            "R": request,
            "A": admitted,
            "J": overflow,
            "saturated": saturated,
            "unused_capacity": sum(capacities[j] - admitted[j] for j in range(e)),
        })
        if arm == "requested":
            signal = request
            q = update(q, signal, e, k, t)
        elif arm == "admitted":
            signal = admitted
            q = update(q, signal, e, k, t)
        elif arm == "none":
            pass
        else:
            raise ValueError(arm)
    return trajectory, tau


def verify_no_clipping(rows, e: int, k: int, t: int, h: int):
    capacity = (t,) * e
    requested, _ = one_arm(rows, capacity, e, k, t, h, "requested")
    admitted, _ = one_arm(rows, capacity, e, k, t, h, "admitted")
    assert requested == admitted


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plant_rows = []
    affinity_rows = []
    trajectory_rows = []
    checks = {
        "balanced_initial_counts": 0,
        "positive_capacities_below_balanced_count": 0,
        "strict_k_cut_gap": 0,
        "requested_equals_no_feedback": 0,
        "admitted_constant_feedback_until_exit": 0,
        "exit_within_n_sep": 0,
        "overflow_floor_identity_all_states": 0,
        "strict_excess_at_exit": 0,
        "nonnegative_prefix_gap": 0,
        "positive_prefix_by_n_sep_plus_one": 0,
        "no_clipping_equivalence": 0,
    }
    total_plants = 0
    for e in E_VALUES:
        for k in choose_ks(e):
            for seed in SEEDS:
                rows, capacities, t, n = make_plant(e, k, seed)
                plant_id = f"E{e}_K{k}_seed{seed:02d}"
                affinity_payload = "\n".join(
                    ",".join(str(value) for value in row) for row in rows
                ).encode("utf-8")
                affinity_hash = hashlib.sha256(affinity_payload).hexdigest()
                for token_index, row in enumerate(rows):
                    affinity_rows.append({
                        "plant_id": plant_id,
                        "E": e,
                        "K": k,
                        "T": t,
                        "seed": seed,
                        "token_index": token_index,
                        **{f"affinity_{expert}": str(value) for expert, value in enumerate(row)},
                    })
                h_bound, low_set = n_sep_bound(rows, capacities, e, k, t)
                h = h_bound + 2
                d = k * t - sum(capacities)
                req0 = route_counts(rows, tuple(Fraction(0) for _ in range(e)), k)
                assert req0 == (n,) * e
                assert all(0 < c <= n for c in capacities)
                sorted_c = sorted(capacities)
                assert sorted_c[k - 1] < sorted_c[k]
                checks["balanced_initial_counts"] += 1
                checks["positive_capacities_below_balanced_count"] += 1
                checks["strict_k_cut_gap"] += 1

                admitted, tau = one_arm(rows, capacities, e, k, t, h, "admitted")
                requested, tau_r = one_arm(rows, capacities, e, k, t, h, "requested")
                none, tau_n = one_arm(rows, capacities, e, k, t, h, "none")
                assert tau_r is None and tau_n is None
                assert all(s["q"] == (Fraction(0),) * e for s in requested + none)
                assert all(s["J"] == d for s in requested + none)
                checks["requested_equals_no_feedback"] += 1

                assert tau is not None and tau <= h_bound
                assert all(admitted[i]["saturated"] for i in range(tau))
                assert not admitted[tau]["saturated"]
                expected_q = tuple(Fraction(0) for _ in range(e))
                saturated_q_match = True
                for state in range(tau + 1):
                    if admitted[state]["q"] != expected_q:
                        saturated_q_match = False
                    expected_signal = capacities
                    expected_q = update(expected_q, expected_signal, e, k, t)
                assert saturated_q_match
                checks["admitted_constant_feedback_until_exit"] += 1
                checks["exit_within_n_sep"] += 1
                assert admitted[tau]["J"] > d
                checks["strict_excess_at_exit"] += 1

                cumulative_gap = 0
                positive_seen = False
                for state in range(h):
                    a = admitted[state]
                    assert a["J"] - d == a["unused_capacity"] >= 0
                    checks["overflow_floor_identity_all_states"] += 1
                    cumulative_gap += a["J"] - requested[state]["J"]
                    assert cumulative_gap >= 0
                    positive_seen = positive_seen or cumulative_gap > 0
                assert positive_seen
                assert sum(admitted[i]["J"] - requested[i]["J"] for i in range(h_bound + 1)) > 0
                checks["nonnegative_prefix_gap"] += 1
                checks["positive_prefix_by_n_sep_plus_one"] += 1

                arm_paths = {
                    "admitted": admitted,
                    "requested": requested,
                    "none": none,
                }
                no_clip_h = h
                no_clip_capacity = (t,) * e
                no_clip_requested, _ = one_arm(rows, no_clip_capacity, e, k, t, no_clip_h, "requested")
                no_clip_admitted, _ = one_arm(rows, no_clip_capacity, e, k, t, no_clip_h, "admitted")
                assert no_clip_requested == no_clip_admitted
                arm_paths["no_clipping_requested"] = no_clip_requested
                arm_paths["no_clipping_admitted"] = no_clip_admitted
                checks["no_clipping_equivalence"] += 1

                for arm_name, path in arm_paths.items():
                    running_gap = 0
                    for state, record in enumerate(path):
                        baseline_cost = requested[state]["J"] if state < h else 0
                        running_gap += record["J"] - baseline_cost
                        floor = d if arm_name in {"admitted", "requested", "none"} else 0
                        trajectory_rows.append({
                            "E": e, "K": k, "T": t, "seed": seed,
                            "state": state, "arm": arm_name,
                            "saturated": int(record["saturated"]),
                            "overflow": record["J"],
                            "overflow_floor": floor,
                            "excess_over_floor": record["J"] - floor,
                            "cumulative_gap_vs_requested": running_gap,
                            "q": ";".join(str(x) for x in record["q"]),
                            "R": ";".join(str(x) for x in record["R"]),
                            "A": ";".join(str(x) for x in record["A"]),
                        })

                plant_rows.append({
                    "plant_id": plant_id,
                    "E": e, "K": k, "T": t, "n": n, "seed": seed,
                    "affinity_sha256": affinity_hash,
                    "capacities": ";".join(map(str, capacities)),
                    "low_capacity_set": ";".join(map(str, low_set)),
                    "aggregate_shortage_D": d,
                    "N_sep": h_bound,
                    "tau_admitted": tau,
                    "horizon": h,
                    "strict_gap_by_N_sep_plus_one": sum(admitted[i]["J"] - requested[i]["J"] for i in range(h_bound + 1)),
                    "final_cumulative_gap": sum(admitted[i]["J"] - requested[i]["J"] for i in range(h)),
                    "initial_request": ";".join(map(str, req0)),
                    "no_clipping_control": "passed",
                })
                total_plants += 1

    def write_csv(path: Path, data: list[dict], fieldnames=None):
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames or list(data[0]))
            writer.writeheader()
            writer.writerows(data)

    plants_path = OUT / "plants.csv"
    affinities_path = OUT / "affinities.csv"
    trajectories_path = OUT / "trajectories.csv"
    write_csv(plants_path, plant_rows)
    affinity_fields = ["plant_id", "E", "K", "T", "seed", "token_index"]
    affinity_fields.extend(f"affinity_{expert}" for expert in range(max(E_VALUES)))
    write_csv(affinities_path, affinity_rows, affinity_fields)
    write_csv(trajectories_path, trajectory_rows)
    summary = {
        "experiment": "balanced_saturation_cost",
        "seed_schedule": list(SEEDS),
        "E_values": list(E_VALUES),
        "K_rule": "deduplicated {1, floor(E/2), E-1}",
        "controller": "canonical proportional gauge-pressure; eta=gamma=1; delta=0",
        "target": "uniform",
        "arithmetic": "fractions.Fraction; exact top-k, pressure, clipping, and overflow",
        "plants": total_plants,
        "cells": sum(len(choose_ks(e)) for e in E_VALUES),
        "checks": checks,
        "all_checks_passed": (
            all(v == total_plants for k, v in checks.items() if k != "overflow_floor_identity_all_states")
            and checks["overflow_floor_identity_all_states"] == sum(row["horizon"] for row in plant_rows)
            and len(trajectory_rows) == 5 * sum(row["horizon"] for row in plant_rows)
        ),
        "plant_artifact_rows": len(plant_rows),
        "affinity_artifact_rows": len(affinity_rows),
        "trajectory_artifact_rows": len(trajectory_rows),
        "protocol_sha256": sha256(PROTOCOL),
        "runner_sha256": sha256(Path(__file__)),
        "plants_sha256": sha256(plants_path),
        "affinities_sha256": sha256(affinities_path),
        "trajectories_sha256": sha256(trajectories_path),
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    assert summary["all_checks_passed"]


if __name__ == "__main__":
    main()
