#!/usr/bin/env python3
"""Exact paired audit of a Top-2 admitted-sign finite-horizon theorem."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import subprocess
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "top2_signed_bias_separation"
SEEDS = tuple(range(100))
REPLICAS = (1, 3, 10)
SCORE_SCALE = F(1, 250)
ETAS = (F(9, 10000), F(3, 3125), F(1, 1000))
NOISE = (F(-1, 250000), F(0), F(1, 250000))
HORIZON = 9
CAPACITY = 10
BASE_AFFINITIES = (
    (F(0), F(5), F(11, 10)),
    *((F(0), F(101), F(100)) for _ in range(10)),
    *((F(2), F(6, 5), F(0)) for _ in range(9)),
)
MU_AFFINITIES = tuple(tuple(x * SCORE_SCALE for x in row) for row in BASE_AFFINITIES)
ETA_INTERVAL = (F(9, 10000), F(1, 1000))


def centered(values):
    mean = sum(values, F(0)) / len(values)
    return tuple(value - mean for value in values)


def perturbed_affinities(seed: int):
    rng = random.Random(seed)
    return tuple(tuple(x + rng.choice(NOISE) for x in row) for row in MU_AFFINITIES)


def tie_excluded(scores):
    return min(range(3), key=lambda e: (scores[e], e))


def route_batch(affinities, bias):
    excluded = []
    min_margins = []
    for row in affinities:
        scores = tuple(row[e] + bias[e] for e in range(3))
        order = sorted(range(3), key=lambda e: (scores[e], e))
        excluded.append(order[0])
        min_margins.append(scores[order[1]] - scores[order[0]])
    assert min(min_margins) > 0
    requested = tuple(sum(x != e for x in excluded) for e in range(3))
    return tuple(excluded), requested, min(min_margins)


def retained_ids(excluded, affinities, capacities, rule):
    retained = []
    for expert in range(3):
        ids = [t for t, ex in enumerate(excluded) if ex != expert]
        slots = capacities[expert]
        if rule == "score":
            ids.sort(key=lambda t: (-affinities[t][expert], t))
        elif rule == "position":
            ids.sort()
        else:
            raise ValueError(rule)
        retained.append(set(ids[:slots]))
    return tuple(retained)


def expected_signs(signal, requested, admitted):
    if signal == "none":
        return (F(0),) * 3
    counts = requested if signal == "requested" else admitted
    mean = F(sum(counts), 3)
    return tuple(F(1) if n < mean else F(-1) if n > mean else F(0) for n in counts)


def run(affinity_types, replica, eta, signal, drop_rule, cap_scale=1):
    affinities = tuple(row for _ in range(replica) for row in affinity_types)
    capacities = (CAPACITY * replica * cap_scale,) * 3
    bias = (F(0),) * 3
    rows = []
    for step in range(HORIZON):
        excluded, requested, margin = route_batch(affinities, bias)
        retained = retained_ids(excluded, affinities, capacities, drop_rule)
        admitted = tuple(sum(ex != e and t in retained[e] for t, ex in enumerate(excluded))
                         for e in range(3))
        assert admitted == tuple(min(requested[e], capacities[e]) for e in range(3))
        overflow = sum(requested) - sum(admitted)
        signs = expected_signs(signal, requested, admitted)
        rows.append({
            "step": step,
            "signal": signal,
            "drop_rule": drop_rule,
            "bias": [str(x) for x in bias],
            "excluded_counts": [sum(x == e for x in excluded) for e in range(3)],
            "retained_token_ids_by_expert": [sorted(ids) for ids in retained],
            "requested": list(requested),
            "admitted": list(admitted),
            "overflow": overflow,
            "cumulative_overflow": sum(r["overflow"] for r in rows) + overflow,
            "minimum_top2_cut_margin": str(margin),
            "globally_saturated": all(x >= capacities[0] for x in requested),
        })
        bias = centered(tuple(bias[e] + eta * signs[e] for e in range(3)))
    return rows


def main():
    protocol = ROOT / "docs" / "paper" / "top2_signed_bias_separation_protocol_2026-10-17.md"
    rows = []
    cells = []
    minimum_observed_margin = None
    minimum_base_margin = None

    for seed in SEEDS:
        affinity_types = perturbed_affinities(seed)
        for replica in REPLICAS:
            for eta in ETAS:
                arm_traces = {}
                for signal in ("admitted", "requested", "none"):
                    for rule in ("score", "position"):
                        trace = run(affinity_types, replica, eta, signal, rule)
                        arm_traces[(signal, rule)] = trace
                        rows.extend({"seed": seed, "replicas": replica, "eta": str(eta), **r} for r in trace)
                        for record in trace:
                            margin = F(record["minimum_top2_cut_margin"])
                            minimum_observed_margin = margin if minimum_observed_margin is None else min(minimum_observed_margin, margin)

                expected_counts = {
                    "admitted": [(9, 20, 11)] * 3 + [(10, 20, 10)] * 6,
                    "requested": [(9, 20, 11)] * 3 + [(9, 11, 20), (9, 20, 11),
                                   (9, 11, 20), (9, 20, 11), (9, 11, 20), (10, 20, 10)],
                    "none": [(9, 20, 11)] * HORIZON,
                }
                expected_hit = {"admitted": 3, "requested": 8, "none": None}
                expected_cost = {"admitted": 93 * replica, "requested": 98 * replica, "none": 99 * replica}
                for signal in ("admitted", "requested", "none"):
                    trace = arm_traces[(signal, "score")]
                    got = [tuple(r["requested"]) for r in trace]
                    assert got == [tuple(replica * x for x in counts) for counts in expected_counts[signal]], (
                        seed, replica, eta, signal, got
                    )
                    hit = next((i for i, r in enumerate(trace) if r["globally_saturated"]), None)
                    assert hit == expected_hit[signal], (seed, replica, eta, signal, hit)
                    assert trace[-1]["cumulative_overflow"] == expected_cost[signal]
                    pos = arm_traces[(signal, "position")]
                    for left, right in zip(trace, pos):
                        for key in ("bias", "excluded_counts", "requested", "admitted", "overflow"):
                            assert left[key] == right[key], (seed, replica, eta, signal, key)

                # Dropless control: cap all experts at 20m, so A=R and the
                # requested/admitted state trajectories must coincide.
                r0 = run(affinity_types, replica, eta, "requested", "score", cap_scale=2)
                a0 = run(affinity_types, replica, eta, "admitted", "score", cap_scale=2)
                for left, right in zip(r0, a0):
                    assert left["requested"] == right["requested"]
                    assert left["admitted"] == right["admitted"] == left["requested"]
                    assert left["bias"] == right["bias"]

                cells.append({
                    "seed": seed,
                    "replicas": replica,
                    "eta": str(eta),
                    "admitted_first_global_saturation": 3,
                    "requested_first_global_saturation": 8,
                    "none_global_saturation": False,
                    "overflow_h9_admitted": 93 * replica,
                    "overflow_h9_requested": 98 * replica,
                    "overflow_h9_none": 99 * replica,
                })

    # For the claimed compact gain interval, each required cut margin is
    # affine in eta inside its known routing cell; its minimum is attained at
    # an interval endpoint. This computes the exact unperturbed margin for
    # the prescribed route sequences in the base plant.
    for eta in ETA_INTERVAL:
        for signal in ("admitted", "requested", "none"):
            base_trace = run(MU_AFFINITIES, 1, eta, signal, "score")
            for record in base_trace:
                value = F(record["minimum_top2_cut_margin"])
                minimum_base_margin = value if minimum_base_margin is None else min(minimum_base_margin, value)

    summary = {
        "status": "PASS",
        "claim_scope": "fixed parameterized E=3,K=2 Top-2 affinity family, replicated m times; exact signed expert-bias feedback",
        "design": {
            "perturbations": len(SEEDS),
            "replicas": list(REPLICAS),
            "eta_grid": [str(x) for x in ETAS],
            "certified_compact_eta_interval": [str(x) for x in ETA_INTERVAL],
            "affinity_and_gain_scale_relative_to_theorem_units": str(SCORE_SCALE),
            "entrywise_affinity_noise": [str(x) for x in NOISE],
            "horizon_batches": HORIZON,
            "signals": ["admitted", "requested", "none"],
            "per_expert_retention_controls": ["score", "position"],
            "no_clipping_capacity": "20m per expert",
        },
        "checks": {
            "paired_cells": len(cells),
            "admitted_first_saturates_at_batch_3": True,
            "requested_first_saturates_at_batch_8": True,
            "none_never_saturates_in_horizon": True,
            "horizon_9_cumulative_overflow": {"admitted": "93m", "requested": "98m", "none": "99m"},
            "score_vs_position_count_and_state_paths_identical": True,
            "dropless_requested_vs_admitted_paths_identical": True,
            "minimum_base_cut_margin_over_compact_interval": str(minimum_base_margin),
            "minimum_perturbed_cut_margin_observed": str(minimum_observed_margin),
            "perturbed_routes_strict": minimum_observed_margin > 0,
        },
        "provenance": {
            "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "protocol_sha256": hashlib.sha256(protocol.read_bytes()).hexdigest(),
            "interpretation": "Perturbed plants are deterministic robustness checks inside the theorem's open margin region, not a population sample.",
        },
        "cells": cells,
    }
    assert minimum_base_margin == F(1, 2500), minimum_base_margin
    assert minimum_observed_margin >= minimum_base_margin - 2 * max(abs(x) for x in NOISE)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (OUT / "trajectories.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({k: v for k, v in summary.items() if k != "cells"}, indent=2))


if __name__ == "__main__":
    main()
