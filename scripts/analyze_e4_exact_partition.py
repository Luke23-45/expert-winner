"""Exact Fourier-Motzkin audit of the E=4, K=1 pressure partition.

Enumerates all 4**6 assignments of winners to the three low-margin token
types and three high-margin token types. Feasibility uses rational
Fourier-Motzkin elimination with strict inequalities for tie-priority
comparisons. The script then derives admitted vectors and overflow costs for
the three static worlds and summarizes one-round information costs.

This is a reproducible finite-case audit. A paper proof should still state
the score inequalities and explain the finite reduction; script output is
not a substitute for that proof.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import gcd, lcm

F = Fraction
N_REGULAR = 3
N_EXPERTS = 4
C = 50
E_S = 20
C_SINK = 30
CAPACITY = (C, C, C, C_SINK)

# Score intercepts for L_1,L_2,L_3,H_1,H_2,H_3. The pressure-dependent
# coefficients are expert score = affinity - x_e; sink score is zero.
TOKEN_INTERCEPTS = []
for expert in range(N_REGULAR):
    low = [-3, -3, -3, 0]
    low[expert] = 1
    TOKEN_INTERCEPTS.append(tuple(map(F, low)))
for expert in range(N_REGULAR):
    high = [-3, -3, -3, 0]
    high[expert] = 3
    TOKEN_INTERCEPTS.append(tuple(map(F, high)))

SCORE_COEFFICIENTS = (
    (F(-1), F(0), F(0)),
    (F(0), F(-1), F(0)),
    (F(0), F(0), F(-1)),
    (F(0), F(0), F(0)),
)


def _normalize(rows):
    """Deduplicate inequalities a*x >= b, preserving strictness exactly."""
    strongest = {}
    for coefficients, rhs, strict in rows:
        values = (*coefficients, rhs)
        denominator = 1
        for value in values:
            denominator = lcm(denominator, value.denominator)
        integers = [int(value * denominator) for value in values]
        divisor = 0
        for value in integers:
            divisor = gcd(divisor, abs(value))
        if divisor:
            integers = [value // divisor for value in integers]
        key = tuple(F(value) for value in integers[:-1])
        bound = F(integers[-1])
        previous = strongest.get(key)
        if previous is None or bound > previous[0]:
            strongest[key] = (bound, strict)
        elif bound == previous[0]:
            strongest[key] = (bound, previous[1] or strict)
    return [(a, b, strict) for a, (b, strict) in strongest.items()]


def _feasible(rows, dimension=N_REGULAR):
    """Decide a rational strict/non-strict linear system by exact elimination."""
    rows = _normalize(rows)
    for _ in range(dimension):
        positive = [row for row in rows if row[0][0] > 0]
        negative = [row for row in rows if row[0][0] < 0]
        reduced = [
            (coefficients[1:], rhs, strict)
            for coefficients, rhs, strict in rows
            if coefficients[0] == 0
        ]
        for a_pos, b_pos, strict_pos in positive:
            for a_neg, b_neg, strict_neg in negative:
                # (-a_neg[0])*positive + a_pos[0]*negative cancels x_0.
                coefficients = tuple(
                    (-a_neg[0]) * a_pos[j] + a_pos[0] * a_neg[j]
                    for j in range(1, len(a_pos))
                )
                rhs = (-a_neg[0]) * b_pos + a_pos[0] * b_neg
                reduced.append((coefficients, rhs, strict_pos or strict_neg))
        rows = _normalize(reduced)
    return all(not (rhs > 0 or (rhs == 0 and strict)) for _, rhs, strict in rows)


def _winner_constraints(winners):
    """Build exact score inequalities for one joint winner assignment."""
    constraints = []
    for token, winner in enumerate(winners):
        intercepts = TOKEN_INTERCEPTS[token]
        for competitor in range(N_EXPERTS):
            if competitor == winner:
                continue
            coefficients = tuple(
                SCORE_COEFFICIENTS[winner][j]
                - SCORE_COEFFICIENTS[competitor][j]
                for j in range(N_REGULAR)
            )
            # score_winner - score_competitor >= 0
            rhs = intercepts[competitor] - intercepts[winner]
            # A lower-index competitor wins an equality, so this comparison
            # must be strict exactly when competitor < winner.
            constraints.append((coefficients, rhs, competitor < winner))
    return constraints


def _world_observations(winners):
    observations, costs = [], []
    for world in range(N_REGULAR):
        requests = [0] * N_EXPERTS
        requests[winners[N_REGULAR + world]] += C  # H_world baseline block
        for expert in range(N_REGULAR):
            if expert != world:
                requests[winners[expert]] += C  # L_expert baseline block
        requests[winners[world]] += E_S  # extra L_world block
        admitted = tuple(min(load, cap) for load, cap in zip(requests, CAPACITY))
        observations.append(admitted)
        costs.append(sum(requests) - sum(admitted))
    return tuple(observations), tuple(costs)


def _summary(maps, support):
    values = []
    informative_values = []
    for observations, costs in maps:
        value = F(sum(costs[i] for i in support), len(support))
        values.append(value)
        if len({observations[i] for i in support}) > 1:
            informative_values.append(value)
    return {
        "minimum_expected_cost": min(values),
        "minimum_informative_expected_cost": (
            min(informative_values) if informative_values else None
        ),
    }


def _partition(observations):
    labels = {}
    result = []
    for observation in observations:
        if observation not in labels:
            labels[observation] = len(labels)
        result.append(labels[observation])
    return tuple(result)


def _bellman_two_stage_relaxed(maps):
    """One full-prior Bellman step with an unrestricted next-pressure move."""
    support = tuple(range(N_REGULAR))
    one_stage_values = {
        subset: min(
            F(sum(costs[i] for i in subset), len(subset))
            for _, costs in maps
        )
        for size in (1, 2, 3)
        for subset in combinations(range(N_REGULAR), size)
    }
    candidates = []
    for observations, costs in maps:
        groups = {}
        for world, observation in enumerate(observations):
            groups.setdefault(observation, []).append(world)
        immediate = F(sum(costs), len(support))
        continuation = sum(
            F(len(group), len(support))
            * one_stage_values[tuple(group)]
            for group in groups.values()
        )
        candidates.append((immediate + continuation, observations, costs))
    return one_stage_values, min(candidates)


def main():
    feasible_assignments = []
    maps = set()
    for winners in product(range(N_EXPERTS), repeat=len(TOKEN_INTERCEPTS)):
        if not _feasible(_winner_constraints(winners)):
            continue
        feasible_assignments.append(winners)
        maps.add(_world_observations(winners))

    all_worlds = tuple(range(N_REGULAR))
    pair_summaries = {
        "".join(str(i + 1) for i in pair): _summary(maps, pair)
        for pair in combinations(all_worlds, 2)
    }
    zero_cost_world_counts = Counter(
        sum(cost == 0 for cost in costs) for _, costs in maps
    )
    triplets = sorted({costs for _, costs in maps})
    partition_costs = {}
    for observations, costs in maps:
        key = _partition(observations)
        partition_costs.setdefault(key, []).append(F(sum(costs), N_REGULAR))
    one_stage_values, two_stage = _bellman_two_stage_relaxed(maps)
    print(f"feasible_joint_winner_assignments={len(feasible_assignments)}")
    print(f"distinct_joint_observation_cost_maps={len(maps)}")
    print(
        "partition_minimum_immediate_cost={"
        + ", ".join(
            f"{key}:{min(values)}"
            for key, values in sorted(partition_costs.items())
        )
        + "}"
    )
    print(f"three_world_uniform={_summary(maps, all_worlds)}")
    print(f"pair_uniform={pair_summaries}")
    print(f"one_stage_values_by_support={one_stage_values}")
    print(f"two_stage_unrestricted_transition_value={two_stage[0]}")
    print(f"zero_overflow_world_count_histogram={dict(sorted(zero_cost_world_counts.items()))}")
    print(f"distinct_overflow_triplets={triplets}")


if __name__ == "__main__":
    main()
