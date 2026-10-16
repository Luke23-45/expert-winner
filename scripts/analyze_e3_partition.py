"""
Analyze the E=3 pressure partition for cost-vs-information tradeoff.

For each (x,y) cell, compute:
- A^1, A^2 (admitted vectors)
- c_1, c_2 (overflow costs)
- informative: whether A^1 != A^2 (reveals the world)
- expected cost under equal prior

Goal: characterize the Pareto frontier of (information, cost).
"""
import numpy as np
import sys
sys.path.insert(0, 'tests')
from test_phase1_h3_math import (
    admitted_and_cost, C, E_S, C_SINK, M_LOW, M_MARGIN
)

def analyze_partition(n=121, extent=6.0):
    xs = np.linspace(-extent, extent, n)
    ys = np.linspace(-extent, extent, n)
    cells = {}  # (A1_tuple, A2_tuple) -> dict
    for x in xs:
        for y in ys:
            A1, c1, A2, c2 = admitted_and_cost(float(x), float(y))
            key = (tuple(np.round(A1, 6)), tuple(np.round(A2, 6)))
            if key not in cells:
                cells[key] = {
                    'A1': A1, 'A2': A2,
                    'c1': c1, 'c2': c2,
                    'informative': not np.allclose(A1, A2),
                    'expected_cost': (c1 + c2) / 2,
                    'min_cost': min(c1, c2),
                    'max_cost': max(c1, c2),
                    'representative': (float(x), float(y)),
                    'count': 0,
                }
            cells[key]['count'] += 1
    return cells

def main():
    cells = analyze_partition()
    print(f"Total distinct (A1,A2) cells: {len(cells)}")
    print(f"\n{'informative':<12} {'E[c]':<10} {'c1':<10} {'c2':<10} "
          f"{'A1':<28} {'A2':<28} {'rep (x,y)'}")
    print("-" * 130)
    # Sort by expected cost
    for key in sorted(cells, key=lambda k: cells[k]['expected_cost']):
        d = cells[key]
        print(f"{str(d['informative']):<12} {d['expected_cost']:<10.2f} "
              f"{d['c1']:<10.2f} {d['c2']:<10.2f} "
              f"{str(np.round(d['A1'],1)):<28} {str(np.round(d['A2'],1)):<28} "
              f"{d['representative']}")

    # Key question: cheapest INFORMATIVE action?
    inf = [d for d in cells.values() if d['informative']]
    if inf:
        cheapest = min(inf, key=lambda d: d['expected_cost'])
        print(f"\n--- Cheapest informative action ---")
        print(f"Expected cost: {cheapest['expected_cost']:.2f}")
        print(f"c1={cheapest['c1']:.2f}, c2={cheapest['c2']:.2f}")
        print(f"A1={cheapest['A1']}, A2={cheapest['A2']}")
        print(f"At (x,y)={cheapest['representative']}")

    # Uninformative actions: what's the min expected cost?
    uninf = [d for d in cells.values() if not d['informative']]
    if uninf:
        cheapest_u = min(uninf, key=lambda d: d['expected_cost'])
        print(f"\n--- Cheapest UNINFORMATIVE action ---")
        print(f"Expected cost: {cheapest_u['expected_cost']:.2f}")
        print(f"c1={cheapest_u['c1']:.2f}, c2={cheapest_u['c2']:.2f}")

if __name__ == '__main__':
    main()
