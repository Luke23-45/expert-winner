#!/usr/bin/env python3
"""Exact-binomial audit of the capacity-matched admitted-field equilibrium.

This is a deterministic numerical audit of the theorem addendum in
``capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md``. It uses the
canonical Top-1 iid-Gumbel inclusion-probability coordinates and independent
per-expert admission A_e=min(R_e,C_e); it does not simulate training.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEOREM = ROOT / "docs/paper/capacity_clipped_topk_mirror_descent_theorem_2026-10-17.md"
PROTOCOL = ROOT / "docs/paper/capacity_clipped_topk_mirror_descent_protocol_2026-10-17.md"
OUT = ROOT / "results/capacity_matched_equilibrium"
T_VALUES = (24, 60, 120, 600)
CAPACITY_RATIOS = {
    "uniform": (1 / 3, 1 / 3, 1 / 3),
    "heterogeneous_a": (1 / 6, 5 / 12, 5 / 12),
    "heterogeneous_b": (1 / 4, 1 / 3, 5 / 12),
}
ROOT_TOL = 2.0e-11


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def binomial_admitted_mean(T: int, C: int, p: float) -> float:
    """Return E[min(Binomial(T,p),C)] with a mode-centered PMF recurrence."""
    if C <= 0 or T <= 0:
        return 0.0
    if C >= T or p <= 0.0:
        return T * max(0.0, p)
    if p >= 1.0:
        return float(C)

    mode = min(T, int((T + 1) * p))
    log_mode = (
        math.lgamma(T + 1)
        - math.lgamma(mode + 1)
        - math.lgamma(T - mode + 1)
        + mode * math.log(p)
        + (T - mode) * math.log1p(-p)
    )
    pmf_mode = math.exp(log_mode)
    terms = [min(mode, C) * pmf_mode]

    prob = pmf_mode
    for k in range(mode, 0, -1):
        prob *= (k / (T - k + 1)) * ((1.0 - p) / p)
        terms.append(min(k - 1, C) * prob)

    prob = pmf_mode
    for k in range(mode + 1, T + 1):
        prob *= ((T - k + 1) / k) * (p / (1.0 - p))
        terms.append(min(k, C) * prob)
    return math.fsum(terms)


def bisect_root(fn, lo: float, hi: float, *, iterations: int = 72) -> float:
    flo, fhi = fn(lo), fn(hi)
    if flo == 0.0:
        return lo
    if fhi == 0.0:
        return hi
    if flo * fhi > 0:
        raise ValueError(f"root not bracketed: f(lo)={flo}, f(hi)={fhi}")
    for _ in range(iterations):
        mid = (lo + hi) / 2.0
        fm = fn(mid)
        if fm == 0.0:
            return mid
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return (lo + hi) / 2.0


def equilibrium(T: int, capacities: tuple[int, ...]) -> tuple[list[float], float]:
    """Solve interior KKT equations m_e(p_e)/T-c_e=lambda, sum p=1."""
    E = len(capacities)
    if sum(capacities) != T or any(C <= 0 or C >= T for C in capacities):
        raise ValueError("audit requires positive, sub-batch, exact-total capacities")

    def p_at_lambda(C: int, lam: float) -> float:
        target = C + T * lam
        if target <= 0.0:
            return 0.0
        if target >= C:
            return 1.0
        return bisect_root(
            lambda p: binomial_admitted_mean(T, C, p) - target,
            0.0,
            1.0,
            iterations=56,
        )

    def mass_residual(lam: float) -> float:
        return math.fsum(p_at_lambda(C, lam) for C in capacities) - 1.0

    lower = -min(capacities) / T
    lam = bisect_root(mass_residual, lower, 0.0, iterations=64)
    probs = [p_at_lambda(C, lam) for C in capacities]
    return probs, lam


def capacity_counts(T: int, ratios: tuple[float, ...]) -> tuple[int, ...]:
    values = tuple(round(T * ratio) for ratio in ratios)
    if not math.isclose(sum(ratios), 1.0, abs_tol=1e-14):
        raise AssertionError("capacity proportions must sum to one")
    if any(not math.isclose(T * r, c, abs_tol=1e-10) for r, c in zip(ratios, values)):
        raise AssertionError(f"T={T} does not make capacities integral for {ratios}")
    return values


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    max_mass_error = 0.0
    max_kkt_error = 0.0
    max_vacancy_spread = 0.0

    for T in T_VALUES:
        for name, ratios in CAPACITY_RATIOS.items():
            caps = capacity_counts(T, ratios)
            c = [C / T for C in caps]
            p_star, lam = equilibrium(T, caps)
            admitted = [
                binomial_admitted_mean(T, C, p) / T
                for C, p in zip(caps, p_star)
            ]
            kkt = [m - cap - lam for m, cap in zip(admitted, c)]
            vacancies = [C - T * m for C, m in zip(caps, admitted)]
            overflow_fraction = math.fsum(p - m for p, m in zip(p_star, admitted))
            predicted_overflow = -len(caps) * lam
            mass_error = abs(math.fsum(p_star) - 1.0)
            kkt_error = max(abs(x) for x in kkt)
            vacancy_spread = max(vacancies) - min(vacancies)
            max_mass_error = max(max_mass_error, mass_error)
            max_kkt_error = max(max_kkt_error, kkt_error)
            max_vacancy_spread = max(max_vacancy_spread, vacancy_spread)

            rows.append({
                "T": T,
                "capacity_profile": name,
                "capacities": json.dumps(caps),
                "capacity_proportions": json.dumps(c),
                "equilibrium_probabilities": json.dumps(p_star),
                "lambda": lam,
                "expected_admitted_fractions": json.dumps(admitted),
                "expected_unused_slots": json.dumps(vacancies),
                "l1_equilibrium_to_capacity": math.fsum(abs(p - cap) for p, cap in zip(p_star, c)),
                "l1_requested_target_error_at_equilibrium": math.fsum(abs(p - cap) for p, cap in zip(p_star, c)),
                "overflow_fraction_at_equilibrium": overflow_fraction,
                "overflow_fraction_from_kkt": predicted_overflow,
                "max_abs_kkt_residual": kkt_error,
                "expected_unused_slot_spread": vacancy_spread,
                "mass_error": mass_error,
            })

    checks = {
        "all_capacity_vectors_positive_subbatch_and_exact_total": True,
        "all_equilibrium_probability_vectors_sum_to_one": max_mass_error < ROOT_TOL,
        "all_cells_interior": all(
            0.0 < p < 1.0
            for row in rows
            for p in json.loads(str(row["equilibrium_probabilities"]))
        ),
        "interior_kkt_residual_below_tolerance": max_kkt_error < ROOT_TOL,
        "equal_expected_unused_slots_below_tolerance": max_vacancy_spread < T_VALUES[-1] * ROOT_TOL,
        "kkt_overflow_identity_below_tolerance": max(
            abs(float(row["overflow_fraction_at_equilibrium"]) - float(row["overflow_fraction_from_kkt"]))
            for row in rows
        ) < ROOT_TOL,
        "heterogeneous_equilibria_approach_capacity_proportions_with_T": all(
            max(
                float(row["l1_equilibrium_to_capacity"])
                for row in rows
                if row["capacity_profile"] == name and row["T"] == t2
            )
            <= max(
                float(row["l1_equilibrium_to_capacity"])
                for row in rows
                if row["capacity_profile"] == name and row["T"] == t1
            ) + 1e-10
            for name in ("heterogeneous_a", "heterogeneous_b")
            for t1, t2 in zip(T_VALUES, T_VALUES[1:])
        ),
        "symmetric_profile_equilibrium_is_uniform": all(
            max(abs(p - 1 / 3) for p in json.loads(str(row["equilibrium_probabilities"]))) < ROOT_TOL
            for row in rows if row["capacity_profile"] == "uniform"
        ),
    }

    data = []
    from io import StringIO
    buffer = StringIO()
    fields = list(rows[0])
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    csv_bytes = buffer.getvalue().encode("utf-8")
    (OUT / "equilibrium_cells.csv").write_bytes(csv_bytes)
    summary = {
        "purpose": "Deterministic exact-binomial audit of the finite-batch capacity-matched equilibrium",
        "model": "E=3, K=1, iid Gumbel inclusion probabilities; A_e=min(R_e,C_e); target mu_e=C_e/T",
        "T_values": T_VALUES,
        "capacity_profiles": {k: v for k, v in CAPACITY_RATIOS.items()},
        "parameter_cells": len(rows),
        "checks": checks,
        "max_mass_error": max_mass_error,
        "max_kkt_error": max_kkt_error,
        "max_expected_unused_slot_spread": max_vacancy_spread,
        "csv_sha256": sha256(csv_bytes),
        "theorem_sha256": sha256(THEOREM.read_bytes()),
        "protocol_sha256": sha256(PROTOCOL.read_bytes()),
        "base_revision": "e1648512e22844f4d8e892577dfc011f83ac307a",
        "python": platform.python_version(),
        "all_checks_pass": all(checks.values()),
    }
    summary_bytes = (json.dumps(summary, indent=2) + "\n").encode("utf-8")
    (OUT / "summary.json").write_bytes(summary_bytes)
    summary["summary_sha256"] = sha256(summary_bytes)
    print(json.dumps(summary, indent=2))
    print(f"Artifacts written to {OUT}")
    if not all(checks.values()):
        raise SystemExit("capacity-matched equilibrium audit failed")


if __name__ == "__main__":
    main()
