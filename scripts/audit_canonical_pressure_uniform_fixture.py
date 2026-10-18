from __future__ import annotations

import csv
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path


E, K, T, CAPACITY, HORIZON = 8, 2, 128, 32, 120
GAMMA = F(1)
ETAS = (F(1, 100), F(1, 10), F(1, 2), F(1))
FIXTURE = Path("docs/paper/fixtures/uniform_capacity_seed5_affinities.csv")


def load_affinities() -> list[list[F]]:
    with FIXTURE.open(newline="", encoding="utf-8") as f:
        rows = [[F(value) for value in row] for row in csv.reader(f)]
    assert len(rows) == T and all(len(row) == E for row in rows)
    return rows


def route(row: list[F], pressure: list[F]) -> tuple[list[int], F]:
    order = sorted(range(E), key=lambda e: (-(row[e] - GAMMA * pressure[e]), e))
    margin = (row[order[K - 1]] - GAMMA * pressure[order[K - 1]]) - (
        row[order[K]] - GAMMA * pressure[order[K]]
    )
    return order[:K], margin


def run(affinities: list[list[F]], sensor: str, eta: F, capacity: int = CAPACITY) -> dict:
    pressure = [F(0)] * E
    overflow = []
    route_counts = []
    route_history = []
    margins = []
    pressure_linf = []
    globally_saturated_steps = []
    for step in range(HORIZON):
        requested = [0] * E
        selected_routes = []
        min_margin = None
        for row in affinities:
            selected, margin = route(row, pressure)
            selected_routes.append(selected)
            for expert in selected:
                requested[expert] += 1
            min_margin = margin if min_margin is None else min(min_margin, margin)
        admitted = [min(value, capacity) for value in requested]
        observed = {
            "requested": requested,
            "admitted": admitted,
            "none": None,
        }[sensor]
        if observed is not None:
            feedback = [F(value, K * T) - F(1, E) for value in observed]
            z = [pressure[e] + eta * GAMMA * feedback[e] for e in range(E)]
            minimum = min(z)
            pressure = [value - minimum for value in z]
        route_counts.append(requested)
        route_history.append(selected_routes)
        overflow.append(sum(requested) - sum(admitted))
        margins.append(min_margin)
        pressure_linf.append(max(pressure))
        if all(value >= capacity for value in requested):
            globally_saturated_steps.append(step)
    return {
        "cumulative_overflow": sum(overflow),
        "per_step_overflow": overflow,
        "first_requested": route_counts[0],
        "min_cutoff_margin": min(margins),
        "all_routes_strict": all(margin > 0 for margin in margins),
        "first_global_saturation_step": globally_saturated_steps[0]
        if globally_saturated_steps
        else None,
        "globally_saturated_step_count": len(globally_saturated_steps),
        "final_pressure_linf": pressure_linf[-1],
        "route_counts": route_counts,
        "route_history": route_history,
    }


def certify_positive_eta_interval(
    affinities: list[list[F]], trajectory: dict, sensor: str, capacity: int = CAPACITY
) -> tuple[F, F | None, int]:
    """Certify the exact open eta interval preserving this trajectory.

    Work in the zero-mean representative of the pressure quotient. With
    delta=0 and q_0=0, q_t(eta)=eta*v_t as long as the route sequence is fixed.
    Every selected-vs-unselected Top-K inequality is affine in eta, so their
    intersection is an exact open interval.
    """
    lower, upper = F(0), None
    slope_state = [F(0)] * E
    constraints = 0
    for requested, selected_per_token in zip(
        trajectory["route_counts"], trajectory["route_history"]
    ):
        for row, selected in zip(affinities, selected_per_token):
            selected_set = set(selected)
            for e in selected:
                for f in range(E):
                    if f in selected_set:
                        continue
                    intercept = row[e] - row[f]
                    slope = GAMMA * (slope_state[e] - slope_state[f])
                    assert intercept - slope > 0, "base eta=1 path is not strict"
                    constraints += 1
                    if slope > 0:
                        bound = intercept / slope
                        upper = bound if upper is None else min(upper, bound)
                    elif slope < 0:
                        lower = max(lower, intercept / slope)

        admitted = [min(value, capacity) for value in requested]
        observed = {
            "requested": requested,
            "admitted": admitted,
            "none": None,
        }[sensor]
        if observed is not None:
            feedback = [F(value, K * T) - F(1, E) for value in observed]
            z = [slope_state[e] + GAMMA * feedback[e] for e in range(E)]
            mean = sum(z, F(0)) / E
            slope_state = [value - mean for value in z]
    if sensor == "none":
        assert upper is None and lower == 0
        return lower, None, constraints
    assert upper is not None and lower < F(1) < upper
    return lower, upper, constraints


def main() -> None:
    affinities = load_affinities()
    rows = {}
    for eta in ETAS:
        key = str(eta)
        rows[key] = {
            sensor: run(affinities, sensor, eta)
            for sensor in ("admitted", "requested", "none")
        }
        assert all(result["all_routes_strict"] for result in rows[key].values())

    stability = {}
    for sensor in ("admitted", "requested", "none"):
        lower, upper, count = certify_positive_eta_interval(
            affinities, rows["1"][sensor], sensor
        )
        stability[sensor] = {
            "lower_open": str(lower),
            "upper_open": str(upper) if upper is not None else "infinity",
            "selected_vs_unselected_inequalities": count,
        }
    common_lower = max(F(stability[s]["lower_open"]) for s in stability)
    finite_uppers = [
        F(stability[s]["upper_open"])
        for s in stability
        if stability[s]["upper_open"] != "infinity"
    ]
    common_upper = min(finite_uppers) if finite_uppers else None
    assert common_lower < 1 and (common_upper is None or 1 < common_upper)
    midpoint = (common_lower + common_upper) / 2 if common_upper is not None else common_lower + 1
    midpoint_checks = {}
    for sensor in ("admitted", "requested", "none"):
        at_midpoint = run(affinities, sensor, midpoint)
        base = rows["1"][sensor]
        assert at_midpoint["route_history"] == base["route_history"]
        assert at_midpoint["cumulative_overflow"] == base["cumulative_overflow"]
        midpoint_checks[sensor] = True

    epsilon = F(1, 1_000_000)
    controlled_margin = min(
        rows["1"][sensor]["min_cutoff_margin"] for sensor in ("admitted", "requested")
    )
    assert 2 * epsilon < controlled_margin
    affinity_perturbations = (
        [[value + (epsilon if (t + e) % 2 else -epsilon) for e, value in enumerate(row)]
         for t, row in enumerate(affinities)],
        [[value + (epsilon if (2 * t + e) % 3 == 0 else F(0)) for e, value in enumerate(row)]
         for t, row in enumerate(affinities)],
    )
    perturbation_checks = 0
    for perturbed in affinity_perturbations:
        for sensor in ("admitted", "requested", "none"):
            candidate = run(perturbed, sensor, F(1))
            assert candidate["route_history"] == rows["1"][sensor]["route_history"]
            assert candidate["cumulative_overflow"] == rows["1"][sensor]["cumulative_overflow"]
            perturbation_checks += 1

    # Exact negative control: with capacity above every possible expert load,
    # A=R at every state, so the two signal-conditioned pressure paths coincide.
    no_clipping = {}
    for eta in ETAS:
        r = run(affinities, "requested", eta, capacity=T)
        a = run(affinities, "admitted", eta, capacity=T)
        assert r["route_counts"] == a["route_counts"]
        assert r["cumulative_overflow"] == a["cumulative_overflow"] == 0
        no_clipping[str(eta)] = {
            "requested_and_admitted_paths_identical": True,
            "overflow_both_zero": True,
        }

    compact = {
        eta: {
            sensor: {
                key: str(value) if isinstance(value, F) else value
                for key, value in result.items()
                if key not in ("route_counts", "route_history", "per_step_overflow")
            }
            for sensor, result in by_sensor.items()
        }
        for eta, by_sensor in rows.items()
    }
    output_dir = Path("results/bidirectional_bias_comparison")
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "status": "PASS",
        "arithmetic": "exact fractions.Fraction",
        "controller": "formal.md proportional gauge-pressure update; delta=0; q_next=P_g(q+eta*gamma*(L/(K*T)-mu)); score=a-gamma*q",
        "plant": {
            "experts": E,
            "top_k": K,
            "tokens": T,
            "per_expert_capacity": CAPACITY,
            "horizon": HORIZON,
            "gamma": str(GAMMA),
            "eta_grid": [str(eta) for eta in ETAS],
            "target": "uniform",
            "affinity_fixture": str(FIXTURE).replace("\\", "/"),
            "affinity_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "tie_rule": "lower expert index wins exact score ties",
        },
        "paired_results": compact,
        "exact_route_stability_interval_around_eta_1": stability,
        "common_open_interval_preserving_all_three_eta_1_paths": {
            "lower_open": str(common_lower),
            "upper_open": str(common_upper) if common_upper is not None else "infinity",
            "exact_midpoint_checked": str(midpoint),
            "midpoint_paths_and_costs_match_eta_1": midpoint_checks,
            "requested_minus_admitted_overflow": rows["1"]["requested"]["cumulative_overflow"]
            - rows["1"]["admitted"]["cumulative_overflow"],
        },
        "affinity_robustness_at_eta_1": {
            "entrywise_epsilon": str(epsilon),
            "maximum_pairwise_gap_change": str(2 * epsilon),
            "minimum_controlled_cutoff_margin": str(controlled_margin),
            "strict_margin_proves_open_affinity_neighborhood": True,
            "exact_perturbed_controller_cells_checked": perturbation_checks,
            "all_checked_paths_and_costs_preserved": True,
        },
        "exact_controls": {
            "dropless_requested_admitted_paths_equal_for_every_eta": True,
            "all_routes_strict_for_all_reported_controller_eta_pairs": True,
        },
        "no_clipping_control": no_clipping,
        "interpretation": "A finite exact sensitivity audit on one fixed plant; it does not imply a universal controller ranking or a Top-K-specific benchmark separation.",
    }
    path = output_dir / "canonical_pressure_uniform_fixture.json"
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
