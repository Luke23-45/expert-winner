"""Exact audit of a Top-1 admitted-feedback cyclic-monotonicity violation."""

from __future__ import annotations

import json
from fractions import Fraction as F


AFFINITIES = (
    (F(1, 2), F(43, 50), F(371, 100)),
    (F(381, 100), F(11, 10), F(172, 25)),
    (F(191, 100), F(189, 25), F(27, 4)),
)
# Quotient-chart coordinates (x, y) represent q=(x, y, 0).
POINTS = ((-3, -1), (-2, -2), (3, 1), (-3, 4))
E, K, BASE_T = 3, 1, len(AFFINITIES)
GAMMA = F(1)
MU = (F(1, 3),) * E


def p0(vector: tuple[F, ...]) -> tuple[F, ...]:
    mean = sum(vector, F(0)) / len(vector)
    return tuple(value - mean for value in vector)


def route_and_admit(x: int, y: int, affinity_batch, capacity):
    q = (F(x), F(y), F(0))
    requested = [0] * E
    minimum_margin = None
    routes = []
    for affinity in affinity_batch:
        scores = tuple(affinity[e] - GAMMA * q[e] for e in range(E))
        ranking = sorted(scores, reverse=True)
        margin = ranking[0] - ranking[1]
        assert margin > 0, "Every Top-1 choice must be strict."
        minimum_margin = margin if minimum_margin is None else min(minimum_margin, margin)
        winner = scores.index(ranking[0])
        routes.append(winner)
        requested[winner] += 1
    admitted = tuple(min(requested[e], capacity[e]) for e in range(E))
    return tuple(requested), admitted, minimum_margin, tuple(routes)


def quotient_field(load: tuple[int, ...], total_tokens: int) -> tuple[F, F]:
    target_mass = tuple(F(K * total_tokens) * MU[e] for e in range(E))
    centered = p0(tuple(target_mass[e] - load[e] for e in range(E)))
    # P0's first two coordinates are the covector in the (q1-q3,q2-q3) chart.
    return centered[0], centered[1]


def cyclic_sum(fields: tuple[tuple[F, F], ...]) -> F:
    total = F(0)
    for i, (x, y) in enumerate(POINTS):
        x_next, y_next = POINTS[(i + 1) % len(POINTS)]
        total += fields[i][0] * (x_next - x) + fields[i][1] * (y_next - y)
    return total


def main() -> None:
    assert E == 3 and K == 1 and BASE_T == 3
    audits = []
    for replicas in (1, 2, 3, 10):
        total_tokens = BASE_T * replicas
        capacity = (replicas,) * E
        affinity_batch = AFFINITIES * replicas
        assert sum(capacity) == K * total_tokens
        rows, requested_fields, admitted_fields = [], [], []
        min_margin = None
        for x, y in POINTS:
            requested, admitted, margin, routes = route_and_admit(
                x, y, affinity_batch, capacity
            )
            assert sum(requested) == K * total_tokens
            assert admitted == tuple(min(requested[e], capacity[e]) for e in range(E))
            shift = -min(x, y, 0)
            rows.append({
                "quotient_point": [x, y],
                "min_zero_pressure_representative": [x + shift, y + shift, shift],
                "routes_zero_based": list(routes),
                "requested": list(requested),
                "admitted": list(admitted),
                "requested_field": [str(v) for v in quotient_field(requested, total_tokens)],
                "admitted_field": [str(v) for v in quotient_field(admitted, total_tokens)],
                "minimum_top1_margin": str(margin),
            })
            requested_fields.append(quotient_field(requested, total_tokens))
            admitted_fields.append(quotient_field(admitted, total_tokens))
            min_margin = margin if min_margin is None else min(min_margin, margin)

        requested_cycle = cyclic_sum(tuple(requested_fields))
        admitted_cycle = cyclic_sum(tuple(admitted_fields))
        assert min_margin == F(7, 100)
        assert requested_cycle == -2 * replicas
        assert admitted_cycle == F(2 * replicas, 3) and admitted_cycle > 0
        audits.append({
            "replicas": replicas,
            "T": total_tokens,
            "capacity": list(capacity),
            "capacity_sum_equals_KT": True,
            "minimum_top1_margin_over_cycle": str(min_margin),
            "entrywise_affinity_perturbation_radius_preserving_routes": str(min_margin / 2),
            "points": rows if replicas == 1 else "same four route patterns scaled by replicas",
            "requested_cycle_sum": str(requested_cycle),
            "admitted_cycle_sum": str(admitted_cycle),
            "admitted_cycle_sum_per_token": str(admitted_cycle / total_tokens),
        })
    result = {
        "status": "PASS",
        "scope": "replicated fixed Top-1 affinity family; exact rational audit",
        "E": E, "K": K, "gamma": str(GAMMA),
        "mu": [str(v) for v in MU],
        "affinities": [[str(v) for v in row] for row in AFFINITIES],
        "replica_audits": audits,
        "conclusion": "For each audited replica count, the admitted field violates cyclic monotonicity. Exact replication gives admitted circulation 2m/3 for every positive integer m, normalized to 2/9 per token.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
