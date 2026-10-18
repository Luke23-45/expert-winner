# Requested/admitted information dominance and the costed comparison

**Purpose:** make the comparison target precise for the existing requested
versus admitted feedback program. This result follows from the observation
map and does not depend on a professor's recommendation.

## Model

At each round, an environment generates a requested-count vector `R_t`.
The admitted signal is a deterministic function of it; under the canonical
per-expert capacity rule,

```text
A_t = g(R_t) = min(R_t,C).
```

Both policy classes may use the same actions, state, history, randomization,
and objective. The `R` policy observes `R_t`; the `A` policy observes only
`A_t`. Let `J_R^*` and `J_A^*` be their minimum expected cumulative task
costs when observing counts is free.

## Theorem: free requested observations weakly dominate admitted observations

This is a direct application of Blackwell's comparison of experiments, not
a new information-order theorem. Blackwell's classical reference is
[“Equivalent Comparisons of Experiments,” *Annals of Mathematical
Statistics* 24(2), 265–272 (1953)](https://doi.org/10.1214/aoms/1177729032).

For every causal admitted-observation policy `pi_A`, define a requested-
observation policy `pi_R` that computes `A_t=g(R_t)` and then applies
`pi_A` to the resulting admitted history. The two policies have identical
conditional action distributions at every history. By induction over rounds,
they induce the same joint law over environment states, actions, and task
costs. Therefore

```text
J_R^* <= J_A^*.
```

This holds for deterministic or randomized policies, any horizon, and any
plant dynamics, provided the requested observer can compute the same
admission map and there is no differential observation cost or policy-class
restriction.

## Consequence for the publication comparison

A claim that admitted counts are intrinsically more informative or that an
unrestricted admitted observer beats an unrestricted requested observer is
incompatible with `A=g(R)`. The meaningful comparison is a **costed** one.
For total observation charges `K_R` and `K_A`, compare

```text
J_R^* + K_R   versus   J_A^* + K_A.
```

The requested signal is worthwhile exactly when

```text
J_A^* - J_R^* > K_R - K_A.
```

The units and implementation path for `K_R-K_A` must be measured or fixed
from a concrete system design. In the audited Megatron path, a count-vector
reduction already exists for expert-bias updates; replacing its local
post-drop accumulator with the pre-drop request accumulator may reuse that
reduction. The cost of *adding* a second reduced vector is a different
intervention. No extra-collective surcharge is assumed here.

## Why some fixed-controller runs favor admitted feedback

The theorem compares **optimal causal policy classes**. It does not say that
one named update rule performs better with every observation. The exact
Top-2 signed-bias family has nine-batch cumulative overflow `93m` under its
direct admitted-sign update and `98m` under its direct requested-sign update
([the theorem](top2_signed_bias_separation_theorem_2026-10-17.md)). These
are two particular policies. An unrestricted requested-observation policy
can compute `A=min(R,C)` internally and reproduce the admitted-sign update
exactly, so the `98m` requested direct-update result is not the optimal
requested-observation value. This reconciles that result with the
information-dominance theorem.

Likewise, the exact Top-1 swapped-world analysis compares the two observation
channels under a registered two-target-action class and finds a positive
requested-signal value in the tested family
([analysis](top1_arbitrary_e_bayes_value_analysis_2026-10-17.md)). It is a
concrete finite-batch value calculation, but its observations and losses are
also representable as a generic censored Bayesian experiment. It does not by
itself establish a Top-K-specific benchmark separation.

## Research gate

The current evidence gives two distinct facts: (1) information alone cannot
make the optimal requested policy worse because it can emulate admission;
(2) a fixed direct-feedback controller can behave differently under `R`
and `A`, with direction depending on the routing plant and dynamics. A
conference-level claim on this line must therefore do at least one of the
following:

1. prove a nontrivial Top-K-specific value/complexity result against a
   benchmark fixed independently of the MoE instance; or
2. measure `J_A^*-J_R^*` for a precisely defined practical policy class and
   compare it to the true marginal cost `K_R-K_A` in the same implementation.

The present synthetic evidence completes neither gate. In particular, it
does not justify training a model or charging an unmeasured extra collective.
