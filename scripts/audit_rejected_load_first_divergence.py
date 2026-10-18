#!/usr/bin/env python3
"""Exact audit of the common-prefix rejected-load route-divergence identity.

Run from the exploration repository root:
    python scripts/audit_rejected_load_first_divergence.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
from fractions import Fraction as F
from pathlib import Path


E, K, T, HORIZON = 4, 2, 12, 120
ETA, GAMMA, DELTA = F(1, 10), F(1), F(0)
SEEDS = tuple(range(40))
CAPACITIES = {
    "no_clipping": (12, 12, 12, 12),
    "exact_total_uniform": (6, 6, 6, 6),
    "exact_total_heterogeneous": (2, 4, 8, 10),
    "aggregate_shortage": (3, 3, 3, 3),
}
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/rejected_load_first_divergence"
PROTOCOL = ROOT / "docs/paper/facet_to_trajectory_bridge_protocol_2026-10-17.md"
THEOREM = ROOT / "docs/paper/rejected_load_route_divergence_identity_2026-10-17.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def affinities_for(seed: int):
    rng = random.Random(seed)
    return tuple(tuple(rng.randint(-4, 4) for _ in range(E)) for _ in range(T))


def project(z):
    m = min(z)
    return tuple(x - m for x in z)


def routes_for(affinities, q):
    routes = []
    for row in affinities:
        scores = tuple(F(a) - GAMMA * p for a, p in zip(row, q))
        routes.append(tuple(sorted(sorted(range(E), key=lambda e: (-scores[e], e))[:K])))
    return tuple(routes)


def counts(routes):
    out = [0] * E
    for route in routes:
        for e in route:
            out[e] += 1
    return tuple(out)


def score_gaps(affinities, q_adm, q_req, adm_routes):
    rows = []
    for token, selected in enumerate(adm_routes):
        unselected = tuple(e for e in range(E) if e not in selected)
        for i in selected:
            for j in unselected:
                gap_adm = F(affinities[token][i] - affinities[token][j]) - GAMMA * (q_adm[i] - q_adm[j])
                delta = (q_req[i] - q_req[j]) - (q_adm[i] - q_adm[j])
                gap_req = gap_adm - GAMMA * delta
                rows.append((gap_adm, gap_req, token, i, j, delta))
    return rows


def audit_pair(seed, profile, capacity):
    affinities = affinities_for(seed)
    q_req = tuple(F(0) for _ in range(E))
    q_adm = tuple(F(0) for _ in range(E))
    history_j = []
    first_divergence = None
    checked_common_prefix_states = 0
    minimum_common_route_gap = None
    divergence_rows = None

    for step in range(HORIZON):
        route_req = routes_for(affinities, q_req)
        route_adm = routes_for(affinities, q_adm)

        # Check the theorem's pairwise common-prefix identity directly against
        # the actual gauge-fixed states, including the divergence state.
        for i in range(E):
            for j in range(E):
                actual = (q_req[i] - q_req[j]) - (q_adm[i] - q_adm[j])
                predicted = F(0)
                for s, rejected in enumerate(history_j):
                    predicted += (
                        ETA * GAMMA / (K * T)
                        * (1 - DELTA) ** (step - 1 - s)
                        * (rejected[i] - rejected[j])
                    )
                assert actual == predicted, (seed, profile, step, i, j, actual, predicted)

        if route_req != route_adm:
            first_divergence = step
            divergence_rows = score_gaps(affinities, q_adm, q_req, route_adm)
            violating = [r for r in divergence_rows if r[1] <= 0]
            assert violating, (seed, profile, step, "route changed without selected/unselected margin witness")
            break

        checked_common_prefix_states += 1
        gaps = score_gaps(affinities, q_adm, q_req, route_adm)
        local_min = min((r[1] for r in gaps), default=None)
        if local_min is not None and (minimum_common_route_gap is None or local_min < minimum_common_route_gap):
            minimum_common_route_gap = local_min

        requested = counts(route_req)
        admitted = tuple(min(r, c) for r, c in zip(requested, capacity))
        rejected = tuple(r - a for r, a in zip(requested, admitted))
        assert sum(requested) == K * T
        assert sum(rejected) == sum(requested) - sum(admitted)
        history_j.append(rejected)

        q_req = project(tuple(
            (1 - DELTA) * q_req[e]
            + ETA * GAMMA * (F(requested[e], K * T) - F(1, E))
            for e in range(E)
        ))
        q_adm = project(tuple(
            (1 - DELTA) * q_adm[e]
            + ETA * GAMMA * (F(admitted[e], K * T) - F(1, E))
            for e in range(E)
        ))

    row = {
        "seed": seed,
        "capacity_profile": profile,
        "capacity": ",".join(map(str, capacity)),
        "first_route_divergence_state": first_divergence,
        "common_prefix_updates_checked": checked_common_prefix_states,
        "rejected_load_updates_in_prefix": len(history_j),
        "minimum_requested_gap_over_admitted_topk_during_common_prefix": "" if minimum_common_route_gap is None else str(minimum_common_route_gap),
        "first_divergence_witness_count": 0 if divergence_rows is None else sum(r[1] <= 0 for r in divergence_rows),
        "first_divergence_min_selected_unselected_requested_gap": "" if divergence_rows is None else str(min(r[1] for r in divergence_rows)),
    }
    return row


def exact_stats(values):
    finite = sorted(v for v in values if v is not None)
    if not finite:
        return {"n": 0, "mean": None, "median": None, "min": None, "max": None}
    n = len(finite)
    median = finite[n // 2] if n % 2 else (finite[n // 2 - 1] + finite[n // 2]) / 2
    return {"n": n, "mean": str(sum(finite, F(0)) / n), "median": str(median), "min": str(finite[0]), "max": str(finite[-1])}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [audit_pair(seed, profile, cap) for seed in SEEDS for profile, cap in CAPACITIES.items()]
    csv_path = OUT / "first_divergence.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    profiles = {}
    for profile in CAPACITIES:
        subset = [row for row in rows if row["capacity_profile"] == profile]
        times = [None if row["first_route_divergence_state"] is None else F(row["first_route_divergence_state"]) for row in subset]
        profiles[profile] = {
            "capacity": list(CAPACITIES[profile]),
            "plants": len(subset),
            "divergence_within_horizon": sum(x is not None for x in times),
            "no_divergence_within_horizon": sum(x is None for x in times),
            "first_divergence_state": exact_stats(times),
            "all_divergence_states_have_nonpositive_selected_unselected_gap_witness": all(
                row["first_route_divergence_state"] is None or
                F(row["first_divergence_min_selected_unselected_requested_gap"]) <= 0
                for row in subset
            ),
        }

    summary = {
        "status": "PASS",
        "audit": "rejected_load_first_divergence_identity",
        "theorem": str(THEOREM.relative_to(ROOT)),
        "theorem_sha256": sha256(THEOREM),
        "protocol_sha256": sha256(PROTOCOL),
        "script_sha256": sha256(Path(__file__)),
        "dimensions": {"E": E, "K": K, "T": T, "horizon": HORIZON, "seeds": list(SEEDS)},
        "dynamics": {"eta": str(ETA), "gamma": str(GAMMA), "delta": str(DELTA), "target": "uniform"},
        "exact_checks": {
            "common_prefix_pairwise_pressure_identity_checked_for_all_pairs": True,
            "every_observed_first_divergence_has_topk_margin_witness": all(
                row["first_route_divergence_state"] is None or
                row["first_divergence_witness_count"] > 0 for row in rows
            ),
            "paired_plants": len(rows),
        },
        "profiles": profiles,
        "interpretation": "Exact mechanism audit of the prefix identity and first route divergence; it does not predict post-divergence cumulative overflow.",
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "profiles": profiles, "summary": str(summary_path)}, indent=2))


if __name__ == "__main__":
    main()
