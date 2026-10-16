"""Finite-action-grid Bellman solver for the static E=3 research instance.

This is an exact dynamic program on a finite pressure grid, not a certified
solver for the continuous-pressure problem. Every grid-to-grid transition is
checked against the exact transformed Reach ellipsoid. The grid action set is
a subset of the continuous action set, so reported values are grid-restricted
values; they must not be presented as continuous-policy lower bounds.

Usage:
    python scripts/analyze_e3_grid_dp.py --B 2.65 --horizons 3 4 5 8 --n 121
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
# Share the exact instance definition with its mathematical verification tests.
from moe_control.research.e3_instance import (  # noqa: E402
    C,
    C_SINK,
    E_S,
    GAMMA,
    M_LOW,
    M_MARGIN,
    admitted_and_cost,
)

ETA = 0.1
DELTA = 0.0


def exact_reach_offsets(step_xy_radius: float, spacing: float) -> list[tuple[int, int]]:
    """Integer grid offsets satisfying exact Reach in (x,y) coordinates.

    For x=gamma(q1-q3), y=gamma(q2-q3), and delta=0,

      ||P0(q' - q)||^2 = 2/(3 gamma^2) * (dx^2 - dx*dy + dy^2).

    Since the pressure update radius is eta*gamma*B, feasibility is
    dx^2-dx*dy+dy^2 <= 3/2 * (eta*gamma^2*B)^2.
    """
    coord_radius = math.sqrt(3.0) * step_xy_radius
    k = math.ceil(coord_radius / spacing)
    offsets = []
    qmax = 1.5 * step_xy_radius**2
    for di in range(-k, k + 1):
        for dj in range(-k, k + 1):
            dx, dy = di * spacing, dj * spacing
            if dx * dx - dx * dy + dy * dy <= qmax + 1e-12:
                offsets.append((di, dj))
    return offsets


def min_over_reachable(values: np.ndarray, offsets: list[tuple[int, int]]) -> np.ndarray:
    """Return min of `values` over exact-reachable grid successors at each cell."""
    nx, ny = values.shape
    out = np.full_like(values, np.inf, dtype=float)
    for di, dj in offsets:
        ix0, ix1 = max(0, -di), min(nx, nx - di)
        iy0, iy1 = max(0, -dj), min(ny, ny - dj)
        if ix0 >= ix1 or iy0 >= iy1:
            continue
        dst = (slice(ix0, ix1), slice(iy0, iy1))
        src = (slice(ix0 + di, ix1 + di), slice(iy0 + dj, iy1 + dj))
        np.minimum(out[dst], values[src], out=out[dst])
    return out


def solve(B: float, horizons: list[int], n: int, extent: float) -> dict:
    if n < 3 or n % 2 != 1:
        raise ValueError("n must be an odd integer >= 3 so that zero is on the grid")
    xs = np.linspace(-extent, extent, n)
    ys = np.linspace(-extent, extent, n)
    spacing = float(xs[1] - xs[0])
    X, Y = np.meshgrid(xs, ys, indexing="ij")

    c1 = np.empty((n, n), dtype=float)
    c2 = np.empty((n, n), dtype=float)
    informative = np.empty((n, n), dtype=bool)
    for i in range(n):
        for j in range(n):
            a1, c1[i, j], a2, c2[i, j] = admitted_and_cost(float(X[i, j]), float(Y[i, j]))
            informative[i, j] = not np.array_equal(a1, a2)

    # Map the update norm bound to the exact xy ellipsoid radius parameter.
    step_xy_radius = ETA * GAMMA**2 * B
    offsets = exact_reach_offsets(step_xy_radius, spacing)
    if (0, 0) not in offsets:
        raise AssertionError("the pressure self-loop must always be reachable")

    max_h = max(horizons)
    v1 = np.zeros((n, n), dtype=float)
    v2 = np.zeros((n, n), dtype=float)
    va = np.zeros((n, n), dtype=float)
    values = {}
    i0 = j0 = n // 2

    for h in range(1, max_h + 1):
        # Current-round overflow is paid before the policy selects the next
        # pressure. An observation at this pressure determines the posterior.
        prev1, prev2, prev_a = v1, v2, va
        cont_1 = min_over_reachable(prev1, offsets)
        cont_2 = min_over_reachable(prev2, offsets)
        cont_a = min_over_reachable(prev_a, offsets)

        v1 = c1 + cont_1
        v2 = c2 + cont_2
        blind_continuation = np.where(
            informative,
            0.5 * cont_1 + 0.5 * cont_2,
            cont_a,
        )
        va = 0.5 * (c1 + c2) + blind_continuation

        if h in horizons:
            values[h] = {
                "requested": float(0.5 * (v1[i0, j0] + v2[i0, j0])),
                "admitted": float(va[i0, j0]),
                "gap": float(va[i0, j0] - 0.5 * (v1[i0, j0] + v2[i0, j0])),
            }

    return {
        "B": B,
        "n": n,
        "extent": extent,
        "spacing": spacing,
        "reachable_offsets": len(offsets),
        "step_xy_radius": step_xy_radius,
        "values": values,
        "parameters": {
            "C": C,
            "E_S": E_S,
            "C_sink": C_SINK,
            "m": M_LOW,
            "M": M_MARGIN,
            "eta": ETA,
            "gamma": GAMMA,
            "delta": DELTA,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--B", type=float, default=2.65)
    parser.add_argument("--horizons", type=int, nargs="+", default=[3, 4, 5, 8, 12])
    parser.add_argument("--n", type=int, default=121)
    parser.add_argument("--extent", type=float, default=6.0)
    args = parser.parse_args()
    result = solve(args.B, args.horizons, args.n, args.extent)
    print(
        f"finite grid n={result['n']} spacing={result['spacing']:.6g} "
        f"B={result['B']:.6g}; exact Reach offsets={result['reachable_offsets']}"
    )
    print("H   V_requested   V_admitted   admitted-requested")
    for h in args.horizons:
        row = result["values"][h]
        print(f"{h:<3} {row['requested']:>12.6f} {row['admitted']:>12.6f} {row['gap']:>19.6f}")
    print("NOTE: exact DP on a finite grid only; no continuous-space bound is implied.")


if __name__ == "__main__":
    main()
