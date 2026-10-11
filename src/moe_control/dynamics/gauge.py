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


def pressure_step(
    pressure: Tensor,
    feedback: Tensor,
    eta: float,
    gamma: float,
    delta: float,
) -> Tensor:
    """One gauge-quotient pressure update.

    q_next = Pi_g((1 - delta) * q + eta * gamma * feedback)

    ``feedback`` is the controller's epsilon(obs) vector; this module owns
    the step size, decay, and gauge normalization, never the feedback.
    """
    if not (0.0 <= delta < 1.0):
        raise ValueError(f"Require 0 <= delta < 1, got {delta}.")
    z = (1.0 - delta) * pressure.to(torch.float64) + eta * gamma * feedback.to(torch.float64)
    return gauge_project(z)
