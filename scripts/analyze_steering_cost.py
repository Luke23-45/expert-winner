"""
Minimum-cost steering path with small B.

Not just min steps, but min cumulative overflow along the path
from origin to world-1 sweet spot, under the (Reach) step bound.
Uses Dijkstra over the discretized (x,y) grid.
"""
import numpy as np
import heapq
import sys
sys.path.insert(0, 'tests')
from test_phase1_h3_math import admitted_and_cost, M_LOW, M_MARGIN, GAMMA, E_S

ETA = 0.1

def is_world1_sweet_spot(x, y):
    _, c1, _, _ = admitted_and_cost(x, y)
    return c1 < 1e-9

def min_cost_steering(B, extent=6.0, n=61):
    step_bound = ETA * GAMMA * B
    xs = np.linspace(-extent, extent, n)
    ys = np.linspace(-extent, extent, n)
    dx = xs[1] - xs[0]
    max_dxy = GAMMA * np.sqrt(2) * step_bound
    grid_reach = max(1, int(np.ceil(max_dxy / dx)))

    # Cost of being at each cell (expected overflow, equal prior)
    cost = np.zeros((n, n))
    sweet = np.zeros((n, n), dtype=bool)
    for ix in range(n):
        for iy in range(n):
            _, c1, _, c2 = admitted_and_cost(float(xs[ix]), float(ys[iy]))
            cost[ix, iy] = (c1 + c2) / 2
            sweet[ix, iy] = c1 < 1e-9

    start = (n // 2, n // 2)
    # Dijkstra: dist[ix,iy] = min cumulative cost to reach (ix,iy)
    INF = float('inf')
    dist = np.full((n, n), INF)
    dist[start] = cost[start]  # pay cost at start too
    pq = [(cost[start], start)]
    prev = {}

    while pq:
        d, (ix, iy) = heapq.heappop(pq)
        if d > dist[ix, iy]:
            continue
        if sweet[ix, iy]:
            # Reconstruct path length
            path_len = 0
            cur = (ix, iy)
            while cur in prev:
                cur = prev[cur]
                path_len += 1
            return d, path_len
        for dix in range(-grid_reach, grid_reach + 1):
            for diy in range(-grid_reach, grid_reach + 1):
                jx, jy = ix + dix, iy + diy
                if not (0 <= jx < n and 0 <= jy < n):
                    continue
                if (jx, jy) == (ix, iy):
                    continue
                dist_xy = np.sqrt((xs[jx]-xs[ix])**2 + (ys[jy]-ys[iy])**2)
                if dist_xy <= max_dxy + 1e-9:
                    nd = d + cost[jx, jy]
                    if nd < dist[jx, jy]:
                        dist[jx, jy] = nd
                        prev[(jx, jy)] = (ix, iy)
                        heapq.heappush(pq, (nd, (jx, jy)))
    return None, None

def main():
    B_large = np.sqrt(2) * M_MARGIN / (ETA * GAMMA**2)
    print(f"{'B':<10} {'min_cost':<12} {'steps':<8} {'note'}")
    print("-" * 50)
    for B in [B_large, B_large/2, B_large/4, B_large/8, B_large/16]:
        c, s = min_cost_steering(B)
        note = "1-step reachable" if s == 1 else ""
        print(f"{B:<10.3f} {c:<12.2f} {str(s):<8} {note}")

if __name__ == '__main__':
    main()
