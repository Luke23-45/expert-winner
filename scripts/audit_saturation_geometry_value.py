#!/usr/bin/env python3
"""Exact count-law audit of the one- vs two-saturated Top-1 family."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Dict, Iterable, Tuple

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/paper/saturation_geometry_value_experiment_protocol_2026-10-17.md"
OUT = ROOT / "results/saturation_geometry_value"
WORLDS = ((0.40, 0.40, 0.20), (0.46, 0.34, 0.20))
CAPACITY_PROFILES = {
    "one_saturated": (0.25, 0.50, 0.25),
    "two_saturated": (0.25, 0.25, 0.50),
}
HORIZONS = (40, 80, 160, 320, 640, 1280)

Counts = Tuple[int, int, int]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def compositions(total: int) -> Iterable[Counts]:
    for x0 in range(total + 1):
        for x1 in range(total - x0 + 1):
            yield (x0, x1, total - x0 - x1)


def multinomial_probability(counts: Counts, probs: Tuple[float, ...]) -> float:
    n = sum(counts)
    logp = math.lgamma(n + 1)
    for count, p in zip(counts, probs, strict=True):
        logp -= math.lgamma(count + 1)
        if count:
            logp += count * math.log(p)
    return math.exp(logp)


def multinomial_log_probability(counts: Counts, probs: Tuple[float, ...]) -> float:
    n = sum(counts)
    logp = math.lgamma(n + 1)
    for count, p in zip(counts, probs, strict=True):
        logp -= math.lgamma(count + 1)
        if count:
            logp += count * math.log(p)
    return logp


def request_law(probs: Tuple[float, ...], t: int) -> Dict[Counts, float]:
    return {r: multinomial_probability(r, probs) for r in compositions(t)}


def logaddexp(left: float, right: float) -> float:
    if left == -math.inf:
        return right
    if right == -math.inf:
        return left
    high, low = max(left, right), min(left, right)
    return high + math.log1p(math.exp(low - high))


def request_log_law(probs: Tuple[float, ...], t: int) -> Dict[Counts, float]:
    return {r: multinomial_log_probability(r, probs) for r in compositions(t)}


def clipped_law(law: Dict[Counts, float], caps: Counts, include_r1: bool = False) -> Dict[tuple, float]:
    out: Dict[tuple, float] = {}
    for r, prob in law.items():
        a = tuple(min(x, c) for x, c in zip(r, caps, strict=True))
        key = (a, r[0]) if include_r1 else a
        out[key] = out.get(key, 0.0) + prob
    return out


def clipped_log_law(law: Dict[Counts, float], caps: Counts, include_r1: bool = False) -> Dict[tuple, float]:
    out: Dict[tuple, float] = {}
    for r, logprob in law.items():
        a = tuple(min(x, c) for x, c in zip(r, caps, strict=True))
        key = (a, r[0]) if include_r1 else a
        out[key] = logaddexp(out.get(key, -math.inf), logprob)
    return out


def marginal_law(law: Dict[Counts, float], expert: int) -> Dict[int, float]:
    out: Dict[int, float] = {}
    for r, prob in law.items():
        key = r[expert]
        out[key] = out.get(key, 0.0) + prob
    return out


def marginal_log_law(law: Dict[Counts, float], expert: int) -> Dict[int, float]:
    out: Dict[int, float] = {}
    for r, logprob in law.items():
        key = r[expert]
        out[key] = logaddexp(out.get(key, -math.inf), logprob)
    return out


def binomial_overflow_fraction(p: float, cap: int, t: int) -> float:
    """Exact finite sum for E[(Binomial(t,p)-cap)_+]/t."""
    terms = []
    log_t_fact = math.lgamma(t + 1)
    for x in range(cap + 1, t + 1):
        log_prob = (log_t_fact - math.lgamma(x + 1) - math.lgamma(t - x + 1)
                    + x * math.log(p) + (t - x) * math.log1p(-p))
        terms.append((x - cap) * math.exp(log_prob))
    return math.fsum(terms) / t


def route_after_action(world: Tuple[float, ...], target: Tuple[float, ...], action_target: Tuple[float, ...]) -> Tuple[float, ...]:
    # q^j=log(p_j)-log(c); hence softmax(log(p_h)-q^j) ∝ p_h*c/p_j.
    unnormalized = tuple(p * c / pj for p, c, pj in zip(world, target, action_target, strict=True))
    z = sum(unnormalized)
    return tuple(x / z for x in unnormalized)


def action_costs(target: Tuple[float, ...], caps: Counts, t: int) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    costs = []
    for world in WORLDS:
        row = []
        for action_world in WORLDS:
            routed = route_after_action(world, target, action_world)
            row.append(sum(binomial_overflow_fraction(p, c, t) for p, c in zip(routed, caps, strict=True)))
        costs.append(tuple(row))
    return costs[0], costs[1]


def bayes_policy(laws: Tuple[Dict[tuple, float], Dict[tuple, float]],
                costs: Tuple[Tuple[float, float], Tuple[float, float]]):
    keys = set(laws[0]) | set(laws[1])
    total = 0.0
    actions = {}
    for key in keys:
        p0 = laws[0].get(key, 0.0)
        p1 = laws[1].get(key, 0.0)
        risk0 = 0.5 * (p0 * costs[0][0] + p1 * costs[1][0])
        risk1 = 0.5 * (p0 * costs[0][1] + p1 * costs[1][1])
        action = int(risk1 < risk0)
        actions[key] = action
        total += risk1 if action else risk0
    return total, actions


def bayes_policy_log(laws: Tuple[Dict[tuple, float], Dict[tuple, float]],
                     costs: Tuple[Tuple[float, float], Tuple[float, float]]):
    """Bayes policy using log masses, preserving decisions in tiny tails."""
    keys = set(laws[0]) | set(laws[1])
    total_terms = []
    actions = {}
    for key in keys:
        log_risk_q0 = math.log(0.5) + logaddexp(
            laws[0][key] + math.log(costs[0][0]),
            laws[1][key] + math.log(costs[1][0]),
        )
        log_risk_q1 = math.log(0.5) + logaddexp(
            laws[0][key] + math.log(costs[0][1]),
            laws[1][key] + math.log(costs[1][1]),
        )
        action = int(log_risk_q1 < log_risk_q0)
        actions[key] = action
        total_terms.append(math.exp(min(log_risk_q0, log_risk_q1)))
    return math.fsum(total_terms), actions


def action_disagreement_probability(laws_r, action_r, action_augmented, caps):
    disagreement = 0.0
    count = 0
    for h, law in enumerate(laws_r):
        for r, prob in law.items():
            a = tuple(min(x, c) for x, c in zip(r, caps, strict=True))
            if action_r[r] != action_augmented[(a, r[0])]:
                disagreement += 0.5 * prob
                count += 1
    return disagreement, count


def action_disagreement_from_r1(laws_r, action_r, action_r1):
    disagreement = 0.0
    for law in laws_r:
        for r, prob in law.items():
            if action_r[r] != action_r1[r[0]]:
                disagreement += 0.5 * prob
    return disagreement


def tv(left: Dict[Counts, float], right: Dict[Counts, float]) -> float:
    return 0.5 * sum(abs(left.get(k, 0.0) - right.get(k, 0.0)) for k in set(left) | set(right))


def probability(law: Dict[Counts, float], predicate) -> float:
    value = sum(prob for counts, prob in law.items() if predicate(counts))
    return min(1.0, max(0.0, value))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for regime, cfrac in CAPACITY_PROFILES.items():
        for t in HORIZONS:
            caps = tuple(round(x * t) for x in cfrac)
            if sum(caps) != t:
                raise AssertionError("capacity vector must have exact total T")
            laws_r = tuple(request_law(p, t) for p in WORLDS)
            laws_r_log = tuple(request_log_law(p, t) for p in WORLDS)
            laws_a = tuple(clipped_law(law, caps) for law in laws_r)
            laws_a_plus_r1 = tuple(clipped_law(law, caps, include_r1=True) for law in laws_r)
            laws_r1 = tuple(marginal_law(law, 0) for law in laws_r)
            laws_a_log = tuple(clipped_log_law(law, caps) for law in laws_r_log)
            laws_a_plus_r1_log = tuple(
                clipped_log_law(law, caps, include_r1=True) for law in laws_r_log
            )
            laws_r1_log = tuple(marginal_log_law(law, 0) for law in laws_r_log)
            for h, law in enumerate(laws_r):
                if abs(sum(law.values()) - 1.0) > 2e-10:
                    raise AssertionError(f"world {h}: multinomial law not normalized")
                if any(sum(r) != t for r in law):
                    raise AssertionError("request mass conservation failed")
            costs = action_costs(cfrac, caps, t)
            req_value, req_policy = bayes_policy_log(laws_r_log, costs)
            adm_value, _ = bayes_policy_log(laws_a_log, costs)
            augmented_value, augmented_policy = bayes_policy_log(laws_a_plus_r1_log, costs)
            r1_value, r1_policy = bayes_policy_log(laws_r1_log, costs)
            policy_mismatch, policy_mismatch_count = action_disagreement_probability(
                laws_r, req_policy, augmented_policy, caps
            )
            r1_policy_mismatch = action_disagreement_from_r1(laws_r, req_policy, r1_policy)
            if req_value > adm_value + 2e-10:
                raise AssertionError("requested observation violated Blackwell value ordering")
            if not (req_value <= augmented_value + 2e-10
                    and augmented_value <= adm_value + 2e-10):
                raise AssertionError("R -> (A,R1) -> A value ordering failed")
            if r1_value + 2e-10 < req_value:
                raise AssertionError("single-count signal has lower value than full R")
            exact_reconstruction_prob = []
            if regime == "one_saturated":
                for law in laws_r:
                    exact_reconstruction_prob.append(probability(
                        law,
                        lambda r: sum(x >= c for x, c in zip(r, caps, strict=True)) <= 1,
                    ))
                expected_gap_limit = 0.0
            else:
                for law in laws_r:
                    exact_reconstruction_prob.append(probability(
                        law,
                        lambda r: r[2] < caps[2],
                    ))
                expected_gap_limit = 0.25 * 0.06 / (2 * 0.40)
            tv_admitted = tv(laws_a[0], laws_a[1])
            tv_augmented = tv(laws_a_plus_r1[0], laws_a_plus_r1[1])
            tv_requested = tv(laws_r[0], laws_r[1])
            tv_r1 = tv(laws_r1[0], laws_r1[1])
            if not (tv_admitted <= tv_augmented + 2e-10
                    and tv_augmented <= tv_requested + 2e-10):
                raise AssertionError("R -> (A,R1) -> A total-variation ordering failed")
            rows.append({
                "regime": regime,
                "E": 3,
                "K": 1,
                "T": t,
                "C": ",".join(map(str, caps)),
                "request_value_two_target_class": req_value,
                "R1_only_value_two_target_class": r1_value,
                "admitted_plus_R1_value_two_target_class": augmented_value,
                "admitted_value_two_target_class": adm_value,
                "admitted_minus_requested_value": adm_value - req_value,
                "augmented_minus_requested_value": augmented_value - req_value,
                "R1_only_minus_requested_value": r1_value - req_value,
                "admitted_minus_augmented_value": adm_value - augmented_value,
                "full_R_vs_A_plus_R1_bayes_action_disagreement_probability": policy_mismatch,
                "full_R_vs_A_plus_R1_bayes_action_disagreement_count": policy_mismatch_count,
                "full_R_vs_R1_only_bayes_action_disagreement_probability": r1_policy_mismatch,
                "admitted_law_tv_between_worlds": tv_admitted,
                "admitted_plus_R1_law_tv_between_worlds": tv_augmented,
                "R1_only_law_tv_between_worlds": tv_r1,
                "requested_law_tv_between_worlds": tv_requested,
                "world0_reconstruction_event_probability": exact_reconstruction_prob[0],
                "world1_reconstruction_event_probability": exact_reconstruction_prob[1],
                "population_gap_prediction": expected_gap_limit,
                "population_cost_matrix": json.dumps(costs),
            })
    max_augmented_action_mismatch = max(
        row["full_R_vs_A_plus_R1_bayes_action_disagreement_probability"] for row in rows
    )
    if max_augmented_action_mismatch > 2e-10:
        raise AssertionError("(A,R1) did not reproduce the full-R Bayes action on the registered support")
    max_augmented_action_mismatch_count = max(
        row["full_R_vs_A_plus_R1_bayes_action_disagreement_count"] for row in rows
    )
    if max_augmented_action_mismatch_count != 0:
        raise AssertionError("(A,R1) differed from the full-R Bayes action on an enumerated count vector")
    csv_path = OUT / "exact_values.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "experiment": "exact one-vs-two-saturated Top-1 value audit",
        "protocol_sha256": sha256(PROTOCOL),
        "runner_sha256": sha256(Path(__file__)),
        "rows": len(rows),
        "horizons": list(HORIZONS),
        "worlds": [list(x) for x in WORLDS],
        "capacity_profiles": {k: list(v) for k, v in CAPACITY_PROFILES.items()},
        "registered_action_class": "two pressures that individually route a world to C/T",
        "exact_multinomial_enumeration": True,
        "max_augmented_full_R_bayes_value_difference": max(
            abs(row["admitted_plus_R1_value_two_target_class"] - row["request_value_two_target_class"])
            for row in rows
        ),
        "max_full_R_vs_A_plus_R1_action_disagreement_probability": max(
            row["full_R_vs_A_plus_R1_bayes_action_disagreement_probability"]
            for row in rows
        ),
        "max_full_R_vs_A_plus_R1_action_disagreement_count": max_augmented_action_mismatch_count,
        "max_full_R_vs_R1_only_action_disagreement_probability": max(
            row["full_R_vs_R1_only_bayes_action_disagreement_probability"]
            for row in rows
        ),
        "csv_sha256": sha256(csv_path),
        "checks": {
            "all_world_laws_normalized": True,
            "all_request_vectors_mass_conserving": True,
            "all_capacity_vectors_exact_total": True,
            "requested_value_no_greater_than_admitted_value": True,
            "signal_value_ordering_R_ge_A_plus_R1_ge_A": True,
            "signal_TV_ordering_R_ge_A_plus_R1_ge_A": True,
            "full_R_value_no_greater_than_R1_value": True,
            "full_R_and_A_plus_R1_bayes_actions_agree_on_full_support": max_augmented_action_mismatch <= 2e-10,
            "full_R_and_A_plus_R1_actions_match_all_count_vectors": max_augmented_action_mismatch_count == 0,
            "one_saturation_population_gap_prediction": 0.0,
            "two_saturation_population_gap_prediction": 0.01875,
        },
    }
    json_path = OUT / "summary.json"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
