#!/usr/bin/env python3
"""Unit checks for the admitted_antiwindup controller's reduction properties.

These are pure-function checks on feedback(), independent of the runner:

  U1 no saturation      -> feedback == P_0(A/(K*T) - mu), and the gauge
                           update Pi_g(q + c*eps_aw) is bit-identical to
                           the (A) admitted update Pi_g(q + c*eps_adm).
  U2 global saturation  -> feedback == 0 (full integrator freeze), while
                           (A)/(A_0) would integrate the phantom gradient
                           P_0(C/(K*T)) under heterogeneous capacities.
  U3 partial saturation -> saturated coordinates get exactly 0 relative
                           feedback; unsaturated coordinates integrate
                           their deviation from the unsaturated mean.

Exits nonzero on any failure.
"""

from __future__ import annotations

import sys

import torch

from moe_control.contracts import Observation
from moe_control.controllers import build_controller
from moe_control.controllers.base import zero_sum_project
from moe_control.dynamics.gauge import gauge_project

E, K, T = 8, 2, 1024
KT = K * T


def make_obs(requested, capacity, target):
    requested = torch.tensor(requested, dtype=torch.int64)
    capacity = torch.tensor(capacity, dtype=torch.int64)
    admitted = torch.minimum(requested, capacity)
    return Observation(
        requested=requested,
        admitted=admitted,
        capacity=capacity,
        target=torch.tensor(target, dtype=torch.float64),
        top_k=K,
        tokens=T,
    )


def main() -> int:
    failures = 0

    def check(name, ok, detail=""):
        nonlocal failures
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
              + (f" -- {detail}" if detail else ""))
        failures += not ok

    aw = build_controller("admitted_antiwindup")
    adm = build_controller("admitted")
    adm_c = build_controller("admitted_centered")

    mu_uniform = [1.0 / E] * E
    cap_uniform = [192] * E

    # U1: no saturation -> reduces to admitted on the gauge quotient.
    obs = make_obs(
        requested=[300, 300, 270, 270, 240, 240, 214, 214],
        capacity=[400] * E,  # nothing saturated
        target=mu_uniform,
    )
    eps_aw = aw.feedback(obs)
    a = obs.admitted.to(torch.float64) / KT
    mu = obs.target.to(torch.float64)
    expected = zero_sum_project(a - mu)
    check("U1 feedback == P_0(A/(K*T) - mu) when unsaturated",
          bool(torch.equal(eps_aw, expected)),
          f"max|diff|={(eps_aw - expected).abs().max().item():.3e}")
    # Bit-identical gauge update vs (A) admitted for arbitrary q.
    torch.manual_seed(0)
    bit_ok = True
    for _ in range(20):
        q = torch.randn(E, dtype=torch.float64).abs()
        q = gauge_project(q)
        c = 0.05 * 1.0
        q_aw = gauge_project(q + c * eps_aw)
        q_adm = gauge_project(q + c * adm.feedback(obs))
        if not torch.equal(q_aw, q_adm):
            bit_ok = False
            break
    check("U1 gauge update bit-identical to (A) admitted (20 random q)", bit_ok)

    # U2: global saturation -> full freeze, even with heterogeneous capacity.
    cap_hetero = [300, 270, 240, 210, 180, 150, 120, 66]
    obs_sat = make_obs(
        requested=[400, 380, 350, 320, 300, 280, 250, 220],  # all >= C
        capacity=cap_hetero,
        target=mu_uniform,
    )
    eps_aw_sat = aw.feedback(obs_sat)
    check("U2 feedback == 0 under global saturation",
          bool(torch.equal(eps_aw_sat, torch.zeros(E, dtype=torch.float64))),
          f"max|eps|={eps_aw_sat.abs().max().item():.3e}")
    # (A) and (A_0) integrate a phantom gradient from capacity heterogeneity.
    phantom_a = adm.feedback(obs_sat)
    phantom_a0 = adm_c.feedback(obs_sat)
    check("U2 (A) admitted integrates phantom gradient under hetero capacity",
          bool((zero_sum_project(phantom_a)).abs().max().item() > 1e-6),
          f"max|P_0(eps_adm)|={zero_sum_project(phantom_a).abs().max().item():.3e}")
    check("U2 (A_0) admitted_centered integrates phantom gradient",
          bool(phantom_a0.abs().max().item() > 1e-6),
          f"max|eps|={phantom_a0.abs().max().item():.3e}")
    # Sanity: under UNIFORM capacity the phantom vanishes (v1 freeze regime).
    obs_sat_u = make_obs(
        requested=[300] * E, capacity=cap_uniform, target=mu_uniform,
    )
    check("U2 (A_0) phantom vanishes under uniform capacity (v1 regime)",
          bool(adm_c.feedback(obs_sat_u).abs().max().item() < 1e-12))

    # U3: partial saturation -> saturated coords frozen at exactly 0.
    obs_part = make_obs(
        requested=[500, 500, 100, 100, 100, 100, 100, 100],
        capacity=cap_uniform,  # experts 0,1 saturated; rest not
        target=mu_uniform,
    )
    eps_part = aw.feedback(obs_part)
    sat = torch.tensor([True, True, False, False, False, False, False, False])
    check("U3 saturated coords get exactly 0 feedback",
          bool(torch.equal(eps_part[sat], torch.zeros(2, dtype=torch.float64))),
          f"vals={eps_part[sat].tolist()}")
    g_unsat = (obs_part.admitted.to(torch.float64) / KT - mu)[~sat]
    expected_unsat = g_unsat - g_unsat.mean()
    check("U3 unsaturated coords integrate deviation from unsaturated mean",
          bool(torch.equal(eps_part[~sat], expected_unsat)),
          f"max|diff|={(eps_part[~sat] - expected_unsat).abs().max().item():.3e}")
    check("U3 feedback is zero-sum",
          abs(eps_part.sum().item()) < 1e-12)

    # U4: explicit non-uniform target also works (T1 regime).
    mu_explicit = [0.1875, 0.171875, 0.15625, 0.140625,
                   0.125, 0.109375, 0.0625, 0.046875]
    obs_exp = make_obs(
        requested=[500, 500, 100, 100, 100, 100, 100, 100],
        capacity=cap_uniform,
        target=mu_explicit,
    )
    eps_exp = aw.feedback(obs_exp)
    check("U4 zero-sum under explicit target",
          abs(eps_exp.sum().item()) < 1e-12)
    check("U4 saturated coords frozen under explicit target",
          bool(torch.equal(eps_exp[sat], torch.zeros(2, dtype=torch.float64))))

    print("ALL CHECKS PASSED" if failures == 0 else f"{failures} CHECKS FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
