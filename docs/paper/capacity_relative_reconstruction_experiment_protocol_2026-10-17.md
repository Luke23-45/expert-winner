# Locked experiment: does admitted telemetry suffice after target correction?

**Question.** In the canonical per-expert clipping model, can an admitted-only
controller reproduce requested-feedback capacity-relative control when only
one expert is saturated, and does capacity-relative feedback remove the
overflow behavior caused by the uniform target in the one-short family?

## Model and fixed design

- `E=4`, `K=1`, iid standard Gumbel affinities, one static affinity matrix
  reused by all controller arms and all rounds.
- `T in {2304,9216}`, 50 independent seeded matrices at each T, fixed seed
  formula as in the runner.
- Exact-total capacities `C_1=T/8`, `C_2=C_3=C_4=7T/24`; target
  `mu=(1/4,...,1/4)`, gain `gamma=1`, zero leak, pressure initialized to 0,
  `eta=1`, and horizon `H=8`.
- Hard Top-1 routing uses stable descending score order; canonical admission
  is exactly `A=min(R,C)`. No score-ranked or shared-device admission is used.

## Registered controller arms

All pressure updates use the gauge projection from the canonical formal
definition.

1. `R-uniform`: `R/(K*T)-mu` (the earlier reference arm).
2. `A-uniform`: `A/(K*T)-mu` (the earlier admitted arm).
3. `R-capacity`: `P_0((R-C)/(K*T))`, the formal capacity-relative requested
   controller.
4. `A-capacity-naive`: `P_0((A-C)/(K*T))`; this intentionally uses admitted
   counts directly without reconstructing clipped mass.
5. `A-capacity-reconstructed`: from `A,C,K,T`, recover `R` exactly when zero
   or one coordinate is saturated, then use the same `R-capacity` update.
   If two or more coordinates are saturated, freeze pressure for that step;
   record the recovery failure. This fallback is fixed in advance and is not
   used to claim equivalence outside the proved one-saturation regime.

## Outcomes and controls

Primary outcomes are (i) whether `A-capacity-reconstructed` exactly matches
the `R-capacity` pressure and route trajectory, (ii) number of steps where
the admitted vector has at most one saturated expert, (iii) cumulative
overflow per token over eight rounds, and (iv) paired differences versus
`R-uniform` and `A-uniform`. Report each seed and paired means with 95%
paired t intervals; do not exclude any seed.

At each step assert `sum R=K*T`, `A=min(R,C)`, `sum J=sum(R-A)`, route load
`R_e<=T`, and reconstruction equality whenever the saturation count is at
most one. On every plant, `R-capacity` and reconstructed-admitted-capacity
must have identical pressure and routes up to the first step with two or
more saturated coordinates. The no-clipping control `C_e=T` must give
identical requested/admitted counts and updates for each corresponding
feedback formula.

The population reference is exact for Top-1 Gumbel:
`Q(x)=1/(1+3*exp(x))`, short-capacity fraction `1/8`, equilibrium
`x*=log(7/3)`. With `eta=1`, the requested capacity-relative recurrence is
`x_next=x+(4/3)*(Q(x)-1/8)`; direct admitted capacity-relative feedback has
`x_next=x+(1/3)*(Q(x)-1/8)` while exactly one expert is saturated. Both
recurrences stay below `x*` and converge to it. Compare the finite-batch
averages to these population trajectories, while labeling static-batch
reuse as the finite experiment design.

## Interpretation boundary

This experiment tests a corrected, already formalized controller target and
the exact single-saturation reconstruction proposition. It is not evidence
for a universal controller ranking, a real communication/latency price,
trained-model quality, or separation from the finite outcome-map benchmark.
The finite experiment supports the fixed-horizon theorem only; it does not
prove infinite-horizon convergence at fixed T.
