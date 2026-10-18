# Controlled Top-2 value-gap experiment: explicit-bound batch sizes

## Question

Does the existing two-saturated-expert Top-2 construction exhibit the
requested/admitted signal behavior at the finite batch sizes where the new
all-pressure analytic bound first certifies a positive optimal-value gap?
The theorem is the existing candidate
[`topk_two_saturated_value_theorem_candidate_2026-10-17.md`](topk_two_saturated_value_theorem_candidate_2026-10-17.md),
updated with the explicit `v_* >= 27/200` proof.

## Fixed plant and actions

- `E=3`, `K=2`; the two static worlds use Gumbel Top-2 base weights `(2,1,1)`
  and `(1,2,1)`, with uniform prior.
- Exact-total capacity fractions are `(11/20,11/20,9/10)`.
- Batch sizes are `T={1680,1800,3360}`. `1680` is the first positive
  double-precision evaluation of the theorem's lower-bound expression over
  multiples of 20; `1800` matches the prior pilot's smallest batch; `3360`
  is twice the certificate threshold. The first-positive designation is a
  numerical scan, not interval-certified minimality.
- Generate 50,000 paired batches per size. Use the exact coupling from the
  earlier pilot: draw a shared omitted-expert-3 count, then draw the
  conditional omitted-1/omitted-2 counts under each world.
- Signals are the full requested vector `R` and canonical admitted vector
  `A=min(R,C)`.
- The requested decision uses the registered threshold `R_1/T>17/24` and
  selects the corresponding target-matching pressure. Exact binomial tails
  provide the classifier-error reference.
- Exact finite-batch expected overflow at correct and wrong target pressures
  is computed from binomial marginal tails. The two-action value gap and the
  all-policy theorem lower bound are reported separately.

## Registered controls and metrics

Check `sum R=2T`, `sum C=2T`, `A=min(R,C)`, exact world swap in the paired
construction, and Monte Carlo agreement with the exact request-classifier
error within five standard errors. Report admitted-vector equality under the
paired coupling, requested/admitted classifier rates, exact two-action
overflow gap, exact theorem-bound terms, and the paired MC uncertainty.
No pressure-grid optimization is used as a lower-bound proof. No model
training, hardware communication price, or production prevalence is claimed.
