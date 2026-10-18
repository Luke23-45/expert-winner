#!/usr/bin/env python3
"""Exact post-run audit of T6b on small varied Top-K plants.

This is exploratory diagnostic evidence, not a preregistered experiment or a
proof. Run from the exploration worktree root:
    python scripts/audit_t6b_randomized_small.py
"""

from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_admitted_saturation_exit as model  # noqa: E402


SEED = 20261017
CASE_COUNT = 100


def main() -> None:
    rng = random.Random(SEED)
    model.E = 4
    model.K = 2
    model.TOKENS = 8
    model.ETA = Fraction(1, 10)
    model.GAMMA = Fraction(1)
    model.DELTA = Fraction(0)

    records: list[dict] = []
    attempts = 0
    while len(records) < CASE_COUNT and attempts < 1000:
        attempts += 1
        weights = [rng.randint(2, 6) for _ in range(model.E)]
        weight_sum = sum(weights)
        target = tuple(Fraction(w, weight_sum) for w in weights)
        capacities = tuple(rng.randint(1, 3) for _ in range(model.E))
        model.TARGET = target
        model.CAPACITY = capacities

        h = tuple(
            Fraction(capacities[e], model.K * model.TOKENS) - target[e]
            for e in range(model.E)
        )
        v = model.p0(h)
        ordered_slopes = sorted(v)
        if ordered_slopes[model.K - 1] == ordered_slopes[model.K]:
            continue

        # The same ring-pair request structure is used in every case; only
        # the exact affinity perturbations, target, and capacities vary.
        pairs = [(0, 1), (1, 2), (2, 3), (3, 0)] * 2
        rng.shuffle(pairs)
        affinities = tuple(
            tuple(
                Fraction(rng.randint(100, 110), 100)
                if expert in pair
                else Fraction(rng.randint(0, 10), 100)
                for expert in range(model.E)
            )
            for pair in pairs
        )

        q0 = (Fraction(0),) * model.E
        initial = model.route_counts(affinities, q0)
        if any(initial[e] < capacities[e] for e in range(model.E)):
            raise AssertionError("Generated plant is not initially saturated.")

        n_sep, _, v, slope_gap = model.saturation_bound(affinities, q0)
        n_t6b, witness, leave_count = model.capacity_slack_exit_bound(
            affinities, q0, v
        )
        run = model.run_arm(affinities, "admitted", n_sep + 2)
        tau = next((row["step"] for row in run if not row["saturated"]), None)

        if tau is None or not (tau <= n_t6b <= n_sep):
            raise AssertionError(
                f"T6b violation: tau={tau}, N_e={n_t6b}, N_sep={n_sep}"
            )
        if any(
            sum(row["requested"]) != model.K * model.TOKENS
            or row["admitted"]
            != tuple(min(row["requested"][e], capacities[e]) for e in range(model.E))
            for row in run
        ):
            raise AssertionError("Mass conservation or clipping identity failed.")

        records.append(
            {
                "case": len(records),
                "target": [str(value) for value in target],
                "capacities": list(capacities),
                "initial_requested": list(initial),
                "witness_expert": witness,
                "departures_needed": leave_count,
                "strict_slope_gap": str(slope_gap),
                "N_t6b": n_t6b,
                "N_sep": n_sep,
                "observed_exit": tau,
                "tight": n_t6b == tau,
            }
        )

    if len(records) != CASE_COUNT:
        raise AssertionError(f"Only generated {len(records)} valid cases.")

    script_path = Path(__file__).resolve()
    result = {
        "purpose": "Post-run exact arithmetic diagnostic for T6b; not preregistered and not proof",
        "seed": SEED,
        "case_count": CASE_COUNT,
        "attempts": attempts,
        "plant": {"experts": model.E, "top_k": model.K, "tokens": model.TOKENS},
        "checks": {
            "all_initially_globally_saturated": True,
            "all_strict_K_Kplus1_gaps_positive": True,
            "observed_exit_le_T6b_le_T6a_all_cases": all(
                row["observed_exit"] <= row["N_t6b"] <= row["N_sep"]
                for row in records
            ),
            "all_exact_mass_and_clipping_identities_hold": True,
        },
        "tight_cases": sum(row["tight"] for row in records),
        "ranges": {
            "N_t6b": [min(r["N_t6b"] for r in records), max(r["N_t6b"] for r in records)],
            "N_sep": [min(r["N_sep"] for r in records), max(r["N_sep"] for r in records)],
        },
        "script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
        "base_revision": subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip(),
        "cases": records,
    }
    output = Path("results/admitted_saturation_exit/t6b_property_audit.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
