# Controlled Top-K swapped-saturation experiment: protocol

## Question

Does the proved two-world value mechanism extend across expert count and
Top-K depth under the same per-expert clipping model: requested counts
identify which of two overloaded experts is favored, while admitted counts
clip both and retain only the shared unsaturated counts?

This is a controlled synthetic audit of
[`topk_swapped_saturation_value_theorem_2026-10-17.md`](topk_swapped_saturation_value_theorem_2026-10-17.md).
It is not a real-router reproduction, a trained-model experiment, or a
novelty test against adaptive-testing theory.

## Locked design

- Expert counts `E in {3,4,6,8}`.
- For each `E`, test the deduplicated values `K in {1,floor(E/2),E-1}`.
- Gumbel-Top-K scores use base weights `(5/4,1,...,1)` in world 0 and
  `(1,5/4,1,...,1)` in world 1. World 1 is exactly the expert-1/expert-2
  label swap of world 0.
- Let `u=K/E` and `delta=min(u,1-u)/4`. Set
  `c_1=c_2=u-delta` and `c_j=u+2*delta/(E-2)` for `j>=3`. This is an
  exact-total capacity profile. The runner must stop with an error if the
  computed inclusion margins fail the theorem's strict inequalities.
- Batch sizes are `T=d*[4,16,64]`, where `d` is the least common multiple of
  the exact capacity denominators. Thus every `T*c_e` is an integer and the
  capacity sum is exactly `K*T`.
- For each cell and batch size, draw 2,000 independent world-0 batch-count
  vectors from the exact Top-K Plackett-Luce subset law using a fixed seed
  derived from `(E,K,T)`. The subset probabilities are computed as exact
  rational numbers, then converted to double precision for NumPy's
  multinomial sampler. Couple world 1 by swapping the first two expert
  counts. This is an exact distributional coupling, not two independent
  samples.
- Apply the canonical observation `A_e=min(R_e,C_e)`. Also apply the
  no-clipping control `A_e=min(R_e,T)=R_e` and verify that identity for every
  draw. The primary finite
  first-signal diagnostics are request-classifier error (sign of `R_1-R_2`),
  admitted-classifier error (sign of `A_1-A_2`), paired admitted-vector
  equality, and the same equality control with clipping disabled.
- For each next-batch action, compute expected overflow exactly from the
  binomial marginal for each expert. Compare: no pressure update (`q=0`), a
  fixed action matching world 0, the world-aware target action, and the
  requested- and admitted-sign classifiers selecting between the two
  target-matching actions. The target score vector is found by solving the
  exact population inclusion equations numerically; residuals are recorded.
- The common-action cost at the world-0 target action is reported only as a
  feasible-action **upper bound** on `v_*`. It is never reported as a lower
  bound or as the globally optimal common action.
- Preserve every paired replicate, including both request vectors, both
  admitted vectors, classifier decisions/errors, and conditional next-batch
  risks. Publish raw replicates separately from the cell-level summary.

## Analysis and falsifiers

The analytic columns report the theorem's `Delta`, all clipping margins,
Hoeffding terms `eps_A(T)` and `eps_R(T)`, and the positive asymptotic
constant only as an uncomputed `v_*>0`. The theorem does not predict that its
finite lower bound is positive at every tested `T`; small batch sizes may
have an inconclusive bound.

The experiment fails its implementation check if any of the following
occurs: exact-total mass is violated; a required clipping margin is
nonpositive; the request swap is not exact under the coupled samples; the
target-inclusion residual exceeds `1e-8`; or the no-clipping requested and
admitted signals are not identical within each sample.

No result from this experiment can prove the strict positivity of `v_*`,
global optimality of the common-action search, a universal controller
ranking, an actual collective's hardware price, or separation from a general
adaptive-testing benchmark. Those claims require separate proofs or
measurements.
