#!/usr/bin/env python3
"""Controlled count-law experiment for the general two-saturation theorem."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import beta, binom


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/two_saturated_general_value_protocol_2026-10-17.md"
OUT = ROOT / "results/two_saturated_general_value"
ES = (3, 4, 8)
DELTAS = (0.04, 0.08, 0.12)
TS = (4800, 19200)
REPS = 2000
A = 0.4
C = 0.25
TAIL_MASS = 0.2
ALPHA = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cp_interval(k: int, n: int) -> tuple[float, float]:
    lo = 0.0 if k == 0 else float(beta.ppf(ALPHA / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - ALPHA / 2, k + 1, n - k))
    return lo, hi


def capacities(e: int, t: int) -> np.ndarray:
    tail_c = 0.5 / (e - 2)
    c = np.asarray([C, C] + [tail_c] * (e - 2), dtype=np.float64)
    if not np.allclose(c * t, np.round(c * t), rtol=0, atol=1e-10):
        raise AssertionError("registered capacity is not integer at this T")
    return c


def world_probs(e: int, delta: float) -> tuple[np.ndarray, np.ndarray]:
    tail = TAIL_MASS / (e - 2)
    p0 = np.asarray([A, A] + [tail] * (e - 2), dtype=np.float64)
    p1 = np.asarray([A + delta, A - delta] + [tail] * (e - 2), dtype=np.float64)
    assert np.isclose(p0.sum(), 1.0) and np.isclose(p1.sum(), 1.0)
    return p0, p1


def pressure_for_target(p: np.ndarray, target: np.ndarray) -> np.ndarray:
    q = np.log(p) - np.log(target)
    q -= q.min()
    return q


def routed_prob(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    z = np.log(p) - q
    z -= z.max()
    rho = np.exp(z)
    return rho / rho.sum()


def cost(p: np.ndarray, target: np.ndarray, q: np.ndarray) -> float:
    rho = routed_prob(p, q)
    return float(np.maximum(rho - target, 0).sum())


def expected_batch_overflow_fraction(p: np.ndarray, target: np.ndarray, t: int) -> float:
    """Exact E[sum_e (X_e-C_e)_+]/T for multinomial(T,p)."""
    capacities = np.rint(target * t).astype(np.int64)
    total = 0.0
    for pe, ce in zip(p, capacities, strict=True):
        # E[(X-C)_+] = T p P(Bin(T-1,p)>=C) - C P(Bin(T,p)>=C+1).
        first = t * pe * float(binom.sf(int(ce) - 1, t - 1, pe))
        second = int(ce) * float(binom.sf(int(ce), t, pe))
        total += max(0.0, first - second)
    return total / t


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plant_rows: list[dict] = []
    cell_rows: list[dict] = []
    for e in ES:
        for delta in DELTAS:
            p0, p1 = world_probs(e, delta)
            for ti, t in enumerate(TS):
                c = capacities(e, t)
                c_int = np.rint(c * t).astype(np.int64)
                tail_p = p0[2:]
                eps_a = (2 * math.exp(-2 * t * (A - delta - C) ** 2)
                         + sum(math.exp(-2 * t * (c[2+j] - tail_p[j]) ** 2)
                               for j in range(e - 2)))
                eps_r = math.exp(-t * delta**2 / 2)
                v_star = C * delta / (2 * A)
                q0 = pressure_for_target(p0, c)
                q1 = pressure_for_target(p1, c)
                if not (np.allclose(routed_prob(p0, q0), c, rtol=0, atol=1e-12)
                        and np.allclose(routed_prob(p1, q1), c, rtol=0, atol=1e-12)):
                    raise AssertionError("target-matched pressure does not realize C/T")
                action_cost = np.asarray([
                    [cost(p0, c, q0), cost(p0, c, q1)],
                    [cost(p1, c, q0), cost(p1, c, q1)],
                ])
                if not (np.allclose(action_cost[0, 0], 0, atol=1e-12)
                        and np.allclose(action_cost[1, 1], 0, atol=1e-12)
                        and np.isclose(action_cost[1, 0], 2 * v_star, atol=1e-12)):
                    raise AssertionError("closed-form pressure/action cost check failed")

                batch_action_cost = np.asarray([
                    [expected_batch_overflow_fraction(routed_prob(p0, q0), c, t),
                     expected_batch_overflow_fraction(routed_prob(p0, q1), c, t)],
                    [expected_batch_overflow_fraction(routed_prob(p1, q0), c, t),
                     expected_batch_overflow_fraction(routed_prob(p1, q1), c, t)],
                ])
                if not np.all(batch_action_cost + 1e-12 >= action_cost):
                    raise AssertionError("Jensen check failed: batch cost below population cost")
                if not np.isclose(batch_action_cost[0, 0], batch_action_cost[1, 1], atol=1e-12):
                    raise AssertionError("world-matched target actions have different batch noise")
                threshold_count = math.ceil(t * (A + delta / 2) - 1e-12)
                false_positive = float(binom.sf(threshold_count - 1, t, p0[0]))
                false_negative = float(binom.cdf(threshold_count - 1, t, p1[0]))
                requested_batch_value = 0.5 * (
                    (1 - false_positive) * batch_action_cost[0, 0]
                    + false_positive * batch_action_cost[0, 1]
                    + false_negative * batch_action_cost[1, 0]
                    + (1 - false_negative) * batch_action_cost[1, 1]
                )
                admitted_constant_batch_value = 0.5 * (
                    batch_action_cost[0, 0] + batch_action_cost[1, 0]
                )
                matched_target_noise = 0.5 * (
                    batch_action_cost[0, 0] + batch_action_cost[1, 1]
                )

                seed = 20261017 + e * 1_000_000 + int(round(delta * 1000)) * 10_000 + ti * 1000
                rng = np.random.default_rng(seed)
                errors_r = [0, 0]
                errors_a = [0, 0]
                costs_r = [0.0, 0.0]
                costs_a = [0.0, 0.0]
                good_counts = [0, 0]
                paired_equal = 0
                for rep in range(REPS):
                    # Include the pair as an explicit residual category.
                    # NumPy assigns any remaining probability mass to the
                    # final category, so passing tail_p alone is incorrect.
                    joint_counts = rng.multinomial(t, np.concatenate((tail_p, [2 * A])))
                    tail_counts = joint_counts[:-1]
                    pair_total = int(joint_counts[-1])
                    pair_x0 = int(rng.binomial(pair_total, 0.5))
                    pair_x1 = int(rng.binomial(pair_total, (A + delta) / (2 * A)))
                    requests = (
                        np.concatenate(([pair_x0, pair_total - pair_x0], tail_counts)),
                        np.concatenate(([pair_x1, pair_total - pair_x1], tail_counts)),
                    )
                    admissions = tuple(np.minimum(r, c_int) for r in requests)
                    for h in (0, 1):
                        if int(requests[h].sum()) != t:
                            raise AssertionError("Top-1 request mass was not conserved")
                        if not np.array_equal(admissions[h], np.minimum(requests[h], c_int)):
                            raise AssertionError("canonical per-expert admission identity failed")
                    good = []
                    for h in (0, 1):
                        r = requests[h]
                        good_h = bool(r[0] >= c_int[0] and r[1] >= c_int[1]
                                      and np.all(r[2:] < c_int[2:]))
                        good.append(good_h)
                        good_counts[h] += int(good_h)
                        # Requested threshold classifier, pre-registered.
                        hhat_r = int(r[0] / t >= A + delta / 2)
                        errors_r[h] += int(hhat_r != h)
                        costs_r[h] += float(action_cost[h, hhat_r])
                        # Admitted diagnostic classifier; fair independent
                        # tie-breaking coin is correct for an equal prior.
                        av = admissions[h]
                        if av[0] > av[1]:
                            hhat_a = 1
                        elif av[0] < av[1]:
                            hhat_a = 0
                        else:
                            hhat_a = int(rng.integers(0, 2))
                        errors_a[h] += int(hhat_a != h)
                        costs_a[h] += float(action_cost[h, hhat_a])
                    paired_equal += int(np.array_equal(admissions[0], admissions[1]))
                    plant_rows.append({
                        "E": e, "delta": delta, "T": t, "replicate": rep,
                        "cell_seed": seed, "tail_counts": ",".join(map(str, tail_counts.tolist())),
                        "R0": ",".join(map(str, requests[0].tolist())),
                        "R1": ",".join(map(str, requests[1].tolist())),
                        "A0": ",".join(map(str, admissions[0].tolist())),
                        "A1": ",".join(map(str, admissions[1].tolist())),
                        "good0": good[0], "good1": good[1],
                        "admitted_vectors_equal_under_coupling": bool(np.array_equal(admissions[0], admissions[1])),
                    })

                for h in (0, 1):
                    e_lo, e_hi = cp_interval(errors_r[h], REPS)
                    a_lo, a_hi = cp_interval(errors_a[h], REPS)
                    cell_rows.append({
                        "E": e, "delta": delta, "T": t, "world": h, "replicates": REPS,
                        "good_event_rate": good_counts[h] / REPS,
                        "good_event_failures": REPS - good_counts[h],
                        "theorem_eps_A_bound": eps_a,
                        "requested_classifier_error": errors_r[h] / REPS,
                        "requested_error_ci95_low": e_lo, "requested_error_ci95_high": e_hi,
                        "theorem_eps_R_bound": eps_r,
                        "admitted_simple_classifier_error": errors_a[h] / REPS,
                        "admitted_error_ci95_low": a_lo, "admitted_error_ci95_high": a_hi,
                        "mean_requested_policy_population_cost": costs_r[h] / REPS,
                        "mean_admitted_simple_policy_population_cost": costs_a[h] / REPS,
                    })

                cell_rows.append({
                    "E": e, "delta": delta, "T": t, "world": "pooled",
                    "replicates": REPS, "coupled_admitted_vector_equal_rate": paired_equal / REPS,
                    "theorem_eps_A_bound": eps_a,
                    "exact_common_action_value_V_star": v_star,
                    "admitted_optimal_value_lower_bound": max(0.0, v_star - eps_a),
                    "admitted_optimal_value_upper_bound": v_star,
                    "requested_optimal_value_upper_bound": eps_r,
                    "value_gap_lower_bound": v_star - eps_a - eps_r,
                    "value_gap_upper_bound": v_star,
                    "requested_threshold_false_positive_exact": false_positive,
                    "requested_threshold_false_negative_exact": false_negative,
                    "matched_target_expected_batch_overflow_fraction": matched_target_noise,
                    "requested_threshold_expected_batch_overflow_fraction": requested_batch_value,
                    "admitted_constant_expected_batch_overflow_fraction": admitted_constant_batch_value,
                    "finite_batch_value_gap_lower_bound": v_star - eps_a - requested_batch_value,
                    "finite_batch_value_gap_upper_bound": admitted_constant_batch_value,
                    "admitted_constant_action_value": v_star,
                    "requested_threshold_policy_mean_cost": (costs_r[0] + costs_r[1]) / (2 * REPS),
                    "admitted_simple_policy_mean_cost": (costs_a[0] + costs_a[1]) / (2 * REPS),
                })

    plants_path = OUT / "paired_plants.csv"
    with plants_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(plant_rows[0])); w.writeheader(); w.writerows(plant_rows)
    cells_path = OUT / "cells.csv"
    with cells_path.open("w", newline="", encoding="utf-8") as f:
        # Per-world diagnostics and pooled value summaries intentionally have
        # different fields. Preserve the union so pooled theorem quantities
        # are not silently discarded and heterogeneous rows serialize safely.
        fieldnames = list(dict.fromkeys(key for row in cell_rows for key in row))
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="raise")
        w.writeheader()
        w.writerows(cell_rows)
    pooled = [r for r in cell_rows if r.get("world") == "pooled"]
    summary = {
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha256(PROTOCOL), "script_sha256": sha256(Path(__file__)),
        "E_values": list(ES), "delta_values": list(DELTAS), "T_values": list(TS),
        "replicates_per_world_cell": REPS,
        "paired_draws": len(plant_rows), "cell_rows": len(cell_rows),
        "all_action_cost_checks_passed": True,
        "all_batch_cost_jensen_checks_passed": True,
        "oracle_population_cost": 0.0,
        "minimum_good_event_rate": min(
            r["good_event_rate"] for r in cell_rows if r.get("world") in (0, 1)
        ),
        "pooled_summary": pooled,
        "interpretation_limit": "finite count-law audit of both population overflow and exact expected realized batch overflow; no trained model, measured telemetry cost, multi-round optimality, or benchmark separation",
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "paired_draws": len(plant_rows), "cell_rows": len(cell_rows),
        "pooled_cells": len(pooled),
        "worst_coupled_admitted_equality_rate": min(x["coupled_admitted_vector_equal_rate"] for x in pooled),
        "worst_requested_error": max(r["requested_classifier_error"] for r in cell_rows if r.get("world") in (0, 1)),
        "worst_eps_A": max(x["theorem_eps_A_bound"] for x in pooled),
        "summary_sha256": sha256(summary_path),
        "paired_plants_sha256": sha256(plants_path), "cells_sha256": sha256(cells_path),
        "protocol_sha256": summary["protocol_sha256"], "script_sha256": summary["script_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
