# Locked experiment: saturation multiplicity × target × feedback signal

## Question and estimand

This experiment tests the existing target-by-signal population theorem for
`m` low-capacity experts under the canonical hard Top-K router, independent
per-expert clipping, and proportional pressure update. It extends the prior
one-low-expert target factorial and the uniform-target multi-low study; it
does not change the model or introduce a new research direction.

The primary outcome is paired cumulative overflow per token batch through
each horizon. The registered factors are:

- saturation multiplicity `m ∈ {1,2,3}` at fixed `E=4,K=2`;
- target: uniform or exactly capacity-matched;
- signal: requested counts or admitted counts;
- temporal regime: static affinity batch or fresh iid batch each step.

The five arms are the four target × signal combinations plus no feedback.
The primary paired contrasts are admitted-minus-requested within each target,
the capacity-target admitted arm versus no feedback, and the target-by-signal
interaction. These are overflow comparisons for the specified direct update;
they are not optimal-policy or telemetry-cost comparisons.

## Locked design

- `E=4`, `K=2`, iid standard Gumbel affinities, stable deterministic Top-K.
- `m ∈ {1,2,3}` low-capacity experts and `n=E-m` high-capacity experts.
- `p=K/E=1/2`, `r=1/16`, `c_L=p-r=7/16`,
  `c_H=p+m*r/n`; hence `m*c_L+n*c_H=K` exactly.
- `T ∈ {2304,9216}`; all capacities are exact integers and sum to `K*T`.
- 12 paired seeds per `(m,T)`, horizons `H ∈ {1,2,4,8,16,32,64}`.
- Static regime reuses the first batch. Fresh regime draws an independent
  batch each step. All four arms within a plant receive the same batch at
  each step; initial pressure is zero in every arm.
- `eta=0.5`, `gamma=1`, `delta=0`; projection subtracts the minimum pressure
  coordinate. This lies below the common sufficient population gain bound
  `eta ≤ m*K/(E*L_h)` using the standard-Gumbel bound `L_h ≤ m/e`.
- Uniform target is `mu_e=1/E`; capacity target is `mu=C/(K*T)`.

## Predictions and analysis

The runner computes the one-dimensional Plackett–Luce population response
`h(x)` by dynamic programming, finds the roots `h(x)=c_H` and `h(x)=c_L`,
and evaluates all four deterministic recurrences from the theorem. The
primary finite-batch summaries are means, paired 95% t intervals, medians,
and the fraction of paired plants with positive contrasts. Population
predictions are reported alongside the finite-batch outcomes, not substituted
for them.

The prespecified theorem checks are: (i) uniform-target requested feedback
remains at zero pressure with overflow `m*r`; (ii) uniform-target admitted
feedback approaches overflow `E*r`; (iii) capacity-target requested and
admitted population recurrences approach zero overflow; and (iv) under the
capacity target, requested feedback has no greater population overflow at
each round and strictly lower cumulative overflow for `H≥2`.

## Required controls

At every simulated step verify `sum(R)=K*T`, `A=min(R,C)`, and
`sum(R-A)=sum(max(R-C,0))`. All arms must have identical first-step cost.
Any exact Top-K cutoff tie invalidates the run and is reported; ties are not
silently discarded. A no-clipping control sets every capacity to `T` and
uses the uniform target for both signals; paired requested/admitted pressure
trajectories must be bit-identical.

Seeds, protocol/script hashes, raw-row hash, cell-summary hash, and contrast
hash are recorded. The experiment is a controlled synthetic validation of
the stated population dynamics. It does not establish finite-batch
infinite-horizon behavior, production prevalence, model-quality benefit,
measured collective cost, or a separation from adaptive-testing benchmarks.
