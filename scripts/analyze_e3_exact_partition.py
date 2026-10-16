"""Exhaustively enumerate the E=3 score arrangement and its costs.

The open 2-D cells are enumerated by checking all 3^4 winner assignments
with a strict-margin linear program. Every score-equality line is then
partitioned at all intersections; one point per open line segment and every
vertex captures lower-dimensional tie strata under the router's lower-index
tie rule. This is a reproducibility aid for the finite case analysis, not a
replacement for writing that case analysis in a theorem proof.

Requires the optional research dependency SciPy.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from moe_control.research.e3_instance import (  # noqa: E402
    C,
    C_SINK,
    E_S,
    M_LOW,
    M_MARGIN,
    admitted_and_cost,
    score_cells,
)


def score_affines():
    """For each token type, return score intercepts and (x,y) slopes."""
    slopes = [(-1.0, 0.0), (0.0, -1.0), (0.0, 0.0)]
    return [
        ([M_LOW, -M_MARGIN, 0.0], slopes),
        ([M_MARGIN, -M_MARGIN, 0.0], slopes),
        ([-M_MARGIN, M_LOW, 0.0], slopes),
        ([-M_MARGIN, M_MARGIN, 0.0], slopes),
    ]


def open_cell_witnesses():
    """Return a strict-interior point for every nonempty full-dimensional cell."""
    affine = score_affines()
    witnesses = {}
    for winners in itertools.product(range(3), repeat=4):
        rows, rhs = [], []
        for (intercepts, slopes), winner in zip(affine, winners):
            for other in range(3):
                if other == winner:
                    continue
                # score[winner] - score[other] >= margin > 0
                rows.append([
                    slopes[other][0] - slopes[winner][0],
                    slopes[other][1] - slopes[winner][1],
                    1.0,
                ])
                rhs.append(intercepts[winner] - intercepts[other])
        result = linprog(
            [0.0, 0.0, -1.0],
            A_ub=np.asarray(rows),
            b_ub=np.asarray(rhs),
            bounds=[(-100.0, 100.0), (-100.0, 100.0), (0.0, None)],
            method="highs",
        )
        if result.success and result.x[2] > 1e-8:
            witnesses[winners] = tuple(float(v) for v in result.x[:2])
    return witnesses


def equality_lines():
    """Return unique lines a*x+b*y=c at which any pair of token scores tie."""
    lines = set()
    for intercepts, slopes in score_affines():
        for i, j in itertools.combinations(range(3), 2):
            a = slopes[i][0] - slopes[j][0]
            b = slopes[i][1] - slopes[j][1]
            c = intercepts[j] - intercepts[i]
            if a < 0 or (a == 0 and b < 0):
                a, b, c = -a, -b, -c
            lines.add((a, b, c))
    return sorted(lines)


def boundary_witnesses():
    """Sample every vertex and every open 1-D stratum in the line arrangement."""
    lines = equality_lines()
    vertices = []
    for line1, line2 in itertools.combinations(lines, 2):
        a = np.asarray([line1[:2], line2[:2]], dtype=float)
        if abs(float(np.linalg.det(a))) <= 1e-12:
            continue
        b = np.asarray([line1[2], line2[2]], dtype=float)
        point = np.linalg.solve(a, b)
        vertices.append(point)

    points = [tuple(map(float, p)) for p in vertices]
    for a, b, c in lines:
        norm2 = float(a * a + b * b)
        p0 = np.asarray([a * c / norm2, b * c / norm2], dtype=float)
        direction = np.asarray([-b, a], dtype=float)
        ts = sorted({
            round(float(np.dot(point - p0, direction) / np.dot(direction, direction)), 10)
            for point in vertices
            if abs(a * point[0] + b * point[1] - c) <= 1e-8
        })
        if not ts:
            intervals = [(-1.0, 1.0)]
        else:
            intervals = [(ts[0] - 1.0, ts[0])]
            intervals.extend(zip(ts, ts[1:]))
            intervals.append((ts[-1], ts[-1] + 1.0))
        for left, right in intervals:
            t = (left + right) / 2.0
            point = p0 + t * direction
            points.append(tuple(map(float, point)))
    return points


def main():
    points = list(open_cell_witnesses().values()) + boundary_witnesses()
    cells = {}
    for x, y in points:
        pattern = score_cells(x, y)
        a1, c1, a2, c2 = admitted_and_cost(x, y)
        signature = (
            tuple(pattern),
            int(round(c1)),
            int(round(c2)),
            tuple(int(round(v)) for v in a1),
            tuple(int(round(v)) for v in a2),
        )
        cells[signature] = (x, y)

    if len(cells) != 13:
        raise RuntimeError(f"expected 13 exact signatures for this instance; found {len(cells)}")
    for (pattern, c1, c2, a1, a2), witness in sorted(cells.items()):
        informative = a1 != a2
        if (c1 + c2) / 2 < E_S - 1e-9:
            raise AssertionError(f"cost-information bound failed in cell {pattern}")
        if not informative and (c1 != c2 or c1 < E_S - 1e-9):
            raise AssertionError(f"uninformative-cell property failed in {pattern}")
        if informative and max(c1, c2) < 2 * E_S - 1e-9:
            raise AssertionError(f"informative-cell property failed in {pattern}")
        print(
            f"pattern={pattern} costs=({c1},{c2}) informative={informative} "
            f"A1={a1} A2={a2} witness=({witness[0]:.6g},{witness[1]:.6g})"
        )

    # Check the continuous-pressure witness paths used in the companion note.
    gamma, eta, B = 1.0, 0.1, 2.65
    step_limit = eta * gamma * B

    def pressure_distance(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]
        qform = dx * dx - dx * dy + dy * dy
        return float(np.sqrt(2.0 * qform / (3.0 * gamma**2)))

    requested = [
        (0.0, 0.0),
        (1.01 / 3.0, 0.505 / 3.0),
        (2.0 * 1.01 / 3.0, 2.0 * 0.505 / 3.0),
        (1.01, 0.505),
    ]
    admitted_common = [
        (0.0, 0.0),
        (1.01 / 3.0, 0.3),
        (2.0 * 1.01 / 3.0, 0.6),
        (1.01, 0.9),
    ]
    admitted_world2 = (0.99, 1.01)
    if max(pressure_distance(a, b) for a, b in zip(requested, requested[1:])) > step_limit:
        raise AssertionError("requested witness path violates Reach")
    if max(pressure_distance(a, b) for a, b in zip(admitted_common, admitted_common[1:])) > step_limit:
        raise AssertionError("admitted common path violates Reach")
    if pressure_distance(admitted_common[-1], admitted_world2) > step_limit:
        raise AssertionError("admitted world-2 branch violates Reach")

    requested_costs_world1 = [admitted_and_cost(*p)[1] for p in requested]
    if requested_costs_world1 != [E_S, E_S, E_S, 0.0]:
        raise AssertionError(f"unexpected requested witness costs: {requested_costs_world1}")
    admitted_prebranch = [admitted_and_cost(*p) for p in admitted_common]
    expected_admitted_costs = [(c1 + c2) / 2 for _, c1, _, c2 in admitted_prebranch]
    if expected_admitted_costs != [E_S, E_S, E_S, E_S]:
        raise AssertionError(f"unexpected admitted common costs: {expected_admitted_costs}")
    if admitted_and_cost(*admitted_common[-1])[1] != 0.0:
        raise AssertionError("world-1 branch endpoint must have zero overflow")
    if admitted_and_cost(*admitted_world2)[3] != 0.0:
        raise AssertionError("world-2 branch endpoint must have zero overflow")
    print("Requested witness: 3 feasible updates; costs (world 1) = [20, 20, 20, 0]")
    print("Admitted witness: 3 common updates + 1 feasible branch; expected 5-round total = 80")
    print(f"Enumerated arrangement signatures: {len(cells)}")
    print(f"Minimum equal-prior expected overflow: {min((k[1] + k[2]) / 2 for k in cells):g}")


if __name__ == "__main__":
    main()
