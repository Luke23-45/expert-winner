#!/usr/bin/env python3
"""Finite-size exact-grid audit of uniform-capacity random Top-K facets."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "uniform_capacity_random_facets"
E = 4
K = 2
GRID = 1 << 30
T_REPLICATES = ((256, 400), (4096, 200), (65536, 80), (1048576, 20))


def route_masks(scores: np.ndarray) -> np.ndarray:
    order = np.argsort(-scores, axis=1, kind="stable")[:, :K]
    mask = np.zeros(scores.shape, dtype=np.bool_)
    np.put_along_axis(mask, order, True, axis=1)
    return mask


def first_margin_pair(counts: np.ndarray, capacity: int, margin: int) -> tuple[int, int] | None:
    over = [i for i in range(E) if counts[i] - capacity >= margin]
    under = [j for j in range(E) if counts[j] - capacity <= -margin]
    for i in over:
        for j in under:
            if i != j:
                return i, j
    return None


def no_filler_pair_ties(scores: np.ndarray, candidate: int) -> bool:
    fillers = np.arange(scores.shape[0]) != candidate
    for e in range(E):
        for f in range(e + 1, E):
            if np.any(scores[fillers, e] == scores[fillers, f]):
                return False
    return True


def one_plant(t: int, replicate: int) -> dict[str, int | float | bool]:
    seed = 20261017 + 1000 * t + replicate
    rng = np.random.default_rng(seed)
    affinities = rng.integers(0, GRID + 1, size=(t, E), dtype=np.int64)
    base_mask = route_masks(affinities)
    base_counts = base_mask.sum(axis=0, dtype=np.int64)
    capacity = K * t // E
    margin = math.ceil(t ** (1.0 / 3.0))
    pair = first_margin_pair(base_counts, capacity, margin)

    result: dict[str, int | float | bool] = {
        "T": t,
        "replicate": replicate,
        "seed": seed,
        "capacity": capacity,
        "margin": margin,
        "has_over_under_pair": pair is not None,
        "source": -1 if pair is None else pair[0],
        "destination": -1 if pair is None else pair[1],
        "candidate_facets": 0,
        "regular_facets": 0,
        "mismatched_facets": 0,
        "construction_good_facets": 0,
        "no_clip_mismatches": 0,
        "max_candidate_displacement": 0.0,
        "max_changed_filler_rows": 0,
    }
    if pair is None:
        return result

    i, j = pair
    ui = affinities[:, i]
    uj = affinities[:, j]
    midpoint_sum = ui + uj
    difference = ui - uj
    # Exact integer-grid tests for 5/12 <= M <= 7/12 and 0 < D <= T^(-3/4).
    epsilon_units = math.floor((t ** (-0.75)) * GRID)
    in_midpoint_window = (5 * GRID <= 6 * midpoint_sum) & (6 * midpoint_sum <= 7 * GRID)
    in_displacement_window = (difference > 0) & (difference <= epsilon_units)
    other_experts = [e for e in range(E) if e not in (i, j)]
    other_values = affinities[:, other_experts]
    above = (2 * other_values > midpoint_sum[:, None]).sum(axis=1)
    midpoint_tie = (2 * other_values == midpoint_sum[:, None]).any(axis=1)
    candidates = np.flatnonzero(in_midpoint_window & in_displacement_window & (above == K - 1) & ~midpoint_tie)
    result["candidate_facets"] = int(candidates.size)
    seen_differences: set[int] = set()

    for candidate_np in candidates:
        candidate = int(candidate_np)
        d = int(difference[candidate])
        if d in seen_differences:
            # A repeated pairwise offset is a coincident facet, so do not
            # count it twice in this discrete-grid approximation.
            continue
        seen_differences.add(d)

        # Scores are represented in units of 1/(2*GRID) at q_i=D/2,
        # q_j=-D/2, gamma=1. The candidate's i/j scores tie exactly.
        facet_scores = 2 * affinities.copy()
        facet_scores[:, i] -= d
        facet_scores[:, j] += d
        if facet_scores[candidate, i] != facet_scores[candidate, j]:
            raise AssertionError("constructed candidate is not an exact facet")
        if np.count_nonzero(facet_scores[candidate] > facet_scores[candidate, i]) != K - 1:
            raise AssertionError("candidate tie is not at the Top-K boundary")
        candidate_ties = [
            (e, f)
            for e in range(E)
            for f in range(e + 1, E)
            if facet_scores[candidate, e] == facet_scores[candidate, f]
        ]
        if candidate_ties != [(min(i, j), max(i, j))]:
            continue
        if not no_filler_pair_ties(facet_scores, candidate):
            continue

        result["regular_facets"] = int(result["regular_facets"]) + 1
        facet_mask = route_masks(facet_scores)
        fillers = np.arange(t) != candidate
        filler_counts = facet_mask[fillers].sum(axis=0, dtype=np.int64)
        source_admitted_change = int(filler_counts[i] < capacity)
        destination_admitted_change = int(filler_counts[j] < capacity)
        mismatch = source_admitted_change != destination_admitted_change
        result["mismatched_facets"] = int(result["mismatched_facets"]) + int(mismatch)
        changed = np.any(facet_mask[fillers] != base_mask[fillers], axis=1)
        changed_rows = int(changed.sum())
        result["max_changed_filler_rows"] = max(int(result["max_changed_filler_rows"]), changed_rows)
        result["max_candidate_displacement"] = max(float(result["max_candidate_displacement"]), d / GRID)

        baseline_source = int(base_counts[i])
        baseline_destination = int(base_counts[j])
        has_robust_margins = (
            baseline_source >= capacity + margin
            and baseline_destination <= capacity - margin
        )
        candidate_minus_matches_baseline = bool(base_mask[candidate, i] and not base_mask[candidate, j])
        changed_bound = changed_rows <= t ** (1.0 / 3.0) / 2.0
        construction_good = (
            has_robust_margins
            and candidate_minus_matches_baseline
            and changed_bound
            and source_admitted_change == 0
            and destination_admitted_change == 1
        )
        result["construction_good_facets"] = int(result["construction_good_facets"]) + int(construction_good)

        # With C_e=T, every filler request is admitted, so the two changes match.
        no_clip_source = int(filler_counts[i] < t)
        no_clip_destination = int(filler_counts[j] < t)
        result["no_clip_mismatches"] = int(result["no_clip_mismatches"]) + int(no_clip_source != no_clip_destination)

    if int(result["no_clip_mismatches"]) != 0:
        raise AssertionError("no-clipping negative control produced a mismatch")
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, int | float | bool]] = []
    for t, replicates in T_REPLICATES:
        for replicate in range(replicates):
            rows.append(one_plant(t, replicate))

    aggregate = []
    for t, replicates in T_REPLICATES:
        subset = [row for row in rows if row["T"] == t]
        aggregate.append({
            "T": t,
            "replicates": replicates,
            "plants_with_over_under_pair": sum(bool(r["has_over_under_pair"]) for r in subset),
            "candidate_facets": sum(int(r["candidate_facets"]) for r in subset),
            "regular_facets": sum(int(r["regular_facets"]) for r in subset),
            "mismatched_facets": sum(int(r["mismatched_facets"]) for r in subset),
            "construction_good_facets": sum(int(r["construction_good_facets"]) for r in subset),
            "plants_with_at_least_one_good_facet": sum(int(r["construction_good_facets"]) > 0 for r in subset),
            "no_clip_mismatches": sum(int(r["no_clip_mismatches"]) for r in subset),
        })

    csv_path = OUT / "replicates.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    payload: dict[str, object] = {
        "experiment": "uniform_exact_total_unconditioned_random_facets",
        "model": {"E": E, "K": K, "capacity": "C=K*T/E", "affinity_grid_denominator": GRID,
                  "candidate_epsilon": "T^(-3/4)", "margin": "ceil(T^(1/3))", "seed_rule": "20261017+1000*T+replicate"},
        "cells": aggregate,
        "replicates": rows,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    payload["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"cells": aggregate, "result_sha256": payload["result_sha256"]}, indent=2, sort_keys=True))
    print(f"csv={csv_path}")
    print(f"summary={summary_path}")


if __name__ == "__main__":
    main()
