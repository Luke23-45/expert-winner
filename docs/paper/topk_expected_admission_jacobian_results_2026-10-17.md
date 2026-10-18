# Results: exact expected-admission Jacobian audit

**Theorem:** [`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md)  
**Protocol:** [`topk_expected_admission_jacobian_protocol_2026-10-17.md`](topk_expected_admission_jacobian_protocol_2026-10-17.md)  
**Runner:** [`../../scripts/run_topk_expected_admission_jacobian.py`](../../scripts/run_topk_expected_admission_jacobian.py)

## Execution and exact controls

The locked grid evaluated 72 deterministic cells: three Top-1 Gumbel choice-probability profiles, six batch sizes `T={6,12,24,48,96,192}`, and four common per-expert capacity fractions `{1/6,1/3,1/2,1}`. Expected clipped counts and their derivatives were evaluated with finite binomial sums; the expected choice probabilities use the exact Gumbel-max softmax formula. This is an exact synthetic numerical audit, not Monte Carlo evidence.

| Check | Result |
|---|---:|
| Cells | 72 |
| Max entrywise error: analytic Jacobian vs central finite difference (`eps=1e-5`) | `2.38e-10` |
| Uniform-probability zero-curl controls | 24/24 |
| No-clipping (`C=T`) zero-curl controls | 18/18 |
| Nonzero clipped curl among skewed profiles | 36/36 |
| Exact witness (`T=6,C=2,p=(1/2,1/3,1/6)`) | `-29/2187 = -0.0132601737540` |

For the theorem witness, the exact attenuation vector is `(3/16,112/243,3125/3888)`. In the exact-total-capacity slice `C/T=1/3`, for profile `(1/2,1/3,1/6)`, the overloaded first coordinate's attenuation falls from `0.1875` at `T=6` to `1.4772e-6` at `T=192`, while the underloaded third coordinate rises from `0.8038` to `0.9999999891`. For the stronger skew profile `(2/3,1/4,1/12)`, these are `0.04527` to `2.18e-21` for the overloaded first coordinate and `0.94142` to effectively one for the underloaded third coordinate. These are deterministic binomial-tail evaluations and illustrate the theorem's strict-overload limit; the finite values should not be mistaken for a general closed-loop trajectory result.

The output and runner hashes are recorded in `../../results/topk_expected_admission_jacobian/summary.json`; raw cells are in `../../results/topk_expected_admission_jacobian/grid.csv`.

## What this establishes—and what it does not

The analytical identity and its numerical derivative checks establish that, in this exact Top-1 stochastic synthetic model, independent per-expert clipping left-scales the request-choice Jacobian by a capacity-dependent binomial-tail factor. Its projected mean admitted-feedback field has a nonzero local curl at every registered skewed/clipped cell, while the two pre-registered symmetry/dropless controls have zero curl.

This provides a precise version of the professor's “sensitivity loss” suggestion compatible with the existing formal count model. It corrects two stronger claims: (1) finite-`T` admitted-count laws are not non-identifying for positive capacity, and (2) rank-based token dropping within independent expert caps cannot change the admitted-count map `A=min(R,C)`. The theorem is about local sensitivity and the expected field, not exact finite-sample observability, saturation windup of every controller, overflow ranking, model quality, telemetry cost, or real-system prevalence. The binomial attenuation identity is generic clipping calculus; Top-K contributes the choice Jacobian and its quotient curl. Its novelty relative to clipped-gradient, censored-observation, and random-utility theory remains to be established.
