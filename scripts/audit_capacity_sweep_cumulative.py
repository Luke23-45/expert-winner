#!/usr/bin/env python3
"""Recompute capacity-sweep cumulative overflow without duplicate drop arms.

The experiment verifies that score-ranked and position-ranked retention have
identical per-expert count trajectories. This audit uses one representative
row per seed and capacity, then recomputes paired cumulative-overflow means
and lower/equal/higher counts against no feedback.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results" / "capacity_regime_sweep" / "trajectories.csv"
EXACT_REPLAY = ROOT / "results" / "capacity_regime_sweep" / "capacity28_exact_replay.json"
OUT = ROOT / "results" / "capacity_regime_sweep" / "cumulative_overflow_audit.json"
SENSORS = ("none", "admitted", "requested")
DROP_RULES = ("score", "position")


def main() -> None:
    grouped: dict[tuple[int, int, str, str], list[dict]] = defaultdict(list)
    with SOURCE.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            grouped[(int(row["capacity"]), int(row["seed"]), row["drop_rule"], row["sensor"])].append(row)

    capacities = sorted({key[0] for key in grouped})
    seeds = sorted({key[1] for key in grouped})
    for c in capacities:
        for seed in seeds:
            for sensor in SENSORS:
                arms = {}
                for rule in DROP_RULES:
                    rows = sorted(grouped[(c, seed, rule, sensor)], key=lambda r: int(r["step"]))
                    if len(rows) != 120 or [int(r["step"]) for r in rows] != list(range(120)):
                        raise AssertionError(f"incomplete or duplicated trajectory: C={c}, seed={seed}, {rule}, {sensor}")
                    arms[rule] = rows
                for step, (score, position) in enumerate(zip(arms["score"], arms["position"])):
                    for field in ("requested", "admitted", "feedback", "bias", "overflow"):
                        if score[field] != position[field]:
                            raise AssertionError(f"drop-rule rows differ: C={c}, seed={seed}, sensor={sensor}, step={step}, field={field}")

    summaries = []
    per_seed = {}
    for c in capacities:
        values: dict[str, dict[int, int]] = {}
        for sensor in SENSORS:
            values[sensor] = {}
            for seed in seeds:
                rows = grouped[(c, seed, "score", sensor)]
                if len(rows) != 120:
                    raise AssertionError(f"missing score representative: C={c}, seed={seed}, {sensor}")
                total = sum(int(r["overflow"]) for r in rows)
                values[sensor][seed] = total
                per_seed[f"{c}:{seed}:{sensor}"] = total

        baseline = values["none"]
        for sensor in SENSORS:
            totals = values[sensor]
            mean = F(sum(totals.values()), len(seeds))
            entry = {
                "capacity": c,
                "sensor": sensor,
                "seed_count": len(seeds),
                "mean_cumulative_overflow_exact": str(mean),
                "mean_cumulative_overflow": float(mean),
                "range_cumulative_overflow": [min(totals.values()), max(totals.values())],
            }
            if sensor != "none":
                diffs = [totals[s] - baseline[s] for s in seeds]
                mean_change = F(sum(diffs), len(seeds))
                entry.update({
                    "mean_change_vs_no_feedback_exact": str(mean_change),
                    "mean_change_vs_no_feedback": float(mean_change),
                    "lower_equal_higher_seed_counts": [sum(d < 0 for d in diffs), sum(d == 0 for d in diffs), sum(d > 0 for d in diffs)],
                })
            summaries.append(entry)

    exact = json.loads(EXACT_REPLAY.read_text(encoding="utf-8"))
    if exact["status"] != "PASS":
        raise AssertionError("the C=28 exact replay is not marked PASS")
    replay_totals = {x["seed"]: x["cumulative_overflow_H120"] for x in exact["all_steps"]}
    if replay_totals != {s: per_seed[f"28:{s}:admitted"] for s in seeds}:
        raise AssertionError("C=28 admitted cumulative totals differ from exact replay")

    result = {
        "status": "PASS",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "method": "verified score/position duplicate trajectories, then used score rows once per seed/capacity/sensor",
        "capacities": capacities,
        "seeds": seeds,
        "updates_per_cell": 120,
        "summaries": summaries,
        "per_seed_cumulative_overflow": per_seed,
        "c28_admitted_crosscheck_against_exact_rational_replay": True,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "summaries": summaries,
        "c28_admitted_crosscheck_against_exact_rational_replay": True,
        "output": str(OUT),
    }, indent=2))


if __name__ == "__main__":
    main()
