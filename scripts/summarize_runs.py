#!/usr/bin/env python3
"""Summarize control-experiment runs from their immutable artifacts.

Reads every run directory under results/runs/ (config.resolved.yaml,
manifest.json, metrics.parquet, summary.json, affinity_reference.json)
and prints markdown tables comparing controllers within each scenario.

Usage:
    .venv/bin/python scripts/summarize_runs.py [--runs-dir results/runs]

All values are recomputed from the saved per-step rows; nothing is copied
by hand.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pyarrow.parquet as pq


def load_runs(runs_dir: Path):
    runs = []
    for run_dir in sorted(runs_dir.iterdir()):
        metrics_path = run_dir / "metrics.parquet"
        if not metrics_path.exists():
            continue
        rows = pq.read_table(metrics_path).to_pylist()
        summary = json.loads((run_dir / "summary.json").read_text())
        manifest = json.loads((run_dir / "manifest.json").read_text())
        affinity = json.loads((run_dir / "affinity_reference.json").read_text())
        # step_size is not in summary.json; read it from the resolved config.
        # It is part of the experiment identity: runs that differ only in
        # eta must not be grouped together.
        eta = None
        cfg_path = run_dir / "config.resolved.yaml"
        if cfg_path.exists():
            m = re.search(r"step_size:\s*([\d.]+)", cfg_path.read_text())
            if m:
                eta = float(m.group(1))
        runs.append(
            {
                "run_id": run_dir.name,
                "rows": rows,
                "summary": summary,
                "manifest": manifest,
                "affinity": affinity,
                "eta": eta,
            }
        )
    return runs


def key_of(run):
    s = run["summary"]
    return (s["scenario"], s["capacity_regime"], s["controller"], s["seed"])


def series(rows, col):
    return [r[col] for r in rows]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", default="results/runs")
    ap.add_argument("--only", default=None,
                    help="only runs whose run_id contains this substring")
    args = ap.parse_args()

    runs = load_runs(Path(args.runs_dir))
    if args.only:
        runs = [r for r in runs if args.only in r["run_id"]]
    if not runs:
        print("No runs found.")
        return

    # Group by (scenario, capacity_regime, seed, steps, eta); controllers
    # compared inside. Steps and eta are part of the group key so the
    # 500-step matrix and the 2000-step eta sweep never share a table.
    groups = {}
    for r in runs:
        s = r["summary"]
        groups.setdefault(
            (s["scenario"], s["capacity_regime"], s["seed"], s["steps"],
             r["eta"]), []
        ).append(r)

    print(f"# Run summary ({len(runs)} runs)\n")
    for (scenario, cap_regime, seed, steps, eta), grp in sorted(
            groups.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2],
                                             kv[0][3], kv[0][4] or 0)):
        grp = sorted(grp, key=lambda r: r["summary"]["controller"])
        print(f"## scenario={scenario} capacity={cap_regime} seed={seed} "
              f"steps={steps} eta={eta}\n")
        hashes = {r["affinity"].get("content_hash_sha256",
                                    r["affinity"].get("content_hash_sha256_before"))
                  for r in grp}
        print(f"Paired affinity batch shared across controllers: "
              f"{'yes' if len(hashes) == 1 else 'NO -> ' + str(hashes)}\n")
        print("| controller | sat. frac | init max viol | final max viol | "
              "min max viol | init overflow | final overflow | max |p_after| |")
        print("|---|---|---|---|---|---|---|---|")
        for r in grp:
            rows = r["rows"]
            s = r["summary"]
            viol = series(rows, "requested_max_violation")
            overflow = series(rows, "total_overflow")
            pmax = [max(p) for p in series(rows, "pressure_after")]
            print(
                f"| {s['controller']} | "
                f"{s['fraction_steps_saturated']:.3f} | "
                f"{viol[0]:.4f} | {viol[-1]:.4f} | {min(viol):.4f} | "
                f"{overflow[0]} | {overflow[-1]} | {max(pmax):.4f} |"
            )
        print()
        # Saturation-freeze diagnostic: is pressure differentiating?
        print("Pressure range (max-min across experts) at final step:")
        for r in grp:
            p = r["rows"][-1]["pressure_after"]
            print(f"  {r['summary']['controller']}: {max(p) - min(p):.6f}")
        print()


if __name__ == "__main__":
    main()
