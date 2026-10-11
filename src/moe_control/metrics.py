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


def overshoot(violations: list, baseline: float, start_idx: int) -> float:
    """Max post-event violation excess above a pre-event baseline.

    ``violations`` is the per-step violation time series, ``baseline`` the
    pre-event reference level (e.g. mean violation before a demand spike),
    ``start_idx`` the first post-event step. Returns
    max_{t >= start_idx}(violations[t] - baseline); negative when the
    violation never exceeds the baseline (no overshoot).
    """
    tail = violations[start_idx:]
    if not tail:
        raise ValueError("start_idx is beyond the violation series.")
    return max(v - baseline for v in tail)


def settling_time(
    violations: list, baseline: float, tolerance: float, start_idx: int
) -> int | None:
    """Steps after ``start_idx`` until the violation stays in tolerance.

    Returns the smallest d >= 0 such that |violations[t] - baseline| <=
    tolerance for every t in [start_idx + d, len(violations)). Returns None
    if the series never settles within the observed window. This is the
    standard control-theoretic settling-time definition, applied to the
    violation time series; it is descriptive, not a convergence proof.
    """
    n = len(violations)
    if not (0 <= start_idx < n):
        raise ValueError("start_idx out of range.")
    if tolerance < 0:
        raise ValueError("tolerance must be nonnegative.")
    # Walk backwards: find the last step outside the band; settling starts
    # right after it.
    last_outside = start_idx - 1
    for t in range(start_idx, n):
        if abs(violations[t] - baseline) > tolerance:
            last_outside = t
    if last_outside >= n - 1:
        return None
    return (last_outside + 1) - start_idx


def oscillation_count(
    violations: list, start_idx: int = 0, end_idx: int | None = None
) -> int:
    """Count sign changes of successive violation deltas in a window.

    A step t (start_idx + 1 < t < end_idx) counts as an oscillation when
    sign(v[t] - v[t-1]) != sign(v[t-1] - v[t-2]) with both deltas nonzero.
    Flat segments do not count. Descriptive only.
    """
    n = len(violations)
    end = n if end_idx is None else min(end_idx, n)
    count = 0
    for t in range(start_idx + 2, end):
        d1 = violations[t - 1] - violations[t - 2]
        d2 = violations[t] - violations[t - 1]
        if d1 == 0.0 or d2 == 0.0:
            continue
        if (d1 > 0) != (d2 > 0):
            count += 1
    return count


def specialization_mi(skill_labels: Tensor, top1_expert: Tensor) -> float:
    """Mutual information (nats) between skill label and top-1 expert.

    ``skill_labels`` and ``top1_expert`` are (T,) int64 tensors. The joint
    histogram over (skill, expert) gives MI = sum p(s,e) log(p(s,e)/(p(s)p(e))),
    with 0*log(0) treated as 0. A controller that balances load by smearing
    every skill across all experts drives this toward zero; one that keeps
    skill structure while rebalancing preserves it.
    """
    s = skill_labels.to(torch.int64).flatten()
    e = top1_expert.to(torch.int64).flatten()
    if s.shape != e.shape:
        raise ValueError("skill_labels and top1_expert must have equal length.")
    n_skills = int(s.max().item()) + 1
    n_experts = int(e.max().item()) + 1
    joint = torch.zeros(n_skills, n_experts, dtype=torch.float64)
    joint.index_put_(
        (s, e), torch.ones(s.shape[0], dtype=torch.float64), accumulate=True
    )
    joint = joint / s.shape[0]
    p_s = joint.sum(dim=1, keepdim=True)
    p_e = joint.sum(dim=0, keepdim=True)
    denom = p_s * p_e
    mask = joint > 0
    mi = (joint[mask] * (joint[mask] / denom[mask]).log()).sum()
    return mi.item()
