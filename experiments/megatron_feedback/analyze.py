"""Validate telemetry invariants and requested/admitted no-drop pairing."""

from __future__ import annotations

import argparse
import csv
import json
import re
import math
from collections import defaultdict
from pathlib import Path


VALIDATION_RE = re.compile(
    r"\bvalidation\s+loss\s+at\s+iteration\s+(\d+)[^\n]*?"
    r"lm loss value:\s*([0-9.eE+-]+)", re.IGNORECASE
)
STEP_TIME_RE = re.compile(r"iteration\s+(\d+)\s*/[^\n]*?elapsed time per iteration \(ms\):\s*([0-9.eE+-]+)")
TRAIN_LOSS_RE = re.compile(r"iteration\s+(\d+)\s*/[^\n]*?lm loss:\s*([0-9.eE+-]+)")


def load_run(path: Path) -> tuple[dict, dict[tuple[int, int], dict]]:
    cell = json.loads((path / "cell.json").read_text(encoding="utf-8"))
    grouped: dict[tuple[int, int], dict] = defaultdict(
        lambda: {"requested": None, "admitted": None, "capacity": None,
                 "bias_before": None, "bias_after": None, "rank_rows": 0}
    )
    telemetry = path / "telemetry"
    for file in sorted(telemetry.glob("rank*_layers.jsonl")):
        with file.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                key = (int(row["step"]), int(row["layer"] or -1))
                item = grouped[key]
                req = row["requested_local"]
                adm = row["admitted_local"]
                cap = row.get("capacity_local")
                if item["admitted"] is None:
                    item["admitted"] = [0] * len(adm)
                if req is not None and item["requested"] is None:
                    item["requested"] = [0] * len(req)
                if ((req is not None and len(req) != len(item["requested"]))
                        or len(adm) != len(item["admitted"])):
                    raise ValueError(f"Expert dimension changes inside {path}")
                if req is not None:
                    item["requested"] = [a + int(b) for a, b in zip(item["requested"], req)]
                item["admitted"] = [a + int(b) for a, b in zip(item["admitted"], adm)]
                if cap is not None:
                    if item["capacity"] is None:
                        item["capacity"] = [0] * len(cap)
                    item["capacity"] = [a + int(b) for a, b in zip(item["capacity"], cap)]
                if item["bias_before"] is not None and (
                    item["bias_before"] != row["bias_before"] or item["bias_after"] != row["bias_after"]
                ):
                    item["bias_disagreement"] = True
                item["bias_before"] = row["bias_before"]
                item["bias_after"] = row["bias_after"]
                item["rank_rows"] += 1
    return cell, grouped


def parse_training_log(path: Path) -> tuple[list[dict], list[dict]]:
    log = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    validation = [
        {"iteration": int(step), "validation_nll": float(loss)}
        for step, loss in VALIDATION_RE.findall(log)
    ]
    training = []
    times = {int(step): float(ms) for step, ms in STEP_TIME_RE.findall(log)}
    losses = {int(step): float(loss) for step, loss in TRAIN_LOSS_RE.findall(log)}
    for step in sorted(set(times) | set(losses)):
        training.append({"iteration": step, "step_time_ms": times.get(step), "training_nll": losses.get(step)})
    return validation, training


def load_shape_metrics(counts: list[int] | None) -> tuple[float | None, float | None]:
    if counts is None or not counts or sum(counts) <= 0:
        return None, None
    total = float(sum(counts))
    probabilities = [value / total for value in counts if value > 0]
    entropy = -sum(p * math.log(p) for p in probabilities)
    mean = total / len(counts)
    variance = sum((value - mean) ** 2 for value in counts) / len(counts)
    return entropy, math.sqrt(variance) / mean if mean else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs_root", type=Path)
    args = parser.parse_args()
    if not args.runs_root.is_dir():
        parser.error(
            f"runs directory does not exist: {args.runs_root}. "
            "Run the smoke launcher successfully before analyzing its outputs."
        )
    runs = {}
    for run_path in sorted(args.runs_root.iterdir()):
        if not run_path.is_dir() or not (run_path / "cell.json").is_file():
            continue
        cell, rows = load_run(run_path)
        key = (int(cell["seed"]), str(cell["capacity_factor"]), str(cell["scope"]), str(cell["feedback"]))
        runs[key] = (run_path, cell, rows)

    summary = {"runs": len(runs), "violations": [], "no_drop_pairs": 0, "rows": 0}
    if len(runs) == 0:
        summary["violations"].append({"error": "no run cell metadata found"})
    flat_rows = []
    training_summaries = []
    training_rows = []
    final_validation_by_cell = {}
    for key, (run_path, cell, rows) in runs.items():
        validation, training = parse_training_log(run_path / "stdout.log")
        if validation:
            final_validation = validation[-1]
            sorted_times = sorted(row["step_time_ms"] for row in training if row["step_time_ms"] is not None)
            tail = sorted_times[len(sorted_times) // 2:]
            median_tail_ms = (tail[len(tail) // 2] if tail else None)
            training_summaries.append({
                "run_id": run_path.name,
                "seed": cell["seed"],
                "capacity_factor": cell["capacity_factor"],
                "feedback": cell["feedback"],
                "scope": cell["scope"],
                "validation_iteration": final_validation["iteration"],
                "validation_nll": final_validation["validation_nll"],
                "median_tail_step_time_ms": median_tail_ms,
            })
            final_validation_by_cell[key] = final_validation
            for row in validation:
                training_rows.append({"run_id": run_path.name, "seed": cell["seed"],
                                      "metric": "validation_nll", **row})
        else:
            summary["violations"].append({"run": run_path.name, "error": "validation loss not found in stdout.log"})
        for row in training:
            training_rows.append({"run_id": run_path.name, "seed": cell["seed"],
                                  "metric": "training",
                                  "tokens_per_second": (
                                      cell.get("global_batch_size", 0) * cell.get("sequence_length", 0)
                                      / (row["step_time_ms"] / 1000.0)
                                      if row["step_time_ms"] else None
                                  ), **row})
        for (step, layer), item in sorted(rows.items()):
            requested, admitted = item["requested"], item["admitted"]
            capacity = item["capacity"]
            summary["rows"] += 1
            if item.get("bias_disagreement"):
                summary["violations"].append({"run": run_path.name, "step": step, "layer": layer,
                                               "error": "replicated bias values differ across ranks"})
            if requested is not None and any(a > r for r, a in zip(requested, admitted)):
                summary["violations"].append({"run": run_path.name, "step": step, "layer": layer,
                                               "error": "admitted count exceeds requested count"})
            if capacity is not None and any(a > c for a, c in zip(admitted, capacity)):
                summary["violations"].append({"run": run_path.name, "step": step, "layer": layer,
                                               "error": "admitted count exceeds accumulated capacity"})
            top_k = int(cell.get("top_k", 2))
            if requested is not None and sum(requested) % top_k:
                summary["violations"].append({"run": run_path.name, "step": step, "layer": layer,
                                               "error": f"requested assignments not divisible by top-k={top_k}"})
            if cell["capacity_factor"] == "disabled" and requested is not None and requested != admitted:
                summary["violations"].append({"run": run_path.name, "step": step, "layer": layer,
                                               "error": "drop-off requested/admitted counts differ"})
            req_entropy, req_cv = load_shape_metrics(requested)
            adm_entropy, adm_cv = load_shape_metrics(admitted)
            flat_rows.append({
                "run_id": run_path.name, "seed": cell["seed"], "capacity_factor": cell["capacity_factor"],
                "feedback": cell["feedback"], "scope": cell["scope"], "step": step, "layer": layer,
                "requested_total": None if requested is None else sum(requested),
                "admitted_total": sum(admitted),
                "dropped_assignments": None if requested is None else sum(requested) - sum(admitted),
                "drop_fraction": (None if requested is None or sum(requested) == 0 else
                                  (sum(requested) - sum(admitted)) / sum(requested)),
                "requested_entropy": req_entropy,
                "admitted_entropy": adm_entropy,
                "requested_load_cv": req_cv,
                "admitted_load_cv": adm_cv,
                "capacity_total": None if capacity is None else sum(capacity),
                "fraction_experts_at_capacity": (
                    None if capacity is None else
                    sum(int(a >= c) for a, c in zip(admitted, capacity)) / len(capacity)
                ),
                "requested_counts": json.dumps(requested), "admitted_counts": json.dumps(admitted),
                "bias_before": json.dumps(item["bias_before"]), "bias_after": json.dumps(item["bias_after"]),
                "rank_rows": item["rank_rows"],
            })

    # Mandatory negative control: paired requested/admitted global-scope arms
    # must have identical telemetry and bias paths when the capacity gate is off.
    no_drop_keys = [key for key in runs if key[1] == "disabled" and key[2] == "global"
                    and key[3] in {"requested", "admitted"}]
    for seed in sorted({key[0] for key in no_drop_keys}):
        r_key = (seed, "disabled", "global", "requested")
        a_key = (seed, "disabled", "global", "admitted")
        if r_key not in runs or a_key not in runs:
            continue
        r_rows, a_rows = runs[r_key][2], runs[a_key][2]
        if r_rows.keys() != a_rows.keys():
            summary["violations"].append({"seed": seed, "error": "paired no-drop run step/layer keys differ"})
            continue
        for key in r_rows:
            if (r_rows[key]["requested"] != a_rows[key]["requested"]
                    or r_rows[key]["admitted"] != a_rows[key]["admitted"]
                    or r_rows[key]["bias_after"] != a_rows[key]["bias_after"]):
                summary["violations"].append({"seed": seed, "step": key[0], "layer": key[1],
                                               "error": "paired no-drop controller trajectories differ"})
                break
        summary["no_drop_pairs"] += 1
    if summary["no_drop_pairs"] == 0:
        summary["violations"].append({"error": "no paired requested/admitted drop-off control found"})

    if flat_rows:
        with (args.runs_root / "telemetry_summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(flat_rows[0]))
            writer.writeheader()
            writer.writerows(flat_rows)
    if training_summaries:
        with (args.runs_root / "training_summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(training_summaries[0]))
            writer.writeheader()
            writer.writerows(training_summaries)
    if training_rows:
        fields = sorted({name for row in training_rows for name in row})
        with (args.runs_root / "training_curves.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(training_rows)
    paired_effects = []
    conditions = {(key[0], key[1], key[2]) for key in final_validation_by_cell}
    for seed, capacity_factor, scope in sorted(conditions):
        requested_key = (seed, capacity_factor, scope, "requested")
        admitted_key = (seed, capacity_factor, scope, "admitted")
        if requested_key not in final_validation_by_cell or admitted_key not in final_validation_by_cell:
            continue
        requested_val = final_validation_by_cell[requested_key]
        admitted_val = final_validation_by_cell[admitted_key]
        if requested_val["iteration"] != admitted_val["iteration"]:
            summary["violations"].append({"seed": seed, "capacity_factor": capacity_factor,
                                           "scope": scope, "error": "paired runs evaluated at different iterations"})
            continue
        paired_effects.append({
            "seed": seed,
            "capacity_factor": capacity_factor,
            "scope": scope,
            "validation_iteration": requested_val["iteration"],
            "requested_validation_nll": requested_val["validation_nll"],
            "admitted_validation_nll": admitted_val["validation_nll"],
            "requested_minus_admitted_nll": requested_val["validation_nll"] - admitted_val["validation_nll"],
        })
    if paired_effects:
        with (args.runs_root / "paired_validation_effects.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(paired_effects[0]))
            writer.writeheader()
            writer.writerows(paired_effects)
    (args.runs_root / "telemetry_checks.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 1 if summary["violations"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
