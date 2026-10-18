"""Exact local rectangle audit for the Top-1 admission-facet obstruction."""

from __future__ import annotations

import json
from fractions import Fraction as F

from audit_admitted_noncyclicity import AFFINITIES, p0


CAPACITY = (1, 1, 1)
POINTS = ((F(0), F(4, 5)), (F(1, 10), F(4, 5)),
          (F(1, 10), F(41, 50)), (F(0), F(41, 50)))
E, K, T = 3, 1, 3


def observe(point):
    x, y = point
    q = (x, y, F(0))
    requested = [0] * E
    routes, margins = [], []
    for affinity in AFFINITIES:
        scores = tuple(affinity[e] - q[e] for e in range(E))
        ranking = sorted(scores, reverse=True)
        margin = ranking[0] - ranking[1]
        assert margin > 0
        margins.append(margin)
        winner = scores.index(ranking[0])
        routes.append(winner + 1)
        requested[winner] += 1
    admitted = tuple(min(requested[e], CAPACITY[e]) for e in range(E))
    centered = p0(tuple(F(K * T, E) - admitted[e] for e in range(E)))
    return {
        "point": [str(value) for value in point],
        "routes_one_based": routes,
        "requested": requested,
        "admitted": list(admitted),
        "admitted_field_chart": [str(centered[0]), str(centered[1])],
        "minimum_top1_margin": str(min(margins)),
    }


def main() -> None:
    observations = [observe(point) for point in POINTS]
    fields = [tuple(F(v) for v in row["admitted_field_chart"]) for row in observations]
    circulation = F(0)
    for i, (x, y) in enumerate(POINTS):
        x_next, y_next = POINTS[(i + 1) % len(POINTS)]
        circulation += fields[i][0] * (x_next - x) + fields[i][1] * (y_next - y)

    # The sole regular-facet switch is token 3: expert 2 -> expert 3.
    delta_g = (fields[2][0] - fields[0][0], fields[2][1] - fields[0][1])
    normal = (F(0), F(1))  # quotient normal e_2-e_3
    determinant = normal[0] * delta_g[1] - normal[1] * delta_g[0]
    alpha, beta = 1, 0  # source admission changes; already-full destination does not
    assert [row["requested"] for row in observations] == [
        [0, 1, 2], [0, 1, 2], [0, 0, 3], [0, 0, 3]
    ]
    assert [row["admitted"] for row in observations] == [
        [0, 1, 1], [0, 1, 1], [0, 0, 1], [0, 0, 1]
    ]
    assert min(F(row["minimum_top1_margin"]) for row in observations) == F(1, 100)
    assert delta_g == (F(-1, 3), F(2, 3))
    assert determinant == F(1, 3)
    assert circulation == F(1, 50) and circulation > 0

    print(json.dumps({
        "status": "PASS",
        "scope": "one regular Top-1 facet and a strict four-point rectangle",
        "capacity_sum_equals_KT": sum(CAPACITY) == K * T,
        "facet": {
            "tie_equation": "q2-q3 = 81/100",
            "token_one_based": 3,
            "switch": "expert 2 -> expert 3",
            "source_count_at_capacity": True,
            "destination_already_at_capacity": True,
            "alpha_source_admission_changes": alpha,
            "beta_destination_admission_changes": beta,
            "quotient_normal": [str(v) for v in normal],
            "admitted_field_jump": [str(v) for v in delta_g],
            "normal_jump_determinant": str(determinant),
        },
        "rectangle": observations,
        "minimum_strict_routing_margin": "1/100",
        "admitted_field_cyclic_sum": str(circulation),
        "conclusion": "The mismatched clipping transition creates a tangential field jump and a positive local cyclic sum.",
    }, indent=2))


if __name__ == "__main__":
    main()
