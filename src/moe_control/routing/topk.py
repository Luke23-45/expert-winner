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


def pressured_scores(affinity: Tensor, pressure: Tensor, gamma: float) -> Tensor:
    """Compute pressured scores s_{t,e} = a_{t,e} - gamma * q_e.

    ``affinity`` is (T, E); ``pressure`` is (E,) and broadcasts over tokens.
    """
    return affinity - gamma * pressure


def deterministic_topk_mask(scores: Tensor, k: int) -> Tensor:
    """Return a (T, E) boolean mask with exactly K True entries per row.

    Tie rule: stable descending sort; among equal scores the lower expert
    index is selected first (stable sort preserves the original ascending
    index order within ties).
    """
    if scores.dim() != 2:
        raise ValueError(f"scores must be (T, E); got shape {tuple(scores.shape)}.")
    e = scores.shape[1]
    if not (1 <= k <= e):
        raise ValueError(f"Require 1 <= K <= E, got K={k}, E={e}.")
    # Stable descending sort: equal scores keep ascending index order.
    order = torch.argsort(scores, dim=1, descending=True, stable=True)
    chosen = order[:, :k]
    mask = torch.zeros_like(scores, dtype=torch.bool)
    mask.scatter_(1, chosen, True)
    return mask


def requested_counts(mask: Tensor) -> Tensor:
    """Batch requested load R_e = sum_t 1{e selected for token t}."""
    return mask.sum(dim=0).to(torch.int64)
