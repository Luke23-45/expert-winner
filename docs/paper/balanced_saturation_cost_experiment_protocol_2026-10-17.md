# Controlled synthetic experiment: balanced-request saturation cost theorem

**Status:** protocol fixed before execution. This experiment tests a
corollary of the existing canonical proportional-pressure and clipping
model; it does not introduce another admission or controller model.

## Question and prediction

For a balanced initial Top-K request vector, uniform target, and capacities
strictly below the balanced request count, does admitted feedback leave the
minimum aggregate-shortage overflow set by the theorem's arrangement bound,
while requested feedback and no feedback remain at that minimum?

The theorem is
[`balanced_saturation_cost_theorem_2026-10-17.md`](balanced_saturation_cost_theorem_2026-10-17.md).
It predicts, for each admissible plant, exact zero cumulative gap through
state `tau-1`, positive gap beginning at state `tau`, and `tau<=N_sep`.
No controller ranking other than this theorem's declared conditions is
tested or inferred.

## Plant generation

- `E in {3,4,5,6}`; test `K in {1, floor(E/2), E-1}`, deduplicated.
- Let `m=E+2`, `T=m*binom(E,K)`, and `n=K*T/E=m*binom(E-1,K-1)`.
- Generate one token for each K-subset, repeat each subset `m` times, and
  shuffle the token order with the registered plant seed. This gives exactly
  `R_e(0)=n` for every expert.
- For experts ranked `r=0,...,E-1` in a registered seeded permutation, set
  `C_e=n-(E-1-r)`. Thus every capacity is positive and at most `n`, total
  capacity is strictly below `KT`, and the `K`th and `(K+1)`st sorted
  capacities have a strict gap. The permutation randomizes which expert
  labels carry the low/high capacities while preserving the theorem's
  hypotheses.
- For each token's designated K-subset, draw selected affinities in
  `[1,1.01)` and unselected affinities in `[0,0.01)`, using seeded integer
  numerators over `100000`. These margins make the initial K-subset exact.
  All subsequent score comparisons and dynamics use exact rational
  arithmetic. Ties use lower expert index.
- Use ten registered plants per `(E,K)` cell. The ten seeds are fixed in the
  runner before results are inspected. Failed theorem preconditions are
  assertion failures, not exclusion criteria.

## Controller arms and controls

All arms share the exact same affinity matrix, initial pressure `q=0`,
`gamma=1`, `eta=1`, `delta=0`, and uniform target.

1. **Admitted:** canonical update from `A=min(R,C)`.
2. **Requested:** canonical update from `R`.
3. **No feedback:** hold `q=0`.
4. **No-clipping control:** replay the same plant with `C_e=T`; requested
   and admitted trajectories must be identical.

Run each clipped plant to `H=N_sep+2` states. Save each state including
`R,A,J,q`, the saturation indicator, and the first route-change/exiting
state. Do not tune `eta`, capacities, affinity distributions, or horizons
after seeing the results.

## Primary endpoint and exact assertions

Primary endpoint: paired cumulative-overflow difference
`sum_t J_A(t)-sum_t J_R(t)` through every prefix horizon, plus `tau_A` and
the theorem's `N_sep`.

For every plant and state, assert exactly:

1. `sum_e R_e=K*T`, `A=min(R,C)`, and `J=sum_e(R_e-A_e)`.
2. Initial requests equal `n` in every coordinate, and the capacities have
   the declared positivity, shortage, and strict slope-gap properties.
3. Requested feedback and no feedback stay at `q=0` and have per-state
   overflow `D=KT-sum C`.
4. While the admitted arm is globally saturated, its pressure equals the
   exact constant-feedback line and its overflow equals `D`.
5. `tau_A<=N_sep`; at state `tau_A`, `J_A-D=sum_e(C_e-A_e)>0`.
6. For every state, `J_A-D=sum_e(C_e-A_e)>=0`; every cumulative gap is
   nonnegative and is positive by prefix `N_sep+1`.
7. The no-clipping control has identical requested/admitted pressure paths
   and counts at every state.

Publish every exact affinity matrix, individual plant summary, all per-state
trajectories, cell summaries, script/protocol hashes, and a deterministic
rerun check. No significance testing is required: the registered endpoint is
an exact finite-plant implication with deterministic arithmetic.

## Claim boundary

This is a controlled synthetic validation of the theorem's cost consequence
over a parameterized set of finite Top-K plants. It is not a random workload
sample, does not establish prevalence, and does not measure training loss,
throughput, communication cost, or fixed-`T` fresh-batch stability. The
finite-plant benchmark embedding remains exact. The experiment must be
reported as theorem validation, not novelty clearance.
