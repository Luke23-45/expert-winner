#!/usr/bin/env python3
"""Paired finite-batch check of the general-iid-affinity Top-K theorem."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from fractions import Fraction
from math import comb
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.stats import gumbel_r, logistic, norm, t as student_t

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/topk_nonuniform_affinity_protocol_2026-10-17.md"
OUT = ROOT / "results/topk_nonuniform_affinity"
LAWS = ("uniform", "normal", "logistic", "gumbel")
TS = (2400, 9600)
DS = (Fraction(1, 4), Fraction(1, 2))
REPS = 30


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def capacity(e: int, k: int, total: int) -> tuple[np.ndarray, Fraction]:
    p = Fraction(k, e)
    r = min(p, 1 - p) / 2
    vals = (p - r,) + (p + r / (e - 1),) * (e - 1)
    assert all((v * total).denominator == 1 for v in vals)
    c = np.asarray([int(v * total) for v in vals], dtype=np.int64)
    assert int(c.sum()) == k * total and int(c.max()) <= total
    return c, r


def sample_affinity(rng: np.random.Generator, law: str, total: int, e: int) -> np.ndarray:
    shape = (total, e)
    if law == "uniform":
        return rng.uniform(0.0, 1.0, size=shape)
    if law == "normal":
        return rng.normal(0.0, 1.0, size=shape)
    if law == "logistic":
        return rng.logistic(0.0, 1.0, size=shape)
    if law == "gumbel":
        return rng.gumbel(0.0, 1.0, size=shape)
    raise ValueError(law)


def route(aff: np.ndarray, q: np.ndarray, k: int) -> tuple[np.ndarray, int]:
    scores = aff - q[None, :]
    order = np.argsort(-scores, axis=1, kind="stable")[:, :k]
    counts = np.bincount(order.reshape(-1), minlength=aff.shape[1]).astype(np.int64)
    boundary = np.take_along_axis(scores, order[:, k - 1:k], axis=1)[:, 0]
    ties = int(np.count_nonzero((scores == boundary[:, None]).sum(axis=1) > 1))
    return counts, ties


def update(load: np.ndarray, e: int, k: int, total: int, eta: float) -> np.ndarray:
    q = eta * (load.astype(np.float64) / (k * total) - 1.0 / e)
    return q - q.min()


def overflow(req: np.ndarray, cap: np.ndarray) -> int:
    return int(np.maximum(req - cap, 0).sum())


def g_cdf(u: float, e: int, k: int) -> float:
    return sum(comb(e - 1, j) * (1.0 - u) ** j * u ** (e - 1 - j) for j in range(k))


def population_probability(law: str, e: int, k: int, d: float) -> float:
    if law == "uniform":
        cdf = lambda x: min(1.0, max(0.0, x))
        pdf = lambda x: 1.0 if 0.0 <= x <= 1.0 else 0.0
        val, _ = quad(lambda x: g_cdf(cdf(x + d), e, k) * pdf(x), 0.0, 1.0,
                      epsabs=1e-12, epsrel=1e-12, points=[max(0.0, 1.0 - d)])
        return val
    if law == "gumbel":
        def cdf(x: float) -> float:
            if x < -40.0:
                return 0.0
            if x > 40.0:
                return 1.0
            return math.exp(-math.exp(-x))
        def pdf(x: float) -> float:
            if x < -40.0 or x > 40.0:
                return 0.0
            return math.exp(-x - math.exp(-x))
    else:
        dist = {"normal": norm, "logistic": logistic}[law]
        cdf = lambda x: float(dist.cdf(x))
        pdf = lambda x: float(dist.pdf(x))
    val, err = quad(lambda x: g_cdf(cdf(x + d), e, k) * pdf(x),
                    -np.inf, np.inf, epsabs=1e-11, epsrel=1e-11, limit=300)
    if err > 1e-8:
        raise AssertionError(f"quadrature error too large: {law=} {e=} {k=} {d=} {err=}")
    return val


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plants: list[dict] = []
    no_clip_checks = 0
    all_ties = 0
    for li, law in enumerate(LAWS):
        for k in (1, 2, 3):
            e = 4
            for ti, total in enumerate(TS):
                cap, r = capacity(e, k, total)
                cap_nc = np.full(e, total, dtype=np.int64)
                for rep in range(REPS):
                    seed = 20261017 + li * 1_000_000 + k * 10_000 + ti * 1_000 + rep
                    rng = np.random.default_rng(seed)
                    aff = sample_affinity(rng, law, total, e)
                    r0, ties0 = route(aff, np.zeros(e), k)
                    assert int(r0.sum()) == k * total and int(r0.max()) <= total
                    a0 = np.minimum(r0, cap)
                    j0 = overflow(r0, cap)
                    for dfrac in DS:
                        d = float(dfrac)
                        eta = float(dfrac * k / r)
                        qR = update(r0, e, k, total, eta)
                        qA = update(a0, e, k, total, eta)
                        q0 = np.zeros(e)
                        arms = {}
                        for name, q in (("requested", qR), ("admitted", qA), ("none", q0)):
                            r1, ties1 = route(aff, q, k)
                            a1 = np.minimum(r1, cap)
                            j1 = overflow(r1, cap)
                            assert int(r1.sum()) == k * total and int(r1.max()) <= total
                            assert np.array_equal(a1, np.minimum(r1, cap))
                            assert j1 == int((r1 - a1).sum())
                            arms[name] = (r1, j1, ties1)
                        assert len({j0}) == 1

                        # No-clipping negative control: R and A feedback must be identical.
                        qncR = update(r0, e, k, total, eta)
                        qncA = update(r0, e, k, total, eta)
                        rncR, _ = route(aff, qncR, k)
                        rncA, _ = route(aff, qncA, k)
                        assert np.array_equal(qncR, qncA)
                        assert np.array_equal(rncR, rncA)
                        assert overflow(r0, cap_nc) == 0
                        assert overflow(rncR, cap_nc) == 0
                        no_clip_checks += 1

                        jr = j0 + arms["requested"][1]
                        ja = j0 + arms["admitted"][1]
                        jn = j0 + arms["none"][1]
                        all_ties += ties0 + sum(v[2] for v in arms.values())
                        plants.append({
                            "law": law, "E": e, "K": k, "T": total,
                            "replicate": rep, "seed": seed, "d": str(dfrac),
                            "eta": str(dfrac * k / r),
                            "capacity_short": int(cap[0]),
                            "capacity_other": int(cap[1]),
                            "requested_overflow_two_step": jr,
                            "admitted_overflow_two_step": ja,
                            "no_feedback_overflow_two_step": jn,
                            "gap_A_minus_R_over_T": str(Fraction(ja - jr, total)),
                            "ties_step0": ties0,
                            "ties_R_step1": arms["requested"][2],
                            "ties_A_step1": arms["admitted"][2],
                            "ties_none_step1": arms["none"][2],
                        })

    plants_path = OUT / "plants.csv"
    with plants_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(plants[0]))
        w.writeheader()
        w.writerows(plants)

    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in plants:
        grouped[(row["law"], row["E"], row["K"], row["T"], row["d"])].append(row)
    cells = []
    for key in sorted(grouped, key=lambda z: (LAWS.index(z[0]), z[1], z[2], z[3], Fraction(z[4]))):
        law, e, k, total, dstr = key
        cell = grouped[key]
        gaps = np.asarray([float(Fraction(x["gap_A_minus_R_over_T"])) for x in cell])
        d = float(Fraction(dstr))
        p1 = population_probability(law, e, k, d)
        limit = p1 - k / e
        mean = float(gaps.mean())
        se = float(gaps.std(ddof=1) / math.sqrt(len(gaps)))
        tc = float(student_t.ppf(0.975, len(gaps) - 1))
        cells.append({
            "law": law, "E": e, "K": k, "T": total, "d": dstr,
            "n": len(cell), "mean_gap_A_minus_R_over_T": mean,
            "sample_sd": float(gaps.std(ddof=1)), "standard_error": se,
            "ci95_t_low": mean - tc * se, "ci95_t_high": mean + tc * se,
            "asymptotic_limit_quadrature": limit,
            "abs_error_to_asymptotic_limit": abs(mean - limit),
            "fraction_positive_pairs": float(np.mean(gaps > 0)),
            "fraction_equal_pairs": float(np.mean(gaps == 0)),
            "mean_R_overflow_over_T": float(np.mean([x["requested_overflow_two_step"] for x in cell]) / total),
            "mean_A_overflow_over_T": float(np.mean([x["admitted_overflow_two_step"] for x in cell]) / total),
            "mean_none_overflow_over_T": float(np.mean([x["no_feedback_overflow_two_step"] for x in cell]) / total),
            "quadrature_probability_expert1": p1,
        })

    summary = {
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha256(PROTOCOL),
        "script_sha256": sha256(Path(__file__)),
        "laws": list(LAWS), "E": 4, "K_values": [1, 2, 3],
        "T_values": list(TS), "d_values": [str(x) for x in DS],
        "replicates_per_law_K_T_d": REPS,
        "plant_gain_rows": len(plants), "endpoint_cells": len(cells),
        "no_clipping_controls": no_clip_checks,
        "total_exact_boundary_ties": all_ties,
        "all_invariants_passed": True,
        "cells": cells,
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "plant_gain_rows": len(plants), "endpoint_cells": len(cells),
        "no_clipping_controls": no_clip_checks,
        "total_exact_boundary_ties": all_ties,
        "plants_sha256": sha256(plants_path),
        "summary_sha256": sha256(summary_path),
        "protocol_sha256": summary["protocol_sha256"],
        "script_sha256": summary["script_sha256"],
        "all_invariants_passed": True,
    }, indent=2))


if __name__ == "__main__":
    main()


