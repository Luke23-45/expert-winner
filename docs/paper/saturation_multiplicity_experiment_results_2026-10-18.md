# Controlled synthetic results: one versus two saturated experts

**Theorem:** [`saturation_multiplicity_value_theorem_2026-10-18.md`](saturation_multiplicity_value_theorem_2026-10-18.md)  
**Protocol:** [`saturation_multiplicity_experiment_protocol_2026-10-18.md`](saturation_multiplicity_experiment_protocol_2026-10-18.md)  
**Runner:** [`../../scripts/run_saturation_multiplicity_experiment.py`](../../scripts/run_saturation_multiplicity_experiment.py)  
**Cells and machine summary:** [`../../results/saturation_multiplicity_2026-10-18/`](../../results/saturation_multiplicity_2026-10-18/)

## Result

The experiment used the existing Gumbel-Top-K router, exact-total per-expert
clipping, the two swapped worlds, and the theorem's one- versus two-saturated
capacity profiles. It covered `E={3,4,6,8}`, every `K=1,...,E-1`, three
batch sizes per pair, and 5,000 coupled samples per cell. This produced 102
profile cells and 51 matched one/two-saturation comparisons.

The primary value calculation is the exact finite-count Bayes risk in the
registered **two target-pressure action class**. It is not the unrestricted
pressure-policy value. The count-law formulas are evaluated numerically in
double precision; Monte Carlo only checks their implementation and the
coupling/reconstruction events.

| Registered profile | Cells | Mean request Bayes error | Mean admitted Bayes error | Mean two-action value gap | Mean paired admitted-vector equality |
|---|---:|---:|---:|---:|---:|
| One persistently saturated expert per world | 51 | 0.0428 | 0.1213 | 0.00162 | 21.2% |
| Two persistently saturated experts per world | 51 | 0.0428 | 0.4068 | 0.00693 | 80.8% |

The exact admitted-minus-requested gap was larger for the two-saturation
profile in all 51 matched finite-grid cells. The increase ranged from
`0.000926` to `0.010828` normalized overflow. For example, at
`(E,K,T)=(4,2,512)`, the two-action gap was `0.002696` with one saturated
expert and `0.013523` with two. Within this two-action class, each exact gap
is also the break-even price for buying the requested count vector, measured
in normalized overflow units. This is a finite-grid observation, not a
monotonicity theorem in `T` or a result for the full pressure-action space.

## Checks and limits

All exact-total capacity, request-mass, clipping, world-swap, target-solver,
and no-clipping checks passed. The wrong target pressure had higher exact
expected overflow than the correct target pressure in every cell. The
registered Monte Carlo classifier errors were within four binomial standard
errors of the exact count-law values in all 204 profile/signal checks; the
largest standardized deviation was `2.745`. An independent exact-rational
enumeration of the four-category count law checked both signals in six small
cells (`E=3`, `K=1,2`, `T=64`, both profiles; and `E=4,K=2,T=128`, both
profiles); its maximum difference from the binomial-sum implementation was
`6.4e-16`.

The analytic Hoeffding bounds are too loose at these batch sizes to display
the asymptotic one/two-saturation theorem quantitatively: the one-saturation
decoder-failure bound ranged from `1.145` to `6.923`, and the two-saturation
admitted-law coupling bound ranged from `0.661` to `7.207`. Bounds above one
are vacuous. The data therefore support the finite-family mechanism but do
not numerically demonstrate the large-`T` asymptotic separation.

This experiment does not estimate the theorem's unrestricted common-action
constant `v_*`, prove its positivity, model an additional collective's
hardware cost, or establish a real-model benefit. It also does not remove the
adaptive-testing reduction: every fixed finite instance remains an exact
censored Bayesian experiment. The evidence supports the statement that
saturation multiplicity changes the value of the admitted signal in this
Top-K family; it is not, by itself, evidence of a new general control theory.

## Reproduction record

The runner's deterministic seed is derived from `(E,K,T,profile)`.
Reproduce from the repository root with:

```powershell
python scripts/run_saturation_multiplicity_experiment.py
```

SHA-256 values from the final run:

- Runner: `e8cefc2fc81f67c553cbed472d2f40866b8950b6d021756a5cf711684e1b27de`
- Cell CSV: `7b92fa09248a3ddf21e6533e7b862f4802a6b5a1001645dc6478f3ea477560fd`

A fresh reproduction run on 2026-10-18 exited successfully and reproduced the
same runner, helper, cell-CSV, and summary hashes. The environment, repository
revision, dirty-tree caveat, and verified control flags are recorded in
[`../../results/saturation_multiplicity_2026-10-18/reproduction_manifest.json`](../../results/saturation_multiplicity_2026-10-18/reproduction_manifest.json).
