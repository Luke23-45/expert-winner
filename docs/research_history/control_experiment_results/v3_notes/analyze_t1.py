#!/usr/bin/env python3
"""T1 non-uniform-target analysis (v3).

Reads the 36 nonuniform_target runs and reports, per (capacity regime,
controller, seed): violation/overflow trajectories, exact-balance
attainment (min over steps of max|R_e - KT*mu_e|), saturation detail,
pressure movement, and the phantom-gradient vs freeze contrast under
global saturation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

RUNS = REPO / "docs/control_experiment_results/v3_runs"
TARGET = [384, 352, 320, 288, 256, 224, 128, 96]
KT = 2048


def load():
    runs = []
    for rd in sorted(RUNS.iterdir()):
        s = json.loads((rd / "summary.json").read_text())
        if s["scenario"] != "nonuniform_target":
            continue
        rows = pq.read_table(rd / "metrics.parquet").to_pylist()
        runs.append((s, rows, rd.name))
    return runs


def main():
    runs = load()
    print(f"T1 runs loaded: {len(runs)}")
    print(f"target counts: {TARGET}")
    for cap in ("hetero_balanced", "hetero_shortage"):
        print(f"\n=== capacity={cap} ===")
        grp = [(s, rows) for s, rows, _ in runs
               if s["capacity_regime"] == cap]
        for ctl in ("requested", "admitted", "admitted_centered",
                    "capacity_relative", "admitted_antiwindup",
                    "bias_integral"):
            g = [(s, rows) for s, rows in grp if s["controller"] == ctl]
            if not g:
                print(f"  {ctl}: MISSING")
                continue
            line = f"  {ctl:<22}"
            for s, rows in sorted(g, key=lambda x: x[0]["seed"]):
                v0 = rows[0]["requested_max_violation"]
                vf = rows[-1]["requested_max_violation"]
                # exact-balance: min over steps of max|R_e - target_e|
                best = min(max(abs(rc - t) for rc, t in
                               zip(row["requested_counts"], TARGET))
                           for row in rows)
                # pressure movement: max range over run
                pr = max(max(float(v) for v in row["pressure_after"]) -
                         min(float(v) for v in row["pressure_after"])
                         for row in rows)
                sat = s["fraction_steps_saturated"]
                line += (f" | seed={s['seed']}: viol {v0:.4f}->{vf:.4f} "
                         f"best_exact={best:.0f} prange_max={pr:.3f} "
                         f"sat={sat:.2f}")
            print(line)

    # Phantom-gradient vs freeze under global saturation (hetero_shortage).
    print("\n=== global-saturation step behavior (hetero_shortage, seed 17) ===")
    for ctl in ("admitted", "admitted_centered", "admitted_antiwindup",
                "requested"):
        hit = [(s, rows) for s, rows, _ in runs
               if s["capacity_regime"] == "hetero_shortage"
               and s["controller"] == ctl and s["seed"] == 17][0]
        s, rows = hit
        sat_steps = [row for row in rows if row["all_experts_saturated"]]
        # pressure change across consecutive globally-saturated steps
        import math
        moved = 0
        maxd = 0.0
        for a, b in zip(sat_steps, sat_steps[1:]):
            if b["step"] != a["step"] + 1:
                continue
            d = max(abs(x - y) for x, y in
                    zip(a["pressure_after"], b["pressure_after"]))
            maxd = max(maxd, d)
            if d > 1e-12:
                moved += 1
        fb0 = sat_steps[0]["feedback"]
        print(f"  {ctl:<22} saturated_steps={len(sat_steps)} "
              f"consecutive_pairs_moved={moved} max_step_d={maxd:.2e} "
              f"feedback@sat0={[f'{v:.4f}' for v in fb0]}")

    # admitted_centered final R under hetero_shortage (divergence detail).
    print("\n=== admitted_centered hetero_shortage final R (divergence) ===")
    for s, rows, _ in runs:
        if s["capacity_regime"] == "hetero_shortage" and \
                s["controller"] == "admitted_centered":
            print(f"  seed={s['seed']}: R_final={rows[-1]['requested_counts']} "
                  f"viol={rows[-1]['requested_max_violation']:.4f} "
                  f"overflow={rows[-1]['total_overflow']}")


if __name__ == "__main__":
    main()
