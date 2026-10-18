#!/usr/bin/env python3
"""Exact paired check of the canonical proportional admitted-pressure exit law.

Run from the exploration worktree root:
    python scripts/run_admitted_saturation_exit.py

All scores, capacities, controller states, and thresholds are rational; no
floating-point routing or tie ambiguity is used.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import subprocess
from fractions import Fraction
from pathlib import Path


E = 4
K = 2
TOKENS = 128
CAPACITY = (40, 42, 43, 44)
TARGET = tuple(Fraction(x, 10) for x in (4, 3, 2, 1))
ETA = Fraction(1, 10)
GAMMA = Fraction(1, 1)
DELTA = Fraction(0, 1)
EDGE_COUNTS = (40, 24, 32, 32)
SEEDS = tuple(range(20))
MIN_HORIZON = 120
CONTROLLERS = ("admitted", "requested", "none")


def p0(vector: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    mean = sum(vector, Fraction(0)) / len(vector)
    return tuple(value - mean for value in vector)


def gauge_project(vector: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    minimum = min(vector)
    return tuple(value - minimum for value in vector)


def make_affinities(seed: int) -> tuple[tuple[Fraction, ...], ...]:
    """Create paired Top-2 ring-pair scores with exact initial counts."""
    rng = random.Random(seed)
    rows: list[tuple[Fraction, ...]] = []
    for edge, count in enumerate(EDGE_COUNTS):
        left, right = edge, (edge + 1) % E
        for _ in range(count):
            row = [Fraction(rng.randrange(0, 5), 1000) for _ in range(E)]
            row[left] = Fraction(300 + rng.randrange(0, 5), 1000)
            row[right] = Fraction(280 + rng.randrange(0, 5), 1000)
            rows.append(tuple(row))
    rng.shuffle(rows)
    return tuple(rows)


def route_counts(
    affinities: tuple[tuple[Fraction, ...], ...],
    q: tuple[Fraction, ...],
) -> tuple[int, ...]:
    counts = [0] * E
    for selected in route_signature(affinities, q):
        for expert in selected:
            counts[expert] += 1
    return tuple(counts)


def route_signature(
    affinities: tuple[tuple[Fraction, ...], ...],
    q: tuple[Fraction, ...],
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(sorted(
            sorted(
                range(E),
                key=lambda e: (-(row[e] - GAMMA * q[e]), e),
            )[:K]
        ))
        for row in affinities
    )


def update_pressure(
    q: tuple[Fraction, ...], feedback: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    z = tuple(
        (1 - DELTA) * q[e] + ETA * GAMMA * feedback[e]
        for e in range(E)
    )
    return gauge_project(z)


def feedback_for(
    sensor: str,
    requested: tuple[int, ...],
    admitted: tuple[int, ...],
) -> tuple[Fraction, ...]:
    if sensor == "admitted":
        counts = admitted
    elif sensor == "requested":
        counts = requested
    elif sensor == "none":
        return (Fraction(0),) * E
    else:
        raise ValueError(sensor)
    kt = K * TOKENS
    return tuple(Fraction(counts[e], kt) - TARGET[e] for e in range(E))


def saturation_bound(
    affinities: tuple[tuple[Fraction, ...], ...],
    q0: tuple[Fraction, ...],
) -> tuple[int, tuple[int, ...], tuple[Fraction, ...], Fraction]:
    """Return N_sep, asymptotic Top-K set, phantom direction, slope gap."""
    kt = K * TOKENS
    h = tuple(Fraction(CAPACITY[e], kt) - TARGET[e] for e in range(E))
    v = p0(h)
    order = sorted(range(E), key=lambda e: (v[e], e))
    assert v[order[K - 1]] < v[order[K]], "strict K/(K+1) slope gap required"
    selected = tuple(order[:K])
    outside = tuple(order[K:])
    gap = v[order[K]] - v[order[K - 1]]
    alpha = ETA * GAMMA * GAMMA
    p_init = tuple(GAMMA * value for value in q0)
    thresholds: list[Fraction] = []
    for row in affinities:
        for i in selected:
            for j in outside:
                thresholds.append(
                    (p_init[i] - p_init[j] - (row[i] - row[j]))
                    / (alpha * (v[j] - v[i]))
                )
    n_sep = max(0, max(value.numerator // value.denominator + 1 for value in thresholds))
    return n_sep, selected, v, gap


def capacity_slack_exit_bound(
    affinities: tuple[tuple[Fraction, ...], ...],
    q0: tuple[Fraction, ...],
    v: tuple[Fraction, ...],
) -> tuple[int, int, int]:
    """Return T6b's capacity-aware exit bound, witness expert, and leave count.

    For an expert with maximal phantom slope, every other expert's score
    relative to it is nondecreasing along the saturated open-loop path. The
    bound is the order statistic of the token events needed to lose enough
    initial requests to fall below this expert's capacity.
    """
    e_star = max(range(E), key=lambda e: (v[e], -e))
    initial_routes = route_signature(affinities, q0)
    initial_count = sum(e_star in selected for selected in initial_routes)
    leave_count = initial_count - CAPACITY[e_star] + 1
    if leave_count <= 0:
        raise ValueError("The initial state must saturate the witness expert.")

    alpha = ETA * GAMMA * GAMMA
    token_leave_bounds: list[int] = []
    for token, selected in enumerate(initial_routes):
        if e_star not in selected:
            continue
        row = affinities[token]
        expert_thresholds: list[int | None] = []
        for j in range(E):
            if j == e_star:
                continue
            slope = alpha * (v[e_star] - v[j])
            if slope == 0:
                score_j = row[j] - GAMMA * q0[j]
                score_e = row[e_star] - GAMMA * q0[e_star]
                outranks_at_zero = score_j > score_e or (
                    score_j == score_e and j < e_star
                )
                expert_thresholds.append(0 if outranks_at_zero else None)
                continue

            theta = (
                GAMMA * q0[j]
                - GAMMA * q0[e_star]
                - (row[j] - row[e_star])
            ) / slope
            if j < e_star:  # lower index wins an exact score tie
                threshold = max(
                    0, -((-theta.numerator) // theta.denominator)
                )
            else:
                threshold = max(
                    0, theta.numerator // theta.denominator + 1
                )
            expert_thresholds.append(threshold)

        finite = sorted(value for value in expert_thresholds if value is not None)
        if len(finite) < K:
            raise ValueError("Strict slope gap must give K finite outranking events.")
        token_leave_bounds.append(finite[K - 1])

    return sorted(token_leave_bounds)[leave_count - 1], e_star, leave_count


def open_loop_pressure(
    q0: tuple[Fraction, ...],
    feedback: tuple[Fraction, ...],
    n: int,
) -> tuple[Fraction, ...]:
    """Gauge representative after n identical feedback updates."""
    z = tuple(q0[e] + n * ETA * GAMMA * feedback[e] for e in range(E))
    return gauge_project(z)


def run_arm(
    affinities: tuple[tuple[Fraction, ...], ...],
    controller: str,
    horizon: int,
) -> list[dict]:
    q = (Fraction(0),) * E
    rows: list[dict] = []
    initial_routes = route_signature(affinities, q)
    for step in range(horizon + 1):
        routes = route_signature(affinities, q)
        requested = tuple(
            sum(e in selected for selected in routes) for e in range(E)
        )
        admitted = tuple(min(requested[e], CAPACITY[e]) for e in range(E))
        rejected = tuple(requested[e] - admitted[e] for e in range(E))
        saturated = all(requested[e] >= CAPACITY[e] for e in range(E))
        rows.append(
            {
                "step": step,
                "controller": controller,
                "route_changed": routes != initial_routes,
                "q": q,
                "requested": requested,
                "admitted": admitted,
                "rejected": rejected,
                "saturated": saturated,
                "overflow": sum(rejected),
            }
        )
        if step < horizon:
            q = update_pressure(
                q, feedback_for(controller, requested, admitted)
            )
    return rows


def fraction_list(values: tuple[Fraction, ...]) -> list[str]:
    return [str(value) for value in values]


def main() -> None:
    records: list[dict] = []
    trajectories: list[dict] = []
    checks = {
        "initial_global_saturation_all_seeds": True,
        "theorem_strict_slope_gap_all_seeds": True,
        "predicted_exit_by_Nsep_all_seeds": True,
        "order_statistic_bound_finite_all_seeds": True,
        "admitted_exit_by_order_statistic_bound_all_seeds": True,
        "order_statistic_bound_le_Nsep_all_seeds": True,
        "order_statistic_bound_exact_in_registered_plant_all_seeds": True,
        "admitted_state_matches_open_loop_through_exit_all_seeds": True,
        "no_feedback_remains_frozen_and_saturated_all_seeds": True,
        "mass_and_clipping_identities_all_states": True,
    }

    for seed in SEEDS:
        affinities = make_affinities(seed)
        q0 = (Fraction(0),) * E
        n_sep, min_slope_set, v, slope_gap = saturation_bound(affinities, q0)
        n_order, e_star, leave_count = capacity_slack_exit_bound(
            affinities, q0, v
        )
        h = tuple(Fraction(CAPACITY[e], K * TOKENS) - TARGET[e] for e in range(E))
        horizon = max(MIN_HORIZON, n_sep + 10)
        arms = {
            name: run_arm(affinities, name, horizon) for name in CONTROLLERS
        }
        a_rows = arms["admitted"]
        first_exit = next(
            (row["step"] for row in a_rows if not row["saturated"]), None
        )
        predicted_exit = None
        for n in range(n_sep + 1):
            q_open = open_loop_pressure(q0, h, n)
            r_open = route_counts(affinities, q_open)
            if not all(r_open[e] >= CAPACITY[e] for e in range(E)):
                predicted_exit = n
                break

        initial_r = a_rows[0]["requested"]
        checks["initial_global_saturation_all_seeds"] &= all(
            initial_r[e] >= CAPACITY[e] for e in range(E)
        )
        checks["theorem_strict_slope_gap_all_seeds"] &= (
            min_slope_set == (0, 1) and slope_gap > 0 and all(CAPACITY[e] > 0 for e in range(E))
        )
        checks["predicted_exit_by_Nsep_all_seeds"] &= (
            predicted_exit is not None
            and first_exit == predicted_exit
            and first_exit <= n_sep
        )
        checks["order_statistic_bound_finite_all_seeds"] &= n_order is not None
        checks["admitted_exit_by_order_statistic_bound_all_seeds"] &= (
            first_exit is not None and first_exit <= n_order
        )
        checks["order_statistic_bound_le_Nsep_all_seeds"] &= n_order <= n_sep
        checks["order_statistic_bound_exact_in_registered_plant_all_seeds"] &= (
            first_exit == n_order
        )
        path_matches = first_exit is not None
        if first_exit is not None:
            for n in range(first_exit + 1):
                q_open = open_loop_pressure(q0, h, n)
                if a_rows[n]["q"] != q_open:
                    path_matches = False
                    break
        checks["admitted_state_matches_open_loop_through_exit_all_seeds"] &= path_matches

        none_rows = arms["none"]
        checks["no_feedback_remains_frozen_and_saturated_all_seeds"] &= all(
            row["q"] == q0 and row["saturated"] for row in none_rows
        )

        for controller, run_rows in arms.items():
            for row in run_rows:
                checks["mass_and_clipping_identities_all_states"] &= (
                    sum(row["requested"]) == K * TOKENS
                    and row["admitted"]
                    == tuple(min(row["requested"][e], CAPACITY[e]) for e in range(E))
                    and row["overflow"] == K * TOKENS - sum(row["admitted"])
                )
                trajectories.append(
                    {
                        "seed": seed,
                        "step": row["step"],
                        "controller": controller,
                        "route_changed": row["route_changed"],
                        "pressure": json.dumps(fraction_list(row["q"])),
                        "requested": json.dumps(list(row["requested"])),
                        "admitted": json.dumps(list(row["admitted"])),
                        "rejected": json.dumps(list(row["rejected"])),
                        "global_saturation": row["saturated"],
                        "overflow": row["overflow"],
                    }
                )

        records.append(
            {
                "seed": seed,
                "initial_requested": list(initial_r),
                "minimum_slope_experts": list(min_slope_set),
                "phantom_direction": fraction_list(v),
                "strict_slope_gap": str(slope_gap),
                "N_sep": n_sep,
                "max_slope_expert": e_star,
                "initial_requests_to_max_slope_expert": initial_r[e_star],
                "departures_needed_to_fall_below_capacity": leave_count,
                "capacity_slack_exit_bound": n_order,
                "predicted_first_exit": predicted_exit,
                "admitted_first_exit": first_exit,
                "requested_first_exit": next(
                    (r["step"] for r in arms["requested"] if not r["saturated"]), None
                ),
                "admitted_first_route_change": next(
                    (r["step"] for r in a_rows if r["route_changed"]), None
                ),
                "no_feedback_first_exit": next(
                    (r["step"] for r in none_rows if not r["saturated"]), None
                ),
                "admitted_exit_overflow": (
                    a_rows[first_exit]["overflow"] if first_exit is not None else None
                ),
            }
        )

    script_path = Path(__file__).resolve()
    protocol_path = Path("docs/paper/admitted_phantom_exit_protocol_2026-10-17.md")
    summary = {
        "protocol": {
            "experts": E,
            "top_k": K,
            "tokens": TOKENS,
            "capacities": list(CAPACITY),
            "target": fraction_list(TARGET),
            "eta": str(ETA),
            "gamma": str(GAMMA),
            "delta": str(DELTA),
            "edge_pair_multiplicities": list(EDGE_COUNTS),
            "seeds": list(SEEDS),
            "controllers": list(CONTROLLERS),
            "route_scores_and_state_are_exact_fractions": True,
            "protocol_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            "script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
            "base_revision": subprocess.run(
                ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
            ).stdout.strip(),
        },
        "theorem": "T6a global N_sep bound; T6b capacity-slack order-statistic refinement",
        "exact_checks": checks,
        "per_seed": records,
        "summary": {
            "seeds": len(records),
            "N_sep_min": min(row["N_sep"] for row in records),
            "N_sep_max": max(row["N_sep"] for row in records),
            "capacity_slack_bound_min": min(
                row["capacity_slack_exit_bound"] for row in records
            ),
            "capacity_slack_bound_max": max(
                row["capacity_slack_exit_bound"] for row in records
            ),
            "admitted_exit_min": min(row["admitted_first_exit"] for row in records),
            "admitted_exit_max": max(row["admitted_first_exit"] for row in records),
            "admitted_exit_equals_exact_open_loop_prediction_all_seeds": checks[
                "predicted_exit_by_Nsep_all_seeds"
            ],
            "capacity_slack_bound_equals_observed_exit_all_seeds": checks[
                "order_statistic_bound_exact_in_registered_plant_all_seeds"
            ],
        },
    }

    out_dir = Path("results/admitted_saturation_exit")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    with (out_dir / "trajectories.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(trajectories[0]))
        writer.writeheader()
        writer.writerows(trajectories)
    print(json.dumps(summary["summary"], indent=2))
    print(json.dumps(checks, indent=2))
    if not all(checks.values()):
        raise SystemExit("One or more exact controls failed; inspect summary.json.")


if __name__ == "__main__":
    main()
