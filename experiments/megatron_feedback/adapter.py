"""Version-guarded requested/admitted feedback adapter for Megatron-Core.

This module is loaded by ``sitecustomize.py`` in every torchrun process. It
wraps the pinned TopKRouter call path to record requested assignments before
capacity dropping and admitted assignments after dropping, then replaces only
the existing expert-bias update at the finalize-model-grads boundary.

The adapter intentionally targets one exact Megatron-LM commit. Megatron's
router and training-finalization internals are not a stable plugin API.
"""

from __future__ import annotations

import contextvars
import json
import os
import subprocess
import atexit
import importlib
import weakref
from pathlib import Path
from typing import Any

import torch

PINNED_MEGATRON_SHA = "62c063f2b731b57b1c2031b2b4f4c6a769271ccb"
_ACTIVE_ROUTER: contextvars.ContextVar[tuple[Any, torch.Tensor | None] | None] = (
    contextvars.ContextVar("moe_feedback_active_router", default=None)
)
_INSTALLED = False
_MODULES: weakref.WeakSet[Any] = weakref.WeakSet()


def _source_checkout_sha(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def _has_only_expected_megatron_compat_patch(root: Path) -> bool:
    """Accept the launcher's exact autograd-safe patch, and no other edits."""
    patch_path = Path(__file__).resolve().parent / "patches" / "megatron-mlp-view-safe-output-bias.patch"
    status = subprocess.check_output(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
        text=True,
    ).splitlines()
    if status != [" M megatron/core/transformer/mlp.py"]:
        return False
    diff = subprocess.check_output(
        ["git", "-C", str(root), "diff", "--binary", "--no-ext-diff"],
    )
    return diff == patch_path.read_bytes()


def _count_routes(routing_map: torch.Tensor, padding_mask: torch.Tensor | None) -> torch.Tensor:
    """Count valid token-expert assignments for bool maps or dense top-k IDs."""
    n_experts = getattr(_ACTIVE_ROUTER.get()[0].config, "num_moe_experts")
    valid_rows = None if padding_mask is None else ~padding_mask.reshape(-1).bool()
    if routing_map.dtype == torch.bool:
        selected = routing_map
        if valid_rows is not None:
            selected = selected & valid_rows.unsqueeze(-1)
        return selected.sum(dim=0, dtype=torch.int64)

    indices = routing_map.long()
    valid = indices.ge(0)
    if valid_rows is not None:
        valid &= valid_rows.unsqueeze(-1)
    safe_indices = indices.masked_fill(~valid, 0).reshape(-1)
    weights = valid.reshape(-1).to(torch.int64)
    return torch.zeros(n_experts, dtype=torch.int64, device=indices.device).scatter_add_(
        0, safe_indices, weights
    )


def _accumulate(module: Any, attr: str, value: torch.Tensor) -> None:
    current = getattr(module, attr, None)
    if current is None:
        setattr(module, attr, value.detach().clone())
    else:
        current.add_(value.detach())


def _append_record(module: Any, step: int, requested: torch.Tensor | None,
                   admitted: torch.Tensor, bias_before: torch.Tensor,
                   bias_after: torch.Tensor, scope: str, signal: str,
                   capacity: torch.Tensor | None) -> None:
    """Persist rank-local telemetry; do not add a telemetry collective."""
    out = Path(os.environ["MOE_FEEDBACK_OUTPUT"])
    out.mkdir(parents=True, exist_ok=True)
    rank = int(os.environ.get("RANK", "0"))
    layer = getattr(module, "layer_number", None)
    arm = os.environ.get("MOE_FEEDBACK_ARM", signal)
    rows = getattr(module, "_cf_pending_rows", None)
    if rows is None:
        rows = []
        module._cf_pending_rows = rows
    rows.append({
        "step": step,
        "rank": rank,
        "layer": layer,
        "signal": signal,
        "arm": arm,
        "scope": scope,
        "requested_local": None if requested is None else requested.detach().cpu().tolist(),
        "admitted_local": admitted.detach().cpu().tolist(),
        "capacity_local": None if capacity is None else capacity.detach().cpu().tolist(),
        "bias_before": bias_before.detach().float().cpu().tolist(),
        "bias_after": bias_after.detach().float().cpu().tolist(),
    })
    # Bound host memory on long runs while amortizing synchronous D2H copies.
    if len(rows) >= 128:
        _flush_rows(module, out)


def _flush_rows(module: Any, out: Path | None = None) -> None:
    rows = getattr(module, "_cf_pending_rows", None)
    if not rows:
        return
    out = out or Path(os.environ["MOE_FEEDBACK_OUTPUT"])
    rank = int(os.environ.get("RANK", "0"))
    path = out / f"rank{rank:05d}_layers.jsonl"
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    rows.clear()


def _collect_router_modules(model: list[torch.nn.Module], get_wrapped: Any) -> list[Any]:
    result = []
    for chunk in model:
        for module in get_wrapped(chunk, "modules")():
            if getattr(module, "expert_bias", None) is not None and module.training:
                result.append(module)
    return result


def install() -> None:
    """Install guarded hooks. Called once from sitecustomize on every rank."""
    global _INSTALLED
    if _INSTALLED or os.environ.get("MOE_FEEDBACK_EXPERIMENT") != "1":
        return
    signal = os.environ.get("MOE_FEEDBACK_SIGNAL", "admitted")
    scope = os.environ.get("MOE_FEEDBACK_SCOPE", "global")
    if signal not in {"requested", "admitted"}:
        raise ValueError("MOE_FEEDBACK_SIGNAL must be requested or admitted")
    if scope not in {"local", "global"}:
        raise ValueError("MOE_FEEDBACK_SCOPE must be local or global")
    root = Path(os.environ["MEGATRON_ROOT"]).resolve()
    actual_sha = _source_checkout_sha(root)
    dirty = subprocess.check_output(
        ["git", "-C", str(root), "status", "--porcelain"], text=True
    ).strip()
    expected_sha = os.environ.get("MEGATRON_EXPECTED_SHA", PINNED_MEGATRON_SHA)
    if actual_sha != expected_sha:
        raise RuntimeError(
            f"Unsupported Megatron checkout {actual_sha}; adapter expects {expected_sha}. "
            "Review the source changes and update the adapter deliberately."
        )
    if dirty and not _has_only_expected_megatron_compat_patch(root):
        raise RuntimeError(
            "Megatron checkout has unrecognized changes; only the exact experiment compatibility "
            "patch is allowed. Restore other edits before running."
        )
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable in this worker; the experiment does not permit CPU fallback")

    router_module = importlib.import_module("megatron.core.transformer.moe.router")
    moe_utils = importlib.import_module("megatron.core.transformer.moe.moe_utils")
    finalize_module = importlib.import_module("megatron.core.distributed.finalize_model_grads")
    from megatron.core.utils import get_attr_wrapped_model

    RouterClass = router_module.TopKRouter
    if getattr(RouterClass, "_moe_feedback_adapter_installed", False):
        _INSTALLED = True
        return
    original_routing = RouterClass.routing
    original_apply_expert_bias = RouterClass._apply_expert_bias
    original_drop = router_module.apply_router_token_dropping

    def routing_with_context(self, logits, padding_mask=None, *args, **kwargs):
        token = _ACTIVE_ROUTER.set((self, padding_mask))
        try:
            return original_routing(self, logits, padding_mask, *args, **kwargs)
        finally:
            _ACTIVE_ROUTER.reset(token)

    def drop_with_request_capture(routing_probs, routing_map, *args, **kwargs):
        active = _ACTIVE_ROUTER.get()
        if active is not None and torch.is_grad_enabled():
            module, padding_mask = active
            factor = module.config.moe_expert_capacity_factor
            if factor is not None:
                capacity = moe_utils.get_capacity(
                    num_tokens=routing_probs.shape[0] * module.topk,
                    num_experts=module.config.num_moe_experts,
                    capacity_factor=factor,
                )
                _accumulate(
                    module,
                    "_cf_capacity_counts",
                    torch.full((module.config.num_moe_experts,), capacity,
                               dtype=torch.int64, device=routing_map.device),
                )
            if os.environ.get("MOE_FEEDBACK_CAPTURE_REQUESTED") == "1":
                _accumulate(module, "_cf_requested_counts", _count_routes(routing_map, padding_mask))
        return original_drop(routing_probs, routing_map, *args, **kwargs)

    def apply_bias_with_admission_capture(self, routing_map, padding_mask=None):
        _MODULES.add(self)
        if self.config.moe_pad_expert_input_to_capacity:
            raise RuntimeError("This experiment requires --moe-pad-expert-input-to-capacity to remain disabled")
        if self.config.moe_router_fusion:
            raise RuntimeError("Validate the adapter with router fusion disabled before enabling fusion")
        if (torch.is_grad_enabled() and self.config.moe_expert_capacity_factor is None
                and os.environ.get("MOE_FEEDBACK_CAPTURE_REQUESTED") == "1"):
            # In the drop-off negative control, the framework's post-drop map
            # is also the request map, so no second histogram is needed.
            _accumulate(self, "_cf_requested_counts", _count_routes(routing_map, padding_mask))
        return original_apply_expert_bias(self, routing_map, padding_mask)

    RouterClass.routing = routing_with_context
    RouterClass._apply_expert_bias = apply_bias_with_admission_capture
    router_module.apply_router_token_dropping = drop_with_request_capture
    RouterClass._moe_feedback_adapter_installed = True

    def update_router_bias(model, config, tp_dp_cp_group=None):
        modules = _collect_router_modules(model, get_attr_wrapped_model)
        if not modules:
            return
        requested_rows = [getattr(m, "_cf_requested_counts", None) for m in modules]
        if signal == "requested" and any(value is None for value in requested_rows):
            raise RuntimeError("Requested-feedback controller has a missing pre-drop count vector")
        requested = requested_rows
        admitted = torch.stack([m.local_tokens_per_expert.detach().clone() for m in modules])
        capacity_rows = [getattr(m, "_cf_capacity_counts", None) for m in modules]
        local_selected = torch.stack(
            [value if value is not None else torch.zeros_like(admitted[index])
             for index, value in enumerate(requested)]
        ) if signal == "requested" else admitted
        bias_before = torch.stack([m.expert_bias.detach().clone() for m in modules])
        group = tp_dp_cp_group
        if group is None:
            from megatron.core import parallel_state
            group = parallel_state.get_tensor_and_data_parallel_group(with_context_parallel=True)

        if scope == "global":
            selected = local_selected.clone()
            if torch.distributed.is_available() and torch.distributed.is_initialized():
                torch.distributed.all_reduce(selected, group=group)
            direction = torch.sign(selected.sum(dim=-1, keepdim=True) - selected * selected.shape[-1])
        else:
            # Compute rank-local error signs, then average actions so replicated
            # bias state remains synchronized without sharing the raw count vector.
            direction = torch.sign(
                local_selected.sum(dim=-1, keepdim=True)
                - local_selected * local_selected.shape[-1]
            ).to(dtype=bias_before.dtype)
            if torch.distributed.is_available() and torch.distributed.is_initialized():
                torch.distributed.all_reduce(direction, group=group)
                direction.div_(torch.distributed.get_world_size(group=group))

        updated = bias_before + direction.to(bias_before.dtype) * config.moe_router_bias_update_rate
        for index, module in enumerate(modules):
            module.expert_bias.copy_(updated[index])
            module._cf_update_step = getattr(module, "_cf_update_step", 0) + 1
            _append_record(
                module,
                module._cf_update_step,
                requested[index], admitted[index], bias_before[index], updated[index], scope, signal,
                capacity_rows[index],
            )
            module._cf_requested_counts = None
            module._cf_capacity_counts = None

    finalize_module._update_router_expert_bias = update_router_bias
    out = Path(os.environ["MOE_FEEDBACK_OUTPUT"])
    out.mkdir(parents=True, exist_ok=True)
    if int(os.environ.get("RANK", "0")) == 0:
        runtime = {
            "megatron_sha": actual_sha,
            "torch_version": torch.__version__,
            "cuda_version": torch.version.cuda,
            "cuda_available": torch.cuda.is_available(),
            "device": torch.cuda.get_device_name() if torch.cuda.is_available() else "cpu",
            "world_size": int(os.environ.get("WORLD_SIZE", "1")),
            "signal": signal,
            "scope": scope,
            "run_id": os.environ.get("MOE_FEEDBACK_RUN_ID"),
        }
        (out / "adapter_runtime.json").write_text(
            json.dumps(runtime, indent=2) + "\n", encoding="utf-8"
        )
    atexit.register(flush)
    _INSTALLED = True


def flush() -> None:
    """Flush per-layer telemetry on normal interpreter shutdown."""
    if os.environ.get("MOE_FEEDBACK_EXPERIMENT") != "1":
        return
    try:
        for module in list(_MODULES):
            _flush_rows(module)
    except Exception:
        # Shutdown may occur after partially initialized Megatron imports.
        return
