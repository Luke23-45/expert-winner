# Results: rejected-load identity at first route divergence

**Status:** completed exact-rational audit of the common-prefix lemma; the
cross-tabulation with cumulative overflow is post-hoc and descriptive.

## Exact audit

The audit reconstructs the 40 affinity plants from the preregistered bridge
experiment and checks every expert-pair pressure-difference identity at every
shared-route state, including the first state where routes split. It then
checks that every observed first divergence has a selected-versus-unselected
Top-$K$ score comparison with nonpositive margin under the requested pressure.
All checks passed for all 160 plant/capacity pairs.

| Capacity profile | Plants with a route split by state 119 | No split by state 119 | First split state, mean / median / range, among those that split |
|---|---:|---:|---:|
| No clipping `(12,12,12,12)` | 0 | 40 | — |
| Exact-total uniform `(6,6,6,6)` | 28 | 12 | `31.64 / 4 / [1,100]` |
| Exact-total heterogeneous `(2,4,8,10)` | 38 | 2 | `12.5 / 1 / [1,80]` |
| Aggregate shortage `(3,3,3,3)` | 34 | 6 | `8.59 / 1 / [1,80]` |

The mean split time is strongly right-skewed in every clipping regime: the
median is one or four states. Therefore report the full per-plant states in
[`first_divergence.csv`](../../results/rejected_load_first_divergence/first_divergence.csv),
not the mean alone.

## Post-hoc join to cumulative overflow

Joining each split time to the bridge experiment's already-computed
`D = overflow_admitted - overflow_requested` gives a useful warning about the
cost endpoint:

- In the uniform exact-total profile, all 12 plants with no split had `D=0`.
  Among 28 plants that split, `D` ranged from `-2` to `141` (2 negative, 13
  zero, 13 positive). Route divergence is necessary for the signals to
  separate, but does not determine which signal has lower cost.
- In the heterogeneous exact-total profile, both no-split plants had `D=0`.
  All 38 plants that split had `D>0`, ranging from 32 to 399. In this
  constructed 40-plant set, requested feedback therefore had lower cumulative
  overflow whenever the trajectories split; this is an observed property of
  this generator, controller, gain, initialization, and horizon, not a proven
  family theorem.
- In aggregate shortage, all 40 plants had `D=0`, including all 34 plants
  whose route sets split. Here `sum(C)=12<KT=24`; when every expert remains
  saturated, the overflow is the fixed aggregate shortage `KT-sum(C)=12` per
  step. Route and pressure trajectories may differ without affecting this
  overflow endpoint.

This join is post-hoc and does not amend the fixed protocol. It gives a precise
lead for a theorem: to predict an overflow benefit, the signal-induced route
split must interact with the capacity-feasible allocation, not merely occur.
The lemma supplies an exact condition for the split; it does not yet describe
the post-split dynamics or predict the allocation cost. The aggregate-shortage
case is an exact negative control for any claim that pressure divergence alone
implies lower overflow.

## Artifacts and limits

Run `python scripts/audit_rejected_load_first_divergence.py`. The machine
summary is
[`summary.json`](../../results/rejected_load_first_divergence/summary.json).
The audit is exact for the 40 declared static plants and four capacity
profiles. It does not establish real-router prevalence, a universal signal
ranking, model-quality gains, telemetry cost, or a separation from the
polyhedral outcome-map benchmark.
