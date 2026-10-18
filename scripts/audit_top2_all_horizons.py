#!/usr/bin/env python3
"""Exact-rational finite-horizon audit for the P2f Top-2 family."""

from __future__ import annotations

import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "run_top2_signed_bias_separation.py"
OUT = ROOT / "results" / "top2_signed_bias_separation" / "all_horizon_audit.json"
HORIZON = 100
REPLICAS = (1, 3, 10)
GAINS = (F(9, 40), F(6, 25), F(1, 4))

spec = importlib.util.spec_from_file_location("p2f_runner", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load the audited route implementation: {SOURCE}")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def simulate(replica: int, gain: F, signal: str) -> list[int]:
    """Return cumulative overflow for batches 1..HORIZON, using exact rationals."""
    affinity_types = runner.BASE_AFFINITIES
    affinities = tuple(row for _ in range(replica) for row in affinity_types)
    capacities = (10 * replica,) * 3
    bias = (F(0),) * 3
    cumulative = 0
    costs: list[int] = []

    for _ in range(HORIZON):
        _, requested, _ = runner.route_batch(affinities, bias)
        admitted = tuple(min(requested[e], capacities[e]) for e in range(3))
        cumulative += sum(requested) - sum(admitted)
        costs.append(cumulative)
        signs = runner.expected_signs(signal, requested, admitted)
        bias = runner.centered(
            tuple(bias[e] + gain * signs[e] for e in range(3))
        )
    return costs


def main() -> None:
    cells = []
    for replica in REPLICAS:
        for gain in GAINS:
            trajectories = {
                signal: simulate(replica, gain, signal)
                for signal in ("admitted", "requested", "none")
            }
            a = trajectories["admitted"]
            r = trajectories["requested"]
            n = trajectories["none"]

            for h in range(1, HORIZON + 1):
                admitted_expected = (
                    11 * h * replica
                    if h <= 2
                    else 10 * h * replica + 3 * replica
                )
                assert a[h - 1] == admitted_expected, (
                    replica,
                    gain,
                    h,
                    "admitted",
                    a[h - 1],
                    admitted_expected,
                )
                assert n[h - 1] == 11 * h * replica, (
                    replica,
                    gain,
                    h,
                    "none",
                    n[h - 1],
                )
                if h <= 8:
                    assert r[h - 1] == 11 * h * replica, (
                        replica,
                        gain,
                        h,
                        "requested_exact_prefix",
                        r[h - 1],
                    )
                else:
                    assert r[h - 1] >= 10 * h * replica + 8 * replica, (
                        replica,
                        gain,
                        h,
                        "requested_lower_bound",
                        r[h - 1],
                    )
                if h <= 3:
                    assert a[h - 1] == r[h - 1] == n[h - 1]
                elif h >= 4:
                    assert a[h - 1] < r[h - 1]
                    assert a[h - 1] < n[h - 1]

            cells.append(
                {
                    "replication_m": replica,
                    "gain_theorem_units": str(gain),
                    "overflow": {
                        str(h): {
                            signal: trajectories[signal][h - 1]
                            for signal in ("admitted", "requested", "none")
                        }
                        for h in (3, 4, 8, 9, 20, 100)
                    },
                    "checked_all_integer_horizons_1_through_100": True,
                }
            )

    result = {
        "status": "PASS",
        "model": "P2f static E=3,K=2 Top-2 family; exact Fraction arithmetic",
        "horizon": HORIZON,
        "replication_factors": list(REPLICAS),
        "gains_theorem_units": [str(gain) for gain in GAINS],
        "paired_cells": len(cells),
        "claims_checked": [
            "admitted cumulative overflow exact for every H=1..100",
            "no-feedback cumulative overflow exact for every H=1..100",
            "requested cumulative overflow exact through H=8",
            "requested total-shortage lower bound for every H=9..100",
            "all arms tie through H=3 and admitted is strictly lower for H=4..100",
        ],
        "cells": cells,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "cells"}, indent=2))


if __name__ == "__main__":
    main()
