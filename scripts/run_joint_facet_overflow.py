#!/usr/bin/env python3
"""Paired audit of random Top-K facets and two-step overflow on shared plants.

This run keeps the canonical per-expert admission rule A=min(R,C). It checks
co-occurrence of the already-stated facet and two-step overflow results; it
does not test whether one phenomenon causes the other.
"""

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
PROTOCOL = ROOT / "docs/paper/joint_facet_overflow_protocol_2026-10-17.md"
OUT = ROOT / "results/joint_facet_overflow"
E = 4
K = 2
SHORT = 0
DEST = 1
GRID = 1 << 30
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


def capacities(t: int, no_clip: bool = False) -> np.ndarray:
    if no_clip:
        return np.full(E, t, dtype=np.int64)
    out = np.asarray([t // 4, 7 * t // 12, 7 * t // 12, 7 * t // 12], dtype=np.int64)
    if int(out.sum()) != K * t:
        raise AssertionError("registered capacities do not sum to K*T")
    return out


def route(aff: np.ndarray, q_num: tuple[int, ...], q_den: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exact-grid Top-K counts, selected sets, and boundary-tie mask."""
    scores = aff.astype(np.int64) * q_den
    if any(q_num):
        scores -= np.asarray(q_num, dtype=np.int64)[None, :] * GRID
    order = np.argsort(-scores, axis=1, kind="stable")[:, :K]
    counts = np.bincount(order.reshape(-1), minlength=E).astype(np.int64)
    boundary = np.take_along_axis(scores, order[:, K - 1:K], axis=1)[:, 0]
    boundary_multiplicity = (scores == boundary[:, None]).sum(axis=1)
    return counts, order, boundary_multiplicity


def update(load: np.ndarray, t: int, eta: Fraction) -> tuple[tuple[int, ...], int]:
    # Pi_g(x) subtracts the minimum coordinate; the common mode does not
    # affect routing, so this is an exact rational representative.
    raw = eta.numerator * (E * load - K * t)
    den = eta.denominator * E * K * t
    raw -= int(raw.min())
    return tuple(int(x) for x in raw), den


def overflow(r: np.ndarray, c: np.ndarray) -> int:
    return int(np.maximum(r - c, 0).sum())


def phi(e: int, k: int, d: Fraction) -> Fraction:
    out = d
    for j in range(k):
        for m in range(j + 1):
            exponent_plus_one = e - j + m
            term = Fraction((-1) ** m * comb(e - 1, j) * comb(j, m), exponent_plus_one)
            out += term * (1 - d ** exponent_plus_one)
    return out


def facet_candidates(aff: np.ndarray, t: int, c: np.ndarray) -> dict:
    """Audit the registered (0,1) candidate-facet construction exactly."""
    sum_pair = aff[:, SHORT] + aff[:, DEST]
    diff = aff[:, SHORT] - aff[:, DEST]
    mid_ok = (6 * sum_pair >= 5 * GRID) & (6 * sum_pair <= 7 * GRID)
    diff_ok = diff.astype(object) ** 2 * t <= GRID**2
    other_above = np.zeros(t, dtype=np.int64)
    for e in range(E):
        if e not in (SHORT, DEST):
            other_above += (2 * aff[:, e] > sum_pair)
    candidate_indices = np.flatnonzero(mid_ok & diff_ok & (other_above == K - 1))

    counts = {"candidates": int(len(candidate_indices)), "regular_candidates": 0,
              "mismatched_facets": 0, "ambiguous_candidates": 0,
              "no_clip_mismatches": 0, "no_clip_ambiguous_candidates": 0}
    max_examined_ties = 0
    for token in candidate_indices:
        d = int(diff[token])
        # q_0=d/(2*GRID), q_1=-d/(2*GRID), represented with a factor 2
        # of headroom so a one-unit perturbation cannot move another score
        # across an integer-grid margin.
        multiplier = 2
        q_den = 2 * GRID * multiplier
        q_num = [0] * E
        q_num[SHORT] = d * multiplier
        q_num[DEST] = -d * multiplier
        _, _, boundary_multiplicity = route(aff, tuple(q_num), q_den)
        tied = np.flatnonzero(boundary_multiplicity > 1)
        max_examined_ties = max(max_examined_ties, int(len(tied)))
        if (len(tied) != 1 or int(tied[0]) != int(token)
                or int(boundary_multiplicity[token]) != 2):
            counts["ambiguous_candidates"] += 1
            counts["no_clip_ambiguous_candidates"] += 1
            continue

        # Move from the i-side to the j-side of the facet. The reverse move
        # is the opposite perturbation. The only changed row must be token.
        q_plus = q_num.copy()
        q_plus[SHORT] += 1
        q_plus[DEST] -= 1
        q_minus = q_num.copy()
        q_minus[SHORT] -= 1
        q_minus[DEST] += 1
        r_minus, set_minus, ties_minus = route(aff, tuple(q_minus), q_den)
        r_plus, set_plus, ties_plus = route(aff, tuple(q_plus), q_den)
        changed = np.flatnonzero(np.any(set_minus != set_plus, axis=1))
        if (len(changed) != 1 or int(changed[0]) != int(token)
                or SHORT not in set_minus[token] or DEST in set_minus[token]
                or DEST not in set_plus[token] or SHORT in set_plus[token]
                or np.any(ties_minus > 1) or np.any(ties_plus > 1)):
            counts["ambiguous_candidates"] += 1
            counts["no_clip_ambiguous_candidates"] += 1
            continue
        counts["regular_candidates"] += 1

        # Compare the admitted-count jump with the no-clipping jump. The
        # latter equals the facet normal and must have zero tangent part.
        a_minus = np.minimum(r_minus, c)
        a_plus = np.minimum(r_plus, c)
        jump = a_plus - a_minus
        admitted_source_change = int(r_minus[SHORT] <= c[SHORT])
        admitted_dest_change = int(r_minus[DEST] < c[DEST])
        mismatch = admitted_source_change != admitted_dest_change
        expected_jump = np.zeros(E, dtype=np.int64)
        expected_jump[SHORT] = -admitted_source_change
        expected_jump[DEST] = admitted_dest_change
        if not np.array_equal(jump, expected_jump):
            raise AssertionError("clipped-count jump disagrees with exact capacity-boundary indicators")
        normal = np.zeros(E, dtype=np.int64)
        normal[SHORT], normal[DEST] = 1, -1
        tangent_numerator = 2 * jump - int(np.dot(jump, normal)) * normal
        tangent_nonzero = bool(np.any(tangent_numerator != 0))
        if mismatch != tangent_nonzero:
            raise AssertionError("indicator mismatch and tangential-jump criteria disagree")
        if mismatch:
            counts["mismatched_facets"] += 1

        a_minus_nc = r_minus  # C_e=T and R_e<=T for every expert.
        a_plus_nc = r_plus
        jump_nc = a_plus_nc - a_minus_nc
        tangent_nc = 2 * jump_nc - int(np.dot(jump_nc, normal)) * normal
        if np.any(tangent_nc != 0):
            counts["no_clip_mismatches"] += 1

    counts["max_boundary_ties_at_candidate_pressures"] = max_examined_ties
    counts["plant_audit_valid"] = (
        counts["ambiguous_candidates"] == 0
        and counts["no_clip_ambiguous_candidates"] == 0
        and counts["no_clip_mismatches"] == 0
    )
    return counts


def run_plant(t: int, t_index: int, replicate: int) -> tuple[list[dict], dict]:
    seed = 20261031 + 100000 * E + 1000 * K + 10 * t_index + replicate
    rng = np.random.default_rng(seed)
    aff = rng.integers(0, GRID + 1, size=(t, E), dtype=np.int64)
    c = capacities(t)
    c_nc = capacities(t, no_clip=True)
    r0, sets0, tie0 = route(aff, (0,) * E, 1)
    if int(r0.sum()) != K * t or int(r0.max()) > t:
        raise AssertionError("zero-pressure mass/load invariant failed")
    a0 = np.minimum(r0, c)
    facet = facet_candidates(aff, t, c)
    rows: list[dict] = []

    for d in DS:
        eta = 8 * d  # d=eta*r/K with r=1/4 and K=2.
        if eta * Fraction(1, 4) / K != d:
            raise AssertionError("registered d and eta do not agree")
        arm_results = {}
        for signal in ("requested", "admitted"):
            load = r0 if signal == "requested" else a0
            q_num, q_den = update(load, t, eta)
            r1, _, tie1 = route(aff, q_num, q_den)
            a1 = np.minimum(r1, c)
            if int(r1.sum()) != K * t or int(r1.max()) > t:
                raise AssertionError("step-one Top-K mass/load invariant failed")
            if not np.array_equal(a1, np.minimum(r1, c)):
                raise AssertionError("canonical clipping identity failed")
            j0, j1 = overflow(r0, c), overflow(r1, c)
            if j0 != int((r0 - a0).sum()) or j1 != int((r1 - a1).sum()):
                raise AssertionError("overflow accounting invariant failed")
            arm_results[signal] = (q_num, q_den, r1, j0 + j1, int(np.count_nonzero(tie1)))

        # A no-clipping controller control must be identical to the requested
        # controller in both pressure and routing, since A=R there.
        a0_nc = np.minimum(r0, c_nc)
        for signal in ("requested", "admitted"):
            load_nc = r0 if signal == "requested" else a0_nc
            q_nc, qd_nc = update(load_nc, t, eta)
            r1_nc, _, _ = route(aff, q_nc, qd_nc)
            if np.any(overflow(r0, c_nc)) or np.any(overflow(r1_nc, c_nc)):
                raise AssertionError("no-clipping control has nonzero overflow")
            if signal == "requested":
                q_requested_nc, r_requested_nc = q_nc, r1_nc
            elif q_nc != q_requested_nc or not np.array_equal(r1_nc, r_requested_nc):
                raise AssertionError("no-clipping requested/admitted arms differ")

        j_a = arm_results["admitted"][3]
        j_r = arm_results["requested"][3]
        gap = Fraction(j_a - j_r, t)
        limit = phi(E, K, d) - Fraction(K, E)
        rows.append({
            "E": E, "K": K, "T": t, "T_index": t_index,
            "replicate": replicate, "seed": seed, "d": str(d), "eta": str(eta),
            "capacity_short": int(c[SHORT]), "capacity_other": int(c[DEST]),
            "overflow_admitted_two_step": j_a,
            "overflow_requested_two_step": j_r,
            "gap_normalized_A_minus_R": str(gap),
            "theory_limit": str(limit),
            "positive_gap": bool(gap > 0),
            "ties_step0": int(np.count_nonzero(tie0 > 1)),
            "ties_requested_step1": arm_results["requested"][4],
            "ties_admitted_step1": arm_results["admitted"][4],
            "facet_candidate_count": facet["candidates"],
            "facet_regular_candidate_count": facet["regular_candidates"],
            "facet_mismatch_count": facet["mismatched_facets"],
            "facet_ambiguous_candidate_count": facet["ambiguous_candidates"],
            "facet_no_clip_mismatch_count": facet["no_clip_mismatches"],
            "facet_audit_valid": facet["plant_audit_valid"],
            "joint_event_positive_gap_and_facet": bool(gap > 0 and facet["plant_audit_valid"] and facet["mismatched_facets"] > 0),
        })
    return rows, facet


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    facet_plants: list[dict] = []
    for ti, t in enumerate(TS):
        for rep in range(REPLICATES):
            plant_rows, facet = run_plant(t, ti, rep)
            rows.extend(plant_rows)
            facet_plants.append({
                "E": E, "K": K, "T": t, "T_index": ti, "replicate": rep,
                "seed": 20261031 + 100000 * E + 1000 * K + 10 * ti + rep,
                **facet,
            })

    plants_path = OUT / "plants.csv"
    with plants_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    facets_path = OUT / "facet_plants.csv"
    with facets_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(facet_plants[0]))
        writer.writeheader()
        writer.writerows(facet_plants)

    grouped: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["T"]), str(row["d"]))].append(row)
    cells = []
    for (t, d), cell in sorted(grouped.items(), key=lambda x: (x[0][0], Fraction(x[0][1]))):
        gaps = np.asarray([float(Fraction(row["gap_normalized_A_minus_R"])) for row in cell])
        mean = float(gaps.mean())
        se = float(gaps.std(ddof=1) / math.sqrt(len(gaps)))
        valid = [row for row in cell if row["facet_audit_valid"]]
        both = [row for row in valid if row["positive_gap"] and row["facet_mismatch_count"] > 0]
        cells.append({
            "E": E, "K": K, "T": t, "d": d, "n_plants": len(cell),
            "mean_gap": mean, "sample_sd": float(gaps.std(ddof=1)),
            "ci95_t_low": mean - T_CRIT_95_DF49 * se,
            "ci95_t_high": mean + T_CRIT_95_DF49 * se,
            "theory_limit": float(Fraction(cell[0]["theory_limit"])),
            "fraction_positive_gap": float(np.mean([row["positive_gap"] for row in cell])),
            "valid_facet_audits": len(valid),
            "fraction_with_regular_mismatched_facet_among_valid": (
                sum(int(row["facet_mismatch_count"] > 0) for row in valid) / len(valid) if valid else None
            ),
            "fraction_joint_event_among_valid": len(both) / len(valid) if valid else None,
            "invalid_facet_audits": len(cell) - len(valid),
        })

    joint = []
    for t in TS:
        facet_rows = [r for r in facet_plants if r["T"] == t]
        valid = [r for r in facet_rows if r["plant_audit_valid"]]
        joint.append({
            "T": t, "n_plants": len(facet_rows), "valid_facet_audits": len(valid),
            "fraction_with_candidate": float(np.mean([r["candidates"] > 0 for r in facet_rows])),
            "fraction_with_regular_facet": float(np.mean([r["regular_candidates"] > 0 for r in valid])) if valid else None,
            "fraction_with_mismatched_facet": float(np.mean([r["mismatched_facets"] > 0 for r in valid])) if valid else None,
            "fraction_no_clip_mismatch": float(np.mean([r["no_clip_mismatches"] > 0 for r in facet_rows])),
            "invalid_audit_count": len(facet_rows) - len(valid),
        })

    summary = {
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha256(PROTOCOL), "script_sha256": sha256(Path(__file__)),
        "affinity_grid_max": GRID, "E": E, "K": K, "T_values": list(TS),
        "replicates_per_T": REPLICATES, "paired_rows": len(rows),
        "all_150_plant_rows_retained": True,
        "no_clipping_control_mismatches": sum(r["no_clip_mismatches"] for r in facet_plants),
        "plant_facet_audits_valid": sum(r["plant_audit_valid"] for r in facet_plants),
        "plant_facet_audits_total": len(facet_plants),
        "all_mass_clipping_overflow_and_no_clip_controls_passed": True,
        "facet_cooccurrence_by_T": joint, "paired_gap_cells": cells,
        "confidence_interval": "paired plant mean +/- t_(0.975,49)*SE; t critical rounded to 2.0096",
        "interpretation_limit": "same-plant co-occurrence only; no causal mediation or benchmark separation claim",
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "paired_rows": len(rows), "cells": len(cells),
        "valid_facet_audits": summary["plant_facet_audits_valid"],
        "total_facet_audits": summary["plant_facet_audits_total"],
        "no_clipping_control_mismatches": summary["no_clipping_control_mismatches"],
        "summary_sha256": sha256(summary_path),
        "plants_sha256": sha256(plants_path), "facet_plants_sha256": sha256(facets_path),
        "protocol_sha256": summary["protocol_sha256"], "script_sha256": summary["script_sha256"],
        "facet_cooccurrence_by_T": joint,
    }, indent=2))


if __name__ == "__main__":
    main()
