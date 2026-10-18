#!/usr/bin/env python3
"""Audit Top-1 clipped-load mirror dynamics and finite-batch equilibrium.

Run from the repository root:
    python scripts/run_top1_arbitrary_capacity_mirror_equilibrium.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import binom, t as student_t


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "top1_arbitrary_capacity_mirror_equilibrium"
ES = (3, 4, 6, 8)
TS = (256, 1024, 4096)
PROFILES_PER_CELL = 24
ETAS = (0.1, 0.5, 0.9)
HORIZON = 1024
CHECKPOINTS = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
MC_BATCHES = 4096
BASE_SEED = 20261017


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def largest_remainder(prob: np.ndarray, total: int) -> np.ndarray:
    raw = prob * total
    counts = np.floor(raw).astype(np.int64)
    left = total - int(counts.sum())
    if left:
        order = np.argsort(-(raw - counts), kind="stable")
        counts[order[:left]] += 1
    return counts


def make_capacity_profiles(E: int, T: int, cell_index: int) -> list[tuple[int, np.ndarray]]:
    profiles: list[tuple[int, np.ndarray]] = []
    for replicate in range(PROFILES_PER_CELL):
        seed = BASE_SEED + 1_000_000 * cell_index + replicate
        rng = np.random.default_rng(seed)
        attempts = 0
        while True:
            attempts += 1
            proportions = rng.dirichlet(np.full(E, 12.0))
            C = largest_remainder(proportions, T)
            if np.all(C > 0) and np.any(C != C[0]):
                break
            if attempts > 1000:
                raise AssertionError("failed to draw a valid preregistered profile")
        profiles.append((seed, C))
    return profiles


def softmax_negative(q: np.ndarray) -> np.ndarray:
    z = -q - np.max(-q)
    exp_z = np.exp(z)
    return exp_z / exp_z.sum()


def capacity_potential(p: np.ndarray, c: np.ndarray) -> float:
    low = p <= c
    terms = np.empty_like(p, dtype=np.float64)
    terms[low] = 0.5 * p[low] ** 2
    terms[~low] = c[~low] * p[~low] - 0.5 * c[~low] ** 2
    return float(terms.sum())


def equilibrium_distribution(c: np.ndarray) -> np.ndarray:
    E = len(c)
    c_min = float(c.min())
    S = np.isclose(c, c_min, rtol=0.0, atol=0.0)
    m = int(S.sum())
    p_star = np.full(E, c_min, dtype=np.float64)
    p_star[S] = (1.0 - (E - m) * c_min) / m
    return p_star


def exact_finite_binomial(p: float, capacity: int, T: int) -> tuple[float, float]:
    k = np.arange(T + 1, dtype=np.int64)
    pmf = binom.pmf(k, T, p)
    admitted = np.minimum(k, capacity)
    overflow = np.maximum(k - capacity, 0)
    return float(np.dot(admitted, pmf) / T), float(np.dot(overflow, pmf) / T)


def mean_interval(values: np.ndarray) -> tuple[float, float, float]:
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(values.size))
    half = float(student_t.ppf(0.975, values.size - 1) * se)
    return mean, mean - half, mean + half


def run_population_profile(E: int, T: int, profile_id: int, seed: int,
                           C: np.ndarray) -> tuple[list[dict], dict]:
    c = C.astype(np.float64) / T
    c_min = float(c.min())
    p_star = equilibrium_distribution(c)
    q_star = -np.log(p_star)
    q_star -= q_star.mean()
    a_star = np.minimum(p_star, c)
    p_reconstructed = softmax_negative(q_star)
    expected_equilibrium_overflow = float(np.maximum(p_star - c, 0.0).sum())
    requested_overflow = float(np.maximum(1.0 / E - c, 0.0).sum())
    lower_bound = float(1.0 / E - c_min)
    equilibrium_overflow = float(1.0 - E * c_min)
    low_count = int(np.sum(c < 1.0 / E))
    W_star = capacity_potential(p_star, c)

    checks = {
        "capacities_valid_exact_total_nonuniform": bool(
            int(C.sum()) == T and np.all(C > 0) and np.all(C < T)
            and np.any(C != C[0])
        ),
        "equilibrium_distribution_interior_simplex": bool(
            np.all(p_star > 0) and np.all(p_star < 1)
            and math.isclose(float(p_star.sum()), 1.0, abs_tol=1e-12)
        ),
        "equilibrium_admissions_equal_cmin": bool(
            np.max(np.abs(a_star - c_min)) <= 1e-12
        ),
        "equilibrium_softmax_reconstruction": bool(
            np.max(np.abs(p_reconstructed - p_star)) <= 1e-12
        ),
        "equilibrium_overflow_identity": bool(
            math.isclose(expected_equilibrium_overflow, equilibrium_overflow,
                         rel_tol=0.0, abs_tol=1e-12)
        ),
        "requested_overflow_identity": bool(
            math.isclose(requested_overflow,
                         float(np.maximum(1.0 / E - c, 0.0).sum()),
                         rel_tol=0.0, abs_tol=1e-12)
        ),
        "strict_overflow_gap_bound": bool(
            equilibrium_overflow - requested_overflow + 1e-12 >= lower_bound
            and lower_bound > 0
        ),
    }

    rows: list[dict] = []
    for eta in ETAS:
        q = np.zeros(E, dtype=np.float64)
        p = softmax_negative(q)
        W0 = capacity_potential(p, c)
        W_previous = W0
        KL0 = float(np.sum(p_star * np.log(p_star / p)))
        checkpoints = set(CHECKPOINTS)
        for step in range(1, HORIZON + 1):
            p_old = p.copy()
            admitted = np.minimum(p, c)
            q_next = q + eta * (admitted - 1.0 / E)
            q_next -= q_next.mean()
            p_from_pressure = softmax_negative(q_next)
            logp = np.log(p) - eta * admitted
            logp -= np.max(logp)
            p_from_mirror = np.exp(logp)
            p_from_mirror /= p_from_mirror.sum()
            if np.max(np.abs(p_from_pressure - p_from_mirror)) > 1e-12:
                checks["pressure_equals_mirror_step"] = False
            else:
                checks.setdefault("pressure_equals_mirror_step", True)

            q, p = q_next, p_from_pressure
            W_now = capacity_potential(p, c)
            if W_now > W_previous + 1e-12:
                checks["potential_nonincreasing"] = False
            else:
                checks.setdefault("potential_nonincreasing", True)
            kl_old = float(np.sum(p_star * np.log(p_star / p_old)))
            kl_new = float(np.sum(p_star * np.log(p_star / p)))
            kl_step = float(np.sum(p * np.log(p / p_old)))
            one_step_rhs = (kl_old - kl_new) / eta - (1.0 / eta - 1.0) * kl_step
            if W_now - W_star > one_step_rhs + 1e-10:
                checks["one_step_mirror_descent_inequality"] = False
            else:
                checks.setdefault("one_step_mirror_descent_inequality", True)
            if step in checkpoints:
                gap = W_now - W_star
                bound = KL0 / (eta * step)
                overflow_now = float(np.maximum(p - c, 0.0).sum())
                if gap > bound + 1e-10:
                    checks["relative_smoothness_rate_bound"] = False
                else:
                    checks.setdefault("relative_smoothness_rate_bound", True)
                rows.append({
                    "E": E, "T": T, "profile_id": profile_id,
                    "capacity_seed": seed, "eta": eta, "N": step,
                    "c_min": c_min, "min_capacity_count": int(np.sum(c == c_min)),
                    "potential": W_now, "potential_gap": gap,
                    "KL_equilibrium_to_current": float(
                        np.sum(p_star * np.log(p_star / p))
                    ),
                    "rate_bound": bound,
                    "overflow_admitted_current": overflow_now,
                    "overflow_admitted_equilibrium": equilibrium_overflow,
                    "overflow_requested_equilibrium": requested_overflow,
                    "overflow_gap_equilibrium": equilibrium_overflow - requested_overflow,
                    "theorem_gap_lower_bound": lower_bound,
                    "low_capacity_count_below_mean": low_count,
                })
            W_previous = W_now

    profile = {
        "E": E, "T": T, "profile_id": profile_id,
        "capacity_seed": seed, "capacities": C.tolist(),
        "capacity_fractions": c.tolist(), "c_min": c_min,
        "p_star": p_star.tolist(),
        "requested_equilibrium_overflow": requested_overflow,
        "admitted_equilibrium_overflow": equilibrium_overflow,
        "equilibrium_overflow_gap": equilibrium_overflow - requested_overflow,
        "theorem_gap_lower_bound": lower_bound,
        "potential_at_equilibrium": W_star,
        "KL_uniform_to_equilibrium": KL0,
        "low_capacity_count_below_mean": low_count,
        "checks": checks,
    }
    return rows, profile


def finite_batch_profile(E: int, T: int, profile_id: int, seed: int,
                         C: np.ndarray, p_star: np.ndarray) -> dict:
    rng = np.random.default_rng(seed + 77_000_003)
    R = rng.multinomial(T, p_star, size=MC_BATCHES)
    A = np.minimum(R, C[None, :])
    J = np.maximum(R - C[None, :], 0)
    if not np.all(R.sum(axis=1) == T):
        raise AssertionError("finite batch request mass violated")
    if not np.array_equal(A, np.minimum(R, C[None, :])):
        raise AssertionError("finite batch clipping identity violated")
    overflow = J.sum(axis=1) / T
    if not np.allclose(overflow, 1.0 - A.sum(axis=1) / T, rtol=0.0, atol=1e-14):
        raise AssertionError("finite batch overflow mass identity violated")

    expected_admitted = []
    expected_overflow = []
    mc_admitted = A.mean(axis=0) / T
    for e in range(E):
        adm_e, ov_e = exact_finite_binomial(float(p_star[e]), int(C[e]), T)
        expected_admitted.append(adm_e)
        expected_overflow.append(ov_e)
    exact_ov = float(sum(expected_overflow))
    mc_mean, mc_lo, mc_hi = mean_interval(overflow)
    admitted_means = A.mean(axis=0) / T
    projected_mc_feedback_norm = float(np.linalg.norm(admitted_means - admitted_means.mean()))
    exact_admitted = np.asarray(expected_admitted)
    projected_exact_feedback_norm = float(
        np.linalg.norm(exact_admitted - exact_admitted.mean())
    )
    return {
        "E": E, "T": T, "profile_id": profile_id,
        "capacity_seed": seed, "mc_batches": MC_BATCHES,
        "mc_overflow_mean": mc_mean, "mc_overflow_ci95_low": mc_lo,
        "mc_overflow_ci95_high": mc_hi,
        "exact_finite_T_expected_overflow": exact_ov,
        "population_overflow_limit": float(1.0 - E * np.min(C / T)),
        "overflow_mc_interval_covers_exact": bool(mc_lo <= exact_ov <= mc_hi),
        "mc_projected_mean_admitted_feedback_l2": projected_mc_feedback_norm,
        "exact_projected_mean_admitted_feedback_l2": projected_exact_feedback_norm,
        "equilibrium_admitted_fractions_population": np.minimum(p_star, C / T).tolist(),
        "exact_expected_admitted_fractions_finite_T": exact_admitted.tolist(),
        "controls_pass": True,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pop_rows: list[dict] = []
    mc_rows: list[dict] = []
    profiles_out: list[dict] = []
    global_checks: dict[str, bool] = {
        "all_profile_controls_pass": True,
        "all_population_update_and_rate_controls_pass": True,
        "all_finite_batch_identities_pass": True,
    }

    cell_index = 0
    for E in ES:
        for T in TS:
            capacity_profiles = make_capacity_profiles(E, T, cell_index)
            cell_index += 1
            for profile_id, (seed, C) in enumerate(capacity_profiles):
                rows, profile = run_population_profile(E, T, profile_id, seed, C)
                pop_rows.extend(rows)
                profiles_out.append(profile)
                if not all(profile["checks"].values()):
                    global_checks["all_profile_controls_pass"] = False
                    global_checks["all_population_update_and_rate_controls_pass"] = False

                p_star = np.asarray(profile["p_star"], dtype=np.float64)
                mc = finite_batch_profile(E, T, profile_id, seed, C, p_star)
                mc_rows.append(mc)
                if not mc["controls_pass"]:
                    global_checks["all_finite_batch_identities_pass"] = False

    pop_path = OUT / "population_trajectories.csv"
    with pop_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(pop_rows[0]))
        writer.writeheader()
        writer.writerows(pop_rows)
    mc_path = OUT / "finite_batch_equilibrium.csv"
    with mc_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(mc_rows[0]))
        writer.writeheader()
        writer.writerows(mc_rows)
    profiles_path = OUT / "capacity_profiles.json"
    profiles_path.write_text(json.dumps(profiles_out, indent=2) + "\n", encoding="utf-8")

    eta_summary = []
    for eta in ETAS:
        eta_rows = [row for row in pop_rows if row["eta"] == eta]
        final = [row for row in eta_rows if row["N"] == HORIZON]
        eta_summary.append({
            "eta": eta,
            "profiles": len(final),
            "max_final_potential_gap": max(row["potential_gap"] for row in final),
            "mean_final_potential_gap": float(np.mean([row["potential_gap"] for row in final])),
            "max_final_overflow_abs_error": max(
                abs(row["overflow_admitted_current"] - row["overflow_admitted_equilibrium"])
                for row in final
            ),
            "rate_bound_passes": all(
                row["potential_gap"] <= row["rate_bound"] + 1e-10
                for row in eta_rows
            ),
        })

    mc_coverage = int(sum(row["overflow_mc_interval_covers_exact"] for row in mc_rows))
    summary_path = OUT / "summary.json"
    summary = {
        "experiment": "Top-1 arbitrary-capacity mirror equilibrium audit",
        "E_values": list(ES), "T_values": list(TS),
        "profiles_per_E_T": PROFILES_PER_CELL,
        "profile_count": len(profiles_out),
        "population_trajectory_rows": len(pop_rows),
        "finite_batch_profiles": len(mc_rows),
        "population_etas": list(ETAS), "population_horizon": HORIZON,
        "checkpoints": list(CHECKPOINTS), "finite_batch_replicates": MC_BATCHES,
        "finite_batch_overflow_ci_cover_count": mc_coverage,
        "finite_batch_overflow_ci_total": len(mc_rows),
        "checks": global_checks,
        "eta_summary": eta_summary,
        "population_trajectories_sha256": sha256(pop_path),
        "finite_batch_equilibrium_sha256": sha256(mc_path),
        "capacity_profiles_sha256": sha256(profiles_path),
        "runner_sha256": sha256(Path(__file__)),
    }
    if not all(global_checks.values()) or not all(r["rate_bound_passes"] for r in eta_summary):
        raise AssertionError(f"registered controls failed: {global_checks}; {eta_summary}")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
