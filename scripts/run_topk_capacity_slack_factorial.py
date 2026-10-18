#!/usr/bin/env python3
"""Locked paired finite-batch factorial for the canonical Top-K feedback theorem."""
from __future__ import annotations

import csv
import argparse
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
PROTOCOL = ROOT / "docs/paper/topk_capacity_slack_factorial_protocol_2026-10-18.md"
OUT = ROOT / "results/topk_capacity_slack_factorial_2026-10-18"
LAWS = ("normal", "logistic", "gumbel")
EXPERT_COUNTS = (4, 8)
SHORTAGE_FRACTIONS = (Fraction(1, 4), Fraction(1, 2))
SCALES = (8, 32)
REPLICATES = 8
HORIZONS = (1, 2, 4, 8, 16, 32)
MASTER_SEED = 20261018


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def density_max(law: str) -> float:
    return {"normal": 1 / math.sqrt(2 * math.pi), "logistic": 0.25,
            "gumbel": 1 / math.e}[law]


def shortage_max(e: int, k: int) -> Fraction:
    return min(Fraction(k, e), Fraction(e-k, e*(e-1)))


def capacity_fractions(e: int, k: int, alpha: Fraction) -> tuple[Fraction, ...]:
    r = shortage_max(e, k) * alpha
    p = Fraction(k, e)
    return (p-r,) + (p+r/(e-1),) * (e-1)


def draw_affinity(rng: np.random.Generator, law: str, t: int, e: int) -> np.ndarray:
    shape = (t, e)
    if law == "normal":
        return rng.normal(size=shape)
    if law == "logistic":
        return rng.logistic(size=shape)
    if law == "gumbel":
        return rng.gumbel(size=shape)
    raise ValueError(law)


def route(aff: np.ndarray, q: np.ndarray, k: int) -> tuple[np.ndarray, int]:
    scores = aff - q[None, :]
    e = scores.shape[1]
    cutoff = np.partition(scores, e-k, axis=1)[:, e-k]
    above = scores > cutoff[:, None]
    on_boundary = scores == cutoff[:, None]
    needed = k - above.sum(axis=1)
    # Lower expert index wins exact boundary ties, matching the stable sort.
    boundary_rank = np.cumsum(on_boundary, axis=1)
    selected = above | (on_boundary & (boundary_rank <= needed[:, None]))
    if np.any(selected.sum(axis=1) != k):
        raise AssertionError("Top-K tie selection did not choose exactly K experts")
    counts = np.bincount(np.flatnonzero(selected) % e, minlength=e).astype(np.int64)
    ties = int(np.count_nonzero(on_boundary.sum(axis=1) > 1))
    return counts, ties


def update(q: np.ndarray, load: np.ndarray, k: int, t: int, eta: float) -> np.ndarray:
    nxt = q + eta * (load.astype(np.float64)/(k*t) - 1/len(q))
    return nxt - nxt.min()


def overflow(r: np.ndarray, c: np.ndarray) -> int:
    return int(np.maximum(r-c, 0).sum())


def topk_cdf_count(u: float, e: int, k: int) -> float:
    return sum(comb(e-1, j)*(1-u)**j*u**(e-1-j) for j in range(k))


def response(law: str, e: int, k: int, x: float) -> float:
    if x == 0:
        return k/e
    dist = {"normal": norm, "logistic": logistic, "gumbel": gumbel_r}[law]
    value, err = quad(
        lambda y: topk_cdf_count(float(dist.cdf(y+x)), e, k)*float(dist.pdf(y)),
        -np.inf, np.inf, epsabs=1e-10, epsrel=1e-10, limit=300)
    if not math.isfinite(value) or err > 1e-7:
        raise ArithmeticError(f"response quadrature failed: {law=} {e=} {k=} {x=} {err=}")
    return value


def population_gaps(law: str, e: int, k: int, r: Fraction, eta: float, hmax: int) -> list[float]:
    p = k/e
    x = 0.0
    gaps = []
    for _ in range(hmax):
        px = response(law, e, k, x)
        gaps.append(px-p)
        x += eta/(k*(e-1))*((e-1)*float(r)-(px-p))
    return gaps


def seed_for(law_i: int, e: int, k: int, t: int, rep: int, regime_i: int) -> int:
    return MASTER_SEED + law_i*10_000_000 + e*1_000_000 + k*100_000 + t*10 + rep*2 + regime_i


def main() -> None:
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--e", type=int, choices=EXPERT_COUNTS, required=True,
                        help="run one registered expert-count block; E=4 and E=8 are merged afterward")
    args = parser.parse_args()
    OUT = ROOT / "results" / "topk_capacity_slack_factorial_2026-10-18" / f"E{args.e}"
    OUT.mkdir(parents=True, exist_ok=True)
    raw: list[dict[str, object]] = []
    exact_ties = 0
    no_clip_controls = 0
    cell_keys = 0

    for law_i, law in enumerate(LAWS):
        for e in (args.e,):
            for k in range(1, e):
                lbound = density_max(law)*(e-1)*comb(e-2, k-1)
                eta = 0.8*k*(e-1)/lbound
                if eta > k*(e-1)/lbound + 1e-12:
                    raise AssertionError("gain violates theorem's sufficient bound")
                for alpha in SHORTAGE_FRACTIONS:
                    caps_frac = capacity_fractions(e, k, alpha)
                    r = shortage_max(e, k)*alpha
                    denom = math.lcm(*(x.denominator for x in caps_frac))
                    pred = population_gaps(law, e, k, r, eta, max(HORIZONS))
                    for scale_i, scale in enumerate(SCALES):
                        total = denom*scale
                        caps = np.asarray([int(x*total) for x in caps_frac], dtype=np.int64)
                        if int(caps.sum()) != k*total or int(caps.max()) >= total or int(caps.min()) <= 0:
                            raise AssertionError("invalid exact-total capacity profile")
                        for regime_i, regime in enumerate(("static", "fresh")):
                            for rep in range(REPLICATES):
                                seed = seed_for(law_i, e, k, total, rep, regime_i)
                                rng = np.random.default_rng(seed)
                                static_aff = draw_affinity(rng, law, total, e) if regime == "static" else None
                                q_req = np.zeros(e)
                                q_adm = np.zeros(e)
                                q_nc_req = np.zeros(e)
                                q_nc_adm = np.zeros(e)
                                cum_req = cum_adm = 0
                                hset = set(HORIZONS)
                                for step in range(1, max(HORIZONS)+1):
                                    aff = static_aff if static_aff is not None else draw_affinity(rng, law, total, e)
                                    rr, tr = route(aff, q_req, k)
                                    ra, ta = route(aff, q_adm, k)
                                    ar, aa = np.minimum(rr, caps), np.minimum(ra, caps)
                                    jr, ja = overflow(rr, caps), overflow(ra, caps)
                                    for req, adm, rej, cap in ((rr, ar, jr, caps), (ra, aa, ja, caps)):
                                        if int(req.sum()) != k*total or int(req.max()) > total:
                                            raise AssertionError("request mass/load invariant failed")
                                        if not np.array_equal(adm, np.minimum(req, cap)):
                                            raise AssertionError("admission identity failed")
                                        if rej != int((req-adm).sum()):
                                            raise AssertionError("overflow identity failed")
                                    if step == 1 and jr != ja:
                                        raise AssertionError("initial-state costs differ")
                                    cum_req += jr
                                    cum_adm += ja
                                    exact_ties += tr+ta
                                    q_req = update(q_req, rr, k, total, eta)
                                    q_adm = update(q_adm, aa, k, total, eta)
                                    # Full no-clipping trajectory negative control.
                                    if not np.array_equal(q_nc_req, q_nc_adm):
                                        raise AssertionError("no-clipping states diverged before routing")
                                    rn, tn = route(aff, q_nc_req, k)
                                    if overflow(rn, np.full(e, total)):
                                        raise AssertionError("no-clipping overflow is nonzero")
                                    q_nc_req = update(q_nc_req, rn, k, total, eta)
                                    # Since C_e=T>=R_e pathwise, A=R. The second
                                    # arm has exactly the same deterministic state map.
                                    q_nc_adm = update(q_nc_adm, rn, k, total, eta)
                                    if not np.array_equal(q_nc_req, q_nc_adm):
                                        raise AssertionError("no-clipping pressure trajectories differ")
                                    exact_ties += tn
                                    no_clip_controls += 1
                                    if step in hset:
                                        d = (cum_adm-cum_req)/total
                                        pop = sum(pred[:step])
                                        raw.append({
                                            "law": law, "E": e, "K": k,
                                            "shortage_fraction_of_max": str(alpha),
                                            "r": str(r), "T": total, "regime": regime,
                                            "replicate": rep, "seed": seed, "eta": eta,
                                            "H": step, "gap_A_minus_R_over_T": d,
                                            "population_cumulative_gap": pop,
                                            "abs_prediction_error": abs(d-pop),
                                            "population_long_run_average": (e-1)*float(r),
                                            "ties_this_step": tr+ta,
                                        })
                        cell_keys += 1
                print(f"completed law={law} E={e} K={k}", flush=True)

    raw_path = OUT/"paired_plants.csv"
    with raw_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw[0]))
        writer.writeheader()
        writer.writerows(raw)

    grouped: dict[tuple, list[dict[str, object]]] = defaultdict(list)
    for row in raw:
        key = (row["law"], row["E"], row["K"], row["shortage_fraction_of_max"], row["T"], row["regime"], row["H"])
        grouped[key].append(row)
    summary_cells = []
    for key, rows in sorted(grouped.items(), key=lambda kv: tuple(map(str, kv[0]))):
        vals = np.asarray([float(row["gap_A_minus_R_over_T"]) for row in rows])
        predicted = float(rows[0]["population_cumulative_gap"])
        se = float(vals.std(ddof=1)/math.sqrt(len(vals)))
        tc = float(student_t.ppf(0.975, len(vals)-1))
        h = int(key[-1])
        summary_cells.append({
            "law": key[0], "E": key[1], "K": key[2], "shortage_fraction_of_max": key[3],
            "T": key[4], "regime": key[5], "H": h, "n": len(rows),
            "mean_gap_A_minus_R_over_T": float(vals.mean()),
            "mean_horizon_average_gap": float(vals.mean()/h),
            "ci95_low": float(vals.mean()-tc*se), "ci95_high": float(vals.mean()+tc*se),
            "population_cumulative_gap": predicted,
            "population_average_gap": predicted/h,
            "abs_mean_error_to_population": abs(float(vals.mean())-predicted),
            "fraction_positive": float(np.mean(vals > 0)),
            "long_run_average_prediction_(E-1)r": float(rows[0]["population_long_run_average"]),
            "fraction_ci_contains_population": bool(vals.mean()-tc*se <= predicted <= vals.mean()+tc*se),
        })

    cells_path = OUT/"cells.csv"
    with cells_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_cells[0]))
        writer.writeheader()
        writer.writerows(summary_cells)

    summary = {
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha256(PROTOCOL),
        "script_sha256": sha256(Path(__file__)),
        "paired_rows": len(raw), "summary_cells": len(summary_cells),
        "parameter_profiles": cell_keys, "no_clipping_round_controls": no_clip_controls,
        "exact_score_ties": exact_ties, "all_registered_invariants_passed": True,
        "E_values": list(EXPERT_COUNTS), "all_K": True, "laws": list(LAWS),
        "shortage_fractions_of_max": [str(x) for x in SHORTAGE_FRACTIONS],
        "T_scales": list(SCALES), "regimes": ["static", "fresh"],
        "replicates": REPLICATES, "horizons": list(HORIZONS),
        "paired_plants_sha256": sha256(raw_path), "cells_sha256": sha256(cells_path),
        "cells": summary_cells,
    }
    summary_path = OUT/"summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({
        key: summary[key] for key in ("paired_rows", "summary_cells", "parameter_profiles",
                                       "no_clipping_round_controls", "exact_score_ties",
                                       "all_registered_invariants_passed", "paired_plants_sha256",
                                       "cells_sha256", "protocol_sha256", "script_sha256")
    }, indent=2))


if __name__ == "__main__":
    main()
