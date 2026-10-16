"""Enumerate the E=3 score arrangement using rational arithmetic.

The four token types each have three affine expert scores in (x,y). Their
pairwise equalities form a finite line arrangement. A rational vertical-slab
decomposition visits every open 2-D cell; rational samples on every line
segment and at every vertex cover tie strata under the lower-index tie rule.
The output is a compact, reproducible finite-case certificate, not a
substitute for presenting the score inequalities in a paper proof.
"""
from __future__ import annotations

from fractions import Fraction as F
from itertools import combinations, product
from math import gcd, lcm
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from moe_control.research.e3_instance import (  # noqa: E402
    C,
    C_SINK,
    E_S,
    M_LOW,
    M_MARGIN,
)

# Each score is intercept + x_slope*x + y_slope*y.
SCORES = (
    ((F(M_LOW), -1, 0), (F(-M_MARGIN), 0, -1), (F(0), 0, 0)),
    ((F(M_MARGIN), -1, 0), (F(-M_MARGIN), 0, -1), (F(0), 0, 0)),
    ((F(-M_MARGIN), -1, 0), (F(M_LOW), 0, -1), (F(0), 0, 0)),
    ((F(-M_MARGIN), -1, 0), (F(M_MARGIN), 0, -1), (F(0), 0, 0)),
)
C_EXACT, E_S_EXACT, C_SINK_EXACT = F(C), F(E_S), F(C_SINK)
CAP = (C_EXACT, C_EXACT, C_SINK_EXACT)


def _canonical_line(a: F, b: F, c: F) -> tuple[int, int, int]:
    """Normalize a*x+b*y=c to a unique primitive integer triple."""
    denominator = lcm(a.denominator, b.denominator, c.denominator)
    ai, bi, ci = int(a * denominator), int(b * denominator), int(c * denominator)
    divisor = gcd(gcd(abs(ai), abs(bi)), abs(ci))
    ai, bi, ci = ai // divisor, bi // divisor, ci // divisor
    if ai < 0 or (ai == 0 and bi < 0):
        ai, bi, ci = -ai, -bi, -ci
    return ai, bi, ci


def equality_lines() -> tuple[tuple[int, int, int], ...]:
    lines = set()
    for scores in SCORES:
        for i, j in combinations(range(3), 2):
            ci, ai, bi = scores[i]
            cj, aj, bj = scores[j]
            lines.add(_canonical_line(ai - aj, bi - bj, cj - ci))
    return tuple(sorted(lines))


def intersections(lines):
    points = set()
    for (a1, b1, c1), (a2, b2, c2) in combinations(lines, 2):
        determinant = a1 * b2 - a2 * b1
        if determinant == 0:
            continue
        x = F(c1 * b2 - c2 * b1, determinant)
        y = F(a1 * c2 - a2 * c1, determinant)
        points.add((x, y))
    return points


def _interval_samples(values):
    values = sorted(set(values))
    if not values:
        return [F(0)]
    samples = [values[0] - 1]
    samples.extend((left + right) / 2 for left, right in zip(values, values[1:]))
    samples.append(values[-1] + 1)
    return samples


def open_2d_witnesses(lines, vertices):
    """Sample every full-dimensional arrangement cell by exact vertical slabs."""
    critical_x = {x for x, _ in vertices}
    critical_x.update(F(c, a) for a, b, c in lines if b == 0)
    x_samples = _interval_samples(critical_x)
    witnesses = set()
    for x in x_samples:
        y_breaks = [F(c - a * x, b) for a, b, c in lines if b != 0]
        witnesses.update((x, y) for y in _interval_samples(y_breaks))
    return witnesses


def boundary_witnesses(lines, vertices):
    """Sample every open line stratum and every arrangement vertex exactly."""
    points = set(vertices)
    for a, b, c in lines:
        norm2 = a * a + b * b
        p0 = (F(a * c, norm2), F(b * c, norm2))
        direction = (-b, a)
        ts = set()
        for x, y in vertices:
            if a * x + b * y == c:
                ts.add(F((x - p0[0]) * direction[0] + (y - p0[1]) * direction[1], norm2))
        samples = _interval_samples(ts)
        if not ts:
            samples = [F(0)]
        points.update((p0[0] + t * direction[0], p0[1] + t * direction[1]) for t in samples)
    return points


def winner(scores, x: F, y: F) -> int:
    values = [intercept + xs * x + ys * y for intercept, xs, ys in scores]
    best = 0
    for index in range(1, 3):
        if values[index] > values[best]:
            best = index
    return best


def evaluate(x: F, y: F):
    pattern = tuple(winner(scores, x, y) for scores in SCORES)
    r1 = [F(0), F(0), F(0)]
    r2 = [F(0), F(0), F(0)]
    d1l, d1h, d2l, d2h = pattern
    r1[d1h] += C_EXACT
    r1[d1l] += E_S_EXACT
    r1[d2l] += C_EXACT
    r2[d1l] += C_EXACT
    r2[d2h] += C_EXACT
    r2[d2l] += E_S_EXACT
    a1 = tuple(min(value, cap) for value, cap in zip(r1, CAP))
    a2 = tuple(min(value, cap) for value, cap in zip(r2, CAP))
    c1 = sum(r1) - sum(a1)
    c2 = sum(r2) - sum(a2)
    return pattern, a1, c1, a2, c2


def _fmt_vector(values):
    return "(" + ",".join(str(int(value)) for value in values) + ")"


EXPECTED_LINES = {
    (0, 1, -3), (0, 1, 1), (0, 1, 3),
    (1, -1, -6), (1, -1, -4), (1, -1, 4), (1, -1, 6),
    (1, 0, -3), (1, 0, 1), (1, 0, 3),
}
EXPECTED_PATTERNS = {
    (0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 1),
    (0, 0, 2, 1), (0, 0, 2, 2), (1, 0, 1, 1),
    (1, 1, 1, 1), (2, 0, 1, 1), (2, 0, 2, 1),
    (2, 0, 2, 2), (2, 2, 1, 1), (2, 2, 2, 1),
    (2, 2, 2, 2),
}


def pressure_norm_squared(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    return F(2, 3) * (dx * dx - dx * dy + dy * dy)


def verify_paths():
    requested = [
        (F(0), F(0)), (F(101, 300), F(101, 600)),
        (F(101, 150), F(101, 300)), (F(101, 100), F(101, 200)),
    ]
    admitted_common = [
        (F(0), F(0)), (F(101, 300), F(3, 10)),
        (F(101, 150), F(3, 5)), (F(101, 100), F(9, 10)),
    ]
    admitted_world2 = (F(99, 100), F(101, 100))
    radius_squared = F(53, 200) ** 2
    for path in (requested, admitted_common):
        if any(pressure_norm_squared(a, b) > radius_squared for a, b in zip(path, path[1:])):
            raise AssertionError("a displayed continuous-pressure path violates Reach")
    if pressure_norm_squared(admitted_common[-1], admitted_world2) > radius_squared:
        raise AssertionError("the admitted world-2 branch violates Reach")
    if [evaluate(*point)[2] for point in requested] != [20, 20, 20, 0]:
        raise AssertionError("requested path costs changed")
    if [sum(evaluate(*point)[2::2]) / 2 for point in admitted_common] != [20, 20, 20, 20]:
        raise AssertionError("admitted common-path expected costs changed")
    if evaluate(*admitted_common[-1])[2] != 0 or evaluate(*admitted_world2)[4] != 0:
        raise AssertionError("a post-identification pressure is not zero-overflow")


def main():
    lines = equality_lines()
    if set(lines) != EXPECTED_LINES:
        raise AssertionError(f"unexpected equality-line set: {lines}")
    vertices = intersections(lines)
    if len(vertices) != 25:
        raise AssertionError(f"expected 25 arrangement vertices, found {len(vertices)}")
    points = open_2d_witnesses(lines, vertices) | boundary_witnesses(lines, vertices)
    cells = {}
    for x, y in points:
        pattern, a1, c1, a2, c2 = evaluate(x, y)
        cells.setdefault(pattern, (x, y, a1, c1, a2, c2))

    if set(cells) != EXPECTED_PATTERNS:
        missing = sorted(EXPECTED_PATTERNS - set(cells))
        extra = sorted(set(cells) - EXPECTED_PATTERNS)
        raise RuntimeError(f"score-pattern mismatch; missing={missing}, extra={extra}")
    for pattern, (x, y, a1, c1, a2, c2) in sorted(cells.items()):
        informative = a1 != a2
        if c1 + c2 < 2 * E_S_EXACT:
            raise AssertionError(f"expected-cost bound failed for pattern {pattern}")
        if not informative and (c1 != c2 or c1 < E_S_EXACT):
            raise AssertionError(f"uninformative-cell bound failed for pattern {pattern}")
        if informative and max(c1, c2) < 2 * E_S:
            raise AssertionError(f"information/worst-world bound failed for pattern {pattern}")
        if any(cost != 0 and cost < E_S_EXACT for cost in (c1, c2)):
            raise AssertionError(f"positive-overflow quantization failed for pattern {pattern}")
        print(
            f"pattern={tuple(i + 1 for i in pattern)} witness=({x},{y}) "
            f"A1={_fmt_vector(a1)} c1={c1} A2={_fmt_vector(a2)} c2={c2} "
            f"informative={informative}"
        )

    verify_paths()
    print(f"Distinct winner patterns: {len(cells)}")
    print(f"Equality lines: {len(lines)}; vertices: {len(vertices)}")
    print("Arithmetic: exact rational arrangement, costs, and reach checks")


if __name__ == "__main__":
    main()
