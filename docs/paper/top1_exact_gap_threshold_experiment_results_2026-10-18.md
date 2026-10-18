# Results: Top-1 synthetic check at positive finite-size theorem thresholds

**Protocol:** [locked design](top1_exact_gap_threshold_experiment_protocol_2026-10-18.md)  
**Theorem:** [exact arbitrary-E Top-1 value theorem](top1_arbitrary_e_exact_swapped_value_theorem_2026-10-17.md)  
**Runner:** [`../../scripts/run_top1_exact_gap_threshold_experiment.py`](../../scripts/run_top1_exact_gap_threshold_experiment.py)  
**Raw cells and summary:** [`../../results/top1_exact_gap_threshold_2026-10-18/`](../../results/top1_exact_gap_threshold_2026-10-18/)

## Result

The experiment ran six cells (`E={3,4,8}` at each first-positive
finite-batch certificate threshold and twice that batch size), with 50,000
paired draws per cell. Every request-mass, clipping, and coordinate-swap
check passed. Each Monte Carlo request/admitted classifier rate was within
five estimated standard errors of its exact finite-binomial value.

| `E` | `T` | Exact requested error | Exact admitted error | Paired admitted vectors equal | Exact two-action value gap | All-policy lower bound |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 704 | 0.006962 | 0.499843 | 0.9997 | 0.021166 | 0.000129 |
| 3 | 1,408 | 0.000253 | 0.500000 | 1.0000 | 0.023444 | 0.013005 |
| 4 | 832 | 0.003753 | 0.499948 | 0.9999 | 0.021735 | 0.000027 |
| 4 | 1,664 | 0.000078 | 0.500000 | 1.0000 | 0.023707 | 0.010764 |
| 8 | 1,356 | 0.000321 | 0.499999 | 1.0000 | 0.023124 | 0.000124 |
| 8 | 2,712 | 0.000001 | 0.500000 | 1.0000 | 0.024557 | 0.008445 |

The table separates two results. The two-action value gap is computed from
exact count-law errors and exact next-batch binomial overflow; it is not
Monte Carlo-estimated. The all-policy lower bound comes from the theorem's
analytic inequality and is smaller, as expected for a conservative
certificate. The simulation checks the classifier and coupling predictions;
it does not prove the all-policy statement.

At the first-positive thresholds, the rigorous theorem form is an explicit
finite-binomial inequality, but the displayed positive margins are only
double-precision diagnostics. The per-cell lower bounds are small
(`2.7e-5` to `1.3e-4`); they are not large empirical effects. Doubling `T`
increases the certificate to `0.0084`–`0.0130` in these cells. This confirms
the finite-size algebra is not merely asymptotic, while keeping clear that
the result is still a constructed Top-1 family and an exact censored
Bayesian decision problem.

## Reproduction hashes

- Runner SHA-256: `7a50a6391a94fa317880af209d58b2395b6b0bb4f612e085d62ca0972b574870`
- Cells SHA-256: `bea4c4eb9020ab2ccfa3ca67919e61e4b804a86cf89fadc721cbbe350d1ddc82`
- Summary SHA-256: `62503e1cc201d55376dbee6533a5f42c5c8c93a625646f4034d6e47229e0e7e4`
- Threshold scan SHA-256: `168e38b8263f2db1ebfbfae0b8bec84ec818ca7f7d22bfb57cc924e29d2e59c6`

No hardware collective, model-quality metric, trained router, or deployment
effect was measured. The experiment does not clear the adaptive-testing
reduction or the top-conference novelty gate.
