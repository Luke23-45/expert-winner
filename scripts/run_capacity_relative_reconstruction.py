#!/usr/bin/env python3
"""Paired synthetic audit of admitted-only request reconstruction and targets."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/capacity_relative_reconstruction_experiment_protocol_2026-10-17.md"
OUT = ROOT / "results/capacity_relative_reconstruction"
E, K = 4, 1
TS = (2304, 9216)
REPS = 50
H = 8
ETA = 1.0
ARMS = ("R_uniform", "A_uniform", "R_capacity", "A_capacity_naive", "A_capacity_reconstructed")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def capacities(t: int, no_clip: bool = False) -> np.ndarray:
    if no_clip:
        return np.full(E, t, dtype=np.int64)
    c = np.asarray([t // 8, 7 * t // 24, 7 * t // 24, 7 * t // 24], dtype=np.int64)
    if int(c.sum()) != K * t:
        raise AssertionError("capacity vector must have exact total K*T")
    return c


def route(aff: np.ndarray, q: np.ndarray) -> tuple[np.ndarray, int]:
    scores = aff - q[None, :]
    order = np.argsort(-scores, axis=1, kind="stable")[:, :K]
    counts = np.bincount(order.reshape(-1), minlength=E).astype(np.int64)
    boundary = np.take_along_axis(scores, order[:, K - 1:K], axis=1)[:, 0]
    ties = int(np.count_nonzero((scores == boundary[:, None]).sum(axis=1) > 1))
    return counts, ties


def p0(x: np.ndarray) -> np.ndarray:
    return x - x.mean()


def reconstruct(a: np.ndarray, c: np.ndarray, t: int) -> tuple[np.ndarray | None, int]:
    saturated = np.flatnonzero(a >= c)
    if len(saturated) == 0:
        return a.copy(), 0
    if len(saturated) > 1:
        return None, len(saturated)
    s = int(saturated[0])
    r_hat = a.copy()
    r_hat[s] = K * t - int(a.sum() - a[s])
    if r_hat[s] < c[s] or int(r_hat.sum()) != K * t:
        raise AssertionError("singleton-saturation reconstruction invalid")
    if not np.array_equal(np.minimum(r_hat, c), a):
        raise AssertionError("reconstructed requests do not map back to admitted counts")
    return r_hat, 1


def update(q: np.ndarray, load: np.ndarray, c: np.ndarray, t: int, mode: str) -> np.ndarray:
    mu = np.full(E, 1.0 / E, dtype=np.float64)
    if mode == "uniform":
        feedback = load.astype(np.float64) / (K * t) - mu
    elif mode == "capacity":
        feedback = p0((load.astype(np.float64) - c.astype(np.float64)) / (K * t))
    else:
        raise ValueError(mode)
    out = q + ETA * feedback
    return out - out.min()


def population_reference(h: int) -> dict[str, list[float]]:
    short_cap = 1.0 / 8.0

    def qshort(x: float) -> float:
        return 1.0 / (1.0 + 3.0 * math.exp(x))

    states = {name: 0.0 for name in ARMS}
    costs = {name: [] for name in ARMS}
    for _ in range(h):
        for name, x in states.items():
            costs[name].append(max(qshort(x) - short_cap, 0.0))
        # x = q_short - q_rival. Exact Gumbel Top-1 population recurrences.
        q_r = states["R_uniform"]
        states["R_uniform"] = q_r  # requested uniform target is balanced at q=0.
        q_a = states["A_uniform"]
        q_probability = qshort(q_a)
        states["A_uniform"] = q_a + ETA * (
            -1.0 / 8.0 + (q_probability - 1.0 / 4.0) / 3.0
        )
        q_c = states["R_capacity"]
        states["R_capacity"] = q_c + ETA * (E / (K * (E - 1))) * (qshort(q_c) - short_cap)
        q_an = states["A_capacity_naive"]
        states["A_capacity_naive"] = q_an + ETA * (1.0 / (K * (E - 1))) * (qshort(q_an) - short_cap)
        states["A_capacity_reconstructed"] = states["R_capacity"]
    return costs


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    plant_rows: list[dict] = []
    ties = 0
    recovery_failures = 0
    exact_parity_failures = 0
    no_clip_checks = 0
    for ti, t in enumerate(TS):
        c = capacities(t)
        for rep in range(REPS):
            seed = 20261017 + 8_000_000 + ti * 100_000 + rep
            rng = np.random.default_rng(seed)
            aff = rng.gumbel(size=(t, E))
            qs = {name: np.zeros(E, dtype=np.float64) for name in ARMS}
            cumulative = {name: 0 for name in ARMS}
            recovered_all_steps = True
            exact_path_match = True
            for step in range(H):
                current: dict[str, tuple[np.ndarray, np.ndarray, int, int]] = {}
                for name in ARMS:
                    r, tie = route(aff, qs[name])
                    a = np.minimum(r, c)
                    j = int((r - a).sum())
                    ties += tie
                    if int(r.sum()) != K * t or int(r.max()) > t:
                        raise AssertionError("Top-1 mass/load invariant failed")
                    if not np.array_equal(a, np.minimum(r, c)) or j != int(np.maximum(r-c, 0).sum()):
                        raise AssertionError("canonical admission/overflow invariant failed")
                    current[name] = (r, a, j, tie)

                r_a, a_a, _, _ = current["A_capacity_reconstructed"]
                r_hat, sat_count = reconstruct(a_a, c, t)
                recovered = r_hat is not None
                if not recovered:
                    recovery_failures += 1
                    recovered_all_steps = False

                # All feedback arms update from their own observation.
                for name in ARMS:
                    r, a, _, _ = current[name]
                    if name == "R_uniform":
                        qs[name] = update(qs[name], r, c, t, "uniform")
                    elif name == "A_uniform":
                        qs[name] = update(qs[name], a, c, t, "uniform")
                    elif name == "R_capacity":
                        qs[name] = update(qs[name], r, c, t, "capacity")
                    elif name == "A_capacity_naive":
                        qs[name] = update(qs[name], a, c, t, "capacity")
                    elif recovered:
                        qs[name] = update(qs[name], r_hat, c, t, "capacity")
                    # Registered fallback on a multi-saturated fiber: freeze.

                if not recovered:
                    exact_path_match = False
                elif not np.array_equal(current["R_capacity"][0], r_hat):
                    # R_hat here comes from the reconstructed arm, while its
                    # own trajectory must agree with the requested arm.
                    exact_path_match = False
                if recovered and not np.array_equal(qs["R_capacity"], qs["A_capacity_reconstructed"]):
                    exact_path_match = False

                for name in ARMS:
                    r, a, j, tie = current[name]
                    cumulative[name] += j
                    rows.append({
                        "T": t, "replicate": rep, "seed": seed, "step": step,
                        "arm": name, "requested_overflow": j,
                        "cumulative_overflow": cumulative[name],
                        "cumulative_overflow_per_token": cumulative[name] / t,
                        "saturated_experts": int(np.count_nonzero(a >= c)),
                        "reconstruction_available": recovered,
                        "reconstructed_request_matches_arm_request": bool(recovered and np.array_equal(r_hat, r)),
                        "route_ties": tie,
                    })
            plant_rows.append({
                "T": t, "replicate": rep, "seed": seed,
                "reconstruction_available_all_steps": recovered_all_steps,
                "reconstruction_fallback_steps": sum(
                    1 for x in rows[-H * len(ARMS):]
                    if x["arm"] == "A_capacity_reconstructed" and not x["reconstruction_available"]
                ),
                "exact_capacity_feedback_path_match": exact_path_match,
                **{f"cumulative_overflow_{name}": cumulative[name] for name in ARMS},
            })

            # Pairwise no-clipping identity for uniform, capacity-relative,
            # and reconstruction feedback on the same matrix.
            c_nc = capacities(t, no_clip=True)
            r0, _ = route(aff, np.zeros(E))
            a0_nc = np.minimum(r0, c_nc)
            assert np.array_equal(r0, a0_nc)
            for mode in ("uniform", "capacity"):
                q_r = update(np.zeros(E), r0, c_nc, t, mode)
                q_a = update(np.zeros(E), a0_nc, c_nc, t, mode)
                assert np.array_equal(q_r, q_a)
            no_clip_checks += 1

    steps_path = OUT / "steps.csv"
    with steps_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    plants_path = OUT / "plants.csv"
    with plants_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(plant_rows[0]))
        writer.writeheader(); writer.writerows(plant_rows)

    grouped: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for row in plant_rows:
        for arm in ARMS:
            grouped[(row["T"], arm)].append({
                "T": row["T"], "replicate": row["replicate"], "seed": row["seed"],
                "arm": arm, "cum": row[f"cumulative_overflow_{arm}"],
            })
    pop = population_reference(H)
    cells = []
    for (t, arm), cell in sorted(grouped.items()):
        vals = np.asarray([x["cum"] / t for x in cell], dtype=np.float64)
        mean = float(vals.mean()); se = float(vals.std(ddof=1) / math.sqrt(len(vals)))
        tc = float(student_t.ppf(0.975, len(vals) - 1))
        cells.append({
            "T": t, "arm": arm, "n": len(cell),
            "mean_cumulative_overflow_per_token": mean,
            "sample_sd": float(vals.std(ddof=1)), "standard_error": se,
            "ci95_low": mean-tc*se, "ci95_high": mean+tc*se,
            "population_cumulative_reference": float(sum(pop[arm])),
            "mean_per_step_overflow": mean/H,
            "positive_seed_count": int(np.count_nonzero(vals > 0)),
        })
    summary = {
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha256(PROTOCOL), "script_sha256": sha256(Path(__file__)),
        "E": E, "K": K, "T_values": list(TS), "replicates_per_T": REPS,
        "H": H, "eta": ETA, "rows": len(rows), "plant_rows": len(plant_rows),
        "arms": list(ARMS), "total_exact_boundary_ties": ties,
        "reconstruction_fallback_steps": recovery_failures,
        "plants_with_exact_capacity_relative_path_match": sum(x["exact_capacity_feedback_path_match"] for x in plant_rows),
        "no_clipping_controls": no_clip_checks,
        "all_route_mass_clipping_overflow_invariants_passed": True,
        "cells": cells,
        "interpretation_limit": "static finite-batch controlled audit; no physical telemetry price, trained-model gain, or benchmark separation",
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "rows": len(rows), "plant_rows": len(plant_rows),
        "plants_with_exact_capacity_relative_path_match": summary["plants_with_exact_capacity_relative_path_match"],
        "fallback_steps": recovery_failures, "no_clipping_controls": no_clip_checks,
        "ties": ties, "summary_sha256": sha256(summary_path),
        "plants_sha256": sha256(plants_path), "steps_sha256": sha256(steps_path),
        "protocol_sha256": summary["protocol_sha256"], "script_sha256": summary["script_sha256"],
        "all_invariants_passed": True,
    }, indent=2))


if __name__ == "__main__":
    run()
