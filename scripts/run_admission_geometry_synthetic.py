#!/usr/bin/env python3
"""Paired synthetic experiment: admission geometry vs. count feedback.

This script is intentionally separate from ``moe_control.runner``. The latter
implements the canonical per-expert count rule A=min(R,C); this experiment
needs token identities and route scores to compare per-expert and grouped
score-ranked admission without changing that canonical implementation.

Run from the repository root:
    python scripts/run_admission_geometry_synthetic.py

The deterministic summary is written under ``results/admission_geometry``.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import torch


E = 8
K = 2
TOKENS = 128
STEPS = 120
BIAS_STEP = 0.025
SEEDS = tuple(range(20))
DEVICE_GROUPS = (tuple(range(4)), tuple(range(4, 8)))
EXPERT_CAPACITY = 24
MCORE_CAPACITY_FACTOR = 0.75  # ceil(T*K/E * factor) = 24 for this protocol
GROUP_CAPACITY = 112


@dataclass(frozen=True)
class Plant:
    affinities: torch.Tensor  # [tokens, experts], float64
    tokens: int
    experts: int


def build_plant(seed: int) -> Plant:
    """Build the same fixed Top-2 request plant for every paired arm.

    Tokens are assigned to adjacent expert pairs around a ring. Pair
    multiplicities are deliberately unequal, but every expert starts at or
    above the per-expert capacity 24. Small seeded perturbations break score
    ties without changing the initial requested pair.
    """
    edge_counts = (30, 8, 22, 10, 26, 6, 18, 8)
    assert sum(edge_counts) == TOKENS
    generator = torch.Generator().manual_seed(seed)
    affinities = torch.full((TOKENS, E), -2.0, dtype=torch.float64)
    row = 0
    for edge, count in enumerate(edge_counts):
        left, right = edge, (edge + 1) % E
        for _ in range(count):
            # Fixed, paired noise; each arm receives exactly the same matrix.
            noise = torch.rand(E, generator=generator, dtype=torch.float64) * 0.02
            affinities[row] += noise
            affinities[row, left] = 2.0 + noise[left]
            affinities[row, right] = 1.8 + noise[right]
            row += 1
    # Break the correlation between token position and the deliberately
    # ordered construction of the ring-edge multiplicities. Position-based
    # dropping remains deterministic, but its order is not aligned with a
    # particular expert pair by construction.
    permutation = torch.randperm(TOKENS, generator=generator)
    affinities = affinities[permutation]
    return Plant(affinities=affinities, tokens=TOKENS, experts=E)


def topk_routes(scores: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Stable Top-K routing; lower expert index wins an exact tie."""
    order = torch.argsort(scores, dim=1, descending=True, stable=True)
    routes = torch.zeros_like(scores, dtype=torch.bool)
    routes.scatter_(1, order[:, :K], True)
    return routes, order[:, :K]


def counts_from_routes(routes: torch.Tensor) -> torch.Tensor:
    return routes.sum(dim=0, dtype=torch.int64)


def admit_per_expert(
    routes: torch.Tensor,
    route_scores: torch.Tensor,
    rule: str,
) -> torch.Tensor:
    """Admit up to C routes independently for every expert."""
    admitted = torch.zeros_like(routes)
    for expert in range(E):
        token_ids = torch.where(routes[:, expert])[0]
        count = min(EXPERT_CAPACITY, int(token_ids.numel()))
        if rule == "score":
            order = torch.argsort(
                route_scores[token_ids, expert], descending=True, stable=True
            )
            keep = token_ids[order[:count]]
        elif rule == "position":
            keep = token_ids[:count]
        else:
            raise ValueError(f"unknown per-expert admission rule: {rule}")
        admitted[keep, expert] = True
    return admitted


def admit_by_device(
    routes: torch.Tensor,
    route_scores: torch.Tensor,
    rule: str,
) -> torch.Tensor:
    """Admit up to GROUP_CAPACITY routes per expert group/device."""
    admitted = torch.zeros_like(routes)
    for group in DEVICE_GROUPS:
        expert_ids = torch.tensor(group, dtype=torch.int64)
        token_ids, local_experts = torch.where(routes[:, expert_ids])
        count = min(GROUP_CAPACITY, int(token_ids.numel()))
        if rule == "score":
            scores = route_scores[token_ids, expert_ids[local_experts]]
            order = torch.argsort(scores, descending=True, stable=True)
        elif rule == "position":
            # Deterministic token-major, then expert-index ordering.
            keys = token_ids * E + expert_ids[local_experts]
            order = torch.argsort(keys, stable=True)
        else:
            raise ValueError(f"unknown device admission rule: {rule}")
        keep = order[:count]
        admitted[token_ids[keep], expert_ids[local_experts[keep]]] = True
    return admitted


def admit_none(routes: torch.Tensor) -> torch.Tensor:
    return routes.clone()


def feedback(counts: torch.Tensor, enabled: bool) -> torch.Tensor:
    """Aux-loss-free sign update: underloaded +1, overloaded -1."""
    if not enabled:
        return torch.zeros(E, dtype=torch.float64)
    centered = counts.to(torch.float64) - counts.to(torch.float64).mean()
    return torch.where(centered < 0, 1.0, torch.where(centered > 0, -1.0, 0.0))


def project_bias(bias: torch.Tensor) -> torch.Tensor:
    """Remove the unidentifiable common score shift."""
    return bias - bias.mean()


def run_arm(seed: int, admission: str, rule: str, sensor: str) -> list[dict]:
    plant = build_plant(seed)
    bias = torch.zeros(E, dtype=torch.float64)
    records: list[dict] = []

    for step in range(STEPS):
        score = plant.affinities + bias.unsqueeze(0)
        routes, _ = topk_routes(score)
        requested = counts_from_routes(routes)

        # Drop scores are the un-biased route affinities, matching the
        # separation between selection bias and combination probabilities.
        if admission == "per_expert":
            admitted_mask = admit_per_expert(routes, plant.affinities, rule)
        elif admission == "device":
            admitted_mask = admit_by_device(routes, plant.affinities, rule)
        elif admission == "none":
            admitted_mask = admit_none(routes)
        else:
            raise ValueError(f"unknown admission: {admission}")

        admitted = counts_from_routes(admitted_mask)
        observed = requested if sensor == "requested" else admitted
        update = feedback(observed, enabled=(sensor != "none"))
        bias = project_bias(bias + BIAS_STEP * update)

        records.append(
            {
                "seed": seed,
                "admission": admission,
                "drop_rule": rule,
                "sensor": sensor,
                "step": step,
                "requested": requested.tolist(),
                "admitted": admitted.tolist(),
                "overflow": int((requested - admitted).sum()),
                "feedback": update.tolist(),
                "bias": bias.tolist(),
                "bias_l2": float(torch.linalg.vector_norm(bias)),
                "bias_linf": float(bias.abs().max()),
                "request_l1_from_uniform": int(
                    (requested - requested.to(torch.float64).mean()).abs().sum()
                ),
                "admitted_l1_from_uniform": float(
                    (admitted - admitted.to(torch.float64).mean()).abs().sum()
                ),
            }
        )
    return records


def assert_exact_controls(records: dict[tuple, list[dict]]) -> None:
    """Verify mathematical controls, raising on any discrepancy."""
    # For the per-expert policy, score/position ordering changes route identity
    # only. Counts, feedback and bias trajectories must be identical.
    for sensor in ("requested", "admitted", "none"):
        score = records[("per_expert", "score", sensor)]
        position = records[("per_expert", "position", sensor)]
        for left, right in zip(score, position):
            for field in ("requested", "admitted", "feedback", "bias"):
                assert left[field] == right[field], (
                    f"per-expert order-invariance failed for {sensor=} "
                    f"at step {left['step']} field {field}"
                )

    # With no admission, R=A so both sensor arms must be identical.
    requested = records[("none", "position", "requested")]
    admitted = records[("none", "position", "admitted")]
    for left, right in zip(requested, admitted):
        assert left["requested"] == left["admitted"]
        for field in ("feedback", "bias"):
            assert left[field] == right[field], (
                f"dropless negative control failed at step {left['step']}"
            )

    # At the initial state all experts exceed C=24; uniform per-expert
    # admitted counts imply zero admitted sign feedback and no initial drift.
    initial = records[("per_expert", "score", "admitted")][0]
    assert all(n >= EXPERT_CAPACITY for n in initial["requested"])
    assert initial["admitted"] == [EXPERT_CAPACITY] * E
    assert initial["feedback"] == [0.0] * E
    assert initial["bias"] == [0.0] * E

    # Minimal Top-1-realizable shared-device example: requests stay fixed at
    # one route per expert, while changing only the within-device route scores
    # changes which expert receives the single shared admission slot.
    two_expert_routes = torch.tensor([[True, False], [False, True]])
    score_case_1 = torch.tensor([[2.0, 0.0], [0.0, 1.0]])
    score_case_2 = torch.tensor([[1.0, 0.0], [0.0, 2.0]])
    request_counts = counts_from_routes(two_expert_routes)
    assert request_counts.tolist() == [1, 1]

    def one_shared_slot(scores: torch.Tensor) -> torch.Tensor:
        admitted = torch.zeros_like(two_expert_routes)
        token_ids, expert_ids = torch.where(two_expert_routes)
        winner = torch.argmax(scores[token_ids, expert_ids])
        admitted[token_ids[winner], expert_ids[winner]] = True
        return admitted

    admitted_case_1 = counts_from_routes(one_shared_slot(score_case_1))
    admitted_case_2 = counts_from_routes(one_shared_slot(score_case_2))
    assert admitted_case_1.tolist() == [1, 0]
    assert admitted_case_2.tolist() == [0, 1]


def summarize(records: Iterable[dict]) -> list[dict]:
    grouped: dict[tuple, list[dict]] = {}
    for row in records:
        key = (row["admission"], row["drop_rule"], row["sensor"])
        grouped.setdefault(key, []).append(row)

    output: list[dict] = []
    for (admission, drop_rule, sensor), rows in sorted(grouped.items()):
        final_by_seed: dict[int, dict] = {}
        for row in rows:
            final_by_seed[row["seed"]] = row
        finals = list(final_by_seed.values())
        output.append(
            {
                "admission": admission,
                "drop_rule": drop_rule,
                "sensor": sensor,
                "seeds": len(finals),
                "mean_final_bias_l2": sum(r["bias_l2"] for r in finals) / len(finals),
                "max_final_bias_l2": max(r["bias_l2"] for r in finals),
                "mean_final_bias_linf": sum(r["bias_linf"] for r in finals) / len(finals),
                "mean_final_request_l1": sum(
                    r["request_l1_from_uniform"] for r in finals
                ) / len(finals),
                "mean_final_admitted_l1": sum(
                    r["admitted_l1_from_uniform"] for r in finals
                ) / len(finals),
                "mean_final_overflow": sum(r["overflow"] for r in finals) / len(finals),
            }
        )
    return output


def main() -> None:
    assert math.ceil(TOKENS * K / E * MCORE_CAPACITY_FACTOR) == EXPERT_CAPACITY
    arms = (
        ("per_expert", "score", "requested"),
        ("per_expert", "position", "requested"),
        ("per_expert", "score", "admitted"),
        ("per_expert", "position", "admitted"),
        ("per_expert", "score", "none"),
        ("per_expert", "position", "none"),
        ("device", "score", "requested"),
        ("device", "position", "requested"),
        ("device", "score", "admitted"),
        ("device", "position", "admitted"),
        ("device", "score", "none"),
        ("device", "position", "none"),
        ("none", "position", "requested"),
        ("none", "position", "admitted"),
    )
    records_by_arm: dict[tuple, list[dict]] = {}
    all_rows: list[dict] = []
    for admission, rule, sensor in arms:
        arm_rows: list[dict] = []
        for seed in SEEDS:
            arm_rows.extend(run_arm(seed, admission, rule, sensor))
        records_by_arm[(admission, rule, sensor)] = arm_rows
        all_rows.extend(arm_rows)

    assert_exact_controls(records_by_arm)
    report = {
        "protocol": {
            "experts": E,
            "top_k": K,
            "tokens": TOKENS,
            "steps": STEPS,
            "bias_step": BIAS_STEP,
            "seeds": list(SEEDS),
            "initial_ring_pair_multiplicities": [30, 8, 22, 10, 26, 6, 18, 8],
            "per_expert_capacity": EXPERT_CAPACITY,
            "per_expert_capacity_factor": MCORE_CAPACITY_FACTOR,
            "capacity_formula_note": (
                "matches Megatron-Core get_capacity: ceil(T*K/E * factor); "
                "does not model its full distributed training or probability scores"
            ),
            "device_groups": [list(g) for g in DEVICE_GROUPS],
            "device_group_capacity": GROUP_CAPACITY,
            "group_policy_note": (
                "synthetic group-capacity abstraction; not a reproduction of DeepSeek-V2"
            ),
            "drop_score_note": "raw affinity; selection bias affects routing only",
        },
        "exact_control_checks": {
            "per_expert_score_vs_position_counts_and_trajectories_equal": True,
            "dropless_requested_vs_admitted_trajectories_equal": True,
            "initial_uniform_per_expert_admitted_sign_feedback_zero": True,
            "shared_device_rank_change_changes_A_at_fixed_R": True,
        },
        "summary": summarize(all_rows),
    }

    out_dir = Path("results/admission_geometry")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    fields = [
        "seed", "admission", "drop_rule", "sensor", "step", "requested",
        "admitted", "overflow", "feedback", "bias", "bias_l2", "bias_linf",
        "request_l1_from_uniform", "admitted_l1_from_uniform",
    ]
    with (out_dir / "trajectories.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)
    print(json.dumps(report, indent=2))
    print(f"Artifacts written to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
