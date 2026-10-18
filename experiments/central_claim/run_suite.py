#!/usr/bin/env python3
"""Run the preregistered synthetic audit of the capacity-censoring claim.

The production run is paired by seed: each controller sees the same affinity
tensor, capacity, and zero initial pressure. Artifacts go to a new directory
and are never overwritten. This is a mechanism audit, not a model-quality test.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import yaml
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from moe_control.capacity.per_expert import CanonicalCapacityPolicy
from moe_control.controllers.base import build_controller
from moe_control.reproducibility import enable_deterministic_mode, seed_all
from moe_control.runner import RunContext, run_experiment
from moe_control.scenarios.synthetic import SyntheticScenario


def weak_composition(total: int, parts: int, rng: random.Random) -> list[int]:
    """Uniformly sample a weak composition by choosing bar positions."""
    bars = sorted(rng.sample(range(total + parts - 1), parts - 1))
    cuts = [-1, *bars, total + parts - 1]
    return [cuts[i + 1] - cuts[i] - 1 for i in range(parts)]


def group_profile(kind: str, seed: int, capacity: int, tokens: int) -> list[int]:
    rng = random.Random((seed << 16) ^ capacity ^ 0x5EED_C0DE)
    if kind == "balanced":
        if tokens % 4:
            raise ValueError("Balanced profile requires T divisible by four.")
        return [tokens // 4] * 4
    if kind == "saturated_imbalanced":
        # A 32-token margin absorbs small affinity-induced count changes;
        # realized saturation is still audited from the routed batch.
        floor = capacity + 32
        remaining = tokens - 4 * floor
        if remaining < 0:
            raise ValueError("Capacity is too large for saturated profile.")
        for _ in range(100_000):
            profile = [floor + x for x in weak_composition(remaining, 4, rng)]
            if max(profile) - min(profile) >= 32:
                return profile
        raise RuntimeError("Could not sample saturated imbalanced profile.")
    if kind == "partial_saturation":
        for _ in range(100_000):
            profile = weak_composition(tokens, 4, rng)
            if max(profile) >= capacity + 16 and min(profile) <= capacity - 16:
                return profile
        raise RuntimeError("Could not sample partial-saturation profile.")
    raise ValueError(f"Unknown profile kind: {kind}")


def git_value(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def experiment_sources() -> list[Path]:
    paths = [
        Path(__file__).resolve(),
        Path(__file__).with_name("analyze_suite.py").resolve(),
        (ROOT / "pyproject.toml").resolve(),
        *sorted((ROOT / "src" / "moe_control").rglob("*.py")),
    ]
    return paths


def snapshot_sources(destination: Path) -> dict[str, str]:
    hashes = {}
    for source in experiment_sources():
        relative = source.relative_to(ROOT)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        hashes[relative.as_posix()] = hashlib.sha256(source.read_bytes()).hexdigest()
    return hashes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=Path(__file__).with_name("protocol.yaml"))
    parser.add_argument("--output-root", type=Path, default=Path(__file__).parent / "results")
    parser.add_argument(
        "--device", choices=("cpu", "cuda"), default="cpu",
    )
    parser.add_argument(
        "--seed-count", type=int,
        help="Diagnostic override; default is the preregistered 50 seeds.",
    )
    parser.add_argument(
        "--step-limit", type=int,
        help="Diagnostic override; caps steps and is recorded in the manifest.",
    )
    args = parser.parse_args()

    protocol_path = args.protocol.resolve()
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    sampling = protocol["sampling"]
    scope = protocol["claim"]["scope"]
    seed_count = int(sampling["seed_count"]) if args.seed_count is None else args.seed_count
    if seed_count < 1:
        parser.error("--seed-count must be positive")
    if args.step_limit is not None and args.step_limit < 1:
        parser.error("--step-limit must be positive")
    if args.device == "cuda" and not torch.cuda.is_available():
        parser.error("CUDA requested but torch.cuda.is_available() is false")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output_root.resolve() / run_id
    output.mkdir(parents=True, exist_ok=False)
    source_hashes = snapshot_sources(output / "source_snapshot")
    torch_device = torch.device(args.device)
    seed_all(int(sampling["seed_start"]))
    enable_deterministic_mode()

    protocol_bytes = protocol_path.read_bytes()
    manifest = {
        "suite_id": run_id,
        "protocol": str(protocol_path),
        "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
        "source_sha256": source_hashes,
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_status_porcelain": git_value("status", "--porcelain"),
        "python": sys.version,
        "torch": torch.__version__,
        "numpy": np.__version__,
        "pyyaml": yaml.__version__,
        "cuda_runtime": torch.version.cuda,
        "cuda_device": torch.cuda.get_device_name(0) if args.device == "cuda" else None,
        "device": args.device,
        "seed_start": int(sampling["seed_start"]),
        "seed_count": seed_count,
        "protocol_seed_count": int(sampling["seed_count"]),
        "step_limit_override": args.step_limit,
        "diagnostic_overrides_used": (
            seed_count != int(sampling["seed_count"]) or args.step_limit is not None
        ),
        "claim_statement": protocol["claim"]["statement"],
        "inferential_scope": protocol["analysis"]["inferential_scope"],
    }
    write_json(output / "manifest.json", manifest)
    (output / "protocol.yaml").write_bytes(protocol_bytes)

    experts, top_k, tokens = (
        int(scope["experts"]), int(scope["top_k"]), int(scope["tokens"])
    )
    target = torch.full((experts,), 1.0 / experts, dtype=torch.float64)
    conditions = protocol["conditions"]
    primary = next(c for c in conditions if c["name"] == "shortage_c075")
    no_drop = next(c for c in conditions if c["group_profile"] == "paired_with_shortage_c075")
    seeds = [int(sampling["seed_start"]) + i for i in range(seed_count)]
    primary_profiles = {
        seed: group_profile(
            primary["group_profile"], seed, int(primary["capacity_per_expert"]), tokens
        )
        for seed in seeds
    }
    profiles: dict[str, dict[int, list[int]]] = {
        "shortage_c075": primary_profiles,
        no_drop["name"]: primary_profiles,
    }
    for condition in conditions:
        if condition["name"] in profiles:
            continue
        profiles[condition["name"]] = {
            seed: group_profile(
                condition["group_profile"], seed,
                int(condition["capacity_per_expert"]), tokens,
            )
            for seed in seeds
        }

    index_rows: list[dict[str, Any]] = []
    trajectory_path = output / "trajectories.jsonl.gz"
    total_runs = len(conditions) * seed_count * len(sampling["controllers"])
    completed = 0
    with gzip.open(trajectory_path, "wt", encoding="utf-8", newline="\n") as trajectories:
        for condition in conditions:
            name = condition["name"]
            cap = int(condition["capacity_per_expert"])
            capacity = torch.full((experts,), cap, dtype=torch.int64)
            planned_steps = int(condition["steps"])
            steps = min(planned_steps, args.step_limit) if args.step_limit else planned_steps
            for seed in seeds:
                profile = profiles[name][seed]
                scenario = SyntheticScenario(
                    name=f"central_claim_{name}", seed=seed, tokens=tokens,
                    experts=experts, group_sizes=profile,
                    noise_scale=float(condition.get("noise_scale", sampling.get("noise_scale", 0.1))),
                    affinity_dtype="float32",
                )
                reference = scenario.reference()
                for controller_name in sampling["controllers"]:
                    run_name = f"{name}_seed{seed}_{controller_name}"
                    initial_condition = (
                        "all_saturated"
                        if condition["group_profile"] == "saturated_imbalanced"
                        else "balanced"
                        if condition["group_profile"] == "balanced"
                        else "unconstrained"
                    )
                    ctx = RunContext(
                        run_id=run_name, seed=seed, scenario_name=name,
                        controller_name=controller_name, capacity_regime=name,
                        steps=steps, experts=experts, top_k=top_k, tokens=tokens,
                        gamma=float(scope["score_gain"]), score_sign=-1.0,
                        eta=float(scope["step_size"]), delta=float(scope["pressure_decay"]),
                        update_gain=float(scope["score_gain"]), projection="gauge",
                        target=target, capacity=capacity,
                        initial_condition=initial_condition,
                        device=torch_device, float_dtype=torch.float32,
                    )
                    rows, summary = run_experiment(
                        ctx, scenario, build_controller(controller_name),
                        CanonicalCapacityPolicy(), progress_every=0,
                    )
                    for row in rows:
                        row["condition"] = name
                        row["role"] = condition["role"]
                        row["affinity_sha256"] = reference["content_hash_sha256"]
                        trajectories.write(json.dumps(row, separators=(",", ":")) + "\n")
                    index_rows.append({
                        "run_id": run_name, "condition": name,
                        "role": condition["role"], "seed": seed,
                        "controller": controller_name, "steps": steps,
                        "planned_steps": planned_steps, "capacity_per_expert": cap,
                        "capacity_ratio": condition["capacity_ratio"],
                        "group_sizes": json.dumps(profile),
                        "affinity_sha256": reference["content_hash_sha256"],
                        "initial_condition_verified": summary["initial_condition"]["verified"],
                        "realized_initial_counts": json.dumps(
                            summary["initial_condition"].get("realized_requested")
                        ),
                    })
                    completed += 1
                    print(f"[{completed}/{total_runs}] {run_name}", flush=True)

    with (output / "run_index.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(index_rows[0]))
        writer.writeheader()
        writer.writerows(index_rows)
    print(f"Completed {completed} runs. Artifacts: {output}")
    print("Run analyze_suite.py on this directory before interpreting results.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
