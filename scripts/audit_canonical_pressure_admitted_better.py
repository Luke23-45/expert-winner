from __future__ import annotations

import csv
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path


E, K, T, C, H = 3, 1, 3, 1, 12
GAMMA, ETA = F(1), F(4)
AFFINITIES = Path("docs/paper/fixtures/canonical_pressure_admitted_better.csv")


def load_affinities() -> list[list[F]]:
    with AFFINITIES.open(newline="", encoding="utf-8") as f:
        rows = [[F(value) for value in row] for row in csv.reader(f)]
    assert rows == [[F(0), F(0), F(1)], [F(0), F(0), F(1)], [F(0), F(1), F(0)]]
    return rows


def route(row: list[F], pressure: list[F]) -> tuple[list[int], F]:
    order = sorted(range(E), key=lambda e: (-(row[e] - GAMMA * pressure[e]), e))
    margin = (row[order[K - 1]] - GAMMA * pressure[order[K - 1]]) - (
        row[order[K]] - GAMMA * pressure[order[K]]
    )
    return order[:K], margin


def run(affinities: list[list[F]], sensor: str, eta: F, capacity: int = C) -> dict:
    pressure = [F(0)] * E
    counts_history, route_history, overflow, margins = [], [], [], []
    for _ in range(H):
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
        counts_history.append(requested)
        route_history.append(selected_routes)
        overflow.append(sum(requested) - sum(admitted))
        margins.append(min_margin)
    return {
        "counts": counts_history,
        "routes": route_history,
        "per_step_overflow": overflow,
        "cumulative_overflow": sum(overflow),
        "minimum_cutoff_margin": min(margins),
        "all_routes_strict": all(margin > 0 for margin in margins),
    }


def certify_eta_interval(
    affinities: list[list[F]], trajectory: dict, sensor: str, base_eta: F
) -> tuple[F, F | None, int]:
    """Exact interval retaining a complete route path around base_eta.

    In the pressure quotient and with delta=0, q_t(eta)=eta*v_t while the
    route path is fixed. Each selected-vs-unselected score inequality is
    affine in eta. Intersecting these inequalities gives the certificate.
    """
    lower, upper = F(0), None
    slope_state = [F(0)] * E
    comparisons = 0
    for counts, routes in zip(trajectory["counts"], trajectory["routes"]):
        for row, selected in zip(affinities, routes):
            selected_set = set(selected)
            for e in selected:
                for f in range(E):
                    if f in selected_set:
                        continue
                    intercept = row[e] - row[f]
                    slope = GAMMA * (slope_state[e] - slope_state[f])
                    assert intercept - base_eta * slope > 0
                    comparisons += 1
                    if slope > 0:
                        bound = intercept / slope
                        upper = bound if upper is None else min(upper, bound)
                    elif slope < 0:
                        lower = max(lower, intercept / slope)

        if sensor != "none":
            observed = counts if sensor == "requested" else [min(v, C) for v in counts]
            feedback = [F(value, K * T) - F(1, E) for value in observed]
            z = [slope_state[e] + GAMMA * feedback[e] for e in range(E)]
            mean = sum(z, F(0)) / E
            slope_state = [value - mean for value in z]
    if sensor == "none":
        assert upper is None and lower == 0
    else:
        assert lower < base_eta and (upper is None or base_eta < upper)
    return lower, upper, comparisons


def main() -> None:
    affinities = load_affinities()
    base = {sensor: run(affinities, sensor, ETA) for sensor in ("admitted", "requested", "none")}
    assert {sensor: row["cumulative_overflow"] for sensor, row in base.items()} == {
        "admitted": 18,
        "requested": 23,
        "none": 12,
    }
    assert all(row["all_routes_strict"] for row in base.values())
    assert min(row["minimum_cutoff_margin"] for row in base.values()) == F(1, 3)
    assert all(sum(counts) == K * T for row in base.values() for counts in row["counts"])

    intervals = {}
    for sensor in ("admitted", "requested", "none"):
        lower, upper, comparisons = certify_eta_interval(affinities, base[sensor], sensor, ETA)
        intervals[sensor] = {
            "lower_open": str(lower),
            "upper_open": str(upper) if upper is not None else "infinity",
            "selected_vs_unselected_inequalities": comparisons,
        }
    common_lower = max(F(intervals[sensor]["lower_open"]) for sensor in intervals)
    finite_uppers = [
        F(intervals[sensor]["upper_open"])
        for sensor in intervals
        if intervals[sensor]["upper_open"] != "infinity"
    ]
    common_upper = min(finite_uppers) if finite_uppers else None
    assert common_lower < ETA and (common_upper is None or ETA < common_upper)
    midpoint = (common_lower + common_upper) / 2 if common_upper is not None else common_lower + 1
    midpoint_checks = {}
    for sensor in base:
        candidate = run(affinities, sensor, midpoint)
        assert candidate["routes"] == base[sensor]["routes"]
        assert candidate["cumulative_overflow"] == base[sensor]["cumulative_overflow"]
        midpoint_checks[sensor] = True

    # Open affinity-neighborhood certificate: every selected/unselected score
    # gap changes by at most 2*epsilon, less than the exact 1/3 cutoff margin.
    epsilon = F(1, 10)
    assert 2 * epsilon < F(1, 3)
    perturbations = (
        [[v + F((t + e) % 3 - 1, 10) for e, v in enumerate(row)] for t, row in enumerate(affinities)],
        [[v + F((2 * t + e) % 3 - 1, 10) for e, v in enumerate(row)] for t, row in enumerate(affinities)],
    )
    for perturbed in perturbations:
        for sensor in ("admitted", "requested", "none"):
            candidate = run(perturbed, sensor, ETA)
            assert candidate["routes"] == base[sensor]["routes"]
            assert candidate["cumulative_overflow"] == base[sensor]["cumulative_overflow"]

    # Repeating every token m times and scaling capacities by m leaves each
    # normalized feedback vector and pressure path unchanged, while overflow
    # scales by m. Verify representative factors; the identity proves all m.
    replication = {}
    for m in (1, 2, 5, 10):
        replicated = [row for row in affinities for _ in range(m)]
        costs = {
            sensor: run(replicated, sensor, ETA, capacity=C * m)["cumulative_overflow"]
            for sensor in ("admitted", "requested", "none")
        }
        expected = {"admitted": 18 * m, "requested": 23 * m, "none": 12 * m}
        assert costs == expected
        replication[str(m)] = costs

    # Dropless exact control, checked over both the base and gain interval.
    for eta in (F(1, 2), ETA, midpoint):
        requested = run(affinities, "requested", eta, capacity=T)
        admitted = run(affinities, "admitted", eta, capacity=T)
        assert requested["routes"] == admitted["routes"]
        assert requested["counts"] == admitted["counts"]
        assert requested["cumulative_overflow"] == admitted["cumulative_overflow"] == 0

    fixture_hash = hashlib.sha256(AFFINITIES.read_bytes()).hexdigest()
    summary = {
        "status": "PASS",
        "arithmetic": "exact fractions.Fraction",
        "controller": "canonical proportional gauge-pressure update; delta=0; q_next=P_g(q+eta*gamma*(L/(K*T)-mu)); score=a-gamma*q",
        "plant": {
            "experts": E,
            "top_k": K,
            "tokens_per_batch": T,
            "uniform_capacity_per_expert": C,
            "horizon_batches": H,
            "gamma": str(GAMMA),
            "eta": str(ETA),
            "target": "uniform",
            "initial_pressure": [0] * E,
            "affinity_fixture": str(AFFINITIES).replace("\\", "/"),
            "affinity_sha256": fixture_hash,
            "tie_rule": "lower expert index wins exact ties",
        },
        "cumulative_overflow": {
            sensor: base[sensor]["cumulative_overflow"] for sensor in base
        },
        "per_step_overflow": {sensor: base[sensor]["per_step_overflow"] for sensor in base},
        "minimum_cutoff_margin": {
            sensor: str(base[sensor]["minimum_cutoff_margin"]) for sensor in base
        },
        "exact_common_eta_interval": {
            "lower_open": str(common_lower),
            "upper_open": str(common_upper) if common_upper is not None else "infinity",
            "midpoint": str(midpoint),
            "midpoint_routes_and_costs_match": midpoint_checks,
            "requested_minus_admitted_overflow": base["requested"]["cumulative_overflow"]
            - base["admitted"]["cumulative_overflow"],
        },
        "affinity_robustness": {
            "entrywise_epsilon": str(epsilon),
            "maximum_pairwise_gap_change": str(2 * epsilon),
            "minimum_cutoff_margin": "1/3",
            "strict_margin_proves_full_open_neighborhood": True,
            "exact_perturbation_matrices_checked": len(perturbations),
            "all_signals_preserved_paths_and_costs": True,
        },
        "row_replication": replication,
        "dropless_negative_control": "requested and admitted paths are exactly identical at each checked eta",
        "interpretation": "A strict admitted-better witness for the canonical proportional controller; combined with the separate strict requested-better uniform-capacity witness, it disproves universal signal dominance for this controller. It does not provide a predictive family criterion or benchmark separation.",
    }
    out = Path("results/bidirectional_bias_comparison/canonical_pressure_admitted_better.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
