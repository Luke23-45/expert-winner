#!/usr/bin/env python3
"""Paired Top-K experiment separating capacity-target mismatch from signal choice."""
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
from scipy.stats import binom as binom_dist, t as student_t

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/capacity_matched_target_experiment_protocol_2026-10-18.md"
OUT = ROOT / "results/capacity_matched_target_2026-10-18"
E = 4
R = Fraction(1, 48)
KS = (1, 2, 3)
TS = (2304, 9216)
REPS = 12
HORIZONS = (1, 2, 4, 8, 16, 32, 64)
ARMS = (("uniform", "requested"), ("uniform", "admitted"),
        ("capacity", "requested"), ("capacity", "admitted"))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def capacities(k: int, total: int) -> np.ndarray:
    p = Fraction(k, E)
    vals = (p - R,) + (p + R / (E - 1),) * (E - 1)
    assert all((v * total).denominator == 1 for v in vals)
    out = np.asarray([int(v * total) for v in vals], dtype=np.int64)
    assert int(out.sum()) == k * total and int(out.max()) < total
    return out


def route(a: np.ndarray, q: np.ndarray, k: int) -> tuple[np.ndarray, int]:
    scores = a - q[None, :]
    idx = np.argsort(-scores, axis=1, kind="stable")[:, :k]
    counts = np.bincount(idx.reshape(-1), minlength=E).astype(np.int64)
    cutoff = np.take_along_axis(scores, idx[:, -1:], axis=1)[:, 0]
    ties = int(np.count_nonzero((scores == cutoff[:, None]).sum(axis=1) > 1))
    return counts, ties


def update(q: np.ndarray, load: np.ndarray, mu: np.ndarray, k: int,
           total: int, eta: float) -> np.ndarray:
    nxt = q + eta * (load.astype(np.float64) / (k * total) - mu)
    return nxt - nxt.min()


def overflow(req: np.ndarray, cap: np.ndarray) -> int:
    return int(np.maximum(req - cap, 0).sum())


def p_topk(x: float, k: int) -> float:
    if x == 0.0:
        return k / E

    def cdf(y: float) -> float:
        if y < -40:
            return 0.0
        if y > 40:
            return 1.0
        return math.exp(-math.exp(-y))

    def pdf(y: float) -> float:
        if y < -40 or y > 40:
            return 0.0
        return math.exp(-y - math.exp(-y))

    def g(u: float) -> float:
        return math.fsum(comb(E - 1, j) * (1 - u) ** j * u ** (E - 1 - j)
                         for j in range(k))

    value, err = quad(lambda y: g(cdf(y + x)) * pdf(y), -np.inf, np.inf,
                      epsabs=1e-11, epsrel=1e-11, limit=300)
    if err > 1e-8:
        raise ArithmeticError((x, k, err))
    return value


def clipped_mean(total: int, p: float, cap: int) -> float:
    return float(np.sum(binom_dist.sf(np.arange(cap, dtype=np.int64), total, p)))


def expected_overflow(total: int, p: float, cap: int) -> float:
    return total * p - clipped_mean(total, p, cap)


def gain(k: int) -> tuple[float, float]:
    lf = (1 / math.e) * (E - 1) * comb(E - 2, k - 1)
    eta = 0.8 * k * (E - 1) / (E * lf)
    return eta, lf


def target_vector(target: str, cap: np.ndarray, k: int, total: int) -> np.ndarray:
    if target == "uniform":
        return np.full(E, 1 / E, dtype=np.float64)
    if target == "capacity":
        return cap.astype(np.float64) / (k * total)
    raise ValueError(target)


def simulate_one(k: int, total: int, cap: np.ndarray, eta: float,
                 batches: list[np.ndarray], regime: str, seed: int,
                 pred_pop: dict[tuple[str, str], list[float]],
                 pred_finite: dict[tuple[str, str], list[float]]) -> list[dict]:
    qs = {arm: np.zeros(E, dtype=np.float64) for arm in ARMS}
    cum = {arm: 0 for arm in ARMS}
    cum_none = 0
    rows: list[dict] = []
    by_h = set(HORIZONS)
    total_ties = 0
    for n, aff in enumerate(batches, start=1):
        costs = {}
        for arm in ARMS:
            target, signal = arm
            q = qs[arm]
            req, ties = route(aff, q, k)
            total_ties += ties
            adm = np.minimum(req, cap)
            cost = overflow(req, cap)
            assert int(req.sum()) == k * total and int(req.max()) <= total
            assert np.array_equal(adm, np.minimum(req, cap))
            assert cost == int((req - adm).sum())
            costs[arm] = cost
            cum[arm] += cost
            load = req if signal == "requested" else adm
            qs[arm] = update(q, load, target_vector(target, cap, k, total),
                             k, total, eta)
        base_req, base_ties = route(aff, np.zeros(E), k)
        total_ties += base_ties
        cum_none += overflow(base_req, cap)
        if n == 1:
            assert len(set(costs.values())) == 1
        if n in by_h:
            for target, signal in ARMS:
                rows.append({
                    "regime": regime, "K": k, "T": total, "replicate": seed,
                    "H": n, "target": target, "signal": signal, "eta": eta,
                    "cumulative_overflow_over_T": cum[(target, signal)] / total,
                    "population_prediction": pred_pop[(target, signal)][n - 1],
                    "finiteT_mean_recursion_prediction": pred_finite[(target, signal)][n - 1],
                    "ties": total_ties,
                })
            rows.append({
                "regime": regime, "K": k, "T": total, "replicate": seed,
                "H": n, "target": "none", "signal": "none", "eta": 0.0,
                "cumulative_overflow_over_T": cum_none / total,
                "population_prediction": n * float(R),
                "finiteT_mean_recursion_prediction": n * (
                    sum(expected_overflow(total, k / E, int(c)) for c in cap) / total),
                "ties": total_ties,
            })
    assert total_ties == 0, f"tie detected in registered replicate {seed}"
    return rows


def no_clipping_control(k: int, total: int, eta: float, seed: int) -> None:
    rng = np.random.default_rng(seed)
    q = {arm: np.zeros(E, dtype=np.float64) for arm in ARMS}
    cap = np.full(E, total, dtype=np.int64)
    mu = np.full(E, 1 / E, dtype=np.float64)
    for _ in range(max(HORIZONS)):
        aff = rng.gumbel(size=(total, E))
        reqs = {arm: route(aff, q[arm], k)[0] for arm in ARMS}
        assert all(np.array_equal(reqs[ARMS[0]], reqs[a]) for a in ARMS)
        for arm in ARMS:
            q[arm] = update(q[arm], reqs[arm], mu, k, total, eta)
        assert all(np.array_equal(q[ARMS[0]], q[a]) for a in ARMS)


def summarize(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[(row["regime"], row["K"], row["T"], row["H"], row["target"], row["signal"])].append(row)
    out = []
    for key, vals in sorted(groups.items()):
        arr = np.asarray([v["cumulative_overflow_over_T"] for v in vals], dtype=float)
        n = len(arr)
        mean = float(arr.mean())
        se = float(arr.std(ddof=1) / math.sqrt(n))
        tcrit = float(student_t.ppf(0.975, n - 1))
        out.append({"regime": key[0], "K": key[1], "T": key[2], "H": key[3],
                    "target": key[4], "signal": key[5], "n": n,
                    "mean_overflow_over_T": mean,
                    "ci95_low": mean - tcrit * se, "ci95_high": mean + tcrit * se,
                    "median": float(np.median(arr)),
                    "population_prediction": vals[0]["population_prediction"],
                    "finiteT_mean_recursion_prediction": vals[0]["finiteT_mean_recursion_prediction"],
                    "population_abs_error": abs(mean - vals[0]["population_prediction"]),
                    "finiteT_abs_error": abs(mean - vals[0]["finiteT_mean_recursion_prediction"]),
                    "fraction_positive_vs_no_feedback": None})
    # Pair each controller trajectory against no-feedback using the same replicate.
    index = {(r["regime"], r["K"], r["T"], r["H"], r["replicate"], r["target"], r["signal"]): r
             for r in rows}
    contrasts = []
    contrast_defs = (
        ("A_uniform_minus_R_uniform", [("uniform", "admitted", 1), ("uniform", "requested", -1)]),
        ("A_capacity_minus_R_capacity", [("capacity", "admitted", 1), ("capacity", "requested", -1)]),
        ("A_capacity_minus_none", [("capacity", "admitted", 1), ("none", "none", -1)]),
        ("target_interaction", [("capacity", "admitted", 1), ("capacity", "requested", -1),
                                ("uniform", "admitted", -1), ("uniform", "requested", 1)]),
    )
    for regime in ("static", "fresh"):
        for k in KS:
            for total in TS:
                for h in HORIZONS:
                    for name, terms in contrast_defs:
                        d = []
                        for rep in range(REPS):
                            seed = 2026101800 + k * 100000 + TS.index(total) * 10000 + rep
                            value = 0.0
                            for target, signal, sign in terms:
                                value += sign * index[(regime, k, total, h, seed, target, signal)]["cumulative_overflow_over_T"]
                            d.append(value)
                        a = np.asarray(d, dtype=float)
                        se = float(a.std(ddof=1) / math.sqrt(len(a)))
                        tc = float(student_t.ppf(0.975, len(a) - 1))
                        contrasts.append({"regime": regime, "K": k, "T": total, "H": h,
                                          "contrast": name,
                                          "mean": float(a.mean()), "ci95_low": float(a.mean() - tc * se),
                                          "ci95_high": float(a.mean() + tc * se),
                                          "fraction_positive": float(np.mean(a > 0))})
    return out, contrasts


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    ties = controls = 0
    for ki, k in enumerate(KS):
        eta, lf = gain(k)
        assert eta <= k * (E - 1) / (E * lf) + 1e-12
        for ti, total in enumerate(TS):
            cap = capacities(k, total)
            # Existing formulas yield the T-infinity one-step population dynamics.
            pop_pred_limit = population_predictions_limit(k, cap, eta, max(HORIZONS))
            finite_pred = finite_predictions(k, total, cap, eta, max(HORIZONS))
            for rep in range(REPS):
                seed = 2026101800 + k * 100000 + ti * 10000 + rep
                rng = np.random.default_rng(seed)
                batches = [rng.gumbel(size=(total, E)) for _ in range(max(HORIZONS))]
                for regime in ("static", "fresh"):
                    use = [batches[0]] * max(HORIZONS) if regime == "static" else batches
                    pred = {arm: pop_pred_limit[arm] for arm in ARMS}
                    fpred = {arm: finite_pred[arm] for arm in ARMS}
                    emitted = simulate_one(k, total, cap, eta, use, regime, seed,
                                           pred, fpred)
                    rows.extend(emitted)
                    # simulate_one rejects a tied trajectory rather than dropping it.
                no_clipping_control(k, total, eta, seed + 9000000)
                controls += 1
    raw = OUT / "plants.csv"
    with raw.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    cells, contrasts = summarize(rows)
    for name, data in (("cells.csv", cells), ("contrasts.csv", contrasts)):
        with (OUT / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader(); w.writerows(data)
    summary = {
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha(PROTOCOL), "script_sha256": sha(Path(__file__)),
        "plants_sha256": sha(raw), "cells_sha256": sha(OUT / "cells.csv"),
        "contrasts_sha256": sha(OUT / "contrasts.csv"),
        "rows": len(rows), "controller_cells": len(cells), "paired_contrasts": len(contrasts),
        "E": E, "K_values": list(KS), "T_values": list(TS),
        "H_values": list(HORIZONS), "replicates_per_cell": REPS,
        "temporal_regimes": ["static", "fresh"], "no_clipping_controls": controls,
        "all_invariants_passed": True, "ties": ties,
        "interpretation": "Synthetic paired study of target choice and feedback signal; no system-cost claim.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


def population_predictions_limit(k: int, cap: np.ndarray, eta: float,
                                 max_h: int) -> dict[tuple[str, str], list[float]]:
    out = {}
    cs, cr = (cap / (cap.sum() / k)).tolist()[:2]  # capacity/T, since sum(C)=K*T
    p = k / E
    for target, signal in ARMS:
        mu = np.full(E, 1 / E) if target == "uniform" else cap / cap.sum()
        x = 0.0
        cum = 0.0
        vals = []
        for _ in range(max_h):
            ps = p_topk(x, k); pr = (k - ps) / (E - 1)
            cost = max(ps - cs, 0.0) + (E - 1) * max(pr - cr, 0.0)
            cum += cost; vals.append(cum)
            if signal == "requested":
                ls, lr = ps, pr
            else:
                ls, lr = min(ps, cs), min(pr, cr)
            dx = eta * ((lr / k - mu[1]) - (ls / k - mu[0]))
            x += dx
        out[(target, signal)] = vals
    return out


def finite_predictions(k: int, total: int, cap: np.ndarray, eta: float,
                       max_h: int) -> dict[tuple[str, str], list[float]]:
    out = {}
    for target, signal in ARMS:
        mu = target_vector(target, cap, k, total)
        x = 0.0; cum = 0.0; vals = []
        for _ in range(max_h):
            ps = p_topk(x, k); pr = (k - ps) / (E - 1)
            cost = (expected_overflow(total, ps, int(cap[0]))
                    + (E - 1) * expected_overflow(total, pr, int(cap[1]))) / total
            cum += cost; vals.append(cum)
            if signal == "requested":
                ls, lr = total * ps, total * pr
            else:
                ls = clipped_mean(total, ps, int(cap[0]))
                lr = clipped_mean(total, pr, int(cap[1]))
            dx = eta * ((lr / (k * total) - mu[1])
                        - (ls / (k * total) - mu[0]))
            x += dx
        out[(target, signal)] = vals
    return out


if __name__ == "__main__":
    main()
