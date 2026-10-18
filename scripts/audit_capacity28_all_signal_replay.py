#!/usr/bin/env python3
"""Exact paired replay of all three C=28 capacity-sweep feedback arms.

Reconstructs each stored float64 affinity matrix as exact binary rationals,
uses the intended rational step alpha=1/40, and checks every requested and
admitted count vector against the saved 120-step trajectories for requested,
admitted, and no-feedback controllers. This is a post-hoc audit of the
existing synthetic experiment.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_capacity_regime_sweep.py"
REFERENCE = ROOT / "results" / "capacity_regime_sweep" / "trajectories.csv"
OUT = ROOT / "results" / "capacity_regime_sweep" / "capacity28_all_signal_replay.json"
C = 28
ALPHA = F(1, 40)
HORIZON = 120
SENSORS = ("admitted", "requested", "none")


def load_runner():
    spec = importlib.util.spec_from_file_location("capacity_sweep", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def center(xs: tuple[F, ...]) -> tuple[F, ...]:
    mean = sum(xs, F(0)) / len(xs)
    return tuple(x - mean for x in xs)


def choose(row: tuple[F, ...], bias: tuple[F, ...], k: int) -> tuple[int, ...]:
    # Stable descending ordering is equivalent to score descending, then the
    # lower expert index first. All audited route cutoffs are strict.
    return tuple(sorted(sorted(range(len(row)), key=lambda e: (-(row[e] + bias[e]), e))[:k]))


def feedback(counts: tuple[int, ...]) -> tuple[int, ...]:
    total = sum(counts)
    n = len(counts)
    return tuple((total > n * x) - (total < n * x) for x in counts)


def replay(seed: int, sensor: str, runner, reference_rows: dict) -> dict:
    e, k = runner.E, runner.K
    affinity_tensor = runner.build_affinities(seed)
    affinities = tuple(tuple(F.from_float(float(v)) for v in row) for row in affinity_tensor.tolist())
    bias = tuple(F(0) for _ in range(e))
    path = []
    min_margin: F | None = None
    first_flip = None
    first_saturation = None
    previous_routes = None
    cumulative_overflow = 0

    for step in range(HORIZON):
        token_routes = tuple(choose(row, bias, k) for row in affinities)
        requested = [0] * e
        margins = []
        for row, selected in zip(affinities, token_routes):
            scores = tuple(row[x] + bias[x] for x in range(e))
            ordered = sorted(scores, reverse=True)
            margins.append(ordered[k - 1] - ordered[k])
            for expert in selected:
                requested[expert] += 1
        margin = min(margins)
        min_margin = margin if min_margin is None else min(min_margin, margin)
        r = tuple(requested)
        if previous_routes is not None and first_flip is None and token_routes != previous_routes:
            first_flip = step
        previous_routes = token_routes
        a = tuple(min(x, C) for x in r)
        saturated = tuple(x for x, count in enumerate(r) if count >= C)
        if first_saturation is None and len(saturated) == e:
            first_saturation = step
        overflow = sum(r) - sum(a)
        cumulative_overflow += overflow
        observed = a if sensor == "admitted" else r if sensor == "requested" else None
        u = (0,) * e if observed is None else feedback(observed)
        bias_next = center(tuple(bias[i] + ALPHA * u[i] for i in range(e)))
        if sensor == "admitted" and len(saturated) == e and bias_next != bias:
            raise AssertionError("uniform-cap global saturation must freeze the admitted bias")
        bias = bias_next

        ref = reference_rows[(C, seed, sensor, step)]
        if tuple(json.loads(ref["requested"])) != r or tuple(json.loads(ref["admitted"])) != a:
            raise AssertionError(f"count mismatch: seed={seed}, sensor={sensor}, step={step}")
        path.append({
            "step": step,
            "requested": list(r),
            "admitted": list(a),
            "overflow": overflow,
            "cutoff_margin": str(margin),
            "saturated_experts": list(saturated),
        })

    return {
        "seed": seed,
        "sensor": sensor,
        "first_route_change_step": first_flip,
        "first_global_saturation_step": first_saturation,
        "minimum_topk_cutoff_margin": str(min_margin),
        "cumulative_overflow_H120": cumulative_overflow,
        "trajectory": path,
    }


def main() -> None:
    runner = load_runner()
    reference_rows = {}
    with REFERENCE.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if int(row["capacity"]) == C and row["drop_rule"] == "score" and row["sensor"] in SENSORS:
                reference_rows[(C, int(row["seed"]), row["sensor"], int(row["step"]))] = row

    trajectories = [
        replay(seed, sensor, runner, reference_rows)
        for seed in runner.SEEDS
        for sensor in SENSORS
    ]
    by_seed = {seed: {x["sensor"]: x for x in trajectories if x["seed"] == seed} for seed in runner.SEEDS}
    comparisons = []
    for seed in runner.SEEDS:
        a = by_seed[seed]["admitted"]["cumulative_overflow_H120"]
        r = by_seed[seed]["requested"]["cumulative_overflow_H120"]
        n = by_seed[seed]["none"]["cumulative_overflow_H120"]
        comparisons.append({"seed": seed, "admitted_minus_requested": a - r, "admitted_minus_none": a - n})

    margins = [F(x["minimum_topk_cutoff_margin"]) for x in trajectories]
    common_margin = min(margins)
    all_admitted_better = all(x["admitted_minus_requested"] < 0 and x["admitted_minus_none"] < 0 for x in comparisons)
    if not all_admitted_better:
        raise AssertionError("the paired admitted advantage failed in the exact replay")

    result = {
        "status": "PASS",
        "model": "existing E=8,K=2,T=128,C=28 capacity sweep; three signed-bias sensor arms",
        "arithmetic": "exact fractions reconstructed from stored float64 affinity entries; exact alpha=1/40",
        "horizon": HORIZON,
        "seeds": list(runner.SEEDS),
        "all_7200_sensor_step_count_pairs_match_saved_float64_sweep": True,
        "all_20_admitted_arms_have_lower_H120_overflow_than_requested_and_none": True,
        "common_minimum_topk_cutoff_margin": str(common_margin),
        "entrywise_perturbation_radius_preserving_all_three_arms": f"< {common_margin / 2}",
        "mean_cumulative_overflow": {
            sensor: str(F(sum(by_seed[s][sensor]["cumulative_overflow_H120"] for s in runner.SEEDS), len(runner.SEEDS)))
            for sensor in SENSORS
        },
        "mean_admitted_advantage": {
            "versus_requested": str(F(-sum(x["admitted_minus_requested"] for x in comparisons), len(comparisons))),
            "versus_none": str(F(-sum(x["admitted_minus_none"] for x in comparisons), len(comparisons))),
        },
        "per_seed_comparison": comparisons,
        "trajectories": trajectories,
        "source_hashes": {
            "sweep_script_sha256": hashlib.sha256(RUNNER_PATH.read_bytes()).hexdigest(),
            "reference_csv_sha256": hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
        },
        "scope_note": "Exact finite-horizon paired replay for 20 perturbed instances. Robustness is local to these matrices; this is not a population theorem or benchmark separation.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "status", "all_7200_sensor_step_count_pairs_match_saved_float64_sweep",
        "all_20_admitted_arms_have_lower_H120_overflow_than_requested_and_none",
        "common_minimum_topk_cutoff_margin", "entrywise_perturbation_radius_preserving_all_three_arms",
        "mean_cumulative_overflow", "mean_admitted_advantage",
    )}, indent=2))


if __name__ == "__main__":
    main()
