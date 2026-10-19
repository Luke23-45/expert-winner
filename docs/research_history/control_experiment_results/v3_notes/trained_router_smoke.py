#!/usr/bin/env python3
"""Toy trained-router smoke test (v3 Track 3).

Minimal MoE (8 MLP experts + learned top-2 router) on a synthetic 8-class
task, trained under three conditions: (A) aux-loss balancing, (B) the real
RequestedFeedback pressure controller from moe_control (selection-only
pressure on routing scores, no aux loss), (C) no balancing.

Purpose: validate the feasibility ESTIMATE (runs on CPU in minutes; loss
and balance jointly measurable). This is a mechanics smoke test, NOT
evidence for the paper's claims -- see trained_router_feasibility.md.

Budget: must complete in well under 15 minutes wall-clock.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import torch
import torch.nn as nn

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from moe_control.contracts import Observation  # noqa: E402
from moe_control.controllers import build_controller  # noqa: E402
from moe_control.dynamics.gauge import gauge_project  # noqa: E402

E, K, T = 8, 2, 256
D_IN, D_HID, NCLS = 16, 32, 8
STEPS = 300
LR = 3e-3


def make_centers():
    gen = torch.Generator().manual_seed(7)
    angles = torch.linspace(0, 2 * torch.pi, NCLS + 1)[:-1]
    base = torch.stack([torch.cos(angles), torch.sin(angles)], dim=1)
    pad = torch.randn(NCLS, D_IN - 2, generator=gen) * 0.3
    return torch.cat([base * 4.0, pad], dim=1)


CENTERS = make_centers()


def sample_batch(n, gen):
    labels = torch.randint(0, NCLS, (n,), generator=gen)
    x = CENTERS[labels] + torch.randn(n, D_IN, generator=gen)
    return x, labels


class ToyMoE(nn.Module):
    def __init__(self):
        super().__init__()
        self.experts = nn.ModuleList([
            nn.Sequential(nn.Linear(D_IN, D_HID), nn.ReLU(),
                          nn.Linear(D_HID, NCLS))
            for _ in range(E)
        ])
        self.router = nn.Linear(D_IN, E)

    def forward(self, x, pressure=None, gamma=1.0):
        router_logits = self.router(x)  # (T, E)
        scores = (router_logits - gamma * pressure if pressure is not None
                  else router_logits)
        order = torch.argsort(scores, dim=1, descending=True, stable=True)
        top2 = order[:, :K]
        # expert logits for the selected experts
        sel_logits = torch.stack(
            [self.experts[e](x) for e in range(E)], dim=1)  # (T, E, C)
        idx = top2.unsqueeze(-1).expand(T, K, NCLS)
        chosen = sel_logits.gather(1, idx)  # (T, K, C)
        w = torch.softmax(scores.gather(1, top2), dim=1).unsqueeze(-1)
        out = (chosen * w).sum(dim=1)  # (T, C)
        # requested counts from selection
        mask = torch.zeros(T, E, dtype=torch.bool)
        mask.scatter_(1, top2, True)
        requested = mask.sum(dim=0)
        # aux-loss ingredients (condition A)
        prob = torch.softmax(router_logits, dim=1).mean(dim=0)
        frac = requested.to(torch.float64) / (K * T)
        aux = E * (frac * prob.to(torch.float64)).sum()
        return out, requested, aux


def run_condition(name, use_pressure, use_aux, seed):
    torch.manual_seed(seed)
    gen = torch.Generator().manual_seed(1000 + seed)
    model = ToyMoE()
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    ce = nn.CrossEntropyLoss()
    fb = build_controller("requested")
    mu = torch.full((E,), 1.0 / E, dtype=torch.float64)
    cap = torch.full((E,), T, dtype=torch.int64)  # no dropping in the toy
    q = torch.zeros(E, dtype=torch.float64)
    eta, gamma = 0.5, 1.0
    hist = []
    t0 = time.time()
    for step in range(STEPS):
        x, y = sample_batch(T, gen)
        out, requested, aux = model(
            x, pressure=q if use_pressure else None, gamma=gamma)
        loss = ce(out, y)
        if use_aux:
            loss = loss + 0.01 * aux
        opt.zero_grad()
        loss.backward()
        opt.step()
        if use_pressure:
            obs = Observation(requested=requested.detach(),
                              admitted=requested.detach(),
                              capacity=cap, target=mu, top_k=K, tokens=T)
            eps = fb.feedback(obs)
            q = gauge_project(q + eta * gamma * eps)
        if (step + 1) % 25 == 0:
            with torch.no_grad():
                acc = (out.argmax(dim=1) == y).float().mean().item()
            viol = float((requested.double() / (K * T) - 1 / E).abs().max())
            hist.append((step + 1, float(loss.item()), acc, viol,
                         float(q.abs().max())))
    dt = time.time() - t0
    return hist, dt


def main():
    print("condition: (A) aux-loss | (B) pressure | (C) none; 300 steps each")
    results = {}
    for name, use_pressure, use_aux, seed in [
            ("A aux-loss", False, True, 11),
            ("B pressure", True, False, 11),
            ("C none", False, False, 11)]:
        hist, dt = run_condition(name, use_pressure, use_aux, seed)
        results[name] = (hist, dt)
        print(f"[{name}] {STEPS} steps in {dt:.1f}s "
              f"({1000 * dt / STEPS:.1f} ms/step)")
        for step, loss, acc, viol, qmax in hist[::2]:
            print(f"  step {step:>3}: loss={loss:.3f} acc={acc:.3f} "
                  f"viol={viol:.4f} |q|max={qmax:.3f}")
    total = sum(dt for _, dt in results.values())
    print(f"TOTAL wall-clock: {total:.1f}s for 3x{STEPS} steps")
    ok = all(h[-1][1] < h[0][1] for h, _ in results.values())
    print("loss decreased on all conditions:", ok)


if __name__ == "__main__":
    main()
