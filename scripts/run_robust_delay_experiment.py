#!/usr/bin/env python3
"""Exact paired perturbation experiment for the Top-1 delay theorem.

The theorem gives a uniform routing-margin certificate on eta in [0.08, 0.1].
This experiment samples affinity matrices inside the certified entrywise
neighborhood, replicates every token row, and checks requested/admitted
transients, per-expert drop-order invariance, and the dropless negative control.
All routing and state calculations use Fraction arithmetic.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import subprocess
from fractions import Fraction as F
from pathlib import Path

from audit_admitted_noncyclicity import AFFINITIES
from audit_closed_loop_admission_delay import ROUTE_STATES


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "closed_loop_delay_robustness"
SEEDS = tuple(range(100))
REPLICAS = (1, 2, 5, 10)
ETAS = (F(2, 25), F(9, 100), F(1, 10))
PERTURBATION_LEVELS = (F(-1, 1200), F(0), F(1, 1200))
CAPACITY = 1
START = (F(0), F(2), F(3))
MU = (F(1, 3),) * 3
CERTIFIED_MIN_MARGIN = F(1, 300)
MAX_ENTRYWISE_PERTURBATION = F(1, 1200)
HORIZON = 6


def perturbed_affinities(seed: int) -> tuple[tuple[F, ...], ...]:
    rng = random.Random(seed)
    return tuple(
        tuple(value + rng.choice(PERTURBATION_LEVELS) for value in row)
        for row in AFFINITIES
    )


def minimum_baseline_margin(lo: F, hi: F) -> F:
    margins = []
    for _name, base, slope, winners in ROUTE_STATES:
        for token, row in enumerate(AFFINITIES):
            winner = winners[token]
            for competitor in range(3):
                if competitor == winner:
                    continue
                intercept = row[winner] - base[winner] - row[competitor] + base[competitor]
                coefficient = -slope[winner] + slope[competitor]
                margins.extend((intercept + coefficient * lo, intercept + coefficient * hi))
    return min(margins)


def routes_and_margin(q: tuple[F, ...], affinities):
    winners = []
    minimum_margin = None
    for row in affinities:
        scores = tuple(row[e] - q[e] for e in range(3))
        order = sorted(range(3), key=lambda e: (-scores[e], e))
        margin = scores[order[0]] - scores[order[1]]
        assert margin > 0, (q, row, scores)
        minimum_margin = margin if minimum_margin is None else min(minimum_margin, margin)
        winners.append(order[0])
    counts = tuple(winners.count(e) for e in range(3))
    return tuple(winners), counts, minimum_margin


def admitted_route_ids(winners, affinities, capacity: int, rule: str):
    admitted = set()
    for expert in range(3):
        ids = [token for token, winner in enumerate(winners) if winner == expert]
        if rule == "score":
            ids.sort(key=lambda token: (-affinities[token][expert], token))
        elif rule == "position":
            ids.sort()
        else:
            raise ValueError(rule)
        admitted.update(ids[:capacity])
    return admitted


def one_run(base_affinities, replicas: int, eta: F, signal: str, rule: str, cap_scale: int = 1):
    affinities = tuple(row for _ in range(replicas) for row in base_affinities)
    tokens = len(affinities)
    capacity = CAPACITY * replicas * cap_scale
    q = START
    records = []
    cumulative_overflow = 0
    balanced_step = None
    for step in range(HORIZON):
        winners, requested, margin = routes_and_margin(q, affinities)
        kept = admitted_route_ids(winners, affinities, capacity, rule)
        admitted = tuple(sum(winner == e and token in kept for token, winner in enumerate(winners))
                         for e in range(3))
        overflow = sum(requested) - sum(admitted)
        cumulative_overflow += overflow
        if requested == (replicas,) * 3 and balanced_step is None:
            balanced_step = step
        observed = requested if signal == "requested" else admitted if signal == "admitted" else (0, 0, 0)
        z = tuple(q[e] + eta * (F(observed[e], tokens) - MU[e]) for e in range(3))
        floor = min(z)
        q_next = tuple(value - floor for value in z)
        records.append({
            "step": step,
            "signal": signal,
            "drop_rule": rule,
            "pressure": [str(x) for x in q],
            "requested": list(requested),
            "admitted": list(admitted),
            "overflow": overflow,
            "cumulative_overflow": cumulative_overflow,
            "minimum_top1_margin": str(margin),
            "balanced": requested == (replicas,) * 3,
        })
        q = q_next
    return records, balanced_step


def main() -> None:
    assert minimum_baseline_margin(F(2, 25), F(1, 10)) == CERTIFIED_MIN_MARGIN
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    cell_summaries = []
    min_observed_margin = None

    for seed in SEEDS:
        base = perturbed_affinities(seed)
        for replica in REPLICAS:
            for eta in ETAS:
                for rule in ("score", "position"):
                    for signal in ("requested", "admitted", "none"):
                        trace, balanced_step = one_run(base, replica, eta, signal, rule)
                        rows.extend({"seed": seed, "replicas": replica, "eta": str(eta), **r} for r in trace)
                        for r in trace:
                            margin = F(r["minimum_top1_margin"])
                            min_observed_margin = margin if min_observed_margin is None else min(min_observed_margin, margin)
                        if signal == "requested":
                            assert balanced_step == 2, (seed, replica, eta, rule, balanced_step)
                            assert trace[0]["requested"] == [0, replica, 2 * replica]
                            assert trace[1]["requested"] == [0, replica, 2 * replica]
                            assert trace[2]["requested"] == [replica, replica, replica]
                            assert trace[0]["cumulative_overflow"] == replica
                            assert trace[1]["cumulative_overflow"] == 2 * replica
                        elif signal == "admitted":
                            assert balanced_step == 3, (seed, replica, eta, rule, balanced_step)
                            assert all(trace[t]["requested"] == [0, replica, 2 * replica] for t in range(3))
                            assert trace[3]["requested"] == [replica, replica, replica]
                            assert trace[2]["cumulative_overflow"] == 3 * replica
                        else:
                            assert balanced_step is None, (seed, replica, eta, rule, balanced_step)
                            assert all(trace[t]["requested"] == [0, replica, 2 * replica] for t in range(HORIZON))

                # Paired score- and position-ranked admission must induce the
                # same count/state records because each expert fills its own cap.
                for signal in ("requested", "admitted", "none"):
                    score, _ = one_run(base, replica, eta, signal, "score")
                    position, _ = one_run(base, replica, eta, signal, "position")
                    for left, right in zip(score, position):
                        for key in ("pressure", "requested", "admitted", "overflow", "cumulative_overflow"):
                            assert left[key] == right[key], (seed, replica, eta, signal, key)

                # Capacity 3m is a no-clipping control for these three-token
                # replicated batches; requested and admitted state paths match.
                requested_drop, _ = one_run(base, replica, eta, "requested", "score", cap_scale=3)
                admitted_drop, _ = one_run(base, replica, eta, "admitted", "score", cap_scale=3)
                for left, right in zip(requested_drop, admitted_drop):
                    assert left["requested"] == right["requested"]
                    assert left["admitted"] == right["admitted"] == left["requested"]
                    assert left["pressure"] == right["pressure"]

                cell_summaries.append({
                    "seed": seed,
                    "replicas": replica,
                    "eta": str(eta),
                    "requested_balance_step": 2,
                    "admitted_balance_step": 3,
                    "requested_cumulative_overflow_to_balance": 2 * replica,
                    "admitted_cumulative_overflow_to_balance": 3 * replica,
                    "extra_admitted_overflow": replica,
                })

    protocol_path = ROOT / "docs" / "paper" / "closed_loop_delay_robustness_protocol_2026-10-17.md"
    source_revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    summary = {
        "status": "PASS",
        "scope": "deterministic exact-rational paired perturbation audit for the fixed E=3,K=1 Top-1 delay family",
        "design": {
            "seeds": list(SEEDS),
            "replicas": list(REPLICAS),
            "step_sizes": [str(x) for x in ETAS],
            "entrywise_perturbation_set": [str(x) for x in PERTURBATION_LEVELS],
            "certified_step_interval": ["2/25", "1/10"],
            "certified_baseline_minimum_route_margin": str(CERTIFIED_MIN_MARGIN),
            "maximum_entrywise_affinity_perturbation": str(MAX_ENTRYWISE_PERTURBATION),
            "horizon": HORIZON,
            "signals": ["requested", "admitted", "none"],
            "per_expert_drop_rules": ["score", "position"],
            "negative_control": "capacity 3m; requested and admitted paths must match",
        },
        "checks": {
            "paired_trials": len(cell_summaries),
            "all_requested_arms_balance_at_step_2": True,
            "all_admitted_arms_balance_at_step_3": True,
            "extra_overflow_equals_replica_count": True,
            "score_and_position_count_trajectories_identical": True,
            "dropless_requested_and_admitted_paths_identical": True,
            "no_feedback_remains_on_saturated_route_pattern": True,
            "minimum_observed_route_margin": str(min_observed_margin),
            "observed_margin_at_least_certified_lower_bound": min_observed_margin >= CERTIFIED_MIN_MARGIN - 2 * MAX_ENTRYWISE_PERTURBATION,
        },
        "provenance": {
            "source_revision": source_revision,
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "protocol_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            "summary_note": "100 perturbations are deterministic robustness checks inside a proved open parameter neighborhood, not a statistical sample of routers.",
        },
        "cells": cell_summaries,
    }
    assert summary["checks"]["observed_margin_at_least_certified_lower_bound"]
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (OUT / "trajectories.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({k: v for k, v in summary.items() if k != "cells"}, indent=2))


if __name__ == "__main__":
    main()
