#!/usr/bin/env python3
"""Paired finite-batch check of the long-run population Top-K theorem."""
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
PROTOCOL = ROOT / "docs/paper/topk_long_run_admitted_overflow_protocol_2026-10-17.md"
OUT = ROOT / "results/topk_long_run_admitted_overflow"
LAWS = ("normal", "logistic", "gumbel")
TS = (2304, 9216)
REPS = 12
HORIZONS = (1, 2, 4, 8, 16, 32, 64)
E = 4
R = Fraction(1, 48)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def density_max(law: str) -> float:
    return {"normal": 1.0 / math.sqrt(2.0 * math.pi),
            "logistic": 0.25, "gumbel": 1.0 / math.e}[law]


def cap_vector(k: int, total: int) -> np.ndarray:
    p = Fraction(k, E)
    values = (p - R,) + (p + R / (E - 1),) * (E - 1)
    assert all((x * total).denominator == 1 for x in values)
    c = np.asarray([int(x * total) for x in values], dtype=np.int64)
    assert int(c.sum()) == k * total and int(c.max()) < total
    return c


def sample(rng: np.random.Generator, law: str, total: int, e: int) -> np.ndarray:
    shape = (total, e)
    if law == "normal":
        return rng.normal(size=shape)
    if law == "logistic":
        return rng.logistic(size=shape)
    if law == "gumbel":
        return rng.gumbel(size=shape)
    raise ValueError(law)


def route(aff: np.ndarray, q: np.ndarray, k: int) -> tuple[np.ndarray, int]:
    scores = aff - q[None, :]
    order = np.argsort(-scores, axis=1, kind="stable")[:, :k]
    counts = np.bincount(order.reshape(-1), minlength=aff.shape[1]).astype(np.int64)
    boundary = np.take_along_axis(scores, order[:, k-1:k], axis=1)[:, 0]
    ties = int(np.count_nonzero((scores == boundary[:, None]).sum(axis=1) > 1))
    return counts, ties


def update(pressure: np.ndarray, load: np.ndarray, k: int, total: int, eta: float) -> np.ndarray:
    q = pressure + eta * (load.astype(np.float64) / (k * total) - 1.0 / E)
    return q - q.min()


def overflow(req: np.ndarray, cap: np.ndarray) -> int:
    return int(np.maximum(req - cap, 0).sum())


def g_value(u: float, k: int) -> float:
    return sum(comb(E - 1, j) * (1-u)**j * u**(E - 1-j) for j in range(k))


def population_probability(law: str, k: int, x: float) -> float:
    if x == 0.0:
        return k / E
    if law == "gumbel":
        def cdf(y: float) -> float:
            if y < -40: return 0.0
            if y > 40: return 1.0
            return math.exp(-math.exp(-y))
        def pdf(y: float) -> float:
            if y < -40 or y > 40: return 0.0
            return math.exp(-y - math.exp(-y))
    else:
        dist = {"normal": norm, "logistic": logistic}[law]
        cdf = lambda y: float(dist.cdf(y))
        pdf = lambda y: float(dist.pdf(y))
    value, err = quad(lambda y: g_value(cdf(y+x), k) * pdf(y),
                      -np.inf, np.inf, epsabs=1e-11, epsrel=1e-11, limit=300)
    if err > 1e-8:
        raise AssertionError(f"quadrature error {law=} {k=} {x=} {err=}")
    return value


def meanfield(law: str, k: int, eta: float, max_h: int) -> list[float]:
    p = k / E
    lbound = density_max(law) * (E-1) * comb(E-2, k-1)
    assert eta <= k * (E-1) / lbound + 1e-12
    x = 0.0
    gaps = []
    for _ in range(max_h):
        pk = population_probability(law, k, x)
        gaps.append(pk - p)
        x += eta / (k * (E-1)) * ((E-1)*float(R) - (pk-p))
    return gaps


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plants: list[dict] = []
    ties_total = 0
    no_clip_checks = 0
    for li, law in enumerate(LAWS):
        for k in (1, 2, 3):
            lbound = density_max(law) * (E-1) * comb(E-2, k-1)
            eta = 0.8 * k * (E-1) / lbound
            theoretical_gaps = meanfield(law, k, eta, max(HORIZONS))
            for ti, total in enumerate(TS):
                cap = cap_vector(k, total)
                cap_nc = np.full(E, total, dtype=np.int64)
                for rep in range(REPS):
                    seed = 20261017 + li*1_000_000 + k*10_000 + ti*1_000 + rep
                    aff = sample(np.random.default_rng(seed), law, total, E)
                    qR = np.zeros(E)
                    qA = np.zeros(E)
                    cumR = cumA = 0
                    horizon_lookup = set(HORIZONS)
                    for n in range(1, max(HORIZONS)+1):
                        rR, tieR = route(aff, qR, k)
                        rA, tieA = route(aff, qA, k)
                        aR = np.minimum(rR, cap)
                        aA = np.minimum(rA, cap)
                        jR, jA = overflow(rR, cap), overflow(rA, cap)
                        for rr, aa, jj in ((rR,aR,jR),(rA,aA,jA)):
                            assert int(rr.sum()) == k*total and int(rr.max()) <= total
                            assert np.array_equal(aa, np.minimum(rr, cap))
                            assert jj == int((rr-aa).sum())
                        if n == 1:
                            assert jR == jA
                        cumR += jR
                        cumA += jA
                        ties_total += tieR + tieA
                        qR = update(qR, rR, k, total, eta)
                        qA = update(qA, aA, k, total, eta)
                        if n in horizon_lookup:
                            pred = sum(theoretical_gaps[:n])
                            plants.append({
                                "law": law, "E": E, "K": k, "T": total,
                                "replicate": rep, "seed": seed, "eta": eta,
                                "H": n, "requested_overflow": cumR,
                                "admitted_overflow": cumA,
                                "gap_A_minus_R_over_T": str(Fraction(cumA-cumR, total)),
                                "population_cumulative_gap": pred,
                                "ties_R": tieR, "ties_A": tieA,
                            })
                    # Exact no-clipping one-step negative control.
                    r0, _ = route(aff, np.zeros(E), k)
                    qncR = update(np.zeros(E), r0, k, total, eta)
                    qncA = update(np.zeros(E), np.minimum(r0, cap_nc), k, total, eta)
                    assert np.array_equal(qncR, qncA)
                    rncR, _ = route(aff, qncR, k)
                    rncA, _ = route(aff, qncA, k)
                    assert np.array_equal(rncR, rncA)
                    assert overflow(r0, cap_nc) == overflow(rncR, cap_nc) == 0
                    no_clip_checks += 1

    plants_path = OUT / "plants.csv"
    with plants_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(plants[0]))
        w.writeheader()
        w.writerows(plants)

    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in plants:
        grouped[(row["law"], row["K"], row["T"], row["H"])].append(row)
    cells = []
    for key in sorted(grouped, key=lambda z: (LAWS.index(z[0]), z[1], z[2], z[3])):
        law,k,total,h = key
        cell=grouped[key]
        gaps=np.asarray([float(Fraction(x["gap_A_minus_R_over_T"])) for x in cell])
        pred=float(cell[0]["population_cumulative_gap"])
        mean=float(gaps.mean()); se=float(gaps.std(ddof=1)/math.sqrt(len(gaps)))
        tc=float(student_t.ppf(0.975,len(gaps)-1))
        cells.append({
            "law":law,"E":E,"K":k,"T":total,"H":h,"n":len(cell),
            "mean_cumulative_gap_over_T":mean,
            "mean_average_gap_per_token_batch":mean/h,
            "sample_sd":float(gaps.std(ddof=1)),"standard_error":se,
            "ci95_low":mean-tc*se,"ci95_high":mean+tc*se,
            "population_cumulative_gap":pred,
            "population_average_gap":pred/h,
            "abs_error_to_population":abs(mean-pred),
            "fraction_positive":float(np.mean(gaps>0)),
            "fraction_ci_contains_population":bool(mean-tc*se<=pred<=mean+tc*se),
        })

    summary={
        "protocol":PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256":sha256(PROTOCOL),"script_sha256":sha256(Path(__file__)),
        "rows":len(plants),"cells":len(cells),"no_clipping_controls":no_clip_checks,
        "total_exact_boundary_ties":ties_total,"all_invariants_passed":True,
        "laws":list(LAWS),"T_values":list(TS),"H_values":list(HORIZONS),
        "replicates_per_law_K_T":REPS,"cells_data":cells,
    }
    summary_path=OUT/"summary.json"
    summary_path.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "rows":len(plants),"cells":len(cells),"no_clipping_controls":no_clip_checks,
        "ties":ties_total,"positive_cell_means":sum(c["mean_cumulative_gap_over_T"]>0 for c in cells),
        "ci_population_coverage":sum(c["fraction_ci_contains_population"] for c in cells),
        "plants_sha256":sha256(plants_path),"summary_sha256":sha256(summary_path),
        "protocol_sha256":summary["protocol_sha256"],"script_sha256":summary["script_sha256"],
        "all_invariants_passed":True,
    },indent=2))

if __name__ == "__main__":
    main()
