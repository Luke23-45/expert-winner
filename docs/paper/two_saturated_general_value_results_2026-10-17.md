# Results: two-saturated Top-1 value theorem

**Status:** controlled synthetic count-law audit; corrected runner; reproducible
rerun. This is evidence for the declared Top-1/Gumbel/per-expert-clipping
family, not a trained-model result.

## Registered design and implementation correction

The locked grid is `E in {3,4,8}`, `delta in {0.04,0.08,0.12}`,
`T in {4800,19200}`, with 2,000 paired count-law draws in each of 18 cells.
The paired worlds share their tail-count vector; the pair mass is split with
the appropriate conditional binomial distribution. Thus each marginal is
exactly the Top-1 Gumbel-Max multinomial law, while the pair is coupled for
checking admitted-vector equality.

The first execution was invalid and is not used: the sampler passed tail
probabilities summing to `0.2` to NumPy's multinomial routine without an
explicit `0.8` pair category. The residual mass was assigned to the final
tail category. The corrected runner draws the full category vector
`(tail_3,...,tail_E,pair)` and overwrites the result files. The runner also
now checks request mass conservation and canonical admission row by row.

## Findings

Across 36,000 paired draws (72,000 world-specific request vectors), the
theorem's two-saturated/no-tail-clipping event held in both worlds; there
were zero event failures. In all 36,000 paired draws, the admitted vectors
were equal under the registered common-tail coupling. The largest observed requested-threshold classification error was
`0.0045`; all 36 world/cell empirical rates were below their stated
Hoeffding bounds. These are finite Monte Carlo checks, not proofs of the
tail bounds.

The runner computes expected realized finite-batch overflow exactly from the
binomial positive-part identity, rather than equating population overflow
with realized overflow. The exact expected costs of the registered requested
threshold policy and the constant admitted policy yield the following
rigorous bounds on the **optimal** normalized value gap:

| E | delta | T | Proven lower bound on `W_A-W_R` | Upper bound from constant admitted policy |
|---:|---:|---:|---:|---:|
| 3 | 0.04 | 4,800 | 0.004584 | 0.017872 |
| 3 | 0.04 | 19,200 | 0.008567 | 0.015186 |
| 3 | 0.08 | 4,800 | 0.017135 | 0.030372 |
| 3 | 0.08 | 19,200 | 0.021067 | 0.027686 |
| 3 | 0.12 | 4,800 | 0.029281 | 0.042872 |
| 3 | 0.12 | 19,200 | 0.033567 | 0.040186 |
| 4 | 0.04 | 4,800 | 0.002477 | 0.019980 |
| 4 | 0.04 | 19,200 | 0.007513 | 0.016240 |
| 4 | 0.08 | 4,800 | 0.015027 | 0.032480 |
| 4 | 0.08 | 19,200 | 0.020013 | 0.028740 |
| 4 | 0.12 | 4,800 | 0.027173 | 0.044980 |
| 4 | 0.12 | 19,200 | 0.032513 | 0.041240 |
| 8 | 0.04 | 4,800 | **−0.002083** | 0.024540 |
| 8 | 0.04 | 19,200 | 0.005232 | 0.018521 |
| 8 | 0.08 | 4,800 | 0.010467 | 0.037040 |
| 8 | 0.08 | 19,200 | 0.017732 | 0.031021 |
| 8 | 0.12 | 4,800 | 0.022613 | 0.049540 |
| 8 | 0.12 | 19,200 | 0.030232 | 0.043521 |

The lower bound is strictly positive in 17 of 18 cells. The `E=8`,
`delta=0.04`, `T=4800` lower bound is negative and therefore inconclusive;
it is not evidence that admitted feedback is better. In all cells, the
registered requested policy's exact finite-batch expected cost is below the
constant admitted policy's cost. That policy comparison is not itself the
optimal-value lower bound; the table's lower-bound column is.

At `T=19,200`, the exact expected normalized overflow of the world-informed
target-matched action is `0.003933` for `E=3`, `0.004987` for `E=4`, and
`0.007268` for `E=8`. These are finite-batch sampling-noise floors; the
population cost of the same action is zero.

## Reproduction record

Command:

```text
python scripts/run_two_saturated_general_value.py
```

Two consecutive corrected runs produced identical hashes:

| Artifact | SHA-256 |
|---|---|
| `scripts/run_two_saturated_general_value.py` | `704083b52be1ed80b618948f8067b14eee67c6a00cb5da75de4e8d8e182c6b7d` |
| `docs/paper/two_saturated_general_value_protocol_2026-10-17.md` | `3378f831acd4d4b6904f200c8cde3a94fd23374ef45afa646ebc307380a0d072` |
| `results/two_saturated_general_value/paired_plants.csv` | `e1ade956303fa20021228dbbda3242f0fef0aa40cfe7b9a0cb667c4834b7c5e0` |
| `results/two_saturated_general_value/cells.csv` | `16e118442d7db5f0d506d01002d56ed6d3df6c6d17dcddb38925d0be1abbb6a4` |
| `results/two_saturated_general_value/summary.json` | `659d5a12513a65edfc98c0fb3d82dc2920161c6ea7fe4fff12a2a0674504fe9e` |

The exact binomial identity was independently compared with direct PMF
summation for `n in {5,10,40}`, `p in {0.1,0.3,0.7}`, and every integer
capacity from zero through `n`; all 27 checks agreed within `1e-10`.

## Interpretation boundary

This strengthens the original model line: two saturated coordinates hide a
split that one saturated coordinate cannot hide, and the resulting
requested/admitted decision-value gap holds for the **realized finite-batch
overflow objective** in the stated Top-1 Gumbel family. It does not establish
a Top-K (`K>1`) theorem, a multi-round control advantage, an optimal physical
telemetry price, a trained-model improvement, or separation from generic
censored hypothesis testing / the outcome-map benchmark. Those remain
distinct proof and evidence obligations for the conference-level claim.
