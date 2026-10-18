#!/usr/bin/env python3
"""Exact-expectation audit of local rank loss under capacity saturation."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/saturation_rank_threshold_experiment_2026-10-18.md"
OUT = ROOT / "results/saturation_rank_threshold_2026-10-18"
E = 4
K_GRID = (1, 2, 3)
T_GRID = (160, 320, 640)
LOGITS = np.array([0.7, 0.25, -0.2, -0.75], dtype=np.float64)
FD_STEP = 1e-5
P0 = np.eye(E) - np.ones((E, E), dtype=np.float64) / E
ONES = np.ones(E, dtype=np.float64)
BASIS = np.linalg.svd(ONES.reshape(1, E), full_matrices=True)[2][1:].T


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def inclusion(logits: np.ndarray, k: int) -> np.ndarray:
    """Exact Plackett-Luce Top-K inclusion probabilities by E! enumeration."""
    weights = np.exp(np.asarray(logits, dtype=np.float64) - np.max(logits))
    out = np.zeros(E, dtype=np.float64)
    for order in itertools.permutations(range(E)):
        remaining = float(weights.sum())
        probability = 1.0
        for expert in order:
            probability *= float(weights[expert]) / remaining
            remaining -= float(weights[expert])
        out[list(order[:k])] += probability
    return out


def binomial_pmf(n: int, p: float) -> list[float]:
    logs = [
        math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(n - x + 1)
        + x * math.log(p) + (n - x) * math.log1p(-p)
        for x in range(n + 1)
    ]
    peak = max(logs)
    unnormalized = [math.exp(value - peak) for value in logs]
    total = math.fsum(unnormalized)
    return [value / total for value in unnormalized]


def attenuation(t: int, capacity: int, p: float) -> float:
    return math.fsum(binomial_pmf(t - 1, p)[:capacity])


def exact_total_caps(target: np.ndarray, total: int, t: int) -> list[int]:
    raw = target * t
    caps = np.floor(raw).astype(int)
    remainder = total - int(caps.sum())
    order = sorted(range(E), key=lambda i: (-(raw[i] - caps[i]), i))
    for expert in order[:remainder]:
        caps[expert] += 1
    if sum(caps) != total or not all(1 <= c <= t for c in caps):
        raise AssertionError(f"invalid capacities {caps.tolist()} for total={total}, T={t}")
    return [int(c) for c in caps]


def centered_jacobian(fn, q: np.ndarray) -> np.ndarray:
    columns = []
    for j in range(E):
        direction = np.zeros(E)
        direction[j] = FD_STEP
        columns.append((fn(q + direction) - fn(q - direction)) / (2.0 * FD_STEP))
    return np.column_stack(columns)


def regime_capacity(p: np.ndarray, saturated_count: int, k: int, t: int) -> list[int]:
    if saturated_count == 0:
        return [t] * E
    if not 1 <= saturated_count < E:
        raise ValueError("registered saturation count must be between 1 and E-1")
    m = saturated_count
    d = min(
        0.06,
        float(np.min(p[:m])) / 4.0,
        float(np.min(1.0 - p[m:])) * (E - m) / (4.0 * m),
    )
    shift = np.full(E, m * d / (E - m), dtype=np.float64)
    shift[:m] = -d
    target = p + shift
    if not (np.all(target[:m] < p[:m]) and np.all(target[m:] > p[m:])):
        raise AssertionError("capacity fractions do not create the registered saturation set")
    return exact_total_caps(target, k * t, t)


def evaluate(k: int, t: int, saturated_count: int) -> dict[str, object]:
    q0 = np.zeros(E, dtype=np.float64)
    p = inclusion(LOGITS, k)
    caps = regime_capacity(p, saturated_count, k, t)
    cap_fraction = np.asarray(caps, dtype=np.float64) / t
    overload = p - cap_fraction

    if saturated_count == 0:
        if caps != [t] * E:
            raise AssertionError("no-clipping control changed")
    else:
        if not np.all(overload[:saturated_count] > 0.0):
            raise AssertionError(f"registered saturated experts are not overloaded: {overload}")
        if not np.all(overload[saturated_count:] < 0.0):
            raise AssertionError(f"registered unsaturated experts are not under capacity: {overload}")
        if sum(caps) != k * t:
            raise AssertionError("exact-total capacity control failed")

    alphas = np.asarray(
        [attenuation(t, caps[e], float(p[e])) for e in range(E)], dtype=np.float64
    )

    def p_of_q(q: np.ndarray) -> np.ndarray:
        return inclusion(LOGITS - q, k)

    def requested_field(q: np.ndarray) -> np.ndarray:
        return P0 @ (p_of_q(q) / k - 1.0 / E)

    def admitted_field(q: np.ndarray) -> np.ndarray:
        probs = p_of_q(q)
        admitted_means = np.asarray([
            math.fsum(x * prob for x, prob in enumerate(binomial_pmf(t, float(probs[e])))
                      if x < caps[e])
            + caps[e] * math.fsum(binomial_pmf(t, float(probs[e]))[caps[e]:])
            for e in range(E)
        ])
        return P0 @ (admitted_means / (k * t) - 1.0 / E)

    jac_p = centered_jacobian(p_of_q, q0)
    direct_r = centered_jacobian(requested_field, q0)
    direct_a = centered_jacobian(admitted_field, q0)
    predicted_r = P0 @ jac_p / k
    predicted_a = P0 @ np.diag(alphas) @ jac_p / k

    reduced_r = BASIS.T @ direct_r @ BASIS
    reduced_a = BASIS.T @ direct_a @ BASIS
    relative_direct = reduced_a @ np.linalg.inv(reduced_r)
    relative_exact_chain = BASIS.T @ P0 @ np.diag(alphas) @ BASIS
    singular_values = np.sort(np.linalg.svd(relative_exact_chain, compute_uv=False))

    alpha_limit = np.ones(E, dtype=np.float64)
    alpha_limit[:saturated_count] = 0.0
    relative_limit = BASIS.T @ P0 @ np.diag(alpha_limit) @ BASIS
    limit_singular_values = np.linalg.svd(relative_limit, compute_uv=False)
    limit_rank = int(np.count_nonzero(limit_singular_values > 1e-10))
    expected_limit_rank = E - 1 if saturated_count == 0 else E - saturated_count

    saturated_alpha_max = float(np.max(alphas[:saturated_count])) if saturated_count else 0.0
    small_singular_count = int(np.count_nonzero(singular_values <= saturated_alpha_max + 1e-10))
    required_small_count = max(saturated_count - 1, 0)

    if np.linalg.matrix_rank(relative_exact_chain, tol=1e-12) != E - 1:
        raise AssertionError("finite-batch relative response must have full quotient rank")
    if limit_rank != expected_limit_rank:
        raise AssertionError(f"limiting rank {limit_rank} != predicted {expected_limit_rank}")
    if small_singular_count < required_small_count:
        raise AssertionError("too few singular values meet the saturated-subspace bound")

    err_r = float(np.max(np.abs(direct_r - predicted_r)))
    err_a = float(np.max(np.abs(direct_a - predicted_a)))
    err_relative = float(np.max(np.abs(relative_direct - relative_exact_chain)))
    if max(err_r, err_a, err_relative) > 3e-6:
        raise AssertionError(f"analytic/finite-difference Jacobian mismatch: {err_r}, {err_a}, {err_relative}")

    return {
        "E": E, "K": k, "T": t, "saturated_count": saturated_count,
        "capacities": caps, "capacity_fractions": cap_fraction.tolist(),
        "request_probabilities": p.tolist(), "overload_margins": overload.tolist(),
        "attenuation": alphas.tolist(), "saturated_alpha_max": saturated_alpha_max,
        "finite_relative_rank": E - 1, "limiting_rank": limit_rank,
        "predicted_limiting_rank": expected_limit_rank,
        "required_small_singular_count": required_small_count,
        "observed_singular_values_le_saturated_alpha": small_singular_count,
        "relative_singular_values_ascending": singular_values.tolist(),
        "limiting_singular_values_descending": np.sort(limit_singular_values)[::-1].tolist(),
        "max_requested_jacobian_error": err_r,
        "max_admitted_jacobian_error": err_a,
        "max_relative_operator_error": err_relative,
    }


def main() -> None:
    rows = [evaluate(k, t, m)
            for m in range(E)
            for k in (K_GRID)
            for t in T_GRID]
    OUT.mkdir(parents=True, exist_ok=True)
    cells = OUT / "cells.csv"
    with cells.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, separators=(",", ":"))
                             if isinstance(v, (list, dict)) else v
                             for k, v in row.items()})
    summary = {
        "experiment": "exact_expected_topk_saturation_rank_threshold",
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha(PROTOCOL), "runner_sha256": sha(Path(__file__)),
        "cells_sha256": sha(cells), "cell_count": len(rows),
        "E": E, "K_values": list(K_GRID), "T_values": list(T_GRID),
        "saturated_counts": list(range(E)),
        "router": "iid standard-Gumbel Top-K; exact Plackett-Luce order enumeration",
        "computation": "exact binomial clipping expectations; central finite differences only as an independent Jacobian audit",
        "all_finite_ranks_full": all(r["finite_relative_rank"] == E - 1 for r in rows),
        "all_limiting_ranks_match": all(r["limiting_rank"] == r["predicted_limiting_rank"] for r in rows),
        "all_saturated_subspace_bounds_pass": all(
            r["observed_singular_values_le_saturated_alpha"] >= r["required_small_singular_count"]
            for r in rows
        ),
        "max_jacobian_error": max(max(r["max_requested_jacobian_error"],
                                       r["max_admitted_jacobian_error"],
                                       r["max_relative_operator_error"]) for r in rows),
        "rank_claim_boundary": "local expected-mean feedback only; not finite-law non-identifiability, policy-value separation, closed-loop performance, or hardware cost",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
