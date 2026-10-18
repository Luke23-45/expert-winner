#!/usr/bin/env python3
"""Paired exact-grid experiment for the arbitrary-E Top-1 theorem."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/top1_e_expert_overflow_protocol_2026-10-17.md"
OUT = ROOT / "results/top1_e_expert_overflow"
GRID = 1 << 30
ES = (3, 4, 8, 16)
TS = (3360, 6720, 13440)
REPLICATES = 100
T_CRIT_95_DF99 = 1.9842


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cap_vector(e: int, t: int) -> np.ndarray:
    cap0 = Fraction(t, 2 * e)
    other = Fraction(t * (2 * e - 1), 2 * e * (e - 1))
    values = (cap0,) + (other,) * (e - 1)
    if any(v.denominator != 1 for v in values):
        raise AssertionError(f"capacity not integral: {e=} {t=}")
    out = np.asarray([int(v) for v in values], dtype=np.int64)
    if int(out.sum()) != t:
        raise AssertionError("capacity total is not exact")
    return out


def route(aff: np.ndarray, q_num: tuple[int, ...], q_den: int) -> tuple[np.ndarray, int]:
    scores = aff.astype(np.int64) * q_den
    if any(q_num):
        scores -= np.asarray(q_num, dtype=np.int64)[None, :] * GRID
    maxima = scores.max(axis=1)
    ties = int(np.count_nonzero((scores == maxima[:, None]).sum(axis=1) > 1))
    return np.bincount(scores.argmax(axis=1), minlength=aff.shape[1]).astype(np.int64), ties


def update(load: np.ndarray, e: int, t: int, eta: Fraction) -> tuple[tuple[int, ...], int]:
    raw = eta.numerator * (e * load - t)
    den = eta.denominator * e * t
    raw -= int(raw.min())
    return tuple(int(x) for x in raw), den


def overflow(r: np.ndarray, c: np.ndarray) -> int:
    return int(np.maximum(r - c, 0).sum())


def arm(aff: np.ndarray, c: np.ndarray, r0: np.ndarray, ties0: int, eta: Fraction, signal: str) -> dict:
    e, t = aff.shape[1], aff.shape[0]
    a0 = np.minimum(r0, c)
    if signal == "requested":
        qn, qd = update(r0, e, t, eta)
    elif signal == "admitted":
        qn, qd = update(a0, e, t, eta)
    elif signal == "none":
        qn, qd = (0,) * e, 1
    else:
        raise ValueError(signal)
    r1, ties1 = route(aff, qn, qd)
    a1 = np.minimum(r1, c)
    return {
        "r0": r0, "a0": a0, "j0": overflow(r0, c),
        "r1": r1, "a1": a1, "j1": overflow(r1, c),
        "ties0": ties0, "ties1": ties1, "qn": qn, "qd": qd,
    }


def theory(e: int, d: Fraction) -> float:
    x = float(d)
    return x - x**e / e


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    no_clip_checks = 0
    for e in ES:
        rfrac = Fraction(1, 2 * e)
        etas = (Fraction(e, 2), Fraction(e), Fraction(3 * e, 2))
        for ti, t in enumerate(TS):
            c = cap_vector(e, t)
            c_nc = np.full(e, t, dtype=np.int64)
            for rep in range(REPLICATES):
                seed = 20261021 + 100000 * e + 1000 * ti + rep
                rng = np.random.default_rng(seed)
                aff = rng.integers(0, GRID + 1, size=(t, e), dtype=np.int64)
                r0, ties0 = route(aff, (0,) * e, 1)
                if int(r0.sum()) != t:
                    raise AssertionError("step-zero Top-1 mass conservation failed")
                for eta in etas:
                    d = eta * rfrac
                    if not 0 < d < 1:
                        raise AssertionError("registered d is outside theorem range")
                    arms = {name: arm(aff, c, r0, ties0, eta, name)
                            for name in ("requested", "admitted", "none")}
                    for name, res in arms.items():
                        for step in (0, 1):
                            rr, aa = res[f"r{step}"], res[f"a{step}"]
                            if int(rr.sum()) != t:
                                raise AssertionError("Top-1 mass conservation failed")
                            if not np.array_equal(aa, np.minimum(rr, c)):
                                raise AssertionError("canonical clipping identity failed")
                            if int(res[f"j{step}"]) != int((rr - aa).sum()):
                                raise AssertionError("overflow accounting failed")
                    if len({int(arms[sig]["j0"]) for sig in arms}) != 1:
                        raise AssertionError("paired step-zero overflow differs")

                    ncr = arm(aff, c_nc, r0, ties0, eta, "requested")
                    nca = arm(aff, c_nc, r0, ties0, eta, "admitted")
                    if any((ncr["j0"], ncr["j1"], nca["j0"], nca["j1"])):
                        raise AssertionError("no-clipping control overflowed")
                    if not np.array_equal(ncr["r1"], nca["r1"]) or ncr["qn"] != nca["qn"]:
                        raise AssertionError("no-clipping R/A trajectories differ")
                    no_clip_checks += 1

                    totals = {name: int(arms[name]["j0"] + arms[name]["j1"])
                              for name in arms}
                    gap = (totals["admitted"] - totals["requested"]) / t
                    rows.append({
                        "E": e, "T": t, "T_index": ti, "replicate": rep,
                        "seed": seed, "d": str(d), "eta": str(eta),
                        "capacity_e1": int(c[0]),
                        "capacity_other": int(c[1]),
                        "r0_e1": int(r0[0]),
                        "requested_overflow_2step": totals["requested"],
                        "admitted_overflow_2step": totals["admitted"],
                        "no_feedback_overflow_2step": totals["none"],
                        "gap_normalized": gap,
                        "theory_limit": theory(e, d),
                        "abs_error_to_limit": abs(gap - theory(e, d)),
                        "ties_step0": ties0,
                        "ties_R_step1": int(arms["requested"]["ties1"]),
                        "ties_A_step1": int(arms["admitted"]["ties1"]),
                        "ties_none_step1": int(arms["none"]["ties1"]),
                    })

    csv_path = OUT / "plants.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["E"], row["T"], row["d"])].append(row)
    cells = []
    for (e, t, dstr), cell in sorted(grouped.items(), key=lambda x: (x[0][0], x[0][1], Fraction(x[0][2]))):
        gvals = np.asarray([x["gap_normalized"] for x in cell], dtype=np.float64)
        mean = float(gvals.mean())
        se = float(gvals.std(ddof=1) / math.sqrt(len(gvals)))
        d = Fraction(dstr)
        cells.append({
            "E": e, "T": t, "d": dstr, "n": len(cell),
            "mean_gap_A_minus_R_over_T": mean,
            "sample_sd": float(gvals.std(ddof=1)), "standard_error": se,
            "ci95_t_low": mean - T_CRIT_95_DF99 * se,
            "ci95_t_high": mean + T_CRIT_95_DF99 * se,
            "theory_limit": theory(e, d),
            "absolute_mean_error_to_limit": abs(mean - theory(e, d)),
            "fraction_positive_gap": float(np.mean(gvals > 0)),
            "fraction_equal_gap": float(np.mean(gvals == 0)),
            "mean_requested_overflow_per_T": float(np.mean([x["requested_overflow_2step"] for x in cell]) / t),
            "mean_admitted_overflow_per_T": float(np.mean([x["admitted_overflow_2step"] for x in cell]) / t),
            "mean_no_feedback_overflow_per_T": float(np.mean([x["no_feedback_overflow_2step"] for x in cell]) / t),
            "exact_tie_tokens": int(sum(x[k] for x in cell for k in ("ties_step0", "ties_R_step1", "ties_A_step1", "ties_none_step1"))),
        })

    summary = {
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha256(PROTOCOL),
        "script_sha256": sha256(Path(__file__)),
        "affinity_grid_max": GRID,
        "replicates_per_E_T": REPLICATES,
        "rows": len(rows), "no_clipping_checks": no_clip_checks,
        "all_invariants_passed": True,
        "confidence_interval": "mean +/- t_(0.975,99) * standard error; t critical rounded to 1.9842",
        "cells": cells,
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "rows": len(rows), "summary": str(summary_path),
        "summary_sha256": sha256(summary_path), "plants_sha256": sha256(csv_path),
        "protocol_sha256": summary["protocol_sha256"],
        "script_sha256": summary["script_sha256"],
        "no_clipping_checks": no_clip_checks, "all_invariants_passed": True,
    }, indent=2))


if __name__ == "__main__":
    main()
