#!/usr/bin/env python3
"""Analysis for the v2 hardened control experiments (protocol 0.2.0).

Loads every run under the v2 runs dir and reports, per scenario x controller:

- head-to-head: final/min violation, first routing change step, final
  overflow, and (windup) overshoot / settling time / oscillation counts
  around the spike and release, plus (specialization_probe) MI trajectory.
- thrash mapping: per-gain classification into converged / oscillating /
  thrash, with settling time and overshoot vs. gain.

Operational definitions (descriptive, not convergence claims):
- baseline (windup): mean violation over [spike_step-100, spike_step).
- overshoot: max post-release violation excess above baseline.
- settling_time: steps after release until the violation stays within
  baseline +/- max(0.01, 0.5*baseline) for the rest of the run (None if never).
- oscillation_count: sign changes of successive violation deltas.
- thrash classification on the demand-shift tail (last 200 steps):
    thrash      if final_viol > 2*max(init_viol,1e-3) or final_viol > 0.4
    oscillating if oscillation_count(tail) >= 20
    converged   if tail_range < 0.002 and oscillation_count(tail) <= 4
    settling    otherwise

Usage:
    .venv/bin/python scripts/analyze_v2.py [--runs-dir docs/control_experiment_results/v2_runs]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from moe_control.metrics import (  # noqa: E402
    oscillation_count,
    overshoot,
    settling_time,
)


def load_runs(runs_dir: Path):
    runs = []
    for run_dir in sorted(runs_dir.iterdir()):
        if not (run_dir / "metrics.parquet").exists():
            continue
        rows = pq.read_table(run_dir / "metrics.parquet").to_pylist()
        summary = json.loads((run_dir / "summary.json").read_text())
        cfg_text = (run_dir / "config.resolved.yaml").read_text()
        eta = float(re.search(r"step_size:\s*([\d.]+)", cfg_text).group(1))
        bg = re.search(r"bias_gamma:\s*([\d.]+)", cfg_text)
        runs.append({
            "run_id": run_dir.name, "rows": rows, "summary": summary,
            "eta": eta, "bias_gamma": float(bg.group(1)) if bg else None,
        })
    return runs


def first_routing_change(rows):
    r0 = [float(v) for v in rows[0]["requested_counts"]]
    for row in rows:
        if any(abs(a - b) > 1e-9
               for a, b in zip([float(v) for v in row["requested_counts"]], r0)):
            return row["step"]
    return None


def classify(viol):
    init, final = viol[0], viol[-1]
    tail = viol[-200:]
    trange = max(tail) - min(tail)
    osc = oscillation_count(viol, len(viol) - 200, len(viol))
    if abs(final - init) < 0.002 and trange < 1e-9 and osc == 0:
        return "inert", trange, osc
    if final > 2 * max(init, 1e-3) or final > 0.4:
        return "thrash", trange, osc
    if osc >= 20:
        return "oscillating", trange, osc
    if trange < 0.002 and osc <= 4:
        return "converged", trange, osc
    return "settling", trange, osc


def analyze_head_to_head(runs):
    print("# v2 head-to-head\n")
    groups = {}
    for r in runs:
        s = r["summary"]
        if "thrash" in r["run_id"]:
            continue
        groups.setdefault((s["scenario"], s["seed"]), []).append(r)
    for (scenario, seed), grp in sorted(groups.items()):
        print(f"## scenario={scenario} seed={seed}")
        for r in sorted(grp, key=lambda x: x["summary"]["controller"]):
            s = r["summary"]
            rows = r["rows"]
            viol = [row["requested_max_violation"] for row in rows]
            fc = first_routing_change(rows)
            line = (f"  {s['controller']:24s} init_viol={viol[0]:.4f} "
                    f"final_viol={viol[-1]:.4f} min_viol={min(viol):.4f} "
                    f"first_change={fc} final_overflow={rows[-1]['total_overflow']}")
            if scenario == "saturation_windup":
                base = sum(viol[300:400]) / 100
                ov = overshoot(viol, base, 800)
                st = settling_time(viol, base, max(0.01, 0.5 * base), 800)
                osc_spike = oscillation_count(viol, 400, 800)
                osc_post = oscillation_count(viol, 800, 1200)
                pr = max(max(row["pressure_after"]) - min(row["pressure_after"])
                         for row in rows[400:800])
                line += (f" overshoot={ov:+.4f} settle={st} osc_spike={osc_spike} "
                         f"osc_post={osc_post} prange_spike={pr:.2f}")
            if scenario == "specialization_probe":
                mis = [row.get("specialization_mi") for row in rows]
                mis = [m for m in mis if m is not None]
                if mis:
                    line += f" MI_init={mis[0]:.3f} MI_final={mis[-1]:.3f}"
            print(line)
        print()


def _exp_name(run_id: str) -> str:
    """Extract the experiment.name token from a run_id.

    run_id format: <timestamp>-<experiment_name>-<scenario>-<controller>-<hex>.
    """
    for name in ("thrash_gamma_sweep_exact", "thrash_gamma_sweep",
                 "thrash_eta_sweep"):
        if f"-{name}-" in run_id:
            return name
    return ""


def analyze_thrash(runs):
    print("# v2 thrash mapping (demand_shift, 1000 steps, shift at 250)\n")
    for exp_name, key, label in (
        ("thrash_eta_sweep", "eta", "pressure eta sweep"),
        ("thrash_gamma_sweep_exact", "bias_gamma",
         "bias gamma sweep (exact_total)"),
    ):
        print(f"## {label}")
        sel = [r for r in runs if _exp_name(r["run_id"]) == exp_name]
        for r in sorted(sel, key=lambda x: x[key]):
            rows = r["rows"]
            viol = [row["requested_max_violation"] for row in rows]
            cls, trange, osc = classify(viol)
            fc = first_routing_change(rows)
            st = settling_time(viol, viol[-1], 0.01, 250)
            print(f"  {key}={r[key]:<8g} {r['summary']['controller']:10s} "
                  f"class={cls:11s} final_viol={viol[-1]:.4f} "
                  f"tail_range={trange:.4f} tail_osc={osc} "
                  f"first_change={fc} settle_post_shift={st}")
        print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir",
                    default="docs/control_experiment_results/v2_runs")
    args = ap.parse_args()
    runs = load_runs(Path(args.runs_dir))
    print(f"# loaded {len(runs)} v2 runs\n")
    analyze_head_to_head(runs)
    analyze_thrash(runs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
