#!/usr/bin/env python3
"""Exact-rational DP audit of the finite-horizon E-world value lower bound."""
from __future__ import annotations

import csv
import hashlib
import json
import runpy
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/eworld_finite_horizon_lower_bound_protocol_2026-10-18.md"
DP_SOURCE = ROOT / "scripts/audit_eworld_pair_separation.py"
OUT = ROOT / "results/eworld_finite_horizon_lower_bound_2026-10-18"
PARAMETERS = ((50, 20, 30), (45, 20, 30), (55, 20, 30), (100, 20, 20))
WORLD_COUNTS = tuple(range(2, 8))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    source = runpy.run_path(str(DP_SOURCE))
    exact_value = source["subset_probe_value"]
    rows: list[dict[str, object]] = []
    for capacity, excess, sink_capacity in PARAMETERS:
        assert excess <= sink_capacity < capacity - Fraction(excess, 2)
        L = excess + capacity - sink_capacity
        for worlds in WORLD_COUNTS:
            a = Fraction(L * (worlds - 1), 2)
            b = Fraction(excess, 4)
            assert a > b
            for horizon in range(1, worlds + 3):
                dp = exact_value(worlds, capacity, excess, sink_capacity, horizon)
                bound = a * b * horizon / (a + b * (horizon - 1))
                half_min = min(a, b * horizon) / 2
                assert dp >= bound, (capacity, excess, sink_capacity, worlds, horizon, dp, bound)
                assert bound >= half_min, (capacity, excess, sink_capacity, worlds, horizon, bound, half_min)
                singleton_upper_attained = horizon >= worlds - 1 and dp == a
                rows.append({
                    "C": capacity, "E_S": excess, "C_sink": sink_capacity,
                    "N": worlds, "D": horizon, "L": L,
                    "a_exact": str(a), "b_exact": str(b),
                    "dp_value_exact": str(dp), "fh_lower_bound_exact": str(bound),
                    "half_min_bound_exact": str(half_min),
                    "singleton_upper_attained": singleton_upper_attained,
                    "dp_value_decimal": float(dp),
                    "fh_lower_bound_decimal": float(bound),
                    "lower_bound_fraction_of_dp": float(bound / dp) if dp else None,
                })

    OUT.mkdir(parents=True, exist_ok=True)
    cells = OUT / "cells.csv"
    with cells.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    attained = [r for r in rows if r["D"] >= r["N"] - 1]
    summary = {
        "experiment": "exact_rational_eworld_finite_horizon_lower_bound_audit",
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha(PROTOCOL),
        "runner_sha256": sha(Path(__file__)),
        "dp_source_sha256": sha(DP_SOURCE),
        "cells_sha256": sha(cells),
        "cell_count": len(rows),
        "parameter_rows": [list(x) for x in PARAMETERS],
        "N_values": list(WORLD_COUNTS),
        "all_dp_values_above_bound": True,
        "all_bounds_above_half_min": True,
        "singleton_upper_cases": len(attained),
        "singleton_upper_attained_cases": sum(bool(r["singleton_upper_attained"]) for r in attained),
        "minimum_bound_to_dp_ratio": min(r["lower_bound_fraction_of_dp"] for r in rows),
        "maximum_bound_to_dp_ratio": max(r["lower_bound_fraction_of_dp"] for r in rows),
        "method": "exact rational finite-horizon DP over all subset probes, under the proved all-pressure action reduction",
        "claim_boundary": "validates a lower bound for this family; no generic adaptive-testing novelty or hardware/model-quality claim",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
