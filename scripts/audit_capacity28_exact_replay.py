#!/usr/bin/env python3
"""Exact rational replay of the existing C=28 admitted-bias sweep arm.

This post-hoc audit reconstructs the same 20 seeded affinity matrices, treats
their stored float64 entries as exact binary rationals, uses alpha=1/40, and
checks every request vector against the saved float64 sweep trajectory.
It is an audit of the existing experiment, not a new model or preregistered
confirmatory experiment.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_capacity_regime_sweep.py"
REFERENCE = ROOT / "results" / "capacity_regime_sweep" / "trajectories.csv"
OUT = ROOT / "results" / "capacity_regime_sweep" / "capacity28_exact_replay.json"
CAPACITY = 28
ALPHA = F(1, 40)
MAX_STEPS = 120


def load_runner():
    spec = importlib.util.spec_from_file_location("capacity_sweep", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import sweep implementation {RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def centered(xs: tuple[F, ...]) -> tuple[F, ...]:
    mean = sum(xs, F(0)) / len(xs)
    return tuple(x - mean for x in xs)


def route(row: tuple[F, ...], bias: tuple[F, ...], top_k: int) -> tuple[int, ...]:
    order = sorted(range(len(row)), key=lambda e: (-(row[e] + bias[e]), e))
    return tuple(sorted(order[:top_k]))


def sign_feedback(counts: tuple[int, ...]) -> tuple[int, ...]:
    total = sum(counts)
    n = len(counts)
    return tuple((total > n * x) - (total < n * x) for x in counts)


def main() -> None:
    runner = load_runner()
    E, K, T = runner.E, runner.K, runner.TOKENS
    reference_rows: dict[tuple[int, int], dict] = {}
    with REFERENCE.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if int(row["capacity"]) == CAPACITY and row["sensor"] == "admitted" and row["drop_rule"] == "score":
                reference_rows[(int(row["seed"]), int(row["step"]))] = row

    results = []
    common_path_prefix = None
    for seed in runner.SEEDS:
        float_affinities = runner.build_affinities(seed)
        affinities = tuple(
            tuple(F.from_float(float(value)) for value in row)
            for row in float_affinities.tolist()
        )
        bias = tuple(F(0) for _ in range(E))
        trajectory = []
        min_margin: F | None = None
        first_flip = None
        previous_routes = None
        first_global_saturation = None
        cumulative_overflow = 0

        for step in range(MAX_STEPS):
            token_routes = tuple(route(row, bias, K) for row in affinities)
            margins = []
            requested = [0] * E
            for row, selected in zip(affinities, token_routes):
                scores = tuple(row[e] + bias[e] for e in range(E))
                ranked = sorted(scores, reverse=True)
                margins.append(ranked[K - 1] - ranked[K])
                for e in selected:
                    requested[e] += 1
            margin = min(margins)
            min_margin = margin if min_margin is None else min(min_margin, margin)
            requested_tuple = tuple(requested)
            if previous_routes is not None and first_flip is None and token_routes != previous_routes:
                first_flip = step
            previous_routes = token_routes
            saturated = tuple(e for e, x in enumerate(requested_tuple) if x >= CAPACITY)
            if first_global_saturation is None and len(saturated) == E:
                first_global_saturation = step
            admitted = tuple(min(x, CAPACITY) for x in requested_tuple)
            overflow = sum(requested_tuple) - sum(admitted)
            cumulative_overflow += overflow
            update = sign_feedback(admitted)
            bias_next = centered(tuple(bias[e] + ALPHA * update[e] for e in range(E)))
            if len(saturated) == E and bias_next != bias:
                raise AssertionError("uniform-cap global saturation should freeze exact bias")
            bias = bias_next

            ref = reference_rows.get((seed, step))
            if ref is None:
                raise AssertionError(f"missing reference row seed={seed}, step={step}")
            ref_requested = tuple(json.loads(ref["requested"]))
            ref_admitted = tuple(json.loads(ref["admitted"]))
            if requested_tuple != ref_requested or admitted != ref_admitted:
                raise AssertionError({
                    "seed": seed, "step": step,
                    "exact_requested": requested_tuple, "float_requested": ref_requested,
                    "exact_admitted": admitted, "float_admitted": ref_admitted,
                    "minimum_cutoff_margin_so_far": str(min_margin),
                })
            trajectory.append({
                "step": step,
                "requested": list(requested_tuple),
                "saturated_experts": list(saturated),
                "overflow": overflow,
                "cutoff_margin": str(margin),
            })
            if first_global_saturation is not None:
                # The exact control says the globally saturated state is fixed.
                if any(x < CAPACITY for x in requested_tuple):
                    raise AssertionError("global saturation lost after entry")
                if step + 1 < MAX_STEPS:
                    # Bias has zero update under uniform capacity, hence future
                    # routing is identical. Continue to check against all saved rows.
                    pass

        if first_flip != 76:
            raise AssertionError(f"unexpected first routing change seed={seed}: {first_flip}")
        if first_global_saturation is None:
            raise AssertionError(f"seed {seed} did not reach global saturation")
        prefix = [x["requested"] for x in trajectory[:76]]
        if common_path_prefix is None:
            common_path_prefix = prefix
        elif prefix != common_path_prefix:
            raise AssertionError(f"seeds do not share the expected initial 76-state path: {seed}")
        results.append({
            "seed": seed,
            "first_routing_change_step": first_flip,
            "first_global_saturation_step": first_global_saturation,
            "steps_from_first_change_to_saturation": first_global_saturation - first_flip,
            "minimum_topk_cutoff_margin_through_step_119": str(min_margin),
            "cumulative_overflow_H120": cumulative_overflow,
            "trajectory": trajectory,
        })

    result = {
        "status": "PASS",
        "experiment": "existing E=8,K=2,T=128,C=28 admitted-sign-bias arm",
        "arithmetic": "exact fractions reconstructed from stored float64 affinity entries; exact alpha=1/40",
        "seeds": list(runner.SEEDS),
        "all_120_requested_and_admitted_vectors_match_saved_float64_sweep": True,
        "shared_requested_path_through_steps_0_to_75": True,
        "shared_path_length": 76,
        "distinct_full_requested_trajectories": len({
            tuple(tuple(x["requested"]) for x in r["trajectory"])
            for r in results
        }),
        "first_routing_change_step": 76,
        "first_global_saturation_step_range": [min(x["first_global_saturation_step"] for x in results), max(x["first_global_saturation_step"] for x in results)],
        "steps_from_first_change_to_saturation_range": [min(x["steps_from_first_change_to_saturation"] for x in results), max(x["steps_from_first_change_to_saturation"] for x in results)],
        "first_global_saturation_step_counts": {str(k): v for k, v in sorted(Counter(x["first_global_saturation_step"] for x in results).items())},
        "minimum_cutoff_margin_over_all_seeds_and_steps": str(min(F(x["minimum_topk_cutoff_margin_through_step_119"]) for x in results)),
        "all_steps": results,
        "source_hashes": {
            "sweep_script_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
            "reference_csv_sha256": hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
        },
        "scope_note": "A post-hoc exact replay of a fixed synthetic sweep. It does not establish a theorem for other affinity matrices or a benchmark separation.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "status", "all_120_requested_and_admitted_vectors_match_saved_float64_sweep",
        "shared_path_length", "first_global_saturation_step_range",
        "steps_from_first_change_to_saturation_range", "first_global_saturation_step_counts",
        "minimum_cutoff_margin_over_all_seeds_and_steps",
    )}, indent=2))


if __name__ == "__main__":
    main()
