# Locked experiment: does a capacity-matched target remove the admitted-feedback overflow gap?

## Hypothesis and estimand

This experiment tests the population theorem in
[`capacity_matched_target_theorem_2026-10-18.md`](capacity_matched_target_theorem_2026-10-18.md)
and separates target mismatch from signal choice in the existing one-short-
capacity Top-K model.

Primary estimand: paired cumulative overflow per token-batch through each
registered horizon, for each of four controller arms:

1. requested signal with uniform target (`R/U`),
2. admitted signal with uniform target (`A/U`),
3. requested signal with capacity-matched target (`R/C`),
4. admitted signal with capacity-matched target (`A/C`).

No-feedback at the initial pressure is the fifth reference arm. The paired
contrasts are `A/U - R/U`, `A/C - R/C`, `A/C - no-feedback`, and the target
interaction `(A/C-A/U)-(R/C-R/U)`. These are overflow outcomes; no system
latency or telemetry-cost quantity is inferred.

## Locked design

- `E=4`, `K in {1,2,3}`, iid standard Gumbel affinity rows.
- Exact-total capacities `C_s/T=K/4-r`, `C_r/T=K/4+r/3`,
  `r=1/48`, with integer capacities for every registered batch size.
- `T in {2304,9216}`; 12 paired affinity seeds per `(K,T)`.
- Horizons `H in {1,2,4,8,16,32,64}`.
- Fresh regime: draw a new independent affinity batch each update. Static
  regime: reuse the initial batch at every update. Initial batch is paired
  across regimes, and within each plant every arm receives the same batch at
  each step.
- Gain `eta=0.8*K*(E-1)/(E*L_F)`, with
  `L_F=(1/e)*(E-1)*binom(E-2,K-1)`. This is below the common population
  non-overshoot bound for both capacity-target recurrences.
- Every arm starts at zero pressure. Targets are exactly
  `mu_U=(1/4,...,1/4)` and `mu_C=C/(K*T)`.
- Router is hard Top-K with stable deterministic ordering; any exact
  boundary tie invalidates that replicate and is reported, not silently
  discarded.

## Primary analysis

For each arm, report cumulative overflow / `T` at each horizon, paired mean,
95% paired-t interval, median, and fraction of paired plants in which each
contrast is positive. Also report cumulative target deviation, pressure
norm, and fraction of saturated experts as secondary diagnostics.

Compare the results with two deterministic symmetric-pressure predictions:
the population recurrences in the theorem and the exact finite-`T` expected-
count recurrences. The finite-`T` recurrence is a comparator for the mean
field, not asserted equal to the expected stochastic trajectory.

## Required controls

- At every step, verify `sum R=K*T`, `A=min(R,C)`, and
  `sum(R-A)=sum(max(R-C,0))`.
- All arms share the same initial overflow.
- No-clipping control: set all capacities to `T` and explicitly set both
  targets to `mu_U`; then `R=A`, and requested/admitted trajectories must be
  bit-identical for paired data. Do not use `C/(K*T)` as a target in this
  control because those capacities are deliberately not exact-total.
- Verify the first population update from the closed-form/finite-count
  equations before interpreting cumulative outcomes.
- Re-run the locked seeds; report file hashes.

## Decision rules

1. The population-theorem check passes only if the implemented recurrences
   match their analytic update formulas and converge to the stated root on
   the registered grid.
2. The target-mismatch diagnosis is supported only if `A/C` removes the
   positive long-run overflow predicted for `A/U`; finite-batch deviations
   must be reported with their intervals and may not be described as proof
   of the population theorem.
3. If `A/C` fails to track the capacity-target population prediction as `T`
   grows, do not claim finite-batch convergence from this study.
4. Regardless of the outcome, this experiment does not establish a measured
   observation cost, trained-model quality, prevalence in production, or a
   separation from the independent outcome-map benchmark.
