# Controlled Top-2 multi-saturation pilot: protocol

## Question

Does the two-saturated-expert observation/value mechanism from the canonical
Top-1 theorem persist in a nondegenerate Gumbel Top-2 router, with no change
to per-expert admission `A_e=min(R_e,C_e)` or to the pressure-action family?

This is a discovery/diagnostic experiment for a possible Top-K theorem. It is
not preregistered evidence, a proof, a controller-performance claim, or a
substitute for the existing formal model.

## Fixed plant

- `E=3`, `K=2`; each token draws an independent Gumbel-perturbed ranking
  (Plackett-Luce Top-2) with base weights `(2,1,1)` in world 0 and `(1,2,1)`
  in world 1.
- A pressure `q` multiplies each base weight by `exp(-q_e)`; pressures are
  identified modulo a common shift.
- Capacity fractions are `c=(11/20,11/20,9/10)`, summing to `K=2`.
  Both first and second experts are above their caps in both worlds at
  `q=0`; expert 3 is below capacity. The two worlds swap the saturated
  experts' demand and have exactly the same marginal law for `R_3`.
- Batch sizes are `T in {1800,7200,28800}`, divisible by 20. Use 500
  independent paired replications at each size, seed `2026101701+T_index*100000+r`.
- Sample the exact count law by sampling the multinomial counts of the
  omitted expert in Top-2. Couple the two worlds by sharing the omitted-3
  count, then sample the remaining omitted-1/omitted-2 counts using each
  world's conditional probabilities. This preserves each world-specific
  Plackett-Luce law and gives an exact coupling for checking admitted-vector
  equality.

## Action and objective

For each world, numerically solve for a gauge-fixed pressure `q^h` whose
population Top-2 inclusion vector equals `c`; report solver residuals. This
is the target-matched action and has zero population overflow by
construction. A requested-count classifier chooses world 0 when
`R_1/T > 17/24` and world 1 otherwise, then selects the corresponding
`q^h`. The admitted-only diagnostic uses the fixed action `q^0`; it is
explicitly not called the optimal admitted policy.

Also minimize the equal-prior population overflow over common pressure
actions with a deterministic two-dimensional search and report the attained
value and search domain. Because this is a numerical search over a bounded
domain, its result is an upper bound on the unrestricted common-action
minimum, not a certified optimum or lower bound.

The primary diagnostics are (i) fraction of pairs with identical admitted
vectors, (ii) the same equality rate with no clipping (`A=R`), (iii)
requested-classifier error, (iv) the population risk of the
classifier-selected action, (v) admitted fixed-action risk, (vi)
common-action search risk, and (vii) target-matched policy risk. Report all
finite-batch rows and do not drop failed or atypical draws.

## Interpretation gate

The pilot supports a Top-2 extension only if the admitted vectors coincide
with increasing frequency, requested classification error decreases, and
the common-action risk stays bounded away from zero while world-matched risk
is zero at the population level. Even that outcome would be empirical
support only. A theorem must prove a positive action-class value gap for all
pressures and quantify finite-batch admitted-law error before claiming a
Top-2 value result.
