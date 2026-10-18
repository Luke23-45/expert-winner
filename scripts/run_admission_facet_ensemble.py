#!/usr/bin/env python3
"""Exact synthetic audit of the admitted-field regular-facet criterion.

Run from the repository root:
    python scripts/run_admission_facet_ensemble.py

This is a controlled structural experiment, not a training or performance
study. Random integer-affinity Top-K plants are paired across capacity
profiles. Pressure candidates are sampled on exact score-tie hyperplanes;
all routing and admission calculations use fractions.
"""

from __future__ import annotations

import csv
import json
import random
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


E, K, T = 4, 2, 12
SEEDS = tuple(range(40))
PAIR_SAMPLES = 12
EPS = F(1, 1000)
OUT = Path("results/admission_facet_ensemble")
CAPACITIES = {
    "no_clipping": (T, T, T, T),
    "exact_total_uniform": (6, 6, 6, 6),
    "exact_total_heterogeneous": (2, 4, 8, 10),
    "aggregate_shortage": (3, 3, 3, 3),
}


def centered(v: tuple[F, ...]) -> tuple[F, ...]:
    mean = sum(v, F(0)) / len(v)
    return tuple(x - mean for x in v)


def scores(affinity: tuple[int, ...], q: tuple[F, ...]) -> tuple[F, ...]:
    return tuple(F(a) - x for a, x in zip(affinity, q))


def route_one(scores_: tuple[F, ...]) -> tuple[int, ...]:
    # Exact ties are broken by smaller expert index; sampled side points must
    # be strict, so this convention only makes the implementation total.
    return tuple(sorted(sorted(range(E), key=lambda e: (-scores_[e], e))[:K]))


def route_batch(affinities: tuple[tuple[int, ...], ...], q: tuple[F, ...]):
    return tuple(route_one(scores(row, q)) for row in affinities)


def counts(routes: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    out = [0] * E
    for selected in routes:
        for e in selected:
            out[e] += 1
    return tuple(out)


def admit(requested: tuple[int, ...], capacity: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(min(r, c) for r, c in zip(requested, capacity))


def field(admitted: tuple[int, ...]) -> tuple[F, ...]:
    # Uniform target; its constant term cancels in every field jump.
    return centered(tuple(F(K * T, E) - a for a in admitted))


def margin(affinities, q) -> F:
    """Minimum Top-K boundary margin across the batch at a strict point."""
    result = None
    for row in affinities:
        ordered = sorted(scores(row, q), reverse=True)
        value = ordered[K - 1] - ordered[K]
        if result is None or value < result:
            result = value
    return result if result is not None else F(0)


def segment_has_constant_routes(affinities, start, end, expected_routes) -> bool:
    """Certify routes on every open subinterval cut by pairwise score ties."""
    breaks = {F(0), F(1)}
    for row in affinities:
        start_scores = scores(row, start)
        end_scores = scores(row, end)
        for e in range(E):
            for f in range(e + 1, E):
                d0 = start_scores[e] - start_scores[f]
                d1 = end_scores[e] - end_scores[f]
                if d0 == d1:
                    continue
                t = -d0 / (d1 - d0)
                if 0 < t < 1:
                    breaks.add(t)
    ordered = sorted(breaks)
    for lo, hi in zip(ordered, ordered[1:]):
        t = (lo + hi) / 2
        point = tuple(x + t * (y - x) for x, y in zip(start, end))
        if route_batch(affinities, point) != expected_routes:
            return False
    return True


def make_candidate(rng, affinities, token, i, j):
    """Put token's i/j score tie on the boundary of its Top-K set."""
    q = [F(rng.randint(-5, 5), 7) for _ in range(E)]
    q[j] = F(0)
    q[i] = F(affinities[token][i] - affinities[token][j])
    return tuple(q)


def crossing_at(affinities, q, i, j):
    """Return a regular facet's simultaneous i->j route exchanges, or None."""
    active = False
    for row in affinities:
        s = scores(row, q)
        ordered = sorted(s, reverse=True)
        if ordered[K - 1] == ordered[K]:
            tie = ordered[K - 1]
            tied_at_cutoff = {e for e, value in enumerate(s) if value == tie}
            above = sum(value > tie for value in s)
            if tied_at_cutoff != {i, j} or above != K - 1:
                return None
            active = True
    if not active:
        return None
    q_minus, q_plus = list(q), list(q)
    q_minus[i] -= EPS / 2
    q_minus[j] += EPS / 2
    q_plus[i] += EPS / 2
    q_plus[j] -= EPS / 2
    r_minus = route_batch(affinities, tuple(q_minus))
    r_plus = route_batch(affinities, tuple(q_plus))
    moved = []
    for t, (before, after) in enumerate(zip(r_minus, r_plus)):
        if before == after:
            continue
        if len(before) != K or len(after) != K:
            return None
        if i not in before or j in before or j not in after or i in after:
            return None
        if set(before) - {i} != set(after) - {j}:
            return None
        tie = F(affinities[t][i]) - q[i]
        if tie != F(affinities[t][j]) - q[j]:
            return None
        # At the exact facet, the tied pair must straddle the Top-K boundary.
        at_facet = scores(affinities[t], q)
        above = sum(at_facet[e] > tie for e in range(E) if e not in (i, j))
        if above != K - 1:
            return None
        moved.append(t)
    if not moved:
        return None
    if margin(affinities, tuple(q_minus)) <= 0 or margin(affinities, tuple(q_plus)) <= 0:
        return None
    return tuple(moved), r_minus, r_plus, tuple(q_minus), tuple(q_plus)


def rectangle_circulation(affinities, capacity, q, i, j, q_minus, q_plus):
    """Find a strict local rectangle crossing only this facet; return its sum."""
    tangent = next(e for e in range(E) if e not in (i, j))
    n = EPS
    while n >= F(1, 10**12):
        h = n / 10
        vertices = []
        for side, tangential_sign in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            point = list(q)
            point[i] += side * n / 2
            point[j] -= side * n / 2
            point[tangent] += tangential_sign * h
            vertices.append(tuple(point))
        route_sets = [route_batch(affinities, p) for p in vertices]
        midpoints = []
        for tangent_sign in (-1, 1):
            point = list(q)
            point[tangent] += tangent_sign * h
            midpoints.append(tuple(point))
        minus_routes, plus_routes = route_sets[0], route_sets[1]
        locally_constant = (
            route_sets[0] == route_sets[3]
            and route_sets[1] == route_sets[2]
            and all(margin(affinities, p) > 0 for p in vertices)
            and segment_has_constant_routes(affinities, vertices[1], vertices[2], plus_routes)
            and segment_has_constant_routes(affinities, vertices[2], midpoints[1], plus_routes)
            and segment_has_constant_routes(affinities, midpoints[1], vertices[3], minus_routes)
            and segment_has_constant_routes(affinities, vertices[3], vertices[0], minus_routes)
            and segment_has_constant_routes(affinities, vertices[0], midpoints[0], minus_routes)
            and segment_has_constant_routes(affinities, midpoints[0], vertices[1], plus_routes)
        )
        if locally_constant:
            fs = [field(admit(counts(r), capacity)) for r in (minus_routes, plus_routes)]
            # Integrate the piecewise-constant field exactly. The two edges
            # normal to the facet split equally between both sides and cancel;
            # the two tangent edges contribute 2h times the tangential jump.
            total = 2 * h * (fs[1][tangent] - fs[0][tangent])
            if total:
                return total, h
        n /= 10
    return None, None


def one_seed(seed: int):
    rng = random.Random(seed)
    affinities = tuple(
        tuple(rng.randint(-4, 4) for _ in range(E)) for _ in range(T)
    )
    rows = []
    seen = set()
    for token in range(T):
        for i in range(E):
            for j in range(i + 1, E):
                for sample in range(PAIR_SAMPLES):
                    q = make_candidate(rng, affinities, token, i, j)
                    found = crossing_at(affinities, q, i, j)
                    if found is None:
                        continue
                    moved, r_minus, r_plus, q_minus, q_plus = found
                    # A sampled facet may be rediscovered from another token
                    # on a coincident hyperplane. Deduplicate exact geometry.
                    key = (i, j, q[i] - q[j], moved)
                    if key in seen:
                        continue
                    seen.add(key)
                    rm, rp = counts(r_minus), counts(r_plus)
                    m = len(moved)
                    assert tuple(rp[e] - rm[e] for e in range(E)) == tuple(
                        (-m if e == i else m if e == j else 0) for e in range(E)
                    )
                    for name, cap in CAPACITIES.items():
                        am, ap = admit(rm, cap), admit(rp, cap)
                        a = am[i] - ap[i]
                        b = ap[j] - am[j]
                        assert tuple(ap[e] - am[e] for e in range(E)) == tuple(
                            (-a if e == i else b if e == j else 0) for e in range(E)
                        )
                        g_jump = tuple(x - y for x, y in zip(field(ap), field(am)))
                        normal = centered(tuple(F(1 if e == i else -1 if e == j else 0) for e in range(E)))
                        if a == b:
                            assert g_jump == tuple(a * x for x in normal)
                            local_cycle = None
                        else:
                            # For E>=3, any coordinate outside {i,j} gives
                            # this exact nonzero tangential component.
                            k = next(e for e in range(E) if e not in (i, j))
                            assert g_jump[k] == F(b - a, E) and g_jump[k] != 0
                            local_cycle, h = rectangle_circulation(
                                affinities, cap, q, i, j, q_minus, q_plus
                            )
                            assert local_cycle is not None, (
                                f"no local rectangle found: seed={seed}, profile={name}, "
                                f"facet={(i, j, str(q[i] - q[j]))}, moved={moved}, "
                                f"a={a}, b={b}, jump={g_jump}, q={q}"
                            )
                        rows.append({
                            "seed": seed,
                            "capacity_profile": name,
                            "pair_i": i,
                            "pair_j": j,
                            "facet_offset": str(q[i] - q[j]),
                            "simultaneous_token_switches": m,
                            "source_admission_decrease": a,
                            "destination_admission_increase": b,
                            "matched_facet": a == b,
                            "field_jump_outside_pair": str(g_jump[next(e for e in range(E) if e not in (i, j))]),
                            "local_cycle_sum": "" if local_cycle is None else str(local_cycle),
                        })
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [row for seed in SEEDS for row in one_seed(seed)]
    with (OUT / "facet_observations.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {}
    for profile in CAPACITIES:
        subset = [r for r in rows if r["capacity_profile"] == profile]
        matched = sum(r["matched_facet"] for r in subset)
        mismatched = len(subset) - matched
        summary[profile] = {
            "facets": len(subset),
            "matched": matched,
            "mismatched": mismatched,
            "mismatch_fraction": None if not subset else mismatched / len(subset),
            "independent_plants_with_facet": len({r["seed"] for r in subset}),
            "mismatch_facets_with_nonzero_exact_local_cycle": sum(
                r["local_cycle_sum"] != "" for r in subset
            ),
            "capacity_vector": list(CAPACITIES[profile]),
        }
    totals = Counter()
    for row in rows:
        totals["facets"] += 1
        totals["matched"] += int(row["matched_facet"])
        totals["mismatched"] += int(not row["matched_facet"])
        totals["local_cycles"] += int(row["local_cycle_sum"] != "")
    output = {
        "design": {
            "experts": E, "top_k": K, "tokens": T,
            "seeds": list(SEEDS), "affinities": "iid integer Uniform[-4,4]",
            "candidate_pressure": "exact random rational points on sampled token-pair tie hyperplanes",
            "admission": "A_e=min(R_e,C_e)",
            "tie_rule": "lower expert index; side evaluations are strict",
            "scope": "exact finite structural audit; not model quality or production prevalence",
        },
        "totals": dict(totals),
        "by_capacity_profile": summary,
        "interpretation": (
            "Every sampled facet passed the exact jump formula. On E=4, a facet is "
            "potential-compatible exactly when aggregate admitted source decrease equals "
            "aggregate destination increase. The no-clipping arm is a negative control. "
            "Unsampled facets and untested router regimes are not covered."
        ),
    }
    (OUT / "summary.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
