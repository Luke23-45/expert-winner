"""Seeding and deterministic-execution controls."""

from __future__ import annotations

import random

import numpy as np
import torch


def seed_all(seed: int) -> None:
    """Seed Python, NumPy, and PyTorch generators from one seed."""
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)


def enable_deterministic_mode() -> None:
    """Request deterministic algorithms; fail loudly if unavailable.

    PyTorch notes deterministic mode alone does not guarantee whole-run
    reproducibility; it is combined here with explicit seeding, a fixed
    tie rule, and version capture in the run manifest.
    """
    torch.use_deterministic_algorithms(True, warn_only=False)
