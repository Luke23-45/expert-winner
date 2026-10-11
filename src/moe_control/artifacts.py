"""Run artifacts and reproducibility metadata.

Each execution creates one immutable run directory::

    <output_root>/<run_id>/
        config.resolved.yaml      # fully composed Hydra configuration
        manifest.json             # git commit, versions, device, seed, protocol
        metrics.parquet           # one row per step
        summary.json              # aggregate statistics for the run
        affinity_reference.json   # generator parameters + content hash

An existing run is never overwritten: every execution mints a new run ID.
"""

from __future__ import annotations

import datetime as _dt
import json
import platform
import subprocess
import uuid
from pathlib import Path
from typing import Any, Dict, List

import pyarrow as pa
import pyarrow.parquet as pq
import torch
from omegaconf import OmegaConf


def new_run_id(experiment_name: str, scenario: str, controller: str) -> str:
    """Mint a unique, human-readable run ID."""
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    suffix = uuid.uuid4().hex[:8]
    return f"{stamp}-{experiment_name}-{scenario}-{controller}-{suffix}"


def create_run_dir(output_root: str, run_id: str) -> Path:
    """Create the run directory; never reuse or overwrite an existing one."""
    path = Path(output_root) / run_id
    if path.exists():
        # Practically unreachable given UUID suffixes, but the contract is
        # explicit: never overwrite.
        for attempt in range(1, 1000):
            alt = Path(output_root) / f"{run_id}-retry{attempt}"
            if not alt.exists():
                path = alt
                break
        else:
            raise RuntimeError(f"Could not mint a fresh run directory for {run_id}.")
    path.mkdir(parents=True, exist_ok=False)
    return path


def _git_info(repo_root: Path) -> Dict[str, Any]:
    def _run(*args: str) -> str | None:
        try:
            out = subprocess.run(
                ["git", *args], cwd=repo_root, capture_output=True, text=True,
                timeout=10,
            )
            return out.stdout.strip() if out.returncode == 0 else None
        except Exception:
            return None

    commit = _run("rev-parse", "HEAD")
    status = _run("status", "--porcelain")
    return {
        "commit": commit,
        "dirty": None if status is None else bool(status),
        "branch": _run("rev-parse", "--abbrev-ref", "HEAD"),
    }


def build_manifest(
    repo_root: Path,
    seed: int,
    scenario: str,
    controller: str,
    capacity_regime: str,
    protocol_version: str,
    device: str,
    equivalence: Dict[str, Any],
    config_warnings: List[str],
) -> Dict[str, Any]:
    """Assemble the reproducibility manifest for a run."""
    import hydra  # local import: manifest writer only

    manifest = {
        "protocol_version": protocol_version,
        "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "seed": seed,
        "scenario": scenario,
        "controller": controller,
        "capacity_regime": capacity_regime,
        "git": _git_info(repo_root),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "device": device,
        "hydra": hydra.__version__,
        "gauge_equivalence": equivalence,
        "config_warnings": config_warnings,
    }
    if torch.cuda.is_available():
        manifest["cuda_device_name"] = torch.cuda.get_device_name(0)
        manifest["cuda_version"] = torch.version.cuda
    return manifest


def write_run(
    run_dir: Path,
    resolved_config: Any,
    manifest: Dict[str, Any],
    rows: List[Dict[str, Any]],
    summary: Dict[str, Any],
    affinity_reference: Dict[str, Any],
) -> None:
    """Persist all run artifacts. The directory is treated as immutable after."""
    with open(run_dir / "config.resolved.yaml", "w") as f:
        f.write(OmegaConf.to_yaml(resolved_config))
    with open(run_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, run_dir / "metrics.parquet")
    with open(run_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    with open(run_dir / "affinity_reference.json", "w") as f:
        json.dump(affinity_reference, f, indent=2, sort_keys=True)
