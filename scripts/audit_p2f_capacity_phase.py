#!/usr/bin/env python3
"""Exact capacity-phase audit of the existing P2f Top-2 family.

This varies only the uniform per-expert capacity in the already-defined
three-row-type family. Routing, sign feedback, clipping, and costs use exact
integers/Fractions. A repeated exact pressure state certifies the subsequent
trajectory forever for each finite audited parameter cell.
"""

from __future__ import annotations

import importlib.util
import hashlib
import json
import math
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "run_top2_signed_bias_separation.py"
OUT = ROOT / "results" / "top2_signed_bias_separation" / "capacity_phase_audit.json"
CAPACITIES = tuple(range(1, 20))
GAINS = (F(9, 40), F(6, 25), F(1, 4))
MAX_STEPS = 2000
SIGNALS = ("admitted", "requested", "none")

spec = importlib.util.spec_from_file_location("p2f_runner", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load the audited P2f affinity fixture: {SOURCE}")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def omit_expert(scores: tuple[F, ...]) -> int:
    """Top-2 among three experts; lower expert index wins an exact score tie."""
    # The excluded expert is the lowest score; when the two lowest tie, the
    # higher index loses the Top-2 tie and is therefore omitted.
    return min(range(3), key=lambda e: (scores[e], -e))


def simulate(capacity: int, gain: F, signal: str) -> dict:
    affinities = runner.BASE_AFFINITIES
    bias = (F(0), F(0), F(0))
    seen: dict[tuple[F, ...], int] = {}
    overflows: list[int] = []
    requests: list[tuple[int, int, int]] = []
    first_global_saturation = None

    for step in range(MAX_STEPS):
        if bias in seen:
            cycle_start = seen[bias]
            cycle_end = step
            break
        seen[bias] = step

        excluded = []
        for row in affinities:
            scores = tuple(row[e] + bias[e] for e in range(3))
            excluded.append(omit_expert(scores))
        requested = tuple(sum(ex != e for ex in excluded) for e in range(3))
        admitted = tuple(min(requested[e], capacity) for e in range(3))
        overflow = sum(requested) - sum(admitted)
        requests.append(requested)
        overflows.append(overflow)

        if first_global_saturation is None and all(x >= capacity for x in requested):
            first_global_saturation = step

        signs = runner.expected_signs(signal, requested, admitted)
        bias = runner.centered(tuple(bias[e] + gain * signs[e] for e in range(3)))
    else:
        raise RuntimeError(
            f"No exact pressure-state cycle within {MAX_STEPS} steps for "
            f"C={capacity}, gain={gain}, signal={signal}"
        )

    period = cycle_end - cycle_start
    cycle_overflows = overflows[cycle_start:cycle_end]
    cycle_requests = requests[cycle_start:cycle_end]
    if period <= 0:
        raise AssertionError("cycle detector produced an empty cycle")

    def cumulative(horizon: int) -> int:
        """Exact cumulative overflow for any nonnegative horizon."""
        if horizon <= cycle_start:
            return sum(overflows[:horizon])
        pre_cost = sum(overflows[:cycle_start])
        cycles, remainder = divmod(horizon - cycle_start, period)
        return pre_cost + cycles * sum(cycle_overflows) + sum(cycle_overflows[:remainder])

    total_demand = 40
    capacity_total = 3 * capacity
    overflow_floor = max(0, total_demand - capacity_total)
    assert all(sum(row) == total_demand for row in requests)
    assert all(x >= overflow_floor for x in overflows)

    return {
        "cycle_start_state": cycle_start,
        "cycle_repeat_state": cycle_end,
        "cycle_period": period,
        "cycle_request_vectors": [list(x) for x in cycle_requests],
        "cycle_overflow": cycle_overflows,
        "cycle_mean_overflow": str(F(sum(cycle_overflows), period)),
        "first_global_saturation_batch": first_global_saturation,
        "cumulative_overflow": {
            str(h): cumulative(h) for h in (1, 4, 9, 100, 1000, 10000)
        },
        "capacity_lower_bound_per_batch": overflow_floor,
        "cycle_certifies_all_future_steps": True,
        "_overflows": overflows,
        "_requests": requests,
    }


def main() -> None:
    cells = []
    for capacity in CAPACITIES:
        for gain in GAINS:
            arms = {signal: simulate(capacity, gain, signal) for signal in SIGNALS}
            common_period = math.lcm(*(arms[s]["cycle_period"] for s in SIGNALS))
            common_prefix = max(arms[s]["cycle_start_state"] for s in SIGNALS)
            # Over this prefix plus one joint period, all transient behavior
            # and every eventual horizon residue are represented exactly.
            comparison_horizon = common_prefix + common_period
            gap_r_minus_a = []
            gap_none_minus_a = []
            for horizon in range(1, comparison_horizon + 1):
                # Reconstruct arbitrary horizons from the exact preperiod and cycle.
                def cost(signal: str, h: int) -> int:
                    item = arms[signal]
                    # Cycle and prefix vectors are saved internally below by rerunning
                    # the compact exact sequence for this cell if needed.
                    return _cost_from_saved(item, h)
                gap_r_minus_a.append(cost("requested", horizon) - cost("admitted", horizon))
                gap_none_minus_a.append(cost("none", horizon) - cost("admitted", horizon))

            cycle_drift_r_minus_a = (
                int(F(arms["requested"]["cycle_mean_overflow"]) * common_period)
                - int(F(arms["admitted"]["cycle_mean_overflow"]) * common_period)
            )
            cycle_drift_none_minus_a = (
                int(F(arms["none"]["cycle_mean_overflow"]) * common_period)
                - int(F(arms["admitted"]["cycle_mean_overflow"]) * common_period)
            )

            def exact_all_horizon_profile(gaps: list[int], drift: int) -> dict:
                # For h >= common_prefix, g(h + common_period) = g(h) + drift.
                # The checked prefix plus one joint period therefore determines
                # every horizon; drift gives the exact behavior of later copies.
                if drift > 0:
                    lower = min(gaps)
                    upper = "+infinity"
                elif drift < 0:
                    lower = "-infinity"
                    upper = max(gaps)
                else:
                    lower = min(gaps)
                    upper = max(gaps)

                strict_from = None
                prefix_gaps = gaps[:common_prefix]
                last_bad = max(
                    (h for h, value in enumerate(prefix_gaps, start=1) if value <= 0),
                    default=0,
                )
                eventual_gaps = gaps[common_prefix : common_prefix + common_period]
                if drift > 0:
                    for offset, value in enumerate(eventual_gaps, start=1):
                        if value <= 0:
                            last_bad = max(
                                last_bad,
                                common_prefix + offset
                                + ((-value) // drift) * common_period,
                            )
                    strict_from = last_bad + 1
                elif drift == 0:
                    if all(value > 0 for value in eventual_gaps):
                        strict_from = last_bad + 1
                return {
                    "minimum_gap_over_all_horizons": lower,
                    "maximum_gap_over_all_horizons": upper,
                    "strict_advantage_all_horizons_from": strict_from,
                }

            def request_at(signal: str, step: int) -> tuple[int, int, int]:
                item = arms[signal]
                seq = item["_requests"]
                start = item["cycle_start_state"]
                period = item["cycle_period"]
                if step < len(seq):
                    return tuple(seq[step])
                return tuple(seq[start + (step - start) % period])

            request_paths = {
                signal: [request_at(signal, t) for t in range(comparison_horizon)]
                for signal in SIGNALS
            }
            requested_admitted_paths_equal = (
                request_paths["requested"] == request_paths["admitted"]
            )

            r_minus_a_profile = exact_all_horizon_profile(
                gap_r_minus_a, cycle_drift_r_minus_a
            )
            none_minus_a_profile = exact_all_horizon_profile(
                gap_none_minus_a, cycle_drift_none_minus_a
            )
            arms_for_json = {
                signal: {
                    key: value
                    for key, value in item.items()
                    if key not in ("_overflows", "_requests")
                }
                for signal, item in arms.items()
            }
            cells.append(
                {
                    "capacity_per_expert": capacity,
                    "gain": str(gain),
                    "arms": arms_for_json,
                    "comparison_certificate": {
                        "joint_cycle_start_bound": common_prefix,
                        "joint_cycle_period": common_period,
                        "checked_horizons_through": comparison_horizon,
                        "requested_minus_admitted_gap_min": min(gap_r_minus_a),
                        "requested_minus_admitted_gap_max": max(gap_r_minus_a),
                        "no_feedback_minus_admitted_gap_min": min(gap_none_minus_a),
                        "no_feedback_minus_admitted_gap_max": max(gap_none_minus_a),
                        "requested_minus_admitted_drift_per_joint_period": cycle_drift_r_minus_a,
                        "no_feedback_minus_admitted_drift_per_joint_period": cycle_drift_none_minus_a,
                        "requested_minus_admitted_all_horizon": r_minus_a_profile,
                        "no_feedback_minus_admitted_all_horizon": none_minus_a_profile,
                        "requested_and_admitted_request_paths_equal_for_all_steps": requested_admitted_paths_equal,
                        "all_future_horizon_costs_and_gaps_certified_by_exact_cycles": True,
                    },
                }
            )

    result = {
        "status": "PASS",
        "arithmetic": "exact fractions.Fraction and integer counts",
        "family": "existing P2f E=3,K=2,T=20m affinity multiset, m=1 representative",
        "capacity_grid": list(CAPACITIES),
        "gain_grid": [str(x) for x in GAINS],
        "tie_rule": "Top-2; lower expert index wins exact score ties",
        "cycle_detection": "exact repeated gauge-centered bias state",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "audit_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "cells": cells,
        "replication_note": (
            "Repeating every affinity row m times and scaling capacities by m "
            "preserves the sign feedback and bias trajectories; all overflow "
            "costs and gaps scale by m."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "capacity_cells": len(CAPACITIES),
        "gain_cells": len(GAINS),
        "total_exact_cells": len(cells),
        "result": str(OUT),
    }, indent=2))


def _cost_from_saved(item: dict, horizon: int) -> int:
    # Reconstruct the small exact prefix/cycle by using the cached private
    # sequence attached during simulation. It is stripped before JSON output.
    costs = item["_overflows"]
    start = item["cycle_start_state"]
    end = item["cycle_repeat_state"]
    if horizon <= len(costs):
        return sum(costs[:horizon])
    period = end - start
    cycle = costs[start:end]
    cycles, remainder = divmod(horizon - start, period)
    return sum(costs[:start]) + cycles * sum(cycle) + sum(cycle[:remainder])


if __name__ == "__main__":
    main()
