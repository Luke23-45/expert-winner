"""Capacity accounting.

Implements the canonical count admission rule from the formal document:
``A_e = min(R_e, C_e)`` with rejected load ``J = R - A``. This is a pure
count rule; it does not model which individual tokens are admitted (a
token-order adapter can be added later as a separate component).
"""

from __future__ import annotations

import torch
from torch import Tensor

from moe_control.contracts import CapacityResult


class CanonicalCapacityPolicy:
    """Per-expert canonical admission: A_e = min(R_e, C_e), J_e = R_e - A_e."""

    name = "canonical"

    def admit(self, requested: Tensor, capacity: Tensor) -> CapacityResult:
        if requested.shape != capacity.shape:
            raise ValueError(
                "requested and capacity shapes differ: "
                f"{tuple(requested.shape)} vs {tuple(capacity.shape)}."
            )
        requested = requested.to(torch.int64)
        capacity = capacity.to(torch.int64)
        admitted = torch.minimum(requested, capacity)
        rejected = requested - admitted
        return CapacityResult(admitted=admitted, rejected=rejected)
