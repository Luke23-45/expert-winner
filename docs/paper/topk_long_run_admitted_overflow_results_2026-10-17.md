# Corrected results: long-run admitted-feedback population theorem check

**Theorem:** [`topk_long_run_admitted_overflow_theorem_2026-10-17.md`](topk_long_run_admitted_overflow_theorem_2026-10-17.md)  
**Protocol:** [`topk_long_run_admitted_overflow_protocol_2026-10-17.md`](topk_long_run_admitted_overflow_protocol_2026-10-17.md)  
**Runner:** [`../../scripts/run_topk_long_run_admitted_overflow.py`](../../scripts/run_topk_long_run_admitted_overflow.py)

## Correction to the earlier report

The earlier version of this experiment report stated that finite-batch cumulative gaps fell far below the population prediction at `H>=4`. That conclusion came from an implementation error: the runner recomputed pressure from the current load at every round and **omitted the previous pressure state**. The formal controller is cumulative, `q_next=Pi_g(q+eta*feedback)`. The earlier finite-batch numbers and conclusions are superseded and must not be cited. The analytic population theorem and its proof were not changed by this runner error.

The runner now passes the current pressure into each update, uses the cumulative formal recurrence, and has been rerun. This correction is recorded here rather than silently replacing the earlier numbers.

## Corrected execution

The corrected run produced 1,512 plant-horizon rows and 126 cells: `E=4`, `K=1,2,3`, three affinity laws (Normal, Logistic, Gumbel), `T=2304,9216`, 12 paired plants per `(law,K,T)`, and `H={1,2,4,8,16,32,64}`. Each plant reuses its fixed affinity matrix across rounds and shares it between the requested/admitted arms. All 216 full no-clipping trajectory controls passed; there were no exact boundary ties; all mass, clipping, and overflow identities passed.

| Artifact | SHA-256 |
|---|---|
| Protocol | `4540e0d0c7023dc6dfa08cb11533e9f963a9dcc4a32c9e39ff26955b4f892b5b` |
| Corrected runner | `0d0543100ea7af988c12332a6491b97eae1caeb36dd36661c86bb21a30dbeb08` |
| Corrected plant-horizon rows | `eb4e0397e6bf4261cffd1ec79a11d901da2d3d498a69cd4ee331956d52e37971` |
| Corrected summary | `7cc7cf167e5db038cfe0fc856adc0ded5e524627d68f7d6d4af2d49ddf4d0433` |

The output is in [`../../results/topk_long_run_admitted_overflow/summary.json`](../../results/topk_long_run_admitted_overflow/summary.json) and [`../../results/topk_long_run_admitted_overflow/plants.csv`](../../results/topk_long_run_admitted_overflow/plants.csv). The corrected run was independently repeated with identical output hashes.

## Corrected results

Every cell mean is positive for `H>1`; at `H=2`, at least 11/12 plants are positive in every cell, and at every `H>=4` all 12/12 plants are positive in every cell. The aggregate mean cumulative gap closely tracks the population prediction:

| H | Corrected mean gap / T | Population prediction | Ratio | 95% intervals covering prediction |
|---:|---:|---:|---:|---:|
| 1 | 0.0000 | 0.0000 | — | 18/18 |
| 2 | 0.0089 | 0.0092 | 0.968 | 17/18 |
| 4 | 0.0480 | 0.0495 | 0.968 | 17/18 |
| 8 | 0.1880 | 0.1915 | 0.982 | 17/18 |
| 16 | 0.5932 | 0.5985 | 0.991 | 16/18 |
| 32 | 1.5514 | 1.5576 | 0.996 | 17/18 |
| 64 | 3.5454 | 3.5515 | 0.998 | 17/18 |

Across all horizons, 119/126 nominal 95% paired-mean intervals cover the population prediction; 84/90 do so for `H>=4`. This is strong finite-grid support for the iterated population magnitude under the corrected **static-batch-reuse** design. These intervals summarize 12 paired plants per cell and should not be read as a proof or as broad population coverage beyond the registered cells.

## Interpretation boundary

The correction reverses the prior finite-size assessment: with the actual cumulative pressure update, the static-batch experiment tracks the population prediction closely through `H=64`. The next controlled check compares static reuse with fresh iid batches using the same formal dynamics; that distinguishes sensitivity to a repeated plant from training-like batch resampling. Neither experiment proves fixed-`T` infinite-horizon convergence, universal controller dominance, a measured observation surcharge, trained-model benefit, or separation from the exact finite-instance outcome-map benchmark.
