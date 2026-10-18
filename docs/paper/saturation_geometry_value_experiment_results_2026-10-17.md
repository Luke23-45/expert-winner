# Results: exact one- vs two-saturated Top-1 value audit

**Status:** exhaustive finite-count enumeration; controlled synthetic evidence for
the declared E=3, K=1, two-world family. This is not a trained-model result or
a benchmark-separation result.

## Result

The runner enumerated every three-expert request vector at six batch sizes
(`T=40,80,160,320,640,1280`) under both capacity assignments. No Monte Carlo
sampling is used in the primary values. The latent worlds and their Top-1
Gumbel-Max request laws are held fixed; only the exact-total capacity profile
changes.

| T | One-sat `V_A−V_R` | Two-sat `V_A−V_R` | One-sat A reconstructs R, worst world | Two-sat `(A,R_1)` reconstructs R, worst world | Two-sat `TV(A_0,A_1)` | `TV(R_0,R_1)` |
|---:|---:|---:|---:|---:|---:|---:|
| 40 | 0.00001457 | 0.00098781 | 0.62059 | 0.999978 | 0.06690 | 0.33067 |
| 80 | 0.00001149 | 0.00227383 | 0.79396 | 0.999999998 | 0.03023 | 0.45348 |
| 160 | 0.00000772 | 0.00443095 | 0.92157 | >0.999999999999 | 0.00546 | 0.60602 |
| 320 | 0.00000150 | 0.00747346 | 0.98283 | >0.999999999999 | 0.000198 | 0.77188 |
| 640 | 0.000000061 | 0.01093360 | 0.998802 | >0.999999999999 | 3.33e-7 | 0.91167 |
| 1280 | 8.88e-11 | 0.01370065 | 0.999992 | >0.999999999999 | 1.32e-12 | 0.98405 |

“Value” is the exact equal-prior expected **next-batch realized normalized
overflow**, optimized over the two registered target-matching pressures. It
is not optimized over the full continuous pressure space. The saturation
reconstruction columns are exact probabilities under the corresponding
multinomial law. In the one-saturated profile, `A` reconstructs R whenever at
most one expert reaches capacity. In the two-saturated profile, `(A,R_1)`
reconstructs R whenever expert 3 remains below capacity, since mass
conservation then recovers `R_2`.

The two-saturated population theorem predicts the limiting gap
`c*delta/(2a)=0.01875`. The finite exact gap is increasing toward that limit
over this range, while the admitted observation laws become nearly
indistinguishable (`TV=1.32e-12` at `T=1280`) and the requested laws become
more separable (`TV=0.98405`). The realized-overflow values remain above
their population limits at finite T because each next batch has sampling
variation.

## Compressed-signal follow-up

The signal `(A,R_1)` selected the same Bayes-optimal action as full `R` on
every enumerated request vector in all 12 cells; its Bayes value agreed with
full `R` within `2.8e-16`. The runner confirmed zero action disagreements over
every count composition, including compositions whose floating-point
probability underflowed to zero. This holds in both capacity profiles for the
registered two-target action class. In the two-saturated profile, `R_1`
alone was close to full-request value at `T=1280` (difference `0.0001984`),
but it was not decision-sufficient: the full-R and R1-only Bayes actions
disagreed on prior mass `0.01158`. This supports a precise, limited design
finding: for this family and action set, retain the admitted vector and add
one selected requested count; do not claim that one requested count alone
preserves the finite-batch decision.

The `(A,R_1)` comparison was added after the first execution, prompted by
the initial equality of its Bayes value and the full-request value. It is a
post hoc exploratory extension, not preregistered confirmatory evidence. The
action agreement is exhaustive over the declared finite support; it is not
an analytic theorem for all parameters.

These results support the proposed **saturation-geometry transition** in this
family: admitted counts retain essentially all decision value when the
clipping fiber is typically singleton, while two simultaneously clipped
coordinates leave a hidden split and a positive asymptotic value gap. The
finite audit does not by itself prove the transition theorem; the exact
one-saturation reconstruction proposition and two-saturation value theorem
provide the analytic statements.

## Checks and reproduction

The runner exhaustively summed the finite multinomial support in double
precision; “exact” means full-support enumeration without Monte Carlo, not
rational arithmetic. It verified exact-total capacities, request mass
conservation, normalization of every enumerated law, and the information
orderings `TV(A_0,A_1) <= TV((A,R_1)_0,(A,R_1)_1) <= TV(R_0,R_1)` and
`V_R <= V_(A,R1) <= V_A` in every cell. The binomial overflow sum was
independently compared with SciPy PMF summation at four parameter points;
the largest discrepancy was `1.02e-15`.

```text
python scripts/audit_saturation_geometry_value.py
```

Artifacts are `results/saturation_geometry_value/exact_values.csv` and
`results/saturation_geometry_value/summary.json`. The summary records hashes
of the protocol, runner, and output. The experiment is a small exact
finite-size audit; the larger `T=4800,19200` controlled count-law study in
[`two_saturated_general_value_results_2026-10-17.md`](two_saturated_general_value_results_2026-10-17.md)
is complementary evidence for the large-batch theorem.

## Claim boundary

This audit does not establish a universal windup result, arbitrary-Top-K
generalization, measured telemetry break-even, trained-model gain, or a
separation from metric-constrained polyhedral active testing. The exact
instance benchmark reduction remains in force. A paper using this result
must present it as a Top-1 saturation-geometry/value theorem and separately
justify why the structured family theorem matters beyond general censored
decision theory.
