"""Exact E=4 Top-1 witness for admitted-field non-cyclic-monotonicity."""

from __future__ import annotations

import json
from fractions import Fraction as F


AFFINITIES = (
    (F(157, 125), F(191, 100), F(7617, 1000), F(1657, 500)),
    (F(13, 50), F(3131, 500), F(3273, 500), F(6587, 1000)),
    (F(4253, 1000), F(3437, 500), F(6103, 1000), F(487, 500)),
    (F(1533, 500), F(377, 125), F(1373, 1000), F(7297, 1000)),
)
# Quotient coordinates (x1,x2,x3) represent q=(x1,x2,x3,0).
POINTS = (
    (F(-2501, 1000), F(-3043, 1000), F(-1579, 500)),
    (F(133, 40), F(457, 1000), F(-97, 125)),
    (F(-79, 200), F(347, 200), F(-3657, 1000)),
    (F(-533, 500), F(417, 250), F(1097, 500)),
    (F(-517, 1000), F(33, 25), F(3853, 1000)),
)
E, K, BASE_T = 4, 1, len(AFFINITIES)


def p0(values: tuple[F, ...]) -> tuple[F, ...]:
    mean = sum(values, F(0)) / len(values)
    return tuple(value - mean for value in values)


def cyclic_sum(fields: tuple[tuple[F, ...], ...]) -> F:
    total = F(0)
    for i, point in enumerate(POINTS):
        nxt = POINTS[(i + 1) % len(POINTS)]
        total += sum(fields[i][j] * (nxt[j] - point[j]) for j in range(E - 1))
    return total


def audit(replicas: int):
    total_tokens = BASE_T * replicas
    capacities = (replicas,) * E
    affinity_batch = AFFINITIES * replicas
    rows, requested_fields, admitted_fields = [], [], []
    min_margin = None
    for point in POINTS:
        q = (*point, F(0))
        requested = [0] * E
        margins, routes = [], []
        for affinity in affinity_batch:
            scores = tuple(affinity[e] - q[e] for e in range(E))
            ranking = sorted(scores, reverse=True)
            margin = ranking[0] - ranking[1]
            assert margin > 0, "Every Top-1 choice must be strict."
            margins.append(margin)
            winner = scores.index(ranking[0])
            routes.append(winner)
            requested[winner] += 1
        admitted = tuple(min(requested[e], capacities[e]) for e in range(E))
        assert sum(requested) == K * total_tokens
        min_margin = min(margins) if min_margin is None else min(min_margin, *margins)

        def field(load):
            centered = p0(tuple(F(total_tokens, E) - load[e] for e in range(E)))
            return centered[: E - 1]

        requested_tuple = tuple(requested)
        requested_fields.append(field(requested_tuple))
        admitted_fields.append(field(admitted))
        shift = -min(*point, F(0))
        rows.append({
            "quotient_point": [str(value) for value in point],
            "min_zero_pressure_representative": [str(value + shift) for value in point] + [str(shift)],
            "routes_zero_based": routes,
            "requested": list(requested_tuple),
            "admitted": list(admitted),
            "requested_field": [str(value) for value in field(requested_tuple)],
            "admitted_field": [str(value) for value in field(admitted)],
            "minimum_top1_margin": str(min(margins)),
        })
    req_sum = cyclic_sum(tuple(requested_fields))
    adm_sum = cyclic_sum(tuple(admitted_fields))
    assert sum(capacities) == K * total_tokens
    assert min_margin == F(113, 1000)
    assert req_sum < 0 and adm_sum == F(733 * replicas, 2000)
    return {
        "replicas": replicas,
        "T": total_tokens,
        "capacity": list(capacities),
        "capacity_sum_equals_KT": True,
        "minimum_top1_margin": str(min_margin),
        "entrywise_affinity_perturbation_radius_preserving_routes": str(min_margin / 2),
        "requested_cycle_sum": str(req_sum),
        "admitted_cycle_sum": str(adm_sum),
        "admitted_cycle_sum_per_token": str(adm_sum / total_tokens),
        "points": rows if replicas == 1 else "same five route patterns scaled by replicas",
    }


def main() -> None:
    audits = [audit(m) for m in (1, 2, 5)]
    print(json.dumps({
        "status": "PASS",
        "scope": "E=4 fixed Top-1 affinity family; exact rational audit",
        "E": E, "K": K,
        "mu": ["1/4"] * E,
        "affinities": [[str(value) for value in row] for row in AFFINITIES],
        "replica_audits": audits,
        "conclusion": "The admitted field violates cyclic monotonicity for the base plant and every exact replica; the normalized circulation is 733/8000 per token.",
    }, indent=2))


if __name__ == "__main__":
    main()
