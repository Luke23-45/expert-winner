"""Typed configuration schemas and pre-run validation.

The Hydra YAML files under ``configs/`` compose into these dataclasses.
Validation runs before any tensor is built, so invalid combinations fail
fast with a specific error instead of corrupting a run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


class ConfigValidationError(ValueError):
    """Raised when a composed experiment configuration is invalid."""


@dataclass
class ExperimentConfig:
    name: str = "saturation_signal_test"
    steps: int = 500
    seed: int = 17
    protocol_version: str = "0.1.0"
    output_root: str = "results/runs"


@dataclass
class ProblemConfig:
    experts: int = 8          # E
    top_k: int = 2            # K
    tokens: int = 1024        # T
    target: str = "uniform"   # "uniform" or "explicit"
    target_weights: Optional[List[float]] = None  # required when target == "explicit"
    score_gain: float = 1.0   # gamma, pressure gain in pressured scores


@dataclass
class ScenarioConfig:
    name: str = "shortage"
    kind: str = "synthetic"   # "synthetic" | "demand_shift"
    seed: int = 17
    # Synthetic affinity construction: token group g (of size group_sizes[g])
    # strongly prefers expert pair (2g, 2g+1). Requires E even and
    # len(group_sizes) == E // 2, sum(group_sizes) == T.
    group_sizes: List[int] = field(default_factory=lambda: [300, 270, 240, 214])
    noise_scale: float = 0.1
    affinity_dtype: str = "float32"
    # Demand shift: from this step onward (0-based) use shift_group_sizes.
    shift_step: Optional[int] = None
    shift_group_sizes: Optional[List[int]] = None
    # Declared initial condition, verified against realized counts at step 0:
    # "all_saturated" (every R_e >= C_e), "balanced" (R_e == K*T/E for all e),
    # "unconstrained" (record only, no requirement).
    initial_condition: str = "all_saturated"


@dataclass
class CapacityConfig:
    name: str = "shortage"
    kind: str = "uniform"     # "uniform" | "explicit"
    value: int = 192          # used when kind == "uniform"
    values: Optional[List[int]] = None  # used when kind == "explicit"
    policy: str = "canonical"  # canonical count admission: A_e = min(R_e, C_e)


@dataclass
class ControllerConfig:
    name: str = "requested"   # requested | admitted | admitted_centered | capacity_relative
    step_size: float = 0.05   # eta
    pressure_decay: float = 0.0  # delta in [0, 1)


@dataclass
class RuntimeConfig:
    device: str = "cpu"
    deterministic: bool = True
    dtype: str = "float32"    # float32 | float64


@dataclass
class ArtifactsConfig:
    save_token_masks: bool = False  # opt-in: persist full (T, E) routing masks per step


@dataclass
class RootConfig:
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)
    problem: ProblemConfig = field(default_factory=ProblemConfig)
    scenario: ScenarioConfig = field(default_factory=ScenarioConfig)
    capacity: CapacityConfig = field(default_factory=CapacityConfig)
    controller: ControllerConfig = field(default_factory=ControllerConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    artifacts: ArtifactsConfig = field(default_factory=ArtifactsConfig)


def resolve_target(problem: ProblemConfig):
    """Return the target distribution mu as a list of floats (sums to 1)."""
    if problem.target == "uniform":
        return [1.0 / problem.experts] * problem.experts
    if problem.target == "explicit":
        if problem.target_weights is None:
            raise ConfigValidationError(
                "problem.target is 'explicit' but problem.target_weights is not set."
            )
        return list(problem.target_weights)
    raise ConfigValidationError(
        f"Unknown problem.target {problem.target!r}; expected 'uniform' or 'explicit'."
    )


def resolve_capacity_vector(capacity: CapacityConfig, experts: int) -> List[int]:
    """Return the per-expert integer capacity vector of length E."""
    if capacity.kind == "uniform":
        return [int(capacity.value)] * experts
    if capacity.kind == "explicit":
        if capacity.values is None:
            raise ConfigValidationError(
                "capacity.kind is 'explicit' but capacity.values is not set."
            )
        return [int(v) for v in capacity.values]
    raise ConfigValidationError(
        f"Unknown capacity.kind {capacity.kind!r}; expected 'uniform' or 'explicit'."
    )


def validate_config(cfg: RootConfig) -> List[str]:
    """Validate the fully composed config. Returns non-fatal warnings.

    Raises ConfigValidationError on any hard violation. The checks follow
    the required list: 1 <= K <= E, T > 0, capacity vector length E,
    nonnegative integer capacities, mu on the simplex, scenario tensor
    dimensions compatible with the problem size.
    """
    warnings: List[str] = []
    p, c, s, ctl = cfg.problem, cfg.capacity, cfg.scenario, cfg.controller

    # Problem dimensions.
    if not (1 <= p.top_k <= p.experts):
        raise ConfigValidationError(
            f"Require 1 <= K <= E, got K={p.top_k}, E={p.experts}."
        )
    if p.tokens <= 0:
        raise ConfigValidationError(f"Require T > 0, got T={p.tokens}.")
    if p.score_gain <= 0:
        raise ConfigValidationError(
            f"Require score_gain (gamma) > 0, got {p.score_gain}."
        )
    if cfg.experiment.steps <= 0:
        raise ConfigValidationError(
            f"Require experiment.steps > 0, got {cfg.experiment.steps}."
        )

    # Target distribution on the simplex.
    mu = resolve_target(p)
    if len(mu) != p.experts:
        raise ConfigValidationError(
            f"Target length {len(mu)} does not match E={p.experts}."
        )
    if any(w < 0 for w in mu):
        raise ConfigValidationError("Target mu must be nonnegative.")
    if abs(sum(mu) - 1.0) > 1e-9:
        raise ConfigValidationError(
            f"Target mu must sum to 1, got sum={sum(mu)}."
        )
    for e, w in enumerate(mu):
        if w > 1.0 / p.top_k + 1e-12:
            warnings.append(
                f"mu[{e}]={w:.6f} exceeds the necessary Top-K feasibility bound "
                f"1/K={1.0 / p.top_k:.6f}; exact matching is impossible."
            )
    kt = p.top_k * p.tokens
    for e, w in enumerate(mu):
        if abs(kt * w - round(kt * w)) > 1e-6:
            warnings.append(
                f"K*T*mu[{e}]={kt * w:.4f} is not an integer; exact requested-load "
                "matching on this finite batch is impossible."
            )

    # Capacity vector.
    cap = resolve_capacity_vector(c, p.experts)
    if len(cap) != p.experts:
        raise ConfigValidationError(
            f"Capacity vector length {len(cap)} does not match E={p.experts}."
        )
    for e, v in enumerate(cap):
        if v < 0:
            raise ConfigValidationError(
                f"Capacity C[{e}]={v} is negative; capacities must be nonnegative integers."
            )
    if sum(cap) != kt:
        warnings.append(
            f"Aggregate capacity sum(C)={sum(cap)} != K*T={kt}. The capacity "
            "dual is then not gauge-invariant; the relative controller observes "
            "only the quotient component. Track aggregate shortage separately."
        )

    # Controller scalars.
    if ctl.step_size <= 0:
        raise ConfigValidationError(
            f"Require controller.step_size (eta) > 0, got {ctl.step_size}."
        )
    if not (0.0 <= ctl.pressure_decay < 1.0):
        raise ConfigValidationError(
            f"Require 0 <= pressure_decay (delta) < 1, got {ctl.pressure_decay}."
        )

    # Scenario tensor dimensions.
    if s.kind not in ("synthetic", "demand_shift"):
        raise ConfigValidationError(
            f"Unknown scenario.kind {s.kind!r}; expected 'synthetic' or 'demand_shift'."
        )
    if p.experts % 2 != 0:
        raise ConfigValidationError(
            "The synthetic group generator requires an even expert count "
            f"(pairs (2g, 2g+1)); got E={p.experts}."
        )
    n_groups = p.experts // 2
    if len(s.group_sizes) != n_groups:
        raise ConfigValidationError(
            f"len(group_sizes)={len(s.group_sizes)} does not match E/2={n_groups}."
        )
    if sum(s.group_sizes) != p.tokens:
        raise ConfigValidationError(
            f"sum(group_sizes)={sum(s.group_sizes)} does not match T={p.tokens}."
        )
    if any(g < 0 for g in s.group_sizes):
        raise ConfigValidationError("group_sizes must be nonnegative.")
    if s.kind == "demand_shift":
        if s.shift_step is None or s.shift_group_sizes is None:
            raise ConfigValidationError(
                "demand_shift scenario requires shift_step and shift_group_sizes."
            )
        if not (0 < s.shift_step < cfg.experiment.steps):
            raise ConfigValidationError(
                f"shift_step={s.shift_step} must satisfy 0 < shift_step < steps={cfg.experiment.steps}."
            )
        if len(s.shift_group_sizes) != n_groups:
            raise ConfigValidationError(
                "len(shift_group_sizes) does not match E/2."
            )
        if sum(s.shift_group_sizes) != p.tokens:
            raise ConfigValidationError(
                "sum(shift_group_sizes) does not match T."
            )
    if s.initial_condition not in ("all_saturated", "balanced", "unconstrained"):
        raise ConfigValidationError(
            f"Unknown initial_condition {s.initial_condition!r}."
        )
    if s.affinity_dtype not in ("float32", "float64"):
        raise ConfigValidationError(
            f"Unsupported affinity_dtype {s.affinity_dtype!r}."
        )
    if cfg.runtime.dtype not in ("float32", "float64"):
        raise ConfigValidationError(
            f"Unsupported runtime.dtype {cfg.runtime.dtype!r}."
        )

    return warnings
