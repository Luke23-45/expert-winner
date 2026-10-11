#!/usr/bin/env python3
"""Cross-seed verification of the headline findings in
docs/control_experiment_results/results.md.

Loads every run in results/runs/, groups by (scenario, capacity_regime, seed),
and checks each headline finding independently per seed:

  F1 saturation freeze: in the shortage regime, admitted/admitted_centered
     feedback is the constant (c-1)/E and pressure stays [0]*E all 500 steps.
  F2 gauge equivalence: requested == capacity_relative (bit-identical pressure
     trajectories); admitted == admitted_centered (bit-identical pressure).
  F3 slack contrast: requested-direction rebalances and cuts overflow while
     admitted-direction barely moves (first routing change much later).
  F4 demand shift: pressure state preserved exactly across the shift step;
     stale requested-pattern unwinds after the shift.
  F5 paired batches: identical affinity content hash across controllers
     within each (scenario, seed).

Usage:
    .venv/bin/python scripts/verify_findings.py [--runs-dir results/runs]

Exits nonzero if any check fails. Tolerances are deliberately tight for
deterministic quantities (F1/F2/F5) and loose for behavioral ones (F3/F4).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

E = 8
C_MINUS_ONE_OVER_E = (0.75 - 1.0) / E  # -0.03125, shortage regime


def load_runs(runs_dir: Path):
    runs = []
    for run_dir in sorted(runs_dir.iterdir()):
        metrics_path = run_dir / "metrics.parquet"
        if not metrics_path.exists():
            continue
        rows = pq.read_table(metrics_path).to_pylist()
        summary = json.loads((run_dir / "summary.json").read_text())
        affinity = json.loads((run_dir / "affinity_reference.json").read_text())
        runs.append(
            {
                "run_id": run_dir.name,
                "rows": rows,
                "summary": summary,
                "affinity": affinity,
            }
        )
    return runs


def as_floats(x):
    return [float(v) for v in x]


def check_group(runs):
    """runs: the 4 controller runs of one (scenario, capacity_regime, seed)."""
    out = {"checks": [], "notes": []}
    by_ctl = {r["summary"]["controller"]: r for r in runs}
    s = runs[0]["summary"]
    scenario, seed = s["scenario"], s["seed"]

    def add(name, ok, detail=""):
        out["checks"].append({"name": name, "ok": bool(ok), "detail": detail})

    # F5: paired affinity batches
    hashes = set()
    for r in runs:
        a = r["affinity"]
        hashes.add(
            a.get("content_hash_sha256", a.get("content_hash_sha256_before"))
        )
    add("F5 paired affinity batch", len(hashes) == 1,
        f"distinct hashes: {len(hashes)}")

    if scenario == "shortage":
        for ctl in ("admitted", "admitted_centered"):
            r = by_ctl[ctl]
            rows = r["rows"]
            p_zero = all(
                all(abs(v) < 1e-12 for v in as_floats(row["pressure_after"]))
                for row in rows
            )
            add(f"F1 freeze {ctl} pressure==[0]*{E}", p_zero)
        # admitted feedback is the constant (c-1)/E; admitted_centered must
        # differ from it only by a common-mode component (formal doc:
        # the two variants coincide on the gauge quotient).
        ra = by_ctl["admitted"]["rows"]
        rb = by_ctl["admitted_centered"]["rows"]
        common_mode_ok = True
        for rowa, rowb in zip(ra, rb):
            fa = as_floats(rowa["feedback"])
            fb = as_floats(rowb["feedback"])
            if not all(abs(v - C_MINUS_ONE_OVER_E) < 1e-12 for v in fa):
                common_mode_ok = False
            diff = [b - a for a, b in zip(fa, fb)]
            if max(diff) - min(diff) > 1e-12:
                common_mode_ok = False
        add("F1 freeze admitted feedback==(c-1)/E and centered differs "
            "by common mode only", common_mode_ok)
        # overflow fixed at aggregate shortage for every controller
        for ctl, r in by_ctl.items():
            ov = [row["total_overflow"] for row in r["rows"]]
            add(f"F1 fixed overflow {ctl}",
                all(v == 512 for v in ov), f"init={ov[0]} final={ov[-1]}")

    if scenario == "slack":
        rq, cr = by_ctl["requested"], by_ctl["capacity_relative"]
        ad, ac = by_ctl["admitted"], by_ctl["admitted_centered"]
        ov0 = rq["rows"][0]["total_overflow"]
        rq_fin = rq["rows"][-1]["total_overflow"]
        ad_fin = ad["rows"][-1]["total_overflow"]
        v0 = rq["rows"][0]["requested_max_violation"]
        rq_vf = rq["rows"][-1]["requested_max_violation"]
        ad_vf = ad["rows"][-1]["requested_max_violation"]
        add("F3 requested cuts overflow", rq_fin <= 0.25 * ov0,
            f"init={ov0} requested_final={rq_fin} admitted_final={ad_fin}")
        add("F3 admitted barely moves", ad_fin >= 0.8 * ov0,
            f"init={ov0} admitted_final={ad_fin}")
        add("F3 requested halves violation", rq_vf <= 0.55 * v0,
            f"init={v0:.4f} requested_final={rq_vf:.4f} admitted_final={ad_vf:.4f}")
        # first routing change: first step where R differs from step 0
        def first_change(r):
            r0 = as_floats(r["rows"][0]["requested_counts"])
            for row in r["rows"]:
                if any(abs(a - b) > 1e-9
                       for a, b in zip(as_floats(row["requested_counts"]), r0)):
                    return row["step"]
            return None
        fc_rq, fc_ad = first_change(rq), first_change(ad)
        add("F3 requested changes earlier than admitted",
            fc_rq is not None and fc_ad is not None and fc_rq < fc_ad,
            f"requested={fc_rq} admitted={fc_ad}")
        _ = (cr, ac)  # used in F2 below

    if scenario == "demand_shift":
        for ctl in ("requested", "admitted", "admitted_centered",
                    "capacity_relative"):
            r = by_ctl[ctl]
            rows = r["rows"]
            before = as_floats(rows[249]["pressure_after"])
            after = as_floats(rows[250]["pressure_before"])
            ok = all(a == b for a, b in zip(before, after))
            add(f"F4 pressure preserved across shift ({ctl})", ok)
        # stale pattern unwinds under requested: range at step 249 vs 499
        r = by_ctl["requested"]
        rows = r["rows"]
        prange = lambda p: max(p) - min(p)
        r249 = prange(as_floats(rows[249]["pressure_after"]))
        r499 = prange(as_floats(rows[-1]["pressure_after"]))
        add("F4 stale pressure unwinds (requested)", r499 < r249,
            f"range step249={r249:.3f} step499={r499:.3f}")

    # F2: gauge equivalence (checked in every scenario where all four ran).
    # Exact bit-equality holds for degenerate (frozen) trajectories; otherwise
    # the common-mode removal is exact in real arithmetic but rounds in
    # floating point, so compare with a tight tolerance.
    rq = by_ctl.get("requested")
    cr = by_ctl.get("capacity_relative")
    ad = by_ctl.get("admitted")
    ac = by_ctl.get("admitted_centered")
    if rq and cr:
        maxdiff = max(
            abs(a - b)
            for r1, r2 in zip(rq["rows"], cr["rows"])
            for a, b in zip(as_floats(r1["pressure_after"]),
                            as_floats(r2["pressure_after"]))
        )
        add("F2 requested==capacity_relative (pressure, tol 1e-9)",
            maxdiff < 1e-9, f"max |diff| = {maxdiff:.3e}")
    if ad and ac:
        maxdiff = max(
            abs(a - b)
            for r1, r2 in zip(ad["rows"], ac["rows"])
            for a, b in zip(as_floats(r1["pressure_after"]),
                            as_floats(r2["pressure_after"]))
        )
        add("F2 admitted==admitted_centered (pressure, tol 1e-9)",
            maxdiff < 1e-9, f"max |diff| = {maxdiff:.3e}")

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", default="results/runs")
    args = ap.parse_args()
    runs = load_runs(Path(args.runs_dir))
    groups = {}
    for r in runs:
        s = r["summary"]
        if s["steps"] != 500:
            continue  # smoke runs excluded
        groups.setdefault(
            (s["scenario"], s["capacity_regime"], s["seed"]), []
        ).append(r)

    failures = 0
    print(f"# Findings verification ({len(groups)} scenario x seed groups)\n")
    for (scenario, cap, seed), grp in sorted(groups.items()):
        if len(grp) != 4:
            print(f"## scenario={scenario} capacity={cap} seed={seed}: "
                  f"SKIP (only {len(grp)} controllers)")
            continue
        res = check_group(sorted(grp, key=lambda r: r["summary"]["controller"]))
        print(f"## scenario={scenario} capacity={cap} seed={seed}")
        for c in res["checks"]:
            mark = "PASS" if c["ok"] else "FAIL"
            line = f"  [{mark}] {c['name']}"
            if c["detail"]:
                line += f" -- {c['detail']}"
            print(line)
            failures += not c["ok"]
        print()
    print(f"{'ALL CHECKS PASSED' if failures == 0 else f'{failures} CHECKS FAILED'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
