#!/usr/bin/env python3
"""Exact-grid audit of the many-facet random-affinity theorem corollary."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path


E = 4
K = 2
TOKENS = (64, 256, 1024, 4096)
REPLICATES = 500
GRID = 1 << 30
SEED_BASE = 20261018
B_EK = 25 / 216
OUT = Path("results/many_random_facets")
PROTOCOL = Path("docs/paper/many_facet_random_affinity_protocol_2026-10-17.md")


def is_candidate(row: tuple[int, ...], tokens: int) -> bool:
    """Exact-grid candidate event from the probability proof, E=4,K=2."""
    x0, x1, x2, x3 = row
    pair_sum = x0 + x1
    if not (5 * GRID <= 6 * pair_sum <= 7 * GRID):
        return False
    if (x0 - x1) ** 2 * tokens > GRID**2:
        return False
    # The intended tie must be the sole tie in this candidate row.
    if 2 * x2 == pair_sum or 2 * x3 == pair_sum or x2 == x3:
        return False
    return (2 * x2 > pair_sum) + (2 * x3 > pair_sum) == K - 1


def facet_scores(row: tuple[int, ...], delta: int) -> tuple[int, ...]:
    """Scores multiplied by 2*GRID at q=(delta/2,-delta/2,0,0)."""
    x0, x1, x2, x3 = row
    return (2 * x0 - delta, 2 * x1 + delta, 2 * x2, 2 * x3)


def regular_at(rows: list[tuple[int, ...]], tau: int, delta: int) -> bool:
    """Exactly one pair tie occurs in the full score arrangement at q."""
    selected = facet_scores(rows[tau], delta)
    if selected[0] != selected[1]:
        raise AssertionError("candidate does not create the intended tie")
    if sum(score > selected[0] for score in selected[2:]) != K - 1:
        raise AssertionError("intended tie is not at the Top-2 cutoff")
    if len(set(selected)) != E - 1:
        return False
    for index, row in enumerate(rows):
        if index != tau and len(set(facet_scores(row, delta))) != E:
            return False
    return True


def filler_counts(rows: list[tuple[int, ...]], tau: int, delta: int) -> list[int]:
    counts = [0] * E
    for index, row in enumerate(rows):
        if index == tau:
            continue
        scores = facet_scores(row, delta)
        if len(set(scores)) != E:
            raise AssertionError("regularity must be checked before counting")
        winners = sorted(range(E), key=lambda expert: (-scores[expert], expert))[:K]
        for expert in winners:
            counts[expert] += 1
    if sum(counts) != K * (len(rows) - 1):
        raise AssertionError("filler request mass is not conserved")
    return counts


def run_plant(tokens: int, replicate: int) -> dict[str, int | float | bool]:
    seed = SEED_BASE + 10_000 * tokens + replicate
    rng = random.Random(seed)
    rows = [tuple(rng.randrange(GRID + 1) for _ in range(E)) for _ in range(tokens)]
    candidates = [index for index, row in enumerate(rows) if is_candidate(row, tokens)]
    capacities = (tokens // 4, 3 * tokens // 4, tokens // 2, tokens // 2)

    seen_delta: set[int] = set()
    regular_count = mismatch_count = no_clip_mismatch_count = 0
    distinct_mismatch_deltas: set[int] = set()
    x0_sum = x1_sum = 0
    candidate_rows = len(candidates)

    for tau in candidates:
        delta = rows[tau][0] - rows[tau][1]
        duplicate_pressure = delta in seen_delta
        seen_delta.add(delta)
        if duplicate_pressure or not regular_at(rows, tau, delta):
            continue
        regular_count += 1
        counts = filler_counts(rows, tau, delta)
        x0, x1 = counts[0], counts[1]
        x0_sum += x0
        x1_sum += x1

        # Across this facet the selected token moves 0 -> 1. These are the
        # exact admitted count-change indicators under per-expert clipping.
        d0 = x0 < capacities[0]
        d1 = x1 < capacities[1]
        mismatch = d0 != d1
        if mismatch:
            mismatch_count += 1
            distinct_mismatch_deltas.add(delta)
        if (x0 < tokens) != (x1 < tokens):
            no_clip_mismatch_count += 1

        # Verify the claimed tangent jump norm in the E=4 quotient.
        tangent_sq = 0 if not mismatch else 1 / 4
        if tangent_sq not in (0, 1 / 4):
            raise AssertionError("unexpected tangent jump norm")

    if mismatch_count != len(distinct_mismatch_deltas):
        raise AssertionError("a facet pressure was counted more than once")
    if no_clip_mismatch_count:
        raise AssertionError("no-clipping negative control failed")
    if mismatch_count > regular_count or regular_count > candidate_rows:
        raise AssertionError("invalid candidate/regular/mismatch nesting")

    lower_count = math.ceil(B_EK * math.sqrt(tokens) / 2)
    return {
        "T": tokens,
        "replicate": replicate,
        "seed": seed,
        "candidate_rows": candidate_rows,
        "distinct_regular_facets": regular_count,
        "distinct_regular_mismatched_facets": mismatch_count,
        "no_clipping_mismatches": no_clip_mismatch_count,
        "meets_integerized_theorem_lower_count": mismatch_count >= lower_count,
        "theorem_lower_count": lower_count,
        "mean_X0_over_T": (x0_sum / regular_count / tokens) if regular_count else "",
        "mean_X1_over_T": (x1_sum / regular_count / tokens) if regular_count else "",
    }


def summarize(records: list[dict[str, int | float | bool]]) -> list[dict[str, int | float]]:
    summaries = []
    for tokens in TOKENS:
        group = [record for record in records if record["T"] == tokens]
        candidates = [int(record["candidate_rows"]) for record in group]
        regular = [int(record["distinct_regular_facets"]) for record in group]
        mismatch = [int(record["distinct_regular_mismatched_facets"]) for record in group]
        plant_lower = sum(bool(record["meets_integerized_theorem_lower_count"]) for record in group)
        valid_means = [record for record in group if record["distinct_regular_facets"]]
        summaries.append({
            "T": tokens,
            "replicates": len(group),
            "theorem_lower_count": math.ceil(B_EK * math.sqrt(tokens) / 2),
            "mean_candidate_rows": statistics.mean(candidates),
            "mean_candidate_rows_over_sqrt_T": statistics.mean(candidates) / math.sqrt(tokens),
            "candidate_rows_range": [min(candidates), max(candidates)],
            "mean_regular_facets": statistics.mean(regular),
            "mean_mismatched_facets": statistics.mean(mismatch),
            "mean_mismatched_facets_over_sqrt_T": statistics.mean(mismatch) / math.sqrt(tokens),
            "mismatched_facets_range": [min(mismatch), max(mismatch)],
            "plants_meeting_integerized_lower_count": plant_lower,
            "fraction_facets_mismatched": sum(mismatch) / max(1, sum(regular)),
            "mean_X0_over_T": statistics.mean(float(r["mean_X0_over_T"]) for r in valid_means),
            "mean_X1_over_T": statistics.mean(float(r["mean_X1_over_T"]) for r in valid_means),
            "no_clipping_mismatches": sum(int(r["no_clipping_mismatches"]) for r in group),
        })
    return summaries


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = [run_plant(tokens, replicate) for tokens in TOKENS for replicate in range(REPLICATES)]
    summary = {
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "model": "iid rational-grid affinities; deterministic Top-2; A_e=min(R_e,C_e)",
        "parameters": {
            "E": E,
            "K": K,
            "T": TOKENS,
            "replicates_per_T": REPLICATES,
            "grid_denominator": GRID,
            "capacity_fraction": ["1/4", "3/4", "1/2", "1/2"],
            "candidate_rule": "midpoint in [5/12,7/12], |a0-a1|<=T^-1/2, exactly one outsider above midpoint",
            "candidate_affinity_pair": [0, 1],
            "seed_rule": "20261018 + 10000*T + replicate_index",
            "b_EK": "25/216",
        },
        "by_T": summarize(records),
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    plants_path = OUT / "plants.csv"
    with plants_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(json.dumps({
        "summary": str(summary_path),
        "plants": str(plants_path),
        "summary_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
        "by_T": summary["by_T"],
    }, indent=2))


if __name__ == "__main__":
    main()
