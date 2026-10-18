# Locked fresh-batch protocol: multi-low-capacity Top-K population theorem

**Date:** 2026-10-18  
**Parent result:** [`topk_multilow_population_overflow_theorem_2026-10-17.md`](topk_multilow_population_overflow_theorem_2026-10-17.md)  
**Purpose:** audit its fixed-horizon population limit with independent batches at each update. This is a validation of the existing mathematical line, not a new controller or an infinite-horizon claim.

## Hypothesis and estimand

For every registered feasible `(E,K,m)` family and fixed horizon `H`, the paired finite-batch admitted-minus-requested cumulative overflow per token converges as `T` grows to

```text
sum_{t=0}^{H-1} (E-m) * (K/E - h(x_t)),
```

where `x_0=0` and `x_(t+1)=x_t + eta/K * (h(x_t)-c_low)` is computed from the exact Gumbel Top-K population probabilities. Each training step uses a newly sampled independent affinity batch. Within each replicate and round, all controller arms use the same affinity batch (common random numbers); arms retain their own pressure states.

The primary endpoint is the replicate-level paired cumulative gap at `H=32`. All six registered horizons are reported. No test requires every finite-batch replicate to have a positive gap; finite sampling noise is expected. The audit asks whether the cell means approach the theorem's finite-horizon prediction as batch size increases.

## Locked setup

- Router: hard Top-K on iid standard Gumbel affinities, scores `a-q`, stable descending sort with lower expert index breaking exact ties.
- Admission: independent per-expert clipping, `A_e=min(R_e,C_e)`.
- Feedback: requested counts `R`, admitted counts `A`, and no-update diagnostic.
- Update: `q_next=P0(q + eta*(signal/(K*T)-1/E))`, `eta=0.5`, zero decay, `gamma=1`.
- Freshness: generate a new independent `T x E` Gumbel matrix at every step. Reuse that step's matrix across the three arms only.
- Capacity fractions: the same `r=1/(4E)`, `c_low=K/E-r`, and `c_high=K/E + m*r/(E-m)` construction as the parent protocol. Capacities are integer and sum exactly to `K*T`.
- Families: all 32 feasible `(E,K,m)` families in the parent protocol, for `E in {4,6}`. Keep its explicit hypothesis-based exclusions.
- Batch sizes: `T in {1440,2880,5760}`; 12 independent paired replicates per family and size.
- Horizons: `H in {1,2,4,8,16,32}`. Use a new seed schedule with base `20261018`; derive each family/size/replicate seed deterministically and record it.

## Registered analysis

For every family, batch size, and horizon, report all 12 paired replicate gaps, their mean, two-sided 95% Student-t interval, exact population prediction, and mean-minus-prediction residual. Also report requested, admitted, and no-update overflow separately, high-minus-low pressure separation, and the number of positive paired gaps. Aggregate summaries may be shown after the complete cell table; no family may be dropped based on its result.

Use the paired interval descriptively. Do not call the 95% intervals a simultaneous familywise guarantee. Do not infer a fixed-`T` infinite-horizon law from this experiment.

## Required controls and invalidation rules

1. At every arm and every step, `sum(R)=K*T`, `A=min(R,C)`, and `sum(R-A)=K*T-sum(A)`.
2. Exact-total integer capacities match the registered fractions for every cell.
3. Independently recomputed population response starts at `K/E`, is strictly decreasing on `[0,x_*]`, and has residual `|h(x_*)-c_low|<=2e-12`.
4. Population prediction is zero at `H=1`, positive for later horizons, and converges numerically to `(E-m)r` per round.
5. A synthetic exact cutoff-tie control confirms lower-index tie resolution. Any cutoff ties in random batches are resolved by the same stable rule and counted.
6. A no-clipping fresh-batch control gives pathwise equal requested and admitted pressure/count trajectories.
7. Re-running the locked script produces byte-identical plant data and summary on the same NumPy/SciPy versions.

Any failed control invalidates the run and must be repaired before interpreting outcomes. Do not change family membership, capacities, seeds, horizons, update rate, or endpoint after seeing results.

## Scope

The parent theorem covers a symmetric two-capacity population family and one proportional controller. The fresh-batch proposition covers fixed `H` as `T` grows. Neither this protocol nor its results establish arbitrary capacity profiles, controller optimality, finite-`T` infinite-horizon convergence, value separation from a general polyhedral-testing benchmark, measured system cost, or trained-model quality.
