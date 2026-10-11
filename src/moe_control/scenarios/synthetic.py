"""Deterministic synthetic affinity scenarios.

Construction: token group g (of ``group_sizes[g]`` tokens) strongly
prefers expert pair (2g, 2g+1), with small deterministic noise on every
coordinate. This requires an even expert count. Group sizes are the only
declared skew parameter; realized request counts are validated at runtime
by the runner rather than assumed from the skew parameter.

The generator depends only on (seed, T, E, group_sizes, noise_scale), so
the affinity batch is identical across controller runs with the same
scenario seed, giving paired comparisons.
"""

from __future__ import annotations

import hashlib
from typing import List, Optional

import torch
from torch import Tensor

# Favorite-pair score offsets. With q = 0 the Top-K selection for a group-g
# token is exactly the pair (2g, 2g+1); both offsets dominate noise_scale.
_FAVORITE_OFFSETS = (2.0, 1.9)


def build_affinity_tensor(
    seed: int,
    tokens: int,
    experts: int,
    group_sizes: List[int],
    noise_scale: float = 0.1,
    dtype: torch.dtype = torch.float32,
) -> Tensor:
    """Build a deterministic (T, E) affinity tensor."""
    if experts % 2 != 0:
        raise ValueError("Synthetic group generator requires an even expert count.")
    if len(group_sizes) != experts // 2:
        raise ValueError("len(group_sizes) must equal E // 2.")
    if sum(group_sizes) != tokens:
        raise ValueError("sum(group_sizes) must equal T.")
    gen = torch.Generator().manual_seed(seed)
    affinities = torch.randn(tokens, experts, generator=gen, dtype=torch.float64)
    affinities = affinities * noise_scale
    start = 0
    rows = torch.arange(tokens)
    for g, size in enumerate(group_sizes):
        idx = rows[start : start + size]
        affinities[idx, 2 * g] += _FAVORITE_OFFSETS[0]
        affinities[idx, 2 * g + 1] += _FAVORITE_OFFSETS[1]
        start += size
    return affinities.to(dtype)


def affinity_content_hash(affinity: Tensor) -> str:
    """SHA-256 over the raw affinity bytes (canonical float64 view)."""
    blob = affinity.detach().to(torch.float64).contiguous().numpy().tobytes()
    return hashlib.sha256(blob).hexdigest()


class SyntheticScenario:
    """Stationary synthetic affinity scenario."""

    def __init__(
        self,
        name: str,
        seed: int,
        tokens: int,
        experts: int,
        group_sizes: List[int],
        noise_scale: float = 0.1,
        affinity_dtype: str = "float32",
    ) -> None:
        self.name = name
        self.seed = seed
        self._affinity = build_affinity_tensor(
            seed, tokens, experts, list(group_sizes), noise_scale,
            getattr(torch, affinity_dtype),
        )
        self._params = {
            "kind": "synthetic",
            "seed": seed,
            "tokens": tokens,
            "experts": experts,
            "group_sizes": list(group_sizes),
            "noise_scale": noise_scale,
            "affinity_dtype": affinity_dtype,
            "favorite_offsets": list(_FAVORITE_OFFSETS),
        }

    def batch(self, step: int) -> Tensor:
        return self._affinity

    def reference(self) -> dict:
        return {
            **self._params,
            "content_hash_sha256": affinity_content_hash(self._affinity),
        }


class DemandShiftScenario:
    """Synthetic scenario with a one-time demand shift at ``shift_step``.

    Affinity preferences switch from ``group_sizes`` to
    ``shift_group_sizes`` at the configured step. The pressure state is
    untouched by the scenario; the runner carries q across the shift.
    """

    def __init__(
        self,
        name: str,
        seed: int,
        tokens: int,
        experts: int,
        group_sizes: List[int],
        shift_step: int,
        shift_group_sizes: List[int],
        noise_scale: float = 0.1,
        affinity_dtype: str = "float32",
    ) -> None:
        self.name = name
        self.shift_step = shift_step
        self._before = build_affinity_tensor(
            seed, tokens, experts, list(group_sizes), noise_scale,
            getattr(torch, affinity_dtype),
        )
        # A different seed stream for the post-shift batch so the shift is a
        # genuine preference change, still fully deterministic.
        self._after = build_affinity_tensor(
            seed + 1_000_003, tokens, experts, list(shift_group_sizes),
            noise_scale, getattr(torch, affinity_dtype),
        )
        self._params = {
            "kind": "demand_shift",
            "seed": seed,
            "tokens": tokens,
            "experts": experts,
            "group_sizes": list(group_sizes),
            "shift_step": shift_step,
            "shift_group_sizes": list(shift_group_sizes),
            "noise_scale": noise_scale,
            "affinity_dtype": affinity_dtype,
            "favorite_offsets": list(_FAVORITE_OFFSETS),
        }

    def batch(self, step: int) -> Tensor:
        return self._after if step >= self.shift_step else self._before

    def reference(self) -> dict:
        return {
            **self._params,
            "content_hash_sha256_before": affinity_content_hash(self._before),
            "content_hash_sha256_after": affinity_content_hash(self._after),
        }


def build_scenario(
    name: str,
    kind: str,
    seed: int,
    tokens: int,
    experts: int,
    group_sizes: List[int],
    noise_scale: float,
    affinity_dtype: str,
    shift_step: Optional[int] = None,
    shift_group_sizes: Optional[List[int]] = None,
):
    """Construct a scenario from validated config values."""
    if kind == "synthetic":
        return SyntheticScenario(
            name, seed, tokens, experts, group_sizes, noise_scale, affinity_dtype
        )
    if kind == "demand_shift":
        assert shift_step is not None and shift_group_sizes is not None
        return DemandShiftScenario(
            name, seed, tokens, experts, group_sizes, shift_step,
            shift_group_sizes, noise_scale, affinity_dtype,
        )
    raise ValueError(f"Unknown scenario kind {kind!r}.")
