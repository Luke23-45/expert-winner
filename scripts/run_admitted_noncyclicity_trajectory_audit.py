"""Exact controlled trajectories for the non-cyclic admitted-field plant."""

from __future__ import annotations

import json
from fractions import Fraction as F

from audit_admitted_noncyclicity import AFFINITIES, POINTS


E, K, T = 3, 1, 3
CAPACITY = (1, 1, 1)
MU = (F(1, 3),) * E
HORIZON = 100
ETAS = (F(1, 10), F(1, 2), F(1), F(2))
EXPECTED_OVERFLOW = {
    F(1, 10): ((2, 17, 93, 63), (3, 33, 106, 99)),
    F(1, 2): ((100, 100, 19, 14), (1, 7, 39, 21)),
    F(1): ((100, 100, 101, 103), (144, 140, 141, 146)),
    F(2): ((100, 100, 101, 104), (147, 145, 146, 148)),
}


def counts(q: tuple[F, ...]):
    requested = [0] * E
    tie_tokens = 0
    for affinity in AFFINITIES:
        scores = tuple(affinity[e] - q[e] for e in range(E))
        top = max(scores)
        if scores.count(top) > 1:
            tie_tokens += 1
        # max returns the first expert on a tie, matching the formal lower-index rule.
        winner = max(range(E), key=lambda e: scores[e])
        requested[winner] += 1
    admitted = tuple(min(requested[e], CAPACITY[e]) for e in range(E))
    return tuple(requested), admitted, tie_tokens


def run(start: tuple[int, int], signal: str, eta: F):
    x, y = start
    shift = -min(x, y, 0)
    q = (F(x + shift), F(y + shift), F(shift))
    seen = {}
    cumulative_overflow = 0
    tie_token_steps = 0
    transient, period = None, None
    for t in range(HORIZON):
        if period is None:
            if q in seen:
                transient = seen[q]
                period = t - transient
            else:
                seen[q] = t
        requested, admitted, ties = counts(q)
        tie_token_steps += ties
        cumulative_overflow += sum(requested) - sum(admitted)
        load = requested if signal == "requested" else admitted
        z = tuple(q[e] + eta * (F(load[e], T) - MU[e]) for e in range(E))
        floor = min(z)
        q = tuple(value - floor for value in z)
    return {
        "signal": signal,
        "eta": str(eta),
        "start_quotient_point": list(start),
        "horizon_updates": HORIZON,
        "cumulative_overflow": cumulative_overflow,
        "exact_repeat_transient": transient,
        "exact_repeat_period": period,
        "distinct_states_before_repeat_or_horizon": len(seen),
        "tie_token_steps": tie_token_steps,
        "final_pressure": [str(value) for value in q],
    }


def main() -> None:
    output = []
    for eta in ETAS:
        for start_index, start in enumerate(POINTS):
            requested_result = run(start, "requested", eta)
            admitted_result = run(start, "admitted", eta)
            assert requested_result["cumulative_overflow"] == EXPECTED_OVERFLOW[eta][0][start_index]
            assert admitted_result["cumulative_overflow"] == EXPECTED_OVERFLOW[eta][1][start_index]
            assert requested_result["tie_token_steps"] == admitted_result["tie_token_steps"] == 0
            output.extend((requested_result, admitted_result))
    print(json.dumps({
        "scope": "deterministic exact finite-horizon trajectory audit; one fixed plant",
        "E": E, "K": K, "T": T, "capacity": list(CAPACITY),
        "mu": [str(value) for value in MU], "delta": "0",
        "eta_grid": [str(value) for value in ETAS],
        "horizon": HORIZON,
        "projection": "subtract coordinate minimum after each update",
        "tie_break": "lowest expert index",
        "results": output,
    }, indent=2))


if __name__ == "__main__":
    main()
