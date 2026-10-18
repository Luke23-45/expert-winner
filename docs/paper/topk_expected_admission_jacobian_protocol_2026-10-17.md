# Locked exact synthetic audit: expected admitted Top-K Jacobian

## Question and model

Audit the exact finite-batch clipping-attenuation theorem in `topk_expected_admission_jacobian_theorem_2026-10-17.md` and test its quotient-curl consequence in one model where the requested probability map is known exactly. The plant is Top-1 Gumbel-max with `E=3`, iid standard Gumbel affinities, pressure scores `a-q`, and canonical independent per-expert admission `A_e=min(R_e,C_e)`. The three feedback coordinates are projected by `P0`. This is the existing formal model; there is no group/device cap, score-ranked count rule, new controller, or measured observation surcharge.

## Locked grid

Use probability profiles

- uniform: `(1/3,1/3,1/3)`;
- theorem witness: `(1/2,1/3,1/6)`;
- stronger skew: `(2/3,1/4,1/12)`.

Use `T in {6,12,24,48,96,192}` and common per-expert capacities `C/T in {1/6,1/3,1/2,1}`. All capacities are integers, and `C/T=1/3` is exact total capacity. Compute the clipped binomial expectation, attenuation `alpha_e`, and Jacobian from exact finite binomial sums (float evaluation with a separately checked rational witness). For each cell, independently estimate the Jacobian using central finite differences of the exact expected field at step `1e-5`.

The primary numerical outcome is the quotient curl on `(e1-e3,e2-e3)`. Secondary outcomes are the coordinate attenuation factors, finite-difference error, and the change in curl as `T` grows. The sweep is deterministic; there are no sampled seeds or confidence intervals because the plant's expected field is evaluated exactly.

## Controls and invariants

1. **No-clipping:** `C=T` must give `alpha=(1,1,1)`, zero curl within numerical tolerance, and finite differences matching the requested-field Jacobian.
2. **Exchangeable state:** the uniform probability profile must give zero curl for every common capacity and `T`.
3. **Exact theorem witness:** `T=6,C=2,p=(1/2,1/3,1/6)` must reproduce `alpha=(3/16,112/243,3125/3888)` and `curl=-29/2187` to `1e-12`.
4. **Derivative identity:** every analytic Jacobian entry must match a central finite difference of the exact expected clipped field within `2e-7`.
5. **Probability and capacity checks:** each profile sums to one; `C` is integral and in `[1,T]`; probabilities from the perturbed pressure equal softmax probabilities; no count quantity is mislabeled as a sampled-run result.

## Interpretation fixed before computation

A nonzero curl verifies that the expected admitted feedback is not a potential field at the tested point. It does not by itself establish a control-cost penalty, controller ranking, closed-loop instability, a cost-benefit threshold, or novelty over generic clipped feedback. Exponential attenuation is claimed only when the fixed request probability is strictly above the limiting capacity fraction; equality is excluded from that asymptotic claim.
