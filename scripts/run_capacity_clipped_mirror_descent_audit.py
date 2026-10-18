#!/usr/bin/env python3
"""Exact-binomial/float audit of the Top-1 capacity-clipped mirror step."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/capacity_clipped_topk_mirror_descent_protocol_2026-10-17.md"
OUT = ROOT / "results/capacity_clipped_mirror_descent_audit"
P_PROFILES = {
    "uniform": (Fraction(1, 3),) * 3,
    "skew_left": (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
    "skew_right": (Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)),
}
ETAS = (Fraction(1, 100), Fraction(1, 20), Fraction(1, 10))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def admitted_mean_fraction(T: int, C: int, p: Fraction) -> Fraction:
    return sum(
        (min(k, C) * math.comb(T, k) * p**k * (1 - p) ** (T - k)
         for k in range(T + 1)),
        Fraction(0),
    ) / T


def softmax(xs: list[float]) -> list[float]:
    m = max(xs)
    vals = [math.exp(x - m) for x in xs]
    z = sum(vals)
    return [v / z for v in vals]


def project_gauge(q: list[float]) -> list[float]:
    m = min(q)
    return [v - m for v in q]


def calculate(T: int, caps: tuple[int, int, int], probs: tuple[Fraction, ...],
              target: tuple[Fraction, ...], eta: Fraction,
              gauge_shift: float = 0.0) -> tuple[list[float], list[float], list[Fraction]]:
    gamma = 1.0
    # theta=-q and q=-log(p) is a legal nonnegative representative.
    q = [-math.log(float(p)) + gauge_shift for p in probs]
    eps = [admitted_mean_fraction(T, C, p) - mu
           for C, p, mu in zip(caps, probs, target)]

    q_next = project_gauge(
        [q_e + float(eta) * gamma * float(e_e) for q_e, e_e in zip(q, eps)]
    )
    from_pressure = softmax([-gamma * q_e for q_e in q_next])

    # Entropic mirror descent with alpha=eta*gamma^2 and grad L_A=eps.
    log_weights = [math.log(float(p)) - float(eta) * gamma**2 * float(e)
                   for p, e in zip(probs, eps)]
    from_mirror = softmax(log_weights)
    return from_pressure, from_mirror, eps


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    max_error = 0.0
    max_gauge_error = 0.0
    no_clip_rows = 0
    cell_count = 0

    for T in (12, 24, 60):
        uniform_caps = (T // 3,) * 3
        hetero_caps = (T // 6, 5 * T // 12, 5 * T // 12)
        cap_profiles = {
            "uniform_exact_total": uniform_caps,
            "heterogeneous_exact_total": hetero_caps,
            "no_clipping": (T, T, T),
        }
        for cap_name, caps in cap_profiles.items():
            assert all(isinstance(c, int) and c > 0 for c in caps)
            if cap_name != "no_clipping":
                assert sum(caps) == T
            for p_name, probs in P_PROFILES.items():
                for mu_name, target in {
                    "uniform_target": (Fraction(1, 3),) * 3,
                    "capacity_target": tuple(Fraction(c, sum(caps)) for c in caps),
                }.items():
                    for eta in ETAS:
                        base, mirror, eps = calculate(T, caps, probs, target, eta)
                        error = max(abs(a - b) for a, b in zip(base, mirror))
                        shifted, _, _ = calculate(T, caps, probs, target, eta, 17.25)
                        gauge_error = max(abs(a - b) for a, b in zip(base, shifted))
                        max_error = max(max_error, error)
                        max_gauge_error = max(max_gauge_error, gauge_error)
                        assert error < 2e-14, (T, caps, probs, target, eta, error)
                        assert gauge_error < 2e-14, (T, caps, probs, target, eta, gauge_error)

                        if cap_name == "no_clipping":
                            req_eps = [p - mu for p, mu in zip(probs, target)]
                            req_weights = [math.log(float(p)) - float(eta) * float(e)
                                           for p, e in zip(probs, req_eps)]
                            req_next = softmax(req_weights)
                            req_err = max(abs(a - b) for a, b in zip(base, req_next))
                            assert req_err < 2e-14, req_err
                            no_clip_rows += 1

                        rows.append({
                            "T": T,
                            "capacity_profile": cap_name,
                            "capacities": ",".join(map(str, caps)),
                            "probability_profile": p_name,
                            "probabilities": ",".join(map(str, probs)),
                            "target_profile": mu_name,
                            "target": ",".join(map(str, target)),
                            "eta": str(eta),
                            "expected_admitted_error": ",".join(map(str, eps)),
                            "max_pressure_vs_mirror_error": f"{error:.17g}",
                            "max_gauge_shift_error": f"{gauge_error:.17g}",
                        })
                        cell_count += 1

    csv_path = OUT / "mirror_step_cells.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    csv_bytes = csv_path.read_bytes()
    summary = {
        "model": "E=3,K=1,iid standard Gumbel, fresh-batch conditional mean, canonical A=min(R,C)",
        "cells": cell_count,
        "max_pressure_vs_mirror_probability_error": max_error,
        "max_common_shift_gauge_error": max_gauge_error,
        "no_clipping_requested_formula_controls": no_clip_rows,
        "all_capacity_and_exact_total_checks_passed": True,
        "all_identity_tolerances_passed": True,
        "claims_not_tested": [
            "closed-loop convergence or monotone objective decrease",
            "finite-batch stochastic trajectory concentration",
            "reused-affinity empirical trajectory equivalence",
            "real-system cost or model-quality benefit",
            "conference novelty",
        ],
        "protocol_sha256": sha256(PROTOCOL.read_bytes()),
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "csv_sha256": sha256(csv_bytes),
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
