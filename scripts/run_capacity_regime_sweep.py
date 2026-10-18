#!/usr/bin/env python3
"""Paired capacity-regime sweep for the canonical per-expert count model.

This is a fixed synthetic Top-2 router plant. It compares requested-count,
admitted-count, and no-feedback bias updates across four uniform capacities.
The score/position retention arms are an exact count-invariance control.

Run from the repository root:
    python scripts/run_capacity_regime_sweep.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path

import torch


E = 8
K = 2
TOKENS = 128
STEPS = 120
BIAS_STEP = 0.025
SEEDS = tuple(range(20))
CAPACITY_FACTORS = (0.75, 0.875, 1.0, 1.125)
CAPACITIES = tuple(math.ceil(TOKENS * K / E * x) for x in CAPACITY_FACTORS)
EDGE_COUNTS = (30, 8, 22, 10, 26, 6, 18, 8)
SNAPSHOTS = (0, 29, 59, 119)


def build_affinities(seed: int) -> torch.Tensor:
    """Use the same paired ring-pair plant as the earlier mechanism pilot."""
    assert sum(EDGE_COUNTS) == TOKENS
    generator = torch.Generator().manual_seed(seed)
    affinities = torch.full((TOKENS, E), -2.0, dtype=torch.float64)
    row = 0
    for edge, count in enumerate(EDGE_COUNTS):
        left, right = edge, (edge + 1) % E
        for _ in range(count):
            noise = torch.rand(E, generator=generator, dtype=torch.float64) * 0.02
            affinities[row] += noise
            affinities[row, left] = 2.0 + noise[left]
            affinities[row, right] = 1.8 + noise[right]
            row += 1
    return affinities[torch.randperm(TOKENS, generator=generator)]


def route(scores: torch.Tensor) -> torch.Tensor:
    order = torch.argsort(scores, dim=1, descending=True, stable=True)
    mask = torch.zeros_like(scores, dtype=torch.bool)
    mask.scatter_(1, order[:, :K], True)
    return mask


def admit(routes: torch.Tensor, raw_scores: torch.Tensor, capacity: int, rule: str) -> torch.Tensor:
    admitted = torch.zeros_like(routes)
    for expert in range(E):
        tokens = torch.where(routes[:, expert])[0]
        keep_count = min(int(tokens.numel()), capacity)
        if rule == "score":
            order = torch.argsort(raw_scores[tokens, expert], descending=True, stable=True)
            keep = tokens[order[:keep_count]]
        elif rule == "position":
            keep = tokens[:keep_count]
        else:
            raise ValueError(rule)
        admitted[keep, expert] = True
    return admitted


def sign_feedback(counts: torch.Tensor, sensor: str) -> torch.Tensor:
    if sensor == "none":
        return torch.zeros(E, dtype=torch.float64)
    counts = counts.to(torch.float64)
    centered = counts - counts.mean()
    return torch.where(centered < 0, 1.0, torch.where(centered > 0, -1.0, 0.0))


def project_bias(bias: torch.Tensor) -> torch.Tensor:
    return bias - bias.mean()


def run_arm(seed: int, capacity: int, rule: str, sensor: str) -> list[dict]:
    affinities = build_affinities(seed)
    bias = torch.zeros(E, dtype=torch.float64)
    rows: list[dict] = []
    previous_routes: torch.Tensor | None = None
    previous_bias: torch.Tensor | None = None
    previous_all_saturated = False
    first_flip: int | None = None
    first_all_saturated: int | None = None

    for step in range(STEPS):
        routes = route(affinities + bias.unsqueeze(0))
        if sensor == "admitted" and previous_all_saturated:
            assert previous_routes is not None and previous_bias is not None
            assert torch.equal(routes, previous_routes), (seed, capacity, rule, step, "absorbing routes")
            assert torch.equal(bias, previous_bias), (seed, capacity, rule, step, "absorbing bias")
        if previous_routes is not None and first_flip is None and not torch.equal(routes, previous_routes):
            first_flip = step
        previous_routes = routes.clone()
        requested = routes.sum(dim=0, dtype=torch.int64)
        all_saturated = bool(torch.all(requested >= capacity))
        if all_saturated and first_all_saturated is None:
            first_all_saturated = step
        admitted_mask = admit(routes, affinities, capacity, rule)
        admitted = admitted_mask.sum(dim=0, dtype=torch.int64)
        observed = requested if sensor == "requested" else admitted
        update = sign_feedback(observed, sensor)
        bias_before = bias.clone()
        bias = project_bias(bias + BIAS_STEP * update)

        # With a uniform per-expert cap, all experts saturated at this step
        # have the same A=C and therefore the same admitted-sign update. Their
        # pairwise bias gaps must be invariant for this update.
        if sensor == "admitted":
            saturated = torch.where(requested >= capacity)[0].tolist()
            for i, expert in enumerate(saturated):
                for other in saturated[i + 1:]:
                    before_gap = bias_before[expert] - bias_before[other]
                    after_gap = bias[expert] - bias[other]
                    assert torch.isclose(before_gap, after_gap, atol=1e-12, rtol=0), (
                        seed, capacity, step, expert, other, before_gap, after_gap
                    )

        assert int(requested.sum()) == TOKENS * K
        assert torch.equal(admitted, torch.minimum(requested, torch.full_like(requested, capacity)))
        assert int((requested - admitted).sum()) == int(requested.sum() - admitted.sum())
        rows.append({
            "seed": seed,
            "capacity": capacity,
            "capacity_factor": capacity / (TOKENS * K / E),
            "drop_rule": rule,
            "sensor": sensor,
            "step": step,
            "requested": requested.tolist(),
            "admitted": admitted.tolist(),
            "feedback": update.tolist(),
            "bias": bias.tolist(),
            "bias_l2": float(torch.linalg.vector_norm(bias)),
            "request_l1_uniform": int((requested - requested.to(torch.float64).mean()).abs().sum()),
            "admitted_l1_equalized": float((admitted - admitted.to(torch.float64).mean()).abs().sum()),
            "overflow": int((requested - admitted).sum()),
            "all_experts_saturated": bool(torch.all(requested >= capacity)),
            "saturated_expert_count": int(torch.sum(requested >= capacity)),
            "first_flip_step": first_flip,
            "first_all_saturated_step": first_all_saturated,
        })
        previous_all_saturated = all_saturated
        previous_bias = bias.clone()
    return rows


def verify_exact_controls(data: dict[tuple[int, str, str], list[dict]]) -> dict[str, bool]:
    for capacity in CAPACITIES:
        for sensor in ("requested", "admitted", "none"):
            score = data[(capacity, "score", sensor)]
            position = data[(capacity, "position", sensor)]
            for left, right in zip(score, position):
                for field in ("requested", "admitted", "feedback", "bias", "overflow"):
                    assert left[field] == right[field], (capacity, sensor, field, left["step"])

    full = data[(CAPACITIES[0], "score", "admitted")]
    assert all(row["all_experts_saturated"] for row in full)
    assert all(row["admitted"] == [CAPACITIES[0]] * E for row in full)
    assert all(row["feedback"] == [0.0] * E and row["bias"] == [0.0] * E for row in full)
    assert all(row["overflow"] == TOKENS * K - E * CAPACITIES[0] for row in full)

    for seed in SEEDS:
        requested = run_no_admission(seed, "requested")
        admitted = run_no_admission(seed, "admitted")
        for left, right in zip(requested, admitted):
            for field in ("requested", "admitted", "feedback", "bias"):
                assert left[field] == right[field], (seed, field, left["step"])

    return {
        "score_vs_position_per_expert_trajectories_identical_all_capacities": True,
        "full_saturation_admitted_controller_exactly_frozen": True,
        "admitted_global_saturation_absorbing_for_stationary_affinities": True,
        "admitted_controller_preserves_bias_gaps_within_saturated_set": True,
        "full_saturation_overflow_exactly_KT_minus_EC": True,
        "dropless_requested_vs_admitted_trajectories_identical": True,
        "all_steps_mass_and_admission_identities_checked": True,
    }


def run_no_admission(seed: int, sensor: str) -> list[dict]:
    affinities = build_affinities(seed)
    bias = torch.zeros(E, dtype=torch.float64)
    rows = []
    for step in range(STEPS):
        routes = route(affinities + bias.unsqueeze(0))
        requested = routes.sum(dim=0, dtype=torch.int64)
        admitted = requested.clone()
        observed = requested if sensor == "requested" else admitted
        update = sign_feedback(observed, sensor)
        bias = project_bias(bias + BIAS_STEP * update)
        rows.append({"step": step, "requested": requested.tolist(), "admitted": admitted.tolist(),
                     "feedback": update.tolist(), "bias": bias.tolist()})
    return rows


def summarize(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[int, str], list[dict]] = {}
    for row in rows:
        # Score/position runs are exactly paired and asserted equal above;
        # summarize one representative rule so each seed is counted once.
        if row["step"] == STEPS - 1 and row["drop_rule"] == "score":
            groups.setdefault((row["capacity"], row["sensor"]), []).append(row)
    out = []
    for (capacity, sensor), finals in sorted(groups.items()):
        out.append({
            "capacity": capacity,
            "capacity_factor": capacity / (TOKENS * K / E),
            "sensor": sensor,
            "seed_count": len(finals),
            "mean_final_request_l1": sum(r["request_l1_uniform"] for r in finals) / len(finals),
            "range_final_request_l1": [min(r["request_l1_uniform"] for r in finals), max(r["request_l1_uniform"] for r in finals)],
            "mean_final_admitted_l1": sum(r["admitted_l1_equalized"] for r in finals) / len(finals),
            "mean_final_overflow": sum(r["overflow"] for r in finals) / len(finals),
            "range_final_overflow": [min(r["overflow"] for r in finals), max(r["overflow"] for r in finals)],
            "mean_final_bias_l2": sum(r["bias_l2"] for r in finals) / len(finals),
            "all_seed_first_flip_steps": [r["first_flip_step"] for r in finals],
            "first_global_saturation_steps": [r["first_all_saturated_step"] for r in finals],
            "global_saturation_hit_count": sum(r["first_all_saturated_step"] is not None for r in finals),
            "mean_saturated_experts_at_horizon": sum(r["saturated_expert_count"] for r in finals) / len(finals),
        })
    return out


def main() -> None:
    arms: dict[tuple[int, str, str], list[dict]] = {}
    all_rows: list[dict] = []
    for capacity in CAPACITIES:
        for rule in ("score", "position"):
            for sensor in ("requested", "admitted", "none"):
                arm = [row for seed in SEEDS for row in run_arm(seed, capacity, rule, sensor)]
                arms[(capacity, rule, sensor)] = arm
                all_rows.extend(arm)

    checks = verify_exact_controls(arms)
    try:
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        worktree_dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        revision = "unavailable"
        worktree_dirty = None

    script_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    protocol_path = Path("docs/paper/admitted_feedback_capacity_sweep_protocol.md")
    protocol_sha256 = hashlib.sha256(protocol_path.read_bytes()).hexdigest()

    result = {
        "protocol": {
            "experts": E,
            "top_k": K,
            "tokens": TOKENS,
            "steps": STEPS,
            "bias_step": BIAS_STEP,
            "seeds": list(SEEDS),
            "edge_counts": list(EDGE_COUNTS),
            "capacity_factors": list(CAPACITY_FACTORS),
            "capacities": list(CAPACITIES),
            "drop_rules": ["score", "position"],
            "feedback": ["requested", "admitted", "none"],
            "generator": "paired ring-pair affinities with seeded U[0,0.02) perturbations",
            "tie_rule": "stable descending Top-2; lower expert index wins ties",
            "drop_score": "raw affinity; pressure affects routing selection only",
            "source_revision": revision,
            "worktree_dirty_at_run": worktree_dirty,
            "script_sha256": script_sha256,
            "protocol_sha256": protocol_sha256,
            "scope": "fixed synthetic plant; not trained-model or production evidence",
        },
        "exact_control_checks": checks,
        "final_horizon_summary": summarize(all_rows),
    }
    out = Path("results/capacity_regime_sweep")
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with (out / "trajectories.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)
    print(json.dumps(result, indent=2))
    print(f"Artifacts written to {out.resolve()}")


if __name__ == "__main__":
    main()
