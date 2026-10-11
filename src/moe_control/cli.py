"""Hydra CLI entry point for the control experiment.

Usage examples (run from the repository root)::

    python -m moe_control.cli scenario=shortage capacity=shortage controller=requested
    python -m moe_control.cli scenario=exact_total capacity=exact_total controller=admitted
    python -m moe_control.cli scenario=slack capacity=slack controller=capacity_relative
    python -m moe_control.cli scenario=demand_shift capacity=shortage controller=requested

Paired sweep over all four controllers on one scenario/capacity::

    python -m moe_control.cli scenario=shortage capacity=shortage \\
        controller=requested,admitted,admitted_centered,capacity_relative --multirun

Every execution writes a new immutable run directory under
``results/runs/<run_id>/``; existing runs are never overwritten.
"""

from __future__ import annotations

from pathlib import Path

import hydra
import torch
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf

from moe_control import artifacts
from moe_control.config import (
    RootConfig,
    resolve_capacity_vector,
    resolve_target,
    validate_config,
)
from moe_control.controllers import build_controller, gauge_equivalence_classes
from moe_control.reproducibility import enable_deterministic_mode, seed_all
from moe_control.runner import RunContext, run_experiment
from moe_control.scenarios import build_scenario

REPO_ROOT = Path(__file__).resolve().parents[2]


def _register_configs() -> None:
    # Register only the primary config schema. The config-group options
    # (scenario/*, capacity/*, controller/*, runtime/*) live as YAML files;
    # their schemas come from the typed fields of RootConfig. Registering
    # additional store entries for the same groups shadows the YAML options
    # during defaults-list resolution.
    cs = ConfigStore.instance()
    cs.store(name="config", node=RootConfig)


_register_configs()


@hydra.main(version_base=None, config_path="../../configs", config_name="config")
def main(cfg: RootConfig) -> None:
    print("Validating configuration...")
    warnings = validate_config(cfg)
    for w in warnings:
        print(f"WARNING: {w}")

    exp, prob, scen, cap, ctl, rt = (
        cfg.experiment, cfg.problem, cfg.scenario,
        cfg.capacity, cfg.controller, cfg.runtime,
    )

    if rt.deterministic:
        enable_deterministic_mode()
    seed_all(exp.seed)

    device = torch.device(rt.device)
    float_dtype = getattr(torch, rt.dtype)

    capacity_vec = torch.tensor(
        resolve_capacity_vector(cap, prob.experts), dtype=torch.int64
    )
    target = torch.tensor(resolve_target(prob), dtype=torch.float64)

    scenario = build_scenario(
        name=scen.name,
        kind=scen.kind,
        seed=scen.seed,
        tokens=prob.tokens,
        experts=prob.experts,
        group_sizes=list(scen.group_sizes),
        noise_scale=scen.noise_scale,
        affinity_dtype=scen.affinity_dtype,
        shift_step=scen.shift_step,
        shift_group_sizes=list(scen.shift_group_sizes) if scen.shift_group_sizes else None,
        spike_step=scen.spike_step,
        spike_end=scen.spike_end,
        spike_group_sizes=list(scen.spike_group_sizes) if scen.spike_group_sizes else None,
        dominant_expert=scen.dominant_expert,
        dominant_offset=scen.dominant_offset,
        burst_period=scen.burst_period,
        n_bursts=scen.n_bursts,
        preference_gap=scen.preference_gap,
        burst_noise_scale=scen.burst_noise_scale,
    )
    controller_kwargs = {}
    if ctl.name == "bias_integral":
        controller_kwargs["bias_gamma"] = ctl.bias_gamma
    controller = build_controller(ctl.name, **controller_kwargs)

    # The affinity batch is a pure function of the scenario seed and
    # parameters, so runs that share a scenario seed compare controllers on
    # the identical batch (paired comparison).
    run_id = artifacts.new_run_id(exp.name, scen.name, ctl.name)
    run_dir = artifacts.create_run_dir(exp.output_root, run_id)
    print(f"Run ID: {run_id}")

    ctx = RunContext(
        run_id=run_id,
        seed=exp.seed,
        scenario_name=scen.name,
        controller_name=ctl.name,
        capacity_regime=cap.name,
        steps=exp.steps,
        experts=prob.experts,
        top_k=prob.top_k,
        tokens=prob.tokens,
        gamma=(ctl.score_gain_override if ctl.score_gain_override is not None
               else prob.score_gain),
        score_sign=ctl.score_sign,
        eta=ctl.step_size,
        delta=ctl.pressure_decay,
        update_gain=(ctl.update_gain_override
                     if ctl.update_gain_override is not None
                     else (ctl.score_gain_override
                           if ctl.score_gain_override is not None
                           else prob.score_gain)),
        projection=ctl.projection,
        target=target,
        capacity=capacity_vec,
        initial_condition=scen.initial_condition,
        device=device,
        float_dtype=float_dtype,
    )
    print(
        f"Running {exp.steps} steps "
        f"(scenario={scen.name}, capacity={cap.name}, controller={ctl.name})..."
    )
    rows, summary = run_experiment(ctx, scenario, controller)

    capacity_uniform = cap.kind == "uniform"
    target_uniform = prob.target == "uniform"
    equivalence = gauge_equivalence_classes(capacity_uniform, target_uniform)
    controller_notes = []
    if ctl.name == "bias_integral":
        controller_notes.append(
            "bias_integral observes ADMITTED (post-capacity assigned) load, "
            "matching the deployed aux-loss-free system where dropped tokens "
            "are unobserved; bias_gamma=%.6g, sign update outside autograd, "
            "selection-only modulation (score_sign=+1)." % ctl.bias_gamma
        )
    if ctl.name in ("requested_leaky", "requested_no_projection"):
        controller_notes.append(
            "Ablation variant: identical requested feedback vector to "
            f"(requested); dynamics differ (pressure_decay={ctl.pressure_decay}, "
            f"projection={ctl.projection})."
        )
    if ctl.name == "admitted_antiwindup":
        controller_notes.append(
            "admitted_antiwindup: conditional-integration anti-windup on the "
            "admitted signal. Per-coordinate saturation is R_e >= C_e; "
            "saturated coordinates are frozen at the unsaturated mean before "
            "the zero-sum projection (their relative feedback is exactly 0), "
            "unsaturated coordinates integrate A_e/(K*T) - mu_e, and global "
            "saturation gives epsilon = 0 (full integrator freeze). Reduces "
            "to admitted feedback bit-identically on the gauge quotient when "
            "nothing is saturated."
        )
    manifest = artifacts.build_manifest(
        repo_root=REPO_ROOT,
        seed=exp.seed,
        scenario=scen.name,
        controller=ctl.name,
        capacity_regime=cap.name,
        protocol_version=exp.protocol_version,
        device=str(device),
        equivalence=equivalence,
        config_warnings=warnings,
    )
    if controller_notes:
        manifest["controller_notes"] = controller_notes
    resolved = OmegaConf.create(OmegaConf.to_container(cfg, resolve=True))
    artifacts.write_run(
        run_dir=run_dir,
        resolved_config=resolved,
        manifest=manifest,
        rows=rows,
        summary=summary,
        affinity_reference=scenario.reference(),
    )
    print(f"Wrote run artifacts to {run_dir}")
    print(
        "Summary: fraction_steps_saturated="
        f"{summary['fraction_steps_saturated']:.3f}, "
        f"final_requested_max_violation={summary['final_requested_max_violation']:.4f}, "
        f"final_total_overflow={summary['final_total_overflow']}"
    )


def entry() -> None:
    """Console-script entry point (``moe-control``)."""
    main()


if __name__ == "__main__":
    entry()
