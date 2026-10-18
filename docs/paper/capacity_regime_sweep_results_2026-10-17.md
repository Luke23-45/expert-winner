# Capacity-regime sweep: results and theorem boundary

**Run date:** 2026-10-17  
**Base revision:** `e1648512e22844f4d8e892577dfc011f83ac307a` (worktree was dirty)  
**Script SHA-256:** `69d9979e0464394826224771b5a3e433f1b40dd3b59751f386124754b409090a`  
**Protocol SHA-256:** `26ecda40fddb8a48995e72d289b811d47b0efbf14d73be5c4bc2562ba86d955a`  
**Protocol:** [`admitted_feedback_capacity_sweep_protocol.md`](admitted_feedback_capacity_sweep_protocol.md)  
**Artifacts:** [`summary.json`](../../results/capacity_regime_sweep/summary.json), [`trajectories.csv`](../../results/capacity_regime_sweep/trajectories.csv)

## Design

The experiment uses the established fixed Top-2 ring-pair plant with `E=8`,
`T=128`, 20 paired score-perturbation seeds, 120 updates, fixed sign-bias
step `0.025`, and zero initial bias. It compares requested, admitted, and
no-feedback arms at uniform per-expert capacities `C=24,28,32,36`, matching
capacity factors `0.75,0.875,1.0,1.125`. Score-ranked and position-ranked
retention are paired controls under the same per-expert admission rule.

This simulator uses the signed expert-bias controller, represented in the
zero-mean gauge. It is routing-equivalent to the uncentered signed update
when no clipping or other non-gauge-invariant operation is applied. It is a
separate controller from the proportional gauge-pressure variants `(R)` and
`(A)` in the canonical formal model. The seeded variants are perturbations of
one hand-specified plant, not a sample of MoE models or workloads.

## Exact controls and invariants

All six exact checks recorded in `summary.json` passed:

- score-ranked and position-ranked retention produced identical requested,
  admitted, feedback, bias, and overflow trajectories at every capacity;
- at `C=24`, the admitted-feedback arm stayed globally saturated with
  `A=C`, zero feedback and bias, and overflow `KT-EC=64` for all 120 steps;
- for uniform `C`, any two simultaneously saturated experts received the
  same signed update and retained their pairwise bias gap (checked to
  tolerance `1e-12`);
- global saturation was absorbing for admitted feedback under this fixed
  affinity batch: after entry, routing and bias stayed unchanged;
- in the no-admission control, requested and admitted sensors were identical;
- every step satisfied `sum(R)=KT`, `A_e=min(R_e,C)`, and exact overflow
  accounting.

The exact saturated-set result has a short proof. With
`u_e=sign(mean(A)-A_e)` and `b^+=P_0(b+alpha*u)`, if `e,f` are both
saturated under a uniform cap then `A_e=A_f=C`, hence `u_e=u_f`; subtraction
of the two updates gives `b^+_e-b^+_f=b_e-b_f`. If all experts are saturated,
`A=C*1`, so `u=0` and the zero-mean bias state is fixed. With static
affinities the router therefore repeats the same requests, making this an
absorbing state. If `EC<=KT`, it attains the per-batch overflow lower bound
`KT-EC`. This is a signed-bias result under the stated conditions; it does
not imply divergence or a general partial-saturation failure.

## Final-horizon outcomes

`request L1` is `||R-(KT/E)1||_1`; overflow is `sum_e(R_e-A_e)`.
Entries are means over 20 paired seeds.

| Capacity | Feedback | Request L1 | Overflow | Saturated experts at step 120 | Bias L2 |
|---:|---|---:|---:|---:|---:|
| 24 | admitted | 32.00 | 64.00 | 8.00 | 0.000 |
| 24 | none | 32.00 | 64.00 | 8.00 | 0.000 |
| 24 | requested | 30.90 | 65.25 | 7.90 | 4.659 |
| 28 | admitted | 16.60 | 32.00 | 8.00 | 4.613 |
| 28 | none | 32.00 | 38.00 | 6.00 | 0.000 |
| 28 | requested | 30.90 | 38.15 | 6.05 | 4.659 |
| 32 | admitted | 31.30 | 15.65 | 4.35 | 4.710 |
| 32 | none | 32.00 | 16.00 | 5.00 | 0.000 |
| 32 | requested | 30.90 | 15.45 | 5.20 | 4.659 |
| 36 | admitted | 25.40 | 5.95 | 1.25 | 5.166 |
| 36 | none | 32.00 | 4.00 | 3.00 | 0.000 |
| 36 | requested | 30.90 | 4.55 | 2.40 | 4.659 |

Paired comparisons against no feedback at the final step:

| Capacity | Feedback | Mean change in request L1 | Seeds with lower request L1 | Mean change in overflow | Seeds with lower overflow |
|---:|---|---:|---:|---:|---:|
| 24 | admitted | 0.00 | 0/20 | 0.00 | 0/20 |
| 24 | requested | -1.10 | 10/20 | +1.25 | 0/20 |
| 28 | admitted | -15.40 | 20/20 | -6.00 | 20/20 |
| 28 | requested | -1.10 | 10/20 | +0.15 | 9/20 |
| 32 | admitted | -0.70 | 16/20 | -0.35 | 16/20 |
| 32 | requested | -1.10 | 10/20 | -0.55 | 10/20 |
| 36 | admitted | -6.60 | 18/20 | +1.95 | 2/20 |
| 36 | requested | -1.10 | 10/20 | +0.55 | 10/20 |

Negative means lower. These paired counts are descriptive for this constructed
plant, not population inference. Feedback-active arms first changed routing at
step 76 in all seeds. No-feedback arms never changed routing.

## Post-run cumulative-overflow diagnostic

Cumulative overflow was **not** designated as the primary endpoint in the
original protocol. This is a transparent post-run calculation from the 120
saved outcomes, useful for selecting a future primary metric but not
preregistered confirmatory evidence.

**Correction:** an earlier version of this diagnostic counted both the
score-ranked and position-ranked retention rows. The experiment had already
verified that these rows are identical under independent per-expert capacity,
so including both doubled the cumulative totals. The table below is recomputed
from one representative (`score`) row per seed and capacity; paired seed
counts are also recomputed from that same set. The calculation and duplicate-
row assertions are reproducible with
[`audit_capacity_sweep_cumulative.py`](../../scripts/audit_capacity_sweep_cumulative.py);
its machine-readable output is
[`cumulative_overflow_audit.json`](../../results/capacity_regime_sweep/cumulative_overflow_audit.json).

| Capacity | Feedback | Mean cumulative overflow | Change vs no feedback | Seeds with lower / equal / higher cumulative overflow |
|---:|---|---:|---:|---:|
| 24 | none | 7,680.0 | 0.0 | reference |
| 24 | admitted | 7,680.0 | 0.0 | 0 / 20 / 0 |
| 24 | requested | 7,867.9 | +187.9 | 0 / 0 / 20 |
| 28 | none | 4,560.0 | 0.0 | reference |
| 28 | admitted | 4,340.5 | -219.5 | 20 / 0 / 0 |
| 28 | requested | 4,695.25 | +135.25 | 0 / 0 / 20 |
| 32 | none | 1,920.0 | 0.0 | reference |
| 32 | admitted | 2,258.4 | +338.4 | 0 / 0 / 20 |
| 32 | requested | 2,032.5 | +112.5 | 3 / 0 / 17 |
| 36 | none | 480.0 | 0.0 | reference |
| 36 | admitted | 1,117.25 | +637.25 | 0 / 0 / 20 |
| 36 | requested | 662.05 | +182.05 | 0 / 0 / 20 |

At `C=28`, admitted feedback first reached global saturation at steps
`[81,78,78,78,78,78,78,78,78,84,78,78,78,78,77,78,78,78,78,78]` across
the 20 seeds. Requested feedback and no feedback never entered global
saturation during the horizon. After admitted feedback entered it, each later
batch paid overflow exactly `KT-EC=32`, the capacity lower bound. At `C=24`
the admitted arm starts in this absorbing state; at `C=32` and `C=36`, no arm
entered it within 120 steps.

## Post-hoc exact replay of the `C=28` admitted arm

[`audit_capacity28_exact_replay.py`](../../scripts/audit_capacity28_exact_replay.py)
reconstructs the 20 seeded `float64` affinity matrices, treats every stored
affinity entry as its exact binary rational value, and replays the signed-bias
controller with exact `alpha=1/40`. It compares every one of the 120 requested
and admitted count vectors for every seed against the saved sweep CSV. **All
2,400 per-seed steps match exactly.** This is a post-hoc numerical audit; it
does not change the original protocol's status or primary endpoint.

The exact replay shows:

- all seeds have the same request-count path through states 0--75;
- all first change routes at state 76, but all 20 complete trajectories
  thereafter differ;
- all 20 reach global saturation between states 77 and 84 (17 at 78; one
  each at 77, 81, and 84), only 1--8 updates after the first route change;
- the minimum Top-2 cutoff margin over all 20 paths and 120 steps is exactly
  `64867570349/22517998136852480` (about `2.88e-6`);
- exact cumulative overflow over 120 updates ranges from 4,322 to 4,392
  across seeds.

The positive minimum cutoff margin gives a local robustness certificate for
each replayed plant. If every affinity entry is perturbed by less than half
the common minimum margin, each Top-2 cutoff remains strict at every step;
inductively, the requests, controller updates, and full 120-step trajectories
remain unchanged. This is a very small neighborhood around these fixed
plants, not a population-level robustness claim. Full per-step certificates
and source hashes are in
[`capacity28_exact_replay.json`](../../results/capacity_regime_sweep/capacity28_exact_replay.json).

### Exact paired replay of all three feedback arms

[`audit_capacity28_all_signal_replay.py`](../../scripts/audit_capacity28_all_signal_replay.py)
extends the rational replay to requested feedback and no feedback. It checks
all 7,200 seed-arm steps against the saved float64 sweep; **every requested
and admitted count vector matches**. Across the same 20 plants, admitted
feedback has lower cumulative overflow at `H=120` than both requested and no
feedback in every seed. The exact means are `8681/2` (admitted), `18781/4`
(requested), and `4560` (none); the mean admitted savings are `1419/4` against
requested and `439/2` against no feedback.

The minimum Top-2 cutoff margin over all three arms, all seeds, and all 120
steps is the same positive rational margin reported above. Therefore, for
each of these 20 affinity matrices, any fixed entrywise perturbation smaller
than half that margin preserves all three trajectories through `H=120`, by
induction on the routing decisions. The finite-horizon paired advantage is
thus locally robust around each of the 20 matrices. This does not prove the
requested-feedback comparison for horizons beyond 120, or support a claim
about a broader workload population. Full records are in
[`capacity28_all_signal_replay.json`](../../results/capacity_regime_sweep/capacity28_all_signal_replay.json).

## Interpretation and next proof target

This result rejects both blanket narratives: admitted feedback is not always
uninformative (the `C=28` partial-saturation trajectory reaches the
capacity-optimal absorbing region), and it is not uniformly beneficial (at
`C=32` and `C=36`, cumulative overflow is higher than with no feedback for
all 20 seeds). Requested feedback is not uniformly better either. The
mechanism depends on capacity regime and trajectory.

The next proof target is specific: for a parameterized Top-K affinity family,
derive conditions for the signed admitted-count bias controller to enter the
absorbing globally saturated set, and bound the entry time and finite-horizon
cumulative overflow against the same signed controller on requested counts
and against no feedback. The exact replay rules out a single common post-step-
76 route path: the proof must handle seed-dependent switching among saturated
faces. State capacities, initial pressure and margins, step size, horizon,
and quantifiers. Then test the family theorem against the independently
defined outcome-cost testing benchmark. The current E-world theorem does not
prove this partially saturated signed-bias result or escape the adaptive-
testing reduction. The experiment does not justify training or a top-
conference novelty claim by itself.
