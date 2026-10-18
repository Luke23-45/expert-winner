# Reduction attack on the Top-K swapped-saturation theorem

## Benchmark fixed independently of the MoE instance

Consider the standard two-state one-step Bayesian experiment class:

1. A latent state `H` is drawn from a prior on `{0,1}`.
2. A finite-alphabet observation `Y` is drawn from a state-dependent
   observation kernel `P_H`.
3. The decision-maker selects an action `a` from an action set `Q`, using
   only `Y` and optional private randomization.
4. The state and action incur a bounded loss `ell_H(a)`.

The comparison may provide two observation channels, `Y_R` and `Y_A`, where
`Y_A=g(Y_R)` for a deterministic censoring map `g`. The class itself places
no Top-K restriction on the observation kernels or action-dependent losses.
It is the ordinary censored Bayesian decision / active-testing benchmark.

## Exact embedding

For a fixed `(E,K,T)` in the theorem, use the finite token outcome alphabet

```text
Omega={S subset [E] : |S|=K}.
```

In state `h` and pressure `q`, each token has a Plackett-Luce law on `Omega`
with weights `exp(theta^h_e-q_e)`. The first observation is the finite count
vector `Y_R=R`, the sum of `T` independent outcomes. The admitted channel is
the deterministic map

```text
Y_A=g(R),  g(R)_e=min(R_e,C_e).
```

The action set is the gauge quotient of pressure vectors, and the loss is the
theorem's exact finite-batch expected normalized overflow for a fresh batch.
These are valid primitives in the independently defined experiment class.
The Bayes values of that benchmark are therefore exactly `V_R(T)` and
`V_A(T)`. Its censored-observation value gap is the theorem's gap, with no
approximation and no change of constants.

This reduction applies for every finite `T`; the arbitrary-`E,K` theorem is
represented by the corresponding sequence of finite experiments. The
benchmark need not assume Top-K to reproduce the theorem's decision problem.

## Consequence for claims

The theorem is a new mathematical result about a structured Gumbel-Top-K
family if the proof survives independent review. It establishes a
parameterized MoE construction and its exact clipping/value mechanism. It
does **not** separate that construction from the broader censored Bayesian
decision or active-testing benchmark, and cannot support a general claim
that Top-K control has a limitation absent from those models.

The residual Top-K-specific content is the construction of the observation
kernel, capacity margins, and action loss from a common Gumbel-Top-K router.
A subsequent theorem, [`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md), now proves an explicit local small-skew coefficient
`j_(E,K)(r_c)/K`, gives its large-`E` scaling in two regimes, and identifies
it with a weighted flux through Top-K switching facets. This supersedes the
older statement that no useful explicit `(E,K)` law exists. It does **not**
make the broader common-action constant `v_*(c)` explicit for arbitrary
capacity profiles, nor does it separate the theorem from the generic
censored Bayesian benchmark: the fixed finite experiment still embeds
exactly. The synthetic experiment also does not measure the marginal
telemetry cost of a deployed system.

The remaining novelty question is therefore narrower and evidence-based:
does the local coefficient and its capacity/skew/batch law yield a
mathematical consequence that is both important and not already supplied by
the specific neighboring literature, or a system-level decision whose
benefit exceeds measured marginal cost? Until one of those is shown, the
result is a structured Top-K application of Bayesian information value, not
an established top-conference contribution.

This is a no-go only for a **generic control-limitation/separation claim
based on this theorem alone**. It is not a no-go for the existing research
program or for a system paper built around the same requested/admitted
question.

## Literature check

Kumar and Mouchtaki's censored-news-vendor analysis also studies information
loss under capacity censoring and the value of targeted exploration. It is a
close conceptual neighbor; the exact Top-K construction does not, by itself,
establish a new general censored-data principle. See their primary source,
[arXiv:2602.16842](https://arxiv.org/abs/2602.16842). This targeted check is
not an exhaustive novelty review.
