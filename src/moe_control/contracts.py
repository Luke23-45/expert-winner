"""Shared data contracts between the experiment components.

The runner passes immutable records between the router, capacity policy,
controller, pressure dynamics, and metrics. Components communicate only
through these contracts, so a new controller (or scenario, or capacity
policy) can be added without touching the runner.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Tuple

import torch
from torch import Tensor


@dataclass(frozen=True)
class Observation:
    """Immutable pre-update observation for one control step.

    Holds the pre-capacity requested counts R, the post-capacity admitted
    counts A, the capacity vector C, the target distribution mu, and the
    problem sizes K and T. Tensors are cloned and detached on construction
    so downstream components cannot mutate the runner's state.
    """

    requested: Tensor   # (E,) int64, pre-capacity Top-K request counts R
    admitted: Tensor    # (E,) int64, canonical admitted counts A
    capacity: Tensor    # (E,) int64
    target: Tensor      # (E,) float, probability vector mu
    top_k: int          # K
    tokens: int         # T

    def __post_init__(self) -> None:
        object.__setattr__(self, "requested", self.requested.detach().clone())
        object.__setattr__(self, "admitted", self.admitted.detach().clone())
        object.__setattr__(self, "capacity", self.capacity.detach().clone())
        object.__setattr__(self, "target", self.target.detach().clone())


@dataclass(frozen=True)
class CapacityResult:
    """Immutable outcome of capacity admission."""

    admitted: Tensor  # (E,) int64, A_e = min(R_e, C_e) under canonical admission
    rejected: Tensor  # (E,) int64, J = R - A


class AffinityScenario(Protocol):
    """Produces the raw affinity batch for a control step."""

    name: str

    def batch(self, step: int) -> Tensor:
        """Return the (T, E) raw affinity tensor for ``step``."""
        ...

    def reference(self) -> dict:
        """Return affinity-generation parameters and/or a content hash."""
        ...


class CapacityPolicy(Protocol):
    """Maps pre-capacity request counts to admitted/rejected counts."""

    name: str

    def admit(self, requested: Tensor, capacity: Tensor) -> CapacityResult:
        ...


class FeedbackController(Protocol):
    """Computes the feedback vector from an immutable observation.

    Controllers must not mutate pressure state or select experts; they
    only produce the feedback vector epsilon(obs) in R^E.
    """

    name: str

    def feedback(self, obs: Observation) -> Tensor:
        """Return the (E,) float feedback vector for this observation."""
        ...


# A pressure-state update: q_next from (q, feedback, eta, gamma, delta).
PressureStep = Tuple[Tensor, Tensor]
