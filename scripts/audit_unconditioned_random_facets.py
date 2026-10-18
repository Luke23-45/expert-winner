#!/usr/bin/env python3
"""Exact finite-grid audit of the unconditioned random-facet theorem."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from pathlib import Path


E = 4
K = 2
TOKENS = (16, 64, 256, 1024, 4096)
REPLICATES = 500
GRID = 1 << 30
SEED_BASE = 20261017
OUT = Path("results/unconditioned_random_facets")


def is_candidate(row: tuple[int, ...], n: int) -> bool:
    """Exact-grid version of the proof's near-tie/rank event."""
    x0, x1, x2, x3 = row
    total = x0 + x1
    # 5/12 <= (x0+x1)/(2 GRID) <= 7/12.
    if not (5 * GRID <= 6 * total <= 7 * GRID):
        return False
    # |x0-x1|/GRID <= 1/sqrt(n), without floating point.
    if (x0 - x1) ** 2 * n > GRID**2:
        return False
    above = int(2 * x2 > total) + int(2 * x3 > total)
    tied_outsider = 2 * x2 == total or 2 * x3 == total or x2 == x3
    return above == K - 1 and not tied_outsider


def facet_scores2(row: tuple[int, ...], delta: int) -> tuple[int, ...]:
    """Scores scaled by 2*GRID at q=(delta/(2*GRID),-delta/(2*GRID),0,0)."""
    x0, x1, x2, x3 = row
    return (2 * x0 - delta, 2 * x1 + delta, 2 * x2, 2 * x3)


def has_any_tie(values: tuple[int, ...]) -> bool:
    return len(set(values)) != len(values)


def run_one(n: int, replicate: int) -> dict[str, int | float | bool | None]:
    seed = SEED_BASE + 10_000 * n + replicate
    rng = random.Random(seed)
    rows = [tuple(rng.randrange(GRID + 1) for _ in range(E)) for _ in range(n)]
    tau = next((idx for idx, row in enumerate(rows) if is_candidate(row, n)), None)
    if tau is None:
        return {
            "T": n,
            "replicate": replicate,
            "seed": seed,
            "candidate_found": False,
            "regular": False,
            "mismatch": False,
            "no_clipping_mismatch": False,
            "tau_fraction": None,
            "x0_fraction": None,
            "x1_fraction": None,
        }

    # The selected row must have the designed exact Top-2 boundary tie.
    delta = rows[tau][0] - rows[tau][1]
    selected_scores = facet_scores2(rows[tau], delta)
    if selected_scores[0] != selected_scores[1]:
        raise AssertionError("candidate did not create the intended tie")
    if sum(score > selected_scores[0] for score in selected_scores[2:]) != K - 1:
        raise AssertionError("candidate tie is not at the Top-2 boundary")

    other_score_rows = [
        facet_scores2(row, delta) for idx, row in enumerate(rows) if idx != tau
    ]
    regular = not any(has_any_tie(scores) for scores in other_score_rows)
    if not regular:
        return {
            "T": n,
            "replicate": replicate,
            "seed": seed,
            "candidate_found": True,
            "regular": False,
            "mismatch": False,
            "no_clipping_mismatch": False,
            "tau_fraction": tau / n,
            "x0_fraction": None,
            "x1_fraction": None,
        }

    counts = [0] * E
    for scores in other_score_rows:
        winners = sorted(range(E), key=lambda e: (-scores[e], e))[:K]
        for expert in winners:
            counts[expert] += 1

    capacities = (n // 4, 3 * n // 4, n // 2, n // 2)
    d0 = counts[0] < capacities[0]
    d1 = counts[1] < capacities[1]
    mismatch = d0 != d1
    no_clip_mismatch = (counts[0] < n) != (counts[1] < n)
    if no_clip_mismatch:
        raise AssertionError("no-clipping negative control failed")

    return {
        "T": n,
        "replicate": replicate,
        "seed": seed,
        "candidate_found": True,
        "regular": True,
        "mismatch": mismatch,
        "no_clipping_mismatch": no_clip_mismatch,
        "tau_fraction": tau / n,
        "x0_fraction": counts[0] / n,
        "x1_fraction": counts[1] / n,
    }


def summarize(records: list[dict[str, int | float | bool | None]]) -> list[dict[str, int | float]]:
    summaries = []
    for n in TOKENS:
        group = [record for record in records if record["T"] == n]
        found = [record for record in group if record["candidate_found"]]
        regular = [record for record in found if record["regular"]]
        mismatches = sum(bool(record["mismatch"]) for record in regular)
        unconditional = sum(bool(record["mismatch"]) for record in group)
        summaries.append(
            {
                "T": n,
                "replicates": len(group),
                "candidate_found": len(found),
                "regular_facets": len(regular),
                "regular_mismatches": mismatches,
                "candidate_rate": len(found) / len(group),
                "regular_rate_given_candidate": len(regular) / max(1, len(found)),
                "mismatch_rate_given_regular": mismatches / max(1, len(regular)),
                "unconditional_regular_mismatch_rate": unconditional / len(group),
                "no_clipping_mismatches": sum(
                    bool(record["no_clipping_mismatch"]) for record in regular
                ),
                "mean_tau_fraction_given_regular": sum(
                    float(record["tau_fraction"]) for record in regular
                ) / max(1, len(regular)),
                "mean_x0_fraction_given_regular": sum(
                    float(record["x0_fraction"]) for record in regular
                ) / max(1, len(regular)),
                "mean_x1_fraction_given_regular": sum(
                    float(record["x1_fraction"]) for record in regular
                ) / max(1, len(regular)),
            }
        )
    return summaries


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = [run_one(n, replicate) for n in TOKENS for replicate in range(REPLICATES)]
    grouped = summarize(records)
    config = {
        "E": E,
        "K": K,
        "T": TOKENS,
        "replicates_per_T": REPLICATES,
        "affinity_grid_denominator": GRID,
        "capacity_rule": "(T/4, 3T/4, T/2, T/2)",
        "epsilon_rule": "T^(-1/2), checked by integer squaring",
        "seed_rule": "20261017 + 10000*T + replicate_index",
        "admission": "A_e=min(R_e,C_e)",
    }
    summary = {"protocol": config, "by_T": grouped}
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows_path = OUT / "replicates.csv"
    with rows_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    digest = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    print(json.dumps({"summary": str(summary_path), "replicates": str(rows_path), "sha256": digest, "by_T": grouped}, indent=2))


if __name__ == "__main__":
    main()
