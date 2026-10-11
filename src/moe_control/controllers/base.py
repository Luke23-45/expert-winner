"""Feedback-controller base utilities.

Controllers compute the feedback vector epsilon(obs) only. The pressure
transition (step size, decay, gauge normalization) lives in
``moe_control.dynamics.gauge`` and is shared by all controllers.

Equivalence note (from the formal document, section "Exact experimental
update rules"): under a uniform target and uniform capacities,
  * (requested) and (capacity_relative) coincide exactly;
  * (admitted) and (admitted_centered) differ only by a common-mode
    component, which the gauge projection removes, so they define the
    same gauge dynamics.
Equivalent variants must not be counted as independent scientific
findings; the run manifest records the equivalence class for the
configured capacity/target regime.
"""

from __future__ import annotations

import torch
from torch import Tensor

from moe_control.contracts import Observation


def zero_sum_project(x: Tensor) -> Tensor:
    """P_0 x = x - mean(x): projection onto the zero-sum subspace."""
    return x - x.mean()


def normalized_requested(obs: Observation) -> Tensor:
    return obs.requested.to(torch.float64) / (obs.top_k * obs.tokens)


def normalized_admitted(obs: Observation) -> Tensor:
    return obs.admitted.to(torch.float64) / (obs.top_k * obs.tokens)


class RequestedFeedback:
    """(R) Requested feedback: epsilon = R / (K*T) - mu."""

    name = "requested"

    def feedback(self, obs: Observation) -> Tensor:
        return normalized_requested(obs) - obs.target.to(torch.float64)


class AdmittedFeedback:
    """(A) Admitted feedback: epsilon = A / (K*T) - mu."""

    name = "admitted"

    def feedback(self, obs: Observation) -> Tensor:
        return normalized_admitted(obs) - obs.target.to(torch.float64)


class AdmittedCenteredFeedback:
    """(A_0) Admitted feedback with common mode removed: P_0(A / (K*T))."""

    name = "admitted_centered"

    def feedback(self, obs: Observation) -> Tensor:
        return zero_sum_project(normalized_admitted(obs))


class CapacityRelativeFeedback:
    """(C) Capacity-relative requested feedback: P_0(R / (K*T) - C / (K*T))."""

    name = "capacity_relative"

    def feedback(self, obs: Observation) -> Tensor:
        kt = obs.top_k * obs.tokens
        r = obs.requested.to(torch.float64) / kt
        c = obs.capacity.to(torch.float64) / kt
        return zero_sum_project(r - c)


CONTROLLERS = {
    "requested": RequestedFeedback,
    "admitted": AdmittedFeedback,
    "admitted_centered": AdmittedCenteredFeedback,
    "capacity_relative": CapacityRelativeFeedback,
}


def build_controller(name: str):
    """Instantiate a controller by its registry name."""
    try:
        return CONTROLLERS[name]()
    except KeyError as exc:
        raise ValueError(
            f"Unknown controller {name!r}; expected one of {sorted(CONTROLLERS)}."
        ) from exc


def gauge_equivalence_classes(capacity_uniform: bool, target_uniform: bool) -> dict:
    """Return the gauge-equivalence grouping for the configured regime.

    Under uniform capacity and uniform target, requested == capacity_relative
    exactly, and admitted == admitted_centered up to a common-mode component
    removed by the gauge projection. Otherwise each variant is its own class.
    """
    if capacity_uniform and target_uniform:
        return {
            "requested": "gauge-class-R",
            "capacity_relative": "gauge-class-R",
            "admitted": "gauge-class-A",
            "admitted_centered": "gauge-class-A",
            "note": (
                "Under uniform capacity and uniform target, (requested) and "
                "(capacity_relative) feedback vectors are identical, and "
                "(admitted) and (admitted_centered) differ only by a common-mode "
                "component removed by gauge projection. Do not count equivalent "
                "variants as independent scientific findings."
            ),
        }
    return {
        name: f"gauge-class-{name}" for name in CONTROLLERS
    } | {"note": "No gauge equivalence asserted for this capacity/target regime."}
