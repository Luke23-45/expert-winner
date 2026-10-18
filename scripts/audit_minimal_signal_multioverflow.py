#!/usr/bin/env python3
"""Exact enumeration of the preregistered multi-overflow telemetry audit.

Run from the exploration repository root:
    python scripts/audit_minimal_signal_multioverflow.py
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Iterator


EXPERT_COUNTS = (2, 3, 4, 8)
EXCESS_COUNTS = (1, 2, 3, 4)


def compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    """Yield all weak compositions of total into parts in lexicographic order."""
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def gauge_project(values: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    minimum = min(values)
    return tuple(value - minimum for value in values)


def zero_sum_project(values: tuple[int, ...]) -> tuple[Fraction, ...]:
    mean = Fraction(sum(values), len(values))
    return tuple(Fraction(value) - mean for value in values)


def top1_counts(assignments: tuple[int, ...], experts: int) -> tuple[int, ...]:
    """Route exact one-hot rows, with lower-index tie-breaking."""
    counts = [0] * experts
    for assigned in assignments:
        row = tuple(Fraction(int(expert == assigned)) for expert in range(experts))
        winner = max(range(experts), key=lambda expert: (row[expert], -expert))
        counts[winner] += 1
    return tuple(counts)


def main() -> None:
    groups: list[dict] = []
    total_worlds = 0
    for experts in EXPERT_COUNTS:
        for excess in EXCESS_COUNTS:
            tokens = experts + excess
            target = (Fraction(1, experts),) * experts
            expected_fiber = math.comb(experts + excess - 1, excess)
            requested_vectors: set[tuple[int, ...]] = set()
            rejected_signals: set[tuple[Fraction, ...]] = set()
            requested_states: set[tuple[Fraction, ...]] = set()
            admitted_states: set[tuple[Fraction, ...]] = set()

            for d in compositions(excess, experts):
                requested = tuple(1 + value for value in d)
                assignments = tuple(
                    expert
                    for expert, count in enumerate(requested)
                    for _ in range(count)
                )
                routed = top1_counts(assignments, experts)
                admitted = tuple(min(value, 1) for value in routed)
                rejected = tuple(routed[e] - admitted[e] for e in range(experts))

                requested_feedback = tuple(
                    Fraction(routed[e], tokens) - target[e] for e in range(experts)
                )
                admitted_feedback = tuple(
                    Fraction(admitted[e], tokens) - target[e] for e in range(experts)
                )
                q_requested = gauge_project(requested_feedback)
                q_admitted = gauge_project(admitted_feedback)
                centered_rejected = zero_sum_project(rejected)

                if routed != requested:
                    raise AssertionError(("Top-1 realizability", experts, excess, d, routed))
                if sum(routed) != tokens or admitted != (1,) * experts:
                    raise AssertionError(("mass/admission", experts, excess, d))
                if sum(rejected) != excess:
                    raise AssertionError(("rejected mass", experts, excess, d, rejected))

                requested_vectors.add(routed)
                rejected_signals.add(centered_rejected)
                requested_states.add(q_requested)
                admitted_states.add(q_admitted)

            minimum_bits = (expected_fiber - 1).bit_length()
            checks = {
                "fiber_cardinality_stars_and_bars": len(requested_vectors) == expected_fiber,
                "rejected_signal_injective": len(rejected_signals) == expected_fiber,
                "requested_update_injective": len(requested_states) == expected_fiber,
                "admitted_update_constant": len(admitted_states) == 1,
                "fixed_length_code_tight": minimum_bits == (len(requested_vectors) - 1).bit_length(),
                "code_capacity_covers_fiber": (1 << minimum_bits) >= expected_fiber,
            }
            if not all(checks.values()):
                raise AssertionError(("group check", experts, excess, checks))

            groups.append({
                "experts": experts,
                "excess_rejected_mass": excess,
                "tokens": tokens,
                "fiber_size": expected_fiber,
                "distinct_requested_updates": len(requested_states),
                "distinct_admitted_updates": len(admitted_states),
                "minimum_fixed_length_bits": minimum_bits,
                "checks": checks,
            })
            total_worlds += expected_fiber

    protocol = Path("docs/paper/minimal_signal_multioverflow_protocol_2026-10-17.md")
    script = Path(__file__).resolve()
    output = {
        "purpose": "Exact Top-1 enumeration of multi-overflow clipping fibers for one-step requested-update emulation",
        "scope": "finite exact synthetic audit; no controller-optimality or physical-cost claim",
        "expert_counts": list(EXPERT_COUNTS),
        "excess_counts": list(EXCESS_COUNTS),
        "enumerated_worlds": total_worlds,
        "protocol_sha256": hashlib.sha256(protocol.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "base_revision": subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip(),
        "all_groups_pass": True,
        "groups": groups,
    }
    output_path = Path("results/minimal_signal_multioverflow/summary.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_groups_pass": True,
        "enumerated_worlds": total_worlds,
        "groups": [
            {key: group[key] for key in (
                "experts", "excess_rejected_mass", "fiber_size", "minimum_fixed_length_bits"
            )}
            for group in groups
        ],
    }, indent=2))
    print(f"Artifact: {output_path.resolve()}")


if __name__ == "__main__":
    main()
