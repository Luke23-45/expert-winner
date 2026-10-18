#!/usr/bin/env python3
"""Recompute paired summaries for the professor-directed admission pilot.

This is a descriptive analysis of the locked synthetic trajectory artifact,
not a new run and not a test of workload prevalence. It also rechecks the
exact negative controls before calculating any summary statistics.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


SEEDS = tuple(range(20))
STEPS = 120
EXPERTS = 8
TOKENS = 128
TOP_K = 2
EXPERT_CAPACITY = 24
OVERFLOW_FLOOR = TOKENS * TOP_K - EXPERTS * EXPERT_CAPACITY
T_CRIT_DF19 = 2.093024054


def load_rows(path: Path) -> dict[tuple[str, str, str, int], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str, str, int], list[dict[str, Any]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            row: dict[str, Any] = dict(raw)
            for name in ("step", "seed", "overflow"):
                row[name] = int(row[name])
            for name in ("bias_l2", "bias_linf"):
                row[name] = float(row[name])
            for name in ("requested", "admitted", "feedback", "bias"):
                row[name] = json.loads(row[name])
            for name in ("request_l1_from_uniform", "admitted_l1_from_uniform"):
                row[name] = float(row[name])
            key = (row["admission"], row["drop_rule"], row["sensor"], row["seed"])
            grouped[key].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda x: x["step"])
    return grouped


def check_controls(grouped: dict[tuple[str, str, str, int], list[dict[str, Any]]]) -> None:
    expected_arms = {
        ("per_expert", rule, sensor)
        for rule in ("score", "position")
        for sensor in ("requested", "admitted", "none")
    } | {
        ("device", rule, sensor)
        for rule in ("score", "position")
        for sensor in ("requested", "admitted", "none")
    } | {("none", "position", sensor) for sensor in ("requested", "admitted")}

    assert len(grouped) == len(expected_arms) * len(SEEDS), (
        f"expected {len(expected_arms) * len(SEEDS)} arm-seed groups, got {len(grouped)}"
    )
    for admission, rule, sensor in expected_arms:
        for seed in SEEDS:
            rows = grouped[(admission, rule, sensor, seed)]
            assert len(rows) == STEPS
            assert [r["step"] for r in rows] == list(range(STEPS))
            for row in rows:
                assert len(row["requested"]) == EXPERTS
                assert len(row["admitted"]) == EXPERTS
                assert sum(row["requested"]) == TOKENS * TOP_K
                assert sum(row["requested"]) - sum(row["admitted"]) == row["overflow"]
                if admission == "per_expert":
                    assert row["admitted"] == [min(x, EXPERT_CAPACITY) for x in row["requested"]]
                elif admission == "none":
                    assert row["admitted"] == row["requested"]

    fields = ("requested", "admitted", "feedback", "bias")
    for sensor in ("requested", "admitted", "none"):
        for seed in SEEDS:
            score = grouped[("per_expert", "score", sensor, seed)]
            position = grouped[("per_expert", "position", sensor, seed)]
            for left, right in zip(score, position):
                assert all(left[field] == right[field] for field in fields)

    for seed in SEEDS:
        requested = grouped[("none", "position", "requested", seed)]
        admitted = grouped[("none", "position", "admitted", seed)]
        for left, right in zip(requested, admitted):
            assert left["requested"] == left["admitted"]
            assert left["feedback"] == right["feedback"]
            assert left["bias"] == right["bias"]


def ci(values: list[float]) -> dict[str, float]:
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    half = T_CRIT_DF19 * sd / math.sqrt(len(values)) if len(values) == 20 else float("nan")
    return {"mean": mean, "sd": sd, "ci95_low": mean - half, "ci95_high": mean + half}


def summarize_arm(rows_by_seed: list[list[dict[str, Any]]]) -> dict[str, Any]:
    by_seed: list[dict[str, float]] = []
    for rows in rows_by_seed:
        saturated = [all(x >= EXPERT_CAPACITY for x in r["requested"]) for r in rows]
        first_exit = next((i for i, value in enumerate(saturated) if not value), None)
        by_seed.append(
            {
                "cumulative_overflow": float(sum(r["overflow"] for r in rows)),
                "time_mean_overflow": statistics.mean(r["overflow"] for r in rows),
                "final_overflow": float(rows[-1]["overflow"]),
                "time_mean_request_imbalance_l1": statistics.mean(
                    r["request_l1_from_uniform"] for r in rows
                ),
                "final_request_imbalance_l1": rows[-1]["request_l1_from_uniform"],
                "fraction_globally_saturated": statistics.mean(saturated),
                # The value 120 denotes right-censoring: no exit was observed
                # during the 120 recorded states, not an exit at step 120.
                "first_unsaturated_step_or_censor_120": float(first_exit) if first_exit is not None else float(STEPS),
                "max_bias_l2": max(r["bias_l2"] for r in rows),
                "final_bias_l2": rows[-1]["bias_l2"],
            }
        )
    metrics = by_seed[0].keys()
    result: dict[str, Any] = {metric: ci([x[metric] for x in by_seed]) for metric in metrics}
    result["seed_level_values"] = by_seed
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=Path("results/admission_geometry/trajectories.csv")
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    grouped = load_rows(args.input)
    check_controls(grouped)

    arm_stats: dict[str, Any] = {}
    for admission, rule, sensor in (
        ("per_expert", "score", "requested"),
        ("per_expert", "score", "admitted"),
        ("per_expert", "score", "none"),
        ("device", "score", "requested"),
        ("device", "score", "admitted"),
        ("device", "position", "requested"),
        ("device", "position", "admitted"),
        ("device", "position", "none"),
    ):
        name = f"{admission}/{rule}/{sensor}"
        arm_stats[name] = summarize_arm(
            [grouped[(admission, rule, sensor, seed)] for seed in SEEDS]
        )

    contrasts: dict[str, Any] = {}
    for comparator in ("admitted", "none"):
        left = [grouped[("per_expert", "score", "requested", seed)] for seed in SEEDS]
        right = [grouped[("per_expert", "score", comparator, seed)] for seed in SEEDS]
        for metric, fn in (
            ("cumulative_overflow", lambda rows: sum(r["overflow"] for r in rows)),
            ("time_mean_request_imbalance_l1", lambda rows: statistics.mean(r["request_l1_from_uniform"] for r in rows)),
            ("final_request_imbalance_l1", lambda rows: rows[-1]["request_l1_from_uniform"]),
            ("fraction_globally_saturated", lambda rows: statistics.mean(all(x >= EXPERT_CAPACITY for x in r["requested"]) for r in rows)),
        ):
            deltas = [float(fn(a) - fn(b)) for a, b in zip(left, right)]
            entry = ci(deltas)
            entry["positive_seed_count"] = sum(x > 0 for x in deltas)
            entry["negative_seed_count"] = sum(x < 0 for x in deltas)
            entry["zero_seed_count"] = sum(x == 0 for x in deltas)
            contrasts[f"requested_minus_{comparator}/{metric}"] = entry

    # The device/group-capacity arm is a separate constructed hybrid. Here
    # the paired intervention changes only the within-group drop ordering.
    for sensor in ("requested", "admitted", "none"):
        score = [grouped[("device", "score", sensor, seed)] for seed in SEEDS]
        position = [grouped[("device", "position", sensor, seed)] for seed in SEEDS]
        deltas = [
            float(sum(r["overflow"] for r in a) - sum(r["overflow"] for r in b))
            for a, b in zip(score, position)
        ]
        entry = ci(deltas)
        entry["positive_seed_count"] = sum(x > 0 for x in deltas)
        entry["negative_seed_count"] = sum(x < 0 for x in deltas)
        entry["zero_seed_count"] = sum(x == 0 for x in deltas)
        contrasts[f"device_score_minus_position/{sensor}/cumulative_overflow"] = entry

    result = {
        "analysis": {
            "source_csv": str(args.input),
            "seed_count": len(SEEDS),
            "steps": STEPS,
            "per_expert_overflow_floor_per_batch": OVERFLOW_FLOOR,
            "interval_note": (
                "95% paired-t intervals summarize this seeded perturbation generator; "
                "the 20 seeds vary small score noise on one fixed route-pair template and "
                "are not evidence of workload prevalence."
            ),
            "primary_outcome": "cumulative overflow over the 120-step static-batch run",
            "exact_controls": {
                "R_equals_A_trajectories_match_when_dropless": True,
                "per_expert_score_and_position_have_identical_count_feedback_trajectories": True,
                "per_expert_admission_equals_min_R_C_every_step": True,
                "mass_and_dropped_route_accounting_pass_every_step": True,
            },
        },
        "arms": arm_stats,
        "paired_contrasts": contrasts,
    }
    output = args.output or args.input.with_name("analysis_summary.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))
    print(f"Wrote {output.resolve()}")


if __name__ == "__main__":
    main()
