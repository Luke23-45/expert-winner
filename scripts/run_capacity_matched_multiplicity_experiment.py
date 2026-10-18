#!/usr/bin/env python3
"""Paired finite-batch validation of the existing multi-low target×signal theorem."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/capacity_matched_multiplicity_experiment_protocol_2026-10-18.md"
OUT = ROOT / "results/capacity_matched_multiplicity_2026-10-18"
E, K, P, R = 4, 2, Fraction(1, 2), Fraction(1, 16)
MS, TS, REPS = (1, 2, 3), (2304, 9216), 12
HORIZONS = (1, 2, 4, 8, 16, 32, 64)
ARMS = (("uniform", "requested"), ("uniform", "admitted"),
        ("capacity", "requested"), ("capacity", "admitted"))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def capacities(m: int, total: int) -> np.ndarray:
    n = E - m
    cl, ch = P - R, P + Fraction(m, n) * R
    vals = (cl,) * m + (ch,) * n
    assert all((v * total).denominator == 1 for v in vals)
    caps = np.asarray([int(v * total) for v in vals], dtype=np.int64)
    assert int(caps.sum()) == K * total and int(caps.max()) < total
    return caps


def route(a: np.ndarray, q: np.ndarray) -> tuple[np.ndarray, int]:
    scores = a - q[None, :]
    idx = np.argsort(-scores, axis=1, kind="stable")[:, :K]
    counts = np.bincount(idx.reshape(-1), minlength=E).astype(np.int64)
    cutoff = np.take_along_axis(scores, idx[:, -1:], axis=1)[:, 0]
    ties = int(np.count_nonzero((scores == cutoff[:, None]).sum(axis=1) > 1))
    return counts, ties


def pressure_update(q: np.ndarray, load: np.ndarray, mu: np.ndarray,
                    total: int, eta: float) -> np.ndarray:
    qn = q + eta * (load.astype(np.float64) / (K * total) - mu)
    return qn - qn.min()


def overflow(req: np.ndarray, cap: np.ndarray) -> int:
    return int(np.maximum(req - cap, 0).sum())


def high_inclusion(x: float, m: int) -> float:
    """Expected high selections / n in a Plackett–Luce Top-K draw."""
    n = E - m
    wh = math.exp(-x)
    # State probabilities after j sequential Plackett–Luce picks.
    states = {(0, 0): 1.0}
    for _ in range(K):
        nxt: dict[tuple[int, int], float] = defaultdict(float)
        for (lo, hi), prob in states.items():
            rem_lo, rem_hi = m - lo, n - hi
            denom = rem_lo + wh * rem_hi
            if rem_lo:
                nxt[(lo + 1, hi)] += prob * rem_lo / denom
            if rem_hi:
                nxt[(lo, hi + 1)] += prob * (wh * rem_hi) / denom
        states = nxt
    return math.fsum(prob * hi for (lo, hi), prob in states.items()) / n


def root_for(target: float, m: int) -> float:
    lo, hi = -16.0, 16.0
    # h decreases; root is bracketed by these endpoints for registered targets.
    assert high_inclusion(lo, m) > target > high_inclusion(hi, m)
    for _ in range(100):
        mid = (lo + hi) / 2
        if high_inclusion(mid, m) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def population_paths(m: int, eta: float, horizon: int) -> dict[tuple[str, str], list[float]]:
    n = E - m
    cl, ch = float(P - R), float(P + Fraction(m, n) * R)
    assert abs(high_inclusion(0.0, m) - float(P)) < 1e-14
    xc, xu = root_for(ch, m), root_for(cl, m)
    x = {("uniform", "requested"): 0.0,
         ("uniform", "admitted"): 0.0,
         ("capacity", "requested"): 0.0,
         ("capacity", "admitted"): 0.0}
    out = {arm: [] for arm in x}
    for _ in range(horizon):
        # Overflow depends on the request pressure, not the feedback signal.
        for target, signal in ARMS:
            xx = x[(target, signal)]
            h = high_inclusion(xx, m)
            out[(target, signal)].append(n * max(ch - h, 0.0))
        # Requested uniform feedback is zero at the symmetric initial state.
        x[("uniform", "requested")] = 0.0
        h = high_inclusion(x[("uniform", "admitted")], m)
        x[("uniform", "admitted")] += eta * (h - cl) / K
        h = high_inclusion(x[("capacity", "requested")], m)
        x[("capacity", "requested")] += eta * E / (m * K) * (h - ch)
        h = high_inclusion(x[("capacity", "admitted")], m)
        x[("capacity", "admitted")] += eta / K * (h - ch)
        assert xu >= x[("uniform", "admitted")] - 1e-10
        assert xc - 1e-10 <= x[("capacity", "requested")] <= 1e-10
        assert xc - 1e-10 <= x[("capacity", "admitted")] <= 1e-10
    for arm, vals in out.items():
        out[arm] = list(np.cumsum(vals))
    out[("none", "none")] = [j * float(m * R) for j in range(1, horizon + 1)]
    cap_req, cap_adm = out[("capacity", "requested")], out[("capacity", "admitted")]
    assert all(a <= b + 1e-12 for a, b in zip(cap_req, cap_adm))
    assert all(a < b for a, b in zip(cap_req[1:], cap_adm[1:]))
    assert all(abs(v - j * float(m * R)) < 1e-10
               for j, v in enumerate(out[("uniform", "requested")], start=1))
    return out


def no_clipping_control(seed: int, eta: float) -> None:
    rng = np.random.default_rng(seed)
    q = [np.zeros(E, dtype=np.float64) for _ in range(2)]
    mu = np.full(E, 1 / E)
    for _ in range(max(HORIZONS)):
        a = rng.gumbel(size=(512, E))
        r0, ties0 = route(a, q[0]); r1, ties1 = route(a, q[1])
        assert ties0 == ties1 == 0
        assert np.array_equal(r0, r1)
        q = [pressure_update(q[0], r0, mu, 512, eta),
             pressure_update(q[1], r1, mu, 512, eta)]
        assert np.array_equal(q[0], q[1])


def simulate(m: int, total: int, seed: int, eta: float,
             batches: list[np.ndarray], regime: str,
             predictions: dict[tuple[str, str], list[float]]) -> list[dict]:
    cap = capacities(m, total)
    qs = {arm: np.zeros(E, dtype=np.float64) for arm in ARMS}
    cumulative = {arm: 0 for arm in ARMS}
    q_none = np.zeros(E, dtype=np.float64)
    cumulative_none = 0
    rows: list[dict] = []
    ties = 0
    for step, aff in enumerate(batches, start=1):
        costs = {}
        for arm in ARMS:
            target, signal = arm
            req, tie_count = route(aff, qs[arm]); ties += tie_count
            assert req.sum() == K * total and req.max() <= total
            adm = np.minimum(req, cap)
            cost = overflow(req, cap)
            assert np.array_equal(adm, np.minimum(req, cap))
            assert cost == int((req - adm).sum())
            costs[arm] = cost
            cumulative[arm] += cost
            mu = (np.full(E, 1 / E) if target == "uniform"
                  else cap.astype(np.float64) / (K * total))
            load = req if signal == "requested" else adm
            qs[arm] = pressure_update(qs[arm], load, mu, total, eta)
        req0, tie_count = route(aff, q_none); ties += tie_count
        cumulative_none += overflow(req0, cap)
        if step == 1:
            assert len(set(costs.values())) == 1
        if step in HORIZONS:
            for arm in ARMS:
                rows.append({"m": m, "E": E, "K": K, "T": total,
                    "replicate": seed, "regime": regime, "H": step,
                    "target": arm[0], "signal": arm[1], "eta": eta,
                    "cumulative_overflow_per_T": cumulative[arm] / total,
                    "population_prediction": predictions[arm][step - 1]})
            rows.append({"m": m, "E": E, "K": K, "T": total,
                "replicate": seed, "regime": regime, "H": step,
                "target": "none", "signal": "none", "eta": 0.0,
                "cumulative_overflow_per_T": cumulative_none / total,
                "population_prediction": predictions[("none", "none")][step - 1]})
    assert ties == 0, f"registered Top-K tie in seed {seed}, m={m}, T={total}"
    return rows


def mean_ci(values: list[float]) -> tuple[float, float, float]:
    a = np.asarray(values, dtype=float)
    mean = float(a.mean())
    half = float(student_t.ppf(0.975, len(a) - 1) * a.std(ddof=1) / math.sqrt(len(a)))
    return mean, mean - half, mean + half


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raw_rows: list[dict] = []
    controls = 0
    for m in MS:
        for ti, total in enumerate(TS):
            cap = capacities(m, total)
            assert cap[:m].min() / total == float(P - R)
            eta = 0.5
            pop = population_paths(m, eta, max(HORIZONS))
            for rep in range(REPS):
                seed = 2026101800 + m * 100000 + ti * 10000 + rep
                rng = np.random.default_rng(seed)
                batches = [rng.gumbel(size=(total, E)) for _ in range(max(HORIZONS))]
                for regime in ("static", "fresh"):
                    use = [batches[0]] * max(HORIZONS) if regime == "static" else batches
                    raw_rows.extend(simulate(m, total, seed, eta, use, regime, pop))
                no_clipping_control(seed + 9000000, eta)
                controls += 1

    raw_path = OUT / "plants.csv"
    with raw_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw_rows[0]))
        writer.writeheader(); writer.writerows(raw_rows)

    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in raw_rows:
        key = tuple(row[k] for k in ("m", "T", "regime", "H", "target", "signal"))
        grouped[key].append(row)
    cells = []
    for key, rows in sorted(grouped.items()):
        vals = [r["cumulative_overflow_per_T"] for r in rows]
        mean, low, high = mean_ci(vals)
        cells.append({"m": key[0], "T": key[1], "regime": key[2], "H": key[3],
            "target": key[4], "signal": key[5], "n": len(vals), "mean": mean,
            "ci95_low": low, "ci95_high": high, "median": float(np.median(vals)),
            "population_prediction": rows[0]["population_prediction"],
            "population_abs_error": abs(mean - rows[0]["population_prediction"])})

    index = {(r["m"], r["T"], r["regime"], r["H"], r["replicate"],
              r["target"], r["signal"]): r["cumulative_overflow_per_T"] for r in raw_rows}
    contrast_defs = {
        "A_minus_R_uniform": [("uniform", "admitted", 1), ("uniform", "requested", -1)],
        "A_minus_R_capacity": [("capacity", "admitted", 1), ("capacity", "requested", -1)],
        "A_capacity_minus_none": [("capacity", "admitted", 1), ("none", "none", -1)],
        "target_by_signal_interaction": [("capacity", "admitted", 1), ("capacity", "requested", -1),
            ("uniform", "admitted", -1), ("uniform", "requested", 1)],
    }
    contrasts = []
    for m in MS:
        for total in TS:
            for regime in ("static", "fresh"):
                for h in HORIZONS:
                    for name, terms in contrast_defs.items():
                        diffs = []
                        for rep in range(REPS):
                            seed = 2026101800 + m * 100000 + TS.index(total) * 10000 + rep
                            diffs.append(sum(sign * index[(m, total, regime, h, seed, target, signal)]
                                             for target, signal, sign in terms))
                        mean, low, high = mean_ci(diffs)
                        contrasts.append({"m": m, "T": total, "regime": regime, "H": h,
                            "contrast": name, "mean": mean, "ci95_low": low,
                            "ci95_high": high, "fraction_positive": float(np.mean(np.asarray(diffs) > 0))})

    def write_csv(name: str, rows: list[dict]) -> None:
        with (OUT / name).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    write_csv("cells.csv", cells)
    write_csv("contrasts.csv", contrasts)
    summary = {"protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha(PROTOCOL), "script_sha256": sha(Path(__file__)),
        "plants_sha256": sha(raw_path), "cells_sha256": sha(OUT / "cells.csv"),
        "contrasts_sha256": sha(OUT / "contrasts.csv"), "rows": len(raw_rows),
        "controller_cells": len(cells), "paired_contrasts": len(contrasts),
        "m_values": MS, "T_values": TS, "replicates_per_cell": REPS,
        "horizons": HORIZONS, "no_clipping_controls": controls,
        "protocol_locked": True, "topk_ties": 0,
        "capacity_profiles": {str(m): capacities(m, TS[0]).tolist() for m in MS}}
    with (OUT / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True); f.write("\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
