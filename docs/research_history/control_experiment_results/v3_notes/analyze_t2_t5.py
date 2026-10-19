#!/usr/bin/env python3
"""T2/T5 analysis (v3).

T2: admitted_antiwindup (v3_runs/antiwindup_probe) vs requested, admitted,
    admitted_centered, bias_integral (v2_runs head-to-head) on the 5 v2
    scenarios x seeds {17, 23}.
T5: requested vs bias_integral on the 5 v2 scenarios x seeds {17, 23}
    (v2_runs) + {42, 99} (v3_runs/deepseek_headtohead): 4-seed aggregates
    and paired win counts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

V3 = REPO / "docs/control_experiment_results/v3_runs"
V2 = REPO / "docs/control_experiment_results/v2_runs"

SCEN = [
    ("saturation_windup", 1200),
    ("adversarial_init", 800),
    ("adversarial_batches", 1000),
    ("specialization_probe", 800),
    ("small_batch", 800),
]
V2CTLS = ("requested", "admitted", "admitted_centered", "bias_integral")


def load(d, scenario, controller, seed, steps, tag=None):
    cands = []
    for rd in sorted(d.iterdir()):
        if tag and tag not in rd.name:
            continue
        s = json.loads((rd / "summary.json").read_text())
        if (s["scenario"] == scenario and s["controller"] == controller
                and s["seed"] == seed and s["steps"] == steps):
            rows = pq.read_table(rd / "metrics.parquet").to_pylist()
            cands.append((s, rows))
    return cands[0] if cands else None


def first_change(rows):
    r0 = rows[0]["requested_counts"]
    for row in rows:
        if row["requested_counts"] != r0:
            return row["step"]
    return None


def main():
    print("=== T2: anti-windup vs v2 controllers (seeds 17, 23) ===")
    for sc, steps in SCEN:
        print(f"\n--- {sc} ({steps} steps) ---")
        print(f"  {'controller':<22}{'seed':<6}{'viol0':<8}{'violF':<8}"
              f"{'ovF':<8}{'firstchg':<9}{'satfrac':<7}")
        for ctl in ("requested", "admitted", "admitted_centered",
                    "admitted_antiwindup", "bias_integral"):
            for sd in (17, 23):
                d = V3 if ctl == "admitted_antiwindup" else V2
                tag = "antiwindup_probe" if ctl == "admitted_antiwindup" \
                    else None
                hit = load(d, sc, ctl, sd, steps, tag)
                if hit is None:
                    print(f"  {ctl:<22}{sd:<6}MISSING")
                    continue
                s, rows = hit
                fc = first_change(rows)
                print(f"  {ctl:<22}{sd:<6}"
                      f"{rows[0]['requested_max_violation']:<8.4f}"
                      f"{rows[-1]['requested_max_violation']:<8.4f}"
                      f"{rows[-1]['total_overflow']:<8}"
                      f"{str(fc):<9}{s['fraction_steps_saturated']:<7.2f}")
        # windup-specific: spike-end viol + post-release overshoot.
        # Spike window [400, 800) per results_v2.md section 2.
        if sc == "saturation_windup":
            for ctl in ("requested", "admitted", "admitted_antiwindup",
                        "bias_integral"):
                for sd in (17, 23):
                    d = V3 if ctl == "admitted_antiwindup" else V2
                    tag = "antiwindup_probe" if ctl == "admitted_antiwindup" \
                        else None
                    hit = load(d, sc, ctl, sd, steps, tag)
                    if hit is None:
                        continue
                    _, rows = hit
                    viol = [r["requested_max_violation"] for r in rows]
                    v_spike_end = viol[799]
                    base = sum(viol[300:400]) / 100
                    post = viol[800:]
                    ov = max(post) - base if post else float("nan")
                    print(f"    windup {ctl} seed={sd}: spike-end viol="
                          f"{v_spike_end:.4f} post-release overshoot={ov:.4f} "
                          f"final viol={viol[-1]:.4f}")

    print("\n\n=== T5: requested vs bias_integral, 4 seeds ===")
    for sc, steps in SCEN:
        print(f"\n--- {sc} ---")
        for ctl in ("requested", "bias_integral"):
            finals = []
            for sd in (17, 23):
                hit = load(V2, sc, ctl, sd, steps)
                if hit:
                    finals.append(hit[1][-1]["requested_max_violation"])
            for sd in (42, 99):
                hit = load(V3, sc, ctl, sd, steps, "deepseek_headtohead")
                if hit:
                    finals.append(hit[1][-1]["requested_max_violation"])
            if finals:
                print(f"  {ctl:<14} final viol per seed: "
                      f"{[f'{v:.4f}' for v in finals]} "
                      f"mean={sum(finals)/len(finals):.4f} "
                      f"min={min(finals):.4f} max={max(finals):.4f}")
        # paired wins
        wins = {"requested": 0, "bias_integral": 0, "tie": 0}
        for sd in (17, 23, 42, 99):
            d = V2 if sd in (17, 23) else V3
            tag = None if sd in (17, 23) else "deepseek_headtohead"
            hr = load(d, sc, "requested", sd, steps, tag)
            hb = load(d, sc, "bias_integral", sd, steps, tag)
            if hr and hb:
                vr = hr[1][-1]["requested_max_violation"]
                vb = hb[1][-1]["requested_max_violation"]
                if abs(vr - vb) < 1e-12:
                    wins["tie"] += 1
                elif vr < vb:
                    wins["requested"] += 1
                else:
                    wins["bias_integral"] += 1
        print(f"  paired wins (lower final viol): {wins}")


if __name__ == "__main__":
    main()
