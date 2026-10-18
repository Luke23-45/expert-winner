#!/usr/bin/env python3
"""Exhaustive exact check of the T4b minimal-signal family.

Run from the exploration worktree root:
    python scripts/audit_minimal_signal_family.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path


EXPERT_COUNTS = (2, 3, 4, 8, 16, 32)


def gauge_project(vector: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    minimum = min(vector)
    return tuple(value - minimum for value in vector)


def p0(vector: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    mean = sum(vector, Fraction(0)) / len(vector)
    return tuple(value - mean for value in vector)


def top1_counts(rows: tuple[tuple[Fraction, ...], ...], experts: int) -> tuple[int, ...]:
    counts = [0] * experts
    for row in rows:
        winner = max(range(experts), key=lambda e: (row[e], -e))
        counts[winner] += 1
    return tuple(counts)


def as_strings(values: tuple[Fraction, ...]) -> list[str]:
    return [str(value) for value in values]


def main() -> None:
    family_records: list[dict] = []
    global_checks = {
        "top1_affinities_realize_every_request_vector": True,
        "all_worlds_share_the_same_admitted_vector": True,
        "fiber_cardinality_equals_expert_count": True,
        "requested_updates_are_pairwise_distinct": True,
        "admitted_update_is_identical_across_worlds": True,
        "centered_rejected_signal_is_injective": True,
        "message_alphabet_lower_bound_is_tight": True,
        "mass_and_clipping_identities_hold": True,
    }

    for experts in EXPERT_COUNTS:
        top_k = 1
        tokens = experts + 1
        capacity = (1,) * experts
        target = (Fraction(1, experts),) * experts
        kt = top_k * tokens
        q0 = (Fraction(0),) * experts
        worlds: list[dict] = []

        for overloaded in range(experts):
            # One one-hot token per expert, plus a second one-hot token for
            # the overloaded expert. All rows use exact binary affinities.
            assignments = list(range(experts)) + [overloaded]
            affinities = tuple(
                tuple(Fraction(int(e == assigned)) for e in range(experts))
                for assigned in assignments
            )
            requested = top1_counts(affinities, experts)
            admitted = tuple(min(requested[e], capacity[e]) for e in range(experts))
            rejected = tuple(requested[e] - admitted[e] for e in range(experts))
            centered_rejected = p0(tuple(Fraction(x) for x in rejected))

            admitted_feedback = tuple(
                Fraction(admitted[e], kt) - target[e] for e in range(experts)
            )
            requested_feedback = tuple(
                Fraction(requested[e], kt) - target[e] for e in range(experts)
            )
            q_admitted = gauge_project(admitted_feedback)
            q_requested = gauge_project(requested_feedback)

            expected_request = tuple(
                2 if e == overloaded else 1 for e in range(experts)
            )
            exact_world = (
                requested == expected_request
                and sum(requested) == kt
                and admitted == (1,) * experts
                and admitted == tuple(min(requested[e], capacity[e]) for e in range(experts))
                and sum(rejected) == kt - sum(admitted)
                and q_admitted == (Fraction(0),) * experts
                and q_requested
                == tuple(Fraction(int(e == overloaded), tokens) for e in range(experts))
            )
            if not exact_world:
                raise AssertionError(f"Exact family check failed for E={experts}, i={overloaded}")

            worlds.append(
                {
                    "overloaded_expert": overloaded,
                    "requested": list(requested),
                    "admitted": list(admitted),
                    "rejected": list(rejected),
                    "P0_rejected": as_strings(centered_rejected),
                    "q_next_requested": as_strings(q_requested),
                    "q_next_admitted": as_strings(q_admitted),
                    "top1_realizable": True,
                    "mass_and_clipping_exact": True,
                }
            )

        request_vectors = {tuple(w["requested"]) for w in worlds}
        admitted_vectors = {tuple(w["admitted"]) for w in worlds}
        centered_vectors = {tuple(w["P0_rejected"]) for w in worlds}
        requested_updates = {tuple(w["q_next_requested"]) for w in worlds}
        admitted_updates = {tuple(w["q_next_admitted"]) for w in worlds}
        bit_lower_bound = (experts - 1).bit_length()
        fiber_size = len(request_vectors)
        checks = {
            "top1_affinities_realize_every_request_vector": len(worlds) == experts,
            "all_worlds_share_the_same_admitted_vector": len(admitted_vectors) == 1,
            "fiber_cardinality_equals_expert_count": fiber_size == experts,
            "requested_updates_are_pairwise_distinct": len(requested_updates) == experts,
            "admitted_update_is_identical_across_worlds": len(admitted_updates) == 1,
            "centered_rejected_signal_is_injective": len(centered_vectors) == experts,
            "message_alphabet_lower_bound_is_tight": (1 << bit_lower_bound) >= fiber_size
            and bit_lower_bound == (fiber_size - 1).bit_length(),
            "mass_and_clipping_identities_hold": all(
                w["mass_and_clipping_exact"] for w in worlds
            ),
        }
        for name, ok in checks.items():
            global_checks[name] &= ok
        if not all(checks.values()):
            raise AssertionError(f"Family checks failed for E={experts}: {checks}")

        family_records.append(
            {
                "experts": experts,
                "top_k": top_k,
                "tokens": tokens,
                "capacities": list(capacity),
                "target": as_strings(target),
                "admitted_observation": [1] * experts,
                "fiber_size": fiber_size,
                "minimum_fixed_length_bits": bit_lower_bound,
                "requested_update_count": len(requested_updates),
                "admitted_update_count": len(admitted_updates),
                "checks": checks,
                "worlds": worlds,
            }
        )

    protocol_path = Path("docs/paper/minimal_signal_audit_2026-10-17.md")
    script_path = Path(__file__).resolve()
    output = {
        "purpose": "Exact one-step requested-update emulation audit for T4b",
        "scope": "Exhaustive finite family; not a performance experiment or physical communication benchmark",
        "expert_counts": list(EXPERT_COUNTS),
        "protocol_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
        "base_revision": subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip(),
        "checks": global_checks,
        "families": family_records,
    }
    output_path = Path("results/minimal_signal_audit/summary.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks": global_checks, "families": [
        {k: f[k] for k in ("experts", "fiber_size", "minimum_fixed_length_bits", "requested_update_count", "admitted_update_count")}
        for f in family_records
    ]}, indent=2))


if __name__ == "__main__":
    main()
