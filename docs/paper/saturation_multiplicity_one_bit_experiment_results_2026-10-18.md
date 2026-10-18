# Exact synthetic audit: one-bit signal for saturation multiplicity

**Protocol:** [frozen protocol](saturation_multiplicity_one_bit_experiment_protocol_2026-10-18.md)  
**Claim audited:** [one-bit decision-sufficiency theorem](saturation_multiplicity_one_bit_value_theorem_2026-10-18.md)  
**Runner:** [`../../scripts/audit_saturation_multiplicity_one_bit.py`](../../scripts/audit_saturation_multiplicity_one_bit.py)  
**Raw output:** [`../../results/saturation_multiplicity_one_bit_2026-10-18/`](../../results/saturation_multiplicity_one_bit_2026-10-18/)

## Result

The new grid used weight ratio `4/3`, experts `E={3,5,7}`, every `K<E`,
three batch sizes per `(E,K)`, and both exact-total one- and two-saturation
profiles. It contains 72 profile cells (36 per multiplicity). The primary
calculation uses the exact reduced count law and exact target-action risks;
no Monte Carlo estimate enters the result.

| Capacity profile | Cells | Mean `A`-only minus 1-bit value | Range | Mean `A`-only error | Mean 1-bit error |
|---|---:|---:|---:|---:|---:|
| One saturated pair member per world | 36 | 0.002043 | 0.000101–0.005937 | 0.070610 | 0.012002 |
| Two saturated pair members per world | 36 | 0.012903 | 0.004825–0.025792 | 0.445918 | 0.012002 |

Values are expected normalized overflow in the registered two-target action
class. The one-bit and full-request Bayes errors, and therefore their values,
matched in all 72 cells to numerical tolerance `2e-12`. In the two-saturation
profile the one-bit message strictly improved on admitted-only value in all
36 cells. This is a held-out weight ratio and expert-count grid relative to
the prior `5/4`, 102-cell saturation-multiplicity experiment.

An independent exact-rational enumeration aggregated the full request-vector
law for 19 small `(E,K,T)` cells (`E={3,4}`, all `K`, `T<=8`). For every
request vector it verified

```text
P(R=r | world +) / P(R=r | world -) = (a/b)^(r_1-r_2),
```

and found exactly equal rational Bayes errors for full `R` and the one-bit
decision. The complete per-cell rational values are in
`exact_rational_small_grid.csv`.

## Interpretation

The audit supports the theorem’s finite two-action claim and the use of the
same single bit as an asymptotically value-sufficient signal in the existing
all-pressure theorem’s two-saturation regime. It also shows the expected
profile contrast: admitted-only decisions are much less reliable with two
saturated pair coordinates, while the requested sign remains informative.

The finite one-saturation gaps do not have a monotonic trend and are not
evidence against the theorem’s asymptotic reconstruction result. The theorem
predicts decay as `T` grows under fixed strict margins; the tested finite grid
is not a convergence-rate study. No unrestricted pressure optimization was
performed in this experiment. The all-pressure asymptotic implication comes
from the separate analytic theorem, not from the two-action table.

## Claim boundary and prior-art boundary

This is an exact Top-K instantiation of a classical binary likelihood-ratio
decision: it is not a new generic theorem about sufficient statistics. It
does give the professor’s C2 value-of-information line a concrete
decision-signal result: in the stated two-world family, one bit preserves
the full request vector’s two-action value, and the saturation theorem makes
that bit asymptotically necessary and sufficient to recover the full-request
value in the all-pressure problem. Its break-even is measured in normalized
overflow per bit; computing the bit may still require a global reduction.

The result does not establish a real-system benefit, a lower-latency
collective, model-quality improvement, or separation from costed adaptive
testing. It does not turn the one-bit corollary into the paper’s novelty
claim by itself.

## Reproduction and checks

```powershell
python scripts/audit_saturation_multiplicity_one_bit.py
```

The runner checks exact subset-law swaps, exact total capacity, strict
saturation margins, target-risk symmetry, one-bit/full-request equality,
and the independent rational request-vector identities. The output hashes
and aggregate checks are recorded in `summary.json`.
