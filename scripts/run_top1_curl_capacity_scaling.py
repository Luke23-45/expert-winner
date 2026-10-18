#!/usr/bin/env python3
"""Exact rational audit of the three-expert Top-1 admitted-field curl."""

from __future__ import annotations

import csv
import hashlib
import json
from fractions import Fraction
from math import comb
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/top1_curl_capacity_scaling_protocol_2026-10-17.md"
OUT = ROOT / "results/top1_curl_capacity_scaling"
P_MAIN = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
P_MIRROR = (Fraction(1, 6), Fraction(1, 3), Fraction(1, 2))
P_UNIFORM = (Fraction(1, 3),) * 3


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def alpha(T: int, C: int, p: Fraction) -> Fraction:
    """Pr[Binomial(T-1,p) < C], evaluated exactly."""
    return sum(
        (Fraction(comb(T - 1, j)) * p**j * (1 - p) ** (T - 1 - j)
         for j in range(C)),
        Fraction(0),
    )


def curl(T: int, C: int, probs: tuple[Fraction, Fraction, Fraction]) -> Fraction:
    x, y, z = probs
    gx = x * alpha(T, C, x)
    gy = y * alpha(T, C, y)
    gz = z * alpha(T, C, z)
    return gx * (y - z) + gy * (z - x) + gz * (x - y)


def row(T: int, C: int, label: str,
        probs: tuple[Fraction, Fraction, Fraction], omega: Fraction) -> dict[str, object]:
    return {
        "T": T,
        "C": C,
        "condition": label,
        "p1": str(probs[0]),
        "p2": str(probs[1]),
        "p3": str(probs[2]),
        "alpha1": str(alpha(T, C, probs[0])),
        "alpha2": str(alpha(T, C, probs[1])),
        "alpha3": str(alpha(T, C, probs[2])),
        "omega_exact": str(omega),
        "omega_float": float(omega),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    main_values: list[Fraction] = []
    symmetric_zeros = 0
    no_clip_zeros = 0
    mirror_checks = 0

    for m in range(1, 31):
        T, C = 3 * m, m
        assert 3 * C == T and 1 <= C < T

        value = curl(T, C, P_MAIN)
        assert value != 0, (T, C, value)
        main_values.append(value)
        rows.append(row(T, C, "exact_total_skew", P_MAIN, value))

        symmetric = curl(T, C, P_UNIFORM)
        assert symmetric == 0, (T, C, symmetric)
        symmetric_zeros += 1
        rows.append(row(T, C, "uniform_symmetry_control", P_UNIFORM, symmetric))

        unclipped = curl(T, T, P_MAIN)
        assert unclipped == 0, (T, T, unclipped)
        no_clip_zeros += 1
        rows.append(row(T, T, "no_clipping_control", P_MAIN, unclipped))

        mirrored = curl(T, C, P_MIRROR)
        assert mirrored == -value, (T, C, value, mirrored)
        mirror_checks += 1
        rows.append(row(T, C, "expert_swap_orientation_control", P_MIRROR, mirrored))

    assert all(v < 0 for v in main_values)

    columns = list(rows[0])
    csv_path = OUT / "curl_cells.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    csv_bytes = csv_path.read_bytes()

    summary = {
        "model": "E=3, K=1, iid standard Gumbel, per-expert A=min(R,C), gamma=1",
        "main_design": "T=3m, C=m, m=1..30, p=(1/2,1/3,1/6)",
        "main_cells": len(main_values),
        "main_nonzero_curls": sum(v != 0 for v in main_values),
        "main_orientation": "all negative for the registered expert ordering",
        "main_omega_at_T3": str(main_values[0]),
        "main_omega_at_T90": str(main_values[-1]),
        "uniform_symmetry_zero_controls": symmetric_zeros,
        "no_clipping_zero_controls": no_clip_zeros,
        "expert_swap_sign_checks": mirror_checks,
        "exact_rational_arithmetic": True,
        "claims_not_tested": [
            "open-set non-potentiality (proved analytically, not by this grid)",
            "closed-loop controller stability or overflow ranking",
            "real-router prevalence or model-quality benefit",
            "novelty against the full prior literature",
        ],
        "protocol_sha256": sha256(PROTOCOL.read_bytes()),
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "csv_sha256": sha256(csv_bytes),
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
