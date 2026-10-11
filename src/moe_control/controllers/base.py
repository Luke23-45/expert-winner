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


class BiasIntegralFeedback:
    """DeepSeek-style aux-loss-free bias controller (integral control).

    A per-expert bias b is added to routing scores for Top-K SELECTION
    only (the runner adds the state with score_sign=+1; in a real model the
    gating weights would use unbiased scores). After each step the bias is
    updated outside autograd from the observed ADMITTED (assigned) load::

        b_e <- b_e - bias_gamma   if A_e > mean(A)   (overloaded)
        b_e <- b_e + bias_gamma   if A_e < mean(A)   (underloaded)
        b_e unchanged             if A_e == mean(A)

    The feedback() method returns bias_gamma * sign_e; the runner applies it
    with eta=1, update_gain=1, delta=0, projection="identity", so the state
    update is exactly the sign-based integrator above: a pure integral
    controller with no leak and no projection. Admitted (post-capacity)
    load is used because that is what the deployed system observes once
    tokens are dropped; this choice is recorded in the run manifest notes.
    Default bias_gamma=0.001 matches DeepSeek-V3.
    """

    name = "bias_integral"

    def __init__(self, bias_gamma: float = 0.001) -> None:
        if bias_gamma <= 0:
            raise ValueError(f"Require bias_gamma > 0, got {bias_gamma}.")
        self.bias_gamma = float(bias_gamma)

    def feedback(self, obs: Observation) -> Tensor:
        load = obs.admitted.to(torch.float64)
        mean = load.mean()
        sign = torch.where(
            load > mean,
            torch.tensor(-1.0, dtype=torch.float64),
            torch.where(
                load < mean,
                torch.tensor(1.0, dtype=torch.float64),
                torch.tensor(0.0, dtype=torch.float64),
            ),
        )
        return self.bias_gamma * sign


CONTROLLERS = {
    "requested": RequestedFeedback,
    "admitted": AdmittedFeedback,
    "admitted_centered": AdmittedCenteredFeedback,
    "capacity_relative": CapacityRelativeFeedback,
    "bias_integral": BiasIntegralFeedback,
    # Ablation variants: same requested feedback vector, different dynamics.
    # "requested_leaky" runs with pressure_decay > 0 (isolates the leak);
    # "requested_no_projection" runs with projection="identity" (isolates the
    # gauge projection). Dynamics parameters come from the controller config.
    "requested_leaky": RequestedFeedback,
    "requested_no_projection": RequestedFeedback,
}


def build_controller(name: str, **kwargs):
    """Instantiate a controller by its registry name.

    Extra keyword arguments are forwarded to the controller constructor
    (used for bias_gamma on the bias_integral controller).
    """
    try:
        cls = CONTROLLERS[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown controller {name!r}; expected one of {sorted(CONTROLLERS)}."
        ) from exc
    if name == "bias_integral":
        return cls(**kwargs)
    if kwargs:
        raise ValueError(
            f"Controller {name!r} takes no constructor arguments; got {sorted(kwargs)}."
        )
    return cls()


def gauge_equivalence_classes(capacity_uniform: bool, target_uniform: bool) -> dict:
    """Return the gauge-equivalence grouping for the configured regime.

    Under uniform capacity and uniform target, requested == capacity_relative
    exactly, and admitted == admitted_centered up to a common-mode component
    removed by the gauge projection. The requested_leaky and
    requested_no_projection ablations share the requested feedback vector
    exactly (same gauge class for feedback) but run different dynamics, so
    they are separate scientific comparisons, not duplicate findings.
    The bias_integral controller carries a bias state, not a gauge-fixed
    pressure, and is always its own class.
    """
    note_feedback = (
        "Under uniform capacity and uniform target, (requested) and "
        "(capacity_relative) feedback vectors are identical, and "
        "(admitted) and (admitted_centered) differ only by a common-mode "
        "component removed by gauge projection. Do not count equivalent "
        "variants as independent scientific findings. The requested_leaky "
        "and requested_no_projection ablations share the requested feedback "
        "vector exactly; they differ only in dynamics (leak / projection)."
    )
    classes = {
        "requested": "gauge-class-R",
        "capacity_relative": "gauge-class-R",
        "admitted": "gauge-class-A",
        "admitted_centered": "gauge-class-A",
        "requested_leaky": "gauge-class-R",
        "requested_no_projection": "gauge-class-R",
        "bias_integral": "gauge-class-bias",
    }
    if capacity_uniform and target_uniform:
        return {**classes, "note": note_feedback}
    return {
        name: f"gauge-class-{name}" for name in CONTROLLERS
    } | {"note": "No gauge equivalence asserted for this capacity/target regime."}
