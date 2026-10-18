#!/usr/bin/env python3
"""Controlled Top-K audit of clipping attenuation and global-saturation freeze.

Run from the repository root:
    python scripts/run_c2_topk_saturation_sensitivity.py

Expected routing probabilities are computed exactly for Gumbel Top-K by
enumerating Plackett-Luce prefixes. Finite-batch count laws use binomial
marginals. The paired fresh-batch component is seeded Monte Carlo and is
reported separately from the exact Jacobian audit.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import binom


E = 4
KS = (1, 2)
HORIZONS = (60, 240, 960)
PROFILES = ("no_clipping", "global_shortage", "boundary", "one_overloaded", "two_overloaded")
MC_BATCHES = 4_000
MC_CHUNK = 128
FD_STEP = 1e-4
BASE_SEED = 20_261_017


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pl_inclusion_probabilities(logits: np.ndarray, k: int) -> np.ndarray:
    """Exact Top-K marginals for iid Gumbel noise (Plackett-Luce ranking)."""
    weights = np.exp(logits - np.max(logits))
    out = np.zeros(E, dtype=np.float64)
    for prefix in itertools.permutations(range(E), k):
        remaining = list(range(E))
        probability = 1.0
        for expert in prefix:
            denominator = float(weights[remaining].sum())
            probability *= weights[expert] / denominator
            remaining.remove(expert)
        for expert in prefix:
            out[expert] += probability
    return out


def p_at(q: np.ndarray, k: int) -> np.ndarray:
    return pl_inclusion_probabilities(-q, k)


def zero_sum_projection() -> np.ndarray:
    return np.eye(E, dtype=np.float64) - np.ones((E, E), dtype=np.float64) / E


P0 = zero_sum_projection()


def capacity_vector(profile: str, k: int, t: int) -> np.ndarray:
    mean = k * t // E
    if k * t % E:
        raise AssertionError("registered grid must have integer mean load")
    under = 4 * mean // 5
    if 5 * under != 4 * mean:
        raise AssertionError("registered grid must make the 0.8 capacity integral")
    if profile == "no_clipping":
        return np.full(E, t, dtype=np.int64)
    if profile == "global_shortage":
        return np.full(E, under, dtype=np.int64)
    if profile == "boundary":
        return np.full(E, mean, dtype=np.int64)
    if profile == "one_overloaded":
        residual = k * t - under
        if residual % (E - 1):
            raise AssertionError("one-overloaded residual must divide evenly")
        return np.array([under] + [residual // (E - 1)] * (E - 1), dtype=np.int64)
    if profile == "two_overloaded":
        residual = k * t - 2 * under
        if residual % 2:
            raise AssertionError("two-overloaded residual must divide evenly")
        return np.array([under, under, residual // 2, residual // 2], dtype=np.int64)
    raise ValueError(profile)


def binomial_attenuation(t: int, c: int, p: float) -> float:
    return float(binom.cdf(c - 1, t - 1, p))


def expected_clipped_count(t: int, c: int, p: float) -> float:
    ks = np.arange(c, dtype=np.int64)
    return float(np.dot(ks, binom.pmf(ks, t, p)) + c * binom.sf(c - 1, t, p))


def fields(q: np.ndarray, k: int, t: int, capacities: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = p_at(q, k)
    mu = np.full(E, 1.0 / E, dtype=np.float64)
    requested = P0 @ (p / k - mu)
    admitted_mean = np.array(
        [expected_clipped_count(t, int(c), float(pe)) / (k * t)
         for c, pe in zip(capacities, p)], dtype=np.float64
    )
    admitted = P0 @ (admitted_mean - mu)
    return requested, admitted


def finite_difference_jacobian(fn, q0: np.ndarray, h: float) -> np.ndarray:
    result = np.zeros((E, E), dtype=np.float64)
    for j in range(E):
        step = np.zeros(E, dtype=np.float64)
        step[j] = h
        result[:, j] = (fn(q0 + step) - fn(q0 - step)) / (2.0 * h)
    return result


def wilson(successes: int, trials: int, z: float = 1.959963984540054) -> tuple[float, float]:
    phat = successes / trials
    denom = 1.0 + z * z / trials
    center = (phat + z * z / (2.0 * trials)) / denom
    radius = z * math.sqrt(phat * (1.0 - phat) / trials + z * z / (4.0 * trials * trials)) / denom
    return max(0.0, center - radius), min(1.0, center + radius)


def simulate_uniform_gumbel_counts(k: int, t: int, rng: np.random.Generator) -> np.ndarray:
    """Return [replicate, expert] request counts from paired fresh batches."""
    out = np.zeros((MC_BATCHES, E), dtype=np.int64)
    start = 0
    while start < MC_BATCHES:
        n = min(MC_CHUNK, MC_BATCHES - start)
        u = rng.random((n, t, E), dtype=np.float64)
        u = np.clip(u, np.finfo(np.float64).tiny, 1.0 - np.finfo(np.float64).eps)
        g = -np.log(-np.log(u))
        chosen = np.argpartition(g, E - k, axis=2)[:, :, E - k:]
        for e in range(E):
            out[start:start + n, e] = np.sum(chosen == e, axis=(1, 2))
        start += n
    return out


def exact_grid() -> tuple[list[dict], list[dict], dict]:
    q0 = np.zeros(E, dtype=np.float64)
    exact_rows: list[dict] = []
    mc_rows: list[dict] = []
    checks = {
        "pl_probabilities_sum_to_k": True,
        "capacity_profiles_are_valid": True,
        "capacity_profiles_have_registered_saturation_pattern": True,
        "analytic_jacobian_matches_exact_field_finite_difference": True,
        "no_clipping_jacobians_match": True,
        "heterogeneous_factorization_holds": True,
        "dropless_pathwise_R_equals_A": True,
        "admitted_sign_feedback_zero_when_all_counts_saturated": True,
    }

    for k in KS:
        for t in HORIZONS:
            p = p_at(q0, k)
            if not np.allclose(p, k / E, rtol=0.0, atol=1e-14):
                checks["pl_probabilities_sum_to_k"] = False
            if not math.isclose(float(p.sum()), float(k), rel_tol=0.0, abs_tol=1e-14):
                checks["pl_probabilities_sum_to_k"] = False

            dp = finite_difference_jacobian(lambda q: p_at(q, k), q0, FD_STEP)
            j_requested_formula = (P0 @ dp) / k
            fd_requested = finite_difference_jacobian(
                lambda q: fields(q, k, t, capacity_vector("no_clipping", k, t))[0],
                q0, FD_STEP,
            )
            for profile in PROFILES:
                cvec = capacity_vector(profile, k, t)
                if np.any(cvec < 1) or np.any(cvec > t):
                    checks["capacity_profiles_are_valid"] = False
                if profile in ("boundary", "one_overloaded", "two_overloaded") and int(cvec.sum()) != k * t:
                    checks["capacity_profiles_are_valid"] = False
                margins = p - cvec / t
                if profile == "global_shortage" and not np.all(margins > 0.0):
                    checks["capacity_profiles_have_registered_saturation_pattern"] = False
                if profile == "boundary" and not np.allclose(margins, 0.0, rtol=0.0, atol=1e-14):
                    checks["capacity_profiles_have_registered_saturation_pattern"] = False
                if profile == "one_overloaded" and not (
                    margins[0] > 0.0 and np.all(margins[1:] < 0.0)
                ):
                    checks["capacity_profiles_have_registered_saturation_pattern"] = False
                if profile == "two_overloaded" and not (
                    np.all(margins[:2] > 0.0) and np.all(margins[2:] < 0.0)
                ):
                    checks["capacity_profiles_have_registered_saturation_pattern"] = False

                alpha = np.array(
                    [binomial_attenuation(t, int(c), float(pe)) for c, pe in zip(cvec, p)],
                    dtype=np.float64,
                )
                j_admitted_formula = (P0 @ np.diag(alpha) @ dp) / k
                fd_requested_cell = finite_difference_jacobian(
                    lambda q: fields(q, k, t, cvec)[0], q0, FD_STEP
                )
                fd_admitted = finite_difference_jacobian(
                    lambda q: fields(q, k, t, cvec)[1], q0, FD_STEP
                )
                err_r = float(np.max(np.abs(fd_requested_cell - j_requested_formula)))
                err_a = float(np.max(np.abs(fd_admitted - j_admitted_formula)))
                err_factorization = float(np.max(np.abs(fd_admitted - j_admitted_formula)))
                if max(err_r, err_a, err_factorization) > 2e-7:
                    checks["analytic_jacobian_matches_exact_field_finite_difference"] = False
                if profile == "no_clipping":
                    if not np.allclose(alpha, 1.0, rtol=0.0, atol=1e-14):
                        checks["no_clipping_jacobians_match"] = False
                    if not np.allclose(fd_admitted, fd_requested, rtol=0.0, atol=2e-7):
                        checks["no_clipping_jacobians_match"] = False
                if err_factorization > 2e-7:
                    checks["heterogeneous_factorization_holds"] = False

                exact_rows.append({
                    "E": E, "K": k, "T": t, "profile": profile,
                    "p": json.dumps(p.tolist(), separators=(",", ":")),
                    "C": json.dumps(cvec.tolist(), separators=(",", ":")),
                    "capacity_sum": int(cvec.sum()),
                    "alpha": json.dumps(alpha.tolist(), separators=(",", ":")),
                    "min_alpha": float(alpha.min()),
                    "max_alpha": float(alpha.max()),
                    "requested_jacobian_frobenius": float(np.linalg.norm(fd_requested_cell, ord="fro")),
                    "admitted_jacobian_frobenius": float(np.linalg.norm(fd_admitted, ord="fro")),
                    "jacobian_norm_ratio_A_over_R": float(
                        np.linalg.norm(fd_admitted, ord="fro") /
                        max(np.linalg.norm(fd_requested_cell, ord="fro"), np.finfo(float).tiny)
                    ),
                    "max_requested_fd_error": err_r,
                    "max_admitted_fd_error": err_a,
                })

            # Reuse a single set of fresh-batch requests across all capacity profiles.
            rng = np.random.default_rng(BASE_SEED + 1000 * k + t)
            request_counts = simulate_uniform_gumbel_counts(k, t, rng)
            dropless = capacity_vector("no_clipping", k, t)
            if not np.array_equal(np.minimum(request_counts, dropless), request_counts):
                checks["dropless_pathwise_R_equals_A"] = False
            for profile in PROFILES:
                cvec = capacity_vector(profile, k, t)
                admitted = np.minimum(request_counts, cvec[None, :])
                if profile == "global_shortage":
                    all_saturated = np.all(request_counts >= cvec[None, :], axis=1)
                    saturated_admitted = admitted[all_saturated]
                    centered = saturated_admitted.mean(axis=1, keepdims=True) - saturated_admitted
                    admitted_sign = np.sign(centered)
                    if saturated_admitted.size and not np.all(saturated_admitted == cvec[None, :]):
                        checks["admitted_sign_feedback_zero_when_all_counts_saturated"] = False
                    if admitted_sign.size and not np.all(admitted_sign == 0):
                        checks["admitted_sign_feedback_zero_when_all_counts_saturated"] = False
                    successes = int(all_saturated.sum())
                    lo, hi = wilson(successes, MC_BATCHES)
                    mc_rows.append({
                        "E": E, "K": k, "T": t, "profile": profile,
                        "batches": MC_BATCHES,
                        "all_experts_saturated": successes,
                        "saturation_rate": successes / MC_BATCHES,
                        "wilson95_low": lo, "wilson95_high": hi,
                        "admitted_sign_zero_count": int(np.all(admitted_sign == 0, axis=1).sum()) if admitted_sign.size else 0,
                    })
                if profile == "no_clipping" and not np.array_equal(admitted, request_counts):
                    checks["dropless_pathwise_R_equals_A"] = False

    # Verify the registered strict-overload asymptotics on the exact grid.
    for k in KS:
        by_profile = {
            profile: [row for row in exact_rows if row["K"] == k and row["profile"] == profile]
            for profile in PROFILES
        }
        for profile in ("global_shortage", "one_overloaded", "two_overloaded"):
            cells = sorted(by_profile[profile], key=lambda row: row["T"])
            vectors = [np.asarray(json.loads(row["alpha"]), dtype=np.float64) for row in cells]
            under_count = E if profile == "global_shortage" else (1 if profile == "one_overloaded" else 2)
            if any(np.any(np.diff([v[e] for v in vectors]) >= 0.0) for e in range(under_count)):
                checks["capacity_profiles_have_registered_saturation_pattern"] = False
            if profile != "global_shortage" and any(
                np.any(np.diff([v[e] for v in vectors]) <= 0.0)
                for e in range(under_count, E)
            ):
                checks["capacity_profiles_have_registered_saturation_pattern"] = False
        boundary = sorted(by_profile["boundary"], key=lambda row: row["T"])
        boundary_alpha = [np.asarray(json.loads(row["alpha"]), dtype=np.float64) for row in boundary]
        if k == 1:
            if any(np.any(np.diff([abs(v[e] - 0.5) for v in boundary_alpha]) >= 0.0) for e in range(E)):
                checks["capacity_profiles_have_registered_saturation_pattern"] = False
        elif any(not np.allclose(v, 0.5, rtol=0.0, atol=2e-14) for v in boundary_alpha):
            checks["capacity_profiles_have_registered_saturation_pattern"] = False

    summary = {
        "experiment": "controlled Top-K saturation sensitivity and freeze audit",
        "E": E,
        "K_values": list(KS),
        "T_values": list(HORIZONS),
        "profiles": list(PROFILES),
        "MC_batches_per_K_T": MC_BATCHES,
        "MC_seed_formula": f"{BASE_SEED} + 1000*K + T",
        "finite_difference_step": FD_STEP,
        "exact_cells": len(exact_rows),
        "mc_global_shortage_cells": len(mc_rows),
        "max_requested_fd_error": max(r["max_requested_fd_error"] for r in exact_rows),
        "max_admitted_fd_error": max(r["max_admitted_fd_error"] for r in exact_rows),
        "min_global_saturation_rate": min(r["saturation_rate"] for r in mc_rows),
        "max_global_saturation_rate": max(r["saturation_rate"] for r in mc_rows),
        "checks": checks,
    }
    return exact_rows, mc_rows, summary


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise AssertionError(f"refusing to write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    out_dir = Path("results/c2_topk_saturation_sensitivity")
    out_dir.mkdir(parents=True, exist_ok=True)
    exact_rows, mc_rows, summary = exact_grid()
    write_csv(out_dir / "exact_jacobians.csv", exact_rows)
    write_csv(out_dir / "global_freeze_monte_carlo.csv", mc_rows)
    if not all(summary["checks"].values()):
        raise AssertionError(f"one or more controls failed: {summary['checks']}")
    summary["runner_sha256"] = sha256(Path(__file__))
    summary["exact_csv_sha256"] = sha256(out_dir / "exact_jacobians.csv")
    summary["mc_csv_sha256"] = sha256(out_dir / "global_freeze_monte_carlo.csv")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Artifacts written to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
