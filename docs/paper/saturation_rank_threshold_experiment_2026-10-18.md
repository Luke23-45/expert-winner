# Controlled exact-expectation audit: saturation multiplicity and local rank

## Research question

Audit the exact rank corollary in
[`topk_expected_admission_jacobian_theorem_2026-10-17.md`](topk_expected_admission_jacobian_theorem_2026-10-17.md): for the expected admitted-mean feedback map, does the limiting quotient response lose exactly `m-1` dimensions when `m` experts are strictly saturated, while every finite-batch response remains full rank?

This is a local-mean-sensitivity experiment on the existing C2/C3 model. It does not test a new controller or admission rule.

## Locked model and grid

- `E=4`, `K in {1,2,3}`, and `T in {160,320,640}`.
- Router: iid standard-Gumbel hard Top-K. Inclusion means are computed by exact enumeration of all `4!` Plackett-Luce rankings.
- Base logits: `(0.7, 0.25, -0.2, -0.75)`; the first `m` experts form the registered saturated set.
- For `m in {1,2,3}`, choose a common positive margin `d` capped at `0.06` and small enough to keep every capacity fraction strictly inside `(0,1)`. Set the first `m` capacity fractions to `p_e-d`; add `m*d/(E-m)` to each remaining fraction. This preserves `sum_e c_e=K` while making exactly the first `m` experts overloaded in the population.
- Round to integer capacities using largest remainder so `sum_e C_e=K*T` exactly. Retain a cell only if every strict overload/under-capacity relation survives rounding; otherwise fail the run rather than silently changing its regime.
- `m=0` is the no-clipping signal control `C_e=T`; it is intentionally not an exact-total admission profile.

## Primary calculation

For each cell compute the exact binomial attenuation
`alpha_e=Pr[Binomial(T-1,p_e)<C_e]`. Form the relative Jacobian from admitted-response coordinates to requested-response coordinates,

```text
L_T = P_0 diag(alpha) restricted to 1^perp,
```

represented in an orthonormal quotient basis. Record its singular values. The theorem predicts:

1. At finite `T`, all `E-1` singular values are positive.
2. For the limiting attenuation vector (zero on the saturated set, one on the unsaturated set), rank is `E-1` for `m=0` and `E-m` for `m>=1`.
3. At least `m-1` finite-batch singular values are no greater than `max_{e<=m} alpha_e`.

The full requested/admitted Jacobians are also computed by central finite differences of their exact expectation functions. This is an independent numerical check of the chain-rule Jacobian and its relative-operator representation; it is not used to define the singular values.

## Controls and failure criteria

- Check `sum_e p_e=K`, exact total capacity for `m>=1`, positive capacities below `T`, and the strict saturation pattern after integer rounding.
- Check that the finite relative operator has full quotient rank and that the limiting rank equals the predicted value in every cell.
- Check the `m-1` singular-value upper bound in every cell, including all registered `K,T` values.
- Check that all no-clipping relative singular values equal one up to floating-point tolerance.
- Check analytic versus finite-difference requested, admitted, and relative Jacobians; fail if the maximum absolute error exceeds `3e-6`.

All cells are retained. No Monte Carlo is used. The runner is
[`../../scripts/run_saturation_rank_threshold_experiment.py`](../../scripts/run_saturation_rank_threshold_experiment.py); its machine-readable output is in
[`../../results/saturation_rank_threshold_2026-10-18/`](../../results/saturation_rank_threshold_2026-10-18/).

## Claim boundary

Passing this audit supports the exact local expected-mean rank theorem under the registered Gumbel-Top-K family. It does not prove finite-law non-identifiability (the finite-batch mean map remains full rank), an all-policy value separation from adaptive testing, a closed-loop controller result, a measured telemetry price, or trained-model benefit.
