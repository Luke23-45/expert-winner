"""Exact proof audit for a one-update admitted-feedback saturation delay."""

from __future__ import annotations

import json
from fractions import Fraction as F

from audit_admitted_noncyclicity import AFFINITIES


E, K = 3, 1
MU = (F(1, 3),) * E
CYCLE_START = (F(0), F(2), F(3))
SATURATED_ROUTES = (2, 2, 1)  # zero-based expert indices, one route per token
BALANCED_ROUTES = (2, 0, 1)

# Each state is q(eta) = base + eta*slope, with the required strict winners.
ROUTE_STATES = (
    ("initial", (F(0), F(2), F(3)), (F(0), F(0), F(0)), SATURATED_ROUTES),
    ("requested_after_1", (F(0), F(2), F(3)), (F(0), F(1, 3), F(2, 3)), SATURATED_ROUTES),
    ("requested_after_2", (F(0), F(2), F(3)), (F(0), F(2, 3), F(4, 3)), BALANCED_ROUTES),
    ("admitted_after_1", (F(0), F(2), F(3)), (F(0), F(1, 3), F(1, 3)), SATURATED_ROUTES),
    ("admitted_after_2", (F(0), F(2), F(3)), (F(0), F(2, 3), F(2, 3)), SATURATED_ROUTES),
    ("admitted_after_3", (F(0), F(2), F(3)), (F(0), F(1), F(1)), BALANCED_ROUTES),
)


def strict_step_size_interval():
    lower, upper = F(0), None
    lower_witness, upper_witness = None, None
    checked = 0
    for state_name, base, slope, winners in ROUTE_STATES:
        for token, affinity in enumerate(AFFINITIES):
            winner = winners[token]
            for competitor in range(E):
                if competitor == winner:
                    continue
                # Score(winner)-score(competitor) = intercept + slope*eta.
                intercept = (
                    affinity[winner] - base[winner]
                    - affinity[competitor] + base[competitor]
                )
                coefficient = -slope[winner] + slope[competitor]
                checked += 1
                if coefficient == 0:
                    assert intercept > 0, (state_name, token, competitor, intercept)
                elif coefficient > 0:
                    bound = -intercept / coefficient
                    if bound > lower:
                        lower, lower_witness = bound, (state_name, token, winner, competitor)
                else:
                    bound = -intercept / coefficient
                    if upper is None or bound < upper:
                        upper, upper_witness = bound, (state_name, token, winner, competitor)
    assert lower == F(7, 100)
    assert upper == F(21, 200)
    return lower, upper, lower_witness, upper_witness, checked


def route_counts(q, affinity_batch):
    requested = [0] * E
    for affinity in affinity_batch:
        scores = tuple(affinity[e] - q[e] for e in range(E))
        assert len(set(scores)) == E, "Trajectory witness must remain tie-free."
        winner = scores.index(max(scores))
        requested[winner] += 1
    return tuple(requested)


def simulate(replicas: int, signal: str, eta: F):
    total_tokens = 3 * replicas
    capacity = (replicas,) * E
    affinity_batch = AFFINITIES * replicas
    q = CYCLE_START
    states, route_vectors = [], []
    overflow = 0
    seen = set()
    for _ in range(8):
        if q in seen:
            break
        seen.add(q)
        requested = route_counts(q, affinity_batch)
        admitted = tuple(min(requested[e], capacity[e]) for e in range(E))
        load = requested if signal == "requested" else admitted
        route_vectors.append(requested)
        states.append([str(value) for value in q])
        overflow += sum(requested) - sum(admitted)
        z = tuple(q[e] + eta * (F(load[e], total_tokens) - MU[e]) for e in range(E))
        floor = min(z)
        q = tuple(value - floor for value in z)
    return {"states_before_repeat": states, "requested_counts": route_vectors,
            "overflow_until_fixed_or_cycle": overflow, "fixed_or_cycle_state": [str(v) for v in q]}


def main() -> None:
    lower, upper, lower_witness, upper_witness, checked = strict_step_size_interval()
    sample_eta = F(1, 10)
    assert lower < sample_eta < upper
    replications = []
    for m in (1, 2, 10):
        req = simulate(m, "requested", sample_eta)
        adm = simulate(m, "admitted", sample_eta)
        assert req["overflow_until_fixed_or_cycle"] == 2 * m
        assert adm["overflow_until_fixed_or_cycle"] == 3 * m
        replications.append({"replicas": m, "requested": req, "admitted": adm,
                             "extra_admitted_overflow": m})
    result = {
        "status": "PASS",
        "scope": "fixed E=3,K=1 Top-1 affinity family; exact rational proof audit",
        "strict_eta_interval": {"lower_exclusive": str(lower), "upper_exclusive": str(upper)},
        "active_lower_bound": {"state": lower_witness[0], "token_one_based": lower_witness[1] + 1,
                               "winner_one_based": lower_witness[2] + 1,
                               "competitor_one_based": lower_witness[3] + 1,
                               "margin": "eta - 7/100"},
        "active_upper_bound": {"state": upper_witness[0], "token_one_based": upper_witness[1] + 1,
                               "winner_one_based": upper_witness[2] + 1,
                               "competitor_one_based": upper_witness[3] + 1,
                               "margin": "7/100 - 2*eta/3"},
        "strict_score_inequalities_checked": checked,
        "replication_audits_at_eta_1_over_10": replications,
        "theorem": "For every eta in (7/100,21/200), requested feedback reaches zero-overflow balance in 2 saturated updates; admitted feedback takes 3. For every replica count m, cumulative overflow is 2m versus 3m.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
