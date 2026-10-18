#!/usr/bin/env python3
"""Controlled exact-expectation audit of the saturated tangent corollary."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/saturated_tangent_sensitivity_experiment_protocol_2026-10-18.md"
OUT = ROOT / "results/saturated_tangent_sensitivity_2026-10-18"
E = 4
T_GRID = (160, 320, 640)
K_GRID = (1, 2, 3)
LOGITS = (0.7, 0.25, -0.2, -0.75)
FD_STEP = 1e-5
TOL = 2e-6
P0 = np.eye(E) - np.ones((E, E)) / E
ONES = np.ones(E)
BASIS = np.linalg.svd(ONES.reshape(1, E), full_matrices=True)[2][1:].T


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def inclusion(logits: tuple[float, ...] | list[float], k: int) -> np.ndarray:
    """Exact Plackett-Luce Top-K inclusion probabilities by E! enumeration."""
    weights = np.exp(np.asarray(logits, dtype=np.float64) - max(logits))
    out = np.zeros(E, dtype=np.float64)
    for order in itertools.permutations(range(E)):
        remaining = float(weights.sum())
        prob = 1.0
        for e in order:
            prob *= float(weights[e]) / remaining
            remaining -= float(weights[e])
        out[list(order[:k])] += prob
    return out


def binomial_pmf(n: int, p: float) -> list[float]:
    if p <= 0.0:
        return [1.0] + [0.0] * n
    if p >= 1.0:
        return [0.0] * n + [1.0]
    logs = [
        math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(n - x + 1)
        + x * math.log(p) + (n - x) * math.log1p(-p)
        for x in range(n + 1)
    ]
    peak = max(logs)
    unnormalized = [math.exp(x - peak) for x in logs]
    total = math.fsum(unnormalized)
    return [x / total for x in unnormalized]


def alpha(t: int, c: int, p: float) -> float:
    return math.fsum(binomial_pmf(t - 1, p)[:c])


def clipped_mean(t: int, c: int, p: float) -> float:
    return math.fsum(min(x, c) * prob for x, prob in enumerate(binomial_pmf(t, p)))


def allocate_exact_total(fractions: np.ndarray, total: int, t: int) -> list[int]:
    raw = fractions * t
    caps = np.floor(raw).astype(int)
    remainder = total - int(caps.sum())
    order = sorted(range(E), key=lambda i: (-(raw[i] - caps[i]), i))
    for i in order[:remainder]:
        caps[i] += 1
    assert int(caps.sum()) == total
    assert all(1 <= int(c) <= t for c in caps)
    return [int(c) for c in caps]


def centered_jacobian(fn, q: np.ndarray) -> np.ndarray:
    cols = []
    for j in range(E):
        d = np.zeros(E)
        d[j] = FD_STEP
        cols.append((fn(q + d) - fn(q - d)) / (2 * FD_STEP))
    return np.column_stack(cols)


def pressure_for_transfer(jac: np.ndarray, z: np.ndarray) -> np.ndarray:
    reduced = BASIS.T @ jac @ BASIS
    coeff = np.linalg.solve(reduced, BASIS.T @ z)
    v = BASIS @ coeff
    assert np.linalg.norm(jac @ v - z) < 2e-7
    assert abs(float(v.sum())) < 1e-10
    return v


def evaluate(k: int, t: int, regime: str) -> dict[str, object]:
    q0 = np.zeros(E)
    p = inclusion(np.asarray(LOGITS) - q0, k)
    assert abs(float(p.sum()) - k) < 1e-12

    if regime == "two_saturated":
        d = min(0.06, float(p[0]) / 4, float(p[1]) / 4,
                (1.0 - float(p[2])) / 4, (1.0 - float(p[3])) / 4)
        shift = np.array([-d, -d, d, d])
        transfer = np.array([1.0, -1.0, 0.0, 0.0])
        saturated = (0, 1)
    elif regime == "one_saturated":
        d = min(0.01, float(p[0]) / 12,
                (1.0 - float(p[1])) / 4, (1.0 - float(p[2])) / 4,
                (1.0 - float(p[3])) / 4)
        shift = np.array([-3 * d, d, d, d])
        transfer = np.array([1.0, -1.0, 0.0, 0.0])
        saturated = (0,)
    elif regime == "no_clipping":
        caps = [t] * E
        transfer = np.array([1.0, -1.0, 0.0, 0.0])
        saturated = ()
    else:
        raise ValueError(regime)

    if regime != "no_clipping":
        target_caps = p + shift
        assert np.all(target_caps > 0.0) and np.all(target_caps < 1.0)
        caps = allocate_exact_total(target_caps, k * t, t)
    cap_fraction = np.asarray(caps, dtype=np.float64) / t
    overload = p - cap_fraction
    if regime == "two_saturated":
        assert all(overload[e] > 0.0 for e in saturated)
        assert all(overload[e] < 0.0 for e in (2, 3))
    elif regime == "one_saturated":
        assert overload[0] > 0.0
        assert all(overload[e] < 0.0 for e in (1, 2, 3))

    def p_of_q(q: np.ndarray) -> np.ndarray:
        return inclusion(np.asarray(LOGITS) - q, k)

    def fr(q: np.ndarray) -> np.ndarray:
        return P0 @ (p_of_q(q) / k - 1.0 / E)

    def fa(q: np.ndarray) -> np.ndarray:
        pp = p_of_q(q)
        mm = np.array([clipped_mean(t, caps[e], float(pp[e])) for e in range(E)])
        return P0 @ (mm / (k * t) - 1.0 / E)

    jac = centered_jacobian(p_of_q, q0)
    al = np.array([alpha(t, caps[e], float(p[e])) for e in range(E)])
    predicted_r = P0 @ jac / k
    predicted_a = P0 @ np.diag(al) @ jac / k
    direct_r = centered_jacobian(fr, q0)
    direct_a = centered_jacobian(fa, q0)
    v = pressure_for_transfer(jac, transfer)
    fd_scale = 1e-5 / max(1.0, float(np.linalg.norm(v)))
    directional_r_fd = (fr(q0 + fd_scale * v) - fr(q0 - fd_scale * v)) / (2 * fd_scale)
    directional_a_fd = (fa(q0 + fd_scale * v) - fa(q0 - fd_scale * v)) / (2 * fd_scale)
    # Exact chain-rule response for the registered probability transfer z.
    directional_r = P0 @ transfer / k
    directional_a = P0 @ (al * transfer) / k
    rnorm = float(np.linalg.norm(directional_r))
    anorm = float(np.linalg.norm(directional_a))
    ratio = anorm / rnorm
    assert np.linalg.norm(directional_r - transfer / k) < 2e-7
    assert np.linalg.norm(directional_r_fd - directional_r) < TOL
    assert np.linalg.norm(directional_a_fd - directional_a) < TOL
    assert np.max(np.abs(direct_r - predicted_r)) < TOL
    assert np.max(np.abs(direct_a - predicted_a)) < TOL
    assert abs(float(transfer.sum())) < 1e-12
    if regime == "two_saturated":
        assert ratio <= max(al[0], al[1]) + 1e-10
    if regime == "no_clipping":
        assert abs(ratio - 1.0) < 1e-10

    return {
        "E": E, "K": k, "T": t, "regime": regime,
        "logits": list(LOGITS), "request_probabilities": p.tolist(),
        "capacities": caps, "capacity_fractions": cap_fraction.tolist(),
        "overload_margins": overload.tolist(), "attenuation": al.tolist(),
        "transfer_pair": [0, 1], "pressure_direction_norm": float(np.linalg.norm(v)),
        "requested_directional_response_norm": rnorm,
        "admitted_directional_response_norm": anorm,
        "admitted_to_requested_response_ratio": ratio,
        "max_requested_jacobian_error": float(np.max(np.abs(direct_r - predicted_r))),
        "max_admitted_jacobian_error": float(np.max(np.abs(direct_a - predicted_a))),
        "requested_directional_fd_error": float(np.linalg.norm(directional_r_fd - directional_r)),
        "admitted_directional_fd_error": float(np.linalg.norm(directional_a_fd - directional_a)),
        "request_mass_error": abs(float(p.sum()) - k),
        "capacity_mass_error": abs(sum(caps) - k * t) if regime != "no_clipping" else None,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [evaluate(k, t, regime)
            for regime in ("two_saturated", "one_saturated", "no_clipping")
            for k in (K_GRID if regime != "no_clipping" else K_GRID)
            for t in T_GRID]

    two = [r for r in rows if r["regime"] == "two_saturated"]
    one = [r for r in rows if r["regime"] == "one_saturated"]
    none = [r for r in rows if r["regime"] == "no_clipping"]
    assert len(rows) == 27
    for k in K_GRID:
        tr = [r for r in two if r["K"] == k]
        assert all(tr[i + 1]["admitted_to_requested_response_ratio"]
                   < tr[i]["admitted_to_requested_response_ratio"] for i in range(len(tr) - 1))
        assert tr[-1]["admitted_to_requested_response_ratio"] < 1e-3, (k, tr[-1]["T"], tr[-1]["admitted_to_requested_response_ratio"])
    assert min(r["admitted_to_requested_response_ratio"] for r in one) > 0.25
    assert max(abs(r["admitted_to_requested_response_ratio"] - 1.0) for r in none) < 1e-10

    path = OUT / "cells.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "experiment": "exact_expected_topk_saturated_tangent_sensitivity",
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha(PROTOCOL),
        "runner_sha256": sha(Path(__file__)),
        "cells_sha256": sha(path), "cell_count": len(rows),
        "E": E, "K_values": list(K_GRID), "T_values": list(T_GRID),
        "router": "iid standard-Gumbel Top-K; exact Plackett-Luce order enumeration",
        "statistical_design": "exact expectation; no Monte Carlo sampling or confidence intervals",
        "max_jacobian_fd_error": max(max(r["max_requested_jacobian_error"], r["max_admitted_jacobian_error"]) for r in rows),
        "max_directional_fd_error": max(max(r["requested_directional_fd_error"], r["admitted_directional_fd_error"]) for r in rows),
        "two_saturated_ratio_by_K": {
            str(k): [r["admitted_to_requested_response_ratio"] for r in two if r["K"] == k]
            for k in K_GRID
        },
        "single_saturated_ratio_by_K_T": [
            {"K": r["K"], "T": r["T"], "ratio": r["admitted_to_requested_response_ratio"]}
            for r in one
        ],
        "no_clipping_ratio_by_K_T": [r["admitted_to_requested_response_ratio"] for r in none],
        "checks_passed": True,
        "claim_boundary": "local derivative of expected mean feedback only; no finite-law non-identifiability, policy-value gap, stability, or hardware-cost inference",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
