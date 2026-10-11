#!/usr/bin/env python3
"""Predict the first routing-change step for the shortage scenario.

Theorem (see v3_notes/eta_flip_theorem.md): in the pre-flip linear regime
(delta=0, requested feedback, R constant), the pressure is
q_t = t*eta*gamma*(eps - min(eps)) with eps = R/(K*T) - mu, and the first
Top-K flip happens at

    t_flip(eta) = ceil(X / eta),   X = min_{i,e,e'} (a_{i,e} - a_{i,e'})
                                                   / (gamma^2 (eps_e - eps_e'))

over tokens i, e in top2(i), e' not in top2(i), with eps_e > eps_e'.

This script computes X from the regenerated affinity tensor (pure function
of the scenario seed -- no run artifacts used) and prints predicted flip
steps for a list of etas. Run BEFORE the prospective verification runs;
the verifier checks observed first_change_step against these predictions.
"""

from __future__ import annotations

import sys

import torch

from moe_control.routing.topk import deterministic_topk_order
from moe_control.scenarios.synthetic import build_affinity_tensor

E, K, T = 8, 2, 1024
KT = K * T
GAMMA = 1.0
GROUP_SIZES = [300, 270, 240, 214]


def predict(seed: int):
    # float64 for the analytic prediction (runs use float32 scores; the
    # note quantifies that discrepancy).
    a = build_affinity_tensor(
        seed, T, E, GROUP_SIZES, 0.1, torch.float64)
    order = deterministic_topk_order(a)
    top2 = order[:, :K]
    mask = torch.zeros(T, E, dtype=torch.bool)
    mask.scatter_(1, top2, True)
    R = mask.sum(dim=0).to(torch.float64)
    mu = torch.full((E,), 1.0 / E, dtype=torch.float64)
    eps = R / KT - mu

    best = float("inf")
    argmin = None
    for i in range(T):
        e1, e2 = int(top2[i, 0]), int(top2[i, 1])
        ai = a[i]
        for e in (e1, e2):
            for ep in range(E):
                if ep == e1 or ep == e2:
                    continue
                if eps[e] <= eps[ep]:
                    continue
                margin = float(ai[e] - ai[ep])
                if margin <= 0:
                    continue
                ratio = margin / (GAMMA ** 2 * float(eps[e] - eps[ep]))
                if ratio < best:
                    best = ratio
                    argmin = (i, e, ep, margin,
                              float(eps[e]), float(eps[ep]))
    return best, argmin, R.tolist()


def main() -> int:
    etas = [float(x) for x in sys.argv[1:]] or [0.05, 0.1, 0.2, 0.4]
    for seed in (17, 23, 42):
        X, argmin, R = predict(seed)
        i, e, ep, margin, eps_e, eps_ep = argmin
        print(f"seed={seed} R={R}")
        print(f"  X = {X:.6f}")
        print(f"  argmin: token={i} e={e} (eps={eps_e:.6f}) "
              f"e'={ep} (eps={eps_ep:.6f}) margin={margin:.6f}")
        for eta in etas:
            import math
            print(f"  eta={eta:<5} predicted t_flip = ceil({X:.4f}/{eta}) = "
                  f"{math.ceil(X / eta)}   (eta*t in [{X:.4f}, {X + eta:.4f}))")
        print()
    return 0


if __name__ == "__main__":
    main()
