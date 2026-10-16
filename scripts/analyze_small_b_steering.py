"""
Small-B steering analysis for G3.

Question: with B too small to reach the sweet spot in one step,
how many steps does it take, and what overflow is paid per step?

Setup: E=3, q0=0, delta=0. Sweet spot for world 1: x in (m, M), y=0.
Reachability: ||P0(q' - q)||_2 <= eta*gamma*B per step.

We compute the minimum number of steps to reach the sweet-spot
cell from origin, as a function of B.
"""
import numpy as np
import sys
sys.path.insert(0, 'tests')
from test_phase1_h3_math import (
    admitted_and_cost, M_LOW, M_MARGIN, GAMMA, E_S, C
)

ETA = 0.1

def proj_g(v):
    v = np.asarray(v, dtype=float)
    return v - v.min()

def P0(v):
    v = np.asarray(v, dtype=float)
    return v - v.mean()

def to_xy(q):
    """Gauge-invariant coords: x=gamma(q1-q3), y=gamma(q2-q3)."""
    q = np.asarray(q, dtype=float)
    return GAMMA * (q[0] - q[2]), GAMMA * (q[1] - q[2])

def from_xy(x, y):
    """Gauge-fixed q with given (x,y): q = (x/gamma, y/gamma, 0) then proj_g."""
    q = np.array([x / GAMMA, y / GAMMA, 0.0])
    return proj_g(q)

def is_world1_sweet_spot(x, y):
    """Check if (x,y) gives zero overflow in world 1."""
    _, c1, _, _ = admitted_and_cost(x, y)
    return c1 < 1e-9

def min_steps_to_sweet_spot(B, max_steps=50):
    """
    BFS over discretized pressure space to find min steps from
    origin to any world-1 sweet-spot cell, with step bound eta*gamma*B.
    Uses a grid discretization for tractability.
    """
    step_bound = ETA * GAMMA * B
    # Discretize (x,y) space
    extent = 6.0
    n = 61
    xs = np.linspace(-extent, extent, n)
    ys = np.linspace(-extent, extent, n)
    dx = xs[1] - xs[0]

    # Map (ix, iy) -> (x, y)
    # BFS from origin
    from collections import deque
    start = (n // 2, n // 2)  # (0, 0)
    visited = {start: 0}
    queue = deque([start])

    # Precompute which cells are sweet spots
    sweet = np.zeros((n, n), dtype=bool)
    for ix in range(n):
        for iy in range(n):
            sweet[ix, iy] = is_world1_sweet_spot(xs[ix], ys[iy])

    if sweet[start]:
        return 0

    # For BFS, we need to know which grid points are within step_bound.
    # In (x,y) coords: moving from q to q' changes (x,y) by
    # gamma*P0(q'-q) projected. Approximate: ||(dx, dy)|| <=~ step_bound * sqrt(2).
    # Actually: x=gamma(q1-q3), so dx = gamma*d(q1-q3).
    # ||P0(dq)|| <= step_bound implies |d(q1-q3)| <= sqrt(2)*step_bound roughly.
    # Use conservative: max(|dx|,|dy|) <= gamma*sqrt(2)*step_bound.
    max_dxy = GAMMA * np.sqrt(2) * step_bound
    # Grid steps reachable
    grid_reach = max(1, int(np.ceil(max_dxy / dx)))

    while queue:
        ix, iy = queue.popleft()
        d = visited[(ix, iy)]
        if d >= max_steps:
            continue
        for dix in range(-grid_reach, grid_reach + 1):
            for diy in range(-grid_reach, grid_reach + 1):
                jx, jy = ix + dix, iy + diy
                if not (0 <= jx < n and 0 <= jy < n):
                    continue
                if (jx, jy) in visited:
                    continue
                # Check Euclidean distance in (x,y)
                dist = np.sqrt((xs[jx] - xs[ix])**2 + (ys[jy] - ys[iy])**2)
                if dist <= max_dxy + 1e-9:
                    visited[(jx, jy)] = d + 1
                    if sweet[jx, jy]:
                        return d + 1
                    queue.append((jx, jy))
    return None

def main():
    print(f"{'B':<12} {'step_bound':<12} {'min_steps':<10}")
    print("-" * 36)
    # B values: from large (one-step reachable) to small
    B_large = np.sqrt(2) * M_MARGIN / (ETA * GAMMA**2)
    for B in [B_large, B_large/2, B_large/4, B_large/8, B_large/16]:
        steps = min_steps_to_sweet_spot(B)
        print(f"{B:<12.4f} {ETA*GAMMA*B:<12.4f} {str(steps):<10}")

if __name__ == '__main__':
    main()
