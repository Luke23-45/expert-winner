#!/usr/bin/env python3
"""Exact-expectation audit of admitted-field curl for Gumbel Top-K."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Callable, Sequence


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "topk_general_k_admission_curl"
E = 4
T_GRID = (32, 128, 512)
K_GRID = (1, 2, 3)
LOGITS_SKEWED = (1.2, 0.35, -0.4, -1.0)
LOGITS_UNIFORM = (0.0, 0.0, 0.0, 0.0)
FD_STEP = 1e-5
TOL = 2e-7


def topk_inclusion_probabilities(logits: Sequence[float], k: int) -> list[float]:
    """Exact Plackett-Luce inclusion probabilities by enumerating E! orders."""
    e = len(logits)
    weights = [math.exp(x - max(logits)) for x in logits]
    p = [0.0] * e
    for order in itertools.permutations(range(e)):
        remaining = sum(weights)
        probability = 1.0
        for expert in order:
            probability *= weights[expert] / remaining
            remaining -= weights[expert]
        for expert in order[:k]:
            p[expert] += probability
    return p


def clipped_binomial_mean(t: int, capacity: int, p: float) -> float:
    return math.fsum(
        min(x, capacity) * math.comb(t, x) * p**x * (1.0 - p) ** (t - x)
        for x in range(t + 1)
    )


def clipping_sensitivity(t: int, capacity: int, p: float) -> float:
    return math.fsum(
        math.comb(t - 1, x) * p**x * (1.0 - p) ** (t - 1 - x)
        for x in range(capacity)
    )


def project_zero_sum(vector: Sequence[float]) -> list[float]:
    mean = math.fsum(vector) / len(vector)
    return [x - mean for x in vector]


def jacobian(function: Callable[[Sequence[float]], Sequence[float]], q: Sequence[float]) -> list[list[float]]:
    e = len(q)
    columns: list[list[float]] = []
    for j in range(e):
        q_plus = list(q)
        q_minus = list(q)
        q_plus[j] += FD_STEP
        q_minus[j] -= FD_STEP
        f_plus = function(q_plus)
        f_minus = function(q_minus)
        columns.append([(f_plus[i] - f_minus[i]) / (2.0 * FD_STEP) for i in range(e)])
    return [[columns[j][i] for j in range(e)] for i in range(e)]


def matrix_product(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> list[list[float]]:
    return [
        [math.fsum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def project_matrix(a: Sequence[Sequence[float]]) -> list[list[float]]:
    e = len(a)
    p0 = [[(1.0 if i == j else 0.0) - 1.0 / e for j in range(e)] for i in range(e)]
    return matrix_product(matrix_product(p0, a), p0)


def tangent_curl(a: Sequence[Sequence[float]]) -> float:
    # u=e_1-e_4, v=e_2-e_4; return u^T A v - v^T A u.
    u = (1.0, 0.0, 0.0, -1.0)
    v = (0.0, 1.0, 0.0, -1.0)
    au = [math.fsum(a[i][j] * u[j] for j in range(E)) for i in range(E)]
    av = [math.fsum(a[i][j] * v[j] for j in range(E)) for i in range(E)]
    return math.fsum(u[i] * av[i] - v[i] * au[i] for i in range(E))


def max_matrix_error(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> float:
    return max(abs(a[i][j] - b[i][j]) for i in range(len(a)) for j in range(len(a)))


def evaluate_cell(k: int, t: int, logits: Sequence[float], capacity: int) -> dict[str, object]:
    q0 = [0.0] * E

    def probabilities(q: Sequence[float]) -> list[float]:
        return topk_inclusion_probabilities([logits[i] - q[i] for i in range(E)], k)

    def requested_field(q: Sequence[float]) -> list[float]:
        return project_zero_sum([x / k - 1.0 / E for x in probabilities(q)])

    def admitted_field(q: Sequence[float]) -> list[float]:
        p = probabilities(q)
        return project_zero_sum([clipped_binomial_mean(t, capacity, x) / (k * t) - 1.0 / E for x in p])

    p = probabilities(q0)
    dp = jacobian(probabilities, q0)
    alpha = [clipping_sensitivity(t, capacity, x) for x in p]
    scaled_dp = [[alpha[i] * dp[i][j] / k for j in range(E)] for i in range(E)]
    predicted_admitted_jacobian = project_matrix(scaled_dp)
    direct_admitted_jacobian = jacobian(admitted_field, q0)
    direct_requested_jacobian = jacobian(requested_field, q0)
    predicted_requested_jacobian = project_matrix([[dp[i][j] / k for j in range(E)] for i in range(E)])
    return {
        "E": E,
        "K": k,
        "T": t,
        "capacity_per_expert": capacity,
        "capacity_fraction_of_KT_per_expert": capacity / (k * t),
        "logits": list(logits),
        "inclusion_probabilities": p,
        "alpha": alpha,
        "requested_curl": tangent_curl(direct_requested_jacobian),
        "admitted_curl_direct": tangent_curl(direct_admitted_jacobian),
        "admitted_curl_chain_rule": tangent_curl(predicted_admitted_jacobian),
        "max_admitted_jacobian_error": max_matrix_error(direct_admitted_jacobian, predicted_admitted_jacobian),
        "max_requested_jacobian_error": max_matrix_error(direct_requested_jacobian, predicted_requested_jacobian),
        "request_jacobian_symmetry_error": max_matrix_error(dp, [list(row) for row in zip(*dp)]),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for k in K_GRID:
        for t in T_GRID:
            capacity = k * t // E
            assert k * t % E == 0 and 1 <= capacity < t
            rows.append(evaluate_cell(k, t, LOGITS_SKEWED, capacity))
            rows.append(evaluate_cell(k, t, LOGITS_UNIFORM, capacity))
            rows.append(evaluate_cell(k, t, LOGITS_SKEWED, t))

    # Mathematical controls and derivative checks.
    for row in rows:
        assert abs(math.fsum(row["inclusion_probabilities"]) - row["K"]) < 1e-12
        assert row["max_admitted_jacobian_error"] < TOL
        assert row["max_requested_jacobian_error"] < TOL
        assert row["request_jacobian_symmetry_error"] < TOL
        assert abs(row["requested_curl"]) < TOL
        if row["logits"] == list(LOGITS_UNIFORM) or row["capacity_per_expert"] == row["T"]:
            assert abs(row["admitted_curl_direct"]) < TOL
        else:
            assert abs(row["admitted_curl_direct"]) > 1e-5
            assert abs(row["admitted_curl_direct"] - row["admitted_curl_chain_rule"]) < TOL

    csv_path = OUT / "grid.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "experiment": "gumbel_topk_expected_admitted_field_curl",
        "protocol": {"E": E, "K": list(K_GRID), "T": list(T_GRID), "fd_step": FD_STEP, "tolerance": TOL},
        "cells": len(rows),
        "skewed_clipped_cells": sum(r["logits"] == list(LOGITS_SKEWED) and r["capacity_per_expert"] < r["T"] for r in rows),
        "positive_curl_skewed_clipped_cells": sum(r["logits"] == list(LOGITS_SKEWED) and r["capacity_per_expert"] < r["T"] and r["admitted_curl_direct"] < -1e-5 for r in rows),
        "zero_curl_controls": sum((r["logits"] == list(LOGITS_UNIFORM) or r["capacity_per_expert"] == r["T"]) and abs(r["admitted_curl_direct"]) < TOL for r in rows),
        "max_admitted_jacobian_error": max(r["max_admitted_jacobian_error"] for r in rows),
        "max_requested_jacobian_error": max(r["max_requested_jacobian_error"] for r in rows),
        "max_request_jacobian_symmetry_error": max(r["request_jacobian_symmetry_error"] for r in rows),
        "rows": rows,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    payload["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "rows"}, indent=2, sort_keys=True))
    print(f"csv={csv_path}")
    print(f"summary={summary_path}")


if __name__ == "__main__":
    main()
