#!/usr/bin/env python3
"""Validate and summarize one central-claim suite artifact directory."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


def load_rows(path: Path) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {line_no}: {exc}") from exc
            grouped[row["run_id"]].append(row)
    return grouped


def total_variation(counts: list[int], kt: int, experts: int) -> float:
    target = 1.0 / experts
    return 0.5 * sum(abs(value / kt - target) for value in counts)


def bootstrap_mean_ci(values: list[float], seed: int, replicates: int) -> tuple[float, float]:
    if not values:
        raise ValueError("Cannot bootstrap an empty sample.")
    rng = random.Random(seed)
    n = len(values)
    means = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(replicates))
    return means[int(0.025 * replicates)], means[min(replicates - 1, int(0.975 * replicates))]


def near(a: float, b: float, tol: float = 1e-12) -> bool:
    return abs(a - b) <= tol


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path, help="Timestamped directory created by run_suite.py")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    protocol_bytes = (run_dir / "protocol.yaml").read_bytes()
    protocol = yaml.safe_load(protocol_bytes)
    with (run_dir / "run_index.csv").open(newline="", encoding="utf-8") as f:
        index_rows = list(csv.DictReader(f))
    runs = load_rows(run_dir / "trajectories.jsonl.gz")

    scope = protocol["claim"]["scope"]
    experts, top_k, tokens = int(scope["experts"]), int(scope["top_k"]), int(scope["tokens"])
    kt = top_k * tokens
    if scope["target"] != "uniform":
        raise ValueError("This analyzer currently requires the declared uniform target.")
    target = [1.0 / experts] * experts
    eta, gamma, delta = (
        float(scope["step_size"]), float(scope["score_gain"]),
        float(scope["pressure_decay"]),
    )
    cap_by_condition = {c["name"]: int(c["capacity_per_expert"]) for c in protocol["conditions"]}
    expected = len(protocol["conditions"]) * int(manifest["seed_count"]) * len(protocol["sampling"]["controllers"])
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, details: Any = None) -> None:
        checks.append({"name": name, "passed": bool(ok), "details": details})

    check("expected_run_count", len(index_rows) == expected and len(runs) == expected,
          {"expected": expected, "index": len(index_rows), "trajectory_runs": len(runs)})
    index_by_run = {r["run_id"]: r for r in index_rows}
    check("unique_run_ids", len(index_by_run) == len(index_rows))
    check("protocol_hash_matches_manifest",
          hashlib.sha256(protocol_bytes).hexdigest() == manifest["protocol_sha256"])
    source_hash_failures = []
    for relative, expected_hash in manifest.get("source_sha256", {}).items():
        snapshot = run_dir / "source_snapshot" / Path(relative)
        if not snapshot.is_file() or hashlib.sha256(snapshot.read_bytes()).hexdigest() != expected_hash:
            source_hash_failures.append(relative)
    check("source_snapshot_hashes", bool(manifest.get("source_sha256")) and not source_hash_failures,
          source_hash_failures)
    check("run_index_matches_trajectories",
          set(index_by_run) == set(runs),
          {"index_only": sorted(set(index_by_run) - set(runs))[:20],
           "trajectory_only": sorted(set(runs) - set(index_by_run))[:20]})
    initial_condition_failures = [
        {"run_id": row["run_id"], "condition": row["condition"]}
        for row in index_rows
        if row["initial_condition_verified"].strip().lower() != "true"
    ]
    check("runner_initial_condition_checks", not initial_condition_failures,
          initial_condition_failures[:30])

    bad_rows: list[dict[str, Any]] = []
    metrics: dict[str, dict[str, Any]] = {}
    by_pair: dict[tuple[str, int], dict[str, list[dict[str, Any]]]] = defaultdict(dict)
    for run_id, rows in runs.items():
        if run_id not in index_by_run or not rows:
            bad_rows.append({"run_id": run_id, "error": "missing index row or empty trajectory"})
            continue
        entry = index_by_run[run_id]
        rows.sort(key=lambda r: int(r["step"]))
        condition, controller, seed = entry["condition"], entry["controller"], int(entry["seed"])
        cap = cap_by_condition[condition]
        if len(rows) != int(entry["steps"]) or [int(r["step"]) for r in rows] != list(range(len(rows))):
            bad_rows.append({"run_id": run_id, "error": "incorrect step sequence"})
        r_tv, overflows, saturated = [], [], []
        max_q = 0.0
        request_count_change = None
        initial_r = rows[0]["requested_counts"]
        previous_after = [0.0] * experts
        for step_index, row in enumerate(rows):
            r = [int(x) for x in row["requested_counts"]]
            a = [int(x) for x in row["admitted_counts"]]
            j = [int(x) for x in row["rejected_counts"]]
            if len(r) != experts or sum(r) != kt or min(r) < 0 or max(r) > tokens:
                bad_rows.append({"run_id": run_id, "step": row["step"], "error": "request mass/range"})
            if a != [min(x, cap) for x in r] or j != [x - y for x, y in zip(r, a)]:
                bad_rows.append({"run_id": run_id, "step": row["step"], "error": "admission identity"})
            if sum(j) != int(row["total_overflow"]):
                bad_rows.append({"run_id": run_id, "step": row["step"], "error": "overflow total"})
            computed_saturated = all(x >= cap for x in r)
            if bool(row["all_experts_saturated"]) != computed_saturated:
                bad_rows.append({"run_id": run_id, "step": row["step"], "error": "saturation flag"})
            if int(row["aggregate_capacity_shortage"]) != kt - experts * cap:
                bad_rows.append({"run_id": run_id, "step": row["step"], "error": "aggregate shortage metric"})

            signal_counts = r if controller == "requested" else a
            expected_feedback = [signal_counts[e] / kt - target[e] for e in range(experts)]
            observed_feedback = [float(x) for x in row["feedback"]]
            if len(observed_feedback) != experts or any(
                not near(observed_feedback[e], expected_feedback[e]) for e in range(experts)
            ):
                bad_rows.append({"run_id": run_id, "step": row["step"], "error": "feedback formula"})

            pressure_before = [float(x) for x in row["pressure_before"]]
            pressure_after = [float(x) for x in row["pressure_after"]]
            if len(pressure_before) != experts or len(pressure_after) != experts:
                bad_rows.append({"run_id": run_id, "step": row["step"], "error": "pressure vector shape"})
            elif any(not near(pressure_before[e], previous_after[e]) for e in range(experts)):
                bad_rows.append({"run_id": run_id, "step": row["step"], "error": "pressure continuity"})
            if len(pressure_before) == experts and len(pressure_after) == experts and len(observed_feedback) == experts:
                raw_next = [
                    (1.0 - delta) * pressure_before[e] + eta * gamma * observed_feedback[e]
                    for e in range(experts)
                ]
                minimum = min(raw_next)
                expected_after = [x - minimum for x in raw_next]
                if any(not near(pressure_after[e], expected_after[e]) for e in range(experts)):
                    bad_rows.append({"run_id": run_id, "step": row["step"], "error": "gauge pressure update"})
                if min(pressure_after) < -1e-12 or abs(min(pressure_after)) > 1e-12:
                    bad_rows.append({"run_id": run_id, "step": row["step"], "error": "gauge representative"})
            previous_after = pressure_after
            r_tv.append(total_variation(r, kt, experts))
            overflows.append(int(row["total_overflow"]))
            saturated.append(computed_saturated)
            max_q = max(max_q, *(abs(float(x)) for x in row["pressure_after"]))
            if request_count_change is None and r != initial_r:
                request_count_change = int(row["step"])
        metrics[run_id] = {
            "condition": condition, "controller": controller, "seed": seed,
            "time_mean_tv": sum(r_tv) / len(r_tv),
            "initial_tv": r_tv[0], "final_tv": r_tv[-1],
            "mean_overflow": sum(overflows) / len(overflows),
            "final_overflow": overflows[-1],
            "saturation_fraction": sum(saturated) / len(saturated),
            "first_request_count_change_step": request_count_change,
            "max_abs_pressure": max_q, "initial_requested": initial_r,
            "rows": rows,
        }
        by_pair[(condition, seed)][controller] = rows
    check("trajectory_invariants", not bad_rows, bad_rows[:30])

    saturation_failures = []
    for condition in ("shortage_c075", "shortage_c050"):
        for (cond, seed), pair in by_pair.items():
            if cond != condition:
                continue
            if set(pair) != {"requested", "admitted"}:
                saturation_failures.append({"condition": cond, "seed": seed, "error": "unpaired controllers"})
                continue
            for row in pair["admitted"]:
                if not all(int(x) >= cap_by_condition[cond] for x in row["requested_counts"]):
                    saturation_failures.append({"condition": cond, "seed": seed, "error": "not globally saturated"})
                if max(abs(float(q)) for q in row["pressure_before"]) > 1e-12:
                    saturation_failures.append({"condition": cond, "seed": seed, "error": "admitted pressure-before not gauge-null"})
                if max(abs(float(q)) for q in row["pressure_after"]) > 1e-12:
                    saturation_failures.append({"condition": cond, "seed": seed, "error": "admitted pressure not gauge-null"})
            if not all(int(x) >= cap_by_condition[cond] for x in pair["requested"][0]["requested_counts"]):
                saturation_failures.append({"condition": cond, "seed": seed, "error": "requested run not globally saturated at step zero"})
            req0 = pair["requested"][0]
            fb = [int(x) / kt - 1.0 / experts for x in req0["requested_counts"]]
            if max(fb) - min(fb) <= 1e-12:
                saturation_failures.append({"condition": cond, "seed": seed, "error": "requested signal was not imbalanced"})
    check("saturated_signal_prediction", not saturation_failures, saturation_failures[:30])

    boundary_failures = []
    for (condition, seed), pair in by_pair.items():
        if condition == "exact_total_boundary":
            expected_counts = [kt // experts] * experts
            for controller, rows in pair.items():
                if rows[0]["requested_counts"] != expected_counts:
                    boundary_failures.append({"condition": condition, "seed": seed, "controller": controller,
                                              "counts": rows[0]["requested_counts"], "expected": expected_counts})
        elif condition == "partial_slack_c1125":
            for controller, rows in pair.items():
                r0 = rows[0]["requested_counts"]
                sat = [int(x) >= cap_by_condition[condition] for x in r0]
                if not any(sat) or all(sat):
                    boundary_failures.append({"condition": condition, "seed": seed, "controller": controller,
                                              "error": "initial condition is not partially saturated", "counts": r0})
    check("boundary_controls", not boundary_failures, boundary_failures[:30])

    no_drop_failures = []
    for (condition, seed), pair in by_pair.items():
        if condition != "no_drop_control":
            continue
        left, right = pair.get("requested"), pair.get("admitted")
        if left is None or right is None:
            no_drop_failures.append({"seed": seed, "error": "missing paired run"})
            continue
        for i, (rrow, arow) in enumerate(zip(left, right)):
            for field in (
                "requested_counts", "admitted_counts", "rejected_counts",
                "pressure_before", "pressure_after", "feedback",
            ):
                x, y = rrow[field], arow[field]
                mismatch = len(x) != len(y) or any(
                    not near(float(a), float(b)) if field == "pressure_after" else a != b
                    for a, b in zip(x, y)
                )
                if mismatch:
                    no_drop_failures.append({"seed": seed, "step": i, "field": field})
                    break
            if int(rrow["total_overflow"]) != 0 or int(arow["total_overflow"]) != 0:
                no_drop_failures.append({"seed": seed, "step": i, "error": "drop under no-drop control"})
    check("no_drop_equivalence", not no_drop_failures, no_drop_failures[:30])

    pairing_failures = []
    for (condition, seed), pair in by_pair.items():
        hashes = {row[0]["affinity_sha256"] for row in pair.values() if row}
        if len(hashes) != 1 or len(pair) != len(protocol["sampling"]["controllers"]):
            pairing_failures.append({"condition": condition, "seed": seed, "hashes": sorted(hashes)})
    check("paired_affinity_identity", not pairing_failures, pairing_failures[:30])

    analysis_cfg = protocol["analysis"]
    paired: list[dict[str, Any]] = []
    for condition in ("shortage_c075", "shortage_c050"):
        diffs = []
        for (cond, seed), pair in sorted(by_pair.items()):
            if cond != condition or "requested" not in pair or "admitted" not in pair:
                continue
            rmetric = metrics[f"{condition}_seed{seed}_requested"]["time_mean_tv"]
            ametric = metrics[f"{condition}_seed{seed}_admitted"]["time_mean_tv"]
            diff = ametric - rmetric
            diffs.append(diff)
            paired.append({
                "condition": condition, "seed": seed,
                "requested_time_mean_tv": rmetric,
                "admitted_time_mean_tv": ametric,
                "admitted_minus_requested_tv": diff,
            })
        if diffs:
            lo, hi = bootstrap_mean_ci(
                diffs, seed=20261018 + len(condition),
                replicates=int(analysis_cfg["bootstrap_replicates"]),
            )
            metrics[f"paired_summary_{condition}"] = {
                "n_seeds": len(diffs),
                "mean_admitted_minus_requested_tv": sum(diffs) / len(diffs),
                "median_admitted_minus_requested_tv": statistics.median(diffs),
                "seeds_favoring_requested": sum(d > 0 for d in diffs),
                "bootstrap_95_percentile_ci": [lo, hi],
                "interpretation": "Positive means requested feedback had lower time-mean TV under this synthetic generator.",
            }

    run_metrics = {
        k: {field: value for field, value in v.items() if field != "rows"}
        for k, v in metrics.items() if not k.startswith("paired_summary_")
    }
    condition_summary: dict[str, dict[str, dict[str, Any]]] = {}
    for condition in cap_by_condition:
        condition_summary[condition] = {}
        for controller in protocol["sampling"]["controllers"]:
            selected = [
                v for v in metrics.values()
                if v.get("condition") == condition and v.get("controller") == controller
            ]
            if not selected:
                continue
            count_change_steps = [v["first_request_count_change_step"] for v in selected
                                  if v["first_request_count_change_step"] is not None]
            condition_summary[condition][controller] = {
                "n_runs": len(selected),
                "mean_time_mean_tv": sum(v["time_mean_tv"] for v in selected) / len(selected),
                "mean_overflow": sum(v["mean_overflow"] for v in selected) / len(selected),
                "mean_saturation_fraction": sum(v["saturation_fraction"] for v in selected) / len(selected),
                "runs_with_request_count_change": len(count_change_steps),
                "mean_first_request_count_change_step": (
                    statistics.mean(count_change_steps) if count_change_steps else None
                ),
                "mean_final_max_violation": sum(
                    max(abs(x / kt - 1.0 / experts) for x in v["rows"][-1]["requested_counts"])
                    for v in selected
                ) / len(selected),
            }
    audit = {
        "suite_id": manifest["suite_id"],
        "protocol_sha256": manifest["protocol_sha256"],
        "device": manifest["device"],
        "diagnostic_overrides_used": manifest["diagnostic_overrides_used"],
        "run_count": len(index_rows),
        "trajectory_row_count": sum(len(rows) for rows in runs.values()),
        "checks": checks,
        "all_checks_passed": all(c["passed"] for c in checks),
        "per_run_metrics": run_metrics,
        "condition_controller_summary": condition_summary,
        "paired_summaries": {k: v for k, v in metrics.items() if k.startswith("paired_summary_")},
        "paired_effect_scope": protocol["analysis"]["inferential_scope"],
        "warning": (
            "Synthetic mechanism evidence only. These runs do not establish real-data "
            "quality, deployed telemetry availability, or universal convergence."
        ),
    }
    (run_dir / "claim_audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    with (run_dir / "paired_effects.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["condition", "seed", "requested_time_mean_tv", "admitted_time_mean_tv",
                  "admitted_minus_requested_tv"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(paired)

    lines = [
        "# Central-claim synthetic audit",
        "",
        f"- Suite: {manifest['suite_id']}",
        f"- Device: {manifest['device']}",
        f"- Runs: {len(index_rows)}; trajectory rows: {audit['trajectory_row_count']}",
        f"- Diagnostic protocol overrides: {manifest['diagnostic_overrides_used']}",
        f"- Invariants: {'PASS' if audit['all_checks_passed'] else 'FAIL'}",
        "",
        "## Checks",
        "",
    ]
    lines += [f"- [{'x' if c['passed'] else ' '}] {c['name']}" for c in checks]
    lines += ["", "## Condition summaries", "",
              "Mean overflow, saturation fraction, and first request-count change are shown separately from load imbalance."]
    for condition, controllers in condition_summary.items():
        lines += ["", f"### {condition}", "",
                  "| Controller | Mean TV | Mean overflow | Saturated-step fraction | Runs with count change | Mean first count-change step |",
                  "|---|---:|---:|---:|---:|---:|"]
        for controller, value in controllers.items():
            first = value["mean_first_request_count_change_step"]
            first_text = "none" if first is None else f"{first:.1f}"
            lines.append(
                f"| {controller} | {value['mean_time_mean_tv']:.6g} | "
                f"{value['mean_overflow']:.6g} | {value['mean_saturation_fraction']:.4f} | "
                f"{value['runs_with_request_count_change']}/{value['n_runs']} | {first_text} |"
            )
    lines += ["", "## Paired shortage results", ""]
    for condition in ("shortage_c075", "shortage_c050"):
        item = metrics.get(f"paired_summary_{condition}")
        if item:
            lo, hi = item["bootstrap_95_percentile_ci"]
            lines.append(
                f"- {condition}: mean admitted-minus-requested TV "
                f"{item['mean_admitted_minus_requested_tv']:.6g}, "
                f"95% seed-bootstrap interval [{lo:.6g}, {hi:.6g}], "
                f"requested lower TV in {item['seeds_favoring_requested']}/{item['n_seeds']} seeds."
            )
    lines += [
        "",
        "## Interpretation limit",
        "",
        audit["warning"],
        "A failed invariant invalidates interpretation until its cause is understood.",
        "A passing suite validates programmed mechanisms under this generator; it does not prove the broader theory or a real-model performance advantage.",
        "",
    ]
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Audit: {'PASS' if audit['all_checks_passed'] else 'FAIL'}")
    print(f"Report: {run_dir / 'report.md'}")
    print(f"Machine-readable audit: {run_dir / 'claim_audit.json'}")
    return 0 if audit["all_checks_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
