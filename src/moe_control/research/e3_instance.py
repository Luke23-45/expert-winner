"""Shared deterministic E=3, two-world routing instance for Phase 1 analysis."""
from __future__ import annotations

import numpy as np

C = 50.0
E_S = 20.0
C_SINK = 30.0
M_MARGIN = 3.0
M_LOW = 1.0
GAMMA = 1.0
CAP = np.array([C, C, C_SINK], dtype=float)
T_BATCH = 2 * C + E_S

if not (E_S < C_SINK < C - E_S / 2 and 0 < M_LOW < M_MARGIN):
    raise ValueError("E=3 construction capacity or margin assumptions violated")


def winning_expert(scores: np.ndarray | tuple[float, ...]) -> int:
    """Argmax with lower-index tie priority; returns a zero-based index."""
    scores = np.asarray(scores, dtype=float)
    best = 0
    for index in range(1, 3):
        if scores[index] > scores[best]:
            best = index
    return best


def score_cells(x: float, y: float) -> tuple[int, int, int, int]:
    """Return winners (d_1L, d_1H, d_2L, d_2H) at score coordinates (x,y)."""
    m, high = M_LOW, M_MARGIN
    return (
        winning_expert((m - x, -high - y, 0.0)),
        winning_expert((high - x, -high - y, 0.0)),
        winning_expert((-high - x, m - y, 0.0)),
        winning_expert((-high - x, high - y, 0.0)),
    )


def request_vectors(x: float, y: float) -> tuple[np.ndarray, np.ndarray]:
    """Return requested expert counts in worlds 1 and 2."""
    d_1L, d_1H, d_2L, d_2H = score_cells(x, y)
    r1 = np.zeros(3)
    r1[d_1H] += C
    r1[d_1L] += E_S
    r1[d_2L] += C
    r2 = np.zeros(3)
    r2[d_1L] += C
    r2[d_2H] += C
    r2[d_2L] += E_S
    return r1, r2


def admitted_and_cost(x: float, y: float) -> tuple[np.ndarray, float, np.ndarray, float]:
    """Return (A1, overflow1, A2, overflow2) for the two worlds."""
    r1, r2 = request_vectors(x, y)
    a1 = np.minimum(r1, CAP)
    a2 = np.minimum(r2, CAP)
    return a1, float(np.sum(r1 - a1)), a2, float(np.sum(r2 - a2))
