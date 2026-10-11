"""Hardened deterministic affinity scenarios (protocol v0.2.0).

These scenarios stress-test the controller where the v1 synthetic study was
too easy, following the failure-mode catalog in
docs/literature_review/moe_routing_load_balancing.md:

- SaturationWindupScenario: base demand, then a demand spike that saturates
  several experts for a fixed window, then release. Tests integrator windup:
  admitted-direction feedback is censored while saturated, so its pressure
  keeps integrating a blind signal; on release the wound-up state overshoots.
- AdversarialInitScenario: one expert is dominant for every token at step 0
  (rich-get-richer start). Tests escape from a collapsed initialization.
- AdversarialBatchesScenario: near-identical token affinities (collapsed
  representation variance) with bursty, rapidly shifting preference
  patterns. Tests tracking under degenerate per-token signals.
- SpecializationProbeScenario: planted expert-skill block structure with
  unbalanced skill sizes, exposing per-token skill labels so the runner can
  record the mutual information between expert assignment and skill label.
  Tests the balance-vs-specialization Pareto frontier (the SimBal caution:
  perfect balance by smearing tokens is a failure, not a win).

All generators are pure functions of their seed and parameters; the batch
is identical across controller runs with the same scenario seed (paired
comparisons). Content hashes are recorded in reference().
"""

from __future__ import annotations

from typing import List, Optional

import torch
from torch import Tensor

from moe_control.scenarios.synthetic import (
    affinity_content_hash,
    build_affinity_tensor,
)


class SaturationWindupScenario:
    """Three-phase windup probe: base -> spike (saturating) -> release.

    ``spike_group_sizes`` should concentrate demand so that several experts
    exceed capacity during [spike_step, spike_end). The release phase reuses
    the base affinity tensor, so any post-release overshoot or oscillation
    is attributable to controller state built up during the spike.
    """

    def __init__(
        self,
        name: str,
        seed: int,
        tokens: int,
        experts: int,
        group_sizes: List[int],
        spike_step: int,
        spike_end: int,
        spike_group_sizes: List[int],
        noise_scale: float = 0.1,
        affinity_dtype: str = "float32",
    ) -> None:
        self.name = name
        self.spike_step = spike_step
        self.spike_end = spike_end
        dtype = getattr(torch, affinity_dtype)
        self._base = build_affinity_tensor(
            seed, tokens, experts, list(group_sizes), noise_scale, dtype
        )
        # Different seed stream for the spike batch: a genuine demand change,
        # still fully deterministic.
        self._spike = build_affinity_tensor(
            seed + 2_000_011, tokens, experts, list(spike_group_sizes),
            noise_scale, dtype,
        )
        self._params = {
            "kind": "saturation_windup",
            "seed": seed,
            "tokens": tokens,
            "experts": experts,
            "group_sizes": list(group_sizes),
            "spike_step": spike_step,
            "spike_end": spike_end,
            "spike_group_sizes": list(spike_group_sizes),
            "noise_scale": noise_scale,
            "affinity_dtype": affinity_dtype,
        }

    def batch(self, step: int) -> Tensor:
        if self.spike_step <= step < self.spike_end:
            return self._spike
        return self._base

    def reference(self) -> dict:
        return {
            **self._params,
            "content_hash_sha256_base": affinity_content_hash(self._base),
            "content_hash_sha256_spike": affinity_content_hash(self._spike),
        }


class AdversarialInitScenario:
    """One expert dominates every token's affinity at step 0.

    ``dominant_offset`` is added to column ``dominant_expert`` for all
    tokens on top of the usual group-pair structure. With K=2, every token
    initially requests the dominant expert plus its group-pair favorite, so
    R_dominant = T (rich-get-richer start). The controller must build enough
    pressure on the dominant expert to divert tokens elsewhere.
    """

    def __init__(
        self,
        name: str,
        seed: int,
        tokens: int,
        experts: int,
        group_sizes: List[int],
        dominant_expert: int = 0,
        dominant_offset: float = 3.0,
        noise_scale: float = 0.1,
        affinity_dtype: str = "float32",
    ) -> None:
        self.name = name
        dtype = getattr(torch, affinity_dtype)
        base = build_affinity_tensor(
            seed, tokens, experts, list(group_sizes), noise_scale, dtype
        )
        base = base.clone()
        base[:, dominant_expert] += dominant_offset
        self._affinity = base
        self._params = {
            "kind": "adversarial_init",
            "seed": seed,
            "tokens": tokens,
            "experts": experts,
            "group_sizes": list(group_sizes),
            "dominant_expert": dominant_expert,
            "dominant_offset": dominant_offset,
            "noise_scale": noise_scale,
            "affinity_dtype": affinity_dtype,
        }

    def batch(self, step: int) -> Tensor:
        return self._affinity

    def reference(self) -> dict:
        return {
            **self._params,
            "content_hash_sha256": affinity_content_hash(self._affinity),
        }


class AdversarialBatchesScenario:
    """Collapsed token variance with bursty preference shifts.

    Every token in a burst shares the same preference vector (a permuted
    arithmetic progression with gap ``preference_gap``) plus tiny per-token
    noise (``burst_noise_scale``). All tokens therefore request the same two
    experts: extreme skew from a degenerate signal. Every ``burst_period``
    steps the favored pair changes (deterministic permutation per burst),
    forcing the controller to re-track rapidly shifting demand.
    ``group_sizes`` is accepted for config uniformity but ignored.
    """

    def __init__(
        self,
        name: str,
        seed: int,
        tokens: int,
        experts: int,
        burst_period: int = 100,
        n_bursts: int = 12,
        preference_gap: float = 0.15,
        burst_noise_scale: float = 0.01,
        affinity_dtype: str = "float32",
    ) -> None:
        self.name = name
        self.burst_period = burst_period
        self.n_bursts = n_bursts
        dtype = getattr(torch, affinity_dtype)
        # Base preference: symmetric arithmetic progression; the top two
        # entries are separated from the rest by preference_gap.
        center = (experts - 1) / 2.0
        base_pref = torch.tensor(
            [(center - e) * preference_gap for e in range(experts)],
            dtype=torch.float64,
        )
        bursts = []
        for b in range(n_bursts):
            perm_gen = torch.Generator().manual_seed(seed + 7919 * (b + 1))
            perm = torch.randperm(experts, generator=perm_gen)
            pref = base_pref[perm]
            noise_gen = torch.Generator().manual_seed(seed + 104729 * (b + 1))
            noise = torch.randn(tokens, experts, generator=noise_gen,
                                dtype=torch.float64) * burst_noise_scale
            burst = (pref.unsqueeze(0).expand(tokens, experts) + noise).to(dtype)
            bursts.append(burst)
        self._bursts = bursts
        self._params = {
            "kind": "adversarial_batches",
            "seed": seed,
            "tokens": tokens,
            "experts": experts,
            "burst_period": burst_period,
            "n_bursts": n_bursts,
            "preference_gap": preference_gap,
            "burst_noise_scale": burst_noise_scale,
            "affinity_dtype": affinity_dtype,
        }

    def batch(self, step: int) -> Tensor:
        return self._bursts[(step // self.burst_period) % self.n_bursts]

    def reference(self) -> dict:
        return {
            **self._params,
            "content_hash_sha256_bursts": [
                affinity_content_hash(b) for b in self._bursts
            ],
        }


class SpecializationProbeScenario:
    """Planted skill-block affinity with per-token skill labels.

    Token group g (a "skill") strongly prefers expert pair (2g, 2g+1), as in
    the synthetic generator, but group sizes are deliberately unbalanced so
    that rebalancing demand necessarily moves tokens off their skill
    experts. ``skill_labels(step)`` returns the (T,) int64 skill index per
    token, letting the runner record the mutual information between expert
    assignment and skill label: the balance-vs-specialization Pareto probe.
    """

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
        dtype = getattr(torch, affinity_dtype)
        self._affinity = build_affinity_tensor(
            seed, tokens, experts, list(group_sizes), noise_scale, dtype
        )
        labels = torch.empty(tokens, dtype=torch.int64)
        start = 0
        for g, size in enumerate(group_sizes):
            labels[start : start + size] = g
            start += size
        self._labels = labels
        self._params = {
            "kind": "specialization_probe",
            "seed": seed,
            "tokens": tokens,
            "experts": experts,
            "group_sizes": list(group_sizes),
            "noise_scale": noise_scale,
            "affinity_dtype": affinity_dtype,
        }

    def batch(self, step: int) -> Tensor:
        return self._affinity

    def skill_labels(self, step: int) -> Tensor:
        return self._labels

    def reference(self) -> dict:
        return {
            **self._params,
            "content_hash_sha256": affinity_content_hash(self._affinity),
        }


def build_hardened_scenario(
    name: str,
    kind: str,
    seed: int,
    tokens: int,
    experts: int,
    group_sizes: List[int],
    noise_scale: float,
    affinity_dtype: str,
    spike_step: Optional[int] = None,
    spike_end: Optional[int] = None,
    spike_group_sizes: Optional[List[int]] = None,
    dominant_expert: int = 0,
    dominant_offset: float = 3.0,
    burst_period: int = 100,
    n_bursts: int = 12,
    preference_gap: float = 0.15,
    burst_noise_scale: float = 0.01,
):
    """Construct a hardened scenario from validated config values."""
    if kind == "saturation_windup":
        assert spike_step is not None and spike_end is not None
        assert spike_group_sizes is not None
        return SaturationWindupScenario(
            name, seed, tokens, experts, group_sizes, spike_step, spike_end,
            spike_group_sizes, noise_scale, affinity_dtype,
        )
    if kind == "adversarial_init":
        return AdversarialInitScenario(
            name, seed, tokens, experts, group_sizes, dominant_expert,
            dominant_offset, noise_scale, affinity_dtype,
        )
    if kind == "adversarial_batches":
        return AdversarialBatchesScenario(
            name, seed, tokens, experts, burst_period, n_bursts,
            preference_gap, burst_noise_scale, affinity_dtype,
        )
    if kind == "specialization_probe":
        return SpecializationProbeScenario(
            name, seed, tokens, experts, group_sizes, noise_scale,
            affinity_dtype,
        )
    raise ValueError(f"Unknown hardened scenario kind {kind!r}.")
