#!/usr/bin/env python3
"""Paired exact-grid experiment for the arbitrary-E,K Top-K theorem."""

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


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/topk_e_expert_overflow_protocol_2026-10-17.md"
OUT = ROOT / "results/topk_e_expert_overflow"
GRID = 1 << 30
ES = (3, 4, 8)
TS = (3360, 6720, 13440)
DS = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))
REPLICATES = 50
T_CRIT_95_DF49 = 2.0096


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cap_vector(e: int, k: int, t: int) -> np.ndarray:
    m = min(k, e - k)
    r = Fraction(m, 2 * e)
    sigma = r / (e - 1)
    vals = (Fraction(k, e) - r,) + (Fraction(k, e) + sigma,) * (e - 1)
    if any((v * t).denominator != 1 for v in vals):
        raise AssertionError(f"nonintegral capacity: {e=} {k=} {t=}")
    out = np.asarray([int(v * t) for v in vals], dtype=np.int64)
    if int(out.sum()) != k * t:
        raise AssertionError("capacity total is not K*T")
    if int(out.min()) <= 0 or int(out.max()) > t:
        raise AssertionError("registered per-expert capacity outside (0,T]")
    return out


def route(aff: np.ndarray, q_num: tuple[int, ...], q_den: int, k: int) -> tuple[np.ndarray, int]:
    e = aff.shape[1]
    scores = aff.astype(np.int64) * q_den
    if any(q_num):
        scores -= np.asarray(q_num, dtype=np.int64)[None, :] * GRID
    order = np.argsort(-scores, axis=1, kind="stable")[:, :k]
    counts = np.bincount(order.reshape(-1), minlength=e).astype(np.int64)
    boundary = np.take_along_axis(scores, order[:, k - 1:k], axis=1)[:, 0]
    ties = int(np.count_nonzero((scores == boundary[:, None]).sum(axis=1) > 1))
    return counts, ties


def update(load: np.ndarray, e: int, k: int, t: int, eta: Fraction) -> tuple[tuple[int, ...], int]:
    raw = eta.numerator * (e * load - k * t)
    den = eta.denominator * e * k * t
    raw -= int(raw.min())
    return tuple(int(x) for x in raw), den


def overflow(r: np.ndarray, c: np.ndarray) -> int:
    return int(np.maximum(r - c, 0).sum())


def arm(aff: np.ndarray, c: np.ndarray, r0: np.ndarray, ties0: int,
        e: int, k: int, eta: Fraction, signal: str) -> dict:
    t = aff.shape[0]
    a0 = np.minimum(r0, c)
    if signal == "requested":
        qn, qd = update(r0, e, k, t, eta)
    elif signal == "admitted":
        qn, qd = update(a0, e, k, t, eta)
    elif signal == "none":
        qn, qd = (0,) * e, 1
    else:
        raise ValueError(signal)
    r1, ties1 = route(aff, qn, qd, k)
    a1 = np.minimum(r1, c)
    return {"r0": r0, "a0": a0, "j0": overflow(r0, c),
            "r1": r1, "a1": a1, "j1": overflow(r1, c),
            "ties0": ties0, "ties1": ties1, "qn": qn, "qd": qd}


def phi(e: int, k: int, d: Fraction) -> Fraction:
    """Exact polynomial integral in the theorem, evaluated with Fractions."""
    out = d
    for j in range(k):
        for m in range(j + 1):
            exponent_plus_one = e - j + m
            term = Fraction((-1) ** m * comb(e - 1, j) * comb(j, m), exponent_plus_one)
            out += term * (1 - d ** exponent_plus_one)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for e in ES:
        for k in range(1, e):
            for d in DS:
                gap = phi(e, k, d) - Fraction(k, e)
                if gap <= 0:
                    raise AssertionError("population theorem gap must be positive")
                if k == 1 and gap != d - d ** e / e:
                    raise AssertionError("Top-1 specialization does not match prior theorem")
    rows: list[dict] = []
    no_clip_checks = 0
    for e in ES:
        for k in range(1, e):
            m = min(k, e - k)
            rfrac = Fraction(m, 2 * e)
            for ti, t in enumerate(TS):
                c = cap_vector(e, k, t)
                c_nc = np.full(e, t, dtype=np.int64)
                for rep in range(REPLICATES):
                    seed = 20261031 + 100000 * e + 1000 * k + 10 * ti + rep
                    rng = np.random.default_rng(seed)
                    aff = rng.integers(0, GRID + 1, size=(t, e), dtype=np.int64)
                    r0, ties0 = route(aff, (0,) * e, 1, k)
                    if int(r0.sum()) != k * t or int(r0.max()) > t:
                        raise AssertionError("step-zero Top-K mass/load invariant failed")

                    for d in DS:
                        eta = d * k / rfrac
                        if eta * rfrac / k != d:
                            raise AssertionError("registered pressure displacement mismatch")
                        arms = {name: arm(aff, c, r0, ties0, e, k, eta, name)
                                for name in ("requested", "admitted", "none")}
                        for name, res in arms.items():
                            for step in (0, 1):
                                rr, aa = res[f"r{step}"], res[f"a{step}"]
                                if int(rr.sum()) != k * t or int(rr.max()) > t:
                                    raise AssertionError("Top-K mass/load invariant failed")
                                if not np.array_equal(aa, np.minimum(rr, c)):
                                    raise AssertionError("canonical clipping identity failed")
                                if int(res[f"j{step}"]) != int((rr - aa).sum()):
                                    raise AssertionError("overflow accounting failed")
                        if len({int(arms[name]["j0"]) for name in arms}) != 1:
                            raise AssertionError("paired initial overflow differs")

                        ncr = arm(aff, c_nc, r0, ties0, e, k, eta, "requested")
                        nca = arm(aff, c_nc, r0, ties0, e, k, eta, "admitted")
                        if any((ncr["j0"], ncr["j1"], nca["j0"], nca["j1"])):
                            raise AssertionError("no-clipping control overflowed")
                        if ncr["qn"] != nca["qn"] or not np.array_equal(ncr["r1"], nca["r1"]):
                            raise AssertionError("no-clipping R/A trajectories differ")
                        no_clip_checks += 1

                        totals = {name: int(res["j0"] + res["j1"])
                                  for name, res in arms.items()}
                        exact_limit = phi(e, k, d) - Fraction(k, e)
                        gap = Fraction(totals["admitted"] - totals["requested"], t)
                        rows.append({
                            "E": e, "K": k, "T": t, "T_index": ti, "replicate": rep,
                            "seed": seed, "d": str(d), "eta": str(eta),
                            "capacity_e1": int(c[0]), "capacity_other": int(c[1]),
                            "r0_e1": int(r0[0]),
                            "requested_overflow_2step": totals["requested"],
                            "admitted_overflow_2step": totals["admitted"],
                            "no_feedback_overflow_2step": totals["none"],
                            "gap_normalized": str(gap), "theory_limit": str(exact_limit),
                            "abs_error_to_limit": abs(float(gap - exact_limit)),
                            "ties_step0": ties0,
                            "ties_R_step1": arms["requested"]["ties1"],
                            "ties_A_step1": arms["admitted"]["ties1"],
                            "ties_none_step1": arms["none"]["ties1"],
                        })

    csv_path = OUT / "plants.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["E"], row["K"], row["T"], row["d"])].append(row)
    cells = []
    for (e, k, t, dstr), cell in sorted(grouped.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], Fraction(x[0][3]))):
        gaps = np.asarray([float(Fraction(x["gap_normalized"])) for x in cell], dtype=np.float64)
        limit = float(Fraction(cell[0]["theory_limit"]))
        mean = float(gaps.mean())
        se = float(gaps.std(ddof=1) / math.sqrt(len(gaps)))
        cells.append({
            "E": e, "K": k, "T": t, "d": dstr, "n": len(cell),
            "mean_gap_A_minus_R_over_T": mean, "sample_sd": float(gaps.std(ddof=1)),
            "standard_error": se, "ci95_t_low": mean - T_CRIT_95_DF49 * se,
            "ci95_t_high": mean + T_CRIT_95_DF49 * se, "theory_limit": limit,
            "absolute_mean_error_to_limit": abs(mean - limit),
            "fraction_positive_gap": float(np.mean(gaps > 0)),
            "fraction_equal_gap": float(np.mean(gaps == 0)),
            "mean_requested_overflow_per_T": float(np.mean([x["requested_overflow_2step"] for x in cell]) / t),
            "mean_admitted_overflow_per_T": float(np.mean([x["admitted_overflow_2step"] for x in cell]) / t),
            "mean_no_feedback_overflow_per_T": float(np.mean([x["no_feedback_overflow_2step"] for x in cell]) / t),
            "exact_tie_tokens": int(sum(x[z] for x in cell for z in ("ties_step0", "ties_R_step1", "ties_A_step1", "ties_none_step1"))),
        })

    summary = {
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha256(PROTOCOL), "script_sha256": sha256(Path(__file__)),
        "affinity_grid_max": GRID, "replicates_per_E_K_T": REPLICATES,
        "rows": len(rows), "cells": cells, "no_clipping_checks": no_clip_checks,
        "all_invariants_passed": True,
        "confidence_interval": "mean +/- t_(0.975,49) * standard error; t critical rounded to 2.0096",
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "rows": len(rows), "cells": len(cells), "summary_sha256": sha256(summary_path),
        "plants_sha256": sha256(csv_path), "protocol_sha256": summary["protocol_sha256"],
        "script_sha256": summary["script_sha256"], "no_clipping_checks": no_clip_checks,
        "all_invariants_passed": True,
    }, indent=2))


if __name__ == "__main__":
    main()
