#!/usr/bin/env python3
"""Paired synthetic check at positive finite-size Top-1 theorem thresholds."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_top1_finite_batch_value_thresholds import evaluate  # noqa: E402
from run_top1_arbitrary_e_exact_swapped_value import (  # noqa: E402
    exact_sign_classifier_errors,
    expected_overflow,
)


OUT = ROOT / "results" / "top1_exact_gap_threshold_2026-10-18"
EXPERT_COUNTS = (3, 4, 8)
REPLICATES = 50_000
CHUNK = 8_192
MASTER_SEED = 20261018


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def one_cell(e: int, t: int) -> dict[str, float | int | bool | str]:
    n = e - 2
    caps = np.array([t // 4, t // 4] + [t // (2 * n)] * n, dtype=np.int64)
    p0 = np.array([5 / 13, 4 / 13] + [4 / (13 * n)] * n, dtype=np.float64)
    if t % 4 or t % (2 * n) or int(caps.sum()) != t:
        raise AssertionError("batch size does not give exact integer capacities")
    p1 = p0.copy()
    p1[0], p1[1] = p1[1], p1[0]
    if not np.isclose(p0.sum(), 1.0, atol=1e-15):
        raise AssertionError("world-0 probabilities do not sum to one")

    # For K=1, the exact target pressure gives request probabilities c.
    c = caps.astype(np.float64) / t
    wrong0 = c.copy()
    wrong0[0] *= 5 / 4
    wrong0[1] /= 5 / 4
    wrong0 /= wrong0.sum()
    rc = expected_overflow(t, caps, c)
    rw = expected_overflow(t, caps, wrong0)
    if not rw > rc:
        raise AssertionError("wrong-world target must have higher overflow")

    exact_r_error, exact_a_error = exact_sign_classifier_errors(t, int(caps[0]))
    r_values: list[np.ndarray] = []
    a_values: list[np.ndarray] = []
    paired_admitted_equal = 0
    paired_requested_equal = 0
    request_mass_checks = 0
    admission_checks = 0
    rng = np.random.default_rng(MASTER_SEED + e + t)
    remaining = REPLICATES
    while remaining:
        count = min(CHUNK, remaining)
        r0 = rng.multinomial(t, p0, size=count)
        r1 = r0.copy()
        r1[:, [0, 1]] = r1[:, [1, 0]]
        a0 = np.minimum(r0, caps)
        a1 = np.minimum(r1, caps)

        if not (np.all(r0.sum(axis=1) == t) and np.all(r1.sum(axis=1) == t)):
            raise AssertionError("request mass conservation failed")
        if not np.array_equal(r1[:, [0, 1]], r0[:, [1, 0]]):
            raise AssertionError("paired world swap failed")
        if not (np.array_equal(a0, np.minimum(r0, caps))
                and np.array_equal(a1, np.minimum(r1, caps))):
            raise AssertionError("canonical clipping identity failed")

        # World 0 is the truth. Randomized ties have expected loss 1/2.
        r_diff = r0[:, 0] - r0[:, 1]
        a_diff = a0[:, 0] - a0[:, 1]
        r_loss = (r_diff < 0).astype(np.float64) + 0.5 * (r_diff == 0)
        a_loss = (a_diff < 0).astype(np.float64) + 0.5 * (a_diff == 0)
        r_values.append(r_loss)
        a_values.append(a_loss)
        paired_admitted_equal += int(np.all(a0 == a1, axis=1).sum())
        paired_requested_equal += int(np.all(r0 == r1, axis=1).sum())
        request_mass_checks += count
        admission_checks += int(np.all(a0 <= caps, axis=1).sum())
        remaining -= count

    r_loss_all = np.concatenate(r_values)
    a_loss_all = np.concatenate(a_values)
    r_mc = float(r_loss_all.mean())
    a_mc = float(a_loss_all.mean())
    r_se = float(r_loss_all.std(ddof=1) / math.sqrt(REPLICATES))
    a_se = float(a_loss_all.std(ddof=1) / math.sqrt(REPLICATES))
    if abs(r_mc - exact_r_error) > 5 * r_se + 1 / REPLICATES:
        raise AssertionError("requested classifier MC check exceeded five SE")
    if abs(a_mc - exact_a_error) > 5 * a_se + 1 / REPLICATES:
        raise AssertionError("admitted classifier MC check exceeded five SE")

    theorem_row = evaluate(e, t)
    exact_two_action_gap = (exact_a_error - exact_r_error) * (rw - rc)
    return {
        "E": e,
        "K": 1,
        "T": t,
        "replicates": REPLICATES,
        "seed": MASTER_SEED + e + t,
        "capacity": ";".join(map(str, caps.tolist())),
        "exact_request_error": exact_r_error,
        "mc_request_error": r_mc,
        "mc_request_error_se": r_se,
        "exact_admitted_error": exact_a_error,
        "mc_admitted_error": a_mc,
        "mc_admitted_error_se": a_se,
        "paired_admitted_vector_equality_rate": paired_admitted_equal / REPLICATES,
        "paired_request_vector_equality_rate": paired_requested_equal / REPLICATES,
        "target_action_expected_overflow": rc,
        "wrong_action_expected_overflow": rw,
        "exact_two_action_value_gap": exact_two_action_gap,
        "all_policy_gap_lower_bound": theorem_row["all_policy_gap_lower_bound"],
        "request_mass_checks_pass": request_mass_checks == REPLICATES,
        "admission_identity_checks_pass": admission_checks == REPLICATES,
        "mc_within_five_se": True,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    threshold_by_e = {}
    for e in EXPERT_COUNTS:
        denominator = math.lcm(4, 2 * (e - 2))
        for multiplier in range(1, 100_001):
            row = evaluate(e, multiplier * denominator)
            if row["all_policy_gap_lower_bound"] > 0:
                threshold_by_e[e] = int(row["T"])
                break
        else:
            raise RuntimeError(f"no positive certificate found for E={e}")

    rows = []
    for e in EXPERT_COUNTS:
        threshold = threshold_by_e[e]
        rows.append(one_cell(e, threshold))
        rows.append(one_cell(e, 2 * threshold))

    cells_path = OUT / "cells.csv"
    with cells_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "experiment": "Top-1 exact value-gap check at positive finite-size certificate thresholds",
        "protocol": "docs/paper/top1_exact_gap_threshold_experiment_protocol_2026-10-18.md",
        "theorem": "docs/paper/top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md",
        "threshold_scan": "scripts/audit_top1_finite_batch_value_thresholds.py",
        "replicates_per_cell": REPLICATES,
        "cells": rows,
        "limits": [
            "Monte Carlo validates the registered signal classifier and coupling only.",
            "The all-policy lower bound is analytic and reported separately.",
            "The two-action value is not the unrestricted-pressure value.",
            "No system price, trained-model quality, or benchmark separation is measured.",
        ],
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"cells_sha256={sha256(cells_path)}")
    print(f"summary_sha256={sha256(summary_path)}")
    for row in rows:
        print(
            f"E={row['E']} T={row['T']} exact_gap={row['exact_two_action_value_gap']:.6g} "
            f"all_policy_lb={row['all_policy_gap_lower_bound']:.6g} "
            f"A_equal={row['paired_admitted_vector_equality_rate']:.4f}"
        )


if __name__ == "__main__":
    main()
