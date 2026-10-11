"""The single shared experiment runner.

One explicit, ordered control loop. The scenario, capacity policy, and
controller are injected; adding a new controller requires only a new
controller implementation plus a config group, never a copy of this
runner.

Iteration order (fixed by the formal document):
  1. Read current pressure q and the affinity batch a.
  2. Compute pressured scores s = a - gamma * q.
  3. Select exactly K distinct experts per token (deterministic tie rule).
  4. Count pre-capacity requests R.
  5. Compute canonical admitted counts A = min(R, C) and rejected J = R - A.
  6. Build an immutable observation (R, A, C, mu, K, T).
  7. Compute controller feedback epsilon.
  8. Update pressure: q_next = Pi_g((1 - delta) q + eta gamma epsilon).
  9. Record metrics for the observation and both pressure-before/after.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import torch
from torch import Tensor

from moe_control.capacity.per_expert import CanonicalCapacityPolicy
from moe_control.config import ConfigValidationError
from moe_control.contracts import Observation
from moe_control.dynamics.gauge import apply_projection, pressure_step
from moe_control.metrics import (
    aggregate_capacity_shortage,
    all_experts_saturated,
    requested_cv,
    requested_max_violation,
    specialization_mi,
    total_overflow,
)
from moe_control.routing.topk import (
    deterministic_topk_order,
    pressured_scores,
    requested_counts,
)


@dataclass
class RunContext:
    run_id: str
    seed: int
    scenario_name: str
    controller_name: str
    capacity_regime: str
    steps: int
    experts: int
    top_k: int
    tokens: int
    gamma: float          # effective score-modulation gain
    score_sign: float     # -1.0: state subtracts from scores (pressure);
                          # +1.0: state adds to scores (selection bias)
    eta: float
    delta: float
    update_gain: float    # gain multiplying feedback in the state update
                          # (== gamma for pressure controllers; 1.0 for bias)
    projection: str       # "gauge" (canonical) | "identity" (ablation)
    target: Tensor        # (E,) float mu
    capacity: Tensor      # (E,) int64
    initial_condition: str
    device: torch.device
    float_dtype: torch.dtype


def verify_initial_condition(
    kind: str, requested: Tensor, capacity: Tensor, top_k: int, tokens: int
) -> Dict[str, Any]:
    """Check the scenario's declared initial condition against realized counts.

    The realized requested counts are used, never the assumed skew. The
    result is recorded in the run summary and returned to the caller.
    """
    result: Dict[str, Any] = {"declared": kind}
    if kind == "all_saturated":
        ok = all_experts_saturated(requested, capacity)
        result["verified"] = ok
        result["detail"] = (
            "every expert at or above capacity at step 0" if ok
            else "VIOLATED: some expert below capacity at step 0"
        )
    elif kind == "balanced":
        expected = (top_k * tokens) // capacity.shape[0]
        deviation = int((requested - expected).abs().max().item())
        result["max_abs_deviation"] = deviation
        result["verified"] = deviation == 0
        result["detail"] = (
            f"R_e == K*T/E == {expected} for all e" if deviation == 0
            else f"VIOLATED: max |R_e - {expected}| = {deviation}"
        )
    else:  # "unconstrained"
        result["verified"] = True
        result["detail"] = "no requirement declared; recorded only"
    result["realized_requested"] = [int(v) for v in requested.tolist()]
    return result


def run_experiment(
    ctx: RunContext,
    scenario: Any,
    controller: Any,
    capacity_policy: Optional[Any] = None,
    progress_every: int = 100,
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Execute the closed-loop control experiment. Returns (rows, summary)."""
    policy = capacity_policy or CanonicalCapacityPolicy()
    device, fdtype = ctx.device, ctx.float_dtype

    # Controller state: pressure for the pressure controllers, selection bias
    # for bias_integral. Initialized at zero and normalized with the
    # configured projection (a no-op on zeros either way; explicit anyway).
    pressure = torch.zeros(ctx.experts, dtype=torch.float64, device=device)
    pressure = apply_projection(pressure, ctx.projection)

    # Optional per-token skill labels (specialization_probe scenario): when
    # present, the runner records the MI between skill label and top-1
    # expert assignment each step.
    skill_labels_fn = getattr(scenario, "skill_labels", None)

    rows: List[Dict[str, Any]] = []
    initial_check: Optional[Dict[str, Any]] = None
    saturated_steps = 0

    with torch.no_grad():
        for step in range(ctx.steps):
            # 1. Read current pressure and affinity batch.
            affinity = scenario.batch(step).to(device=device, dtype=fdtype)

            # 2. Modulated scores (pressure subtracts, bias adds).
            scores = pressured_scores(
                affinity, pressure.to(fdtype), ctx.gamma, ctx.score_sign
            )

            # 3-4. Deterministic Top-K selection and pre-capacity request counts.
            order = deterministic_topk_order(scores)
            mask = torch.zeros_like(scores, dtype=torch.bool)
            mask.scatter_(1, order[:, : ctx.top_k], True)
            requested = requested_counts(mask).to(device)

            # 5. Canonical capacity admission.
            admitted_result = policy.admit(requested, ctx.capacity.to(device))
            admitted, rejected = admitted_result.admitted, admitted_result.rejected

            # 6. Immutable observation.
            obs = Observation(
                requested=requested,
                admitted=admitted,
                capacity=ctx.capacity.to(device),
                target=ctx.target.to(device),
                top_k=ctx.top_k,
                tokens=ctx.tokens,
            )

            # 7. Controller feedback (feedback only; no state mutation here).
            feedback = controller.feedback(obs).to(torch.float64)

            # 8. State transition with the configured projection.
            pressure_before = pressure.clone()
            pressure = pressure_step(
                pressure, feedback, ctx.eta, ctx.update_gain, ctx.delta,
                ctx.projection,
            )

            # Initial-condition verification uses realized counts at step 0.
            if step == 0:
                initial_check = verify_initial_condition(
                    ctx.initial_condition, requested, ctx.capacity.to(device),
                    ctx.top_k, ctx.tokens,
                )
                if not initial_check["verified"]:
                    print(
                        f"WARNING: initial condition '{ctx.initial_condition}' "
                        f"not met: {initial_check['detail']}"
                    )

            # 9. Metrics for this observation, with pressure before and after.
            saturated = all_experts_saturated(requested, ctx.capacity.to(device))
            saturated_steps += int(saturated)
            row = {
                "run_id": ctx.run_id,
                "step": step,
                "seed": ctx.seed,
                "scenario": ctx.scenario_name,
                "controller": ctx.controller_name,
                "capacity_regime": ctx.capacity_regime,
                "requested_counts": [int(v) for v in requested.tolist()],
                "admitted_counts": [int(v) for v in admitted.tolist()],
                "rejected_counts": [int(v) for v in rejected.tolist()],
                "total_overflow": total_overflow(rejected),
                "all_experts_saturated": saturated,
                "requested_max_violation": requested_max_violation(obs),
                "requested_cv": requested_cv(requested),
                "aggregate_capacity_shortage": aggregate_capacity_shortage(
                    ctx.capacity.to(device), ctx.top_k, ctx.tokens
                ),
                "pressure_before": [float(v) for v in pressure_before.tolist()],
                "pressure_after": [float(v) for v in pressure.tolist()],
                "feedback": [float(v) for v in feedback.tolist()],
            }
            if skill_labels_fn is not None:
                # Top-1 expert per token under the documented tie rule.
                top1 = order[:, 0].to(torch.int64).cpu()
                labels = skill_labels_fn(step).to(torch.int64).cpu()
                row["specialization_mi"] = specialization_mi(labels, top1)
            rows.append(row)

            if progress_every and (step + 1) % progress_every == 0:
                print(f"  step {step + 1}/{ctx.steps}")

    if initial_check is None:
        raise ConfigValidationError("Runner produced no steps; check experiment.steps.")

    summary = {
        "run_id": ctx.run_id,
        "steps": ctx.steps,
        "seed": ctx.seed,
        "scenario": ctx.scenario_name,
        "controller": ctx.controller_name,
        "capacity_regime": ctx.capacity_regime,
        "score_sign": ctx.score_sign,
        "projection": ctx.projection,
        "update_gain": ctx.update_gain,
        "initial_condition": initial_check,
        "fraction_steps_saturated": saturated_steps / ctx.steps,
        "final_requested_max_violation": rows[-1]["requested_max_violation"],
        "final_requested_cv": rows[-1]["requested_cv"],
        "final_total_overflow": rows[-1]["total_overflow"],
        "final_all_experts_saturated": rows[-1]["all_experts_saturated"],
    }
    return rows, summary
