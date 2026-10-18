#!/usr/bin/env python3
"""Run the preregistered parameter sweep for the two-step MoE theorem."""

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
PROTOCOL = ROOT / "docs/paper/heterogeneous_capacity_family_protocol_2026-10-17.md"
OUT = ROOT / "results/heterogeneous_family_sweep"
GRID = 1 << 30
TS = (120, 240, 480, 960, 1920)
RS = (Fraction(1, 12), Fraction(1, 6), Fraction(1, 4))
ETAS = (Fraction(1, 2), Fraction(1), Fraction(2), Fraction(3))
REPLICATES = 200
T_CRIT_95_DF199 = 1.9720


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def capacities(t: int, r: Fraction, s: Fraction) -> np.ndarray:
    fractions = (Fraction(1, 3) - r, Fraction(1, 3) + s, Fraction(1, 3) + r - s)
    values = tuple(x * t for x in fractions)
    if any(x.denominator != 1 for x in values):
        raise AssertionError(f"nonintegral capacity: {t=} {r=} {s=}")
    out = np.asarray([int(x) for x in values], dtype=np.int64)
    if int(out.sum()) != t:
        raise AssertionError("registered capacities do not have exact total")
    return out


def route(aff: np.ndarray, q_num: tuple[int, ...], q_den: int) -> tuple[np.ndarray, int]:
    scores = aff.astype(np.int64) * q_den
    if any(q_num):
        scores -= np.asarray(q_num, dtype=np.int64)[None, :] * GRID
    max_score = scores.max(axis=1)
    ties = int(np.count_nonzero((scores == max_score[:, None]).sum(axis=1) > 1))
    return np.bincount(scores.argmax(axis=1), minlength=3).astype(np.int64), ties


def pressure(load: np.ndarray, t: int, eta: Fraction) -> tuple[tuple[int, ...], int]:
    raw = eta.numerator * (3 * load - t)
    den = 3 * eta.denominator * t
    raw -= int(raw.min())
    return tuple(int(x) for x in raw), den


def overflow(r: np.ndarray, c: np.ndarray) -> int:
    return int(np.maximum(r - c, 0).sum())


def arm(aff: np.ndarray, t: int, c: np.ndarray, r0: np.ndarray, ties0: int, eta: Fraction, kind: str) -> dict:
    a0 = np.minimum(r0, c)
    if kind == "requested":
        qn, qd = pressure(r0, t, eta)
    elif kind == "admitted":
        qn, qd = pressure(a0, t, eta)
    elif kind == "none":
        qn, qd = (0, 0, 0), 1
    else:
        raise ValueError(kind)
    r1, ties1 = route(aff, qn, qd)
    a1 = np.minimum(r1, c)
    return {
        "r0": r0.tolist(), "a0": a0.tolist(), "j0": overflow(r0, c),
        "r1": r1.tolist(), "a1": a1.tolist(), "j1": overflow(r1, c),
        "ties0": ties0, "ties1": ties1, "qn": qn, "qd": qd,
    }


def target(eta: Fraction, r: Fraction) -> float:
    d = float(eta * r)
    return d - d**3 / 3


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    no_clip_checks = 0
    for t in TS:
        for rep in range(REPLICATES):
            seed = 20261020 + 100000 * t + rep
            rng = np.random.default_rng(seed)
            aff = rng.integers(0, GRID + 1, size=(t, 3), dtype=np.int64)
            r0, ties0 = route(aff, (0, 0, 0), 1)
            if int(r0.sum()) != t:
                raise AssertionError("step-zero Top-1 mass conservation failed")

            for rfrac in RS:
                for sfrac in (Fraction(0), rfrac / 2, rfrac):
                    c = capacities(t, rfrac, sfrac)
                    for eta in ETAS:
                        if not 0 < eta * rfrac < 1:
                            raise AssertionError("registered theorem condition failed")
                        arms = {name: arm(aff, t, c, r0, ties0, eta, name)
                                for name in ("requested", "admitted", "none")}
                        for name, result in arms.items():
                            for step in (0, 1):
                                rs = np.asarray(result[f"r{step}"], dtype=np.int64)
                                aa = np.asarray(result[f"a{step}"], dtype=np.int64)
                                if int(rs.sum()) != t:
                                    raise AssertionError("Top-1 mass conservation failed")
                                if not np.array_equal(aa, np.minimum(rs, c)):
                                    raise AssertionError("canonical clipping identity failed")
                                if int(result[f"j{step}"]) != int((rs - aa).sum()):
                                    raise AssertionError("overflow accounting failed")
                        if len({int(arms[x]["j0"]) for x in arms}) != 1:
                            raise AssertionError("paired initial overflow differs")

                        total_r = int(arms["requested"]["j0"]) + int(arms["requested"]["j1"])
                        total_a = int(arms["admitted"]["j0"]) + int(arms["admitted"]["j1"])
                        total_n = int(arms["none"]["j0"]) + int(arms["none"]["j1"])
                        gap = (total_a - total_r) / t
                        g = target(eta, rfrac)
                        rows.append({
                            "T": t, "replicate": rep, "seed": seed,
                            "r": str(rfrac), "s": str(sfrac), "eta": str(eta),
                            "capacity_e0": int(c[0]), "capacity_e1": int(c[1]), "capacity_e2": int(c[2]),
                            "r0_e0": int(r0[0]), "r0_e1": int(r0[1]), "r0_e2": int(r0[2]),
                            "requested_overflow_2step": total_r,
                            "admitted_overflow_2step": total_a,
                            "no_feedback_overflow_2step": total_n,
                            "gap_normalized": gap, "theory_limit": g,
                            "abs_error_to_limit": abs(gap - g),
                            "ties_step0": ties0,
                            "ties_R_step1": int(arms["requested"]["ties1"]),
                            "ties_A_step1": int(arms["admitted"]["ties1"]),
                            "ties_none_step1": int(arms["none"]["ties1"]),
                        })

            for eta in ETAS:
                c_nc = np.full(3, t, dtype=np.int64)
                ncr = arm(aff, t, c_nc, r0, ties0, eta, "requested")
                nca = arm(aff, t, c_nc, r0, ties0, eta, "admitted")
                if any((ncr["j0"], ncr["j1"], nca["j0"], nca["j1"])):
                    raise AssertionError("no-clipping control overflowed")
                if ncr["r1"] != nca["r1"] or ncr["qn"] != nca["qn"]:
                    raise AssertionError("no-clipping R/A paths differ")
                no_clip_checks += 1

    csv_path = OUT / "plants.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["T"], row["r"], row["s"], row["eta"])].append(row)
    cells = []
    for (t, rtxt, stxt, etxt), cell in sorted(groups.items(), key=lambda x: (x[0][0], Fraction(x[0][1]), Fraction(x[0][2]), Fraction(x[0][3]))):
        gaps = np.asarray([x["gap_normalized"] for x in cell], dtype=np.float64)
        eta, rfrac = Fraction(etxt), Fraction(rtxt)
        mean = float(gaps.mean())
        se = float(gaps.std(ddof=1) / math.sqrt(len(gaps)))
        cells.append({
            "T": t, "r": rtxt, "s": stxt, "eta": etxt,
            "n": len(cell), "mean_gap_A_minus_R_over_T": mean,
            "sample_sd": float(gaps.std(ddof=1)), "standard_error": se,
            "ci95_t_low": mean - T_CRIT_95_DF199 * se,
            "ci95_t_high": mean + T_CRIT_95_DF199 * se,
            "theory_limit": target(eta, rfrac),
            "absolute_mean_error_to_limit": abs(mean - target(eta, rfrac)),
            "fraction_positive_gap": float(np.mean(gaps > 0)),
            "fraction_equal_gap": float(np.mean(gaps == 0)),
            "mean_requested_overflow_per_T": float(np.mean([x["requested_overflow_2step"] for x in cell]) / t),
            "mean_admitted_overflow_per_T": float(np.mean([x["admitted_overflow_2step"] for x in cell]) / t),
            "mean_no_feedback_overflow_per_T": float(np.mean([x["no_feedback_overflow_2step"] for x in cell]) / t),
            "total_exact_tie_tokens": int(sum(x[k] for x in cell for k in ("ties_step0", "ties_R_step1", "ties_A_step1", "ties_none_step1"))),
        })

    summary = {
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha256(PROTOCOL),
        "script_sha256": sha256(Path(__file__)),
        "affinity_grid_max": GRID,
        "replicates_per_T": REPLICATES,
        "rows": len(rows),
        "no_clipping_checks": no_clip_checks,
        "all_invariants_passed": True,
        "confidence_interval": "mean +/- t_(0.975,199) * standard error; t critical rounded to 1.9720",
        "cells": cells,
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "rows": len(rows), "summary": str(summary_path),
        "summary_sha256": sha256(summary_path), "plants_sha256": sha256(csv_path),
        "protocol_sha256": summary["protocol_sha256"], "script_sha256": summary["script_sha256"],
        "no_clipping_checks": no_clip_checks, "all_invariants_passed": True,
    }, indent=2))


if __name__ == "__main__":
    main()
