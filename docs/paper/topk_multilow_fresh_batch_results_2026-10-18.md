# Fresh-batch validation of the multi-low-capacity Top-K theorem

**Date:** 2026-10-18  
**Branch:** `feat/research-censored-feedback`  
**Protocol:** [`topk_multilow_fresh_batch_protocol_2026-10-18.md`](topk_multilow_fresh_batch_protocol_2026-10-18.md)  
**Theorem:** [`topk_multilow_population_overflow_theorem_2026-10-17.md`](topk_multilow_population_overflow_theorem_2026-10-17.md)

## Result in one sentence

Under the locked finite-horizon Gumbel experiment, the admitted-minus-requested
cumulative overflow gap was positive in every paired replicate at `H=32`, and
the cell-mean residual from the population prediction decreased as batch size
increased. This supports the theorem's fixed-horizon population prediction in
the registered family; it does not establish a general controller advantage,
a benchmark separation, or a trained-model effect.

## Registered experiment and checks

The runner evaluated all 32 feasible `(E,K,m_low)` families, batch sizes
`T in {1440, 2880, 5760}`, 12 paired replicates per family and batch size, and
horizons `H in {1,2,4,8,16,32}`. It generated a fresh independent affinity
batch at each step, shared that step's batch across the requested, admitted,
and no-update arms, and used the locked common seed schedule.

The final run produced 110,592 step rows, 20,736 replicate-horizon rows,
6,912 paired-horizon rows, and 576 family-by-batch-by-horizon cells. All
registered checks passed: exact aggregate capacity, population response and
root checks, mass conservation and clipping identities, equality of requested
and admitted trajectories in the no-clipping control, and the lower-index
cutoff-tie control. No random cutoff ties occurred.

## Primary endpoint

At `H=32`, all **1,152/1,152** paired replicate gaps were positive. Averaged
over the 96 family-by-batch cells, the mean cumulative gap was `1.244952`,
compared with the mean population prediction `1.259891`.

| Batch size `T` | Mean of 32 family cell means at `H=32` | Mean population prediction | Mean absolute cell residual | Largest absolute cell residual | Marginal 95% intervals containing prediction |
|---:|---:|---:|---:|---:|---:|
| 1,440 | 1.230962 | 1.259891 | 0.031216 | 0.217726 | 23/32 |
| 2,880 | 1.248935 | 1.259891 | 0.015856 | 0.113265 | 26/32 |
| 5,760 | 1.254959 | 1.259891 | 0.007430 | 0.047327 | 23/32 |

The six horizon-wise marginal interval coverage counts were `96/96`,
`91/96`, `79/96`, `79/96`, `78/96`, and `72/96` for `H=1,2,4,8,16,32`,
respectively. In total, 495 of 576 marginal intervals contained the
population prediction. The intervals were registered as descriptive
Student-t intervals, not as simultaneous familywise intervals. The observed
coverage—especially at later horizons—is below the nominal 95% rate and must
be reported as such; it is not evidence that every family-level finite-sample
mean is accurately calibrated by these intervals.

## Interpretation and limits

The decrease in residual with increasing `T`, together with the positive
paired gaps at `H=32`, is consistent with the theorem's fixed-`H`,
large-batch prediction. The fresh-batch design addresses the batch-reuse
concern in the parent fixed-batch experiment.

This experiment does not establish any of the following:

- convergence as `H` tends to infinity at fixed finite `T`;
- the theorem for arbitrary capacity profiles (it uses the registered
  two-level family) or arbitrary affinity laws (the audit uses iid Gumbel);
- optimality of either named feedback update among causal policies;
- a Top-K-specific separation from the general outcome-map or adaptive
  testing benchmark;
- a measured marginal cost for requested telemetry, production prevalence,
  or trained-model quality.

Therefore this is validation evidence for an existing theorem in the current
research line, not the final top-conference proof or benchmark. The unresolved
publication gate remains the quantitative Top-K/root-arrangement result that
does not transfer unchanged to the independent benchmark, plus a matched
system experiment only if the eventual claim depends on practical telemetry
cost or model quality.

## Reproducibility record

Versions: Python `3.14.5`, NumPy `2.4.6`, SciPy `1.17.1`.

| Artifact | SHA-256 |
|---|---|
| Final runner | `40d208991923617a3eaea0b9391f195f00e1c95bcc78fdaf652265c8c848aded` |
| Protocol | `f271b96257878b4d9b1b7ba7ee27737e560db426416f85163050576bb4ed05de` |
| `step_trajectories.csv` | `27d6f0a0e4f65e121a575b0e332f4fcfde96d116b2cd6c75909ac8c607a8f2f7` |
| `replicate_horizons.csv` | `74a8cb6f9b058642b0954d7ff76a3e777fa1cd0519ce2e705af2c5872f0a4181` |
| `paired_horizons.csv` | `dfa7a6f80483a0eeccd43282fa89715510791ed2234964ce2d70dda995a974eb` |

The machine-readable run summary is
[`summary.json`](../../results/topk_multilow_fresh_batch/summary.json); the
full row-level outputs are in `results/topk_multilow_fresh_batch/`.
