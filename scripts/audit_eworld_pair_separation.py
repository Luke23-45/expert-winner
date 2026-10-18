"""Finite exact audit of the E-world pair-separation conjecture.

The first audit enumerates every feasible Top-1 score-cell signature in the
existing E=4 construction, then checks the proposed one-step inequality for
every nonempty posterior support. The second audit solves the restricted
subset-probe decision problem by exact rational dynamic programming. Neither
part proves the inequality for arbitrary E or arbitrary pressure states.
"""
from __future__ import annotations

import runpy
from fractions import Fraction
from functools import lru_cache
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def exact_e4_audit() -> None:
    source = ROOT / "scripts" / "analyze_e4_exact_partition.py"
    data = runpy.run_path(str(source))
    n = data["N_REGULAR"]
    experts = data["N_EXPERTS"]
    maps = set()
    for winners in product(range(experts), repeat=len(data["TOKEN_INTERCEPTS"])):
        if data["_feasible"](data["_winner_constraints"](winners)):
            maps.add(data["_world_observations"](winners))

    excess = data["E_S"]
    regular_capacity = data["C"]
    sink_capacity = data["C_SINK"]
    probe_cost = excess + regular_capacity - sink_capacity
    violations = []
    minimum_slack: dict[tuple[int, ...], Fraction] = {}
    checked = 0
    for observations, costs in maps:
        for support_mask in range(1, 1 << n):
            support = [i for i in range(n) if support_mask & (1 << i)]
            size = len(support)
            blocks: dict[tuple[int, ...], int] = {}
            for world in support:
                blocks[observations[world]] = blocks.get(observations[world], 0) + 1
            expected_support_drop = Fraction(size) - sum(
                Fraction(block_size * block_size, size)
                for block_size in blocks.values()
            )
            expected_overflow = Fraction(sum(costs[i] for i in support), size)
            lower_bound = Fraction(probe_cost, 2) * expected_support_drop
            partition_shape = tuple(sorted(blocks.values(), reverse=True))
            slack = expected_overflow - lower_bound
            minimum_slack[partition_shape] = min(
                minimum_slack.get(partition_shape, slack), slack
            )
            checked += 1
            if slack < 0:
                violations.append(
                    (support, partition_shape, expected_overflow, lower_bound)
                )

    print(f"E4 feasible joint winner assignments: exact enumeration")
    print(f"E4 distinct admitted observation/cost maps: {len(maps)}")
    print(f"E4 action-map/support checks: {checked}")
    print(
        "candidate inequality: expected overflow >= "
        f"({probe_cost}/2) * expected support-size reduction"
    )
    print(f"E4 minimum slack by partition shape: {minimum_slack}")
    print(f"E4 violations: {violations}")


def subset_probe_value(
    worlds: int,
    regular_capacity: int,
    excess: int,
    sink_capacity: int,
    horizon: int,
) -> Fraction:
    """Exact finite-horizon value for subset probes with unrestricted moves.

    An action is a subset P of regular experts whose low-margin blocks move to
    the sink. A world in P is identified by the surviving high-margin block;
    all worlds outside P share one outcome. The first blind q=0 round is not
    included: this function starts at the common posterior after that round.
    """
    n = worlds

    def outcome(world: int, action_mask: int) -> tuple[int, ...]:
        action_size = action_mask.bit_count()
        regular = tuple(
            regular_capacity
            if not (action_mask & (1 << expert)) or world == expert
            else 0
            for expert in range(n)
        )
        if action_size == 0:
            sink = 0
        elif action_mask & (1 << world):
            sink_request = (action_size - 1) * regular_capacity + excess
            sink = min(sink_request, sink_capacity)
        else:
            sink = min(action_size * regular_capacity, sink_capacity)
        return regular + (sink,)

    def overflow(world: int, action_mask: int) -> int:
        action_size = action_mask.bit_count()
        if action_size == 0:
            return excess
        if action_mask & (1 << world):
            sink_request = (action_size - 1) * regular_capacity + excess
            return max(0, sink_request - sink_capacity)
        return excess + action_size * regular_capacity - sink_capacity

    @lru_cache(maxsize=None)
    def value(support_mask: int, remaining: int) -> Fraction:
        support = [i for i in range(n) if support_mask & (1 << i)]
        if remaining == 0 or len(support) <= 1:
            return Fraction(0)
        best: Fraction | None = None
        for action_mask in range(1 << n):
            groups: dict[tuple[int, ...], int] = {}
            cost_sum = 0
            for world in support:
                cost_sum += overflow(world, action_mask)
                observation = outcome(world, action_mask)
                groups[observation] = groups.get(observation, 0) | (1 << world)
            candidate = Fraction(cost_sum, len(support))
            candidate += sum(
                Fraction(group.bit_count(), len(support))
                * value(group, remaining - 1)
                for group in groups.values()
            )
            if best is None or candidate < best:
                best = candidate
        assert best is not None
        return best

    return value((1 << n) - 1, horizon)


def subset_probe_audit() -> None:
    parameters = (
        (50, 20, 30),
        (45, 20, 30),
        (55, 20, 30),
        (100, 20, 20),
    )
    for capacity, excess, sink_capacity in parameters:
        if not (excess <= sink_capacity < capacity - excess / 2):
            continue
        results = []
        for n in range(2, 8):
            results.append(
                subset_probe_value(
                    worlds=n,
                    regular_capacity=capacity,
                    excess=excess,
                    sink_capacity=sink_capacity,
                    horizon=n,
                )
            )
        print(
            "subset-probe values, H=N, C/ES/Csink="
            f"{capacity}/{excess}/{sink_capacity}, N=2..7: {results}"
        )


if __name__ == "__main__":
    exact_e4_audit()
    subset_probe_audit()
