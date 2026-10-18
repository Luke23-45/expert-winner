#!/usr/bin/env python3
"""Exact-count audit of one-bit decision sufficiency in swapped Top-K worlds.

The main grid uses a deterministic reduced count-law formula. A separate
Fraction-based enumeration of the complete request-vector distribution checks
the sign-likelihood result on small cells. No Monte Carlo is used.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.stats import binom

from run_topk_swapped_saturation_value import (
    exact_bayes_errors,
    expected_overflow,
    float_inclusion,
    subset_distribution,
    target_score,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "saturation_multiplicity_one_bit_2026-10-18"
WEIGHT = Fraction(4, 3)
MAIN_E = (3, 5, 7)
MULTIPLIERS = (96, 192, 384)
SMALL_E = (3, 4)
SMALL_T = (2, 4, 6, 8)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def cell_laws(e: int, k: int):
    weights_plus = (WEIGHT,) + (Fraction(1),) * (e - 1)
    weights_minus = (Fraction(1), WEIGHT) + (Fraction(1),) * (e - 2)
    masks, p_sub_plus, p_inclusion_plus = subset_distribution(weights_plus, k)
    masks_minus, p_sub_minus, p_inclusion_minus = subset_distribution(weights_minus, k)
    if masks != masks_minus:
        raise AssertionError("worlds enumerated different Top-K subset alphabets")
    plus_map = dict(zip(masks, p_sub_plus, strict=True))
    minus_map = dict(zip(masks, p_sub_minus, strict=True))
    for mask in masks:
        swapped = (mask & ~0b11) | ((mask & 1) << 1) | ((mask & 2) >> 1)
        if minus_map[mask] != plus_map[swapped]:
            raise AssertionError("world laws are not an exact expert-1/2 swap")

    only_plus = [plus_map[m] for m in masks if (m & 1) and not (m & 2)]
    only_minus = [plus_map[m] for m in masks if (m & 2) and not (m & 1)]
    if not only_plus or not only_minus or len(set(only_plus)) != 1 or len(set(only_minus)) != 1:
        raise AssertionError("pair-symmetric PL subset categories are not constant")
    a, b = only_plus[0], only_minus[0]
    if not a > b:
        raise AssertionError("expert-1-only subset probability is not larger in world plus")
    p_plus = sum(only_plus, Fraction(0))
    p_minus = sum(only_minus, Fraction(0))
    p_both = sum((plus_map[m] for m in masks if (m & 1) and (m & 2)), Fraction(0))
    if sum(p_sub_plus, Fraction(0)) != 1 or sum(p_sub_minus, Fraction(0)) != 1:
        raise AssertionError("subset probabilities do not sum to one")
    return masks, p_sub_plus, p_sub_minus, p_inclusion_plus, p_inclusion_minus, a, b, p_plus, p_minus, p_both


def nearest_pair_capacity(target: Fraction, e: int, k: int, t: int) -> int:
    total = k * t
    modulus = e - 2
    lo = max(1, int(target * t) - 2 * e)
    hi = min(t - 1, int(target * t) + 2 * e)
    candidates = [c for c in range(lo, hi + 1) if (2 * c) % modulus == total % modulus]
    if not candidates:
        raise RuntimeError(f"no exact-total integer capacity: E={e}, K={k}, T={t}, target={target}")
    return min(candidates, key=lambda c: (abs(Fraction(c, t) - target), c))


def capacity_profile(e: int, k: int, t: int, p0: tuple[Fraction, ...], delta: Fraction, kind: str):
    low = p0[1]
    if kind == "one":
        target_pair = low + delta / 4
        target_tail = p0[2] + delta / (2 * (e - 2))
    elif kind == "two":
        target_pair = low - delta / 4
        target_tail = p0[2] + 3 * delta / (2 * (e - 2))
    else:
        raise ValueError(kind)
    cp = nearest_pair_capacity(target_pair, e, k, t)
    rem = k * t - 2 * cp
    if rem <= 0 or rem % (e - 2):
        raise RuntimeError("rounded pair capacity cannot yield equal integer tail capacities")
    ct = rem // (e - 2)
    caps = (cp,) * 2 + (ct,) * (e - 2)
    if sum(caps) != k * t or min(caps) <= 0 or max(caps) >= t:
        raise RuntimeError("capacity profile violates exact-total or range conditions")
    cfrac = tuple(Fraction(x, t) for x in caps)
    if kind == "one":
        if not (p0[0] > cfrac[0] > p0[1] and all(p0[j] < cfrac[j] for j in range(2, e))):
            raise RuntimeError(f"one-saturation margin failed for E={e},K={k},T={t}")
    else:
        if not (p0[0] > cfrac[0] and p0[1] > cfrac[1]
                and all(p0[j] < cfrac[j] for j in range(2, e))):
            raise RuntimeError(f"two-saturation margin failed for E={e},K={k},T={t}")
    return caps, cfrac


def sign_error(t: int, p_plus: float, p_minus: float) -> float:
    """Equal-prior Bayes error for Z=1{R1>R2}, tie assigned to either world."""
    pair_mass = p_plus + p_minus
    cond = p_plus / pair_mass
    m = np.arange(t + 1, dtype=np.int64)
    mass = binom.pmf(m, t, pair_mass)
    err = binom.cdf((m - 1) // 2, m, cond)
    even = (m % 2) == 0
    err[even] += 0.5 * binom.pmf(m[even] // 2, m[even], cond)
    return float(np.dot(mass, err))


def compositions(total: int, parts: int):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, parts - 1):
            yield (first,) + tail


def exact_small_cell(e: int, k: int, t: int):
    masks, p0s, p1s, _, _, a, b, *_ = cell_laws(e, k)
    incidence = [tuple((mask >> j) & 1 for j in range(e)) for mask in masks]
    mass0: dict[tuple[int, ...], Fraction] = defaultdict(Fraction)
    mass1: dict[tuple[int, ...], Fraction] = defaultdict(Fraction)
    for counts in compositions(t, len(masks)):
        denominator = math.prod(math.factorial(count) for count in counts)
        coeff = math.factorial(t) // denominator
        prob0 = Fraction(coeff)
        prob1 = Fraction(coeff)
        route = [0] * e
        for count, prob0_s, prob1_s, bits in zip(counts, p0s, p1s, incidence, strict=True):
            prob0 *= prob0_s ** count
            prob1 *= prob1_s ** count
            for j, bit in enumerate(bits):
                route[j] += count * bit
        key = tuple(route)
        mass0[key] += prob0
        mass1[key] += prob1
    if sum(mass0.values(), Fraction(0)) != 1 or sum(mass1.values(), Fraction(0)) != 1:
        raise AssertionError("enumerated request-vector law does not normalize")

    full_error = sum((min(mass0.get(r, Fraction(0)), mass1.get(r, Fraction(0)))
                      for r in mass0.keys() | mass1.keys()), Fraction(0)) / 2
    z0 = [Fraction(0), Fraction(0)]
    z1 = [Fraction(0), Fraction(0)]
    for r in mass0.keys() | mass1.keys():
        z = int(r[0] > r[1])
        z0[z] += mass0.get(r, Fraction(0))
        z1[z] += mass1.get(r, Fraction(0))
        d = r[0] - r[1]
        if mass1.get(r, Fraction(0)) == 0:
            raise AssertionError("positive request event has zero probability in swapped world")
        observed_ratio = mass0.get(r, Fraction(0)) / mass1.get(r, Fraction(0))
        if observed_ratio != (a / b) ** d:
            raise AssertionError("aggregated request likelihood ratio is not a function of R1-R2")
    bit_error = sum((min(z0[z], z1[z]) for z in (0, 1)), Fraction(0)) / 2
    if full_error != bit_error:
        raise AssertionError(f"exact full-R and one-bit risks differ: {full_error} != {bit_error}")
    return {
        "E": e,
        "K": k,
        "T": t,
        "request_vectors": len(mass0.keys() | mass1.keys()),
        "full_R_bayes_error_fraction": str(full_error),
        "one_bit_bayes_error_fraction": str(bit_error),
        "risk_equality_exact": True,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for e in MAIN_E:
        for k in range(1, e):
            (masks, p0_sub, p1_sub, p0_frac, p1_frac,
             a, b, p_plus, p_minus, p_both) = cell_laws(e, k)
            delta = p_plus - p_minus
            if delta <= 0:
                raise AssertionError("strict pair contrast is required")
            for mult in MULTIPLIERS:
                t = (e - 2) * mult
                for kind in ("one", "two"):
                    caps_int, cfrac = capacity_profile(e, k, t, p0_frac, delta, kind)
                    full_error, admitted_error = exact_bayes_errors(
                        t, caps_int[0], float(p_plus), float(p_minus), float(p_both)
                    )
                    bit_err = sign_error(t, float(p_plus), float(p_minus))
                    if abs(full_error - bit_err) > 2e-12:
                        raise AssertionError(f"reduced full-R and independent sign risks differ: {e},{k},{t}")

                    cfrac_array = np.asarray([float(x) for x in cfrac], dtype=float)
                    caps_array = np.asarray(caps_int, dtype=np.int64)
                    logits_cap, residual = target_score(cfrac_array, k)
                    if residual > 1e-8:
                        raise RuntimeError(f"target pressure solver residual exceeds 1e-8: {residual}")
                    theta0 = np.log(np.array([float(WEIGHT)] + [1.0] * (e - 1)))
                    theta1 = np.log(np.array([1.0, float(WEIGHT)] + [1.0] * (e - 2)))
                    q0, q1 = theta0 - logits_cap, theta1 - logits_cap
                    q0 -= q0.mean()
                    q1 -= q1.mean()
                    incl = np.empty((2, 2, e), dtype=float)
                    for h, theta in enumerate((theta0, theta1)):
                        for act, q in enumerate((q0, q1)):
                            incl[h, act] = float_inclusion(theta - q, k)
                    risk = np.array([
                        [expected_overflow(t, caps_array, incl[h, act], k) for act in range(2)]
                        for h in range(2)
                    ])
                    if not (abs(risk[0, 0] - risk[1, 1]) < 2e-9
                            and abs(risk[0, 1] - risk[1, 0]) < 2e-9
                            and risk[0, 1] > risk[0, 0]):
                        raise AssertionError(f"target-action risk conditions failed: E={e},K={k},T={t},type={kind}")

                    loss_gap = float(risk[0, 1] - risk[0, 0])
                    vr = float(risk[0, 0]) + full_error * loss_gap
                    vz = float(risk[0, 0]) + bit_err * loss_gap
                    va = float(risk[0, 0]) + admitted_error * loss_gap
                    rows.append({
                        "E": e, "K": k, "T": t, "profile": kind,
                        "capacity_pair": caps_int[0], "capacity_tail": caps_int[2],
                        "capacity_total": sum(caps_int), "request_mass": k * t,
                        "p_only_1": float(p_plus), "p_only_2": float(p_minus),
                        "pair_contrast": float(delta), "subset_likelihood_ratio": str(a / b),
                        "error_full_R": full_error, "error_one_bit": bit_err,
                        "error_A_only": admitted_error,
                        "risk_full_R_two_action": vr, "risk_one_bit_two_action": vz,
                        "risk_A_only_two_action": va,
                        "one_bit_minus_full_R": vz - vr,
                        "A_only_minus_one_bit": va - vz,
                        "target_risk_correct": float(risk[0, 0]),
                        "target_risk_wrong": float(risk[0, 1]),
                        "target_solver_residual": residual,
                        "capacity_checks_passed": True,
                        "exact_signal_identity_passed": abs(vz - vr) <= 2e-12,
                    })

    small = []
    for e in SMALL_E:
        for k in range(1, e):
            for t in SMALL_T:
                if t < k:
                    continue
                small.append(exact_small_cell(e, k, t))

    cells_path = OUT / "main_grid.csv"
    with cells_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    small_path = OUT / "exact_rational_small_grid.csv"
    with small_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(small[0]))
        writer.writeheader()
        writer.writerows(small)

    summary = {
        "experiment": "one-bit decision sufficiency in saturation-multiplicity Top-K family",
        "protocol": "docs/paper/saturation_multiplicity_one_bit_experiment_protocol_2026-10-18.md",
        "main_grid_cells": len(rows),
        "main_grid_profiles": {p: sum(r["profile"] == p for r in rows) for p in ("one", "two")},
        "small_exact_rational_cells": len(small),
        "all_one_bit_equals_full_R": all(r["exact_signal_identity_passed"] for r in rows)
            and all(r["risk_equality_exact"] for r in small),
        "all_capacity_and_target_checks_passed": all(r["capacity_checks_passed"] for r in rows),
        "all_two_saturation_A_only_gaps_strictly_positive": all(
            r["A_only_minus_one_bit"] > 0 for r in rows if r["profile"] == "two"
        ),
        "minimum_two_saturation_A_only_gap": min(
            r["A_only_minus_one_bit"] for r in rows if r["profile"] == "two"
        ),
        "mean_two_saturation_A_only_gap": float(np.mean([
            r["A_only_minus_one_bit"] for r in rows if r["profile"] == "two"
        ])),
        "main_grid_sha256": sha256(cells_path),
        "small_grid_sha256": sha256(small_path),
        "runner_sha256": sha256(Path(__file__)),
        "master_weight_ratio": str(WEIGHT),
        "main_E": MAIN_E,
        "multipliers": MULTIPLIERS,
    }
    if not summary["all_one_bit_equals_full_R"]:
        raise AssertionError("one-bit/full-R equality failed")
    if not summary["all_capacity_and_target_checks_passed"]:
        raise AssertionError("capacity or target check failed")
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
