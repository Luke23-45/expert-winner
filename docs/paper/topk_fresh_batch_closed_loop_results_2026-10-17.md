# Results: fresh-batch versus static-batch closed-loop audit

**Protocol:** [`topk_fresh_batch_closed_loop_protocol_2026-10-17.md`](topk_fresh_batch_closed_loop_protocol_2026-10-17.md)  
**Runner:** [`../../scripts/run_topk_fresh_batch_closed_loop.py`](../../scripts/run_topk_fresh_batch_closed_loop.py)

## Execution and verification

The paired experiment covered `E=4`, `K={1,2,3}`, standard Gumbel affinities, `T={2304,9216}`, 12 plants per `(K,T)`, and `H={1,2,4,8,16,32,64}` under both static-batch reuse and fresh iid batches. Each replicate used the same initial affinity matrix in both regimes; within each regime, requested and admitted arms shared each step's matrix. The canonical pressure was accumulated each step and min-gauge normalized.

There are 1,008 plant-horizon rows and 84 regime cells. All 144 full-trajectory no-clipping controls passed; there were no Top-K boundary ties; mass, clipping, overflow, initial-pairing, and first-step checks passed. Rerun hashes are stored in `../../results/topk_fresh_batch_closed_loop/summary.json`.

## Results

Both regimes' mean paired gaps are close to the deterministic finite-`T` mean-feedback recurrence at the registered horizons, but the intervals are wider than in the static theorem audit. Across 42 cells per regime, nominal 95% intervals cover that recurrence in 20/42 fresh-batch cells and 16/42 static-batch cells. Mean absolute cell error is `0.0175` for fresh batches and `0.0400` for static reuse. At `T=9216,H=8`, all six `(K,regime)` mean intervals cover the finite-`T` recurrence. The high-horizon intervals often do not, despite small differences between the means and the recurrence.

Fresh batches produced a lower cumulative admitted-minus-requested gap than static reuse in 35/42 paired `(K,T,H)` comparisons; the paired 95% interval was entirely below zero in 29/42. At `H=32`, it was lower in all six `(K,T)` cells with intervals below zero; likewise at `H=64` in all six. This shows that repeated-batch dependence materially affects long-horizon stochastic trajectories in this registered design. It does not show that fresh batches eliminate the effect: the mean gaps remain positive, and they continue to track the finite-`T` mean recurrence closely on average.

The registered mean curves at `H=64` are:

| K | T | Fresh-batch mean | Static-batch mean | Finite-T mean recurrence |
|---:|---:|---:|---:|---:|
| 1 | 2304 | 3.263 | 3.582 | 3.349 |
| 1 | 9216 | 3.525 | 3.587 | 3.549 |
| 2 | 2304 | 3.039 | 3.435 | 3.107 |
| 2 | 9216 | 3.346 | 3.425 | 3.371 |
| 3 | 2304 | 3.285 | 3.633 | 3.440 |
| 3 | 9216 | 3.597 | 3.658 | 3.637 |

These are cumulative overflow differences normalized by `T`, not per-step averages.

## Interpretation boundary

The experiment supports using fresh-batch resampling as a distinct, more training-like stochastic regime and shows that static reuse increases the cumulative gap in most registered paired cells. It does not identify the cause beyond this controlled regime contrast, establish asymptotic rates in `T,H`, or prove a fixed-`T` infinite-horizon theorem. It measures overflow under a synthetic Gumbel router—not model quality, communication cost, or production prevalence. The theorem still has its own benchmark-reduction limitation.
