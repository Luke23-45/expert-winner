"""Gauge-normalized pressure dynamics.

The pressure state lives on the gauge quotient R^E / span{1}: routing
depends only on pressure differences, so the canonical nonnegative
representative is q in R_+^E with min_e q_e = 0.

The gauge projection Pi_g(z) = z - min_i(z_i) * 1 is NOT coordinatewise
clipping (ReLU) and NOT the Euclidean projection onto the nonnegative
orthant. It subtracts the minimum coordinate, keeping pressure
nonnegative with minimum exactly zero while preserving all coordinate
differences.
"""

from __future__ import annotations

import torch
from torch import Tensor


def gauge_project(z: Tensor) -> Tensor:
    """Pi_g(z) = z - min(z): canonical nonnegative gauge representative."""
    return z - z.min()


def identity_project(z: Tensor) -> Tensor:
    """Identity projection: returns z unchanged.

    Used only for the no-projection ablation (``projection="identity"``),
    which isolates what the gauge projection contributes. With the identity,
    common-mode drift accumulates in the state; routing depends only on
    score differences, so any behavioral difference vs. gauge projection
    would indicate the projection does more than gauge-fixing.
    """
    return z


def apply_projection(z: Tensor, projection: str) -> Tensor:
    """Apply the named projection: ``"gauge"`` or ``"identity"``."""
    if projection == "gauge":
        return gauge_project(z)
    if projection == "identity":
        return identity_project(z)
    raise ValueError(
        f"Unknown projection {projection!r}; expected 'gauge' or 'identity'."
    )


def pressure_step(
    pressure: Tensor,
    feedback: Tensor,
    eta: float,
    gamma: float,
    delta: float,
    projection: str = "gauge",
) -> Tensor:
    """One gauge-quotient pressure update.

    q_next = Pi((1 - delta) * q + eta * gamma * feedback)

    where Pi is the gauge projection by default. ``feedback`` is the
    controller's epsilon(obs) vector; this module owns the step size, decay,
    and normalization, never the feedback. With ``projection="gauge"`` this
    is exactly q_next = gauge_project((1-delta)*q + eta*gamma*feedback).
    """
    if not (0.0 <= delta < 1.0):
        raise ValueError(f"Require 0 <= delta < 1, got {delta}.")
    z = (1.0 - delta) * pressure.to(torch.float64) + eta * gamma * feedback.to(torch.float64)
    return apply_projection(z, projection)
