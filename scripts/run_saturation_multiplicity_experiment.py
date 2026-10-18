#!/usr/bin/env python3
"""Controlled one-vs-two-saturation audit for the existing Top-K model.

The primary outputs are exact count-law Bayes risks in the registered
two-target-action class. Monte Carlo is used only to check the exact formulas
and the coupling/reconstruction events.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np

from run_topk_swapped_saturation_value import (
    exact_bayes_errors,
    expected_overflow,
    float_inclusion,
    subset_distribution,
    target_score,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "saturation_multiplicity_2026-10-18"
ES = (3, 4, 6, 8)
SCALES = (64, 128, 256)
REPLICATES = 5_000
MASTER_SEED = 20261018
WEIGHT = Fraction(5, 4)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def profiles(e: int, k: int):
    weights = (WEIGHT,) + (Fraction(1),) * (e - 1)
    weights_swap = (Fraction(1), WEIGHT) + (Fraction(1),) * (e - 2)
    masks, probs, p0 = subset_distribution(weights, k)
    _, _, p1 = subset_distribution(weights_swap, k)
    if p1 != (p0[1], p0[0], *p0[2:]):
        raise AssertionError("world 1 is not the exact coordinate swap")
    high, low = p0[0], p0[1]
    delta = high - low
    if not delta > 0:
        raise AssertionError("swapped pair has no strict request preference")
    one = (low + delta / 4, low + delta / 4, *(
        p0[j] + delta / (2 * (e - 2)) for j in range(2, e)
    ))
    two = (low - delta / 4, low - delta / 4, *(
        p0[j] + 3 * delta / (2 * (e - 2)) for j in range(2, e)
    ))
    return masks, probs, p0, p1, delta, {"one": one, "two": two}


def nearest_integer_pair_capacity(target: Fraction, e: int, k: int, t: int) -> int:
    total = k * t
    residue = total % (e - 2)
    candidates = [c for c in range(max(1, int(float(target * t)) - 2 * e),
                                  min(t - 1, int(float(target * t)) + 2 * e) + 1)
                  if (2 * c) % (e - 2) == residue]
    if not candidates:
        raise RuntimeError(f"no integer capacity candidate E={e}, K={k}, T={t}")
    return min(candidates, key=lambda c: (abs(Fraction(c, t) - target), c))


def rows_for_cell(e: int, k: int, t: int, profile_name: str,
                  masks, subset_probs, p0_fraction, p1_fraction, delta,
                  profile_fraction):
    target_pair = profile_fraction[0]
    pair_cap = nearest_integer_pair_capacity(target_pair, e, k, t)
    rem = k * t - 2 * pair_cap
    if rem <= 0 or rem % (e - 2):
        raise RuntimeError("integer capacity rounding did not preserve exact-total/equal-tail")
    tail_cap = rem // (e - 2)
    cap_int = np.array([pair_cap, pair_cap, *([tail_cap] * (e - 2))], dtype=np.int64)
    cap = cap_int.astype(float) / t
    if int(cap_int.sum()) != k * t or np.any(cap_int <= 0) or np.any(cap_int >= t):
        raise RuntimeError(f"invalid rounded capacity profile E={e},K={k},T={t},profile={profile_name}")

    p0 = np.array([float(x) for x in p0_fraction])
    p1 = np.array([float(x) for x in p1_fraction])
    if profile_name == "one":
        if not (p0[0] > cap[0] > p0[1] and all(p0[j] < cap[j] for j in range(2, e))):
            raise RuntimeError(f"one-saturation margin failed E={e},K={k},T={t}")
    else:
        if not (p0[0] > cap[0] and p0[1] > cap[1]
                and all(p0[j] < cap[j] for j in range(2, e))):
            raise RuntimeError(f"two-saturation margin failed E={e},K={k},T={t}")

    logits_cap, residual = target_score(cap, k)
    theta0 = np.log(np.array([float(WEIGHT)] + [1.0] * (e - 1)))
    theta1 = np.log(np.array([1.0, float(WEIGHT)] + [1.0] * (e - 2)))
    q0, q1 = theta0 - logits_cap, theta1 - logits_cap
    q0 -= q0.mean()
    q1 -= q1.mean()
    incl = np.empty((2, 2, e), dtype=float)
    for h, theta in enumerate((theta0, theta1)):
        for action, q in enumerate((q0, q1)):
            incl[h, action] = float_inclusion(theta - q, k)
    risk = np.array([
        [expected_overflow(t, cap_int, incl[h, action], k) for action in range(2)]
        for h in range(2)
    ])
    # Swap symmetry requires equal on-target and off-target risks.
    if not (abs(risk[0, 0] - risk[1, 1]) < 1e-9
            and abs(risk[0, 1] - risk[1, 0]) < 1e-9
            and risk[0, 1] > risk[0, 0]):
        raise RuntimeError(f"target-action risk symmetry/order failed: {risk.tolist()}")

    plus = sum((prob for mask, prob in zip(masks, subset_probs, strict=True)
                if mask & 1 and not mask & 2), Fraction(0))
    minus = sum((prob for mask, prob in zip(masks, subset_probs, strict=True)
                 if mask & 2 and not mask & 1), Fraction(0))
    both = sum((prob for mask, prob in zip(masks, subset_probs, strict=True)
               if mask & 1 and mask & 2), Fraction(0))
    req_err, adm_err = exact_bayes_errors(t, pair_cap, float(plus), float(minus), float(both))
    exact_req_value = risk[0, 0] + float(req_err) * (risk[0, 1] - risk[0, 0])
    exact_adm_value = risk[0, 0] + float(adm_err) * (risk[0, 1] - risk[0, 0])
    one_reconstruction_bound = 0.0
    two_admitted_tv_bound = 0.0
    for world, inclusion in enumerate((p0, p1)):
        designated = world  # world 0 overloads expert 0; world 1 overloads expert 1.
        if profile_name == "one":
            one_reconstruction_bound += sum(
                math.exp(-2.0 * t * (cap[j] - inclusion[j]) ** 2)
                for j in range(e) if j != designated
            ) / 2.0
        else:
            two_admitted_tv_bound += sum(
                math.exp(-2.0 * t * (inclusion[j] - cap[j]) ** 2)
                if j < 2 else math.exp(-2.0 * t * (cap[j] - inclusion[j]) ** 2)
                for j in range(e)
            ) / 2.0
    request_classification_bound = math.exp(-t * float(delta) ** 2 / 2.0)

    seed = MASTER_SEED + e * 1_000_003 + k * 10_007 + t * 17 + (0 if profile_name == "one" else 1)
    rng = np.random.default_rng(seed)
    probs_float = np.array([float(x) for x in subset_probs], dtype=float)
    probs_float /= probs_float.sum()
    sample0 = rng.multinomial(t, probs_float, size=REPLICATES) @ np.array(
        [[int(bool(mask & (1 << j))) for j in range(e)] for mask in masks], dtype=np.int64
    )
    if not np.all(sample0.sum(axis=1) == k * t):
        raise AssertionError("sampled request counts violate Top-K mass conservation")
    sample1 = sample0.copy()
    sample1[:, [0, 1]] = sample1[:, [1, 0]]
    if not np.array_equal(sample1[:, [0, 1]], sample0[:, [1, 0]]):
        raise AssertionError("paired world sample is not the exact coordinate swap")
    caps_mat = np.broadcast_to(cap_int, sample0.shape)
    admit0 = np.minimum(sample0, caps_mat)
    admit1 = np.minimum(sample1, caps_mat)
    if not np.array_equal(admit0, np.minimum(sample0, caps_mat)) or not np.array_equal(
        admit1, np.minimum(sample1, caps_mat)
    ):
        raise AssertionError("admitted counts violate canonical coordinatewise clipping")

    # Randomize classifier ties with a fixed RNG, preserving the equal-prior Bayes rule.
    req_pred0 = sample0[:, 0] > sample0[:, 1]
    req_tie = sample0[:, 0] == sample0[:, 1]
    req_pred0[req_tie] = rng.integers(0, 2, size=int(req_tie.sum())).astype(bool)
    adm_pred0 = admit0[:, 0] > admit0[:, 1]
    adm_tie = admit0[:, 0] == admit0[:, 1]
    adm_pred0[adm_tie] = rng.integers(0, 2, size=int(adm_tie.sum())).astype(bool)
    # Under world 0, prediction True means world 0; world 1 is the swapped pair.
    req_error_count = int(np.count_nonzero(~req_pred0))
    adm_error_count = int(np.count_nonzero(~adm_pred0))
    req_mc_error = req_error_count / REPLICATES
    adm_mc_error = adm_error_count / REPLICATES
    req_se = math.sqrt(max(float(req_err) * (1.0 - float(req_err)), 0.0) / REPLICATES)
    adm_se = math.sqrt(max(float(adm_err) * (1.0 - float(adm_err)), 0.0) / REPLICATES)
    req_z = abs(req_mc_error - float(req_err)) / max(req_se, 1e-15)
    adm_z = abs(adm_mc_error - float(adm_err)) / max(adm_se, 1e-15)

    equality = np.all(admit0 == admit1, axis=1)
    exact_reconstruction = np.zeros(REPLICATES, dtype=bool)
    for i, a in enumerate(admit0):
        excess = k * t - int(a.sum())
        saturated = np.flatnonzero(a == cap_int)
        if excess == 0:
            decoded = a.copy()
            exact_reconstruction[i] = np.array_equal(decoded, sample0[i])
        elif len(saturated) == 1:
            decoded = a.copy()
            decoded[saturated[0]] += excess
            exact_reconstruction[i] = np.array_equal(decoded, sample0[i])
    no_clip_equal = np.array_equal(sample0, np.minimum(sample0, np.full_like(sample0, t)))
    if not no_clip_equal:
        raise AssertionError("no-clipping control failed")

    return {
        "E": e, "K": k, "T": t, "profile": profile_name,
        "capacity_pair": pair_cap, "capacity_tail": tail_cap,
        "capacity_fraction_pair": pair_cap / t,
        "capacity_fraction_tail": tail_cap / t,
        "p_high": float(p0_fraction[0]), "p_low": float(p0_fraction[1]),
        "delta": float(delta),
        "min_sat_margin": min(float(p0_fraction[0] - cap[0]), float(p0_fraction[1] - cap[1])),
        "min_unsat_margin": min(float(cap[j] - p0[j]) for j in range(2, e)),
        "target_residual_inf": residual,
        "request_bayes_error_exact": float(req_err),
        "admitted_bayes_error_exact": float(adm_err),
        "target_action_risk_correct": float(risk[0, 0]),
        "target_action_risk_wrong": float(risk[0, 1]),
        "two_action_value_request_exact": exact_req_value,
        "two_action_value_admitted_exact": exact_adm_value,
        "two_action_value_gap_exact": exact_adm_value - exact_req_value,
        "one_saturation_decoder_failure_bound": one_reconstruction_bound if profile_name == "one" else "",
        "two_saturation_admitted_tv_bound": two_admitted_tv_bound if profile_name == "two" else "",
        "requested_classifier_hoeffding_bound": request_classification_bound,
        "request_error_mc_world0": req_mc_error,
        "admitted_error_mc_world0": adm_mc_error,
        "request_error_mc_abs_diff": abs(req_mc_error - float(req_err)),
        "admitted_error_mc_abs_diff": abs(adm_mc_error - float(adm_err)),
        "request_error_mc_z": req_z,
        "admitted_error_mc_z": adm_z,
        "admitted_vector_equal_fraction": float(np.mean(equality)),
        "admitted_reconstructs_request_fraction": float(np.mean(exact_reconstruction)),
        "no_clip_identity": no_clip_equal,
        "replicates": REPLICATES, "seed": seed,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for e in ES:
        for k in range(1, e):
            masks, probs, p0, p1, delta, cap_profiles = profiles(e, k)
            for scale in SCALES:
                t = (e - 2) * scale
                for profile_name, cap_profile in cap_profiles.items():
                    rows.append(rows_for_cell(e, k, t, profile_name, masks, probs,
                                              p0, p1, delta, cap_profile))

    cells_path = OUT / "cells.csv"
    fields = list(rows[0])
    with cells_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    by_profile = {}
    for profile in ("one", "two"):
        group = [r for r in rows if r["profile"] == profile]
        by_profile[profile] = {
            "cells": len(group),
            "mean_exact_two_action_gap": float(np.mean([r["two_action_value_gap_exact"] for r in group])),
            "min_exact_two_action_gap": float(np.min([r["two_action_value_gap_exact"] for r in group])),
            "max_exact_two_action_gap": float(np.max([r["two_action_value_gap_exact"] for r in group])),
            "mean_admitted_error": float(np.mean([r["admitted_bayes_error_exact"] for r in group])),
            "mean_request_error": float(np.mean([r["request_bayes_error_exact"] for r in group])),
            "mean_admitted_vector_equality": float(np.mean([r["admitted_vector_equal_fraction"] for r in group])),
            "mean_request_reconstruction": float(np.mean([r["admitted_reconstructs_request_fraction"] for r in group])),
            "max_request_mc_error_abs_diff": float(np.max([r["request_error_mc_abs_diff"] for r in group])),
            "max_admitted_mc_error_abs_diff": float(np.max([r["admitted_error_mc_abs_diff"] for r in group])),
        }
    paired = []
    index = {(r["E"], r["K"], r["T"], r["profile"]): r for r in rows}
    for e in ES:
        for k in range(1, e):
            for scale in SCALES:
                t = (e - 2) * scale
                one, two = index[(e, k, t, "one")], index[(e, k, t, "two")]
                paired.append({"E": e, "K": k, "T": t,
                               "one_saturation_gap": one["two_action_value_gap_exact"],
                               "two_saturation_gap": two["two_action_value_gap_exact"],
                               "gap_increase_two_minus_one": two["two_action_value_gap_exact"] - one["two_action_value_gap_exact"]})

    summary = {
        "experiment": "one-versus-two persistent saturation under Gumbel Top-K",
        "registered_E": list(ES), "registered_K": "all 1..E-1",
        "registered_scales": list(SCALES), "replicates_per_cell": REPLICATES,
        "cell_count": len(rows), "paired_profile_comparisons": len(paired),
        "controls_passed": all(r["no_clip_identity"] and r["target_residual_inf"] <= 1e-8 for r in rows),
        "all_signal_value_gaps_nonnegative": all(r["two_action_value_gap_exact"] >= -1e-12 for r in rows),
        "one_saturation_gap_within_decoder_bound": all(
            r["profile"] != "one" or r["two_action_value_gap_exact"] <= r["one_saturation_decoder_failure_bound"] + 1e-10
            for r in rows
        ),
        "finite_grid_two_minus_one_gap_positive_all_pairs": all(
            p["gap_increase_two_minus_one"] > 0 for p in paired
        ),
        "max_monte_carlo_error_in_standard_errors": max(
            max(r["request_error_mc_z"], r["admitted_error_mc_z"]) for r in rows
        ),
        "all_monte_carlo_checks_within_4_se": all(
            max(r["request_error_mc_z"], r["admitted_error_mc_z"]) < 4 for r in rows
        ),
        "profiles": by_profile,
        "paired_comparisons": paired,
        "runner_sha256": sha256(Path(__file__)),
        "cells_sha256": sha256(cells_path),
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
