#!/usr/bin/env python3
"""Exactly enumerate complete E=3, Top-1 score arrangements and audit clipping facets.

All routing, intersections, perturbations, and admission arithmetic use Fraction.
This is a finite structural audit, not an estimate of real-router prevalence.
"""

from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path


E = 3
TOKENS = 6
SEEDS = tuple(range(40))
CAPACITY_PROFILES = {
    "no_clipping": (6, 6, 6),
    "uniform_exact_total": (2, 2, 2),
    "heterogeneous_exact_total": (1, 2, 3),
}


@dataclass(frozen=True, order=True)
class TieLine:
    i: int
    j: int
    offset: F  # q_i - q_j = a_i - a_j


NORMAL_2D = {
    (0, 1): (F(1), F(-1)),
    (0, 2): (F(1), F(0)),
    (1, 2): (F(0), F(1)),
}


def plant(seed: int) -> tuple[tuple[F, ...], ...]:
    rng = random.Random(seed)
    denominator = 100_003
    return tuple(
        tuple(F(rng.randrange(-100_000, 100_001), denominator) for _ in range(E))
        for _ in range(TOKENS)
    )


def line_base_direction(line: TieLine) -> tuple[tuple[F, F], tuple[F, F]]:
    if (line.i, line.j) == (0, 1):
        return (line.offset, F(0)), (F(1), F(1))
    if (line.i, line.j) == (0, 2):
        return (line.offset, F(0)), (F(0), F(1))
    return (F(0), line.offset), (F(1), F(0))


def intersections_parameter(line: TieLine, other: TieLine) -> F | None:
    base, direction = line_base_direction(line)
    nx, ny = NORMAL_2D[(other.i, other.j)]
    denominator = nx * direction[0] + ny * direction[1]
    if denominator == 0:
        return None
    numerator = other.offset - nx * base[0] - ny * base[1]
    return numerator / denominator


def open_segment_samples(line: TieLine, lines: tuple[TieLine, ...]) -> list[tuple[F, F, F]]:
    base, direction = line_base_direction(line)
    events = sorted(
        {
            value
            for other in lines
            if other != line
            if (value := intersections_parameter(line, other)) is not None
        }
    )
    if not events:
        parameters = [F(0)]
    else:
        parameters = [events[0] - 1]
        parameters.extend((left + right) / 2 for left, right in zip(events, events[1:]))
        parameters.append(events[-1] + 1)
    points = []
    for parameter in parameters:
        x = base[0] + parameter * direction[0]
        y = base[1] + parameter * direction[1]
        points.append((x, y, F(0)))
    return points


def all_tie_lines(scores: tuple[tuple[F, ...], ...]) -> tuple[TieLine, ...]:
    lines = {
        TieLine(i, j, row[i] - row[j])
        for row in scores
        for i in range(E)
        for j in range(i + 1, E)
    }
    return tuple(sorted(lines))


def route_counts(
    scores: tuple[tuple[F, ...], ...], pressure: tuple[F, F, F]
) -> tuple[int, ...]:
    counts = [0] * E
    for row in scores:
        winner = min(range(E), key=lambda expert: (-(row[expert] - pressure[expert]), expert))
        counts[winner] += 1
    return tuple(counts)


def side_epsilon(
    scores: tuple[tuple[F, ...], ...], point: tuple[F, F, F], line: TieLine
) -> F:
    positive_margins: list[F] = []
    for row in scores:
        routed_scores = tuple(row[e] - point[e] for e in range(E))
        for i in range(E):
            for j in range(i + 1, E):
                margin = abs(routed_scores[i] - routed_scores[j])
                if margin:
                    positive_margins.append(margin)
    if not positive_margins:
        raise AssertionError("a regular segment unexpectedly has no nonzero score margin")
    return min(positive_margins) / 8


def p0(vector: tuple[int, ...]) -> tuple[F, ...]:
    mean = F(sum(vector), E)
    return tuple(F(value) - mean for value in vector)


def dot(left: tuple[F, ...], right: tuple[F, ...]) -> F:
    return sum((x * y for x, y in zip(left, right)), F(0))


def facet_transition(
    scores: tuple[tuple[F, ...], ...], line: TieLine, point: tuple[F, F, F]
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    eps = side_epsilon(scores, point, line)
    normal = [F(0)] * E
    normal[line.i] = F(1)
    normal[line.j] = F(-1)
    minus = tuple(point[e] - eps * normal[e] for e in range(E))
    plus = tuple(point[e] + eps * normal[e] for e in range(E))
    return route_counts(scores, minus), route_counts(scores, plus)


def profile_audit(
    scores: tuple[tuple[F, ...], ...], lines: tuple[TieLine, ...], capacities: tuple[int, ...]
) -> dict:
    regular = matched = mismatched = candidate_segments = 0
    max_tangent_sq = F(0)
    first_witness = None

    for line in lines:
        points = open_segment_samples(line, lines)
        candidate_segments += len(points)
        for point in points:
            r_minus, r_plus = facet_transition(scores, line, point)
            if r_minus == r_plus:
                continue
            direction = tuple(r_plus[e] - r_minus[e] for e in range(E))
            if any(direction[e] for e in range(E) if e not in (line.i, line.j)):
                raise AssertionError("a regular pair facet changed a third expert count")
            m = -direction[line.i]
            if m < 1 or direction[line.j] != m:
                raise AssertionError("route transition is not an oriented same-pair exchange")

            a_minus = tuple(min(r_minus[e], capacities[e]) for e in range(E))
            a_plus = tuple(min(r_plus[e], capacities[e]) for e in range(E))
            d_source = a_minus[line.i] - a_plus[line.i]
            d_destination = a_plus[line.j] - a_minus[line.j]
            if d_source < 0 or d_destination < 0:
                raise AssertionError("admitted transition has an invalid orientation")
            regular += 1
            jump = p0(tuple(a_minus[e] - a_plus[e] for e in range(E)))
            normal_q = p0(tuple(1 if e == line.i else -1 if e == line.j else 0 for e in range(E)))
            tangent = tuple(
                jump[e] - normal_q[e] * dot(jump, normal_q) / dot(normal_q, normal_q)
                for e in range(E)
            )
            tangent_sq = dot(tangent, tangent)
            if d_source == d_destination:
                matched += 1
                if tangent_sq != 0:
                    raise AssertionError("matched facet has nonzero tangential jump")
            else:
                mismatched += 1
                if tangent_sq == 0:
                    raise AssertionError("mismatched facet lacks tangential obstruction")
                max_tangent_sq = max(max_tangent_sq, tangent_sq)
                if first_witness is None:
                    first_witness = {
                        "pair_zero_based": [line.i, line.j],
                        "offset": str(line.offset),
                        "sample_point": [str(value) for value in point],
                        "R_minus": list(r_minus),
                        "R_plus": list(r_plus),
                        "A_minus": list(a_minus),
                        "A_plus": list(a_plus),
                        "d_source": d_source,
                        "d_destination": d_destination,
                        "tangential_jump_norm_squared": str(tangent_sq),
                    }

    if regular != matched + mismatched:
        raise AssertionError("facet accounting does not sum")
    return {
        "capacity": list(capacities),
        "candidate_open_segments": candidate_segments,
        "regular_routing_facets": regular,
        "matched_facets": matched,
        "mismatched_facets": mismatched,
        "mismatch_fraction": str(F(mismatched, regular)) if regular else None,
        "max_tangential_jump_norm_squared": str(max_tangent_sq),
        "first_mismatch_witness": first_witness,
    }


def run() -> dict:
    rows = []
    for seed in SEEDS:
        scores = plant(seed)
        lines = all_tie_lines(scores)
        per_profile = {
            name: profile_audit(scores, lines, capacities)
            for name, capacities in CAPACITY_PROFILES.items()
        }
        if per_profile["no_clipping"]["mismatched_facets"] != 0:
            raise AssertionError("no-clipping negative control failed")
        for name, result in per_profile.items():
            rows.append(
                {
                    "seed": seed,
                    "profile": name,
                    "distinct_tie_lines": len(lines),
                    **result,
                }
            )
    aggregates = {}
    for name in CAPACITY_PROFILES:
        selected = [row for row in rows if row["profile"] == name]
        regular = sum(row["regular_routing_facets"] for row in selected)
        mismatched = sum(row["mismatched_facets"] for row in selected)
        aggregates[name] = {
            "plants": len(selected),
            "regular_routing_facets_total": regular,
            "matched_facets_total": sum(row["matched_facets"] for row in selected),
            "mismatched_facets_total": mismatched,
            "pooled_mismatch_fraction": str(F(mismatched, regular)) if regular else None,
            "plants_with_any_mismatch": sum(row["mismatched_facets"] > 0 for row in selected),
        }
    return {
        "protocol": {
            "experts": E,
            "top_k": 1,
            "tokens": TOKENS,
            "seeds": list(SEEDS),
            "score_distribution": "independent integer numerator uniform [-100000,100000] over 100003",
            "arithmetic": "exact rational throughout",
            "arrangement_scope": "all distinct pairwise tie lines and every open segment",
            "tie_break": "lower expert index",
            "capacity_profiles": {name: list(value) for name, value in CAPACITY_PROFILES.items()},
            "profiles_are_paired_on_same_plant": True,
        },
        "exact_controls": {
            "no_clipping_has_zero_mismatches": all(
                row["mismatched_facets"] == 0 for row in rows if row["profile"] == "no_clipping"
            ),
            "all_mismatches_have_nonzero_tangent": True,
            "all_transitions_are_same_pair_exchanges": True,
            "all_facets_accounted": True,
        },
        "aggregate": aggregates,
        "per_seed": rows,
    }


def main() -> None:
    report = run()
    outdir = Path("results/full_arrangement_facets")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (outdir / "by_seed.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "seed", "profile", "distinct_tie_lines", "candidate_open_segments",
            "regular_routing_facets", "matched_facets", "mismatched_facets",
            "mismatch_fraction", "max_tangential_jump_norm_squared", "first_mismatch_witness",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in report["per_seed"]:
            writer.writerow({key: json.dumps(row[key]) if isinstance(row[key], (dict, list)) else row[key] for key in fields})
    print(json.dumps({"protocol": report["protocol"], "exact_controls": report["exact_controls"], "aggregate": report["aggregate"]}, indent=2))
    print(f"Artifacts written under {outdir.resolve()}")


if __name__ == "__main__":
    main()
