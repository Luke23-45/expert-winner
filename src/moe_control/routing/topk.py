"""Deterministic Top-K routing.

Forms pressured scores s = a - gamma * q and selects exactly K distinct
experts per token with an explicit tie rule: stable descending sort with
the lower expert index winning ties. This rule is documented in the run
contract and must not depend on ``torch.topk`` tie ordering, which
PyTorch does not guarantee.
"""

from __future__ import annotations

import torch
from torch import Tensor


def pressured_scores(
    affinity: Tensor, pressure: Tensor, gamma: float, sign: float = -1.0
) -> Tensor:
    """Compute modulated scores s_{t,e} = a_{t,e} + sign * gamma * q_e.

    ``affinity`` is (T, E); ``pressure`` is (E,) and broadcasts over tokens.
    The default ``sign=-1.0`` recovers the pressure form s = a - gamma * q;
    ``sign=+1.0`` adds the state (DeepSeek-style selection bias).
    """
    if sign not in (-1.0, 1.0):
        raise ValueError(f"sign must be -1.0 or 1.0, got {sign}.")
    return affinity + sign * gamma * pressure


def deterministic_topk_order(scores: Tensor) -> Tensor:
    """Stable descending expert order per token (T, E) int64 indices.

    Among equal scores the lower expert index comes first (stable sort
    preserves the original ascending index order within ties). This is the
    documented tie rule; it must not depend on ``torch.topk`` ordering.
    """
    if scores.dim() != 2:
        raise ValueError(f"scores must be (T, E); got shape {tuple(scores.shape)}.")
    return torch.argsort(scores, dim=1, descending=True, stable=True)


def deterministic_topk_mask(scores: Tensor, k: int) -> Tensor:
    """Return a (T, E) boolean mask with exactly K True entries per row.

    Tie rule: stable descending sort; among equal scores the lower expert
    index is selected first (stable sort preserves the original ascending
    index order within ties).
    """
    e = scores.shape[1]
    if not (1 <= k <= e):
        raise ValueError(f"Require 1 <= K <= E, got K={k}, E={e}.")
    chosen = deterministic_topk_order(scores)[:, :k]
    mask = torch.zeros_like(scores, dtype=torch.bool)
    mask.scatter_(1, chosen, True)
    return mask


def requested_counts(mask: Tensor) -> Tensor:
    """Batch requested load R_e = sum_t 1{e selected for token t}."""
    return mask.sum(dim=0).to(torch.int64)
