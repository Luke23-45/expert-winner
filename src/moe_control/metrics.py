"""Pure metric functions over a completed pre-update observation.

Metrics are descriptive only: they never change routing, counts, or
control state. Overflow is reported separately from requested-load
balance, because in the fully saturated aggregate-shortage regime total
overflow is fixed by the aggregate capacity shortage and a controller
cannot reduce it.
"""

from __future__ import annotations

import torch
from torch import Tensor

from moe_control.contracts import Observation


def requested_max_violation(obs: Observation) -> float:
    """max_e |R_e / (K*T) - mu_e|: worst requested-load deviation."""
    frac = obs.requested.to(torch.float64) / (obs.top_k * obs.tokens)
    return (frac - obs.target.to(torch.float64)).abs().max().item()


def requested_cv(requested: Tensor) -> float:
    """Coefficient of variation of the requested counts (population std)."""
    r = requested.to(torch.float64)
    mean = r.mean()
    if mean.item() == 0.0:
        return 0.0
    return (r.std(unbiased=False) / mean).item()


def total_overflow(rejected: Tensor) -> int:
    """Total rejected load sum_e J_e."""
    return int(rejected.sum().item())


def all_experts_saturated(requested: Tensor, capacity: Tensor) -> bool:
    """Whether every expert is at or above capacity (R_e >= C_e for all e)."""
    return bool((requested >= capacity).all().item())


def aggregate_capacity_shortage(capacity: Tensor, top_k: int, tokens: int) -> int:
    """K*T - sum_e C_e: signed aggregate capacity mismatch.

    Positive means aggregate shortage (hard-capacity assignment infeasible);
    reported separately from per-expert overflow.
    """
    return top_k * tokens - int(capacity.sum().item())
