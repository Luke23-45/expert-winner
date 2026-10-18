"""Launch paired Megatron-Core training cells with the feedback adapter."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
ADAPTER_DIR = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--megatron-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--nproc-per-node", type=int, required=True)
    parser.add_argument("--profile", choices=("smoke", "paper"), default="smoke")
    parser.add_argument("--data-mode", choices=("mock", "real"), default="mock")
    parser.add_argument("--data-fingerprint", default=None,
                        help="Precomputed dataset/tokenizer manifest digest for the paper profile.")
    parser.add_argument("--steps", type=int, default=None,
                        help="Override training iterations; required for paper profile.")
    parser.add_argument("--execute", action="store_true",
                        help="Actually launch runs. Without this flag, print a manifest only.")
    parser.add_argument("--save-checkpoints", action="store_true",
                        help="Save a final checkpoint for every run; can require substantial storage.")
    parser.add_argument("--megatron-arg", action="append", default=[],
                        help="One additional Megatron CLI argument. Repeat for each token.")
    parser.add_argument("--torchrun-arg", action="append", default=[],
                        help="One extra torchrun argument, e.g. --rdzv-backend=c10d.")
    parser.add_argument("--device-ids", default=None,
                        help="Optional CUDA_VISIBLE_DEVICES value, e.g. 0,1,2,3.")
    return parser.parse_args()


def git_value(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def runtime_metadata() -> dict:
    info = {"python": sys.version, "platform": platform.platform()}
    try:
        import torch
        info.update({"torch": torch.__version__, "cuda_runtime": torch.version.cuda,
                     "cuda_available": torch.cuda.is_available()})
        if torch.cuda.is_available():
            info["gpu_names"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
    except Exception as exc:
        info["torch_probe_error"] = repr(exc)
    try:
        probe = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, check=False)
        info["nvidia_smi"] = probe.stdout.strip() if probe.returncode == 0 else None
    except FileNotFoundError:
        info["nvidia_smi"] = None
    return info


def require_cuda(nproc_per_node: int, device_ids: str | None) -> None:
    if nproc_per_node <= 0:
        raise SystemExit("--nproc-per-node must be positive.")
    if device_ids is not None:
        selected = [item.strip() for item in device_ids.split(",")]
        if not all(selected) or len(set(selected)) != len(selected):
            raise SystemExit("--device-ids must be a comma-separated list of unique, non-empty GPU IDs.")
    try:
        import torch
    except Exception as exc:
        raise SystemExit(f"Cannot import PyTorch in this environment: {exc}") from exc
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is unavailable. This experiment requires NVIDIA GPU training; CPU fallback is disabled.")
    visible = torch.cuda.device_count()
    if visible < nproc_per_node:
        raise SystemExit(
            f"Requested {nproc_per_node} workers but PyTorch sees only {visible} CUDA devices "
            f"after applying CUDA_VISIBLE_DEVICES={device_ids!r}."
        )


def cells(protocol: dict, profile: str) -> list[dict]:
    design = protocol["design"]
    if profile == "smoke":
        result = [
            {**cell, "seed": seed, "steps": design["smoke_profile"]["steps"]}
            for seed in design["smoke_profile"]["seeds"]
            for cell in design["smoke_profile"]["cells"]
        ]
    else:
        seeds = design["paper_profile"]["seeds"]
        all_cells = []
        for capacity in design["factors"]["capacity_factor"]:
            for feedback in ("none", "aux_loss", "native_admitted"):
                all_cells.append({"capacity_factor": capacity, "feedback": feedback, "scope": "global"})
            for feedback in ("requested", "admitted"):
                for scope in ("local", "global"):
                    all_cells.append({"capacity_factor": capacity, "feedback": feedback, "scope": scope})
        steps = design["paper_profile"].get("steps")
        result = [
            {**cell, "seed": seed, "steps": steps}
            for seed in seeds for cell in all_cells
        ]
    for cell in result:
        cell["experts"] = design["model"]["experts"]
        cell["top_k"] = design["model"]["top_k"]
        profile_model = design["smoke_model"] if profile == "smoke" else design["model"]
        cell["sequence_length"] = profile_model["sequence_length"]
        cell["global_batch_size"] = profile_model["global_batch_size"]
    return result


def cell_id(cell: dict) -> str:
    cap = "off" if cell["capacity_factor"] == "disabled" else f"cf{cell['capacity_factor']}"
    return f"seed{cell['seed']}_{cap}_{cell['feedback']}_{cell['scope']}_s{cell['steps']}"


def run_command(cell: dict, args: argparse.Namespace, out: Path) -> list[str]:
    megatron_root = args.megatron_root.resolve()
    train_script = megatron_root / "pretrain_gpt.py"
    if not train_script.is_file():
        raise FileNotFoundError(f"Expected Megatron entry point at {train_script}")
    model = ({"layers": 2, "hidden": 128, "heads": 4, "sequence": 128,
              "micro_batch": 1, "global_batch": 4}
             if args.profile == "smoke" else
             {"layers": 12, "hidden": 768, "heads": 12, "sequence": 2048,
              "micro_batch": 2, "global_batch": 64})
    eval_interval = max(1, min(100, cell["steps"]))
    command = [
        sys.executable, "-m", "torch.distributed.run",
        f"--nproc_per_node={args.nproc_per_node}", *args.torchrun_arg,
        str(train_script),
        "--num-layers", str(model["layers"]), "--hidden-size", str(model["hidden"]),
        "--num-attention-heads", str(model["heads"]),
        "--seq-length", str(model["sequence"]), "--max-position-embeddings", str(model["sequence"]),
        "--micro-batch-size", str(model["micro_batch"]), "--global-batch-size", str(model["global_batch"]),
        "--train-iters", str(cell["steps"]), "--num-experts", "8", "--moe-router-topk", "2",
        "--moe-router-load-balancing-type", "aux_loss", "--seed", str(cell["seed"]), "--log-throughput",
        "--log-interval", "10", "--eval-interval", str(eval_interval), "--eval-iters", "10",
        "--bf16", "--lr", "3e-4", "--min-lr", "3e-5", "--lr-decay-style", "cosine",
        "--lr-warmup-iters", str(max(1, min(100, cell["steps"] // 10))),
        "--weight-decay", "0.1", "--clip-grad", "1.0", "--deterministic-mode",
        "--moe-token-drop-policy", "probs",
    ]
    if args.save_checkpoints:
        command += ["--save", str(out / "checkpoints"), "--save-interval", str(cell["steps"])]
    if args.data_mode == "mock":
        command += ["--mock-data", "--tokenizer-type", "NullTokenizer", "--vocab-size", "32000",
                    "--data-cache-path", str(out / "dataset-cache"), "--split", "99,1,0",
                    "--no-create-attention-mask-in-dataloader"]
    if cell["capacity_factor"] != "disabled":
        command += ["--moe-expert-capacity-factor", str(cell["capacity_factor"])]
    if cell["feedback"] in {"requested", "admitted", "native_admitted"}:
        command += ["--moe-router-enable-expert-bias", "--moe-router-bias-update-rate", "0.001"]
        command += ["--moe-aux-loss-coeff", "0.0"]
    elif cell["feedback"] == "aux_loss":
        command += ["--moe-aux-loss-coeff", "0.01"]
    else:
        command += ["--moe-aux-loss-coeff", "0.0"]
    command += args.megatron_arg
    return command


def main() -> int:
    args = parse_args()
    if args.steps is not None and args.steps <= 0:
        raise SystemExit("--steps must be positive")
    if args.profile == "paper" and args.steps is None:
        raise SystemExit("Set --steps explicitly for the paper profile before launch.")
    if args.profile == "paper" and args.data_mode != "real":
        raise SystemExit("The paper profile requires --data-mode real and explicit tokenizer/data arguments.")
    if args.profile == "paper":
        if not args.data_fingerprint:
            raise SystemExit("Paper profile requires --data-fingerprint for the fixed data/tokenizer snapshot.")
        missing = {"--data-path", "--split", "--tokenizer-type", "--tokenizer-model"} - set(args.megatron_arg)
        if missing:
            raise SystemExit("Paper profile is missing required --megatron-arg values: " + ", ".join(sorted(missing)))
    if args.execute:
        if args.device_ids is not None:
            # Apply the selection before probing PyTorch, so the preflight
            # counts exactly the devices the torchrun workers will see.
            os.environ["CUDA_VISIBLE_DEVICES"] = args.device_ids
        require_cuda(args.nproc_per_node, args.device_ids)
    args.megatron_root = args.megatron_root.resolve()
    expected = "62c063f2b731b57b1c2031b2b4f4c6a769271ccb"
    actual = git_value(args.megatron_root, "rev-parse", "HEAD")
    if actual != expected:
        raise SystemExit(f"Megatron SHA mismatch: expected {expected}, found {actual}")
    megatron_dirty = git_value(args.megatron_root, "status", "--porcelain")
    if megatron_dirty:
        raise SystemExit("Megatron checkout must be clean before running this experiment.")
    protocol_path = ADAPTER_DIR / "protocol.yaml"
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    run_cells = cells(protocol, args.profile)
    if args.steps is not None:
        for cell in run_cells:
            cell["steps"] = args.steps
    if args.execute:
        args.output_root.mkdir(parents=True, exist_ok=True)
        if any(args.output_root.iterdir()):
            raise SystemExit(f"Output directory is not empty; choose a fresh path: {args.output_root}")
    suite_manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "profile": args.profile,
        "megatron_sha": actual,
        "megatron_dirty": False,
        "data_fingerprint": args.data_fingerprint,
        "adapter_sha256": sha256_file(ADAPTER_DIR / "adapter.py"),
        "run_matrix_sha256": sha256_file(ADAPTER_DIR / "run_matrix.py"),
        "analyzer_sha256": sha256_file(ADAPTER_DIR / "analyze.py"),
        "protocol_sha256": sha256_file(protocol_path),
        "runtime": runtime_metadata(),
        "cells": run_cells,
        "dry_run": not args.execute,
    }
    if args.execute:
        (args.output_root / f"suite_{args.profile}.json").write_text(
            json.dumps(suite_manifest, indent=2) + "\n", encoding="utf-8"
        )
    for cell in run_cells:
        out = args.output_root / cell_id(cell)
        command = run_command(cell, args, out)
        env = os.environ.copy()
        env["MEGATRON_ROOT"] = str(args.megatron_root)
        env["MEGATRON_EXPECTED_SHA"] = expected
        env["MOE_FEEDBACK_EXPERIMENT"] = (
            "1" if cell["feedback"] in {"requested", "admitted"} else "0"
        )
        env["MOE_FEEDBACK_SIGNAL"] = cell["feedback"] if cell["feedback"] in {"requested", "admitted"} else "admitted"
        env["MOE_FEEDBACK_SCOPE"] = cell["scope"]
        env["MOE_FEEDBACK_OUTPUT"] = str(out / "telemetry")
        env["PYTHONPATH"] = os.pathsep.join(
            [str(ADAPTER_DIR), str(args.megatron_root), env.get("PYTHONPATH", "")]
        )
        if args.device_ids is not None:
            env["CUDA_VISIBLE_DEVICES"] = args.device_ids
        capture_requested = (
            cell["feedback"] == "requested"
            or (cell["capacity_factor"] == "disabled" and cell["feedback"] == "admitted")
        )
        env["MOE_FEEDBACK_CAPTURE_REQUESTED"] = "1" if capture_requested else "0"
        env["MOE_FEEDBACK_CAPACITY_FACTOR"] = str(cell["capacity_factor"])
        env["MOE_FEEDBACK_RUN_ID"] = cell_id(cell)
        if not args.execute:
            print(shlex.join(command))
            continue
        out.mkdir(parents=True, exist_ok=False)
        (out / "command.txt").write_text(shlex.join(command) + "\n", encoding="utf-8")
        (out / "cell.json").write_text(json.dumps(cell, indent=2) + "\n", encoding="utf-8")
        run_manifest = {
            "run_id": cell_id(cell),
            "cell": cell,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "megatron_sha": actual,
            "adapter_sha256": suite_manifest["adapter_sha256"],
            "protocol_sha256": suite_manifest["protocol_sha256"],
            "runtime": suite_manifest["runtime"],
            "command": command,
            "data_mode": args.data_mode,
            "data_fingerprint": args.data_fingerprint,
            "save_checkpoints": args.save_checkpoints,
            "cuda_visible_devices": env.get("CUDA_VISIBLE_DEVICES"),
            "world_size": args.nproc_per_node,
            "model": ({"layers": 2, "hidden": 128, "heads": 4, "sequence": 128,
                       "micro_batch": 1, "global_batch": 4, "experts": 8, "top_k": 2}
                      if args.profile == "smoke" else
                      {"layers": 12, "hidden": 768, "heads": 12, "sequence": 2048,
                       "micro_batch": 2, "global_batch": 64, "experts": 8, "top_k": 2}),
            "cwd": str(args.megatron_root),
            "git_head": git_value(ROOT, "rev-parse", "HEAD"),
            "git_status": git_value(ROOT, "status", "--short"),
            "status": "running",
        }
        (out / "manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
        with (out / "stdout.log").open("w", encoding="utf-8") as stdout:
            completed = subprocess.run(command, cwd=args.megatron_root, env=env,
                                        stdout=stdout, stderr=subprocess.STDOUT, check=False)
        if completed.returncode != 0:
            run_manifest["status"] = "failed"
            (out / "manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
            raise SystemExit(f"Run {cell_id(cell)} failed; inspect {out / 'stdout.log'}")
        run_manifest["status"] = "completed"
        (out / "manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(run_cells)} cells under {args.output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
